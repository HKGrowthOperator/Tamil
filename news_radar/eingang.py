"""Eingang (Festlegung F1, Vertrag A1/B1, §8): Einsendungen der Website-Formulare abholen, vorbereiten, entscheiden.

Ablauf (integrationen.md §3 „Einsendungen“): Stopp-Schalter `eingang` prüfen → `GET /einsendungen?nach=` → je
Einsendung speichern → `POST …/status` `abgeholt` → Agent bereitet vor → Redaktion entscheidet → `POST …/status` mit
dem Abschluss. Der Radar holt ab; WordPress ruft den Radar nie auf; niemand verschickt eine E-Mail.

- **Vorbereiten** (`vorbereiten`): Regeln ohne Modell (Pflichtfelder, Einwilligung, Datum in der Zukunft und
  plausibel, Land DE/AT/CH, Dubletten gegen Storys, Termin-Entwürfe und frühere Einsendungen). Mit Schlüssel schreibt
  die Rolle `eingang` über `Claude.call` eine interne Zusammenfassung und bei Event/Beitrag einen Entwurf – ohne
  Kontaktdaten im Prompt. Eine Zahl, ein Link oder eine Adresse im Modelltext, die nicht in der Einsendung steht,
  verwirft den Modell-Entwurf; dann gilt der Entwurf aus den Feldern. Der Agent markiert, er entscheidet nicht.
- **Entscheiden** (nur Menschen, Recht `eingang_entscheiden`): `uebernehmen` legt einen Entwurf mit dem Vermerk
  „Angaben des Einsenders, ungeprüft“ an (dann der normale Weg: prüfen, freigeben, veröffentlichen); `abschliessen`
  mit erledigt, abgelehnt oder Spam. Jeder Übergang ist eine bedingte Anweisung (kein Rennen).
- **Status zurück** (`melden`): unmittelbar vor jedem Aufruf der Schalter; bei unklarem Ausgang (Abbruch nach dem
  Senden) erneut abfragen und abgleichen; was nicht gemeldet ist, geht beim nächsten Lauf hinaus.
- **Protokoll** (`editorial_actions`, Kanal `eingang`): nur Vorgangsnummer, Aktion, wer – keine Namen, keine Inhalte.
- **Löschfrist** (`loeschen`): 90 Tage nach Abschluss, Spam nach 7 Tagen (wie auf der Website).
"""

from __future__ import annotations

import base64
import hashlib
import html
import io
import json
import logging
import re
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import requests
from pydantic import BaseModel

from . import schalter
from .render import safe_url
from .store import now_iso
from .wordpress import VORGANG_RE, TamilRadarClient
from .workflow import repo

log = logging.getLogger(__name__)

TZ = ZoneInfo("Europe/Berlin")
KANAL = "eingang"
REGEL_FASSUNG = "F1 vom 13.11.2026"
VERMERK = "Angaben des Einsenders, ungeprüft"
AGENT = "agent:eingang"
DIENST = "dienst"

ARTEN = {"event": "Event", "beitrag": "Beitrag oder Thema", "kooperation": "Kooperation", "werbung": "Werbeanfrage",
         "kontakt": "Kontakt"}
# Felder je Art (Festlegung F1): (Schlüssel, Bezeichnung, Pflicht)
FELDER: dict[str, tuple[tuple[str, str, bool], ...]] = {
    "event": (("titel", "Titel", True), ("beginn", "Datum und Uhrzeit", True), ("ende", "Ende", False),
              ("ort", "Ort mit Adresse", True), ("stadt", "Stadt", True), ("land", "Land", True),
              ("veranstalter", "Veranstalter", True), ("beschreibung", "Beschreibung", True),
              ("eintritt", "Eintritt", False), ("ticket_link", "Ticket-Link", False)),
    "beitrag": (("thema", "Thema", True), ("text", "Hinweis oder Text", True), ("link", "Link", False)),
    "kooperation": (("organisation", "Organisation", False), ("anliegen", "Anliegen", True)),
    "werbung": (("firma", "Firma", False), ("platz_zeitraum", "Gewünschter Platz und Zeitraum", False),
                ("nachricht", "Nachricht", True)),
    "kontakt": (("nachricht", "Nachricht", True),),
}
HAUPTTEXT = {"event": "beschreibung", "beitrag": "text", "kooperation": "anliegen", "werbung": "nachricht",
             "kontakt": "nachricht"}
MIT_ENTWURF = ("event", "beitrag")
DACH = ("DE", "AT", "CH")
OFFEN = ("abgeholt", "vorbereitet")
ABSCHLUESSE = ("uebernommen", "erledigt", "abgelehnt", "spam")
ENTSCHEIDUNGEN = ("erledigt", "abgelehnt", "spam")  # „übernehmen“ hat seine eigene Funktion
STATUS_LABEL = {"abgeholt": "abgeholt", "vorbereitet": "vorbereitet", "uebernommen": "übernommen",
                "erledigt": "erledigt", "abgelehnt": "abgelehnt", "spam": "Spam"}
FRIST_TAGE, SPAM_TAGE = 90, 7
MAX_FELD, MAX_NOTIZ, MAX_VERSUCHE = 5000, 1000, 3
BILD_MAX = 5 * 1024 * 1024
BILD_TYPEN = ("image/jpeg", "image/png")
BILD_MAX_PIXEL = 25_000_000  # eigene Grenze gegen Dekomprimierungsbomben (vor dem Dekodieren geprüft)
BILD_KANTE = 2400            # längste Kante nach dem Neuspeichern
FEHLT_TAGE = 30              # auf der Website nicht mehr vorhanden: Kopie im Radar 30 Tage nach dem Vermerk löschen
EVENT_DATUM_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")


class Konflikt(Exception):
    """Die Einsendung steht nicht (mehr) im erwarteten Zustand – jemand war schneller."""


class EingangErgebnis(BaseModel):
    zusammenfassung: str
    titel: str
    teaser: str
    absaetze: list[str]


# ---- Lesen ---------------------------------------------------------------------------------------------------------

def _json(wert: Any, standard: Any) -> Any:
    if wert in (None, ""):
        return standard
    try:
        return json.loads(wert)
    except (TypeError, ValueError):
        return standard


def _zeile(row) -> dict | None:
    if row is None:
        return None
    e = dict(row)
    e["felder"] = _json(e.get("felder"), {})
    e["hinweise"] = _json(e.get("hinweise"), [])
    e["bild"] = _json(e.get("bild"), None)
    entwurf = _json(e.get("entwurf"), None)
    # gespeichert als {"regeln": …, "modell": …}: das Formular nimmt immer den Entwurf aus den Feldern, der Vorschlag
    # des Modells steht daneben und gilt nur auf ausdrücklichen Klick
    if isinstance(entwurf, dict) and "regeln" in entwurf:
        e["entwurf"], e["modell_vorschlag"] = entwurf.get("regeln"), entwurf.get("modell")
    elif isinstance(entwurf, dict) and entwurf.get("quelle") == "modell":
        # Zeile aus der Zeit vor der Positivliste: Modelltext verwerfen, Entwurf aus den Feldern
        e["entwurf"], e["modell_vorschlag"] = regel_vorbereitung(e)[1], None
    else:
        e["entwurf"], e["modell_vorschlag"] = entwurf, None
    e["einwilligung"] = bool(e.get("einwilligung"))
    return e


def holen(store, vorgang: str) -> dict | None:
    return _zeile(store.db.execute("SELECT * FROM einsendungen WHERE vorgangsnummer = ?", (vorgang,)).fetchone())


def liste(store, ansicht: str = "offen", art: str | None = None, limit: int = 200) -> list[dict]:
    """`offen` (abgeholt, vorbereitet), `abgeschlossen` oder `alle`; neueste zuerst."""
    where, params = [], []
    if ansicht == "offen":
        where.append(f"status IN ({','.join('?' for _ in OFFEN)})")
        params += OFFEN
    elif ansicht == "abgeschlossen":
        where.append(f"status IN ({','.join('?' for _ in ABSCHLUESSE)})")
        params += ABSCHLUESSE
    if art:
        where.append("art = ?")
        params.append(art)
    sql = "SELECT * FROM einsendungen" + (" WHERE " + " AND ".join(where) if where else "")
    rows = store.db.execute(sql + " ORDER BY eingang_at DESC, id DESC LIMIT ?", (*params, int(limit)))
    return [_zeile(r) for r in rows]


def zaehlen(store) -> dict[str, int]:
    out = {s: 0 for s in (*OFFEN, *ABSCHLUESSE)}
    for row in store.db.execute("SELECT status, COUNT(*) FROM einsendungen GROUP BY status"):
        out[row[0]] = row[1]
    return out


def client_fuer(settings) -> TamilRadarClient:
    return TamilRadarClient(settings.wp_url, settings.wp_user, settings.wp_app_password)


def _protokoll(store, aktion: str, vorgang: str, *, wer: str, ausloeser: str, draft_id: int | None = None,
               notiz: str = "", regel: str = REGEL_FASSUNG) -> None:
    repo.aktion(store, wer=wer, aktion=aktion, draft_id=draft_id, gegenstand_typ="einsendung", gegenstand_id=vorgang,
                kanal=KANAL, regel_fassung=regel, ausloeser=ausloeser, notiz=notiz)


# ---- Abholen -------------------------------------------------------------------------------------------------------

def _cursor(store) -> int:
    row = store.db.execute("SELECT wert FROM eingang_stand WHERE schluessel = 'cursor'").fetchone()
    return int(row[0]) if row and str(row[0]).isdigit() else 0


def _cursor_setzen(store, wert: int) -> None:
    store._write("INSERT INTO eingang_stand (schluessel, wert) VALUES ('cursor', ?) "
                 "ON CONFLICT(schluessel) DO UPDATE SET wert = excluded.wert", (str(int(wert)),))


def _text(wert: Any, laenge: int = MAX_FELD) -> str:
    return str(wert if wert is not None else "").strip()[:laenge]


def _aufnehmen(store, e: dict) -> bool:
    """Eine Einsendung aus der Liste speichern; nur gültige, noch offene. True, wenn neu."""
    vorgang, art = str(e.get("vorgangsnummer") or ""), str(e.get("art") or "")
    if not VORGANG_RE.fullmatch(vorgang) or art not in ARTEN or e.get("status") not in ("eingegangen", "abgeholt"):
        return False
    roh = e.get("felder")
    if not isinstance(roh, dict):
        raise ValueError("Felder fehlen")
    felder = {k: _text(roh.get(k)) for k, _, _ in FELDER[art]}
    bild = e.get("bild") if isinstance(e.get("bild"), dict) else None
    if bild is not None:
        bild = {"typ": _text(bild.get("typ"), 40), "groesse": int(bild.get("groesse") or 0),
                "sha256": _text(bild.get("sha256"), 64), "recht_bestaetigt": bool(bild.get("recht_bestaetigt"))}
    jetzt = now_iso()
    cur = store._write(
        "INSERT OR IGNORE INTO einsendungen (wp_id, vorgangsnummer, art, status, wp_status, eingang_at, abgeholt_at, "
        "name, email, telefon, einwilligung, einwilligung_fassung, felder, bild, aktualisiert) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (int(e.get("id") or 0), vorgang, art, "abgeholt", e["status"], _text(e.get("eingang_at"), 40), jetzt,
         _text(e.get("name"), 200), _text(e.get("email"), 200), _text(e.get("telefon"), 60),
         1 if e.get("einwilligung") else 0, _text(e.get("einwilligung_fassung"), 100),
         json.dumps(felder, ensure_ascii=False), json.dumps(bild) if bild else None, jetzt),
    )
    if cur.rowcount != 1:
        return False
    _protokoll(store, "eingang_abgeholt", vorgang, wer=DIENST, ausloeser="dienst", notiz=f"Art {art}")
    return True


def abholen(store, client, *, anzahl: int = 50, max_seiten: int = 20) -> Counter:
    """Neue Einsendungen holen (Cursor), speichern und `abgeholt` melden. Hält der Schalter an, geschieht nichts –
    die Einsendungen bleiben auf der Website liegen."""
    out: Counter = Counter()
    cursor = _cursor(store)
    for _ in range(max_seiten):
        try:
            schalter.pruefen(store, KANAL)
        except schalter.Gestoppt:
            out["angehalten"] += 1
            return out
        daten = client.einsendungen(nach=cursor, anzahl=anzahl)
        out["seiten"] += 1
        if daten is None:  # Funktion auf der Website aus: nichts abzuholen
            out["funktion_aus"] += 1
            break
        for e in daten["einsendungen"]:
            try:  # eine kaputte Zeile hält den Cursor nicht auf: vermerken, weiter
                out["neu" if isinstance(e, dict) and _aufnehmen(store, e) else "uebersprungen"] += 1
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                out["kaputt"] += 1
                vorgang = str(e.get("vorgangsnummer") or "") if isinstance(e, dict) else ""
                log.warning("Einsendung %s nicht lesbar (%s) – übersprungen",
                            vorgang if VORGANG_RE.fullmatch(vorgang) else "ohne Vorgangsnummer", type(exc).__name__)
                if VORGANG_RE.fullmatch(vorgang):
                    _protokoll(store, "eingang_unlesbar", vorgang, wer=DIENST, ausloeser="dienst",
                               notiz=type(exc).__name__)
        weiter = int(daten.get("weiter") or cursor)
        if weiter > cursor:
            cursor = weiter
            _cursor_setzen(store, cursor)
        if not daten.get("mehr"):
            break
    out.update(melden(store, client))
    return out


# ---- Status an WordPress ---------------------------------------------------------------------------------------------

def _ziel(status: str) -> str:
    return "abgeholt" if status in OFFEN else status


def _hinweis_dazu(store, eid: int, hinweis: str) -> None:
    row = store.db.execute("SELECT hinweise FROM einsendungen WHERE id = ?", (eid,)).fetchone()
    hinweise = _json(row[0] if row else None, [])
    if hinweis not in hinweise:
        hinweise.append(hinweis)
        store._write("UPDATE einsendungen SET hinweise = ?, aktualisiert = ? WHERE id = ?",
                     (json.dumps(hinweise, ensure_ascii=False), now_iso(), eid))


def melden(store, client, *, nur: str | None = None, wer: str = DIENST, ausloeser: str = "dienst") -> Counter:
    """Was WordPress noch nicht weiß, hinschicken: `abgeholt` für Offenes, sonst der Abschluss. Ein anderer Abschluss
    auf der Website (409) wird vermerkt, nicht überschrieben."""
    out: Counter = Counter()
    sql = "SELECT * FROM einsendungen WHERE (wp_status IS NULL OR wp_status IN ('eingegangen', 'abgeholt'))"
    params: tuple = ()
    if nur:
        sql, params = sql + " AND vorgangsnummer = ?", (nur,)
    for e in [_zeile(r) for r in store.db.execute(sql + " ORDER BY id", params)]:
        ziel = _ziel(e["status"])
        if e["wp_status"] == ziel:
            continue
        try:
            schalter.pruefen(store, KANAL)
        except schalter.Gestoppt:
            out["angehalten"] += 1
            break
        vorgang = e["vorgangsnummer"]
        try:
            antwort = client.einsendung_status(vorgang, ziel)
        except (requests.RequestException, RuntimeError) as exc:
            # Unklarer Ausgang: vielleicht ist der Status angekommen. Nachsehen statt blind wiederholen.
            log.warning("Status %s für %s unklar (%s) – Abgleich", ziel, vorgang, type(exc).__name__)
            try:
                stand = client.einsendung(vorgang)
            except (requests.RequestException, RuntimeError):
                out["offen"] += 1
                continue
            antwort = {"fehlt": True} if stand is None else stand
        if antwort.get("konflikt"):
            aktuell = _text(antwort.get("aktuell"), 20) or "unbekannt"
            store._write("UPDATE einsendungen SET wp_status = ?, aktualisiert = ? WHERE id = ?", (aktuell, now_iso(), e["id"]))
            _hinweis_dazu(store, e["id"], f"Auf der Website schon „{STATUS_LABEL.get(aktuell, aktuell)}“ – dort nicht geändert")
            _protokoll(store, "eingang_status_konflikt", vorgang, wer=wer, ausloeser=ausloeser, notiz=f"{ziel} ≠ {aktuell}")
            out["konflikt"] += 1
            continue
        if antwort.get("abgewiesen"):  # dauerhaft (4xx): vermerken, nicht alle drei Minuten wiederholen
            code = int(antwort["abgewiesen"])
            store._write("UPDATE einsendungen SET wp_status = 'abgewiesen', aktualisiert = ? WHERE id = ?",
                         (now_iso(), e["id"]))
            _hinweis_dazu(store, e["id"], f"Website lehnt den Status „{STATUS_LABEL.get(ziel, ziel)}“ ab (HTTP {code}) – "
                                          "bitte dort prüfen")
            _protokoll(store, "eingang_status_abgewiesen", vorgang, wer=wer, ausloeser=ausloeser, notiz=f"HTTP {code}")
            out["abgewiesen"] += 1
            continue
        if antwort.get("fehlt"):
            store._write("UPDATE einsendungen SET wp_status = 'fehlt', aktualisiert = ? WHERE id = ?", (now_iso(), e["id"]))
            _hinweis_dazu(store, e["id"], "Auf der Website nicht mehr vorhanden")
            out["fehlt"] += 1
            continue
        neu = _text(antwort.get("status"), 20) or ziel
        store._write("UPDATE einsendungen SET wp_status = ?, aktualisiert = ? WHERE id = ?", (neu, now_iso(), e["id"]))
        if neu == ziel:
            _protokoll(store, "eingang_status", vorgang, wer=wer, ausloeser=ausloeser, notiz=f"an Website: {ziel}")
            out["gemeldet"] += 1
        else:
            out["offen"] += 1
    return out


# ---- Regeln --------------------------------------------------------------------------------------------------------

def _zeit(wert: str | None) -> datetime | None:
    if not wert:
        return None
    try:
        dt = datetime.fromisoformat(str(wert).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=TZ)


WOCHENTAGE = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November",
          "Dezember")


def datum_text(wert: str | None) -> str:
    dt = _zeit(wert)
    if dt is None:
        return ""
    dt = dt.astimezone(TZ)
    return f"{WOCHENTAGE[dt.weekday()]}, {dt.day}. {MONATE[dt.month - 1]} {dt.year}, {dt:%H:%M} Uhr"


def _lokal(wert: str | None) -> str:
    """ISO mit Versatz → Ortszeit „JJJJ-MM-TTTHH:MM“ (wie Termine im Radar)."""
    dt = _zeit(wert)
    return dt.astimezone(TZ).strftime("%Y-%m-%dT%H:%M") if dt else ""


def _norm(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", (text or "").lower()))


def _passt(a: dict, titel: str, stadt: str, ort: str) -> bool:
    from .agents import cluster

    return cluster._passt(a.get("titel", ""), a.get("stadt", ""), a.get("ort", ""), titel or "", stadt or "", ort or "")


def dublette(store, e: dict) -> tuple[str, str] | None:
    """(Verweis, Text) der ersten möglichen Dublette: Termin-Story, Termin-Entwurf oder frühere Einsendung."""
    f, art = e["felder"], e["art"]
    if art == "event":
        beginn = _zeit(f.get("beginn"))
        if beginn is None:
            return None
        datum = beginn.astimezone(TZ).date().isoformat()
        praefix = f"event:{datum}:"
        for sid, titel, ort in store.db.execute(
                "SELECT id, titel, ort FROM stories WHERE typ = 'event' AND status != 'verworfen' "
                "AND substr(schluessel, 1, ?) = ? ORDER BY id", (len(praefix), praefix)):
            if _passt(f, titel, ort, ort):
                return f"story:{sid}", f"Story {sid} „{titel}“"
        for did, titel, ort, event_ort in store.db.execute(
                "SELECT id, titel, ort, event_ort FROM drafts WHERE typ = 'event' AND status != 'abgelehnt' "
                "AND substr(event_datum, 1, 10) = ? ORDER BY id", (datum,)):
            if _passt(f, titel, ort, event_ort):
                return f"entwurf:{did}", f"Termin-Entwurf {did} „{titel}“"
    schluessel = _norm(f.get(HAUPTTEXT[art], "")) if art != "event" else ""
    for row in store.db.execute("SELECT * FROM einsendungen WHERE art = ? AND id < ? AND status NOT IN "
                                "('spam', 'abgelehnt') ORDER BY id", (art, e["id"])):
        o = _zeile(row)
        if art == "event":
            ob = _zeit(o["felder"].get("beginn"))
            gleich = ob is not None and ob.astimezone(TZ).date().isoformat() == datum and \
                _passt(f, o["felder"].get("titel", ""), o["felder"].get("stadt", ""), o["felder"].get("ort", ""))
        else:
            gleich = bool(schluessel) and _norm(o["felder"].get(HAUPTTEXT[art], "")) == schluessel
        if gleich:
            return f"einsendung:{o['vorgangsnummer']}", f"Einsendung {o['vorgangsnummer']}"
    return None


def regeln(store, e: dict, jetzt: datetime) -> tuple[list[str], str | None]:
    """Hinweise nach Regeln (ohne Modell) und Verweis auf eine mögliche Dublette. Markiert, entscheidet nicht."""
    f, art, hinweise = e["felder"], e["art"], []
    fehlt = [] if e.get("name") else ["Name"]
    fehlt += [] if e.get("email") else ["E-Mail"]
    fehlt += [label for feld, label, pflicht in FELDER[art] if pflicht and not f.get(feld)]
    if fehlt:
        hinweise.append(f"unvollständig: {', '.join(fehlt)} {'fehlt' if len(fehlt) == 1 else 'fehlen'}")
    if not e.get("einwilligung"):
        hinweise.append("ohne Einwilligung")
    if art == "event":
        beginn, ende = _zeit(f.get("beginn")), _zeit(f.get("ende"))
        if f.get("beginn") and beginn is None:
            hinweise.append("Datum unplausibel (nicht lesbar)")
        elif beginn is not None and beginn < jetzt:
            hinweise.append("Datum in der Vergangenheit")
        elif beginn is not None and beginn > jetzt + timedelta(days=730):
            hinweise.append("Datum unplausibel (mehr als zwei Jahre voraus)")
        if f.get("ende") and ende is None:
            hinweise.append("Ende unplausibel (nicht lesbar)")
        elif beginn and ende and ende < beginn:
            hinweise.append("Ende vor Beginn")
        land = (f.get("land") or "").upper()
        if land and land not in DACH:
            hinweise.append(f"Ort außerhalb DACH (Land {land[:10]})")
    if e.get("bild") and not e["bild"].get("recht_bestaetigt"):
        hinweise.append("Bild ohne bestätigtes Nutzungsrecht")
    if felder_maskiert(e)[1]:
        hinweise.append("Kontaktdaten im Text")
    dub = dublette(store, e)
    if dub:
        hinweise.append(f"mögliche Dublette: {dub[1]}")
    return hinweise, dub[0] if dub else None


def _absaetze(text: str) -> list[str]:
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", text or "") if p.strip()][:6]


def _erster_satz(text: str) -> str:
    text = " ".join((text or "").split())
    return re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0][:220] if text else ""


