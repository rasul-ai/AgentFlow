import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.agents.chat_graph import get_chat_graph
from app.auth import get_current_employee
from app.balances import get_all_balances
from app.db import get_session
from app.holidays import build_holiday_context
from app.models import ChatDraft, ChatMessage, Employee, LeaveRequest, LeaveType
from app.routers.leave import LeavePipelineError, _to_out, run_leave_pipeline
from app.schemas import ChatMessageOut, ChatSendIn, ChatSendOut, LeaveRequestCreate
from app.labels import LEAVE_TYPE_LABELS

router = APIRouter(prefix="/chat", tags=["chat"])

MAX_HISTORY_MESSAGES = 16


def _require_self(employee_id: int, employee: Employee) -> None:
    if employee.id != employee_id:
        raise HTTPException(status_code=403, detail="You can only access your own conversation")


def _employee_context(employee: Employee) -> str:
    return (
        f"{employee.name} ({employee.gender.value}), joined {employee.date_of_joining}, "
        f"{'confirmed' if employee.is_confirmed else 'on probation, not yet confirmed'}, "
        f"manager: {employee.manager_name}"
    )


def _balance_context(session: Session, employee: Employee, today: dt.date) -> str:
    balances = get_all_balances(session, employee, today)
    lines = []
    for b in balances:
        available = b["available"] if b["available"] is not None else "as required (discretionary, HR approval only)"
        lines.append(f"{LEAVE_TYPE_LABELS[b['leave_type']]} ({b['leave_type']}): {available} day(s) available")
    return "\n".join(lines)


def _get_or_create_draft(session: Session, employee_id: int) -> ChatDraft:
    draft = session.get(ChatDraft, employee_id)
    if not draft:
        draft = ChatDraft(employee_id=employee_id, slots={})
        session.add(draft)
        session.commit()
        session.refresh(draft)
    return draft


@router.get("/{employee_id}/messages", response_model=list[ChatMessageOut])
def get_messages(
    employee_id: int, session: Session = Depends(get_session), employee: Employee = Depends(get_current_employee)
):
    _require_self(employee_id, employee)

    stmt = select(ChatMessage).where(ChatMessage.employee_id == employee_id).order_by(ChatMessage.created_at)
    out = []
    for m in session.exec(stmt):
        linked = None
        if m.linked_leave_request_id:
            req = session.get(LeaveRequest, m.linked_leave_request_id)
            if req:
                linked = _to_out(req, employee.name)
        out.append(ChatMessageOut(role=m.role, content=m.content, created_at=m.created_at, submitted_request=linked))
    return out


@router.post("/{employee_id}/messages", response_model=ChatSendOut)
def send_message(
    employee_id: int,
    payload: ChatSendIn,
    session: Session = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
):
    _require_self(employee_id, employee)
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    today = dt.date.today()
    draft = _get_or_create_draft(session, employee_id)

    history_rows = session.exec(
        select(ChatMessage)
        .where(ChatMessage.employee_id == employee_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    ).all()
    history = [{"role": m.role, "content": m.content} for m in reversed(history_rows)]

    session.add(ChatMessage(employee_id=employee_id, role="user", content=payload.content))
    session.commit()

    graph_state = {
        "employee_context": _employee_context(employee),
        "balance_context": _balance_context(session, employee, today),
        "holiday_context": build_holiday_context(today),
        "history": history,
        "user_message": payload.content,
        "collected_slots": dict(draft.slots or {}),
    }
    result = get_chat_graph().invoke(graph_state)

    reply = result["reply"]
    updated_slots = result["updated_slots"]
    submitted_request_out = None
    linked_request_id = None

    if result["ready_to_submit"]:
        try:
            leave_type = LeaveType(updated_slots["leave_type"])
            start_date = dt.date.fromisoformat(updated_slots["start_date"])
            end_date = (
                dt.date.fromisoformat(updated_slots["end_date"]) if updated_slots.get("end_date") else start_date
            )
            child_dob = dt.date.fromisoformat(updated_slots["child_dob"]) if updated_slots.get("child_dob") else None

            leave_payload = LeaveRequestCreate(
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                is_half_day=bool(updated_slots.get("is_half_day", False)),
                reason=updated_slots.get("reason", ""),
                medical_certificate_confirmed=bool(updated_slots.get("medical_certificate_confirmed", False)),
                child_dob=child_dob,
            )
            leave_request = run_leave_pipeline(session, employee, leave_payload)
            submitted_request_out = _to_out(leave_request, employee.name)
            linked_request_id = leave_request.id

            if leave_request.eligible:
                reply += (
                    f"\n\nYour {LEAVE_TYPE_LABELS[leave_type.value]} request for {start_date} to {end_date} has "
                    f"been submitted and sent to {employee.manager_name} for approval."
                )
            else:
                reply += "\n\nI wasn't able to submit this one — see the reasons above."

            updated_slots = {}
        except (ValueError, KeyError, LeavePipelineError):
            reply += "\n\n(I had trouble finalizing those details — could you double-check the dates?)"

    draft.slots = updated_slots
    draft.updated_at = dt.datetime.utcnow()
    session.add(draft)
    session.add(
        ChatMessage(employee_id=employee_id, role="assistant", content=reply, linked_leave_request_id=linked_request_id)
    )
    session.commit()

    return ChatSendOut(reply=reply, draft_slots=updated_slots, submitted_request=submitted_request_out)


@router.post("/{employee_id}/reset")
def reset_draft(
    employee_id: int, session: Session = Depends(get_session), employee: Employee = Depends(get_current_employee)
):
    _require_self(employee_id, employee)
    draft = _get_or_create_draft(session, employee_id)
    draft.slots = {}
    draft.updated_at = dt.datetime.utcnow()
    session.add(draft)
    session.commit()
    return {"status": "ok"}
