"""Abnahme-Nachläufe für das Verzeichnis (Festlegung F2, Abnahmetest T4, Szenarien 88 und 89): Einsendungen über den
Fake-Transport der Website, Prüfung mit FakeClaude (oder ohne Modell), Entscheidung wie im Cockpit. Alle Angaben sind
erfunden (example.test)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime

from .. import schalter, verzeichnis
from ..wordpress import TamilRadarClient
from ..web.rechte import darf
from .wp_verzeichnis import FakeWordPressVerzeichnis

EINSENDER = ("Erika Beispiel", "erika@example.test")
VEREIN = {"name": "Tamilischer Kulturverein Essen", "art": "verein", "beschreibung": "Tanz, Musik und Sprachkurse.",
          "plz": "45127", "stadt": "Essen", "land": "DE", "bundesland_kanton": "Nordrhein-Westfalen",
          "telefon": "+49 201 1234567", "website": "https://verein.example.test"}


def _client(wp: FakeWordPressVerzeichnis) -> TamilRadarClient:
    return TamilRadarClient("https://www.tamil.test", "ki-agent", "app-pw", session=wp)


def _ohne_personendaten(store) -> int:
    zeilen = [str(dict(r)) for r in store.db.execute("SELECT * FROM editorial_actions")]
    zeilen += [str(r) for r in store.iter_log()]
    return int(not any(p in z for z in zeilen for p in EINSENDER))


def _schreibend(wp) -> int:
    return sum(1 for _, r, _ in wp.koerper if r.startswith("eintrag"))


def t4(ctx, sz, now: datetime) -> dict:
    """T4: vorschlagen → Hinweise → freigeben; Telefon ändern → alt/neu → freigeben; Ablehnen ändert nichts;
    Dublette erkannt; Premium nicht setzbar; ohne Stadt unvollständig."""
    store, wp = ctx.store, FakeWordPressVerzeichnis()
    c = _client(wp)
    out: Counter = Counter()
    # 1. Vorschlag → Prüfung mit Hinweisen und Kategorie-Vorschlag → Freigabe → öffentlich
    v1 = wp.einreichen("neu", VEREIN)
    ohne_stadt = wp.einreichen("neu", {**{k: w for k, w in VEREIN.items() if k != "stadt"},
                                       "name": "Tamilschule Nord", "plz": "45139", "telefon": "+49 201 555555"})
    out.update({f"vz_{k}": n for k, n in verzeichnis.lauf(store, c, ctx.claude).items()})
    e1 = verzeichnis.holen(store, v1)
    out["kategorie_vorschlag"] = int(e1["pruefung"]["kategorie_vorschlag"] == "verein-kultur")
    out["pruefung_bei_wp"] = int(wp.einsendung(v1)["status"] == "geprueft" and bool(wp.einsendung(v1)["pruefung"]))
    try:
        verzeichnis.freigeben(store, c, v1, von="priya", werte={"premium": "1"})
    except ValueError:
        out["premium_abgewiesen"] += 1
    out["premium_ohne_aufruf"] = int(_schreibend(wp) == 0)
    eid = verzeichnis.freigeben(store, c, v1, von="priya", kategorie=e1["pruefung"]["kategorie_vorschlag"])["eintrag"]["id"]
    eintrag = wp.eintraege[eid]
    out["veroeffentlicht"] = int(eintrag["status"] == "veroeffentlicht" and eintrag["felder"]["stadt"] == "Essen")
    out["premium_aus"] = int(eintrag["premium"] is False)
    # 2. ohne Stadt: nicht ergänzt, als unvollständig markiert
    e2 = verzeichnis.holen(store, ohne_stadt)
    out["unvollstaendig"] = int("stadt" in e2["pruefung"]["fehlt"] and verzeichnis.vorschlag(e2)["stadt"] == verzeichnis.FEHLT)
    # 3. derselbe Verein noch einmal: mögliche Dublette mit Verweis
    v3 = wp.einreichen("neu", {**VEREIN, "name": "Tamilischer Kulturverein Essen e. V."}, email="max@example.test")
    verzeichnis.lauf(store, c, ctx.claude)
    out["dublette"] = int([d["eintrag_id"] for d in verzeichnis.holen(store, v3)["pruefung"]["dubletten"]] == [eid])
    # 4. Telefon ändern → alt neben neu → freigeben → neue Nummer
    v4 = wp.einreichen("aenderung", {"telefon": "+49 201 7654321"}, eintrag_id=eid)
    verzeichnis.lauf(store, c, ctx.claude)
    zeilen = {z["feld"]: z for z in verzeichnis.vergleich(verzeichnis.holen(store, v4))}
    out["alt_neu"] = int((zeilen["telefon"]["alt"], zeilen["telefon"]["neu"]) == ("+49 201 1234567", "+49 201 7654321"))
    verzeichnis.freigeben(store, c, v4, von="priya", annehmen=["telefon"])
    out["neue_nummer"] = int(wp.eintraege[eid]["felder"]["telefon"] == "+49 201 7654321")
    # 5. Ablehnen ändert nichts
    v5 = wp.einreichen("aenderung", {"telefon": "+49 201 0000000"}, eintrag_id=eid)
    verzeichnis.lauf(store, c, ctx.claude)
    vorher, schreib = dict(wp.eintraege[eid]["felder"]), _schreibend(wp)
    verzeichnis.ablehnen(store, c, v5, von="priya")
    out["ablehnen_aendert_nichts"] = int(wp.eintraege[eid]["felder"] == vorher and _schreibend(wp) == schreib
                                         and wp.einsendung(v5)["status"] == "abgelehnt")
    out["leser_darf"] = int(darf("verzeichnis_entscheiden", "leser"))
    out["ohne_personendaten"] = _ohne_personendaten(store)
    return dict(out)


def im_stopp(ctx, sz, now: datetime) -> dict:
    """Schalter „verzeichnis“: kein Aufruf, nichts verloren; ohne Modell nur Regeln, kein Kategorie-Vorschlag."""
    store, wp = ctx.store, FakeWordPressVerzeichnis()
    c = _client(wp)
    v = wp.einreichen("neu", VEREIN)
    schalter.setzen(store, "verzeichnis", True, wer="abnahme", grund="Rechtstexte fehlen")
    vorher = verzeichnis.lauf(store, c, ctx.claude)
    out = {"aufrufe_im_stopp": len(wp.aufrufe), "angehalten": vorher["angehalten"],
           "liegt_auf_website": int(wp.einsendung(v)["status"] == "neu")}
    schalter.setzen(store, "verzeichnis", False, wer="abnahme")
    danach = verzeichnis.lauf(store, c, ctx.claude)
    e = verzeichnis.holen(store, v)
    out.update(geprueft_danach=danach["geprueft"], ohne_kategorie=int(e["pruefung"]["kategorie_vorschlag"] == ""),
               regeln_ok=int(e["pruefung"]["fehlt"] == [] and e["pruefung"]["formfehler"] == []))
    return out


NACHHER = {"verzeichnis_t4": t4, "verzeichnis_stopp": im_stopp}
