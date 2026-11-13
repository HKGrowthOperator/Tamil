"""Fake-Transport für die Einsendungen-Routen von tamil-radar/v1 (Festlegung F1, integrationen.md §3) – ohne Netz.

Steht anstelle der `requests.Session` im `TamilRadarClient` und verhält sich wie das Plugin: Cursor-Liste aufsteigend
nach `id`, eine Einsendung, Status setzen mit den Übergängen der Website (Abschluss endgültig, 409 bei einem anderen
Abschluss), Bild als Base64, 503 bei ausgeschaltetem Funktionsschalter. Für Tests und die Abnahme; alle Personendaten
sind erfunden (example.test).
"""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import requests

NS = "/wp-json/tamil-radar/v1/"
OFFEN = ("eingegangen", "abgeholt")
UEBERGAENGE = {"abgeholt": ("eingegangen",), "uebernommen": OFFEN, "erledigt": OFFEN, "abgelehnt": OFFEN, "spam": OFFEN}
_ZEICHEN = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class Antwort:
    def __init__(self, status_code: int, daten: Any):
        self.status_code = status_code
        self._daten = daten
        self.text = json.dumps(daten, ensure_ascii=False)
        self.headers = {"Content-Type": "application/json"}

    def json(self) -> Any:
        return self._daten


def _jetzt() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fehler(code: str, status: int, **daten) -> Antwort:
    return Antwort(status, {"code": code, "message": code, "data": {"status": status, **daten}})


class FakeWordPressEingang:
    """Session-Ersatz: `request(method, url, **kw)` wie requests. `aufrufe` zeichnet (Methode, Pfad) auf."""

    def __init__(self, *, funktion_an: bool = True):
        self.auth = None
        self.headers: dict[str, str] = {}
        self.funktion_an = funktion_an
        self.zeilen: list[dict] = []
        self.bilder: dict[str, bytes] = {}
        self.aufrufe: list[tuple[str, str]] = []
        self.abbruch_nach_senden: set[str] = set()  # Vorgang: Status wird gesetzt, dann bricht die Verbindung ab
        self.netzfehler = False  # jeder Aufruf scheitert, bevor er WordPress erreicht

    # ---- Website-Seite (was das Formular anlegt) ---------------------------------------------------------------
    def einreichen(self, art: str, felder: dict, *, name: str = "Erika Beispiel", email: str = "erika@example.test",
                   telefon: str = "", einwilligung: bool = True, bild: bytes | None = None, bild_typ: str = "image/png",
                   bild_recht: bool = True, eingang_at: str | None = None) -> str:
        n = len(self.zeilen) + 1
        vorgang = "T261113-" + "".join(_ZEICHEN[(n * 7 + i * 3) % len(_ZEICHEN)] for i in range(5))
        self.zeilen.append({
            "id": n, "vorgangsnummer": vorgang, "art": art, "status": "eingegangen", "eingang_at": eingang_at or _jetzt(),
            "abgeholt_at": None, "abgeschlossen_at": None, "name": name, "email": email, "telefon": telefon,
            "einwilligung": einwilligung, "einwilligung_fassung": "KBS-Entwurf 1", "felder": dict(felder),
            "bild": None if bild is None else {"typ": bild_typ, "groesse": len(bild),
                                               "sha256": hashlib.sha256(bild).hexdigest(), "recht_bestaetigt": bild_recht},
        })
        if bild is not None:
            self.bilder[vorgang] = bild
        return vorgang

    def zeile(self, vorgang: str) -> dict | None:
        return next((z for z in self.zeilen if z["vorgangsnummer"] == vorgang), None)

    # ---- REST ---------------------------------------------------------------------------------------------------
    def request(self, method: str, url: str, params: dict | None = None, json: dict | None = None, **_kw) -> Antwort:
        pfad = urlsplit(url).path
        if NS not in pfad:
            return _fehler("rest_no_route", 404)
        route = pfad.split(NS, 1)[1]
        self.aufrufe.append((method, route))
        if self.netzfehler:
            raise requests.ConnectionError("Verbindung abgelehnt (Fake)")
        if not self.funktion_an:
            return _fehler("tamil_funktion_aus", 503)
        teile = route.split("/")
        if method == "GET" and route == "einsendungen":
            nach, anzahl = int((params or {}).get("nach", 0)), max(1, min(100, int((params or {}).get("anzahl", 50))))
            neu = [z for z in self.zeilen if z["id"] > nach]
            seite = neu[:anzahl]
            return Antwort(200, {"einsendungen": [dict(z) for z in seite], "weiter": seite[-1]["id"] if seite else nach,
                                 "mehr": len(neu) > anzahl})
        if len(teile) >= 2 and teile[0] == "einsendung":
            z = self.zeile(teile[1])
            if z is None:
                return _fehler("tamil_einsendung_fehlt", 404)
            if method == "GET" and len(teile) == 2:
                return Antwort(200, dict(z))
            if method == "GET" and teile[2:] == ["bild"]:
                daten = self.bilder.get(z["vorgangsnummer"])
                if daten is None:
                    return _fehler("tamil_einsendung_ohne_bild", 404)
                return Antwort(200, {"vorgangsnummer": z["vorgangsnummer"], "typ": z["bild"]["typ"], "groesse": len(daten),
                                     "sha256": hashlib.sha256(daten).hexdigest(),
                                     "daten_base64": base64.b64encode(daten).decode()})
            if method == "POST" and teile[2:] == ["status"]:
                return self._status(z, (json or {}).get("status", ""))
        return _fehler("rest_no_route", 404)

    def _status(self, z: dict, neu: str) -> Antwort:
        if neu not in UEBERGAENGE:
            return _fehler("tamil_einsendung_status", 400)
        if z["status"] in UEBERGAENGE[neu]:
            z["status"] = neu
            z["abgeholt_at" if neu == "abgeholt" else "abgeschlossen_at"] = _jetzt()
            if z["vorgangsnummer"] in self.abbruch_nach_senden:
                self.abbruch_nach_senden.discard(z["vorgangsnummer"])
                raise requests.ConnectionError("Verbindung nach dem Senden abgebrochen (Fake)")
            return Antwort(200, dict(z))
        if z["status"] == neu or (neu == "abgeholt" and z["status"] != "eingegangen"):
            return Antwort(200, dict(z))
        return _fehler("tamil_einsendung_abgeschlossen", 409, aktuell=z["status"], angefordert=neu)


__all__ = ["FakeWordPressEingang", "Antwort"]
