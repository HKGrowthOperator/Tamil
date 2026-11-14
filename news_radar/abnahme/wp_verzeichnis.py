"""Fake-Transport für die Verzeichnis-Routen von tamil-radar/v1 (Festlegung F2, integrationen.md §3 „Verzeichnis“) –
ohne Netz.

Steht anstelle der `requests.Session` im `TamilRadarClient` und verhält sich wie das Plugin
(`wordpress/plugins/tamil-site/includes/verzeichnis.php`): Einsendungen mit Cursor (`naechster`), eine Einsendung mit
`regeln`, Status `geprueft`/`abgelehnt` mit `pruefung`, Einträge mit `stand`, Freigabe anlegen/ändern/entfernen mit
den Prüfungen der Website (Premium 403, nur eingesandte Felder, nicht öffentlich 409, veralteter Stand 409, wiederholt
`bereits`). Für Tests und die Abnahme; alle Angaben sind erfunden (example.test).
"""

from __future__ import annotations

import hashlib
import json as jsonlib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import requests

from ..verzeichnis import KATEGORIE_LABEL, REGIONEN
from .wp_eingang import Antwort, _fehler

NS = "/wp-json/tamil-radar/v1/verzeichnis/"
ABHAENGIG = ("plz", "land", "bundesland_kanton", "art", "kategorie")
FELDER = ("name", "art", "kategorie", "beschreibung", "adresse", "plz", "stadt", "land", "bundesland_kanton", "telefon",
          "email", "website", "oeffnungszeiten")
PFLICHT = ("name", "art", "plz", "stadt", "land")
WAHL = ("adresse", "telefon", "email", "website", "oeffnungszeiten")
KONTAKT = ("telefon", "email", "website")
ARTEN = ("business", "dienstleister", "verein", "tempel")
_ZEICHEN = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _jetzt() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fehlt(werte: dict) -> list[str]:
    fehlt = [k for k in PFLICHT if not str(werte.get(k) or "")]
    if not any(str(werte.get(k) or "") for k in KONTAKT):
        fehlt.append("kontakt")
    return fehlt


def _formfehler(werte: dict, land_vorgabe: str = "") -> dict[str, str]:
    fehler: dict[str, str] = {}
    land = str(werte.get("land") or land_vorgabe).upper()
    for k, w in werte.items():
        w = str(w or "")
        if not w:
            continue
        if k == "art" and w not in ARTEN:
            fehler[k] = "Bitte eine der vier Arten wählen."
        elif k == "land" and w.upper() not in ("DE", "AT", "CH"):
            fehler[k] = "Bitte Deutschland, Österreich oder die Schweiz wählen."
        elif k == "plz" and land and not re.fullmatch(r"\d{5}" if land == "DE" else r"\d{4}", w):
            fehler[k] = "PLZ passt nicht zum Land."
        elif k == "telefon" and not re.fullmatch(r"\+?[0-9][0-9 ()/\-]{4,24}", w):
            fehler[k] = "Bitte eine Telefonnummer aus Ziffern angeben."
        elif k == "website" and not re.fullmatch(r"https?://[^\s/]+\.[^\s/]+(/\S*)?", w):
            fehler[k] = "Bitte die Adresse der Website mit https:// angeben."
        elif k == "bundesland_kanton" and land in REGIONEN and w not in REGIONEN[land]:
            fehler[k] = "Bitte ein Bundesland oder einen Kanton aus der Liste wählen."
        elif k == "kategorie" and (w not in KATEGORIE_LABEL or (werte.get("art") and not w.startswith(f"{werte['art']}-"))):
            fehler[k] = "Diese Kategorie gibt es für diese Art nicht."
    return fehler


