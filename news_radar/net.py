"""Sichere HTTP-Abrufe für alles, was der Radar aus dem Netz holt (Quellen, Artikeltexte, Bilder, Recherche).

- nur http/https, keine Zugangsdaten in der URL
- jede Adresse wird aufgelöst; private, Loopback-, Link-local-, reservierte und Multicast-Adressen sind gesperrt
  (Schutz vor SSRF: ein Feed-Link auf http://169.254.169.254/ oder 127.0.0.1 erreicht nie den Server selbst)
- Weiterleitungen folgen wir von Hand (höchstens 5), jedes Ziel wird erneut geprüft
- Größen- und Content-Type-Grenze; die Antwort wird gestreamt und bricht beim Limit ab
- bedingte Abrufe mit ETag/Last-Modified (304 = unverändert)
"""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urljoin, urlsplit

import idna
import requests
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool

USER_AGENT = "TamilDE-NewsRadar/2.0 (+https://www.tamil.de)"
MAX_BYTES = 5_000_000
MAX_REDIRECTS = 5
TEXT_TYPES = ("text/", "application/xml", "application/rss", "application/atom", "application/json",
              "application/ld+json", "application/xhtml")
IMAGE_TYPES = ("image/",)

Resolver = Callable[[str], list[str]]


class UnsafeURL(ValueError):
    """Die Adresse ist für den Radar gesperrt (Schema, Zugangsdaten oder interne Adresse)."""


class ResponseTooLarge(ValueError):
    """Die Antwort überschreitet das Größenlimit."""


class WrongContentType(ValueError):
    """Der Server liefert etwas anderes als erwartet (z. B. HTML statt Bild)."""


