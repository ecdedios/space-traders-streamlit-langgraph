# app.py
import streamlit as st
from graph_logic import get_agent_info, register_agent, stream_graph_updates

def main():
    st.title("SpaceTraders.io Assistant")

    # Check if agent_info is already in session state
    if "agent_info" in st.session_state:
        agent_info = st.session_state["agent_info"]

        # Display agent information in the sidebar
        st.sidebar.header("Agent Information")
        st.sidebar.write(f"**Username:** {agent_info['symbol']}")
        st.sidebar.write(f"**Credits:** {agent_info['credits']}")
        st.sidebar.write(f"**Ships Owned:** {agent_info.get('shipCount', 0)}")
        st.sidebar.write(f"**Structures Owned:** {agent_info.get('structureCount', 0)}")

        # Main chat interface
        with st.form("my_form"):
            user_input = st.text_input("Type a command or question:")
            submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            response = stream_graph_updates(user_input)
            st.write("Assistant:", response if response else "No response available.")

    else:
        # Sidebar for logging in or registering
        st.sidebar.header("Agent Authentication")
        
        # Log in section
        token = st.sidebar.text_input("Enter your token", type="password")
        if st.sidebar.button("Log In"):
            if token:
                agent_info = get_agent_info(token)
                if agent_info:
                    st.session_state["token"] = token
                    st.session_state["agent_info"] = agent_info
                    st.sidebar.success("Logged in successfully!")
                    st.experimental_rerun()
                else:
                    st.sidebar.error("Invalid token. Please try again.")
            else:
                st.sidebar.error("Please enter a token to log in.")

        st.sidebar.write("---")

        # Registration section
        username = st.sidebar.text_input("Register a new username", placeholder="Choose a username")
        if st.sidebar.button("Register"):
            if username:
                registration = register_agent(username)
                if "data" in registration:
                    token = registration["data"]["token"]
                    agent_info = registration["data"]["agent"]
                    st.session_state["token"] = token
                    st.session_state["agent_info"] = agent_info
                    st.sidebar.success(f"Registration successful! Your token: {token}")
                    st.sidebar.info("You can now log in with this token.")
                else:
                    st.sidebar.error("Registration failed. Try using a different username.")
            else:
                st.sidebar.error("Please enter a username to register.")

if __name__ == "__main__":
    main()