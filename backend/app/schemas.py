import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import Gender, LeaveType, RequestStatus


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    username: str
    title: str
    gender: Gender
    date_of_joining: dt.date
    is_confirmed: bool
    manager_name: str
    manager_email: str


class LeaveBalanceOut(BaseModel):
    leave_type: str
    entitlement: Optional[float]
    used: float
    pending: float
    available: Optional[float]


class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: LeaveType
    start_date: dt.date
    end_date: dt.date
    is_half_day: bool = False
    reason: str
    medical_certificate_confirmed: bool = False
    child_dob: Optional[dt.date] = None


class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    leave_type: LeaveType
    start_date: dt.date
    end_date: dt.date
    is_half_day: bool
    reason: str
    submitted_at: dt.datetime
    status: RequestStatus
    requested_days: float
    eligible: Optional[bool]
    agent_trace: list[str]
    eligibility_reasons: list[str]
    policy_citations: list[str]
    needs_senior_approval: bool
    filled_application_text: Optional[str]
    decision_comment: Optional[str]
    decided_at: Optional[dt.datetime]


class PolicySearchResult(BaseModel):
    section: str
    title: str
    text: str
    distance: float


class HRDecisionIn(BaseModel):
    approve: bool
    comment: Optional[str] = None


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: dt.datetime
    submitted_request: Optional[LeaveRequestOut] = None


class ChatSendIn(BaseModel):
    content: str


class ChatSendOut(BaseModel):
    reply: str
    draft_slots: dict
    submitted_request: Optional[LeaveRequestOut] = None


class HRUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    username: str
    title: str


class LoginIn(BaseModel):
    username: str
    password: str


class EmployeeTokenOut(BaseModel):
    token: str
    employee: EmployeeOut


class HRTokenOut(BaseModel):
    token: str
    hr_user: HRUserOut
