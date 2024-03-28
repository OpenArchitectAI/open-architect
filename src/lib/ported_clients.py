from json import JSONDecodeError
import logging
import os
from abc import ABC
import posixpath
import time
from typing import Any, Dict, Iterator, List, Optional, Union
from httpx import Client, ConnectError, HTTPTransport, RequestError, Response

import orjson

from src.lib.ported_exceptions import (
    MistralAPIException,
    MistralAPIStatusException,
    MistralConnectionException,
    MistralException,
)
from src.lib.mistral_chat_completion import ChatCompletionResponse, ChatMessage, Function, ResponseFormat, ToolChoice

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=os.getenv("LOG_LEVEL", "ERROR"),
)

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

ENDPOINT = "https://api.mistral.ai"

class ClientBase(ABC):
    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        max_retries: int = 5,
        timeout: int = 120,
    ):
        self._max_retries = max_retries
        self._timeout = timeout

        self._endpoint = endpoint
        self._api_key = api_key
        self._logger = logging.getLogger(__name__)

        # For azure endpoints, we default to the mistral model
        if "inference.azure.com" in self._endpoint:
            self._default_model = "mistral"

        # This should be automatically updated by the deploy script
        self._version = "0.1.8"

    def _parse_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed_tools: List[Dict[str, Any]] = []
        for tool in tools:
            if tool["type"] == "function":
                parsed_function = {}
                parsed_function["type"] = tool["type"]
                if isinstance(tool["function"], Function):
                    parsed_function["function"] = tool["function"].model_dump(exclude_none=True)
                else:
                    parsed_function["function"] = tool["function"]

                parsed_tools.append(parsed_function)

        return parsed_tools

    def _parse_tool_choice(self, tool_choice: Union[str, ToolChoice]) -> str:
        if isinstance(tool_choice, ToolChoice):
            return tool_choice.value
        return tool_choice

    def _parse_response_format(self, response_format: Union[Dict[str, Any], ResponseFormat]) -> Dict[str, Any]:
        if isinstance(response_format, ResponseFormat):
            return response_format.model_dump(exclude_none=True)
        return response_format

    def _parse_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        parsed_messages: List[Dict[str, Any]] = []
        for message in messages:
            if isinstance(message, ChatMessage):
                parsed_messages.append(message.model_dump(exclude_none=True))
            else:
                parsed_messages.append(message)

        return parsed_messages

    def _make_chat_request(
        self,
        messages: List[Any],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        random_seed: Optional[int] = None,
        stream: Optional[bool] = None,
        safe_prompt: Optional[bool] = False,
        tool_choice: Optional[Union[str, ToolChoice]] = None,
        response_format: Optional[Union[Dict[str, str], ResponseFormat]] = None,
    ) -> Dict[str, Any]:
        request_data: Dict[str, Any] = {
            "messages": self._parse_messages(messages),
            "safe_prompt": safe_prompt,
        }

        if model is not None:
            request_data["model"] = model
        else:
            if self._default_model is None:
                raise MistralException(message="model must be provided")
            request_data["model"] = self._default_model

        if tools is not None:
            request_data["tools"] = self._parse_tools(tools)
        if temperature is not None:
            request_data["temperature"] = temperature
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if top_p is not None:
            request_data["top_p"] = top_p
        if random_seed is not None:
            request_data["random_seed"] = random_seed
        if stream is not None:
            request_data["stream"] = stream

        if tool_choice is not None:
            request_data["tool_choice"] = self._parse_tool_choice(tool_choice)
        if response_format is not None:
            request_data["response_format"] = self._parse_response_format(response_format)

        self._logger.debug(f"Chat request: {request_data}")

        return request_data

    def _process_line(self, line: str) -> Optional[Dict[str, Any]]:
        if line.startswith("data: "):
            line = line[6:].strip()
            if line != "[DONE]":
                json_streamed_response: Dict[str, Any] = orjson.loads(line)
                return json_streamed_response
        return None


