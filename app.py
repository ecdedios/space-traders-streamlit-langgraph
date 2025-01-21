import streamlit as st
import requests


# Base URL for the SpaceTraders API
API_BASE_URL = "https://api.spacetraders.io/v2"

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


from langchain_openai import ChatOpenAI

# Use OpenAI's GPT-4o-mini model
llm = ChatOpenAI(model="gpt-4o-mini")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

# Function to get agent information
def get_agent_info(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/my/agent", headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    return None

# Function to register a new agent
def register_agent(username):
    response = requests.post(f"{API_BASE_URL}/register", json={"symbol": username, "faction": "COSMIC"})
    if response.status_code == 200:
        return response.json()
    return None

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            st.write("Assistant:", value["messages"][-1].content)

def main():
    st.title("SpaceTraders.io Assistant")

    # If the user is logged in, display agent info and chatbot interface
    if "agent_info" in st.session_state:
        agent_info = st.session_state["agent_info"]
        st.sidebar.header("Agent Information")
        st.sidebar.write(f"**Username:** {agent_info['symbol']}")
        st.sidebar.write(f"**Credits:** {agent_info['credits']}")

        ships_owned = agent_info.get('shipCount', [])
        st.sidebar.write(f"**Ships Owned:** {ships_owned}")


        structures_owned = agent_info.get('structureCount', [])
        st.sidebar.write(f"**Structures Owned:** {structures_owned}")

        # Creating a form where the Enter key won't trigger an automatic submission
        with st.form("my_form"):
            text_input = st.text_input("Type a command or question.")
            submit_button = st.form_submit_button(label="Send")
            
        # Display the output only after the button is clicked
        if submit_button:
            stream_graph_updates(text_input)
            
    
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
