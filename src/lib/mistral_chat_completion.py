from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

class UsageInfo(BaseModel):
    prompt_tokens: int
    total_tokens: int
    completion_tokens: Optional[int]

class Function(BaseModel):
    name: str
    description: str
    parameters: dict


class ToolType(str, Enum):
    function = "function"


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str = "null"
    type: ToolType = ToolType.function
    function: FunctionCall


class ResponseFormats(str, Enum):
    text: str = "text"
    json_object: str = "json_object"


class ToolChoice(str, Enum):
    auto: str = "auto"
    any: str = "any"
    none: str = "none"


class ResponseFormat(BaseModel):
    type: ResponseFormats = ResponseFormats.text


class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[str]]
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class FinishReason(str, Enum):
    stop = "stop"
    length = "length"
    error = "error"
    tool_calls = "tool_calls"


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[FinishReason]


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo
