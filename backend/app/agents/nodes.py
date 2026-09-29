from app.agents.schemas import ApplicationDraft, EligibilityExplanation
from app.agents.state import LeaveAgentState
from app.labels import LEAVE_TYPE_LABELS
from app.llm.client import chat_structured
from app.models import Gender, LeaveType
from app.policy_rules import evaluate_request
from app.rag.retriever import retrieve_policy_chunks


def retrieve_policy_node(state: LeaveAgentState) -> dict:
    label = LEAVE_TYPE_LABELS[state["leave_type"]]
    query = f"{label} ({state['leave_type']}) rules, entitlement, notice period and eligibility conditions"
    chunks = retrieve_policy_chunks(query, top_k=3)
    trace = state.get("agent_trace", []) + [
        f"Policy Retrieval: fetched {len(chunks)} relevant clause(s) from the Code 19 Leave Policy "
        f"({', '.join('Section ' + c['section'] for c in chunks)})."
    ]
    return {"retrieved_chunks": chunks, "agent_trace": trace}


def eligibility_agent_node(state: LeaveAgentState) -> dict:
    verdict = evaluate_request(
        employee_gender=Gender(state["employee_gender"]),
        employee_paternity_used=state.get("paternity_used", 0),
        employee_maternity_used=state.get("maternity_used", 0),
        leave_type=LeaveType(state["leave_type"]),
        start=state["start_date"],
        end=state["end_date"],
        is_half_day=state["is_half_day"],
        medical_certificate_confirmed=state["medical_certificate_confirmed"],
        child_dob=state.get("child_dob"),
        balance_available=state.get("balance_available"),
        today=state["today"],
    )

    policy_context = "\n\n".join(f"[Section {c['section']} - {c['title']}]\n{c['text']}" for c in state["retrieved_chunks"])
    system_prompt = (
        "You are the Eligibility Verification agent for Code 19's HR assistant. A deterministic policy engine has "
        "already decided whether the request is eligible; you must NOT change that verdict. Your only job is to "
        "write a short, professional, employee-facing explanation grounded strictly in the provided policy excerpts "
        "and computed reasons. Always cite section letters in your summary."
    )
    user_prompt = (
        f"Leave type: {LEAVE_TYPE_LABELS[state['leave_type']]} ({state['leave_type']})\n"
        f"Requested dates: {state['start_date']} to {state['end_date']} "
        f"({verdict['requested_days']} day(s), half-day: {state['is_half_day']})\n"
        f"Employee's stated reason: {state['reason']}\n"
        f"Available balance at time of request: {state.get('balance_available')}\n\n"
        f"Deterministic verdict: {'ELIGIBLE' if verdict['eligible'] else 'NOT ELIGIBLE'}\n"
        f"Computed reasons: {verdict['reasons']}\n\n"
        f"Relevant policy excerpts:\n{policy_context}"
    )
    explanation = chat_structured(system_prompt, user_prompt, EligibilityExplanation)

    trace = state.get("agent_trace", []) + [
        f"Eligibility Agent: verdict = {'ELIGIBLE' if verdict['eligible'] else 'NOT ELIGIBLE'} "
        f"({verdict['requested_days']} day(s) requested against a balance of {state.get('balance_available')})."
    ]
    return {
        "eligible": verdict["eligible"],
        "rule_reasons": verdict["reasons"],
        "needs_senior_approval": verdict["needs_senior_approval"],
        "requested_days": verdict["requested_days"],
        "notice_working_days": verdict["notice_working_days"],
        "llm_summary": explanation.summary,
        "policy_citations": [f"Section {s}" for s in explanation.cited_sections],
        "agent_trace": trace,
    }


def route_after_eligibility(state: LeaveAgentState) -> str:
    return "fill_application" if state["eligible"] else "reject"


def application_filler_node(state: LeaveAgentState) -> dict:
    system_prompt = (
        "You are the Application Filler agent for Code 19's HR assistant. Draft a concise, formal leave application "
        "letter from the employee to their line manager, ready to be sent as-is. Reference the leave type, dates, "
        "number of days, and reason. Keep it under 150 words and sign off with the employee's name."
    )
    user_prompt = (
        f"Employee: {state['employee_name']}\n"
        f"Manager: {state['manager_name']}\n"
        f"Leave type: {LEAVE_TYPE_LABELS[state['leave_type']]} ({state['leave_type']})\n"
        f"Dates: {state['start_date']} to {state['end_date']} ({state['requested_days']} day(s))\n"
        f"Reason: {state['reason']}\n"
        f"Policy note: {state['llm_summary']}"
    )
    draft = chat_structured(system_prompt, user_prompt, ApplicationDraft)

    trace = state.get("agent_trace", []) + [
        f"Application Filler Agent: drafted the leave application and routed it to {state['manager_name']} "
        f"({state['manager_email']}) for approval."
    ]
    return {
        "filled_application_text": draft.application_text,
        "final_status": "pending_manager",
        "agent_trace": trace,
    }


def rejection_node(state: LeaveAgentState) -> dict:
    trace = state.get("agent_trace", []) + [
        "Eligibility Agent: request does not satisfy policy conditions — application was not generated or sent."
    ]
    return {"final_status": "rejected_by_agent", "agent_trace": trace}
