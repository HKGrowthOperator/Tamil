"""Verzeichnis, Radar-Seite (Festlegung F2, Vertrag B1.4): Einsendungen abholen, prüfen, im Cockpit entscheiden.

Ablauf (integrationen.md §3 „Verzeichnis“): Stopp-Schalter `verzeichnis` → `GET /verzeichnis/einsendungen?nach=` →
je Einsendung speichern → prüfen (feste Regeln, Dubletten gegen `GET /verzeichnis/eintraege`, bei Änderung und
Entfernen der gelesene Eintrag mit `stand`) → `POST …/status` `geprueft` mit `pruefung` → die Redaktion gibt frei
(`POST /verzeichnis/eintrag`, `/eintrag/{id}`, `/eintrag/{id}/entfernen`) oder lehnt ab (`POST …/status` `abgelehnt`).
Der Radar holt ab; WordPress ruft den Radar nie auf; niemand verschickt eine E-Mail.

- **Prüfen** (`pruefen`, Agent, ohne Entscheidung): Pflichtfelder (Name, Art, PLZ, Stadt, Land, ein Kontaktweg), Form
  von PLZ je Land, Telefon und Website-Adresse, Dubletten (ähnlicher Name und dazu gleiche PLZ, Telefonnummer oder
  Website – wie `tamil_site_vz_dubletten`), bei Änderungen der Unterschied alt ↔ neu. Die Befunde der Website
  (`regeln`) zählen mit. **Nichts Erfundenes:** Werte nur aus der Einsendung; Fehlendes heißt „fehlt“.
- **Kategorie** nur mit Modell (Rolle `verzeichnis` über `Claude.call`, nur Art, Name und Beschreibung, keine
  Kontaktdaten); nur ein Slug aus der Liste der Art gilt. Ohne Schlüssel entfällt der Vorschlag.
- **Entscheiden** (nur Menschen, Recht `verzeichnis_entscheiden`): neu mit den eingesandten Werten (die Redaktion darf
  sie ändern), Änderung Feld für Feld, Entfernen mit Bestätigung; immer gegen den gelesenen `stand`. **Premium nie.**
- **Protokoll** (`editorial_actions`, Kanal `verzeichnis`): Vorgangsnummer, Aktion, wer, Feldnamen – keine Namen,
  keine Kontaktdaten des Einsenders.
- **Löschfrist** (`loeschen`): 90 Tage nach Eingang, wie auf der Website.
"""

from __future__ import annotations

import json
import logging
import re
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlsplit

import requests
from pydantic import BaseModel

from . import schalter
from .store import now_iso
from .wordpress import VORUEBERGEHEND, VZ_VORGANG_RE, TamilRadarClient
from .workflow import repo

log = logging.getLogger(__name__)

KANAL = "verzeichnis"
REGEL_FASSUNG = "F2 vom 13.11.2026"
AGENT = "agent:verzeichnis"
DIENST = "dienst"
GEGENSTAND = "verzeichnis_einsendung"
FEHLT = "fehlt"

ARTEN = {"business": "Business", "dienstleister": "Dienstleister", "verein": "Verein", "tempel": "Tempel"}
TYPEN = {"neu": "Neuer Eintrag", "aenderung": "Änderung", "entfernen": "Entfernen"}
LAENDER = {"DE": "Deutschland", "AT": "Österreich", "CH": "Schweiz"}
# Felder wie tamil_site_vz_felder(): (Schlüssel, Bezeichnung, Pflicht, Höchstlänge). „Wahl“: der Einsender entscheidet,
# ob der Wert öffentlich gezeigt werden darf.
FELDER: tuple[tuple[str, str, bool, int], ...] = (
    ("name", "Name", True, 200), ("art", "Art", True, 20), ("kategorie", "Kategorie", False, 200),
    ("beschreibung", "Kurze Beschreibung", False, 600), ("adresse", "Straße und Hausnummer", False, 200),
    ("plz", "PLZ", True, 10), ("stadt", "Stadt", True, 100), ("land", "Land", True, 2),
    ("bundesland_kanton", "Bundesland oder Kanton", False, 60), ("telefon", "Telefon", False, 40),
    ("email", "E-Mail", False, 200), ("website", "Website", False, 300), ("oeffnungszeiten", "Öffnungszeiten", False, 300),
)
FELD_NAMEN = tuple(f[0] for f in FELDER)
LABEL = {f[0]: f[1] for f in FELDER} | {"kontakt": "Kontaktweg (Telefon, E-Mail oder Website)"}
PFLICHT = tuple(f[0] for f in FELDER if f[2])
MAX = {f[0]: f[3] for f in FELDER}
WAHL = ("adresse", "telefon", "email", "website", "oeffnungszeiten")
KONTAKTWEGE = ("telefon", "email", "website")
# Kategorien je Art: Slugs wie in WordPress (Upgrade-Schritt 4, sanitize_title „<art>-<Name>“ unter de_DE).
KATEGORIEN: dict[str, tuple[tuple[str, str], ...]] = {
    "business": (("business-restaurant-und-imbiss", "Restaurant und Imbiss"), ("business-lebensmittel", "Lebensmittel"),
                 ("business-textil-und-schmuck", "Textil und Schmuck"), ("business-reise", "Reise"),
                 ("business-sonstiges", "Sonstiges")),
    "dienstleister": (("dienstleister-recht-und-steuern", "Recht und Steuern"), ("dienstleister-gesundheit", "Gesundheit"),
                      ("dienstleister-uebersetzung", "Übersetzung"), ("dienstleister-foto-und-video", "Foto und Video"),
                      ("dienstleister-catering-und-feiern", "Catering und Feiern"), ("dienstleister-handwerk", "Handwerk"),
                      ("dienstleister-fahrschule", "Fahrschule"), ("dienstleister-sonstiges", "Sonstiges")),
    "verein": (("verein-kultur", "Kultur"), ("verein-sport", "Sport"), ("verein-tamilschule", "Tamilschule"),
               ("verein-hilfe-und-soziales", "Hilfe und Soziales")),
    "tempel": (("tempel-hindu-tempel", "Hindu-Tempel"), ("tempel-kirche", "Kirche"),
               ("tempel-weitere-gebetsstaette", "weitere Gebetsstätte")),
}
KATEGORIE_LABEL = {slug: label for paare in KATEGORIEN.values() for slug, label in paare}
REGIONEN = {
    "DE": ("Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen",
           "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen",
           "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen"),
    "AT": ("Burgenland", "Kärnten", "Niederösterreich", "Oberösterreich", "Salzburg", "Steiermark", "Tirol",
           "Vorarlberg", "Wien"),
    "CH": ("Aargau", "Appenzell Ausserrhoden", "Appenzell Innerrhoden", "Basel-Landschaft", "Basel-Stadt", "Bern",
           "Freiburg", "Genf", "Glarus", "Graubünden", "Jura", "Luzern", "Neuenburg", "Nidwalden", "Obwalden",
           "Schaffhausen", "Schwyz", "Solothurn", "St. Gallen", "Tessin", "Thurgau", "Uri", "Waadt", "Wallis", "Zug",
           "Zürich"),
}
OFFEN = ("abgeholt", "geprueft")
ABSCHLUESSE = ("freigegeben", "abgelehnt")
STATUS_LABEL = {"abgeholt": "abgeholt", "geprueft": "geprüft", "freigegeben": "freigegeben", "abgelehnt": "abgelehnt"}
FRIST_TAGE = 90
MAX_VERSUCHE = 3
_TELEFON_RE = re.compile(r"\+?[0-9][0-9 ()/\-]{4,24}")
_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class Konflikt(Exception):
    """Die Einsendung steht nicht (mehr) im erwarteten Zustand – jemand war schneller, oder die Website entschied."""


