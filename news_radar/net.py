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

import requests

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


def check_url(url: str, resolve: Resolver | None = None) -> str:
    """Prüft eine URL und gibt sie zurück; UnsafeURL, wenn sie gesperrt ist."""
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        raise UnsafeURL(f"Schema nicht erlaubt: {parts.scheme or '(leer)'}")
    if parts.username or parts.password:
        raise UnsafeURL("Zugangsdaten in der URL")
    host = parts.hostname or ""
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
        resp = http.get(current, params=params, headers=hdrs, timeout=timeout, stream=True, allow_redirects=False)
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
