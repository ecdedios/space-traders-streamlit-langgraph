import streamlit as st
from spacepytraders import SpaceTraders
from spacepytraders.errors import SpaceTradersAPIError

def authenticate_agent(api, token=None, username=None):
    """Authenticate agent using either an existing token or by registering as a new agent."""
    if token:
        try:
            api.authenticate(token)
            return api.agent(), True
        except SpaceTradersAPIError as e:
            st.error(f"Authentication failed: {e}")
            return None, False
    elif username:
        try:
            response = api.register(username=username)
            api.authenticate(response.token)
            return response, True
        except SpaceTradersAPIError as e:
            st.error(f"Registration failed: {e}")
            return None, False

    return None, False

def display_agent_status(agent):
    """Display agent details in the sidebar."""
    st.sidebar.header("Agent Status")
    st.sidebar.text(f"Username: {agent.symbol}")
    st.sidebar.text(f"Credits: {agent.credits}")
    st.sidebar.text(f"Number of Ships: {len(agent.ships)}")
    st.sidebar.text(f"Number of Structures: {len(agent.structures)}")

def chatbot_interaction(api, agent):
    """Simple text-based chatbot interface for interacting with the SpaceTraders API."""
    user_input = st.text_input("Ask your SpaceTraders assistant a question or issue a command:")
    if user_input:
        # Dummy response as placeholder for real interaction
        st.write(f"Assistant: I'm sorry, I don't have a response for '{user_input}' yet.")

def main():
    st.set_page_config(page_title="SpaceTraders Assistant", layout="wide")
    st.title("SpaceTraders.io Assistant")

    api = SpaceTraders()

    st.sidebar.header("Log In / Register")
    token = st.sidebar.text_input("Enter your API token", type="password")
    username = st.sidebar.text_input("Or register with a new username")

    if st.sidebar.button("Log In / Register"):
        agent, success = authenticate_agent(api, token=token, username=username)
        if success:
            st.session_state.agent = agent
            st.session_state.api = api

    if "agent" in st.session_state and st.session_state.agent:
        agent = st.session_state.agent
        display_agent_status(agent)
        chatbot_interaction(st.session_state.api, agent)
    else:
        st.write("Please log in or register to interact with SpaceTraders.io")

if __name__ == "__main__":
    main()