class StandVeraltet(Konflikt):
    """Der Eintrag hat sich seit dem Lesen geändert (409 tamil_vz_stand); alt/neu ist neu geladen."""


class Abgewiesen(Exception):
    """Die Website weist die Freigabe ab (4xx mit Fehlercode); nichts geändert."""

    def __init__(self, code: int, kennung: str, text: str):
        self.code, self.kennung = code, kennung
        super().__init__(text)


class VerzeichnisErgebnis(BaseModel):
    kategorie: str


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
    e["regeln"] = _json(e.get("regeln"), {})
    e["pruefung"] = _json(e.get("pruefung"), {})
    e["alt"] = _json(e.get("alt"), None)
    e["entscheidung"] = _json(e.get("entscheidung"), {})
    e["hinweise"] = _json(e.get("hinweise"), [])
    e["einwilligung"] = bool(e.get("einwilligung"))
    return e


def holen(store, vorgang: str) -> dict | None:
    return _zeile(store.db.execute("SELECT * FROM verzeichnis_einsendungen WHERE vorgangsnummer = ?",
                                   (vorgang,)).fetchone())


def liste(store, ansicht: str = "offen", limit: int = 200) -> list[dict]:
    """`offen` (abgeholt, geprüft), `abgeschlossen` oder `alle`; neueste zuerst."""
    status = OFFEN if ansicht == "offen" else ABSCHLUESSE if ansicht == "abgeschlossen" else ()
    sql, params = "SELECT * FROM verzeichnis_einsendungen", ()
    if status:
        sql, params = sql + f" WHERE status IN ({','.join('?' for _ in status)})", status
    rows = store.db.execute(sql + " ORDER BY eingang_at DESC, id DESC LIMIT ?", (*params, int(limit)))
    return [_zeile(r) for r in rows]


def zaehlen(store) -> dict[str, int]:
    out = {s: 0 for s in (*OFFEN, *ABSCHLUESSE)}
    for row in store.db.execute("SELECT status, COUNT(*) FROM verzeichnis_einsendungen GROUP BY status"):
        out[row[0]] = row[1]
    return out


def client_fuer(settings) -> TamilRadarClient:
    return TamilRadarClient(settings.wp_url, settings.wp_user, settings.wp_app_password)


def _protokoll(store, aktion: str, vorgang: str, *, wer: str, ausloeser: str, notiz: str = "",
               regel: str = REGEL_FASSUNG) -> None:
    repo.aktion(store, wer=wer, aktion=aktion, gegenstand_typ=GEGENSTAND, gegenstand_id=vorgang, kanal=KANAL,
                regel_fassung=regel, ausloeser=ausloeser, notiz=notiz)


def _hinweis_dazu(store, eid: int, hinweis: str) -> None:
    row = store.db.execute("SELECT hinweise FROM verzeichnis_einsendungen WHERE id = ?", (eid,)).fetchone()
    hinweise = _json(row[0] if row else None, [])
    if hinweis not in hinweise:
        hinweise.append(hinweis)
        store._write("UPDATE verzeichnis_einsendungen SET hinweise = ?, aktualisiert = ? WHERE id = ?",
                     (json.dumps(hinweise, ensure_ascii=False), now_iso(), eid))


# ---- Abholen -------------------------------------------------------------------------------------------------------

def _cursor(store) -> int:
    row = store.db.execute("SELECT wert FROM verzeichnis_stand WHERE schluessel = 'cursor'").fetchone()
    return int(row[0]) if row and str(row[0]).isdigit() else 0


def _cursor_setzen(store, wert: int) -> None:
    store._write("INSERT INTO verzeichnis_stand (schluessel, wert) VALUES ('cursor', ?) "
                 "ON CONFLICT(schluessel) DO UPDATE SET wert = excluded.wert", (str(int(wert)),))


def _text(wert: Any, laenge: int) -> str:
    return str(wert if wert is not None else "").strip()[:laenge]


def _felder_lesen(roh: Any) -> dict:
    """Nur bekannte Felder, je {wert, oeffentlich}; Premium oder Fremdes fällt weg."""
    if not isinstance(roh, dict):
        raise ValueError("Felder fehlen")
    out = {}
    for k in FELD_NAMEN:
        f = roh.get(k)
        if isinstance(f, dict):
            out[k] = {"wert": _text(f.get("wert"), MAX[k] + 100), "oeffentlich": bool(f.get("oeffentlich", True))}
    return out


def _regeln_lesen(roh: Any) -> dict:
    roh = roh if isinstance(roh, dict) else {}
    dubletten = [{"eintrag_id": int(d.get("eintrag_id") or 0), "grund": _text(d.get("grund"), 60)}
                 for d in roh.get("dubletten") or [] if isinstance(d, dict)]
    return {"fehlt": [_text(x, 40) for x in roh.get("fehlt") or []],
            "formfehler": [_text(x, 40) for x in roh.get("formfehler") or []], "dubletten": dubletten}


def _aufnehmen(store, e: dict) -> bool:
    """Eine Einsendung aus der Liste speichern; nur gültige und auf der Website noch offene. True, wenn neu."""
    vorgang, typ = str(e.get("vorgangsnummer") or ""), str(e.get("typ") or "")
    if not VZ_VORGANG_RE.fullmatch(vorgang) or typ not in TYPEN or e.get("status") not in ("neu", "geprueft"):
        return False
    felder = _felder_lesen(e.get("felder"))
    einsender = e.get("einsender") if isinstance(e.get("einsender"), dict) else {}
    einwilligung = e.get("einwilligung") if isinstance(e.get("einwilligung"), dict) else {}
    jetzt = now_iso()
    cur = store._write(
        "INSERT OR IGNORE INTO verzeichnis_einsendungen (wp_id, vorgangsnummer, typ, eintrag_id, status, wp_status, "
        "eingang_at, abgeholt_at, einsender_name, einsender_email, berechtigung, einwilligung, einwilligung_fassung, "
        "felder, anmerkung, regeln, aktualisiert) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (int(e.get("id") or 0), vorgang, typ, int(e.get("eintrag_id") or 0), "abgeholt", str(e["status"]),
         _text(e.get("eingang"), 40) or jetzt, jetzt, _text(einsender.get("name"), 200),
         _text(einsender.get("email"), 200), _text(e.get("berechtigung"), 20), 1 if einwilligung.get("erteilt") else 0,
         _text(einwilligung.get("fassung"), 40), json.dumps(felder, ensure_ascii=False),
         _text(e.get("anmerkung"), 2000), json.dumps(_regeln_lesen(e.get("regeln")), ensure_ascii=False), jetzt),
    )
    if cur.rowcount != 1:
        return False
    _protokoll(store, "verzeichnis_abgeholt", vorgang, wer=DIENST, ausloeser="dienst", notiz=f"Typ {typ}")
    return True


