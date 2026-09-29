from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agents.chat_nodes import converse_node, retrieve_context_node
from app.agents.chat_state import ChatAgentState


@lru_cache
def get_chat_graph():
    workflow = StateGraph(ChatAgentState)

    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("converse", converse_node)

    workflow.add_edge(START, "retrieve_context")
    workflow.add_edge("retrieve_context", "converse")
    workflow.add_edge("converse", END)

    return workflow.compile()
