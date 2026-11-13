"""Austauschbarer Weg zu Meta (Spezifikation integrationen.md §8 und §9).

  TrockenTransport  Standard: ruft nie etwas auf (jeder Aufruf ist ein Programmierfehler). Der Ablauf bereitet alles
                    vor und speichert die vollständige Nutzlast, schickt aber nichts (Status `trocken`).
  GraphTransport    live: offizielle Graph API, fester Host graph.facebook.com, Token nur im Aufruf, nie im Text
                    eines Fehlers oder Protokolls. Nur mit RADAR_SOCIAL_LIVE und allen Schlüsseln (konfig.py).
  social/fake.py    FakeMeta für Tests und Abnahme (nachgestellte Schnittstelle, kein Netz).

Ausnahme zu „Netz nur über net.safe_get“: Meta verlangt POST, und der Host ist fest (keine Adresse von außen), daher
eine eigene Session mit Timeout. Fehlerklassen steuern den Ablauf:

  ZugangFehler   Token ungültig (190), Rechte fehlen (10, 200), als missbräuchlich eingestuft (368) → Kanal pausiert
  WarteFehler    Ratenlimit (4, 17, 32, 613, 80001, 80002) oder Netzfehler vor dem entscheidenden Aufruf → später
  UnklarFehler   Abbruch beim veröffentlichenden Aufruf → Abgleich mit den letzten Beiträgen, nie blind wiederholen
  MetaFehler     alles andere → an einen Menschen
"""

from __future__ import annotations

from typing import Protocol

import requests

ZUGANG_CODES = {190, 10, 200, 368}
WARTE_CODES = {4, 9, 17, 32, 613, 80001, 80002}


class MetaFehler(Exception):
    def __init__(self, code: int, text: str):
        self.code = code
        self.text = text
        super().__init__(f"Meta-Fehler {code}: {text}")


class ZugangFehler(MetaFehler):
    pass


class WarteFehler(MetaFehler):
    pass


class UnklarFehler(Exception):
    """Ob Meta den Beitrag angenommen hat, ist unbekannt (Timeout, Verbindungsabbruch beim Veröffentlichen)."""


class Transport(Protocol):
    live: bool

    def ig_container(self, image_url: str, caption: str, alt_text: str) -> str: ...
    def ig_status(self, container_id: str) -> str: ...
    def ig_limit(self) -> tuple[int, int]: ...
    def ig_veroeffentlichen(self, container_id: str) -> str: ...
    def ig_permalink(self, media_id: str) -> str: ...
    def ig_letzte(self) -> list[dict]: ...
    def fb_foto(self, url: str, caption: str, alt_text: str) -> dict: ...
    def fb_permalink(self, post_id: str) -> str: ...
    def fb_letzte(self) -> list[dict]: ...


class TrockenTransport:
    """Trockenmodus: kein Aufruf nach außen. Der Ablauf fragt `live` und ruft die Methoden gar nicht erst auf."""

    live = False

    def __getattr__(self, name: str):
        if name.startswith(("ig_", "fb_")):
            def nie(*_a, **_kw):
                raise AssertionError(f"Trockenmodus: {name} darf nicht aufgerufen werden")
            return nie
        raise AttributeError(name)


def fehler_aus(status: int, daten: dict) -> MetaFehler:
    err = daten.get("error") if isinstance(daten, dict) else None
    err = err if isinstance(err, dict) else {}
    code = int(err.get("code") or status or 0)
    text = str(err.get("message") or f"HTTP {status}")[:200]
    if code in ZUGANG_CODES or err.get("type") == "OAuthException" and code == 190:
        return ZugangFehler(code, text)
    if code in WARTE_CODES or status == 429:
        return WarteFehler(code, text)
    return MetaFehler(code, text)


class GraphTransport:
    live = True

    def __init__(self, konf, session: requests.Session | None = None, timeout: float = 30):
        self.basis = f"https://graph.facebook.com/{konf.graph_version}"
        self.ig, self.page = konf.ig_user_id, konf.page_id
        self._zugang = konf.zugang
        self.http = session or requests.Session()
        self.http.headers["User-Agent"] = "TamilDE-NewsRadar/1.0"
        self.timeout = timeout

    def _anfrage(self, methode: str, pfad: str, *, daten: dict | None = None, entscheidend: bool = False) -> dict:
        werte = {**(daten or {}), "access_token": self._zugang}
        try:
            if methode == "GET":
                resp = self.http.get(f"{self.basis}/{pfad}", params=werte, timeout=self.timeout)
            else:
                resp = self.http.post(f"{self.basis}/{pfad}", data=werte, timeout=self.timeout)
        except (requests.Timeout, requests.ConnectionError) as exc:
            if entscheidend:
                raise UnklarFehler(f"Verbindung abgebrochen bei {pfad.split('?')[0]}: {type(exc).__name__}") from None
            raise WarteFehler(0, f"Netzfehler: {type(exc).__name__}") from None
        try:
            antwort = resp.json()
        except ValueError:
            antwort = {}
        if resp.status_code >= 400 or (isinstance(antwort, dict) and "error" in antwort):
            if entscheidend and resp.status_code >= 500:
                raise UnklarFehler(f"Meta antwortet {resp.status_code} beim Veröffentlichen")
            raise fehler_aus(resp.status_code, antwort)
        return antwort if isinstance(antwort, dict) else {}

    def ig_container(self, image_url: str, caption: str, alt_text: str) -> str:
        return str(self._anfrage("POST", f"{self.ig}/media",
                                 daten={"image_url": image_url, "caption": caption, "alt_text": alt_text})["id"])

    def ig_status(self, container_id: str) -> str:
        return str(self._anfrage("GET", container_id, daten={"fields": "status_code"}).get("status_code", ""))

    def ig_limit(self) -> tuple[int, int]:
        d = self._anfrage("GET", f"{self.ig}/content_publishing_limit", daten={"fields": "quota_usage,config"})
        eintrag = (d.get("data") or [{}])[0]
        return int(eintrag.get("quota_usage") or 0), int((eintrag.get("config") or {}).get("quota_total") or 100)

    def ig_veroeffentlichen(self, container_id: str) -> str:
        return str(self._anfrage("POST", f"{self.ig}/media_publish", daten={"creation_id": container_id},
                                 entscheidend=True)["id"])

    def ig_permalink(self, media_id: str) -> str:
        return str(self._anfrage("GET", media_id, daten={"fields": "permalink"}).get("permalink", ""))

    def ig_letzte(self) -> list[dict]:
        d = self._anfrage("GET", f"{self.ig}/media", daten={"fields": "id,caption,timestamp,permalink", "limit": 25})
        return list(d.get("data") or [])

    def fb_foto(self, url: str, caption: str, alt_text: str) -> dict:
        d = self._anfrage("POST", f"{self.page}/photos", entscheidend=True,
                          daten={"url": url, "caption": caption, "alt_text_custom": alt_text, "published": "true"})
        return {"id": str(d.get("id", "")), "post_id": str(d.get("post_id") or d.get("id", ""))}

    def fb_permalink(self, post_id: str) -> str:
        return str(self._anfrage("GET", post_id, daten={"fields": "permalink_url"}).get("permalink_url", ""))

    def fb_letzte(self) -> list[dict]:
        d = self._anfrage("GET", f"{self.page}/posts", daten={"fields": "id,message,created_time,permalink_url",
                                                               "limit": 25})
        return list(d.get("data") or [])
