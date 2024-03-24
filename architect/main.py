"""
    This file will handle setting up an agent that will essentially handle having a conversation with the user and then based on that conversation, break the task up into tickets and then actually create thoe tickets. It will be implemented both through prompts and through DsPy later on.
"""

from trello import TrelloClient
import concurrent.futures
from pydantic import BaseModel
from typing import Any, Union, List
from openai import OpenAI
import time
import json

OPENAI_API_KEY = ""


class Ticket(BaseModel):
    title: str
    description: str


class ArchitectAgentRequest(BaseModel):
    question: str
    history: Any


class CreateTicketsRequest(BaseModel):
    tickets: List[Ticket]


class CreateSubtasksRequest(BaseModel):
    question: str
    history: Any


# Define the function calling agent
def architect_agent(architectAgentRequest: ArchitectAgentRequest):
    """
    Routing logic for all tools supported by the feedback agent.
    """

    client = OpenAI()

    def run_conversation():

        messages = [
            {
                "role": "system",
                "content": f"""You are a principal software engineer who is responsible for mentoring engineers and breaking down tasks into smaller tickets. You want to first ask the user several probing questions to better understand the feature that they are trying to build.  
             
            Ask them questions to better explain different aspects of the feature that they are asking for.  You have been asked to break down a task into smaller tickets and then create those tickets. You have been given the following task: {architectAgentRequest.question}.""",
            },
            {"role": "user", "content": architectAgentRequest.question},
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_subtasks",
                    "description": "Based on the user's initial descriptions of the task, break the task down into detailed subtasks to accomplish the larger task. Each subtask should include a title and a detailed description of the subtask.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_tickets",
                    "description": "Create tickets based on the subtasks that are generated for the task.  This will actually take the subtasks generated and create the trello tickets for them.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]

        beforeFunctionCall = time.time()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        afterFunctionCall = time.time()
        print("Time to function call: " + str(afterFunctionCall - beforeFunctionCall))

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        function_request_mapping = {
            "create_tickets": CreateTicketsRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
            ),
            "create_subtasks": CreateSubtasksRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
            ),
        }

        if tool_calls:
            available_functions = {
                "create_tickets": create_tickets,
                "create_subtasks": create_subtasks,
            }
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                print("FUNCTION NAME: " + str(function_name))
                function_to_call = available_functions[function_name]
                print("FUNCTION TO CALL: " + str(function_to_call))
                function_args = function_request_mapping[function_name]
                print("FUNCTION ARGS: " + str(function_args))

            return function_to_call(function_args)

    return run_conversation()


# Ticket creation tool
client = TrelloClient(
    api_key="YOUR_KEY",
    api_secret="YOUR_SECRET",
    token="YOUR_TOKEN",
    token_secret="YOUR_TOKEN_SECRET",
)


def create_ticket(board_id, list_id, name, desc):
    """
    This function will be responsible for creating the tickets based on the user input and then pushing them to the Trello board.
    """
    board = client.get_board(board_id)
    trello_list = board.get_list(list_id)
    trello_list.add_card(name, desc)

    # Return a response saying that it has created tickets with the corresponding titles and descriptions
    return f"Created ticket with title: {name} and description: {desc}"


def create_tickets(tickets):
    """
    This function will be responsible for creating multiple tickets in parallel.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for ticket in tickets:
            executor.submit(
                create_ticket,
                "BOARD_ID",
                "LIST_ID",
                ticket["title"],
                ticket["description"],
            )


# Define the tool for breaking up the overall project description into multiple smaller tasks and then getting user feedback on them
def create_subtasks(project_description):
    """
    This function will be responsible for breaking up the overall project description into multiple smaller tasks and then getting user feedback on them.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        questionPrompt = f"""Given the following project description {project_description}, please break it down into smaller tasks that can be accomplished to complete the project. Each task should include a title and a detailed description of the task. The subtasks should all be small enough to be completed in a single day and should represent a micro chunk of work that a user can do to build up to solving the overall task. The response should be in the following format
        
        Brief description of the task and breakdown - 
        
        1. SubTask 1: Title of the task
            Brief description of the task
        2. SubTask 2: Title of the task
            Brief description of the task
        3. SubTask 3: Title of the task
            Brief description of the task
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior staff engineer, who is responsible for breaking up large complex tasks into small, granular subtasks that more junior engineers can easily work through and execute on.",
                },
                {"role": "user", "content": questionPrompt},
            ],
        )
        subtasks = response.choices[0].message.content

        return subtasks

    except Exception as e:
        print("Failed to generate subtasks with error " + str(e))
        return "Failed to generate subtasks with error " + str(e)
