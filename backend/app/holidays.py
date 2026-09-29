"""Festival holiday calendar distilled from Section K of the Code 19 Leave Policy, plus the
company's weekly off-days. Kept as structured data (not left to the LLM to recall) so the
chat agent's leave-planning suggestions are grounded in real dates rather than guesses —
fixed-date holidays get an actual resolved date/weekday; moon-sighting or government-declared
ones are surfaced honestly as "not fixed yet" instead of being fabricated.
"""

import datetime as dt

WEEKLY_OFF_DAYS = {4: "Friday", 5: "Saturday"}  # date.weekday(): Monday=0 ... Sunday=6

FESTIVAL_HOLIDAYS = [
    {"name": "International Mother Language Day", "month": 2, "day": 21, "days": 1, "fixed": True},
    {"name": "Birthday of Father of the Nation", "month": 3, "day": 1, "days": 1, "fixed": True},
    {"name": "Independence & National Day", "month": 3, "day": 26, "days": 1, "fixed": True},
    {"name": "Bangali New Year", "month": 4, "day": 14, "days": 1, "fixed": True},
    {"name": "International Labor Day", "month": 5, "day": 1, "days": 1, "fixed": True},
    {"name": "National Mourning Day", "month": 8, "day": 15, "days": 1, "fixed": True},
    {"name": "Victory Day", "month": 12, "day": 16, "days": 1, "fixed": True},
    {"name": "Christmas", "month": 12, "day": 25, "days": 1, "fixed": True},
    {"name": "Buddha Purnima", "days": 1, "fixed": False, "note": "date set by Government declaration"},
    {"name": "Shab-E-Barat", "days": 1, "fixed": False, "note": "depends on moon sighting"},
    {"name": "Shab-E-Qadr", "days": 1, "fixed": False, "note": "depends on moon sighting"},
    {"name": "Eid-Ul-Fitr", "days": 3, "fixed": False, "note": "depends on moon sighting"},
    {"name": "Janmashtami", "days": 1, "fixed": False, "note": "date set by Government declaration"},
    {"name": "Eid-Ul-Azha", "days": 3, "fixed": False, "note": "date set by Government declaration"},
    {"name": "Ashura", "days": 1, "fixed": False, "note": "date set by Government declaration"},
    {"name": "Durga Puja", "days": 1, "fixed": False, "note": "date set by Government declaration"},
    {"name": "Eid-E-Miladunnabi", "days": 1, "fixed": False, "note": "depends on moon sighting"},
]


def build_holiday_context(today: dt.date, horizon_days: int = 240) -> str:
    lines = [
        "Weekly off days: Friday and Saturday (the work week runs Sunday-Thursday).",
        f"Today is {today.isoformat()} ({today.strftime('%A')}).",
        "Upcoming fixed-date festival holidays:",
    ]
    horizon = today + dt.timedelta(days=horizon_days)
    found_fixed = False
    for h in FESTIVAL_HOLIDAYS:
        if not h.get("fixed"):
            continue
        for year in (today.year, today.year + 1):
            d = dt.date(year, h["month"], h["day"])
            if today <= d <= horizon:
                lines.append(f"- {h['name']}: {d.isoformat()} ({d.strftime('%A')}), {h['days']} day(s)")
                found_fixed = True
    if not found_fixed:
        lines.append("- (none within the next few months)")

    lines.append(
        "Other festival holidays exist (Eid-Ul-Fitr, Eid-Ul-Azha, Shab-E-Barat, Shab-E-Qadr, "
        "Eid-E-Miladunnabi, Buddha Purnima, Janmashtami, Ashura, Durga Puja) but their exact dates are "
        "set by moon sighting or government declaration and are NOT known in advance — if asked about "
        "these, say the date isn't fixed yet rather than guessing one."
    )
    return "\n".join(lines)
