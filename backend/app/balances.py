import datetime as dt

from sqlmodel import Session, select

from app.models import Employee, LeaveRequest, LeaveType, RequestStatus
from app.policy_rules import ANNUAL_ENTITLEMENT, pro_rata_entitlement


def _sum_days(
    session: Session,
    employee_id: int,
    leave_type: LeaveType,
    statuses: tuple[RequestStatus, ...],
    since: dt.date | None = None,
) -> float:
    stmt = select(LeaveRequest).where(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.leave_type == leave_type,
        LeaveRequest.status.in_(statuses),
    )
    if since is not None:
        stmt = stmt.where(LeaveRequest.start_date >= since)
    return sum((r.requested_days for r in session.exec(stmt)), 0.0)


def get_leave_balance(
    session: Session, employee: Employee, leave_type: LeaveType, today: dt.date | None = None
) -> dict:
    today = today or dt.date.today()
    approved = (RequestStatus.approved,)
    pending = (RequestStatus.pending_manager,)

    if leave_type == LeaveType.LWP:
        return {"leave_type": leave_type.value, "entitlement": None, "used": 0, "pending": 0, "available": None}

    if leave_type in (LeaveType.CL, LeaveType.SL):
        effective_from = employee.date_of_joining
        entitlement = (
            ANNUAL_ENTITLEMENT[leave_type]
            if effective_from.year < today.year
            else pro_rata_entitlement(ANNUAL_ENTITLEMENT[leave_type], effective_from, today)
        )
        year_start = dt.date(today.year, 1, 1)
        used = _sum_days(session, employee.id, leave_type, approved, since=year_start)
        pend = _sum_days(session, employee.id, leave_type, pending, since=year_start)

    elif leave_type == LeaveType.EL:
        effective_from = employee.confirmation_date or employee.date_of_joining
        entitlement = (
            ANNUAL_ENTITLEMENT[leave_type]
            if effective_from.year < today.year
            else pro_rata_entitlement(ANNUAL_ENTITLEMENT[leave_type], effective_from, today)
        )
        year_start = dt.date(today.year, 1, 1)
        used = _sum_days(session, employee.id, leave_type, approved, since=year_start)
        pend = _sum_days(session, employee.id, leave_type, pending, since=year_start)

    elif leave_type == LeaveType.PL:
        entitlement = ANNUAL_ENTITLEMENT[LeaveType.PL]
        used = _sum_days(session, employee.id, leave_type, approved)
        pend = _sum_days(session, employee.id, leave_type, pending)

    elif leave_type == LeaveType.ML:
        entitlement = ANNUAL_ENTITLEMENT[LeaveType.ML]
        used = _sum_days(session, employee.id, leave_type, approved)
        pend = _sum_days(session, employee.id, leave_type, pending)

    else:
        raise ValueError(f"Unhandled leave type: {leave_type}")

    available = round(entitlement - used - pend, 1)
    return {
        "leave_type": leave_type.value,
        "entitlement": round(entitlement, 1),
        "used": round(used, 1),
        "pending": round(pend, 1),
        "available": available,
    }


def get_all_balances(session: Session, employee: Employee, today: dt.date | None = None) -> list[dict]:
    return [get_leave_balance(session, employee, lt, today) for lt in LeaveType]
