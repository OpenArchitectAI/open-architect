"""
    This file will handle setting up an agent that will essentially handle having a conversation with the user and then based on that conversation, break the task up into tickets and then actually create thoe tickets. It will be implemented both through prompts and through DsPy later on.
"""

from trello_helper import *
import concurrent.futures
from pydantic import BaseModel
from typing import Any, List
from openai import OpenAI
import time
import os 
from models import Ticket


OPENAI_API_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class ArchitectAgentRequest(BaseModel):
    question: str
    history: Any
    trello_client: Any

class CreateTicketsRequest(BaseModel):
    question: str
    history: Any
    trello_client: Any

class CreateSubtasksRequest(BaseModel):
    question: str
    history: Any

class IngestCodebaseRequest(BaseModel):
    codebaseName: str 
    githubAccessToken: str 

class ReferenceExistingCodeRequest(BaseModel):
    question: str
    codebaseName: str

class AskFollowupQuestionsRequest(BaseModel):
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
            {"role": "system", "content": f"""You are a principal software engineer who is responsible for mentoring engineers and breaking down tasks into smaller tickets. 
             
            You want to first ask the user several probing questions to better understand the feature that they are trying to build.  
             
            Ask them questions to better explain different aspects of the feature that they are asking for. 
             
            First ask them in detail what they want to build.  - "What are some of the features that you'd like to include in this project?"
             
            You MUST first clarify the project requirements and ask them to provide a detailed description of the project. DO NOT create tickets until you have a clear understanding of the project requirements.
             
            Once you know all of the details of the project, you can then break down the task into smaller tickets and then create those tickets. 
            
            After you have all the subtasks proceed to creating the tasks - "Here are the subtasks that I have created for this task - are we good to create the tasks?". 
             
            Create the tasks for the user. - "Creating your tasks".
             
            You have been given the following task: {architectAgentRequest.question}.  Based on the conversation so far {architectAgentRequest.history}, determine the next best question to ask the user in order to achieve the goal of understanding what they want to build in detail, creating subtasks and then creating the tasks for the user. """},
            {"role": "user", "content": architectAgentRequest.question}]
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "ask_followup_questions",
                    "description": "Ask additional questions to better understand what the user wants to build. This will help you to better understand the project requirements and break the task down into smaller tickets.  You should ask questions to clarify the project requirements and get a detailed description of the project.  You should not create tickets until you have a clear understanding of the project requirements.  Once you have all the details of the project, you can then break down the task into smaller tickets and create those tickets.  After you have all the subtasks, proceed to creating the tasks.  You should ask the user if they are good to create the tasks and then create the tasks for the user.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
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
                    "name": "create_tasks",
                    "description": "When the user asks to create tasks or create tickets in trello, call create tickets. Create tickets based on the subtasks that are generated for the task.  This will actually take the subtasks generated and create the trello tickets for them.",
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

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        function_request_mapping = {
            "ask_followup_questions": AskFollowupQuestionsRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
            ),
            "create_tasks": CreateTicketsRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
                trello_client=architectAgentRequest.trello_client,
            ),
            "create_subtasks": CreateSubtasksRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
            ),
        }

        if tool_calls:
            available_functions = {
                "ask_followup_questions": ask_followup_questions,
                "create_tasks": create_tasks,
                "create_subtasks": create_subtasks,
            }
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                print("Function called is: " + str(function_name))
                function_to_call = available_functions[function_name]
                print("Function to call is: " + str(function_to_call))
                function_args = function_request_mapping[function_name]
                print("Function args are: " + str(function_args))

            return function_to_call(function_args)
        else:
            print("returning message: " + str(response_message.content))
            return response_message.content

    return run_conversation()


