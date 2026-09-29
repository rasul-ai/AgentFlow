"""Numeric constants and pure helper functions distilled from the Code 19 Leave Policy
(Edition 1.1, 15 Jan 2022). Kept separate from the LLM/RAG layer so that leave-balance
math and hard entitlement caps are deterministic and auditable, never left to the model.
"""

import datetime as dt

from app.models import Gender, LeaveType

ANNUAL_ENTITLEMENT: dict[LeaveType, float] = {
    LeaveType.CL: 10,
    LeaveType.SL: 14,
    LeaveType.EL: 20,
    LeaveType.PL: 7,
    LeaveType.ML: 120,
    LeaveType.LWP: 0,  # "as required" — not balance-based
}

CL_MAX_CONSECUTIVE_DAYS = 2
CL_HALF_DAY_MAX_HOURS = 4
EL_NOTICE_WORKING_DAYS = 10
EL_MAX_CONSECUTIVE_WITHOUT_SENIOR_APPROVAL = 5
PL_NOTICE_WEEKS = 4
PL_MUST_BE_TAKEN_WITHIN_WEEKS_OF_BIRTH = 6
PL_MAX_CHILDREN = 2
ML_NOTICE_WEEKS = 10
ML_MAX_CHILDREN = 2
UNAUTHORIZED_ABSENCE_TRIGGER_DAYS = 3


def count_working_days_between(start: dt.date, end: dt.date) -> int:
    """Business days strictly between two dates (exclusive of both ends), Mon-Fri."""
    if end <= start:
        return 0
    days = 0
    d = start + dt.timedelta(days=1)
    while d < end:
        if d.weekday() < 5:
            days += 1
        d += dt.timedelta(days=1)
    return days


def calendar_days_inclusive(start: dt.date, end: dt.date) -> int:
    return (end - start).days + 1


def pro_rata_entitlement(annual_days: float, effective_from: dt.date, today: dt.date) -> float:
    """Linear pro-ration of an annual entitlement from an effective date (joining or
    confirmation date) within the current leave calendar year (Jan 1 - Dec 31)."""
    year_start = dt.date(today.year, 1, 1)
    year_end = dt.date(today.year, 12, 31)
    if effective_from <= year_start:
        return annual_days
    if effective_from > year_end:
        return 0
    remaining_days = (year_end - effective_from).days + 1
    total_days = (year_end - year_start).days + 1
    return round(annual_days * remaining_days / total_days, 1)