class MistralClient(ClientBase):
    """
    Synchronous wrapper around the async client
    """

    def __init__(
        self,
        api_key: Optional[str] = os.environ.get("MISTRAL_API_KEY", None),
        endpoint: str = ENDPOINT,
        max_retries: int = 5,
        timeout: int = 120,
    ):
        super().__init__(endpoint, api_key, max_retries, timeout)

        self._client = Client(
            follow_redirects=True, timeout=self._timeout, transport=HTTPTransport(retries=self._max_retries)
        )

    def __del__(self) -> None:
        self._client.close()

    def _check_response_status_codes(self, response: Response) -> None:
        if response.status_code in RETRY_STATUS_CODES:
            raise MistralAPIStatusException.from_response(
                response,
                message=f"Status: {response.status_code}. Message: {response.text}",
            )
        elif 400 <= response.status_code < 500:
            if response.stream:
                response.read()
            raise MistralAPIException.from_response(
                response,
                message=f"Status: {response.status_code}. Message: {response.text}",
            )
        elif response.status_code >= 500:
            if response.stream:
                response.read()
            raise MistralException(
                message=f"Status: {response.status_code}. Message: {response.text}",
            )

    def _check_streaming_response(self, response: Response) -> None:
        self._check_response_status_codes(response)

    def _check_response(self, response: Response) -> Dict[str, Any]:
        self._check_response_status_codes(response)

        json_response: Dict[str, Any] = response.json()

        if "object" not in json_response:
            raise MistralException(message=f"Unexpected response: {json_response}")
        if "error" == json_response["object"]:  # has errors
            raise MistralAPIException.from_response(
                response,
                message=json_response["message"],
            )

        return json_response

    def _request(
        self,
        method: str,
        json: Dict[str, Any],
        path: str,
        stream: bool = False,
        attempt: int = 1,
    ) -> Iterator[Dict[str, Any]]:
        accept_header = "text/event-stream" if stream else "application/json"
        headers = {
            "Accept": accept_header,
            "User-Agent": f"mistral-client-python/{self._version}",
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        url = posixpath.join(self._endpoint, path)

        self._logger.debug(f"Sending request: {method} {url} {json}")

        response: Response

        try:
            if stream:
                with self._client.stream(
                    method,
                    url,
                    headers=headers,
                    json=json,
                ) as response:
                    self._check_streaming_response(response)

                    for line in response.iter_lines():
                        json_streamed_response = self._process_line(line)
                        if json_streamed_response:
                            yield json_streamed_response

            else:
                response = self._client.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                )

                yield self._check_response(response)

        except ConnectError as e:
            raise MistralConnectionException(str(e)) from e
        except RequestError as e:
            raise MistralException(f"Unexpected exception ({e.__class__.__name__}): {e}") from e
        except JSONDecodeError as e:
            raise MistralAPIException.from_response(
                response,
                message=f"Failed to decode json body: {response.text}",
            ) from e
        except MistralAPIStatusException as e:
            attempt += 1
            if attempt > self._max_retries:
                raise MistralAPIStatusException.from_response(response, message=str(e)) from e
            backoff = 2.0**attempt  # exponential backoff
            time.sleep(backoff)

            # Retry as a generator
            for r in self._request(method, json, path, stream=stream, attempt=attempt):
                yield r

    def chat(
        self,
        messages: List[Any],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        random_seed: Optional[int] = None,
        safe_mode: bool = False,
        safe_prompt: bool = False,
        tool_choice: Optional[Union[str, ToolChoice]] = None,
        response_format: Optional[Union[Dict[str, str], ResponseFormat]] = None,
    ) -> ChatCompletionResponse:
        """A chat endpoint that returns a single response.

        Args:
            model (str): model the name of the model to chat with, e.g. mistral-tiny
            messages (List[Any]): messages an array of messages to chat with, e.g.
                [{role: 'user', content: 'What is the best French cheese?'}]
            tools (Optional[List[Function]], optional): a list of tools to use.
            temperature (Optional[float], optional): temperature the temperature to use for sampling, e.g. 0.5.
            max_tokens (Optional[int], optional): the maximum number of tokens to generate, e.g. 100. Defaults to None.
            top_p (Optional[float], optional): the cumulative probability of tokens to generate, e.g. 0.9.
            Defaults to None.
            random_seed (Optional[int], optional): the random seed to use for sampling, e.g. 42. Defaults to None.
            safe_mode (bool, optional): deprecated, use safe_prompt instead. Defaults to False.
            safe_prompt (bool, optional): whether to use safe prompt, e.g. true. Defaults to False.

        Returns:
            ChatCompletionResponse: a response object containing the generated text.
        """
        request = self._make_chat_request(
            messages,
            model,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            random_seed=random_seed,
            stream=False,
            safe_prompt=safe_mode or safe_prompt,
            tool_choice=tool_choice,
            response_format=response_format,
        )

        single_response = self._request("post", request, "v1/chat/completions")

        for response in single_response:
            return ChatCompletionResponse(**response)

        raise MistralException("No response received")