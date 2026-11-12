"""Uhrzeiten mit a.m./p.m. (englische Terminseiten, z. B. Tempel Backnang: „November 13, 2026 6:00 p.m.“).

Fund 12.11.2026: „6:00 p.m.“ wurde als 06:00 gelesen. Deutsche Angaben bleiben, wie sie waren; das deutsche Wort
„am“ („10:30 am Bahnhof“) ist keine Uhrzeitangabe."""

from datetime import datetime

import pytest

from news_radar.dates import TZ, parse_de_termin

NOW = datetime(2026, 11, 1, 12, tzinfo=TZ)


def _zeit(text):
    dt, hat_zeit = parse_de_termin(text, NOW)
    return dt.strftime("%Y-%m-%d %H:%M"), hat_zeit


@pytest.mark.parametrize("text, erwartet", [
    ("November 13, 2026 6:00 p.m. – November 13, 2026 9:30 p.m.", "2026-11-13 18:00"),
    ("7.11.2026 6:00 pm", "2026-11-07 18:00"),
    ("7.11.2026 6 PM", "2026-11-07 18:00"),
    ("7.11.2026 6:30 P.M.", "2026-11-07 18:30"),
    ("7.11.2026 6:30p.m.", "2026-11-07 18:30"),
    ("7.11.2026 12:00 p.m.", "2026-11-07 12:00"),
    ("7.11.2026 12:15 a.m.", "2026-11-07 00:15"),
    ("November 16, 2026 9:00 a.m. – November 16, 2026 1:30 p.m.", "2026-11-16 09:00"),
    ("Saturday, November 21, 2026 at 10 AM", "2026-11-21 10:00"),
])
def test_am_pm(text, erwartet):
    assert _zeit(text) == (erwartet, True)


@pytest.mark.parametrize("text, erwartet", [
    ("7.11.2026 18:00 Uhr", ("2026-11-07 18:00", True)),
    ("Sa, 7.11.2026 19:30", ("2026-11-07 19:30", True)),
    ("7.11.2026 18 Uhr", ("2026-11-07 00:00", False)),  # wie bisher: volle Stunde ohne Minuten nicht erkannt
    ("7.11.2026 um 10:30 am Bahnhof", ("2026-11-07 10:30", True)),  # deutsches „am“
    ("7.11.2026, 19:30, Treffpunkt p.m. Hall", ("2026-11-07 19:30", True)),  # „p.m.“ ohne Uhrzeit davor
    ("7.11.2026, Einlass ab 5 am Eingang", ("2026-11-07 00:00", False)),
    ("7.11.2026, Saal p.m. 3", ("2026-11-07 00:00", False)),
])
def test_deutsch_und_gegenproben_unveraendert(text, erwartet):
    assert _zeit(text) == erwartet


def test_ungueltige_stunde_mit_pm_faellt_auf_bisherige_regel_zurueck():
    assert _zeit("7.11.2026 18:00 p.m.") == ("2026-11-07 18:00", True)  # 18 p.m. gibt es nicht: 24-h-Zeit gilt


@pytest.mark.parametrize("text, erwartet", [
    ("7.11.2026 6–9 pm", ("2026-11-07 18:00", True)),
    ("7.11.2026 6-9 PM", ("2026-11-07 18:00", True)),
    ("7.11.2026 6 – 9 p.m.", ("2026-11-07 18:00", True)),
    ("7.11.2026 9–11 a.m.", ("2026-11-07 09:00", True)),
    ("7.11.2026 12–3 pm", ("2026-11-07 12:00", True)),
    # über Mittag: Beginn am Vormittag
    ("7.11.2026 11–1 pm", ("2026-11-07 11:00", True)),
    ("7.11.2026 10-2 PM", ("2026-11-07 10:00", True)),
    ("7.11.2026 11-12 pm", ("2026-11-07 11:00", True)),
    # erste Zahl keine 12-Stunden-Zeit: wie früher die zweite Zahl mit Zusatz
    ("7.11.2026 15 - 6 pm", ("2026-11-07 18:00", True)),
    ("7.11.2026 13-9 pm", ("2026-11-07 21:00", True)),
    ("7.11.2026 0-9 pm", ("2026-11-07 21:00", True)),
    # Zahl gehört zu einem Wort davor (Saal 2, Tag 1, Nr. 3): keine Spanne
    ("7.11.2026 Saal 2 – 6 pm", ("2026-11-07 18:00", True)),
    ("7.11.2026 Tag 1 - 6 pm", ("2026-11-07 18:00", True)),
    ("7.11.2026 Halle 3-7 p.m.", ("2026-11-07 19:00", True)),
    ("7.11.2026 Nr. 4 – 8 PM", ("2026-11-07 20:00", True)),
])
def test_spanne_ohne_doppelpunkt_beginn_mit_gemeinsamem_zusatz(text, erwartet):
    assert _zeit(text) == erwartet


@pytest.mark.xfail(strict=True, reason="Spanne mit Doppelpunkt: Die erste Zeit gilt als 24-Stunden-Zeit (06:00), "
                   "der gemeinsame Zusatz „p.m.“ am Ende wird nicht übernommen. Richtig wäre 18:00; offen.")
def test_spanne_mit_doppelpunkt_uebernimmt_gemeinsamen_zusatz():
    assert _zeit("7.11.2026 6:00 – 9:30 p.m.") == ("2026-11-07 18:00", True)
