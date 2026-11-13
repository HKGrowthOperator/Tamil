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
    e["entwurf"] = _json(e.get("entwurf"), None)
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
    roh = e.get("felder") if isinstance(e.get("felder"), dict) else {}
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
            out["neu" if isinstance(e, dict) and _aufnehmen(store, e) else "uebersprungen"] += 1
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


# ---- Modell (Rolle „eingang“) ---------------------------------------------------------------------------------------

_URL = re.compile(r"(?:https?://|www\.)[^\s\"'<>]+", re.I)
_ZAHL = re.compile(r"\d+")


def fremde_angaben(texte: list[str], erlaubt: str) -> list[str]:
    """Zahlen, Links und Kontaktangaben im Modelltext, die nicht in der Einsendung stehen („nichts Erfundenes“)."""
    zahlen = {int(z) for z in _ZAHL.findall(erlaubt)}
    fremd: list[str] = []
    for t in texte:
        for url in _URL.findall(t):
            url = url.rstrip(".,;:!?)")
            if url not in erlaubt:
                fremd.append(url)
        if "@" in t:
            fremd.append("E-Mail-Adresse")
        fremd += [z for z in _ZAHL.findall(_URL.sub(" ", t)) if int(z) not in zahlen]
    return list(dict.fromkeys(fremd))


def _modell_eingabe(e: dict, hinweise: list[str]) -> tuple[str, str]:
    """Nutzer-Prompt ohne Kontaktdaten (Name, E-Mail, Telefon gehen nicht an das Modell) und der erlaubte Text."""
    from .workflow.providers import json_block

    felder = {k: v for k, v in e["felder"].items() if v}
    daten = {"art": e["art"], "felder": felder, "datum_text": datum_text(e["felder"].get("beginn"))}
    user = json_block("einsendung", daten) + "\n" + json_block("hinweise", hinweise)
    return user, json.dumps(daten, ensure_ascii=False)


def _modell(store, claude, e: dict, hinweise: list[str]) -> tuple[str, dict | None, str, list[str]]:
    """(Zusammenfassung, Entwurf, Prompt-Version, zusätzliche Hinweise) oder wirft Gestoppt/BudgetErschoepft/Fehler."""
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
        return "", None, version, [f"Modell-Entwurf verworfen: Angabe nicht in der Einsendung ({', '.join(fremd[:3])})"]
    entwurf = None
    if e["art"] in MIT_ENTWURF and d.titel.strip() and absaetze:
        entwurf = {"titel": " ".join(d.titel.split())[:90], "teaser": " ".join(d.teaser.split())[:300],
                   "absaetze": absaetze, "quelle": "modell"}
    return " ".join(d.zusammenfassung.split())[:500], entwurf, version, []


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
        zusammenfassung, entwurf = regel_vorbereitung(e)
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
            entwurf = e_modell or entwurf
        cur = store._write(
            "UPDATE einsendungen SET status = 'vorbereitet', vorbereitet_at = ?, zusammenfassung = ?, hinweise = ?, "
            "dublette_von = ?, entwurf = ?, aktualisiert = ? WHERE id = ? AND status = 'abgeholt'",
            (now_iso(), zusammenfassung, json.dumps(hinweise, ensure_ascii=False), dublette_von,
             json.dumps(entwurf, ensure_ascii=False) if entwurf else None, now_iso(), e["id"]))
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


def _bild_uebernehmen(store, settings, client, e: dict) -> tuple[bytes, str] | str:
    """Bild der Einsendung holen und prüfen; (JPEG-Daten, Dateiname) oder ein Hinweis, warum nicht."""
    bild = e.get("bild")
    if not bild:
        return ""
    if not bild.get("recht_bestaetigt"):
        return "Bild der Einsendung nicht übernommen (Nutzungsrecht nicht bestätigt)"
    if client is None:
        return "Bild der Einsendung nicht übernommen (WordPress nicht verbunden)"
    try:
        schalter.pruefen(store, KANAL)
        daten = client.einsendung_bild(e["vorgangsnummer"])
    except schalter.Gestoppt:
        return "Bild der Einsendung nicht übernommen (Eingang angehalten)"
    except (requests.RequestException, RuntimeError):
        return "Bild der Einsendung nicht übernommen (Website nicht erreichbar)"
    if not daten:
        return "Bild der Einsendung nicht übernommen (auf der Website nicht vorhanden)"
    try:
        roh = base64.b64decode(str(daten.get("daten_base64") or ""), validate=True)
    except ValueError:
        return "Bild der Einsendung nicht übernommen (beschädigt)"
    if daten.get("typ") not in BILD_TYPEN or len(roh) > BILD_MAX or \
            hashlib.sha256(roh).hexdigest() != (bild.get("sha256") or daten.get("sha256")):
        return "Bild der Einsendung nicht übernommen (Typ, Größe oder Prüfsumme passt nicht)"
    try:
        from PIL import Image

        with Image.open(io.BytesIO(roh)) as img:
            img.load()
            buf = io.BytesIO()
            img.convert("RGB").save(buf, "JPEG", quality=88)  # neu gespeichert, ohne Metadaten
    except Exception:  # noqa: BLE001 – kein lesbares Bild
        return "Bild der Einsendung nicht übernommen (kein lesbares Bild)"
    return buf.getvalue(), f"einsendung-{e['vorgangsnummer'].lower()}.jpg"