def regel_vorbereitung(e: dict) -> tuple[str, dict | None]:
    """Zusammenfassung und Entwurf nur aus den Feldern (ohne Modell; auch der Rückfall)."""
    f, art = e["felder"], e["art"]
    if art == "event":
        ort = ", ".join(x for x in (f.get("stadt"), f.get("land")) if x)
        teile = [f"Termin „{f.get('titel') or 'ohne Titel'}“"]
        if f.get("beginn"):
            teile.append(f"am {datum_text(f['beginn']) or f['beginn']}")
        if ort:
            teile.append(f"in {ort}")
        zusammenfassung = " ".join(teile) + (f"; Veranstalter: {f['veranstalter']}" if f.get("veranstalter") else "")
        zusammenfassung += "" if zusammenfassung.endswith(".") else "."
    elif art == "beitrag":
        zusammenfassung = f"Themenvorschlag „{f.get('thema') or 'ohne Thema'}“: {_erster_satz(f.get('text', ''))}"
    elif art == "kooperation":
        von = f" von {f['organisation']}" if f.get("organisation") else ""
        zusammenfassung = f"Kooperationsanfrage{von}: {_erster_satz(f.get('anliegen', ''))}"
    elif art == "werbung":
        von = f" von {f['firma']}" if f.get("firma") else ""
        platz = f" ({f['platz_zeitraum']})" if f.get("platz_zeitraum") else ""
        zusammenfassung = f"Werbeanfrage{von}{platz}: {_erster_satz(f.get('nachricht', ''))}"
    else:
        zusammenfassung = f"Nachricht: {_erster_satz(f.get('nachricht', ''))}"
    if art not in MIT_ENTWURF:
        return zusammenfassung[:500], None
    titel = f.get("titel") if art == "event" else f.get("thema")
    text = f.get(HAUPTTEXT[art], "")
    return zusammenfassung[:500], {"titel": (titel or "")[:90], "teaser": _erster_satz(text),
                                   "absaetze": _absaetze(text), "quelle": "regeln"}


# ---- Kontaktdaten im Freitext ---------------------------------------------------------------------------------------

_MAIL_FREI = re.compile(r"[\w.+-]+\s*(?:@|[\[(]\s*(?:at|ät)\s*[\])])\s*[\w-]+"
                        r"(?:\s*(?:\.|[\[(]\s*(?:dot|punkt)\s*[\])]|\s(?:dot|punkt)\s)\s*[\w-]+)+", re.I)
_MAIL_WORTE = re.compile(r"[\w.+-]+\s+(?:at|ät)\s+[\w-]+(?:\s+(?:dot|punkt)\s+[\w-]+)+", re.I)  # info at x punkt de
_HANDLE = re.compile(r"(?<!\w)@[\w.]{2,}")
_TELEFON = re.compile(r"(?<![\w.])(?:\+|00)?\d[\d \t/().-]{5,}\d(?!\w)")
_DATUMSARTIG = re.compile(r"\d{1,2}\.\s?\d{1,2}\.\s?\d{2,4}|\d{4}-\d{2}-\d{2}")
# Datum, Adressen und Ort bleiben wörtlich: keine Kontaktdaten (Postleitzahl und Hausnummer sind keine Telefonnummer)
OHNE_MASKE = ("beginn", "ende", "ticket_link", "link", "ort", "stadt", "land")


def kontakt_maskieren(text: str) -> tuple[str, bool]:
    """E-Mail-Adressen (auch „[at]“ und „at … punkt“), Konten (@name) und Telefonnummern im Freitext ersetzen.
    Telefon heißt: mindestens 8 Ziffern oder eine Vorwahl (+, 00, 0) mit mindestens 6 Ziffern, kein Datum."""
    neu = _MAIL_FREI.sub("[E-Mail]", text or "")
    neu = _MAIL_WORTE.sub("[E-Mail]", neu)
    neu = _HANDLE.sub("[Konto]", neu)

    def telefon(m: re.Match) -> str:
        roh = m.group(0)
        ziffern = sum(c.isdigit() for c in roh)
        vorwahl = roh.lstrip().startswith(("+", "0"))
        if _DATUMSARTIG.fullmatch(roh.strip()) or not (ziffern >= 8 or (vorwahl and ziffern >= 6)):
            return roh
        return "[Telefon]"

    neu = _TELEFON.sub(telefon, neu)
    return neu, neu != (text or "")


def felder_maskiert(e: dict) -> tuple[dict, bool]:
    out, gefunden = {}, False
    for k, v in e["felder"].items():
        if k in OHNE_MASKE:
            out[k] = v
            continue
        out[k], treffer = kontakt_maskieren(v)
        gefunden = gefunden or treffer
    return out, gefunden


# ---- Erfindungsschutz (Positivliste) ----------------------------------------------------------------------------------
#
# Jedes Inhaltswort ab 4 Zeichen – in jeder Schreibung und Schrift – muss (als Stamm) in der Einsendung stehen oder ein
# Funktionswort aus FREIE_WOERTER sein. Zahlen gelten nur zusammen mit einem Nachbarwort aus der Einsendung; Zahlwörter,
# Ordnungszahlen, Wochentage und Monate nur, wenn sie selbst in der Einsendung stehen; kurze großgeschriebene Wörter
# (Namen, Kürzel) ebenso. Links, Domains und E-Mail-Spuren nur, wenn sie wörtlich in der Einsendung stehen.

