# app.py
import streamlit as st
from graph_logic import get_agent_info, register_agent, stream_graph_updates

global AUTH_TOKEN

def main():

    st.title("SpaceTraders.io Assistant")

    # If the user is logged in, display agent info and chatbot interface
    if "agent_info" in st.session_state:
        agent_info = st.session_state["agent_info"]
        print(agent_info)
        symbol = agent_info['data']['symbol']  # Default to 'N/A' if not found
        credits = agent_info['data']['credits']  # Default to 0 if not found
        ships_owned = agent_info['data']['shipCount']

        st.sidebar.header("Agent Information")
        st.sidebar.write(f"**Username:** {symbol}")
        st.sidebar.write(f"**Credits:** {credits:,}")
        st.sidebar.write(f"**Ships Owned:** {ships_owned}")

        # Creating a form where the Enter key won't trigger an automatic submission
        with st.form("my_form"):
            text_input = st.text_input("Type a command or question.")
            submit_button = st.form_submit_button(label="Send")
        
        # Display the output only after the button is clicked
        if submit_button:
            response = stream_graph_updates(text_input, AUTH_TOKEN)
            if response:
                st.write("Assistant:", response)
    
    else:
        # Sidebar for user login/registration
        st.sidebar.header("Agent Authentication")
        token = st.sidebar.text_input("Enter your token", type="password")

        if st.sidebar.button("Log In"):
            if token:
                agent_info = get_agent_info(token)
                if agent_info:
                    st.session_state["token"] = token
                    st.session_state["agent_info"] = agent_info
                    AUTH_TOKEN = token
                    st.sidebar.success("Logged in successfully!")
                    # Clear sidebar by re-writing with an empty message
                    st.sidebar.empty()
                    st.rerun()
                else:
                    st.sidebar.error("Invalid token. Please try again.")
            else:
                st.sidebar.error("Token is required to log in.")

        st.sidebar.write("---")

        username = st.sidebar.text_input("Register as a new agent", placeholder="Enter a new username")

        if st.sidebar.button("Register"):
            if username:
                registration = register_agent(username)
                if registration:
                    token = registration["data"]["token"]
                    agent_info = registration["data"]["agent"]
                    st.session_state["token"] = token
                    st.session_state["agent_info"] = agent_info
                    st.sidebar.success(f"Registered successfully! Your token: {token}")
                else:
                    st.sidebar.error("Registration failed. Try a different username.")
            else:
                st.sidebar.error("Username is required to register.")

if __name__ == "__main__":
    main()
