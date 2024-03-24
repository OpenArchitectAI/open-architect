import streamlit as st
import requests
from architect import main as architect


# Function to send message and get response
def send_message(message, message_history):
    architectureAgentReq = architect.ArchitectAgentRequest(
        question=message,
        history=message_history,
    )
    response = architect.architect_agent(architectureAgentReq)
    return response



st.title("Open Architect")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = send_message(
            prompt, [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
        )
        res = st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