_URL = re.compile(r"(?:https?://|www\.)[^\s\"'<>]+", re.I)
_DOMAIN = re.compile(r"(?<![\w@.-])[\w-]+(?:\.[\w-]+)*\.[^\W\d_]{2,}(?![\w-])")
_MAIL_SPUR = re.compile(r"@|[\[(]\s*(?:at|ät)\s*[\])]|\s(?:at|ät)\s+\S+\s+(?:dot|punkt)\b", re.I)
_ZAHLWORT = re.compile(r"(?:null|eins|zwei|drei|vier|fuenf|sechs|sieben|acht|neun|zehn|elf|zwoelf|sechzehn|siebzehn|"
                       r"zwanzig|dreissig|vierzig|fuenfzig|sechzig|siebzig|achtzig|neunzig|hundert|tausend|"
                       r"dutzend|million|milliarde|ein|und)+(?:e|en|n|s)?")
_ORDINAL = re.compile(r"(?:erst|zweit|dritt|viert|fuenft|sechst|siebt|siebent|acht|neunt|zehnt|elft|zwoelft|\w+zehnt|"
                      r"\w+zigst|\w*hundertst|\w*tausendst|\w+ssigst)(?:e|en|er|es|em)")
_NUR_ARTIKEL = {"ein", "eine", "einen", "einem", "einer", "eines", "und", "eins"}
# feste, kleine Liste: Wörter ohne eigene Angabe (Artikel, Pronomen, Präpositionen, Bindewörter, Hilfsverben)
FREIE_WOERTER = {
    "eine", "einen", "einem", "einer", "eines", "dass", "diese", "dieser", "dieses", "diesem", "diesen", "sind",
    "wird", "werden", "wurde", "wurden", "sein", "seine", "seiner", "seinen", "ihre", "ihrer", "ihren", "ihrem",
    "unser", "unsere", "unseren", "auch", "sowie", "oder", "aber", "dann", "dort", "hier", "dazu", "danach", "damit",
    "dabei", "mehr", "alle", "allen", "aller", "alles", "jede", "jeden", "jeder", "jedes", "nach", "ueber", "unter",
    "neben", "zwischen", "beim", "durch", "gegen", "ohne", "sich", "ihnen", "euch", "wenn", "weil", "also", "noch",
    "schon", "sehr", "sowohl", "findet", "statt", "kann", "koennen", "soll", "sollen", "gibt", "haben", "denen",
    "deren", "dessen", "welche", "welcher", "welches", "werden", "steht", "stehen",
}
KURZ_FREI = {"der", "die", "das", "den", "dem", "des", "ein", "am", "im", "in", "an", "um", "ab", "es", "er", "sie",
             "wir", "ihr", "und", "so", "wo", "wie", "was", "wer", "mit", "bei", "zum", "zur", "von", "vom", "auf",
             "aus", "bis", "fuer", "uhr", "ist", "hat", "zu", "ja", "nur", "man", "uns", "vor", "als", "wie", "auch",
             "gut", "neu", "da", "ob", "oft", "nun", "per", "pro", "je", "zu", "dir", "mir", "ihm", "sei"}
_UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def _norm_wort(wort: str) -> str:
    return unicodedata.normalize("NFC", wort).casefold().translate(_UMLAUT)


def _laeufe(text: str) -> list[tuple[str, bool]]:
    """Text in Läufe zerlegen: (Teil, ist_wort). Wort = Buchstaben, Zeichen-Marken und Ziffern jeder Schrift."""
    out: list[tuple[str, bool]] = []
    for ch in text or "":
        wort = unicodedata.category(ch)[0] in "LMN"
        if out and out[-1][1] == wort:
            out[-1] = (out[-1][0] + ch, wort)
        else:
            out.append((ch, wort))
    return out


def _woerter(text: str) -> list[str]:
    return [t for t, wort in _laeufe(text) if wort]


def erlaubter_text(e: dict) -> str:
    """Was das Modell verwenden darf: die (maskierten) Felder ohne Rohdatum, dazu Beginn und Ende in Worten."""
    felder, _ = felder_maskiert(e)
    teile = [str(v) for k, v in felder.items() if k not in ("beginn", "ende") and v]
    teile += [datum_text(felder.get("beginn")), datum_text(felder.get("ende"))]
    return "\n".join(t for t in teile if t)


def _stamm(wort: str) -> str:
    for endung in ("en", "er", "es", "e", "n", "s"):
        if wort.endswith(endung) and len(wort) - len(endung) >= 4:
            return wort[: -len(endung)]
    return wort


# Wörter, die einen Wert tragen: nur in derselben Wortfolge wie in der Einsendung („Kinder frei“, nicht „Essen frei“)
WERTWOERTER = {"frei", "kostenlos", "gratis", "umsonst", "ausverkauft", "abgesagt", "verschoben", "inklusive", "inkl",
               "ermaessigt", "ermaessigung"}


class _Pruefung:
    """Positivliste gegen den erlaubten Text. Zahlen, Wertwörter und Kalenderwörter gelten nur in der Wortfolge der
    Einsendung (Wort, Zahl, Einheit als n-Gramm, je Feld; nie über Feldgrenzen hinweg)."""

    def __init__(self, erlaubt: str):
        self.klein = erlaubt.lower()
        self.woerter: set[str] = set()
        self.staemme: set[str] = set()
        self.ngramme: set[tuple[str, ...]] = set()
        for zeile in erlaubt.split("\n"):
            tokens = [_norm_wort(t) for t in _woerter(zeile)]
            self.woerter.update(tokens)
            self.staemme.update(_stamm(t) for t in tokens)
            for n in (1, 2, 3):
                self.ngramme.update(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))

    def _in_folge(self, folge: list[str], von: int, bis: int) -> bool:
        return tuple(_norm_wort(t) for t in folge[max(0, von):bis + 1]) in self.ngramme

    def fremd(self, folge: list[str], i: int) -> bool:
        """Ist das i-te Wort der Folge eine Angabe, die nicht in der Einsendung steht?"""
        roh = folge[i]
        w = _norm_wort(roh)
        if w.isdigit():  # mit beiden Nachbarn so in der Einsendung („Kinder 10 Euro“ ≠ „10 Euro, Kinder frei“)
            return not self._in_folge(folge, i - 1, i + 1)
        if w in _KALENDER:  # Wochentag und Monat nur mit der Zahl daneben wie in der Einsendung
            if w not in self.woerter:
                return True
            nachbarn = [j for j in (i - 1, i + 1) if 0 <= j < len(folge) and folge[j].isdigit()]
            return any(not self._in_folge(folge, min(i, j), max(i, j)) for j in nachbarn)
        if w in WERTWOERTER:  # mit dem Wort davor (am Anfang: danach) wie in der Einsendung
            return not (self._in_folge(folge, i - 1, i) if i else self._in_folge(folge, i, i + 1))
        if w in self.woerter or _stamm(w) in self.staemme:
            return False
        if (_ZAHLWORT.fullmatch(w) and w not in _NUR_ARTIKEL) or _ORDINAL.fullmatch(w) or any(c.isdigit() for c in w):
            return True
        if roh.lower() == roh.upper():  # Schrift ohne Groß- und Kleinschreibung (z. B. Tamil): nur aus der Einsendung
            return True
        if len(roh) >= 4:
            return w not in FREIE_WOERTER
        return w not in KURZ_FREI  # kurze lateinische Wörter nur aus der festen Liste, in jeder Schreibung


_KALENDER = {_norm_wort(w) for w in WOCHENTAGE + MONATE} | {"sonnabend", "jaenner", "feber"}


