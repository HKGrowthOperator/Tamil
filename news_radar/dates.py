"""Deutsche Datumsangaben aus Webseiten parsen – klein und vorhersehbar statt dateparser."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Berlin")

MONTHS = {
    "januar": 1, "jan": 1, "februar": 2, "feb": 2, "märz": 3, "maerz": 3, "mär": 3, "mar": 3, "april": 4, "apr": 4,
    "mai": 5, "juni": 6, "jun": 6, "juli": 7, "jul": 7, "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "oktober": 10, "okt": 10, "oct": 10, "november": 11, "nov": 11, "dezember": 12, "dez": 12, "dec": 12,
}
_MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))
_TIME_RE = re.compile(r"(?<!\d)(\d{1,2})[:.](\d{2})(?:\s*uhr)?", re.I)
_ISO_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?")
_NUMERIC_RE = re.compile(r"(?<!\d)(\d{1,2})\.(\d{1,2})\.(\d{2,4})(?!\d)")
_NUMERIC_NOYEAR_RE = re.compile(r"(?<!\d)(\d{1,2})\.(\d{1,2})\.(?!\d)")
_DAY_MONTH_RE = re.compile(rf"(?<!\d)(\d{{1,2}})\.?\s*({_MONTH_RE})\.?\s*(\d{{4}})?", re.I)
_MONTH_DAY_RE = re.compile(rf"\b({_MONTH_RE})\.?\s+(\d{{1,2}})(?:\s*,?\s*(\d{{4}}))?", re.I)


def _year_for(month: int, day: int, now: date) -> int:
    """Ohne Jahresangabe: das nächste Datum in der Zukunft (max. 2 Monate zurück)."""
    year = now.year
    try:
        candidate = date(year, month, day)
    except ValueError:
        return year
    if candidate < now - timedelta(days=60):
        return year + 1
    return year


def parse_de_datetime(text: str, now: datetime | None = None) -> datetime | None:
    """„Sa, 7.11.2026 19:30“, „7. November 2026“, „Okt 17“, „07.11.26“, ISO, heute/morgen → datetime (Europe/Berlin)."""
    if not text:
        return None
    now = now or datetime.now(TZ)
    today = now.date()
    t = text.strip()
    low = t.lower()
    day = month = year = None

    if m := _ISO_RE.search(t):
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        hour, minute = (int(m.group(4)), int(m.group(5))) if m.group(4) else (0, 0)
        try:
            return datetime(year, month, day, hour, minute, tzinfo=TZ)
        except ValueError:
            return None
    if "übermorgen" in low:
        d = today + timedelta(days=2)
        day, month, year = d.day, d.month, d.year
    elif "morgen" in low:
        d = today + timedelta(days=1)
        day, month, year = d.day, d.month, d.year
    elif "heute" in low:
        day, month, year = today.day, today.month, today.year
    elif m := _NUMERIC_RE.search(t):
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if year < 100:
            year += 2000
    elif m := _DAY_MONTH_RE.search(t):
        day, month = int(m.group(1)), MONTHS[m.group(2).lower()]
        year = int(m.group(3)) if m.group(3) else _year_for(month, day, today)
    elif m := _MONTH_DAY_RE.search(t):
        month, day = MONTHS[m.group(1).lower()], int(m.group(2))
        year = int(m.group(3)) if m.group(3) else _year_for(month, day, today)
    elif m := _NUMERIC_NOYEAR_RE.search(t):
        day, month = int(m.group(1)), int(m.group(2))
        year = _year_for(month, day, today)
    if day is None:
        return None

    hour = minute = 0
    # Uhrzeit nur nach dem Datum suchen, damit „7.11.“ nicht als 7:11 gelesen wird
    tail = t[m.end():] if "m" in locals() and m else t
    if tm := _TIME_RE.search(tail):
        hour, minute = int(tm.group(1)), int(tm.group(2))
        if hour > 23 or minute > 59:
            hour = minute = 0
    try:
        return datetime(year, month, day, hour, minute, tzinfo=TZ)
    except ValueError:
        return None


def parse_de_date(text: str, now: datetime | None = None) -> date | None:
    dt = parse_de_datetime(text, now)
    return dt.date() if dt else None
