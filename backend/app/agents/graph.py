from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    application_filler_node,
    eligibility_agent_node,
    rejection_node,
    retrieve_policy_node,
    route_after_eligibility,
)
from app.agents.state import LeaveAgentState


@lru_cache
def get_leave_request_graph():
    workflow = StateGraph(LeaveAgentState)

    workflow.add_node("retrieve_policy", retrieve_policy_node)
    workflow.add_node("check_eligibility", eligibility_agent_node)
    workflow.add_node("fill_application", application_filler_node)
    workflow.add_node("reject", rejection_node)

    workflow.add_edge(START, "retrieve_policy")
    workflow.add_edge("retrieve_policy", "check_eligibility")
    workflow.add_conditional_edges(
        "check_eligibility",
        route_after_eligibility,
        {"fill_application": "fill_application", "reject": "reject"},
    )
    workflow.add_edge("fill_application", END)
    workflow.add_edge("reject", END)

    return workflow.compile()