class FakeWordPressVerzeichnis:
    """Session-Ersatz: `request(method, url, **kw)` wie requests. `aufrufe` zeichnet (Methode, Pfad) auf."""

    def __init__(self, *, funktion_an: bool = True):
        self.auth = None
        self.headers: dict[str, str] = {}
        self.funktion_an = funktion_an
        self.einsendungen: list[dict] = []
        self.eintraege: dict[int, dict] = {}
        self.aufrufe: list[tuple[str, str]] = []
        self.koerper: list[tuple[str, str, dict]] = []  # (Methode, Pfad, JSON) jeder schreibenden Anfrage
        self.netzfehler = False
        self.abbruch_nach_senden: set[str] = set()  # Vorgang: Freigabe läuft durch, dann bricht die Verbindung ab
        self.regeln_extra: dict[str, dict] = {}  # Vorgang → zusätzliche Befunde der Website (z. B. eine Dublette)
        self._naechste_id = 100

    # ---- Website-Seite -------------------------------------------------------------------------------------------
    def eintrag_anlegen(self, felder: dict, *, premium: bool = False, status: str = "veroeffentlicht") -> int:
        self._naechste_id += 1
        self.eintraege[self._naechste_id] = {"felder": {k: str(felder.get(k, "")) for k in FELDER}, "premium": premium,
                                             "status": status, "vorgang": ""}
        return self._naechste_id

    def einreichen(self, typ: str, felder: dict, *, eintrag_id: int = 0, nicht_oeffentlich: tuple[str, ...] = (),
                   name: str = "Erika Beispiel", email: str = "erika@example.test", berechtigung: str = "inhaber",
                   anmerkung: str = "") -> str:
        n = len(self.einsendungen) + 1
        vorgang = "V261114-" + "".join(_ZEICHEN[(n * 7 + i * 3) % len(_ZEICHEN)] for i in range(5))
        self.einsendungen.append({
            "id": n, "vorgangsnummer": vorgang, "typ": typ, "eintrag_id": eintrag_id, "status": "neu",
            "eingang": _jetzt(), "abgeschlossen": None, "einsender": {"name": name, "email": email},
            "berechtigung": berechtigung,
            "felder": {k: {"wert": str(v), "oeffentlich": k not in nicht_oeffentlich} for k, v in felder.items()},
            "anmerkung": anmerkung, "einwilligung": {"erteilt": True, "fassung": "2026-11-vorlaeufig"},
            "pruefung": {}, "entscheidung": {},
        })
        return vorgang

    def einsendung(self, vorgang: str) -> dict | None:
        return next((z for z in self.einsendungen if z["vorgangsnummer"] == vorgang), None)

    def stand(self, eid: int) -> str:
        e = self.eintraege[eid]
        roh = jsonlib.dumps([e["felder"], e["status"]], sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(roh.encode()).hexdigest()[:16]

    def eintrag_ausgabe(self, eid: int) -> dict:
        e = self.eintraege[eid]
        return {"id": eid, "felder": dict(e["felder"]), "premium": e["premium"], "status": e["status"],
                "stand": self.stand(eid), "link": f"https://www.tamil.test/verzeichnis/eintrag-{eid}/"
                if e["status"] == "veroeffentlicht" else "", "geaendert": _jetzt()}

    def _werte(self, z: dict) -> dict:
        return {k: f["wert"] for k, f in z["felder"].items()}

    def _regeln(self, z: dict) -> dict:
        werte = self._werte(z)
        if z["typ"] != "neu":
            alt = dict(self.eintraege.get(z["eintrag_id"], {}).get("felder", {}))
            gesamt = {**alt, **werte}
            out = {"fehlt": [] if z["typ"] == "entfernen" else _fehlt(gesamt),
                   "formfehler": list(_formfehler(werte, gesamt.get("land", ""))), "dubletten": []}
        else:
            out = {"fehlt": _fehlt(werte), "formfehler": list(_formfehler(werte)), "dubletten": []}
        for k, v in self.regeln_extra.get(z["vorgangsnummer"], {}).items():
            out[k] = list(out.get(k, [])) + list(v)
        return out

    def _ausgabe(self, z: dict) -> dict:
        return {**{k: v for k, v in z.items()}, "felder": {k: dict(v) for k, v in z["felder"].items()},
                "regeln": self._regeln(z)}

    # ---- REST -----------------------------------------------------------------------------------------------------
    def request(self, method: str, url: str, params: dict | None = None, json: dict | None = None, **_kw) -> Antwort:
        pfad = urlsplit(url).path
        if NS not in pfad:
            return _fehler("rest_no_route", 404)
        route = pfad.split(NS, 1)[1]
        self.aufrufe.append((method, route))
        if method == "POST":
            self.koerper.append((method, route, dict(json or {})))
        if self.netzfehler:
            raise requests.ConnectionError("Verbindung abgelehnt (Fake)")
        if not self.funktion_an:
            return _fehler("tamil_funktion_aus", 503)
        teile = route.split("/")
        p = params or {}
        if method == "GET" and route in ("einsendungen", "eintraege"):
            nach, anzahl = int(p.get("nach", 0)), max(1, min(100, int(p.get("anzahl", 50))))
            if route == "einsendungen":
                seite = [z for z in self.einsendungen if z["id"] > nach][:anzahl]
                return Antwort(200, {"einsendungen": [self._ausgabe(z) for z in seite],
                                     "naechster": seite[-1]["id"] if seite else nach})
            ids = sorted(i for i in self.eintraege if i > nach)[:anzahl]
            return Antwort(200, {"eintraege": [self.eintrag_ausgabe(i) for i in ids], "naechster": ids[-1] if ids else nach})
        if teile[0] == "einsendung" and len(teile) >= 2:
            z = self.einsendung(teile[1])
            if z is None:
                return _fehler("tamil_vz_einsendung_fehlt", 404)
            if method == "GET" and len(teile) == 2:
                return Antwort(200, self._ausgabe(z))
            if method == "POST" and teile[2:] == ["status"]:
                return self._status(z, (json or {}).get("status", ""), (json or {}).get("pruefung"))
        if teile[0] == "eintrag":
            if method == "GET" and len(teile) == 2 and teile[1].isdigit():
                if int(teile[1]) not in self.eintraege:
                    return _fehler("tamil_vz_eintrag_fehlt", 404)
                return Antwort(200, self.eintrag_ausgabe(int(teile[1])))
            j = json or {}
            if method == "POST" and len(teile) == 1:
                return self._freigabe("anlegen", j.get("einsendung", ""), 0, j.get("felder") or {}, "")
            if method == "POST" and len(teile) == 2 and teile[1].isdigit():
                return self._freigabe("aendern", j.get("einsendung", ""), int(teile[1]), j.get("felder") or {},
                                      str(j.get("stand", "")))
            if method == "POST" and len(teile) == 3 and teile[2] == "entfernen":
                return self._freigabe("entfernen", j.get("einsendung", ""), int(teile[1]), {}, str(j.get("stand", "")))
        return _fehler("rest_no_route", 404)

    def _status(self, z: dict, status: str, pruefung: Any) -> Antwort:
        if status not in ("geprueft", "abgelehnt"):
            return _fehler("tamil_vz_status", 400)
        if z["status"] not in ("neu", "geprueft"):
            return _fehler("tamil_vz_status_konflikt", 409)
        z["status"] = status
        if status == "abgelehnt":
            z["abgeschlossen"] = _jetzt()
        if isinstance(pruefung, dict):
            z["pruefung"] = pruefung
        return Antwort(200, self._ausgabe(z))

    def _freigabe(self, aktion: str, vorgang: str, eid: int, felder: dict, stand: str) -> Antwort:
        typ = {"anlegen": "neu", "aendern": "aenderung", "entfernen": "entfernen"}[aktion]
        z = self.einsendung(vorgang)
        if z is None:
            return _fehler("tamil_vz_einsendung_fehlt", 404)
        if z["typ"] != typ or (aktion != "anlegen" and z["eintrag_id"] != eid):
            return _fehler("tamil_vz_falsche_einsendung", 409)
        if z["status"] == "freigegeben":
            return Antwort(200, {"bereits": True, "eintrag": self.eintrag_ausgabe(z["eintrag_id"]),
                                 "einsendung": self._ausgabe(z)})
        if z["status"] == "abgelehnt":
            return _fehler("tamil_vz_abgelehnt", 409)
        unbekannt = [k for k in felder if k not in FELDER]
        if "premium" in unbekannt:
            return _fehler("tamil_vz_premium_verboten", 403)
        if unbekannt:
            return _fehler("tamil_vz_unbekannte_felder", 400, felder=unbekannt)
        if aktion == "entfernen" and felder:
            return _fehler("tamil_vz_unbekannte_felder", 400)
        fremd = [k for k in felder if k not in z["felder"] and k != "kategorie"]
        if fremd:
            return _fehler("tamil_vz_nicht_eingesandt", 400, felder=fremd)
        alt: dict = {}
        if aktion != "anlegen":
            if eid not in self.eintraege:
                return _fehler("tamil_vz_eintrag_fehlt", 404)
            alt = dict(self.eintraege[eid]["felder"])
        werte = {k: str(v).strip() for k, v in felder.items()}
        fehler = _formfehler(werte, alt.get("land", ""))
        if fehler:
            return _fehler("tamil_vz_ungueltig", 400, fehler=fehler)
        gesamt = {**alt, **werte}
        if aktion != "entfernen":
            if _fehlt(gesamt):
                return _fehler("tamil_vz_unvollstaendig", 400, fehlt=_fehlt(gesamt))
            # wie `$abhaengig` im PHP: bei Teiländerungen abhängige Felder über alt + neu gegeneinander prüfen
            if any(k in werte for k in ABHAENGIG):
                ganz = _formfehler({k: gesamt[k] for k in ABHAENGIG if k in gesamt})
                if ganz:
                    return _fehler("tamil_vz_ungueltig", 400, fehler=ganz)
            for k, f in z["felder"].items():
                if werte.get(k) and not f["oeffentlich"] and k in WAHL:
                    return _fehler("tamil_vz_nicht_oeffentlich", 409, feld=k)
        if aktion != "anlegen" and stand != self.stand(eid):
            return _fehler("tamil_vz_stand", 409, stand=self.stand(eid))
        z["status"], z["abgeschlossen"] = "freigegeben", _jetzt()
        if aktion == "anlegen":
            eid = self.eintrag_anlegen(gesamt)
            self.eintraege[eid]["vorgang"] = vorgang
        elif aktion == "aendern":
            self.eintraege[eid]["felder"].update(werte)
        else:
            self.eintraege[eid]["status"] = "entfernt"
        abweichend = [k for k in werte if k != "kategorie" and z["felder"].get(k, {}).get("wert", "").strip() != werte[k]]
        z["eintrag_id"] = eid
        z["entscheidung"] = {"aktion": aktion, "felder": list(werte), "abweichend": abweichend, "wer": "ki-agent",
                             "zeit": _jetzt()}
        if vorgang in self.abbruch_nach_senden:
            self.abbruch_nach_senden.discard(vorgang)
            raise requests.ConnectionError("Verbindung nach dem Senden abgebrochen (Fake)")
        return Antwort(201 if aktion == "anlegen" else 200,
                       {"bereits": False, "eintrag": self.eintrag_ausgabe(eid), "einsendung": self._ausgabe(z)})


__all__ = ["FakeWordPressVerzeichnis"]
