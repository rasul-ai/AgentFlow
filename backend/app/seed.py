import datetime as dt

from sqlmodel import Session, select

from app.auth import hash_password
from app.db import engine
from app.models import Employee, Gender, HRUser, LeaveRequest, LeaveType, RequestStatus
from app.policy_rules import calendar_days_inclusive

DEMO_PASSWORD = "password123"
DEMO_HR_PASSWORD = "hrpass123"

DEMO_EMPLOYEES = [
    dict(
        name="Ayesha Rahman",
        email="ayesha.rahman@code19.com",
        username="ayesha",
        title="Senior Software Engineer",
        gender=Gender.female,
        date_of_joining=dt.date(2020, 3, 2),
        is_confirmed=True,
        confirmation_date=dt.date(2020, 6, 2),
        manager_name="Farhana Khan",
        manager_email="farhana.khan@code19.com",
    ),
    dict(
        name="Tanvir Ahmed",
        email="tanvir.ahmed@code19.com",
        username="tanvir",
        title="Product Designer",
        gender=Gender.male,
        date_of_joining=dt.date(2022, 5, 15),
        is_confirmed=True,
        confirmation_date=dt.date(2022, 8, 15),
        manager_name="Farhana Khan",
        manager_email="farhana.khan@code19.com",
    ),
    dict(
        name="Nusrat Jahan",
        email="nusrat.jahan@code19.com",
        username="nusrat",
        title="Marketing Associate",
        gender=Gender.female,
        date_of_joining=dt.date(2026, 4, 1),
        is_confirmed=False,
        confirmation_date=None,
        manager_name="Imtiaz Farhan Bin Habib",
        manager_email="imtiaz.habib@code19.com",
    ),
    dict(
        name="Rakib Hasan",
        email="rakib.hasan@code19.com",
        username="rakib",
        title="DevOps Engineer",
        gender=Gender.male,
        date_of_joining=dt.date(2019, 11, 1),
        is_confirmed=True,
        confirmation_date=dt.date(2020, 2, 1),
        manager_name="Imtiaz Farhan Bin Habib",
        manager_email="imtiaz.habib@code19.com",
    ),
    dict(
        name="Farzana Islam",
        email="farzana.islam@code19.com",
        username="farzana",
        title="QA Engineer",
        gender=Gender.female,
        date_of_joining=dt.date(2021, 7, 10),
        is_confirmed=True,
        confirmation_date=dt.date(2021, 10, 10),
        manager_name="Farhana Khan",
        manager_email="farhana.khan@code19.com",
    ),
]

DEMO_HR_USERS = [
    dict(
        name="Farhana Khan",
        email="farhana.khan@code19.com",
        username="farhana",
        title="HR Manager",
    ),
    dict(
        name="Imtiaz Farhan Bin Habib",
        email="imtiaz.habib@code19.com",
        username="imtiaz",
        title="Director, Business Development",
    ),
]