def abholen(store, client, *, anzahl: int = 50, max_seiten: int = 20) -> Counter:
    """Neue Einsendungen holen (Cursor `naechster`) und speichern. Hält der Schalter an, geschieht nichts – die
    Einsendungen bleiben auf der Website liegen. Ein zweiter Lauf legt nichts doppelt an."""
    out: Counter = Counter()
    cursor = _cursor(store)
    for _ in range(max_seiten):
        try:
            schalter.pruefen(store, KANAL)
        except schalter.Gestoppt:
            out["angehalten"] += 1
            return out
        daten = client.vz_einsendungen(nach=cursor, anzahl=anzahl)
        out["seiten"] += 1
        if daten is None:  # Funktion auf der Website aus: nichts abzuholen
            out["funktion_aus"] += 1
            break
        zeilen = daten["einsendungen"]
        for e in zeilen:
            try:  # eine kaputte Zeile hält den Cursor nicht auf: vermerken, weiter
                out["neu" if isinstance(e, dict) and _aufnehmen(store, e) else "uebersprungen"] += 1
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                out["kaputt"] += 1
                vorgang = str(e.get("vorgangsnummer") or "") if isinstance(e, dict) else ""
                gueltig = bool(VZ_VORGANG_RE.fullmatch(vorgang))
                log.warning("Verzeichnis-Einsendung %s nicht lesbar (%s) – übersprungen",
                            vorgang if gueltig else "ohne Vorgangsnummer", type(exc).__name__)
                if gueltig:
                    _protokoll(store, "verzeichnis_unlesbar", vorgang, wer=DIENST, ausloeser="dienst",
                               notiz=type(exc).__name__)
        vorher, weiter = cursor, int(daten.get("naechster") or cursor)
        if weiter > cursor:
            cursor = weiter
            _cursor_setzen(store, cursor)
        if len(zeilen) < anzahl or weiter <= vorher:  # letzte Seite (WordPress meldet kein „mehr“)
            break
    return out


# ---- Regeln (ohne Modell) ------------------------------------------------------------------------------------------

def _wert(e: dict, feld: str) -> str | None:
    """Wert zum Veröffentlichen: wie eingesandt; ein Wahlfeld ohne Haken „öffentlich“ ist leer. None = nicht eingesandt."""
    f = e["felder"].get(feld)
    if f is None:
        return None
    return "" if feld in WAHL and not f.get("oeffentlich", True) else str(f.get("wert") or "").strip()


def _eingesandt(e: dict) -> dict[str, str]:
    return {k: v for k in FELD_NAMEN if (v := _wert(e, k)) is not None}


def _gesamt(e: dict) -> dict[str, str]:
    """Was nach der Freigabe aller eingesandten Felder im Eintrag stünde (bei Änderungen über dem gelesenen Eintrag)."""
    basis = dict(e.get("alt") or {}) if e["typ"] != "neu" else {}
    return {**{k: str(v or "") for k, v in basis.items()}, **_eingesandt(e)}


def fehlt(werte: dict) -> list[str]:
    """Pflichtfelder, die fehlen (wie tamil_site_vz_fehlt); „kontakt“ für den fehlenden Kontaktweg."""
    out = [k for k in PFLICHT if not str(werte.get(k) or "").strip()]
    if not any(str(werte.get(k) or "").strip() for k in KONTAKTWEGE):
        out.append("kontakt")
    return out


def formfehler(werte: dict, land_vorgabe: str = "") -> dict[str, str]:
    """Form der Werte (wie tamil_site_vz_werte_pruefen, ohne Kategorie-Datenbank): Feld → Grund."""
    out: dict[str, str] = {}
    land = str(werte.get("land") or land_vorgabe or "").strip().upper()
    for k, w in werte.items():
        w = str(w or "").strip()
        if k not in MAX or not w:
            continue
        if len(w) > MAX[k]:
            out[k] = f"höchstens {MAX[k]} Zeichen"
        elif k == "art" and w not in ARTEN:
            out[k] = "keine der vier Arten"
        elif k == "land" and w.upper() not in LAENDER:
            out[k] = "nur DE, AT oder CH"
        elif k == "plz" and land in LAENDER and not re.fullmatch(r"\d{5}" if land == "DE" else r"\d{4}", w):
            out[k] = "in Deutschland fünf Ziffern" if land == "DE" else "in Österreich und der Schweiz vier Ziffern"
        elif k == "bundesland_kanton" and land in LAENDER and w not in REGIONEN[land]:
            out[k] = "nicht in der Liste für das Land"
        elif k == "telefon" and not _TELEFON_RE.fullmatch(w):
            out[k] = "keine Telefonnummer aus Ziffern"
        elif k == "email" and not _EMAIL_RE.fullmatch(w):
            out[k] = "keine gültige E-Mail-Adresse"
        elif k == "website" and not _url_ok(w):
            out[k] = "keine Adresse mit http:// oder https://"
        elif k == "kategorie":
            art = str(werte.get("art") or "")
            if w not in KATEGORIE_LABEL or (art in KATEGORIEN and w not in dict(KATEGORIEN[art])):
                out[k] = "Kategorie passt nicht zur Art"
    return out


def _url_ok(wert: str) -> bool:
    try:
        teile = urlsplit(wert)
    except ValueError:
        return False
    return teile.scheme in ("http", "https") and "." in (teile.hostname or "") and " " not in wert


_UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})
_RECHTSFORM = re.compile(r"(?<![^\W_])(e\.?\s?v\.?|gmbh|ug|ag|ohg|kg)(?![^\W_])")


def name_norm(name: str) -> str:
    """Name für den Vergleich (wie tamil_site_vz_name_norm): klein, ohne Akzente und Rechtsform, nur Buchstaben,
    Ziffern und Zeichen (auch tamilische Schrift)."""
    n = (name or "").lower().translate(_UMLAUT)
    zerlegt = unicodedata.normalize("NFKD", n)
    ohne = "".join(c for i, c in enumerate(zerlegt)
                   if not (unicodedata.combining(c) and i and "a" <= zerlegt[i - 1] <= "z"))  # nur lateinische Akzente
    ohne = unicodedata.normalize("NFKC", ohne)
    ohne = _RECHTSFORM.sub(" ", ohne)
    return "".join(c for c in ohne if unicodedata.category(c)[0] in "LNM")


