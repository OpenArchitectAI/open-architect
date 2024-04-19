
import streamlit as st
import json
from architect import Architect, ArchitectAgentRequest, Codebase


CODEBASE_NAME = "open-architect"

if __name__ == "__main__":

    try :
        with open(f"../../data/codebases/{CODEBASE_NAME}.json", "r") as f:
            codebase = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Codebase {CODEBASE_NAME} not found, in data folder. Please make sure the codebase exists in the data folder dev/data/codedases")
    
    codebase = Codebase(**codebase)
    architect = Architect(name="Sophia", codebase=codebase)
    
    st.title("Open Architect")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hey! What new features would you like to add to your project " + CODEBASE_NAME + " today?  I'll help you break it down to subtasks, figure out how to integrate with your existing code and then set my crew of SWE agents to get it built out for you!"})

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
                history=[
                    msg["content"]
                    for msg in st.session_state.messages
                ],
            )
            response = architect.compute_response(architectureAgentReq)
            res = st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})