def evaluate_request(
    employee_gender: Gender,
    employee_paternity_used: int,
    employee_maternity_used: int,
    leave_type: LeaveType,
    start: dt.date,
    end: dt.date,
    is_half_day: bool,
    medical_certificate_confirmed: bool,
    child_dob: dt.date | None,
    balance_available: float | None,
    today: dt.date,
) -> dict:
    """Deterministic, auditable gate. Returns eligibility plus the specific policy
    reasons behind it; an LLM node later turns `reasons` into employee-facing prose
    but never overrides `eligible`."""
    reasons: list[str] = []
    eligible = True
    needs_senior_approval = False

    requested_days = 0.5 if (leave_type == LeaveType.CL and is_half_day) else calendar_days_inclusive(start, end)
    notice_working_days = count_working_days_between(today, start)
    notice_weeks = (start - today).days / 7

    if leave_type == LeaveType.CL:
        if not is_half_day and requested_days > CL_MAX_CONSECUTIVE_DAYS:
            eligible = False
            reasons.append(
                f"Casual Leave cannot exceed {CL_MAX_CONSECUTIVE_DAYS} consecutive day(s) at a stretch (Section D.2)."
            )
        if balance_available is not None and requested_days > balance_available:
            eligible = False
            reasons.append(
                f"Insufficient Casual Leave balance: {balance_available} day(s) available, {requested_days} requested."
            )

    elif leave_type == LeaveType.SL:
        if requested_days > 1 and not medical_certificate_confirmed:
            eligible = False
            reasons.append(
                "A medical certificate must accompany the leave application for Sick Leave exceeding 1 day (Section E.2)."
            )
        if balance_available is not None and requested_days > balance_available:
            eligible = False
            reasons.append(
                f"Insufficient Sick Leave balance: {balance_available} day(s) available, {requested_days} requested."
            )

    elif leave_type == LeaveType.EL:
        if notice_working_days < EL_NOTICE_WORKING_DAYS:
            eligible = False
            reasons.append(
                f"Earned Leave requires at least {EL_NOTICE_WORKING_DAYS} working days' notice; only "
                f"{notice_working_days} working day(s) given before the requested start date (Section F.1)."
            )
        if balance_available is not None and requested_days > balance_available:
            eligible = False
            reasons.append(
                f"Insufficient Earned Leave balance: {balance_available} day(s) available, {requested_days} requested."
            )
        if requested_days > EL_MAX_CONSECUTIVE_WITHOUT_SENIOR_APPROVAL:
            needs_senior_approval = True
            reasons.append(
                f"Requests exceeding {EL_MAX_CONSECUTIVE_WITHOUT_SENIOR_APPROVAL} consecutive days require "
                "additional approval from management, beyond the line manager (Section F.5)."
            )

    elif leave_type == LeaveType.PL:
        if employee_gender != Gender.male:
            eligible = False
            reasons.append("Paternal Leave is only applicable to male employees (Section H).")
        if employee_paternity_used >= PL_MAX_CHILDREN:
            eligible = False
            reasons.append(f"Paternal Leave has already been availed for the maximum of {PL_MAX_CHILDREN} children (Section H.2).")
        if notice_weeks < PL_NOTICE_WEEKS:
            eligible = False
            reasons.append(f"Paternal Leave requires at least {PL_NOTICE_WEEKS} weeks' notice (Section H.1).")
        if child_dob is not None:
            weeks_since_birth = (start - child_dob).days / 7
            if weeks_since_birth > PL_MUST_BE_TAKEN_WITHIN_WEEKS_OF_BIRTH:
                eligible = False
                reasons.append(
                    f"Paternal Leave must be taken within {PL_MUST_BE_TAKEN_WITHIN_WEEKS_OF_BIRTH} weeks of the "
                    "child's date of birth (Section H.2)."
                )
        if balance_available is not None and requested_days > balance_available:
            eligible = False
            reasons.append(
                f"Insufficient Paternal Leave balance: {balance_available} day(s) available, {requested_days} requested."
            )

    elif leave_type == LeaveType.ML:
        if employee_gender != Gender.female:
            eligible = False
            reasons.append("Maternity Leave is only applicable to female employees (Section G).")
        if employee_maternity_used >= ML_MAX_CHILDREN:
            eligible = False
            reasons.append(f"Maternity Leave has already been availed for the maximum of {ML_MAX_CHILDREN} children (Section G.3).")
        if notice_weeks < ML_NOTICE_WEEKS:
            eligible = False
            reasons.append(f"Maternity Leave requires at least {ML_NOTICE_WEEKS} weeks' notice (Section G.1).")
        if not medical_certificate_confirmed:
            eligible = False
            reasons.append("Maternity Leave requires a medical certificate from the attending physician (Section G.1).")
        if balance_available is not None and requested_days > balance_available:
            eligible = False
            reasons.append(
                f"Insufficient Maternity Leave balance: {balance_available} day(s) available, {requested_days} requested."
            )

    elif leave_type == LeaveType.LWP:
        reasons.append(
            "Leave Without Pay is granted at Management's discretion and may affect annual increment, salary "
            "enhancement and other admissible benefits (Section I.2)."
        )

    if eligible and not reasons:
        reasons.append("Request satisfies all applicable policy conditions.")

    return {
        "eligible": eligible,
        "reasons": reasons,
        "needs_senior_approval": needs_senior_approval,
        "requested_days": requested_days,
        "notice_working_days": notice_working_days,
    }
