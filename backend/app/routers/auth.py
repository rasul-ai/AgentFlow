from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import create_access_token, get_current_employee, get_current_hr_user, verify_password
from app.db import get_session
from app.models import Employee, HRUser
from app.schemas import EmployeeTokenOut, HRTokenOut, LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/employee/login", response_model=EmployeeTokenOut)
def employee_login(payload: LoginIn, session: Session = Depends(get_session)):
    employee = session.exec(select(Employee).where(Employee.username == payload.username)).first()
    if not employee or not verify_password(payload.password, employee.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(employee.id, "employee")
    return EmployeeTokenOut(token=token, employee=employee)


@router.get("/employee/me", response_model=EmployeeTokenOut)
def employee_me(employee: Employee = Depends(get_current_employee)):
    token = create_access_token(employee.id, "employee")
    return EmployeeTokenOut(token=token, employee=employee)


@router.post("/hr/login", response_model=HRTokenOut)
def hr_login(payload: LoginIn, session: Session = Depends(get_session)):
    hr_user = session.exec(select(HRUser).where(HRUser.username == payload.username)).first()
    if not hr_user or not verify_password(payload.password, hr_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(hr_user.id, "hr")
    return HRTokenOut(token=token, hr_user=hr_user)


@router.get("/hr/me", response_model=HRTokenOut)
def hr_me(hr_user: HRUser = Depends(get_current_hr_user)):
    token = create_access_token(hr_user.id, "hr")
    return HRTokenOut(token=token, hr_user=hr_user)
