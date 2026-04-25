from __future__ import annotations

from datetime import date, timedelta


FIXED_SPECIAL_DAYS = {
    "09-23": {"name": "Saudi National Day", "tone": "patriotic"},
    "02-22": {"name": "Saudi Founding Day", "tone": "proud"},
    "03-11": {"name": "Flag Day", "tone": "patriotic"},
    "12-02": {"name": "UAE National Day", "tone": "celebratory"},
    "05-25": {"name": "Jordan Independence Day", "tone": "celebratory"},
}


def _get_islamic_days_for_year(gregorian_year: int) -> dict[str, dict]:
    """Calculate Islamic special days for a given Gregorian year using hijri-converter."""
    try:
        from hijri_converter import Gregorian, Hijri

        jan1_hijri = Gregorian(gregorian_year, 1, 1).to_hijri()
        hijri_year = jan1_hijri.year

        islamic: dict[str, dict] = {}

        for h_year in [hijri_year, hijri_year + 1]:
            candidates = [
                (9, 1, "Ramadan Start", "spiritual"),
                (10, 1, "Eid Al-Fitr", "celebratory"),
                (12, 10, "Eid Al-Adha", "celebratory"),
                (3, 12, "Prophet's Birthday", "spiritual"),
            ]
            for h_month, h_day, name, tone in candidates:
                try:
                    g = Hijri(h_year, h_month, h_day).to_gregorian()
                    if g.year == gregorian_year:
                        key = date(g.year, g.month, g.day).isoformat()
                        islamic[key] = {"name": name, "tone": tone}
                except Exception:
                    pass

        return islamic
    except ImportError:
        return {}


def get_special_days_in_range(start_date: date, end_date: date) -> dict[str, dict]:
    years = set(range(start_date.year, end_date.year + 1))
    all_islamic: dict[str, dict] = {}
    for year in years:
        all_islamic.update(_get_islamic_days_for_year(year))

    result: dict[str, dict] = {}
    cursor = start_date
    while cursor <= end_date:
        key_mm_dd = cursor.strftime("%m-%d")
        iso = cursor.isoformat()
        if key_mm_dd in FIXED_SPECIAL_DAYS:
            result[iso] = FIXED_SPECIAL_DAYS[key_mm_dd]
        elif iso in all_islamic:
            result[iso] = all_islamic[iso]
        cursor += timedelta(days=1)
    return result
