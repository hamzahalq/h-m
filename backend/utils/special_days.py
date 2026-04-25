from __future__ import annotations

from datetime import date, timedelta


FIXED_SPECIAL_DAYS = {
    "09-23": {"name": "Saudi National Day", "tone": "patriotic"},
    "02-22": {"name": "Saudi Founding Day", "tone": "proud"},
    "03-11": {"name": "Flag Day", "tone": "patriotic"},
    "12-02": {"name": "UAE National Day", "tone": "celebratory"},
    "05-25": {"name": "Jordan Independence Day", "tone": "celebratory"},
}


def get_special_days_in_range(start_date: date, end_date: date) -> dict[str, dict]:
    result: dict[str, dict] = {}
    cursor = start_date
    while cursor <= end_date:
        key = cursor.strftime("%m-%d")
        if key in FIXED_SPECIAL_DAYS:
            result[cursor.isoformat()] = FIXED_SPECIAL_DAYS[key]
        cursor += timedelta(days=1)
    return result
