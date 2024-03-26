import streamlit as st
from src.agents import architect
from pydantic import BaseModel
import typing


class ArchitectAgentRequest(BaseModel):
    question: str
    history: typing.Any
    trello_client: typing.Any
    github_client: typing.Any

# Function to send message and get response
def send_message(architectureAgentReq: ArchitectAgentRequest):
    architectureAgentReq = architect.ArchitectAgentRequest(
        question=architectureAgentReq.question,
        history=architectureAgentReq.history,
        trello_client=architectureAgentReq.trello_client,
        github_client=architectureAgentReq.github_client,
    )
    response = architect.architect_agent(architectureAgentReq)
    return response


def open_architect(trello_client, github_client):

    st.title("Open Architect")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hey! What new features would you like to add to your project " + str(github_client.repo.full_name) + " today?  I'll help you break it down to subtasks, figure out how to integrate with your existing code and then set my crew of SWE agents to get it built out for you!"})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What do you want to build today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            architectAgentRequest = ArchitectAgentRequest(
                question=prompt,
                history=[
                    msg["content"]
                    for msg in st.session_state.messages
                ],
                trello_client=trello_client,
                github_client=github_client,
            )
            response = send_message(architectAgentRequest)
            res = st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
