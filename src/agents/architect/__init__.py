import json
from typing import Any, List

from pydantic import BaseModel
from openai import OpenAI
import streamlit as st

from src.helpers.github import GHHelper
from src.helpers.trello import TrelloHelper
from src.lib.terminal import colorize
from src.models import Ticket


class ArchitectAgentRequest(BaseModel):
    question: str
    history: Any


class CreateTicketsRequest(BaseModel):
    question: str
    history: Any


class CreateSubtasksRequest(BaseModel):
    question: str
    history: Any


class AskFollowupQuestionsRequest(BaseModel):
    question: str
    history: Any


class ReferenceExistingCodeRequest(BaseModel):
    question: str
    history: Any


class Architect:
    def __init__(self, name, gh_helper: GHHelper, trello_helper: TrelloHelper):
        self.name = name
        self.gh_helper = gh_helper
        self.trello_helper = trello_helper
        self.log_name = colorize(
            f"[{self.name} the Architect]", bold=True, color="green"
        )
        print(
            f"{self.log_name} Nice to meet you, I'm {self.name} the Architect! I'm here to help you break down your tasks into smaller tickets and create them for you! 🏗️🔨📝"
        )

    def run(self):
        # Step 1: Create a chat interface
        st.title("Open Architect")

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Hey! What new features would you like to add to your project "
                    + str(self.gh_helper.repo.full_name)
                    + " today?  I'll help you break it down to subtasks, figure out how to integrate with your existing code and then set my crew of SWE agents to get it built out for you!",
                }
            )

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What do you want to build today?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                architectureAgentReq = ArchitectAgentRequest(
                    question=prompt,
                    history=[msg["content"] for msg in st.session_state.messages],
                )
                response = self.compute_response(architectureAgentReq)
                res = st.write(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

    def compute_response(self, architectAgentRequest: ArchitectAgentRequest):
        """
        Routing logic for all tools supported by the feedback agent.
        """
        messages = [
            {
                "role": "system",
                "content": f"""You are a principal software engineer who is responsible for mentoring engineers and breaking down tasks into smaller tickets. 
                
            Reference the existing codebase to determine how to build the features in the existing code.
            
            Once you know what to build, you can then break down the task into smaller tickets and then create those tickets. 
            
            After you have all the subtasks proceed to creating the tasks - "Here are the subtasks that I have created for this task - are we good to create the tasks?". 
                
            Create the tasks for the user. - "Creating your tasks".
                
            You have been given the following question: {architectAgentRequest.question}.  Based on the conversation so far {architectAgentRequest.history}, do the following 

            - if there is context about what the user is trying to build, reference their existing code
            - if there are references to their existing code, create subtasks
            - if there are subtasks, ask to create tasks  

            """,
            },
            {
                "role": "user",
                "content": f"address the user's question: {architectAgentRequest.question}",
            },
        ]

        tools = [
            # {
            #     "type": "function",
            #     "function": {
            #         "name": "ask_followup_questions",
            #         "description": "Ask additional questions to better understand what the user wants to build. This will help you to better understand the project requirements and break the task down into smaller tickets.  You should ask questions to clarify the project requirements and get a detailed description of the project.  You should not create tickets until you have a clear understanding of the project requirements.  Once you have all the details of the project, you can then break down the task into smaller tickets and create those tickets.  After you have all the subtasks, proceed to creating the tasks.  You should ask the user if they are good to create the tasks and then create the tasks for the user.",
            #         "parameters": {"type": "object", "properties": {}, "required": []},
            #     },
            # },
            {
                "type": "function",
                "function": {
                    "name": "create_subtasks",
                    "description": "If the user asks to break it down into parts, then call create_subtasks. Based on the user's initial descriptions of the task, break the task down into detailed subtasks to accomplish the larger task. Each subtask should include a title and a detailed description of the subtask.",
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
            {
                "type": "function",
                "function": {
                    "name": "reference_existing_code",
                    "description": "If the user asks to implement in their codebase. Go through the existing code in order to better understand how to build the requested user feature in the codebase. Analyze the code files, and determine the best way to build out support for the new features in the existing code. ",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]

        openai_client = OpenAI()

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        function_request_mapping = {
            # "ask_followup_questions": AskFollowupQuestionsRequest(
            #     question=architectAgentRequest.question,
            #     history=architectAgentRequest.history,
            # ),
            "create_tasks": CreateTicketsRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
            ),
            "create_subtasks": CreateSubtasksRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
            ),
            "reference_existing_code": ReferenceExistingCodeRequest(
                question=architectAgentRequest.question,
                history=architectAgentRequest.history,
            ),
        }

        if tool_calls:
            available_functions = {
                # "ask_followup_questions": ask_followup_questions,
                "create_tasks": self.create_tasks,
                "create_subtasks": self.create_subtasks,
                "reference_existing_code": self.reference_existing_code,
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

        print("returning message: " + str(response_message.content))
        return response_message.content

    def ask_followup_questions(
        self, askFollowupQuestionsRequest: AskFollowupQuestionsRequest
    ):
        """
        This function will be responsible for asking follow up questions to better understand what the user wants to build.
        """
        try:
            questionPrompt = f"""Given the description of the project so far {askFollowupQuestionsRequest.history} and the user's latest question {askFollowupQuestionsRequest.question}, come up with additional follow up questions to further deepen your understanding of what the user is trying to build. Ask more questions about the front end, backend, or hosting requirements. Understand the details of the product features. Ask questions until you are confident that you are able to generate a detailed execution plan for the project. The response should be a list of questions that you can ask the user to better understand the project requirements.  Limit to 2-3 questions at a time. 
            """

            openai_client = OpenAI()
            response = openai_client.chat.completions.create(
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

    def reference_existing_code(
        self, referenceExistingCodeRequest: ReferenceExistingCodeRequest
    ):
        """
        This method should take the user's question and search the current codebase for all references to that question. It should then summarize the current code and how the user's request can be built within that codebase.
        """
        # First get the codebase dict
        codebase_dict = self.gh_helper.get_entire_codebase()

        # Now search the codebase for the user's question
        codebase = codebase_dict.files

        try:
            questionPrompt = f"""Given the description of the project so far {referenceExistingCodeRequest.history} and the user's latest question {referenceExistingCodeRequest.question}, figure out which files in the codebase are most relevant for the user in order to best design a solution to the feature requests. You have this codebase to reference {codebase}. If the feature is completely irrelevant to the user's existing code, let the user know that the feature request seems to be unrelated to the existing codebase and ask them to verify if they do indeed want to build that feature in the current codebase.
            
            If the feature request seems relevant, your response should be something like 

            Going through your existing codebase, I would suggest that we build out _feature_ by modifying the following files _files_ and adding the following functionality to them _functionality description_. Happy to break this down into granular subtasks for you next on how I'm planning to approach this execution. 
            """
            openai_client = OpenAI()

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior staff engineer, who is responsible for going through the codebase in detail and coming up with an execution plan of how to build out certain features. You need to reference the codebase to determine which files are most relevant for the user to build out the feature requests and then come up with an execution plan to build it out across several subtasks.",
                    },
                    {"role": "user", "content": questionPrompt},
                ],
            )
            response = response.choices[0].message.content

            return response

        except Exception as e:
            print("Failed to generate subtasks with error " + str(e))
            return "Failed to generate subtasks with error " + str(e)

    def create_tasks(self, createTicketsRequest: CreateTicketsRequest):
        """
        This function will be responsible for creating multiple tickets in parallel.
        """
        # Given the conversation history, create tickets for each subtask
        try:
            questionPrompt = f"""Given the following subtask information {createTicketsRequest.history}, generate a list of tasks in the following json format 
            {{
                "subtasks": [
                    {{
                        "title": "title of the ticket"
                        "description": "description of the ticket"
                    }},
                ]
            }}
        
            Take each subtask and generate a title and description.  Each one should correspond with a list element in the subtask list. You need to cover all of the subtasks that are mentioned and create a ticket for each one. Each ticket should include the title and description of the subtask. The response should be a list of these json objects for each subtask.
            """

            openai_client = OpenAI()
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior staff engineer, who is responsible for breaking up large complex tasks into small, granular subtasks that more junior engineers can easily work through and execute on.",
                    },
                    {"role": "user", "content": questionPrompt},
                ],
                response_format={"type": "json_object"},
            )

            subtasks = response.choices[0].message.content
            print("The tasks created are: " + str(subtasks))
            subtask_json = json.loads(subtasks)["subtasks"]

            # Create a list of ticket objects from the subtasks and call create
            tickets = []
            ticket_titles = []
            for subtask in subtask_json:
                ticket = Ticket(
                    title=subtask["title"], description=subtask["description"]
                )
                tickets.append(ticket)
                ticket_titles.append(ticket.title)

            createdTickets = self.trello_helper.push_tickets_to_backlog_and_assign(
                tickets
            )

            ticketMarkdown = generate_ticket_markdown(createdTickets)

            return (
                "Great! I've just created the following tickets and assigned them to our agents to get started on immediately \n"
                + ticketMarkdown
            )

            # response = client.chat.completions.create(
            #     model="gpt-3.5-turbo-1106",
            #     messages=[
            #         {
            #             "role": "system",
            #             "content": "You are a senior staff engineer, who has just created several tasks for a project. You now need to let the user know which tasks have been created so that they can be worked on.  Let them know the titles of the tasks that have been created and say that you will get to working on them right away.",
            #         },
            #         {
            #             "role": "user",
            #             "content": f"I've just created the following tickets {createdTickets}",
            #         },
            #     ],
            # )
            # finalResponse = response.choices[0].message.content
            # return finalResponse

        except Exception as e:
            print("Failed to generate subtasks with error " + str(e))
            return "Failed to generate subtasks with error " + str(e)

    # Define the tool for breaking up the overall project description into multiple smaller tasks and then getting user feedback on them
    def create_subtasks(self, project_description):
        """
        This function will be responsible for breaking up the overall project description into multiple smaller tasks and then getting user feedback on them.
        """
        try:
            questionPrompt = f"""Given the following project description {project_description}, please break it down into smaller tasks that can be accomplished to complete the project. Each task should include a title and a detailed description of the task. The subtasks should all be small enough to be completed in a single day and should represent a micro chunk of work that a user can do to build up to solving the overall task. Focus only on engineering tasks, don't include design or user testing etc. The response should be in the following format
            
            Brief description of the task and breakdown. Don't include 'Title of the task' in the output, replace it with the actual title - 


            Here is a break down of your task into a list of more manageable subtasks - 
            
            1. Title of the task
                Detailed description of the task with a breakdown of the steps that need to be taken to complete the task
            2. Title of the task
                Detailed description of the task with a breakdown of the steps that need to be taken to complete the task
            3. Title of the task
                Detailed description of the task with a breakdown of the steps that need to be taken to complete the task
            """
            openai_client = OpenAI()
            response = openai_client.chat.completions.create(
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


def generate_ticket_markdown(tickets: List[Ticket]):
    markdown = ""
    for ticket in tickets:
        markdown += f"- **{ticket.title}**: {ticket.description}\n"
    return markdown