# username -> list of historical leave requests. Seeded directly (not run through the live
# LangGraph pipeline) so a fresh install has realistic-looking balances/history without
# depending on a working Ollama connection just to seed. agent_trace/citations are static
# text that mirrors what the live pipeline would have produced.
HISTORICAL_REQUESTS: dict[str, list[dict]] = {
    "ayesha": [
        dict(
            leave_type=LeaveType.CL,
            start_date=dt.date(2026, 1, 15),
            end_date=dt.date(2026, 1, 16),
            reason="Personal errand",
            status=RequestStatus.approved,
            citations=["Section D"],
            summary="Casual Leave approved — within the 2-day consecutive limit and sufficient balance (Section D.2).",
        ),
        dict(
            leave_type=LeaveType.SL,
            start_date=dt.date(2026, 3, 3),
            end_date=dt.date(2026, 3, 3),
            reason="Fever",
            status=RequestStatus.approved,
            citations=["Section E"],
            summary="Sick Leave approved — single day, no medical certificate required (Section E.2).",
        ),
        dict(
            leave_type=LeaveType.EL,
            start_date=dt.date(2026, 5, 4),
            end_date=dt.date(2026, 5, 8),
            reason="Family vacation",
            status=RequestStatus.approved,
            citations=["Section F"],
            summary="Earned Leave approved — notice period and balance requirements satisfied (Section F.1).",
        ),
    ],
    "tanvir": [
        dict(
            leave_type=LeaveType.CL,
            start_date=dt.date(2026, 2, 2),
            end_date=dt.date(2026, 2, 3),
            reason="Moving apartment",
            status=RequestStatus.approved,
            citations=["Section D"],
            summary="Casual Leave approved — within the 2-day consecutive limit (Section D.2).",
        ),
        dict(
            leave_type=LeaveType.SL,
            start_date=dt.date(2026, 4, 20),
            end_date=dt.date(2026, 4, 21),
            reason="Flu",
            medical_certificate_confirmed=True,
            status=RequestStatus.approved,
            citations=["Section E"],
            summary="Sick Leave approved — medical certificate provided for the 2-day absence (Section E.2).",
        ),
        dict(
            leave_type=LeaveType.EL,
            start_date=dt.date(2026, 6, 3),
            end_date=dt.date(2026, 6, 5),
            reason="Short trip",
            status=RequestStatus.rejected_by_agent,
            eligible=False,
            citations=["Section F"],
            summary="Earned Leave request declined — only 2 working days' notice given; policy requires at least 10 (Section F.1).",
            submitted_offset_days=-2,
        ),
    ],
    "nusrat": [
        dict(
            leave_type=LeaveType.CL,
            start_date=dt.date(2026, 8, 24),
            end_date=dt.date(2026, 8, 25),
            reason="Attending a family function",
            status=RequestStatus.pending_manager,
            citations=["Section D"],
            summary="Casual Leave request satisfies all applicable policy conditions (Section D.2).",
            filled_application_text=(
                "Dear Mr. Imtiaz Farhan Bin Habib,\n\nI would like to request Casual Leave (CL) for the period "
                "of 24th August 2026 to 25th August 2026, totaling 2 days, to attend a family function. I have "
                "sufficient leave balance and the duration complies with company policy. Kindly approve this "
                "request.\n\nThank you.\n\nSincerely,\nNusrat Jahan"
            ),
            submitted_offset_days=-15,
        ),
    ],
    "rakib": [
        dict(
            leave_type=LeaveType.CL,
            start_date=dt.date(2026, 1, 20),
            end_date=dt.date(2026, 1, 20),
            is_half_day=True,
            reason="Doctor's appointment",
            status=RequestStatus.approved,
            citations=["Section D"],
            summary="Half-day Casual Leave approved — within the 4-hour limit (Section D.3).",
        ),
        dict(
            leave_type=LeaveType.SL,
            start_date=dt.date(2026, 2, 10),
            end_date=dt.date(2026, 2, 10),
            reason="Migraine",
            status=RequestStatus.approved,
            citations=["Section E"],
            summary="Sick Leave approved — single day, no medical certificate required (Section E.2).",
        ),
        dict(
            leave_type=LeaveType.EL,
            start_date=dt.date(2026, 6, 15),
            end_date=dt.date(2026, 6, 19),
            reason="Hometown visit",
            status=RequestStatus.approved,
            citations=["Section F"],
            summary="Earned Leave approved — notice period and balance requirements satisfied (Section F.1).",
        ),
        dict(
            leave_type=LeaveType.EL,
            start_date=dt.date(2026, 7, 20),
            end_date=dt.date(2026, 7, 21),
            reason="Extended weekend trip",
            status=RequestStatus.rejected_by_manager,
            citations=["Section F"],
            summary="Earned Leave request satisfies all applicable policy conditions (Section F.1).",
            decision_comment="Team is fully booked that week — please pick alternate dates.",
            submitted_offset_days=-12,
        ),
    ],
    "farzana": [
        dict(
            leave_type=LeaveType.CL,
            start_date=dt.date(2026, 3, 10),
            end_date=dt.date(2026, 3, 11),
            reason="Home renovation",
            status=RequestStatus.approved,
            citations=["Section D"],
            summary="Casual Leave approved — within the 2-day consecutive limit (Section D.2).",
        ),
        dict(
            leave_type=LeaveType.EL,
            start_date=dt.date(2026, 4, 1),
            end_date=dt.date(2026, 4, 3),
            reason="Sister's wedding",
            status=RequestStatus.approved,
            citations=["Section F"],
            summary="Earned Leave approved — notice period and balance requirements satisfied (Section F.1).",
        ),
    ],
}


