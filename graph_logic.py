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
    if response.status_code == 200:
        return response.json()
    return None

# Define the custom tool to display agent status
def agent_status_tool(state: State, token: str):
    agent_info = get_agent_info(token)
    if agent_info:
        status = (
            f"**Username:** {agent_info['symbol']}\n"
            f"**Credits:** {agent_info['credits']}\n"
            f"**Ships Owned:** {agent_info.get('shipCount', 0)}\n"
            f"**Structures Owned:** {agent_info.get('structureCount', 0)}"
        )
        return {"messages": [status]}
    return {"messages": ["Could not retrieve agent status."]}

# Add the agent status tool node to the graph
graph_builder.add_node("agent_status", agent_status_tool)

# Function to stream graph updates with the tool interaction logic
def stream_graph_updates(user_input: str, token: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            # Check if the current node is the "agent_status" tool node
            if "agent_status" in value:
                return value["messages"][-1]
            elif not "agent_status" in value:
                return "Ending the conversation as no further tool is called."

# Compile the graph again after adding the new node
graph = graph_builder.compile()