def fremde_angaben(texte: list[str], erlaubt: str) -> list[str]:
    """Fundstellen im Modelltext, die nicht in der Einsendung stehen („nichts Erfundenes“, Positivliste).
    Leer = nichts gefunden."""
    pruefung = _Pruefung(erlaubt)
    fremd: list[str] = []
    for t in texte:
        for url in _URL.findall(t):
            url = url.rstrip(".,;:!?)")
            if url.lower() not in pruefung.klein:
                fremd.append(url[:60])
        ohne_url = _URL.sub(" ", t)
        fremd += [m.group(0) for m in _DOMAIN.finditer(ohne_url) if m.group(0).lower() not in pruefung.klein]
        if _MAIL_SPUR.search(ohne_url):
            fremd.append("E-Mail-Adresse")
        folge = _woerter(ohne_url)
        fremd += [folge[i][:30] for i in range(len(folge)) if pruefung.fremd(folge, i)]
    return list(dict.fromkeys(fremd))


def markieren(text: str, erlaubt: str):
    """Text für das Cockpit: maskiert (escaped), Wörter ohne Gegenstück in der Einsendung als <mark>."""
    from markupsafe import Markup, escape

    pruefung = _Pruefung(erlaubt)
    laeufe = _laeufe(text)
    folge = [t for t, wort in laeufe if wort]
    teile, i = [], 0
    for teil, wort in laeufe:
        if wort:
            teile.append(Markup('<mark title="nicht in der Einsendung">{}</mark>').format(teil)
                         if pruefung.fremd(folge, i) else escape(teil))
            i += 1
        else:
            teile.append(escape(teil))
    return Markup("").join(teile)


# ---- Modell (Rolle „eingang“) ---------------------------------------------------------------------------------------

def _modell_eingabe(e: dict, hinweise: list[str]) -> tuple[str, str]:
    """Nutzer-Prompt ohne Kontaktdaten: Name, E-Mail und Telefon gehen nicht an das Modell, Adressen und Nummern im
    Freitext werden maskiert. Dazu der erlaubte Text für die Prüfung der Antwort."""
    from .workflow.providers import json_block

    felder, _ = felder_maskiert(e)
    daten = {"art": e["art"], "felder": {k: v for k, v in felder.items() if v},
             "datum_text": datum_text(felder.get("beginn"))}
    user = json_block("einsendung", daten) + "\n" + json_block("hinweise", hinweise)
    return user, erlaubter_text(e)


def _modell(store, claude, e: dict, hinweise: list[str]) -> tuple[str, dict | None, str, list[str]]:
    """(Zusammenfassung, Vorschlag, Prompt-Version, zusätzliche Hinweise) oder wirft Gestoppt/BudgetErschoepft/Fehler.
    Findet die Prüfung eine Angabe, die nicht in der Einsendung steht, wird die ganze Antwort verworfen."""
    from . import prompts
    from .workflow.providers import prompt_version

    system = prompts.load_prompt("eingang")
    user, erlaubt = _modell_eingabe(e, hinweise)
    antwort = claude.call("eingang", system, user, EingangErgebnis, kanal=KANAL)
    version = prompt_version(system)
    if not antwort.ok:
        return "", None, version, [f"ohne Modell vorbereitet (Antwort {antwort.status})"]
    d: EingangErgebnis = antwort.daten
    absaetze = [" ".join(a.split())[:1500] for a in d.absaetze if a.strip()][:3]
    texte = [d.zusammenfassung, d.titel, d.teaser, *absaetze]
    fremd = fremde_angaben(texte, erlaubt)
    if fremd:
        return "", None, version, [f"Modell-Entwurf verworfen: Angabe nicht in der Einsendung "
                                   f"({', '.join(fremd[:5])})"]
    vorschlag = None
    if e["art"] in MIT_ENTWURF and d.titel.strip() and absaetze:
        vorschlag = {"titel": " ".join(d.titel.split())[:90], "teaser": " ".join(d.teaser.split())[:300],
                     "absaetze": absaetze, "quelle": "modell"}
    return " ".join(d.zusammenfassung.split())[:500], vorschlag, version, []


def vorbereiten(store, claude=None, *, jetzt: datetime | None = None, limit: int = 20) -> Counter:
    """Abgeholte Einsendungen prüfen und vorbereiten. Ohne `claude` (kein Schlüssel) nur die Regeln."""
    from .workflow.costs import BudgetErschoepft

    jetzt = jetzt or datetime.now(timezone.utc)
    out: Counter = Counter()
    rows = store.db.execute("SELECT * FROM einsendungen WHERE status = 'abgeholt' ORDER BY id LIMIT ?", (int(limit),))
    for e in [_zeile(r) for r in rows.fetchall()]:
        try:
            schalter.pruefen(store, KANAL)
        except schalter.Gestoppt:
            out["angehalten"] += 1
            break
        hinweise, dublette_von = regeln(store, e, jetzt)
        zusammenfassung, entwurf = regel_vorbereitung(e)  # das Formular nimmt immer diesen Entwurf
        vorschlag = None
        regel = REGEL_FASSUNG + " · Regeln"
        if claude is not None:
            try:
                z_modell, e_modell, version, extra = _modell(store, claude, e, hinweise)
            except schalter.Gestoppt:
                out["angehalten"] += 1
                break
            except BudgetErschoepft:
                z_modell, e_modell, version, extra = "", None, "", ["ohne Modell vorbereitet (Budget erreicht)"]
            except Exception as exc:  # noqa: BLE001 – API-Fehler: später erneut, nach drei Versuchen nur Regeln
                if e["versuche"] + 1 < MAX_VERSUCHE:
                    store._write("UPDATE einsendungen SET versuche = versuche + 1, aktualisiert = ? WHERE id = ?",
                                 (now_iso(), e["id"]))
                    out["fehler"] += 1
                    log.warning("Eingang %s: Modell nicht erreichbar (%s)", e["vorgangsnummer"], type(exc).__name__)
                    continue
                z_modell, e_modell, version, extra = "", None, "", ["ohne Modell vorbereitet (Modell nicht erreichbar)"]
            if version:
                out["modell"] += 1
                regel = f"{REGEL_FASSUNG} · Prompt {version}"
            hinweise += extra
            zusammenfassung = z_modell or zusammenfassung
            vorschlag = e_modell  # nur als Vorschlag daneben; übernehmen nur auf ausdrücklichen Klick
        cur = store._write(
            "UPDATE einsendungen SET status = 'vorbereitet', vorbereitet_at = ?, zusammenfassung = ?, hinweise = ?, "
            "dublette_von = ?, entwurf = ?, aktualisiert = ? WHERE id = ? AND status = 'abgeholt'",
            (now_iso(), zusammenfassung, json.dumps(hinweise, ensure_ascii=False), dublette_von,
             json.dumps({"regeln": entwurf, "modell": vorschlag}, ensure_ascii=False) if entwurf else None, now_iso(),
             e["id"]))
        if cur.rowcount == 1:
            _protokoll(store, "eingang_vorbereitet", e["vorgangsnummer"], wer=AGENT, ausloeser="agent", regel=regel,
                       notiz=f"{len(hinweise)} Hinweise")
            out["vorbereitet"] += 1
    return out


def lauf(store, client, claude=None, *, jetzt: datetime | None = None) -> Counter:
    """Ein Takt des Dienstes: abholen (mit Meldung offener Status) und vorbereiten."""
    out = abholen(store, client)
    if not out["angehalten"]:
        out.update(vorbereiten(store, claude, jetzt=jetzt))
    return out


