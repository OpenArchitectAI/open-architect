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

# Main function to display chat interface
def main():
    st.title("Open Architect")

    # Chat area
    chat_messages = st.empty()

    # Input box for user message
    user_input = st.text_input("Your message:")
    submit_button = st.button("Send")

    # Initialize message history
    message_history = []

    # Handling message submission
    if submit_button:
        if user_input:
            # Add user message to chat area
            chat_messages.markdown(f"**You:** {user_input}", unsafe_allow_html=True)
            # Get response from endpoint
            response = send_message(user_input, message_history)
            message_history.append(user_input)
            message_history.append(response)
            
            # Add response to chat area
            chat_messages.markdown(f"**Bot:** {response}", unsafe_allow_html=True)
            # Clear input box after sending message
            user_input = ""

# Run the app
if __name__ == "__main__":
    main()

# def main():
#     st.title("ChatGPT-like clone")

#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     for message in st.session_state.messages:
#         with st.beta_container():  # Use beta_container for better layout
#             if message["role"] == "user":
#                 st.text_input("You", value=message["content"], key=message["content"], disabled=True)
#             elif message["role"] == "assistant":
#                 st.text_area("Assistant", value=message["content"], height=100, disabled=True)

#     if prompt := st.text_input("What is up?"):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.spinner("Thinking..."):
#             response = send_message(prompt, [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"])
#         st.session_state.messages.append({"role": "assistant", "content": response})


# if __name__ == "__main__":
#     main()
