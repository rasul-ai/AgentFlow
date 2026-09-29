import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import get_current_employee, get_current_hr_user
from app.balances import get_all_balances
from app.db import get_session
from app.models import Employee, HRUser
from app.schemas import EmployeeOut, LeaveBalanceOut

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(session: Session = Depends(get_session), _hr: HRUser = Depends(get_current_hr_user)):
    return session.exec(select(Employee)).all()


def _require_self_or_404(employee_id: int, employee: Employee) -> None:
    if employee.id != employee_id:
        raise HTTPException(status_code=403, detail="You can only access your own profile")


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, employee: Employee = Depends(get_current_employee)):
    _require_self_or_404(employee_id, employee)
    return employee


@router.get("/{employee_id}/balances", response_model=list[LeaveBalanceOut])
def get_balances(
    employee_id: int, session: Session = Depends(get_session), employee: Employee = Depends(get_current_employee)
):
    _require_self_or_404(employee_id, employee)
    return get_all_balances(session, employee, dt.date.today())