# ---- Entscheiden (nur Menschen) ------------------------------------------------------------------------------------

def notiz_setzen(store, vorgang: str, notiz: str, *, von: str) -> None:
    notiz = (notiz or "").strip()[:MAX_NOTIZ]
    cur = store._write("UPDATE einsendungen SET notiz = ?, bearbeitet_von = ?, aktualisiert = ? WHERE vorgangsnummer = ?",
                       (notiz, von, now_iso(), vorgang))
    if cur.rowcount != 1:
        raise LookupError(vorgang)
    _protokoll(store, "eingang_notiz", vorgang, wer=von, ausloeser="person")  # Inhalt der Notiz nicht ins Protokoll


def abschliessen(store, vorgang: str, status: str, *, von: str, client=None) -> None:
    """Erledigt, abgelehnt oder Spam – nur aus „vorbereitet“ (bedingte Anweisung), dann an WordPress melden."""
    if status not in ENTSCHEIDUNGEN:
        raise ValueError(f"Status muss {', '.join(ENTSCHEIDUNGEN)} sein")
    cur = store._write(
        "UPDATE einsendungen SET status = ?, abgeschlossen_at = ?, bearbeitet_von = ?, aktualisiert = ? "
        "WHERE vorgangsnummer = ? AND status = 'vorbereitet'", (status, now_iso(), von, now_iso(), vorgang))
    if cur.rowcount != 1:
        raise Konflikt(f"Einsendung {vorgang} ist nicht (mehr) vorbereitet")
    _protokoll(store, f"eingang_{status}", vorgang, wer=von, ausloeser="person")
    if client is not None:
        melden(store, client, nur=vorgang, wer=von, ausloeser="person")


def _nicht(grund: str) -> str:
    return f"Bild der Einsendung nicht übernommen ({grund})"


def bild_neu_speichern(roh: bytes) -> bytes | str:
    """Nur JPEG oder PNG, höchstens BILD_MAX_PIXEL (vor dem Dekodieren geprüft), längste Kante BILD_KANTE, neu als JPEG
    ohne Metadaten (kein EXIF, kein GPS, kein Farbprofil). Gibt die Daten oder den Grund der Ablehnung zurück."""
    import warnings

    from PIL import Image, ImageOps

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(roh), formats=("JPEG", "PNG")) as img:
                breite, hoehe = img.size
                if breite * hoehe > BILD_MAX_PIXEL:
                    return "zu viele Bildpunkte"
                img.load()
                rgb = ImageOps.exif_transpose(img).convert("RGB")  # Ausrichtung übernehmen, bevor EXIF wegfällt
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        return "zu viele Bildpunkte"
    except Exception:  # noqa: BLE001 – kein lesbares JPEG oder PNG
        return "kein lesbares JPEG oder PNG"
    rgb.thumbnail((BILD_KANTE, BILD_KANTE))
    sauber = Image.new("RGB", rgb.size)
    sauber.paste(rgb)  # neues Bild: nichts aus info/EXIF wandert mit
    buf = io.BytesIO()
    sauber.save(buf, "JPEG", quality=88, optimize=True)
    return buf.getvalue()


def _bild_uebernehmen(store, settings, client, e: dict) -> tuple[bytes, str, bool] | str:
    """Bild der Einsendung holen und prüfen; (JPEG-Daten, Dateiname, verkleinert) oder ein Hinweis, warum nicht."""
    bild = e.get("bild")
    if not bild:
        return ""
    if not bild.get("recht_bestaetigt"):
        return _nicht("Nutzungsrecht nicht bestätigt")
    if client is None:
        return _nicht("WordPress nicht verbunden")
    try:
        schalter.pruefen(store, KANAL)
        daten = client.einsendung_bild(e["vorgangsnummer"])
    except schalter.Gestoppt:
        return _nicht("Eingang angehalten")
    except (requests.RequestException, RuntimeError):
        return _nicht("Website nicht erreichbar")
    if not daten:
        return _nicht("auf der Website nicht vorhanden")
    if daten.get("typ") not in BILD_TYPEN:
        return _nicht("Typ nicht erlaubt")
    kodiert = str(daten.get("daten_base64") or "")
    if len(kodiert) > (BILD_MAX * 4) // 3 + 8:
        return _nicht("größer als 5 MB")
    try:
        roh = base64.b64decode(kodiert, validate=True)
    except ValueError:
        return _nicht("beschädigt")
    if len(roh) > BILD_MAX:
        return _nicht("größer als 5 MB")
    if not bild.get("sha256") or hashlib.sha256(roh).hexdigest() != bild["sha256"]:
        return _nicht("Prüfsumme passt nicht")
    neu = bild_neu_speichern(roh)
    if isinstance(neu, str):
        return _nicht(neu)
    from PIL import Image

    with Image.open(io.BytesIO(roh)) as alt, Image.open(io.BytesIO(neu)) as jetzt:
        verkleinert = alt.size != jetzt.size
    return neu, f"einsendung-{e['vorgangsnummer'].lower()}.jpg", verkleinert


def _bild_lizenz(e: dict, *, von: str, verkleinert: bool) -> dict:
    """Lizenz-Datensatz über den gemeinsamen Weg (lizenz.anlegen): Nutzungsrecht, im Formular bestätigt."""
    from . import lizenz

    fassung = e.get("einwilligung_fassung") or "unbekannt"
    return {"herkunft": "upload", "rechteinhaber": f"Einsender (Vorgang {e['vorgangsnummer']})",
            "lizenz_kuerzel": "nutzungsrecht", "lizenz": lizenz.lizenz_name("nutzungsrecht"),
            "umfang": lizenz.umfang_fuer("nutzungsrecht", {"website"}),
            "attribution": "Bild: eingesandt", "bearbeitung": "eingepasst" if verkleinert else "keine",
            "beleg": f"Bestätigung im Formular, Fassung {fassung} (Vorgang {e['vorgangsnummer']})",
            "quelle_url": f"einsendung:{e['vorgangsnummer']}", "geprueft_von": von, "geprueft_am": now_iso()}