def telefon_norm(telefon: str) -> str:
    ziffern = re.sub(r"\D+", "", telefon or "")
    return ziffern[-9:] if len(ziffern) > 9 else ziffern


def website_host(url: str) -> str:
    try:
        host = (urlsplit(url or "").hostname or "").lower()
    except ValueError:
        return ""
    return host.removeprefix("www.")


def _gemeinsam(a: str, b: str) -> int:
    """Wie PHP similar_text: längstes gemeinsames Stück, links und rechts davon rekursiv."""
    if not a or not b:
        return 0
    laenge, pa, pb = 0, 0, 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k > laenge:
                laenge, pa, pb = k, i, j
    if not laenge:
        return 0
    return laenge + _gemeinsam(a[:pa], b[:pb]) + _gemeinsam(a[pa + laenge:], b[pb + laenge:])


def aehnlich(a: str, b: str) -> bool:
    """Normalisierte Namen ähnlich (≥ 80 % wie similar_text, oder einer enthält den anderen ab vier Zeichen)."""
    if not a or not b:
        return False
    prozent = _gemeinsam(a, b) * 200 / (len(a) + len(b))
    return prozent >= 80 or (len(b) >= 4 and (a in b or b in a))


def dubletten(werte: dict, kandidaten: list[tuple[dict, dict]]) -> list[dict]:
    """Mögliche Dubletten (wie tamil_site_vz_dubletten): ähnlicher Name und dazu gleiche PLZ, Telefonnummer oder
    Website. Ergibt der Name nach der Normalisierung nichts, zählen Telefonnummer oder Website allein.
    `kandidaten`: (Verweis, Felder) – Verweis z. B. {"eintrag_id": 12, "name": …} oder {"einsendung": "V…"}."""
    name = name_norm(str(werte.get("name") or ""))
    plz = str(werte.get("plz") or "").strip()
    tel = telefon_norm(str(werte.get("telefon") or ""))
    host = website_host(str(werte.get("website") or ""))
    if not ((name and plz) or tel or host):
        return []
    treffer = []
    for verweis, f in kandidaten:
        gruende = []
        if name and plz and str(f.get("plz") or "").strip() == plz:
            gruende.append("plz")
        if tel and telefon_norm(str(f.get("telefon") or "")) == tel:
            gruende.append("telefon")
        if host and website_host(str(f.get("website") or "")) == host:
            gruende.append("website")
        if not gruende or (name and not aehnlich(name, name_norm(str(f.get("name") or "")))):
            continue
        treffer.append({**verweis, "grund": ("name+" if name else "") + "+".join(gruende)})
    return treffer


def _alle_eintraege(store, client, *, anzahl: int = 100, max_seiten: int = 50) -> list[dict] | None:
    """Alle Einträge der Website (für Dubletten); Schalter vor jeder Seite. None, wenn die Funktion dort aus ist."""
    out, nach = [], 0
    for _ in range(max_seiten):
        schalter.pruefen(store, KANAL)
        daten = client.vz_eintraege(nach=nach, anzahl=anzahl)
        if daten is None:
            return None
        zeilen = [z for z in daten["eintraege"] if isinstance(z, dict)]
        out += zeilen
        weiter = int(daten.get("naechster") or nach)
        if len(daten["eintraege"]) < anzahl or weiter <= nach:
            break
        nach = weiter
    return out


def _liste_text(namen: list[str]) -> str:
    return ", ".join(LABEL.get(n, n) for n in namen)


def regeln(store, e: dict, eintraege: list[dict]) -> dict:
    """Prüfung nach festen Regeln (ohne Modell), zusammen mit den Befunden der Website. Markiert, entscheidet nicht."""
    wp = e.get("regeln") or {}
    hinweise: list[str] = []
    eingesandt = _eingesandt(e)
    gesamt = _gesamt(e)
    if e["typ"] == "entfernen":
        offen_fehlt, form = [], {}
        hinweise.append("Eintrag entfernen: wird nach der Freigabe Entwurf (nicht gelöscht)")
    else:
        offen_fehlt = fehlt(gesamt)
        form = formfehler(eingesandt, str((e.get("alt") or {}).get("land") or ""))
    fehlt_alle = list(dict.fromkeys([*offen_fehlt, *[x for x in wp.get("fehlt", []) if e["typ"] != "entfernen"]]))
    form_alle = list(dict.fromkeys([*form, *wp.get("formfehler", [])]))
    if fehlt_alle:
        hinweise.append(f"unvollständig: {_liste_text(fehlt_alle)} {'fehlt' if len(fehlt_alle) == 1 else 'fehlen'}")
    for k in form_alle:
        hinweise.append(f"Form prüfen: {LABEL.get(k, k)}" + (f" ({form[k]})" if k in form else " (laut Website)"))
    roh_kontakt = [k for k in KONTAKTWEGE if (e["felder"].get(k) or {}).get("wert")]
    if e["typ"] == "neu" and roh_kontakt and "kontakt" in offen_fehlt:
        hinweise.append("Kontaktweg nur intern angegeben (nicht zur Veröffentlichung freigegeben)")
    for k in WAHL:
        f = e["felder"].get(k)
        if f and f.get("wert") and not f.get("oeffentlich", True):
            hinweise.append(f"{LABEL[k]}: nicht öffentlich – wird {'nicht übernommen' if e['typ'] == 'neu' else 'geleert'}")
    if not e.get("einwilligung"):
        hinweise.append("ohne Einwilligung")
    if e.get("berechtigung") == "hinweis":
        hinweise.append("Einsender ist nicht Inhaber (nur Hinweis)")
    dub: list[dict] = []
    if e["typ"] == "neu":
        namen = {int(z.get("id") or 0): str((z.get("felder") or {}).get("name") or "") for z in eintraege}
        kandidaten = [({"eintrag_id": int(z.get("id") or 0), "name": namen[int(z.get("id") or 0)]}, z.get("felder") or {})
                      for z in eintraege]
        # derselbe Vorschlag schon einmal eingesandt und noch nicht entschieden
        for row in store.db.execute("SELECT * FROM verzeichnis_einsendungen WHERE typ = 'neu' AND id < ? AND status "
                                    "IN ('abgeholt', 'geprueft') ORDER BY id", (e["id"],)):
            o = _zeile(row)
            kandidaten.append(({"eintrag_id": 0, "einsendung": o["vorgangsnummer"]}, _eingesandt(o)))
        dub = dubletten(eingesandt, kandidaten)
        bekannt = {d["eintrag_id"] for d in dub if d["eintrag_id"]}
        dub += [{**d, "name": namen.get(d["eintrag_id"], "")} for d in wp.get("dubletten", [])
                if d["eintrag_id"] not in bekannt]
    for d in dub:
        if d.get("einsendung"):
            hinweise.append(f"mögliche Dublette: Einsendung {d['einsendung']} ({d['grund']})")
        else:
            name = f" „{d['name']}“" if d.get("name") else ""
            hinweise.append(f"mögliche Dublette: Eintrag {d['eintrag_id']}{name} ({d['grund']})")
    unterschied = []
    if e["typ"] == "aenderung":
        alt = e.get("alt") or {}
        if not e.get("alt"):
            hinweise.append(f"Eintrag {e['eintrag_id']} gibt es auf der Website nicht (mehr)")
        unterschied = [{"feld": k, "alt": str(alt.get(k) or ""), "neu": v} for k, v in eingesandt.items()
                       if str(alt.get(k) or "") != v]
        if "art" in eingesandt and "kategorie" not in eingesandt:
            hinweise.append("Art geändert: Kategorie prüfen")
    if e["typ"] == "entfernen" and not e.get("alt"):
        hinweise.append(f"Eintrag {e['eintrag_id']} gibt es auf der Website nicht (mehr)")
    return {"fehlt": fehlt_alle, "formfehler": form_alle, "dubletten": dub, "kategorie_vorschlag": "",
            "unterschied": unterschied, "hinweise": hinweise}