def uebernehmen(store, settings, vorgang: str, *, von: str, felder: dict, client=None) -> int:
    """Event oder Beitrag als Entwurf übernehmen (Vermerk „Angaben des Einsenders, ungeprüft“). `felder` sind die
    Änderungen der Redaktion (titel, teaser, text, event_datum, event_ort, ticket_url). Gibt die Entwurfs-ID zurück."""
    e = holen(store, vorgang)
    if e is None:
        raise LookupError(vorgang)
    if e["art"] not in MIT_ENTWURF:
        raise ValueError("Übernehmen gibt es nur für Events und Beiträge; sonst Status und Notiz")
    if e["status"] != "vorbereitet":
        raise Konflikt(f"Einsendung {vorgang} ist nicht (mehr) vorbereitet")
    f = e["felder"]
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
        row.update(event_datum=(felder.get("event_datum") or _lokal(f.get("beginn")))[:16],
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
    # Erst die Einsendung beanspruchen (bedingt), dann den Entwurf anlegen: nie zwei Entwürfe zu einer Einsendung
    jetzt = now_iso()
    cur = store._write("UPDATE einsendungen SET status = 'uebernommen', abgeschlossen_at = ?, bearbeitet_von = ?, "
                       "aktualisiert = ? WHERE id = ? AND status = 'vorbereitet'", (jetzt, von, jetzt, e["id"]))
    if cur.rowcount != 1:
        raise Konflikt(f"Einsendung {vorgang} ist nicht (mehr) vorbereitet")
    try:
        if isinstance(bild, tuple):
            daten, datei = bild
            settings.bilder_dir.mkdir(parents=True, exist_ok=True)
            (settings.bilder_dir / datei).write_bytes(daten)
            row.update(bild_datei=datei, bild_credit="Bild: eingesandt", bild_alt=titel[:120], bild_origin="einsendung")
        did = store.insert_draft(row)
        if did is None:
            raise Konflikt(f"Zu Einsendung {vorgang} gibt es schon einen Entwurf")
    except BaseException:
        store._write("UPDATE einsendungen SET status = 'vorbereitet', abgeschlossen_at = NULL WHERE id = ?", (e["id"],))
        raise
    if isinstance(bild, tuple):
        repo.asset_anlegen(store, datei=bild[1], herkunft="upload", rechteinhaber=f"Einsender (Vorgang {vorgang})",
                           lizenz="Nutzungsrecht vom Einsender bestätigt", umfang="Beitrag auf Tamil.de",
                           attribution="Bild: eingesandt", draft_id=did, daten=bild[0])
    store._write("UPDATE einsendungen SET entwurf_id = ? WHERE id = ?", (did, e["id"]))
    _protokoll(store, "eingang_uebernommen", vorgang, wer=von, ausloeser="person", draft_id=did)
    store.event("eingang_uebernommen", vorgang=vorgang, entwurf=did, von=von)
    if client is not None:
        melden(store, client, nur=vorgang, wer=von, ausloeser="person")
    return did


# ---- Löschfrist ----------------------------------------------------------------------------------------------------

def loeschen(store, *, jetzt: datetime | None = None) -> Counter:
    """Personendaten nicht länger als nötig: 90 Tage nach Abschluss, Spam nach 7 Tagen. Protokoll nur mit Zählern."""
    jetzt = jetzt or datetime.now(timezone.utc)
    grenze = (jetzt - timedelta(days=FRIST_TAGE)).isoformat(timespec="seconds")
    grenze_spam = (jetzt - timedelta(days=SPAM_TAGE)).isoformat(timespec="seconds")
    out: Counter = Counter()
    out["geloescht"] = store._write(
        "DELETE FROM einsendungen WHERE status IN ('uebernommen', 'erledigt', 'abgelehnt') AND abgeschlossen_at IS NOT "
        "NULL AND abgeschlossen_at < ?", (grenze,)).rowcount
    out["spam"] = store._write("DELETE FROM einsendungen WHERE status = 'spam' AND abgeschlossen_at IS NOT NULL "
                               "AND abgeschlossen_at < ?", (grenze_spam,)).rowcount
    if out["geloescht"] or out["spam"]:
        repo.aktion(store, wer=DIENST, aktion="eingang_geloescht", gegenstand_typ="einsendung", kanal=KANAL,
                    regel_fassung=REGEL_FASSUNG, ausloeser="dienst",
                    notiz=f"{out['geloescht']} nach {FRIST_TAGE} Tagen, {out['spam']} Spam nach {SPAM_TAGE} Tagen")
    return out