def ask_followup_questions(askFollowupQuestionsRequest: AskFollowupQuestionsRequest):
    """
        This function will be responsible for asking follow up questions to better understand what the user wants to build.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        questionPrompt = f"""Given the description of the project so far {askFollowupQuestionsRequest.history} and the user's latest question {askFollowupQuestionsRequest.question}, come up with additional follow up questions to further deepen your understanding of what the user is trying to build. Ask more questions about the front end, backend, or hosting requirements. Understand the details of the product features. Ask questions until you are confident that you are able to generate a detailed execution plan for the project. The response should be a list of questions that you can ask the user to better understand the project requirements.  Limit to 2-3 questions at a time. 
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior staff engineer, who is responsible for asking in depth follow up questions to deepen your understanding of a problem before you determine a plan to build it.",
                },
                {"role": "user", "content": questionPrompt},
            ],
        )
        response = response.choices[0].message.content

        return response

    except Exception as e:
        print("Failed to generate subtasks with error " + str(e))
        return "Failed to generate subtasks with error " + str(e)


def ingest_codebase(ingestCodebaseRequest: IngestCodebaseRequest):
    """
        This method should take the codebase and ingest it into the system. It should store the codebase in a way that it can be easily searched and referenced.
    """
    pass


def reference_existing_code(referenceExistingCodeRequest: ReferenceExistingCodeRequest):
    """
        This method should take the user's question and search the current codebase for all references to that question. It should then summarize the current code and how the user's request can be built within that codebase.
    """
    pass 


def create_tasks(createTicketsRequest: CreateTicketsRequest):
    """
        This function will be responsible for creating multiple tickets in parallel.
    """
    trello_client = createTicketsRequest.trello_client
    
    # Given the conversation history, create tickets for each subtask
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        questionPrompt = f"""Given the following subtask information {createTicketsRequest.history}, generate a list of tasks in the following json format 

        {{
            "subtasks": [
                {{
                    "title": "title of the ticket"
                    "description": "description of the ticket"
                }},
            ]
        }}
        
        Take each subtask and generate a title and description.  Each one should correspond with a list element in the subtask list. You need to cover all of the subtasks that are mentioned and create a ticket for each one. Each ticket should include the title and description of the subtask. The respponse should be a list of these json objects for each subtask.
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
            response_format={ "type": "json_object" }
        )

        subtasks = response.choices[0].message.content
        print("The tasks created are: " + str(subtasks))
        subtask_json = json.loads(subtasks)["subtasks"]

        # Create a list of ticket objects from the subtasks and call create
        tickets = []
        ticket_titles = []
        for subtask in subtask_json:
            ticket = Ticket(title=subtask["title"], description=subtask["description"])
            tickets.append(ticket)
            ticket_titles.append(ticket.title)

        createdTickets = trello_client.push_tickets_to_backlog_and_assign(tickets)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "system", "content": "You are a senior staff engineer, who has just created several tasks for a project. You now need to let the user know which tasks have been created so that they can be worked on.  Let them know the titles of the tasks that have been created and say that you will get to working on them right away.",
                },
                {"role": "user", "content": f"I've just created the following tickets {ticket_titles}"},
            ],
        )
        finalResponse = response.choices[0].message.content
        return finalResponse

    except Exception as e:
        print("Failed to generate subtasks with error " + str(e))
        return "Failed to generate subtasks with error " + str(e)



# Define the tool for breaking up the overall project description into multiple smaller tasks and then getting user feedback on them
def create_subtasks(project_description):
    """
    This function will be responsible for breaking up the overall project description into multiple smaller tasks and then getting user feedback on them.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        questionPrompt = f"""Given the following project description {project_description}, please break it down into smaller tasks that can be accomplished to complete the project. Each task should include a title and a detailed description of the task. The subtasks should all be small enough to be completed in a single day and should represent a micro chunk of work that a user can do to build up to solving the overall task. Focus only on engineering tasks, don't include design or user testing etc. The response should be in the following format
        
        Brief description of the task and breakdown. Don't include 'Title of the task' in the output, replace it with the actual title - 
        
        1. Title of the task
            Detailed description of the task with a breakdown of the steps that need to be taken to complete the task
        2. Title of the task
            Detailed description of the task with a breakdown of the steps that need to be taken to complete the task
        3. Title of the task
            Detailed description of the task with a breakdown of the steps that need to be taken to complete the task
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