# ---- Kategorie (Modell, Rolle „verzeichnis“) ----------------------------------------------------------------------

def _art(e: dict) -> str:
    art = _wert(e, "art")
    if art is None:
        art = str((e.get("alt") or {}).get("art") or "")
    return art if art in ARTEN else ""


def _kategorie(claude, e: dict) -> tuple[str, str, list[str]]:
    """(Slug oder leer, Prompt-Version, Hinweise). Nur Art, Name und Beschreibung (Kontaktdaten maskiert) gehen an das
    Modell; nur ein Slug aus der Liste der Art gilt."""
    from . import prompts
    from .eingang import kontakt_maskieren
    from .workflow.providers import json_block, prompt_version

    art = _art(e)
    system = prompts.load_prompt("verzeichnis")
    version = prompt_version(system)
    name = _wert(e, "name") if _wert(e, "name") is not None else str((e.get("alt") or {}).get("name") or "")
    beschreibung = _wert(e, "beschreibung") or ""
    daten = {"art": art, "name": kontakt_maskieren(name)[0], "beschreibung": kontakt_maskieren(beschreibung)[0]}
    liste_art = [{"slug": s, "label": label} for s, label in KATEGORIEN[art]]
    user = json_block("eintrag", daten) + "\n" + json_block("kategorien", liste_art)
    antwort = claude.call("verzeichnis", system, user, VerzeichnisErgebnis, kanal=KANAL)
    if not antwort.ok:
        return "", version, [f"kein Kategorie-Vorschlag (Antwort {antwort.status})"]
    slug = antwort.daten.kategorie.strip()
    if not slug:
        return "", version, ["kein Kategorie-Vorschlag (Modell unsicher)"]
    if slug not in dict(KATEGORIEN[art]):
        return "", version, [f"Kategorie-Vorschlag verworfen (nicht in der Liste für {ARTEN[art]})"]
    return slug, version, []


# ---- Prüfen (Agent) ------------------------------------------------------------------------------------------------

def _alt_lesen(client, e: dict) -> dict | None:
    """Gelesener Eintrag {felder, stand, status} oder None, wenn es ihn nicht gibt. Wirft bei Netzfehlern."""
    daten = client.vz_eintrag(int(e["eintrag_id"]))
    if not daten:
        return None
    felder = daten.get("felder") if isinstance(daten.get("felder"), dict) else {}
    return {"felder": {k: _text(felder.get(k), MAX[k] + 100) for k in FELD_NAMEN},
            "stand": _text(daten.get("stand"), 64), "status": _text(daten.get("status"), 20)}


def _alt_speichern(store, eid: int, alt: dict | None) -> None:
    store._write("UPDATE verzeichnis_einsendungen SET alt = ?, alt_stand = ?, alt_status = ?, aktualisiert = ? "
                 "WHERE id = ?", (json.dumps(alt["felder"], ensure_ascii=False) if alt else None,
                                  alt["stand"] if alt else None, alt["status"] if alt else None, now_iso(), eid))


def pruefen(store, client, claude=None, *, limit: int = 20) -> Counter:
    """Abgeholte Einsendungen prüfen, die Prüfung bei WordPress ablegen. Ohne `claude` (kein Schlüssel) nur die
    Regeln; der Kategorie-Vorschlag entfällt."""
    from .workflow.costs import BudgetErschoepft

    out: Counter = Counter()
    eintraege: list[dict] | None = None
    rows = store.db.execute("SELECT * FROM verzeichnis_einsendungen WHERE status = 'abgeholt' ORDER BY id LIMIT ?",
                            (int(limit),)).fetchall()
    for e in [_zeile(r) for r in rows]:
        try:
            schalter.pruefen(store, KANAL)
            if e["typ"] != "neu":
                alt = _alt_lesen(client, e)
                _alt_speichern(store, e["id"], alt)
                e["alt"], e["alt_stand"] = (alt["felder"], alt["stand"]) if alt else (None, None)
            elif eintraege is None:
                eintraege = _alle_eintraege(store, client)
                if eintraege is None:  # Funktion auf der Website aus
                    out["funktion_aus"] += 1
                    break
        except schalter.Gestoppt:
            out["angehalten"] += 1
            break
        except (requests.RequestException, RuntimeError) as exc:
            log.warning("Verzeichnis %s: Website nicht erreichbar (%s) – später erneut", e["vorgangsnummer"],
                        type(exc).__name__)
            out["fehler"] += 1
            continue
        pruefung = regeln(store, e, eintraege or [])
        regel = REGEL_FASSUNG + " · Regeln"
        modell_noetig = e["typ"] == "neu" or (e["typ"] == "aenderung" and "art" in e["felder"])
        if claude is None:
            if modell_noetig:
                pruefung["hinweise"].append("ohne Modell geprüft: kein Kategorie-Vorschlag")
        elif modell_noetig and _art(e):
            try:
                slug, version, extra = _kategorie(claude, e)
            except schalter.Gestoppt:
                out["angehalten"] += 1
                break
            except BudgetErschoepft:
                slug, version, extra = "", "", ["ohne Modell geprüft: kein Kategorie-Vorschlag (Budget erreicht)"]
            except Exception as exc:  # noqa: BLE001 – API-Fehler: später erneut, nach drei Versuchen nur Regeln
                if e["versuche"] + 1 < MAX_VERSUCHE:
                    store._write("UPDATE verzeichnis_einsendungen SET versuche = versuche + 1, aktualisiert = ? "
                                 "WHERE id = ?", (now_iso(), e["id"]))
                    out["fehler"] += 1
                    log.warning("Verzeichnis %s: Modell nicht erreichbar (%s)", e["vorgangsnummer"], type(exc).__name__)
                    continue
                slug, version, extra = "", "", ["ohne Modell geprüft: kein Kategorie-Vorschlag (Modell nicht erreichbar)"]
            if version:
                out["modell"] += 1
                regel = f"{REGEL_FASSUNG} · Prompt {version}"
            pruefung["kategorie_vorschlag"] = slug
            pruefung["hinweise"] += extra
        pruefung.update(agent=AGENT, fassung=regel, zeit=now_iso())
        cur = store._write(
            "UPDATE verzeichnis_einsendungen SET status = 'geprueft', geprueft_at = ?, pruefung = ?, aktualisiert = ? "
            "WHERE id = ? AND status = 'abgeholt'",
            (now_iso(), json.dumps(pruefung, ensure_ascii=False), now_iso(), e["id"]))
        if cur.rowcount == 1:
            _protokoll(store, "verzeichnis_geprueft", e["vorgangsnummer"], wer=AGENT, ausloeser="agent", regel=regel,
                       notiz=f"{len(pruefung['hinweise'])} Hinweise")
            out["geprueft"] += 1
    out.update(melden(store, client))
    return out


