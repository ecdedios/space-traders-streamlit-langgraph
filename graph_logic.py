# graph_logic.py
import requests
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

API_BASE_URL = "https://api.spacetraders.io/v2"

# Define the state for managing messages
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize the graph builder
graph_builder = StateGraph(State)

# Use OpenAI's GPT-4o-mini model
llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot(state: State):
    # Ensure we are working with the most recent message in the list
    user_message = state["messages"][-1]
    
    # Check if the message is an instance of HumanMessage or something else
    if isinstance(user_message, HumanMessage):
        # Now we can access content from HumanMessage
        user_input = user_message.content
    else:
        # Default handling if not HumanMessage
        user_input = ""

    # Call the OpenAI model with the user's input as the context
    response = llm.invoke([user_message])

    return {"messages": [response]}

# Add the chatbot node and connect it to start and agent status
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "agent_status")  # Path to call agent_status
graph_builder.add_edge("agent_status", END)

# # Compile the graph for streaming
# graph = graph_builder.compile()

# Function to get agent information
def get_agent_info(token: str):
    headers = {
        'Authorization': f'Bearer {token}'
    }    
    response = requests.get(f"{API_BASE_URL}/my/agent", headers=headers)
    response.encoding = 'utf-8'  # Explicitly set encoding to UTF-8
    agent_info = response.json()
    return agent_info

# Function to register a new agent
def register_agent(username: str):
    response = requests.post(f"{API_BASE_URL}/register", json={"symbol": username, "faction": "COSMIC"})
    if response.status_code == 200:
        return response.json()
    return None

# Define the custom tool to display agent status
def agent_status_tool(token: str):
    agent_info = get_agent_info(token)  # Ensure token is used properly
    if agent_info:
        status_message = {
            "agent_status": (
                f"**Username:** {agent_info.get('symbol', 'N/A')}\n"
                f"**Credits:** {agent_info.get('credits', 0)}\n"
                f"**Ships Owned:** {agent_info.get('shipCount', 0)}\n"
                f"**Structures Owned:** {agent_info.get('structureCount', 0)}"
            )
        }
        return status_message
    else:
        return {"agent_status": "Agent status not found."}

# Add the agent status tool node to the graph
graph_builder.add_node("agent_status", agent_status_tool)

# Function to stream graph updates with the tool interaction logic
def stream_graph_updates(user_input: str, token: str):
    # Starting the graph stream with the user's input
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            # Check if value is not None and if it contains "agent_status"
            if value and "agent_status" in value:
                # Pass the token to the tool, e.g., call the tool here with token
                agent_status = agent_status_tool(token)  # Ensure token is passed here
                return agent_status  # Return as a dictionary from the tool
            
            # Normal flow and ending without calling the tool
            elif value and "chatbot" in value and "agent_status" not in value:
                return {"response": "Ending the conversation as no tool was triggered."}




# Compile the graph again after adding the new node
graph = graph_builder.compile()