import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.agents.graph import get_leave_request_graph
from app.auth import get_current_employee
from app.balances import get_leave_balance
from app.db import get_session
from app.models import Employee, LeaveRequest, RequestStatus
from app.schemas import LeaveRequestCreate, LeaveRequestOut

router = APIRouter(prefix="/leave", tags=["leave"])


class LeavePipelineError(Exception):
    """Raised for request-shape problems caught before the agent pipeline runs."""


def _to_out(req: LeaveRequest, employee_name: str) -> LeaveRequestOut:
    return LeaveRequestOut(
        id=req.id,
        employee_id=req.employee_id,
        employee_name=employee_name,
        leave_type=req.leave_type,
        start_date=req.start_date,
        end_date=req.end_date,
        is_half_day=req.is_half_day,
        reason=req.reason,
        submitted_at=req.submitted_at,
        status=req.status,
        requested_days=req.requested_days,
        eligible=req.eligible,
        agent_trace=req.agent_trace,
        eligibility_reasons=req.eligibility_reasons,
        policy_citations=req.policy_citations,
        needs_senior_approval=req.needs_senior_approval,
        filled_application_text=req.filled_application_text,
        decision_comment=req.decision_comment,
        decided_at=req.decided_at,
    )


def run_leave_pipeline(session: Session, employee: Employee, payload: LeaveRequestCreate) -> LeaveRequest:
    """Runs the LangGraph eligibility + application-filler pipeline for a leave request and
    persists the result. Shared by the direct REST endpoint and the chat agent's submit step."""
    if payload.end_date < payload.start_date:
        raise LeavePipelineError("end_date cannot be before start_date")

    today = dt.date.today()
    balance = get_leave_balance(session, employee, payload.leave_type, today)

    initial_state = {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "employee_gender": employee.gender.value,
        "manager_name": employee.manager_name,
        "manager_email": employee.manager_email,
        "leave_type": payload.leave_type.value,
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "is_half_day": payload.is_half_day,
        "reason": payload.reason,
        "medical_certificate_confirmed": payload.medical_certificate_confirmed,
        "child_dob": payload.child_dob,
        "balance_available": balance["available"],
        "paternity_used": employee.paternity_used,
        "maternity_used": employee.maternity_used,
        "today": today,
        "agent_trace": [],
    }

    graph = get_leave_request_graph()
    result = graph.invoke(initial_state)

    leave_request = LeaveRequest(
        employee_id=employee.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        is_half_day=payload.is_half_day,
        reason=payload.reason,
        medical_certificate_confirmed=payload.medical_certificate_confirmed,
        child_dob=payload.child_dob,
        requested_days=result["requested_days"],
        eligible=result["eligible"],
        agent_trace=result["agent_trace"],
        eligibility_reasons=[result["llm_summary"], *result["rule_reasons"]],
        policy_citations=result["policy_citations"],
        needs_senior_approval=result.get("needs_senior_approval", False),
        filled_application_text=result.get("filled_application_text"),
        status=RequestStatus.pending_manager if result["eligible"] else RequestStatus.rejected_by_agent,
    )
    session.add(leave_request)
    session.commit()
    session.refresh(leave_request)
    return leave_request


@router.post("/requests", response_model=LeaveRequestOut)
def create_leave_request(
    payload: LeaveRequestCreate,
    session: Session = Depends(get_session),
    employee: Employee = Depends(get_current_employee),
):
    if payload.employee_id != employee.id:
        raise HTTPException(status_code=403, detail="You can only submit a request for yourself")
    try:
        leave_request = run_leave_pipeline(session, employee, payload)
    except LeavePipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _to_out(leave_request, employee.name)


@router.get("/requests", response_model=list[LeaveRequestOut])
def list_leave_requests(session: Session = Depends(get_session), employee: Employee = Depends(get_current_employee)):
    stmt = (
        select(LeaveRequest, Employee)
        .join(Employee, LeaveRequest.employee_id == Employee.id)
        .where(LeaveRequest.employee_id == employee.id)
        .order_by(LeaveRequest.submitted_at.desc())
    )
    return [_to_out(req, emp.name) for req, emp in session.exec(stmt)]


@router.get("/requests/{request_id}", response_model=LeaveRequestOut)
def get_leave_request(
    request_id: int, session: Session = Depends(get_session), employee: Employee = Depends(get_current_employee)
):
    req = session.get(LeaveRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if req.employee_id != employee.id:
        raise HTTPException(status_code=403, detail="You can only access your own requests")
    return _to_out(req, employee.name)