def _resolve(host: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise UnsafeURL(f"Host nicht auflösbar: {host}") from exc
    return sorted({info[4][0] for info in infos})


def _blocked(address: str) -> bool:
    ip = ipaddress.ip_address(address.split("%", 1)[0])
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return not ip.is_global or ip.is_multicast or ip.is_reserved or ip.is_loopback or ip.is_link_local


def _ascii_host(host: str) -> str:
    """Hostname so kodieren, wie requests/urllib3 es tun (IDNA/UTS46) – sonst prüfen wir einen anderen Host als den,
    zu dem verbunden wird (z. B. „evilß.com“: IDNA2003 → evilss.com, UTS46 → xn--evil-yna.com)."""
    if host.isascii():
        return host
    try:
        return idna.encode(host, uts46=True).decode("ascii")
    except idna.IDNAError as exc:
        raise UnsafeURL(f"Ungültiger Hostname: {host}") from exc


def check_url(url: str, resolve: Resolver | None = None) -> str:
    """Prüft eine URL und gibt sie zurück; UnsafeURL, wenn sie gesperrt ist."""
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        raise UnsafeURL(f"Schema nicht erlaubt: {parts.scheme or '(leer)'}")
    if parts.username or parts.password:
        raise UnsafeURL("Zugangsdaten in der URL")
    host = _ascii_host(parts.hostname or "")
    if not host:
        raise UnsafeURL("Kein Host")
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    addresses = [str(literal)] if literal else (resolve or _resolve)(host)
    if not addresses:
        raise UnsafeURL(f"Host ohne Adresse: {host}")
    bad = [a for a in addresses if _blocked(a)]
    if bad:
        raise UnsafeURL(f"Interne Adresse gesperrt: {host} → {bad[0]}")
    return url


# ---- Prüfung beim Verbindungsaufbau (gegen DNS-Rebinding) ---------------------------------------------
# check_url löst den Host vorher auf; requests löst ihn beim Verbinden noch einmal auf. Ein Angreifer-DNS mit TTL 0
# könnte beim zweiten Mal eine interne Adresse liefern. Deshalb prüfen diese Verbindungsklassen die Gegenstelle des
# tatsächlich geöffneten Sockets. Über einen Proxy (Entwicklungsumgebung) verbindet requests zum Proxy; dort greift
# nur die Vorabprüfung.

class _PeerCheck:
    def _new_conn(self):  # type: ignore[override]
        sock = super()._new_conn()  # type: ignore[misc]
        try:
            peer = sock.getpeername()[0]
        except OSError:
            peer = ""
        if peer and _blocked(peer):
            sock.close()
            raise UnsafeURL(f"Verbindung zu interner Adresse gesperrt: {peer}")
        return sock


class _SafeHTTPConnection(_PeerCheck, HTTPConnection):
    pass


class _SafeHTTPSConnection(_PeerCheck, HTTPSConnection):
    pass


class _SafeHTTPPool(HTTPConnectionPool):
    ConnectionCls = _SafeHTTPConnection


class _SafeHTTPSPool(HTTPSConnectionPool):
    ConnectionCls = _SafeHTTPSConnection


class SafeAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        super().init_poolmanager(*args, **kwargs)
        self.poolmanager.pool_classes_by_scheme = {"http": _SafeHTTPPool, "https": _SafeHTTPSPool}


_SAFE_SESSION: requests.Session | None = None


def _safe_session() -> requests.Session:
    global _SAFE_SESSION
    if _SAFE_SESSION is None:
        s = requests.Session()
        s.mount("http://", SafeAdapter())
        s.mount("https://", SafeAdapter())
        _SAFE_SESSION = s
    return _SAFE_SESSION


def _ohne_proxy(url: str) -> bool:
    """True, wenn requests für diese URL direkt verbindet (kein HTTP(S)-Proxy oder Host in NO_PROXY)."""
    if requests.utils.should_bypass_proxies(url, no_proxy=None):
        return True
    return requests.utils.select_proxy(url, requests.utils.get_environ_proxies(url)) is None


@dataclass
class Fetched:
    url: str  # nach Weiterleitungen
    status: int
    content: bytes
    content_type: str
    etag: str = ""
    last_modified: str = ""

    @property
    def not_modified(self) -> bool:
        return self.status == 304

    def json(self):
        import json

        return json.loads(self.content.decode("utf-8", errors="replace") or "null")

    @property
    def text(self) -> str:
        charset = "utf-8"
        for part in self.content_type.split(";")[1:]:
            key, _, value = part.strip().partition("=")
            if key.lower() == "charset" and value:
                charset = value.strip('"')
        try:
            return self.content.decode(charset, errors="replace")
        except LookupError:
            return self.content.decode("utf-8", errors="replace")


class HTTPError(requests.HTTPError):
    def __init__(self, status: int, url: str):
        super().__init__(f"HTTP {status} für {url}")
        self.status = status
        self.url = url


def safe_get(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float = 12,
    max_bytes: int = MAX_BYTES,
    accept: tuple[str, ...] | None = None,
    etag: str = "",
    last_modified: str = "",
    session: requests.Session | None = None,
    resolve: Resolver | None = None,
    max_redirects: int = MAX_REDIRECTS,
) -> Fetched:
    """GET mit SSRF-Schutz, Weiterleitungen von Hand, Größenlimit und optionalem bedingtem Abruf.

    HTTP-Fehler (4xx/5xx) werfen HTTPError mit `.status`; 304 liefert Fetched(status=304, content=b"").
    """
    http = session or requests
    hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
    if etag:
        hdrs["If-None-Match"] = etag
    if last_modified:
        hdrs["If-Modified-Since"] = last_modified
    current = url
    for _hop in range(max_redirects + 1):
        check_url(current, resolve)
        client = http if session is not None or not _ohne_proxy(current) else _safe_session()
        resp = client.get(current, params=params, headers=hdrs, timeout=timeout, stream=True, allow_redirects=False)
        params = None  # Parameter gehören nur zur ersten Anfrage
        try:
            if resp.status_code in (301, 302, 303, 307, 308) and resp.headers.get("Location"):
                current = urljoin(current, resp.headers["Location"])
                continue
            ctype = resp.headers.get("Content-Type", "")
            meta = dict(url=current, content_type=ctype, etag=resp.headers.get("ETag", ""),
                        last_modified=resp.headers.get("Last-Modified", ""))
            if resp.status_code == 304:
                return Fetched(status=304, content=b"", **meta)
            if resp.status_code >= 400:
                raise HTTPError(resp.status_code, current)
            if accept and ctype and not ctype.lower().startswith(accept):
                raise WrongContentType(f"{ctype} statt {'/'.join(accept)}: {current}")
            declared = resp.headers.get("Content-Length", "")
            if declared.isdigit() and int(declared) > max_bytes:
                raise ResponseTooLarge(f"{declared} Bytes > {max_bytes}: {current}")
            chunks, size = [], 0
            for chunk in resp.iter_content(64 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise ResponseTooLarge(f"mehr als {max_bytes} Bytes: {current}")
                chunks.append(chunk)
            return Fetched(status=resp.status_code, content=b"".join(chunks), **meta)
        finally:
            resp.close()
    raise UnsafeURL(f"Zu viele Weiterleitungen (>{max_redirects}): {url}")


def safe_get_text(url: str, **kw) -> str:
    kw.setdefault("accept", TEXT_TYPES)
    return safe_get(url, **kw).text