def lauf(store, client, claude=None) -> Counter:
    """Ein Takt des Dienstes: abholen, prüfen, Status an die Website melden."""
    out = abholen(store, client)
    if not out["angehalten"] and not out["funktion_aus"]:
        out.update(pruefen(store, client, claude))
    return out


# ---- Status an WordPress -------------------------------------------------------------------------------------------

def _kennung(data: dict) -> str:
    return data.get("code") if isinstance(data.get("code"), str) else ""


def _abgleich_status(store, client, e: dict) -> str | None:
    """Status der Einsendung auf der Website (None: dort nicht mehr vorhanden). Wirft bei Netzfehlern."""
    stand = client.vz_einsendung(e["vorgangsnummer"])
    return None if stand is None else _text(stand.get("status"), 20)


def melden(store, client, *, nur: str | None = None, wer: str = DIENST, ausloeser: str = "dienst") -> Counter:
    """Was WordPress noch nicht weiß, hinschicken: `geprueft` mit der Prüfung, `abgelehnt` nach der Entscheidung. Ein
    anderer Stand auf der Website (409) wird abgeglichen und vermerkt, nicht überschrieben."""
    out: Counter = Counter()
    sql = ("SELECT * FROM verzeichnis_einsendungen WHERE ((status = 'geprueft' AND COALESCE(wp_status, '') NOT IN "
           "('geprueft', 'freigegeben', 'abgelehnt', 'fehlt', 'abgewiesen')) OR (status = 'abgelehnt' AND "
           "COALESCE(wp_status, '') NOT IN ('abgelehnt', 'freigegeben', 'fehlt', 'abgewiesen')))")
    params: tuple = ()
    if nur:
        sql, params = sql + " AND vorgangsnummer = ?", (nur,)
    for e in [_zeile(r) for r in store.db.execute(sql + " ORDER BY id", params).fetchall()]:
        ziel, vorgang = e["status"], e["vorgangsnummer"]
        try:
            schalter.pruefen(store, KANAL)
        except schalter.Gestoppt:
            out["angehalten"] += 1
            break
        try:
            code, data = client.vz_status(vorgang, ziel, e["pruefung"] if ziel == "geprueft" else None)
        except (requests.RequestException, RuntimeError) as exc:
            log.warning("Status %s für %s unklar (%s) – Abgleich", ziel, vorgang, type(exc).__name__)
            code, data = 0, {}
        if code == 200:
            neu = _text(data.get("status"), 20) or ziel
        elif code == 404:
            neu = "fehlt"
        elif code in (0, 409) or code >= 500 or code in VORUEBERGEHEND:
            try:  # unklar oder anders entschieden: nachsehen statt blind wiederholen
                neu = _abgleich_status(store, client, e) or "fehlt"
            except (requests.RequestException, RuntimeError):
                out["offen"] += 1
                continue
            if code != 409 and neu != ziel and neu not in (*ABSCHLUESSE, "fehlt"):
                out["offen"] += 1  # nicht angekommen: beim nächsten Lauf erneut
                continue
        else:  # dauerhaft abgewiesen (4xx): vermerken, nicht bei jedem Lauf wiederholen
            neu = "abgewiesen"
            _hinweis_dazu(store, e["id"], f"Website lehnt den Status „{STATUS_LABEL[ziel]}“ ab (HTTP {code}"
                                          f"{', ' + _kennung(data) if _kennung(data) else ''}) – bitte dort prüfen")
        store._write("UPDATE verzeichnis_einsendungen SET wp_status = ?, aktualisiert = ? WHERE id = ?",
                     (neu, now_iso(), e["id"]))
        if neu == ziel:
            _protokoll(store, "verzeichnis_status", vorgang, wer=wer, ausloeser=ausloeser, notiz=f"an Website: {ziel}")
            out["gemeldet"] += 1
        elif neu == "fehlt":
            _hinweis_dazu(store, e["id"], "Auf der Website nicht mehr vorhanden")
            out["fehlt"] += 1
        elif neu in ABSCHLUESSE:
            # auf der Website schon anders entschieden: übernehmen, wenn hier noch offen; sonst nur vermerken
            if e["status"] in OFFEN:
                store._write("UPDATE verzeichnis_einsendungen SET status = ?, abgeschlossen_at = ?, aktualisiert = ? "
                             "WHERE id = ? AND status IN ('abgeholt', 'geprueft')", (neu, now_iso(), now_iso(), e["id"]))
            _hinweis_dazu(store, e["id"], f"Auf der Website schon „{STATUS_LABEL[neu]}“ – dort nicht geändert")
            _protokoll(store, "verzeichnis_status_konflikt", vorgang, wer=wer, ausloeser=ausloeser,
                       notiz=f"{ziel} ≠ {neu}")
            out["konflikt"] += 1
        elif neu == "abgewiesen":
            _protokoll(store, "verzeichnis_status_abgewiesen", vorgang, wer=wer, ausloeser=ausloeser,
                       notiz=f"HTTP {code}")
            out["abgewiesen"] += 1
        else:
            out["offen"] += 1
    return out


# ---- Für das Cockpit -----------------------------------------------------------------------------------------------

def vorschlag(e: dict) -> dict[str, str]:
    """Neuer Eintrag: je Feld der Wert aus der Einsendung; fehlt ein Pflichtfeld, steht dort „fehlt“ (nie geraten).
    Kategorie: der Vorschlag des Agenten oder leer."""
    out = {}
    for k, _, pflicht, _ in FELDER:
        if k == "kategorie":
            out[k] = (e.get("pruefung") or {}).get("kategorie_vorschlag") or ""
            continue
        w = _wert(e, k) or ""
        out[k] = w if w else (FEHLT if pflicht else "")
    return out


def vergleich(e: dict) -> list[dict]:
    """Änderung: je eingesandtem Feld alt neben neu (neu = Wert zum Veröffentlichen; nicht öffentlich heißt leer)."""
    if e["typ"] != "aenderung":
        return []
    alt = e.get("alt") or {}
    out = []
    for k, label, _, _ in FELDER:
        neu = _wert(e, k)
        if neu is None:
            continue
        a = str(alt.get(k) or "")
        out.append({"feld": k, "label": label, "alt": a, "neu": neu, "geaendert": a != neu,
                    "oeffentlich": bool(e["felder"][k].get("oeffentlich", True)), "roh": e["felder"][k].get("wert", "")})
    return out


