from app.agents.chat_schemas import ChatTurnResponse
from app.agents.chat_state import ChatAgentState
from app.llm.client import chat_structured_conversation
from app.rag.retriever import retrieve_policy_chunks

DRAFT_FIELDS = [
    "leave_type",
    "start_date",
    "end_date",
    "is_half_day",
    "reason",
    "medical_certificate_confirmed",
    "child_dob",
]

SYSTEM_PROMPT_TEMPLATE = """You are the Code 19 HR Leave Assistant, a conversational agent for employees. You help \
with three things ONLY: (1) answering questions about the Code 19 leave policy and the employee's own leave \
balances, (2) suggesting good leave dates using the weekly off-days and known festival holidays provided below, \
and (3) collecting the details of a leave request one or two fields at a time and submitting it once the \
employee explicitly confirms.

Rules:
- Never invent policy rules beyond what is provided in the policy excerpts below.
- Never invent festival holiday dates beyond what is provided in the holiday calendar below. For \
moon-sighting/government-declared holidays, say plainly that the date isn't fixed yet.
- Never claim a request is approved or rejected yourself — that decision is made by the system's rules engine \
immediately after you submit it, not by you. You may say a request was "submitted" or "sent for approval".
- Ask for one or two missing details at a time rather than an overwhelming checklist.
- Before submitting, summarize the full draft request in your reply and explicitly ask the employee to confirm.
- Only set ready_to_submit=true on the turn where the employee clearly confirms (e.g. "yes", "confirm", "go \
ahead", "submit it") AND all required details are already known from prior turns or this one.
- Dates you output must be absolute ISO dates (YYYY-MM-DD), resolved from relative phrases like "next Monday" \
using today's date below.

Employee: {employee_context}

Employee's current leave balances:
{balance_context}

Holiday calendar:
{holiday_context}

Relevant policy excerpts:
{policy_context}

Current draft leave request (may be partial or empty):
{draft_text}"""


def missing_required_fields(slots: dict) -> list[str]:
    missing = []
    if not slots.get("leave_type"):
        missing.append("leave_type")
    if not slots.get("start_date"):
        missing.append("start_date")
    if not slots.get("is_half_day") and not slots.get("end_date"):
        missing.append("end_date")
    if not slots.get("reason"):
        missing.append("reason")
    if slots.get("leave_type") == "ML" and not slots.get("medical_certificate_confirmed"):
        missing.append("medical_certificate_confirmed")
    return missing


def retrieve_context_node(state: ChatAgentState) -> dict:
    chunks = retrieve_policy_chunks(state["user_message"], top_k=2)
    return {"retrieved_chunks": chunks}


def converse_node(state: ChatAgentState) -> dict:
    slots = state.get("collected_slots") or {}
    policy_context = (
        "\n\n".join(f"[Section {c['section']} - {c['title']}]\n{c['text']}" for c in state["retrieved_chunks"])
        or "(no closely matching section)"
    )
    draft_text = "\n".join(f"- {k}: {v}" for k, v in slots.items() if v not in (None, "")) or "(nothing collected yet)"

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        employee_context=state["employee_context"],
        balance_context=state["balance_context"],
        holiday_context=state["holiday_context"],
        policy_context=policy_context,
        draft_text=draft_text,
    )

    response = chat_structured_conversation(
        system_prompt, state.get("history", []), state["user_message"], ChatTurnResponse
    )

    updated = dict(slots)
    for field in DRAFT_FIELDS:
        value = getattr(response, field)
        if value is not None:
            updated[field] = value

    missing = missing_required_fields(updated)
    ready = bool(response.ready_to_submit and not missing)

    return {
        "reply": response.reply,
        "updated_slots": updated,
        "missing_fields": missing,
        "ready_to_submit": ready,
    }
