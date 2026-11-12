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
    "january": 1, "february": 2, "march": 3, "june": 6, "july": 7, "october": 10, "december": 12,
    # tamilische Monatsnamen (Schreibweisen aus Sri Lanka und Indien), wie sie Swiss Tamil Info & Co. verwenden
    "ஜனவரி": 1, "பெப்ரவரி": 2, "பிப்ரவரி": 2, "மார்ச்": 3, "ஏப்ரல்": 4, "மே": 5, "ஜூன்": 6, "ஜூலை": 7,
    "ஆகஸ்ட்": 8, "ஓகஸ்ட்": 8, "ஆகஸ்டு": 8, "செப்டம்பர்": 9, "ஒக்டோபர்": 10, "அக்டோபர்": 10, "நவம்பர்": 11,
    "டிசம்பர்": 12,
}
_MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))
_TIME_RE = re.compile(r"(?<!\d)(\d{1,2})[:.](\d{2})(?:\s*uhr)?", re.I)
# 12-Stunden-Uhrzeit: „6:00 p.m.“, „6:30 P.M.“, „6 pm“, „10 AM“. Ohne Punkte nur „pm“, „AM“, „PM“ – das kleine
# „am“ ist im Deutschen eine Präposition („10:30 am Bahnhof“) und bleibt außen vor. Spanne ohne Doppelpunkt
# („6–9 pm“): Beginn ist die erste Stunde mit dem gemeinsamen Zusatz; über Mittag („11–1 pm“) am Vormittag.
_AMPM_RE = re.compile(r"(?<![\d:.])(?:(\d{1,2})\s*[–—-]\s*)?(\d{1,2})(?:[:.](\d{2}))?\s*"
                      r"(?:([aApP])\.\s?[mM]\.?|(AM|PM|pm)(?![A-Za-z]))")
# Zahl vor dem Bindestrich gehört zu solch einem Wort („Saal 2 – 6 pm“, „Tag 1 - 6 pm“): keine Spanne
_NUMMERN_WORT_RE = re.compile(r"\b(?:saal|tag|day|halle|hall|raum|room|zimmer|nr|no|bühne|stage|gate|tor|platz|"
                              r"gleis|block|haus|teil|runde|level|ebene|stock|eingang|sektor|court|feld)\.?\s*$", re.I)


def _ampm_zeit(ap: re.Match, davor: str) -> tuple[int, int] | None:
    """(Stunde, Minute) im 24-Stunden-Format aus einem _AMPM_RE-Treffer; None, wenn ungültig."""
    nachmittag = (ap.group(4) or ap.group(5)).lower().startswith("p")
    ende, minuten = int(ap.group(2)), int(ap.group(3) or 0)
    if not 1 <= ende <= 12 or minuten > 59:
        return None
    ende24 = ende % 12 + (12 if nachmittag else 0)
    if ap.group(1) and not _NUMMERN_WORT_RE.search(davor):
        anfang = int(ap.group(1))
        if 1 <= anfang <= 12:
            # „6–12 pm“: Abend bis Mitternacht; „11–1 pm“, „10–12 pm“: Vormittag (bei Ende 12 erst ab 9 Uhr)
            bis_mitternacht = nachmittag and ende == 12 and anfang < 9
            vormittag = nachmittag and anfang % 12 > ende % 12 and not bis_mitternacht
            anfang24 = anfang % 12 + (12 if nachmittag and not vormittag else 0)
            ende_spanne = 24 if bis_mitternacht else ende24
            if anfang24 * 60 < ende_spanne * 60 + minuten and ende_spanne - anfang24 <= 12:  # Beginn vor Ende
                return anfang24, 0
    return ende24, minuten


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
    return parse_de_termin(text, now)[0]


def parse_de_termin(text: str, now: datetime | None = None) -> tuple[datetime | None, bool]:
    """Wie parse_de_datetime, dazu, ob der Text eine Uhrzeit nennt (sonst steht 00:00 nur als Platzhalter)."""
    if not text:
        return None, False
    now = now or datetime.now(TZ)
    today = now.date()
    t = text.strip()
    low = t.lower()
    day = month = year = None

    if m := _ISO_RE.search(t):
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        hour, minute = (int(m.group(4)), int(m.group(5))) if m.group(4) else (0, 0)
        try:
            return datetime(year, month, day, hour, minute, tzinfo=TZ), bool(m.group(4))
        except ValueError:
            return None, False
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
        return None, False

    hour = minute = 0
    hat_zeit = False
    # Uhrzeit nur nach dem Datum suchen, damit „7.11.“ nicht als 7:11 gelesen wird
    tail = t[m.end():] if "m" in locals() and m else t
    tm = _TIME_RE.search(tail)
    ap = _AMPM_RE.search(tail)
    zwoelf = _ampm_zeit(ap, tail[:ap.start()]) if ap and (tm is None or ap.start() <= tm.start()) else None
    if zwoelf:
        hour, minute = zwoelf
        hat_zeit = True
    elif tm:
        hour, minute = int(tm.group(1)), int(tm.group(2))
        hat_zeit = True
        if hour > 23 or minute > 59:
            hour = minute = 0
            hat_zeit = False
    try:
        return datetime(year, month, day, hour, minute, tzinfo=TZ), hat_zeit
    except ValueError:
        return None, False


def parse_de_date(text: str, now: datetime | None = None) -> date | None:
    dt = parse_de_datetime(text, now)
    return dt.date() if dt else None


_MONTH_DAY_ALL_RE = re.compile(rf"\b({_MONTH_RE})\.?\s+(\d{{1,2}})(?!\d)(?:\s*,?\s*(\d{{4}}))?", re.I)


def alle_daten(text: str, now: datetime | None = None) -> list[date]:
    """Alle Kalenderdaten in einem Text (ISO, 7.11.2026, 7.11., 7. November 2026, Nov 7) – ohne heute/morgen."""
    if not text:
        return []
    today = (now or datetime.now(TZ)).date()
    gefunden: set[date] = set()

    def add(year: int, month: int, day: int) -> None:
        try:
            gefunden.add(date(year, month, day))
        except ValueError:
            pass

    for m in _ISO_RE.finditer(text):
        add(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    for m in _NUMERIC_RE.finditer(text):
        year = int(m.group(3))
        add(year + 2000 if year < 100 else year, int(m.group(2)), int(m.group(1)))
    for m in _NUMERIC_NOYEAR_RE.finditer(text):
        day, month = int(m.group(1)), int(m.group(2))
        add(_year_for(month, day, today), month, day)
    for m in _DAY_MONTH_RE.finditer(text):
        day, month = int(m.group(1)), MONTHS[m.group(2).lower()]
        add(int(m.group(3)) if m.group(3) else _year_for(month, day, today), month, day)
    for m in _MONTH_DAY_ALL_RE.finditer(text):
        month, day = MONTHS[m.group(1).lower()], int(m.group(2))
        add(int(m.group(3)) if m.group(3) else _year_for(month, day, today), month, day)
    return sorted(gefunden)
