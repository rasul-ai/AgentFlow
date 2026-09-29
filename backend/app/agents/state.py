import datetime as dt
from typing import Optional, TypedDict


class LeaveAgentState(TypedDict, total=False):
    # Inputs (filled by the API layer before the graph runs)
    employee_id: int
    employee_name: str
    employee_gender: str
    manager_name: str
    manager_email: str
    leave_type: str
    start_date: dt.date
    end_date: dt.date
    is_half_day: bool
    reason: str
    medical_certificate_confirmed: bool
    child_dob: Optional[dt.date]
    balance_available: Optional[float]
    paternity_used: int
    maternity_used: int
    today: dt.date

    # Populated by graph nodes
    agent_trace: list[str]
    retrieved_chunks: list[dict]
    requested_days: float
    notice_working_days: int
    eligible: bool
    rule_reasons: list[str]
    needs_senior_approval: bool
    llm_summary: str
    policy_citations: list[str]
    filled_application_text: str
    final_status: str
