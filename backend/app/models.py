import datetime as dt
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Gender(str, Enum):
    male = "male"
    female = "female"


class LeaveType(str, Enum):
    CL = "CL"
    SL = "SL"
    EL = "EL"
    PL = "PL"
    ML = "ML"
    LWP = "LWP"


class RequestStatus(str, Enum):
    pending_manager = "pending_manager"
    approved = "approved"
    rejected_by_agent = "rejected_by_agent"
    rejected_by_manager = "rejected_by_manager"


class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    username: str = Field(unique=True, index=True)
    password_hash: str
    title: str = "Employee"
    gender: Gender
    date_of_joining: dt.date
    is_confirmed: bool = True
    confirmation_date: Optional[dt.date] = None
    manager_name: str
    manager_email: str
    maternity_used: int = 0
    paternity_used: int = 0


class HRUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    username: str = Field(unique=True, index=True)
    password_hash: str
    title: str = "HR Manager"


class LeaveRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    leave_type: LeaveType
    start_date: dt.date
    end_date: dt.date
    is_half_day: bool = False
    reason: str
    medical_certificate_confirmed: bool = False
    child_dob: Optional[dt.date] = None
    submitted_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

    status: RequestStatus = RequestStatus.pending_manager
    requested_days: float = 0

    eligible: Optional[bool] = None
    agent_trace: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    eligibility_reasons: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    policy_citations: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    needs_senior_approval: bool = False
    filled_application_text: Optional[str] = None

    decision_comment: Optional[str] = None
    decided_at: Optional[dt.datetime] = None


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    role: str  # "user" | "assistant"
    content: str
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    linked_leave_request_id: Optional[int] = Field(default=None, foreign_key="leaverequest.id")


class ChatDraft(SQLModel, table=True):
    employee_id: int = Field(primary_key=True, foreign_key="employee.id")
    slots: dict = Field(default_factory=dict, sa_column=Column(JSON))
    updated_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
