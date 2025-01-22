# graph_logic.py
import requests
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

API_BASE_URL = "https://api.spacetraders.io/v2"

# Define the state for managing messages
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the graph builder
graph_builder = StateGraph(State)

# Use OpenAI's GPT-4o-mini model
llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Add the chatbot node and connect it to start and end
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile the graph for streaming
graph = graph_builder.compile()

# Function to get agent information
def get_agent_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/my/agent", headers=headers)
    if response.status_code == 200:
        return response.json()["data"]
    return None

# Function to register a new agent
def register_agent(username: str):
    response = requests.post(f"{API_BASE_URL}/register", json={"symbol": username, "faction": "COSMIC"})
    if response.status_code == 201:
        return response.json()
    return None

# Stream graph updates based on user input
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            return value["messages"][-1].content  # Return chatbot message