def kategorie_text(slug: str) -> str:
    return KATEGORIE_LABEL.get(slug or "", slug or "")


# ---- Entscheiden (nur Menschen) ------------------------------------------------------------------------------------

def _kein_premium(*schluessel) -> None:
    if any("premium" in str(k).casefold() for k in schluessel):
        raise ValueError("Premium setzt nur ein Administrator in WordPress – nicht über das Cockpit")


def _freigabe_felder(e: dict, werte: dict, annehmen: list[str] | None, kategorie: str) -> dict:
    """Die Felder für die Freigabe: nur eingesandte (die Redaktion darf Werte ändern) und die Kategorie."""
    unbekannt = [k for k in werte if k not in FELD_NAMEN]
    if unbekannt:
        raise ValueError(f"Unbekannte Felder: {', '.join(sorted(map(str, unbekannt)))[:200]}")
    eingesandt = _eingesandt(e)
    if e["typ"] == "entfernen":
        if werte or annehmen or kategorie:
            raise ValueError("Beim Entfernen werden keine Felder geschrieben")
        return {}
    fremd = [k for k in [*werte, *(annehmen or [])] if k not in eingesandt and k != "kategorie"]
    if fremd:
        raise ValueError(f"Nicht in der Einsendung: {_liste_text(sorted(set(fremd)))} – nichts ergänzen")
    if e["typ"] == "neu":
        felder = {k: str(werte.get(k, v)).strip() for k, v in eingesandt.items() if k != "kategorie"}
    else:
        felder = {k: str(werte.get(k, eingesandt[k])).strip() for k in (annehmen or []) if k != "kategorie"}
    for k, v in felder.items():
        f = e["felder"][k]
        if v and k in WAHL and not f.get("oeffentlich", True):
            raise ValueError(f"{LABEL[k]}: der Einsender hat diesen Wert nicht zur Veröffentlichung freigegeben")
    if e["typ"] == "neu":
        felder = {k: v for k, v in felder.items() if v}
    kategorie = (kategorie or "").strip()
    if kategorie:
        art = felder.get("art") or _art(e)
        if kategorie not in dict(KATEGORIEN.get(art, ())):
            raise ValueError(f"Kategorie passt nicht zur Art „{ARTEN.get(art, art or '–')}“")
        felder["kategorie"] = kategorie
    if e["typ"] == "aenderung" and not felder:
        raise ValueError("Kein Feld angenommen – dann bitte ablehnen")
    return felder


_GRUND = {
    "tamil_vz_ungueltig": "ungültige Werte", "tamil_vz_unvollstaendig": "Eintrag wäre unvollständig",
    "tamil_vz_nicht_eingesandt": "Felder stehen nicht in der Einsendung",
    "tamil_vz_unbekannte_felder": "unbekannte Felder", "tamil_vz_nicht_oeffentlich": "Wert nicht zur Veröffentlichung "
    "freigegeben", "tamil_vz_premium_verboten": "Premium setzt nur ein Administrator in WordPress",
    "tamil_vz_falsche_einsendung": "Einsendung passt nicht zu diesem Eintrag",
    "tamil_vz_eintrag_fehlt": "Eintrag gibt es nicht mehr", "tamil_vz_einsendung_fehlt": "Einsendung gibt es nicht mehr",
    "tamil_funktion_aus": "Verzeichnis ist auf der Website ausgeschaltet",
}


def _abweisung(code: int, data: dict) -> Abgewiesen:
    kennung = _kennung(data)
    extra = data.get("data") if isinstance(data.get("data"), dict) else {}
    teile = [_GRUND.get(kennung, f"HTTP {code}{' ' + kennung[:60] if kennung else ''}")]
    if isinstance(extra.get("fehler"), dict):
        teile.append("; ".join(f"{k}: {str(v)[:120]}" for k, v in list(extra["fehler"].items())[:8]))
    for schluessel in ("felder", "fehlt"):
        if isinstance(extra.get(schluessel), list):
            teile.append(", ".join(str(x)[:40] for x in extra[schluessel][:12]))
    if extra.get("feld"):
        teile.append(str(extra["feld"])[:40])
    return Abgewiesen(code, kennung, "Website weist ab: " + " – ".join(t for t in teile if t))


def _abschliessen(store, e: dict, status: str, *, von: str, entscheidung: dict | None = None,
                  eintrag_id: int | None = None) -> bool:
    cur = store._write(
        "UPDATE verzeichnis_einsendungen SET status = ?, wp_status = COALESCE(?, wp_status), abgeschlossen_at = ?, "
        "bearbeitet_von = ?, entscheidung = COALESCE(?, entscheidung), eintrag_id = COALESCE(?, eintrag_id), "
        "aktualisiert = ? WHERE id = ? AND status IN ('abgeholt', 'geprueft')",
        (status, status if entscheidung is not None else None, now_iso(), von,
         json.dumps(entscheidung, ensure_ascii=False) if entscheidung is not None else None, eintrag_id, now_iso(),
         e["id"]))
    return cur.rowcount == 1


def _freigegeben(store, e: dict, *, von: str, aktion: str, felder: dict, daten: dict) -> dict:
    eintrag = daten.get("eintrag") if isinstance(daten.get("eintrag"), dict) else {}
    einsendung = daten.get("einsendung") if isinstance(daten.get("einsendung"), dict) else {}
    wp_entscheidung = einsendung.get("entscheidung") if isinstance(einsendung.get("entscheidung"), dict) else {}
    eintrag_id = int(eintrag.get("id") or einsendung.get("eintrag_id") or e["eintrag_id"] or 0) or None
    entscheidung = {"aktion": aktion, "felder": sorted(felder), "wer": von, "zeit": now_iso(),
                    "bereits": bool(daten.get("bereits")), "abgeglichen": bool(daten.get("abgeglichen")),
                    "abweichend": [str(x)[:40] for x in wp_entscheidung.get("abweichend") or []]}
    if _abschliessen(store, e, "freigegeben", von=von, entscheidung=entscheidung, eintrag_id=eintrag_id):
        notiz = f"{aktion}: {','.join(sorted(felder)) or '–'}"
        if entscheidung["abweichend"]:
            notiz += f"; abweichend: {','.join(entscheidung['abweichend'])}"
        _protokoll(store, "verzeichnis_freigegeben", e["vorgangsnummer"], wer=von, ausloeser="person", notiz=notiz)
        store.event("verzeichnis_freigegeben", vorgang=e["vorgangsnummer"], eintrag=eintrag_id, aktion=aktion, von=von)
    return daten