def _build_leave_request(employee_id: int, spec: dict) -> LeaveRequest:
    requested_days = 0.5 if spec.get("is_half_day") else calendar_days_inclusive(spec["start_date"], spec["end_date"])
    submitted_at = dt.datetime.combine(
        spec["start_date"] + dt.timedelta(days=spec.get("submitted_offset_days", -14)), dt.time(9, 30)
    )
    status: RequestStatus = spec["status"]
    eligible = spec.get("eligible", status != RequestStatus.rejected_by_agent)
    decided_at = None
    if status in (RequestStatus.approved, RequestStatus.rejected_by_manager):
        decided_at = submitted_at + dt.timedelta(days=1)
    elif status == RequestStatus.rejected_by_agent:
        decided_at = submitted_at

    filled_application_text = spec.get("filled_application_text")
    if filled_application_text is None and status != RequestStatus.rejected_by_agent:
        filled_application_text = (
            f"Formal {spec['leave_type'].value} application for {spec['start_date']} to {spec['end_date']} "
            f"({requested_days} day(s)) — {spec['reason']}."
        )

    return LeaveRequest(
        employee_id=employee_id,
        leave_type=spec["leave_type"],
        start_date=spec["start_date"],
        end_date=spec["end_date"],
        is_half_day=spec.get("is_half_day", False),
        reason=spec["reason"],
        medical_certificate_confirmed=spec.get("medical_certificate_confirmed", False),
        child_dob=spec.get("child_dob"),
        submitted_at=submitted_at,
        status=status,
        requested_days=requested_days,
        eligible=eligible,
        agent_trace=spec.get(
            "agent_trace",
            [
                f"Policy Retrieval: fetched relevant clause(s) from the Code 19 Leave Policy ({', '.join(spec['citations'])}).",
                f"Eligibility Agent: verdict = {'ELIGIBLE' if eligible else 'NOT ELIGIBLE'}.",
            ]
            + (["Application Filler Agent: drafted the leave application and routed it for approval."] if eligible else []),
        ),
        eligibility_reasons=[spec["summary"]],
        policy_citations=spec["citations"],
        needs_senior_approval=spec.get("needs_senior_approval", False),
        filled_application_text=filled_application_text,
        decision_comment=spec.get("decision_comment"),
        decided_at=decided_at,
    )


def seed_if_empty() -> None:
    with Session(engine) as session:
        existing = session.exec(select(Employee)).first()
        if existing:
            return

        username_to_id: dict[str, int] = {}
        for data in DEMO_EMPLOYEES:
            employee = Employee(**data, password_hash=hash_password(DEMO_PASSWORD))
            session.add(employee)
            session.flush()
            username_to_id[data["username"]] = employee.id

        for data in DEMO_HR_USERS:
            session.add(HRUser(**data, password_hash=hash_password(DEMO_HR_PASSWORD)))

        for username, requests in HISTORICAL_REQUESTS.items():
            employee_id = username_to_id[username]
            for spec in requests:
                session.add(_build_leave_request(employee_id, spec))

        session.commit()