def uebernehmen(store, settings, vorgang: str, *, von: str, felder: dict, client=None) -> int:
    """Event oder Beitrag als Entwurf übernehmen (Vermerk „Angaben des Einsenders, ungeprüft“). Grundlage ist immer
    der Entwurf aus den Feldern; `felder` sind die Änderungen der Redaktion (titel, teaser, text, event_datum,
    event_ort, ticket_url). Nur mit `vorlage = "modell"` (ausdrücklicher Klick) gilt der geprüfte Vorschlag des
    Modells. Gibt die Entwurfs-ID zurück."""
    from . import lizenz

    e = holen(store, vorgang)
    if e is None:
        raise LookupError(vorgang)
    if e["art"] not in MIT_ENTWURF:
        raise ValueError("Übernehmen gibt es nur für Events und Beiträge; sonst Status und Notiz")
    if e["status"] != "vorbereitet":
        raise Konflikt(f"Einsendung {vorgang} ist nicht (mehr) vorbereitet")
    event_datum = (felder.get("event_datum") or "").strip()
    if event_datum and not EVENT_DATUM_RE.fullmatch(event_datum):
        raise ValueError("Beginn im Format JJJJ-MM-TTTHH:MM angeben")
    f = e["felder"]
    if felder.get("vorlage") == "modell":
        if not e.get("modell_vorschlag"):
            raise ValueError("Es gibt keinen geprüften Vorschlag des Agenten")
        basis, felder = e["modell_vorschlag"], {k: v for k, v in felder.items() if k not in ("titel", "teaser", "text")}
    else:
        basis = e["entwurf"] or regel_vorbereitung(e)[1] or {}
    titel = " ".join((felder.get("titel") or basis.get("titel") or "").split())[:200]
    if not titel:
        raise ValueError("Titel fehlt")
    teaser = " ".join((felder.get("teaser") or basis.get("teaser") or "").split())[:400]
    absaetze = _absaetze(felder["text"]) if (felder.get("text") or "").strip() else basis.get("absaetze") or []
    row: dict[str, Any] = {
        "uid": f"einsendung:{vorgang}", "typ": "event" if e["art"] == "event" else "artikel", "status": "neu",
        "herkunft": "einsendung", "quelle_name": f"Einsendung {vorgang}", "quelle_sprache": "de",
        "kategorie": "events" if e["art"] == "event" else "community", "titel": titel, "teaser": teaser,
        "inhalt_html": "\n".join(f"<p>{html.escape(a)}</p>" for a in absaetze), "schlagworte": [],
        "hinweise": [VERMERK, *e["hinweise"]], "seo_titel": titel[:60], "meta_beschreibung": teaser[:155],
    }
    if e["art"] == "event":
        ort = f.get("ort", "")
        if f.get("stadt") and f["stadt"].lower() not in ort.lower():
            ort = f"{ort}, {f['stadt']}" if ort else f["stadt"]
        row.update(event_datum=event_datum or _lokal(f.get("beginn")),
                   event_ort=(felder.get("event_ort") or ort)[:300], ort=f.get("stadt", ""),
                   ticket_url=safe_url(felder.get("ticket_url") or f.get("ticket_link") or ""),
                   dach_bezug=(f.get("land") or "").upper() in DACH,
                   fakten={"einsendung": vorgang, "event_ende": _lokal(f.get("ende")),
                           "event_veranstalter": f.get("veranstalter", ""), "event_preis": f.get("eintritt", ""),
                           "event_land": (f.get("land") or "").upper()})
    else:
        row["fakten"] = {"einsendung": vorgang}
    row["original_json"] = {"titel": titel, "teaser": teaser, "inhalt_html": row["inhalt_html"]}
    bild = _bild_uebernehmen(store, settings, client, e)
    if isinstance(bild, str) and bild:
        row["hinweise"].append(bild)
    if isinstance(bild, tuple):
        row.update(bild_datei=bild[1], bild_credit="Bild: eingesandt", bild_origin="einsendung",
                   bild_alt=f"Eingesandtes Bild zu: {titel}"[:lizenz.ALT_MAX])
    # Einsendung beanspruchen (bedingt), Entwurf und Lizenz-Datensatz anlegen: eine Transaktion, alles oder nichts.
    # Die Bilddatei liegt bis zum Commit unter einem eigenen Namen; erst danach bekommt sie ihren Namen (so löscht ein
    # abgewiesener zweiter Versuch nie das Bild eines gelungenen).
    zwischen = None
    if isinstance(bild, tuple):
        import uuid

        settings.bilder_dir.mkdir(parents=True, exist_ok=True)
        zwischen = settings.bilder_dir / f".{bild[1]}.{uuid.uuid4().hex}.tmp"
        zwischen.write_bytes(bild[0])
    try:
        jetzt = now_iso()
        with store.transaktion():
            cur = store._write("UPDATE einsendungen SET status = 'uebernommen', abgeschlossen_at = ?, bearbeitet_von = ?, "
                               "aktualisiert = ? WHERE id = ? AND status = 'vorbereitet'", (jetzt, von, jetzt, e["id"]))
            if cur.rowcount != 1:
                raise Konflikt(f"Einsendung {vorgang} ist nicht (mehr) vorbereitet")
            did = store.insert_draft(row)
            if did is None:
                raise Konflikt(f"Zu Einsendung {vorgang} gibt es schon einen Entwurf")
            if zwischen is not None:
                lizenz.anlegen(store, datei=bild[1], daten=bild[0], draft_id=did,
                               felder=_bild_lizenz(e, von=von, verkleinert=bild[2]))
            store._write("UPDATE einsendungen SET entwurf_id = ? WHERE id = ?", (did, e["id"]))
        if zwischen is not None:
            zwischen.replace(settings.bilder_dir / bild[1])
    finally:
        if zwischen is not None:
            zwischen.unlink(missing_ok=True)
    _protokoll(store, "eingang_uebernommen", vorgang, wer=von, ausloeser="person", draft_id=did,
               notiz="Vorschlag des Agenten" if basis is e.get("modell_vorschlag") else "Entwurf aus den Feldern")
    store.event("eingang_uebernommen", vorgang=vorgang, entwurf=did, von=von)
    if client is not None:
        melden(store, client, nur=vorgang, wer=von, ausloeser="person")
    return did


# ---- Löschfrist ----------------------------------------------------------------------------------------------------

def loeschen(store, *, jetzt: datetime | None = None) -> Counter:
    """Personendaten nicht länger als nötig: 90 Tage nach Abschluss, Spam nach 7 Tagen, auf der Website nicht mehr
    vorhanden 30 Tage nach dem Vermerk. Protokoll nur mit Zählern. Sicherungen halten Gelöschtes noch bis zu 14 Tage
    (sicherung.AUFBEWAHREN_TAGE)."""
    jetzt = jetzt or datetime.now(timezone.utc)
    grenze = (jetzt - timedelta(days=FRIST_TAGE)).isoformat(timespec="seconds")
    grenze_spam = (jetzt - timedelta(days=SPAM_TAGE)).isoformat(timespec="seconds")
    out: Counter = Counter()
    out["geloescht"] = store._write(
        "DELETE FROM einsendungen WHERE status IN ('uebernommen', 'erledigt', 'abgelehnt') AND abgeschlossen_at IS NOT "
        "NULL AND abgeschlossen_at < ?", (grenze,)).rowcount
    out["spam"] = store._write("DELETE FROM einsendungen WHERE status = 'spam' AND abgeschlossen_at IS NOT NULL "
                               "AND abgeschlossen_at < ?", (grenze_spam,)).rowcount
    # Auf der Website nicht mehr vorhanden (dort gelöscht): die Kopie im Radar 30 Tage nach dem Vermerk, egal ob offen
    grenze_fehlt = (jetzt - timedelta(days=FEHLT_TAGE)).isoformat(timespec="seconds")
    out["fehlt"] = store._write("DELETE FROM einsendungen WHERE wp_status = 'fehlt' AND aktualisiert < ?",
                                (grenze_fehlt,)).rowcount
    if out["geloescht"] or out["spam"] or out["fehlt"]:
        repo.aktion(store, wer=DIENST, aktion="eingang_geloescht", gegenstand_typ="einsendung", kanal=KANAL,
                    regel_fassung=REGEL_FASSUNG, ausloeser="dienst",
                    notiz=f"{out['geloescht']} nach {FRIST_TAGE} Tagen, {out['spam']} Spam nach {SPAM_TAGE} Tagen, "
                          f"{out['fehlt']} ohne Gegenstück auf der Website nach {FEHLT_TAGE} Tagen")
    return out
