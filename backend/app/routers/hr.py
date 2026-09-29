import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import get_current_hr_user
from app.db import get_session
from app.models import Employee, HRUser, LeaveRequest, LeaveType, RequestStatus
from app.routers.leave import _to_out
from app.schemas import HRDecisionIn, LeaveRequestOut

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get("/queue", response_model=list[LeaveRequestOut])
def get_pending_queue(session: Session = Depends(get_session), _hr: HRUser = Depends(get_current_hr_user)):
    stmt = (
        select(LeaveRequest, Employee)
        .join(Employee, LeaveRequest.employee_id == Employee.id)
        .where(LeaveRequest.status == RequestStatus.pending_manager)
        .order_by(LeaveRequest.submitted_at.asc())
    )
    return [_to_out(req, emp.name) for req, emp in session.exec(stmt)]


@router.get("/requests", response_model=list[LeaveRequestOut])
def get_all_requests(session: Session = Depends(get_session), _hr: HRUser = Depends(get_current_hr_user)):
    stmt = (
        select(LeaveRequest, Employee)
        .join(Employee, LeaveRequest.employee_id == Employee.id)
        .order_by(LeaveRequest.submitted_at.desc())
    )
    return [_to_out(req, emp.name) for req, emp in session.exec(stmt)]


@router.post("/requests/{request_id}/decision", response_model=LeaveRequestOut)
def decide_request(
    request_id: int,
    payload: HRDecisionIn,
    session: Session = Depends(get_session),
    _hr: HRUser = Depends(get_current_hr_user),
):
    req = session.get(LeaveRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if req.status != RequestStatus.pending_manager:
        raise HTTPException(status_code=400, detail=f"Request is already {req.status.value}")

    employee = session.get(Employee, req.employee_id)

    if payload.approve:
        req.status = RequestStatus.approved
        if req.leave_type == LeaveType.PL:
            employee.paternity_used += 1
        elif req.leave_type == LeaveType.ML:
            employee.maternity_used += 1
        session.add(employee)
    else:
        req.status = RequestStatus.rejected_by_manager

    req.decision_comment = payload.comment
    req.decided_at = dt.datetime.utcnow()
    session.add(req)
    session.commit()
    session.refresh(req)

    return _to_out(req, employee.name)