def freigeben(store, client, vorgang: str, *, von: str, werte: dict | None = None, annehmen: list[str] | None = None,
              kategorie: str = "") -> dict:
    """Freigabe durch die Redaktion: neu → `POST /eintrag` (eingesandte Werte, von der Redaktion geändert),
    Änderung → `POST /eintrag/{id}` nur mit den angenommenen Feldern gegen den gelesenen `stand`, Entfernen →
    `POST /eintrag/{id}/entfernen`. Premium nie. Gibt die Antwort der Website zurück. Wirft ValueError (Eingabe),
    Konflikt / StandVeraltet (Stand), Abgewiesen (Website), schalter.Gestoppt (Kanal angehalten)."""
    werte = dict(werte or {})
    _kein_premium(*werte, *(annehmen or []), kategorie)
    e = holen(store, vorgang)
    if e is None:
        raise LookupError(vorgang)
    felder = _freigabe_felder(e, werte, annehmen, kategorie)
    if e["status"] != "geprueft":
        raise Konflikt(f"Einsendung {vorgang} ist {'noch nicht geprüft' if e['status'] == 'abgeholt' else 'schon ' + STATUS_LABEL.get(e['status'], e['status'])}")
    if e["typ"] != "neu" and not e.get("alt_stand"):
        raise Konflikt(f"Eintrag {e['eintrag_id']} konnte nicht gelesen werden – erst neu prüfen")
    aktion = {"neu": "anlegen", "aenderung": "aendern", "entfernen": "entfernen"}[e["typ"]]
    schalter.pruefen(store, KANAL)  # unmittelbar vor dem Aufruf nach außen
    try:
        if e["typ"] == "neu":
            code, daten = client.vz_anlegen(vorgang, felder)
        elif e["typ"] == "aenderung":
            code, daten = client.vz_aendern(e["eintrag_id"], vorgang, e["alt_stand"], felder)
        else:
            code, daten = client.vz_entfernen(e["eintrag_id"], vorgang, e["alt_stand"])
    except (requests.RequestException, RuntimeError) as exc:
        log.warning("Freigabe %s: Ausgang unklar (%s) – Abgleich", vorgang, type(exc).__name__)
        code, daten = 0, {}
    if code in (200, 201):
        return _freigegeben(store, e, von=von, aktion=aktion, felder=felder, daten=daten)
    kennung = _kennung(daten)
    if code == 409 and kennung == "tamil_vz_stand":
        try:
            alt = _alt_lesen(client, e)
        except (requests.RequestException, RuntimeError):
            alt = None
        if alt is not None:
            _alt_speichern(store, e["id"], alt)
            e = holen(store, vorgang)
            pruefung = dict(e["pruefung"])
            pruefung["unterschied"] = [{"feld": z["feld"], "alt": z["alt"], "neu": z["neu"]} for z in vergleich(e)
                                       if z["geaendert"]]
            store._write("UPDATE verzeichnis_einsendungen SET pruefung = ?, aktualisiert = ? WHERE id = ?",
                         (json.dumps(pruefung, ensure_ascii=False), now_iso(), e["id"]))
        _protokoll(store, "verzeichnis_stand_veraltet", vorgang, wer=von, ausloeser="person")
        raise StandVeraltet("Der Eintrag wurde seit dem Lesen auf der Website geändert. Alt und neu sind neu geladen – "
                            "bitte noch einmal vergleichen und freigeben.")
    if code == 409 and kennung == "tamil_vz_abgelehnt":
        if _abschliessen(store, e, "abgelehnt", von=von, entscheidung={"aktion": "abgelehnt", "auf_der_website": True}):
            _hinweis_dazu(store, e["id"], "Auf der Website schon „abgelehnt“ – dort nicht geändert")
        raise Konflikt(f"Einsendung {vorgang} ist auf der Website schon abgelehnt")
    if code == 409 and kennung in ("tamil_vz_in_arbeit", "tamil_vz_gesperrt"):
        raise Konflikt("Auf der Website läuft gerade eine Freigabe für diese Einsendung oder diesen Eintrag – in zwei "
                       "Minuten noch einmal versuchen")
    if 400 <= code < 500 and code not in (401, 408, 429):
        raise _abweisung(code, daten)
    # unklarer Ausgang (Netz, 5xx, Anmeldung): abgleichen statt blind wiederholen
    try:
        stand = client.vz_einsendung(vorgang)
    except (requests.RequestException, RuntimeError):
        stand = None
    if stand and stand.get("status") == "freigegeben" and stand.get("entscheidung"):
        return _freigegeben(store, e, von=von, aktion=aktion, felder=felder,
                            daten={"abgeglichen": True, "einsendung": stand,
                                   "eintrag": {"id": int(stand.get("eintrag_id") or 0)}})
    if stand and stand.get("status") == "freigegeben":
        raise Konflikt("Die Freigabe ist auf der Website begonnen, aber nicht bestätigt – in zwei Minuten noch einmal "
                       "freigeben (die Website setzt fort, nichts doppelt)")
    raise Konflikt(f"Website nicht erreichbar oder Fehler (HTTP {code or 'ohne Antwort'}) – nichts geändert, bitte "
                   "später noch einmal freigeben")


def ablehnen(store, client, vorgang: str, *, von: str) -> None:
    """Ablehnen ändert nichts am Eintrag: nur die Einsendung wird abgelehnt (bedingt) und an WordPress gemeldet."""
    e = holen(store, vorgang)
    if e is None:
        raise LookupError(vorgang)
    if not _abschliessen(store, e, "abgelehnt", von=von):
        raise Konflikt(f"Einsendung {vorgang} ist schon {STATUS_LABEL.get(e['status'], e['status'])}")
    store._write("UPDATE verzeichnis_einsendungen SET entscheidung = ? WHERE id = ?",
                 (json.dumps({"aktion": "abgelehnt", "wer": von, "zeit": now_iso()}), e["id"]))
    _protokoll(store, "verzeichnis_abgelehnt", vorgang, wer=von, ausloeser="person")
    if client is not None:
        melden(store, client, nur=vorgang, wer=von, ausloeser="person")


# ---- Löschfrist ----------------------------------------------------------------------------------------------------

def loeschen(store, *, jetzt: datetime | None = None) -> Counter:
    """Personendaten nicht länger als nötig: die Einsendung (mit Name und E-Mail) 90 Tage nach Eingang, wie auf der
    Website. Protokoll nur mit Zählern. Sicherungen halten Gelöschtes noch bis zu ihrer eigenen Frist."""
    jetzt = jetzt or datetime.now(timezone.utc)
    grenze = (jetzt - timedelta(days=FRIST_TAGE)).astimezone(timezone.utc).isoformat(timespec="seconds")
    out: Counter = Counter()
    out["geloescht"] = store._write("DELETE FROM verzeichnis_einsendungen WHERE COALESCE(NULLIF(eingang_at, ''), "
                                    "abgeholt_at) < ?", (grenze,)).rowcount
    if out["geloescht"]:
        repo.aktion(store, wer=DIENST, aktion="verzeichnis_geloescht", gegenstand_typ=GEGENSTAND, kanal=KANAL,
                    regel_fassung=REGEL_FASSUNG, ausloeser="dienst",
                    notiz=f"{out['geloescht']} nach {FRIST_TAGE} Tagen")
    return out
