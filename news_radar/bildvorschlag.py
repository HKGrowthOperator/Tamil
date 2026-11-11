"""Bild mit Nachweis: ein Agent schlägt für einen wartenden Entwurf ein echtes Bild vor; der Radar prüft Herkunft und
Rechte selbst, holt das Bild, legt den Lizenz-Datensatz an und setzt Bild, Nachweis und Herkunft am Entwurf.

  POST /api/agent/bild?von=<name>  (Bearer RADAR_AGENT_TOKEN)   ·   python -m news_radar agent bild --datei b.json

Eingabe: {"bilder": [{story_id, weg: "commons" | "quelle", seite_url, bild_url?, alt?}]} (Web höchstens 5, CLI 100).

- commons: seite_url ist eine Dateiseite auf commons.wikimedia.org. Lizenz, Urheber, Dateityp und Größe liest der
  Radar selbst aus der Commons-API; erlaubt sind nur gemeinfrei/CC0, CC BY und CC BY-SA (feste Positivliste).
- quelle: seite_url ist ein Dokument genau dieser Story auf einem Host aus dem Bildquellen-Register
  ([[bildquellen]] in sources.toml). Das Bild muss auf der abgerufenen Seite stehen und unter dem eingetragenen Host
  (oder einem Host aus `bild_hosts` des Eintrags) liegen; der Nachweis kommt aus dem
  Register, nie aus dem Vorschlag. Soziale Netzwerke und Bildagenturen sind fest gesperrt, Agenturbilder werden am
  Umfeld erkannt und abgelehnt.

Entscheidung vom 11.11.2026 (docs/entscheidungen.md): keine Agenturfotos, keine KI-Bilder, nichts aus sozialen
Netzwerken. Die Freigabe bleibt beim Menschen im Cockpit; dort stehen Bild, Nachweis und Lizenz vor der Freigabe.
Ergebnis je Eintrag: gesetzt · abgelehnt · nicht_bearbeitet (Zeitlimit oder Stopp).
"""

from __future__ import annotations

import hashlib
import io
import logging
import re
import sqlite3
import time
import unicodedata
from html import unescape
from typing import Callable
from urllib.parse import unquote, urlencode, urljoin, urlsplit

from PIL import Image, ImageOps

from . import images, net, schalter
from .config import BILD_GESPERRT, BILD_GESPERRT_MARKEN, Bildquelle, Settings, bild_host_gesperrt
from .images import SIZE, FeaturedImage
from .store import OPEN_STATES, Store, now_iso
from .workflow import repo

MAX_BILDER = 100  # CLI je Aufruf
WEB_MAX_BILDER = 5
WEB_FRIST_GESAMT = 90.0
FRIST_ABRUF = 20.0
MAX_BYTES = 8_000_000
MAX_PIXEL = 40_000_000
URHEBER_MAX = 80
MIN_BREITE = 800
MIN_KANTE = 400
VERHAELTNIS = (0.5, 2.4)
ALT_MAX = 160
WEGE = ("commons", "quelle")
UMFANG = "Online-Veröffentlichung auf tamil.de; Zuschnitt auf das Seitenformat"
FORMATE = {"JPEG", "PNG", "WEBP"}
COMMONS_MIME = ("image/jpeg", "image/png", "image/webp")
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
COMMONS_BILDHOST = "upload.wikimedia.org"

# Fest gesperrt (soziale Netzwerke, Bildagenturen): Liste und Prüfung in config, damit schon das Register sie ablehnt
GESPERRT = BILD_GESPERRT
GESPERRT_MARKEN = BILD_GESPERRT_MARKEN

AGENTUR = re.compile(
    r"(?<![a-z0-9])(dpa|keystone|sda|getty|gettyimages|reuters|afp|ap[ _-]?photo|imago|picture[ _-]?alliance|"
    r"shutterstock|adobe[ _-]?stock|istock|istockphoto|epa|ddp|freshfocus|alamy|unsplash|pexels|"
    r"pti|ani|ians|apa|xinhua|aap|anadolu|efe|kyodo|sipa|abaca|laif|westend61|action[ _-]?press|eibner|"
    r"sven[ _-]?simon)(?![a-z0-9])", re.I)
# „AP“ allein ist zu kurz für ein freies Wort: nur in Nachweis-Mustern („Foto: AP“, „© AP“, „AP/…“)
AGENTUR_AP = re.compile(r"(?:(?<![a-z0-9])(?:foto|photo|bild|quelle)|©)\s*:?\s*ap(?![a-z0-9])|(?<![a-z0-9])ap\s*/",
                        re.I)


def agentur(text: str) -> str:
    """Erster Agenturbegriff im Text (leer, wenn keiner)."""
    m = AGENTUR.search(text or "") or AGENTUR_AP.search(text or "")
    return m.group(1) if m and m.re is AGENTUR else ("AP" if m else "")

# Lizenzprüfung Commons: maßgeblich ist die Lizenz-Adresse (exakte Pfade bei creativecommons.org); der Kurzname muss
# dazu passen und darf kein „nc“, „nd“ oder „fair“ enthalten. Ohne Lizenz-Adresse wird alles abgelehnt.
_LIZENZ_PFADE = (
    (re.compile(r"/licenses/by/(\d\.\d)(?:/[a-z]{2})?"), "cc-by"),
    (re.compile(r"/licenses/by-sa/(\d\.\d)(?:/[a-z]{2})?"), "cc-by-sa"),
    (re.compile(r"/publicdomain/zero/(1\.0)"), "cc0"),
    (re.compile(r"/publicdomain/mark/(1\.0)"), "pdm"),
)
_KURZ = {  # normalisierter Kurzname (klein, „-“/„_“ → „ “) je Lizenzart; Version und Land optional
    "cc-by": re.compile(r"cc by(?: (\d\.\d))?(?: [a-z]{2})?"),
    "cc-by-sa": re.compile(r"cc by sa(?: (\d\.\d))?(?: [a-z]{2})?"),
    "cc0": re.compile(r"cc0(?: (1\.0))?|cc zero"),
    "pdm": re.compile(r"public domain(?: mark)?(?: (1\.0))?"),
}
# Gemeinfrei nur mit Lizenz-Adresse (publicdomain/zero/1.0 oder publicdomain/mark/1.0): Commons liefert bei fast
# allen PD-Vorlagen (PD-old, PD-US-expired, PD-textlogo …) nur den Kurznamen „Public domain“ ohne Adresse; ob die
# Gemeinfreiheit für eine Nutzung in DACH gilt, lässt sich daraus nicht unterscheiden. Deshalb ohne Adresse: abgelehnt.
_VERBOTEN = re.compile(r"(?<![a-z])(?:nc|nd)(?![a-z])|fair")


def _lizenz_norm(kurzname: str) -> str:
    return " ".join(_text(kurzname).lower().replace("_", " ").replace("-", " ").split())


class Abgelehnt(ValueError):
    pass


class Zeitlimit(Exception):
    """Die Gesamtfrist des Aufrufs ist abgelaufen."""


class NichtBearbeitet(Exception):
    """Der Eintrag konnte gerade nicht gesetzt werden (z. B. Datenbank belegt); er kann erneut gesendet werden."""


def standard_abruf(url: str, *, frist: float | None = None, bild: bool = False) -> net.Fetched:
    """Abruf über net.safe_get (SSRF-Schutz, Umleitungen geprüft, Größenlimit)."""
    if bild:
        return net.safe_get(url, accept=net.IMAGE_TYPES, timeout=10, max_bytes=MAX_BYTES, frist=frist)
    return net.safe_get(url, accept=net.TEXT_TYPES, timeout=8, max_bytes=3_000_000, frist=frist)


# ---- Hilfen -------------------------------------------------------------------------------------------

def _host(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def adress_hash(url: str) -> str:
    """Kurzer Hash einer Adresse fürs Protokoll (Dateinamen enthalten oft Personennamen)."""
    return hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:10]


def _unter(host: str, basis: str) -> bool:
    return host == basis or host.endswith("." + basis)


def gesperrt(host: str) -> bool:
    return bild_host_gesperrt(host)


def _text(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]*>", " ", html or "")).split())


def _gleich(a: str, b: str) -> bool:
    """Bildadressen vergleichen: Schema, Host ohne www., Pfad und Abfrage; das Fragment zählt nicht."""
    pa, pb = urlsplit(a.strip()), urlsplit(b.strip())

    def ort(p) -> str:  # vollständige Adresse (netloc mit Port und Benutzerteil), nur www. und Groß/klein egal
        return p.netloc.lower().removeprefix("www.")

    return (pa.scheme.lower(), ort(pa), pa.path, pa.query) == (pb.scheme.lower(), ort(pb), pb.path, pb.query)


def _intern_pruefen(url: str) -> None:
    try:
        net.check_url(url)
    except net.UnsafeURL as exc:
        grund = "interne Adresse" if "Interne Adresse" in str(exc) else "Adresse gesperrt"
        raise Abgelehnt(f"{grund}: {url[:80]}") from None


def _alt(raw) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise Abgelehnt("alt: Text erwartet")
    alt = _text(raw)
    alt = "".join(c for c in alt if c.isprintable())
    if len(alt) > ALT_MAX:
        raise Abgelehnt(f"alt: höchstens {ALT_MAX} Zeichen")
    return alt or None


def _abrufen(store: Store, abruf: Callable, url: str, *, bild: bool, uhr, ende, frist_abruf: float,
             zaehler: list[int] | None = None) -> net.Fetched:
    jetzt = uhr()
    if ende is not None and jetzt >= ende:
        raise Zeitlimit
    schalter.pruefen(store, "redaktion")  # unmittelbar vor dem Abruf nach außen
    frist = time.monotonic() + frist_abruf
    if ende is not None:
        frist = min(frist, time.monotonic() + max(0.0, ende - jetzt))
    if zaehler is not None:
        zaehler[0] += 1
    try:
        return abruf(url, frist=frist, bild=bild)
    except net.Zeitlimit:
        raise Zeitlimit from None
    except net.UnsafeURL as exc:
        raise Abgelehnt(f"Adresse gesperrt: {url[:80]} ({exc})"[:200]) from None
    except net.ResponseTooLarge:
        raise Abgelehnt(f"Bild größer als {MAX_BYTES // 1_000_000} MB") from None
    except net.WrongContentType:
        raise Abgelehnt(f"falscher Dateityp: {url[:80]}") from None
    except Exception as exc:  # noqa: BLE001 – Netzfehler lehnen den Eintrag ab, nicht den Stapel
        raise Abgelehnt(f"nicht abrufbar ({type(exc).__name__}): {url[:80]}") from None


def _bild_lesen(daten: bytes, *, streng: bool) -> Image.Image:
    """Datei prüfen: JPEG, PNG oder WebP, Breite ≥ 800; streng (Quelle): kürzere Kante ≥ 400, Verhältnis 0,5–2,4.
    Abmessungen werden vor dem Dekodieren geprüft (höchstens MAX_PIXEL, gegen Dekompressionsbomben); JPEGs werden per
    draft() schon beim Dekodieren verkleinert, alles andere vor dem Zuschnitt per thumbnail()."""
    if len(daten) > MAX_BYTES:
        raise Abgelehnt(f"Bild größer als {MAX_BYTES // 1_000_000} MB")
    try:
        img = Image.open(io.BytesIO(daten), formats=sorted(FORMATE))
    except Image.DecompressionBombError:
        raise Abgelehnt("Bild zu groß (zu viele Pixel)") from None
    except (OSError, ValueError):
        raise Abgelehnt("Dateityp nicht erlaubt oder Bild nicht lesbar (nur JPEG, PNG, WebP)") from None
    breite, hoehe = img.size
    if breite * hoehe > MAX_PIXEL:
        raise Abgelehnt(f"Bild zu groß ({breite}×{hoehe} Pixel, höchstens {MAX_PIXEL // 1_000_000} Mio.)")
    try:
        if img.getexif().get(0x0112) in (5, 6, 7, 8):  # EXIF-Drehung um 90°: Breite und Höhe tauschen
            breite, hoehe = hoehe, breite
    except (OSError, ValueError):
        pass
    if breite < MIN_BREITE:
        raise Abgelehnt(f"Bild zu klein ({breite} Pixel breit, mindestens {MIN_BREITE})")
    if streng:
        if min(breite, hoehe) < MIN_KANTE:
            raise Abgelehnt(f"Bild zu klein (kürzere Kante {min(breite, hoehe)} Pixel, mindestens {MIN_KANTE})")
        if not VERHAELTNIS[0] <= breite / hoehe <= VERHAELTNIS[1]:
            raise Abgelehnt(f"Seitenverhältnis {breite / hoehe:.2f} passt nicht (Logo, Icon oder Banner?)")
    ziel = (SIZE[0] * 2, SIZE[1] * 2)
    try:
        if img.format == "JPEG":
            img.draft("RGB", ziel)
        img.load()
        img = ImageOps.exif_transpose(img)
        img.thumbnail((max(ziel) * 2, max(ziel) * 2), Image.Resampling.LANCZOS)
    except (OSError, ValueError, Image.DecompressionBombError):
        raise Abgelehnt("Bild nicht lesbar") from None
    return img


# ---- Weg „commons“ ------------------------------------------------------------------------------------

def commons_datei(seite_url: str) -> str:
    teile = urlsplit(seite_url.strip())
    m = re.fullmatch(r"/wiki/(?:File|Datei):(.+)", teile.path)
    if teile.scheme != "https" or (teile.hostname or "").lower() != "commons.wikimedia.org" or not m \
            or teile.username or teile.port:
        raise Abgelehnt("seite_url ist keine Commons-Dateiseite (https://commons.wikimedia.org/wiki/File:…)")
    name = unquote(m.group(1)).replace("_", " ").strip()
    if not name or teile.query or teile.fragment or any(c in name for c in "/|#<>[]{}") \
            or not all(c.isprintable() for c in name):
        raise Abgelehnt("seite_url ist keine Commons-Dateiseite (Dateiname fehlt oder enthält |#<>[]{}/Steuerzeichen)")
    return name


def urhebername(roh: str) -> str:
    """Urheber aus Commons (HTML): erst Entitäten zurückwandeln, dann Skripte und Tags entfernen. Steuer-, Format- und
    Bidi-Zeichen oder mehr als 80 Zeichen → abgelehnt (eine gekürzte Namensnennung wäre unvollständig)."""
    t = unescape(roh or "")
    t = re.sub(r"<(script|style)\b.*?</\1\s*>", " ", t, flags=re.I | re.S)
    t = " ".join(re.sub(r"<[^>]*>", " ", t).split())
    if any(unicodedata.category(c) in ("Cc", "Cf", "Cs", "Co", "Cn") or not c.isprintable() for c in t) \
            or "<" in t or ">" in t:
        raise Abgelehnt("Urhebername enthält Steuer- oder Sonderzeichen")
    if len(t) > URHEBER_MAX:
        raise Abgelehnt(f"Urhebername länger als {URHEBER_MAX} Zeichen (Namensnennung nicht vollständig möglich)")
    return t


def commons_api_url(name: str) -> str:
    return COMMONS_API + "?" + urlencode({
        "action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1600", "titles": f"File:{name}"})


def _ext(meta: dict, key: str) -> str:
    wert = meta.get(key)
    if isinstance(wert, dict):
        wert = wert.get("value")
    return str(wert or "").strip()


def commons_lizenz(kurzname: str, lizenz_url: str = "") -> str | None:
    """'gemeinfrei', 'cc-by' oder 'cc-by-sa' – sonst None (abgelehnt). Im Zweifel None."""
    norm = _lizenz_norm(kurzname)
    if not norm or _VERBOTEN.search(norm):
        return None
    url = (lizenz_url or "").strip()
    if not url:
        return None
    teile = urlsplit(url if "://" in url else "https:" + url)
    if teile.scheme not in ("http", "https") or (teile.hostname or "").lower() not in (
            "creativecommons.org", "www.creativecommons.org") or teile.query or teile.port:
        return None
    pfad = teile.path.rstrip("/")
    for rx, art in _LIZENZ_PFADE:
        m = rx.fullmatch(pfad)
        if not m:
            continue
        k = _KURZ[art].fullmatch(norm)
        if not k or (k.group(1) and k.group(1) != m.group(1)):
            return None
        return "gemeinfrei" if art in ("cc0", "pdm") else art
    return None


def _commons(eintrag: dict, abrufen: Callable) -> dict:
    name = commons_datei(eintrag["seite_url"])
    try:
        data = abrufen(commons_api_url(name), bild=False).json()
        query = (data or {}).get("query") or {}
        seiten = list((query.get("pages") or {}).values())
        angefragt = f"File:{name}"
        for n in query.get("normalized") or []:
            if n.get("from") == angefragt:
                angefragt = n.get("to") or angefragt
        if len(seiten) != 1:  # genau die verlinkte Datei, keine zweite über die Abfrage
            raise Abgelehnt("Datei auf Commons nicht gefunden" if not seiten else "Commons liefert mehr als eine Datei")
        if seiten[0].get("title") != angefragt:
            raise Abgelehnt("Commons liefert eine andere Datei als die verlinkte")
        info = (seiten[0].get("imageinfo") or [None])[0]
    except (ValueError, AttributeError, TypeError) as exc:
        if isinstance(exc, Abgelehnt):
            raise
        raise Abgelehnt("Commons-Antwort unlesbar") from None
    if not info:
        raise Abgelehnt("Datei auf Commons nicht gefunden")
    meta = info.get("extmetadata") or {}
    kurzname = _text(_ext(meta, "LicenseShortName"))
    lizenz_url = _ext(meta, "LicenseUrl")
    if _ext(meta, "NonFree").lower() in ("true", "1", "yes"):
        raise Abgelehnt("Lizenz nicht erlaubt (Commons markiert die Datei als NonFree)")
    art = commons_lizenz(kurzname, lizenz_url)
    if art is None and not lizenz_url and re.match(r"public domain|pd|cc0", _lizenz_norm(kurzname)):
        raise Abgelehnt(f"Lizenz nicht erlaubt: Gemeinfreiheit nicht eindeutig ({kurzname} ohne Lizenz-Adresse)")
    if art is None:
        raise Abgelehnt(f"Lizenz nicht erlaubt ({kurzname or 'leer'}; nur gemeinfrei, CC0, CC BY, CC BY-SA)")
    artist = urhebername(_ext(meta, "Artist"))
    if art != "gemeinfrei" and not artist:
        raise Abgelehnt(f"Namensnennung nicht erfüllbar ({kurzname} ohne Urheber)")
    mime = str(info.get("mime") or "").lower()
    if mime not in COMMONS_MIME:
        raise Abgelehnt(f"Dateityp nicht erlaubt ({mime or 'unbekannt'}; nur JPEG, PNG, WebP)")
    if int(info.get("width") or 0) < MIN_BREITE:
        raise Abgelehnt(f"Bild zu klein ({info.get('width')} Pixel breit, mindestens {MIN_BREITE})")
    bild_url = str(info.get("thumburl") or info.get("url") or "")
    if urlsplit(bild_url).scheme != "https" or (urlsplit(bild_url).hostname or "") != COMMONS_BILDHOST:
        raise Abgelehnt("Commons liefert keine Bildadresse auf upload.wikimedia.org")
    if art == "gemeinfrei":
        nachweis = f"Foto: {artist} / Wikimedia Commons, gemeinfrei" if artist else "Foto: Wikimedia Commons, gemeinfrei"
    else:
        nachweis = f"Foto: {artist} / Wikimedia Commons, {kurzname}"
    lizenz = f"{kurzname} ({lizenz_url})" if lizenz_url.startswith(("http://", "https://")) else kurzname
    got = abrufen(bild_url, bild=True)
    if (urlsplit(got.url).hostname or "").lower() != COMMONS_BILDHOST:  # Umleitung weg von Commons
        raise Abgelehnt(f"Bild leitet weg von {COMMONS_BILDHOST} um")
    img = _bild_lesen(got.content, streng=False)
    hinweis = ", ".join(t for t in re.split(r"[|,]\s*", _text(_ext(meta, "Restrictions"))) if t)[:200]
    return {"img": img, "nachweis": nachweis, "lizenz": lizenz, "rechteinhaber": artist or "gemeinfrei",
            "umfang": f"{UMFANG}; Hinweis von Commons: {hinweis}" if hinweis else UMFANG,
            "quelle_url": eintrag["seite_url"].strip(), "bild_url": bild_url}


# ---- Weg „quelle“ -------------------------------------------------------------------------------------

_ATTR = re.compile(r"""([\w:-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""")


def _attrs(tag: str) -> dict[str, str]:
    return {m.group(1).lower(): unescape(m.group(3) if m.group(3) is not None else m.group(4) if m.group(4) is not None
                                         else m.group(5)) for m in _ATTR.finditer(tag)}


def _figcaption(html: str, start: int) -> str:
    auf = html.lower().rfind("<figure", 0, start)
    if auf < 0 or "</figure" in html.lower()[auf:start]:
        return ""
    zu = html.lower().find("</figure", start)
    m = re.search(r"<figcaption[^>]*>(.*?)</figcaption", html[auf:zu if zu > 0 else len(html)], re.I | re.S)
    return _text(m.group(1)) if m else ""


_NACHWEIS_TAG = re.compile(
    r"<(\w+)\b[^>]*?(?:class|id|itemprop|data-[\w-]+)\s*=\s*[\"'][^\"']*"
    r"(?:credit|copyright|caption|bildnachweis|quelle|source)[^\"']*[\"'][^>]*>"
    r"|<(\w+)\b[^>]*?\bdata-(?:credit|copyright|caption|bildnachweis|quelle|source)\b[^>]*>", re.I)


def nachweise_der_seite(html: str) -> list[str]:
    """Bildnachweise der ganzen Seite: alle figcaption, Elemente mit Klassen/Attributen für Nachweis (credit,
    copyright, caption, bildnachweis, quelle, source) samt Attributwerten, meta author/copyright."""
    texte = [_text(m.group(1)) for m in re.finditer(r"<figcaption[^>]*>(.*?)</figcaption", html, re.I | re.S)]
    for m in _NACHWEIS_TAG.finditer(html):
        tag = m.group(1) or m.group(2)
        zu = html.lower().find(f"</{tag.lower()}", m.end())
        inhalt = html[m.end():zu if 0 < zu < m.end() + 500 else m.end() + 500]
        texte.append(" ".join((*_attrs(m.group(0)).values(), _text(inhalt))))
    for m in re.finditer(r"<meta\b[^>]*>", html, re.I):
        a = _attrs(m.group(0))
        if (a.get("name") or "").lower() in ("author", "copyright"):
            texte.append(a.get("content", ""))
    return [t for t in texte if t.strip()]


def _stamm(url: str) -> str:
    """Dateistamm ohne Endung und Größen-Zusätze (feier-800.jpg, feier-1200x675.jpg, feier_scaled.webp → feier)."""
    name = unquote(urlsplit(url).path.rsplit("/", 1)[-1]).lower().rsplit(".", 1)[0]
    vorher = None
    while vorher != name:
        vorher = name
        name = re.sub(r"[-_@](?:\d{2,4}(?:x\d{2,4})?|\d{2,4}w|w\d{2,4}|\dx|small|medium|large|thumb|thumbnail|scaled|"
                      r"full|og|social)$", "", name)
    return name


def _img_adressen(a: dict[str, str]) -> list[str]:
    adressen = [a.get("src", "")] + [t.strip().split(" ")[0] for t in a.get("srcset", "").split(",")]
    return [u.strip() for u in adressen if u.strip()]


def bilder_der_seite(html: str, basis: str) -> tuple[list[tuple[str, str]], str, str]:
    """([(Adresse, Umfeld)], og:image, twitter:image) – Adressen gegen die Seite aufgelöst."""
    kandidaten: list[tuple[str, str]] = []
    for m in re.finditer(r"<img\b[^>]*>", html, re.I):
        a = _attrs(m.group(0))
        umfeld = " ".join((a.get("alt", ""), a.get("title", ""), _figcaption(html, m.start()),
                           _text(html[max(0, m.start() - 300):m.end() + 300])))
        kandidaten += [(urljoin(basis, u), umfeld) for u in _img_adressen(a)]
    og = tw = ""
    for m in re.finditer(r"<meta\b[^>]*>", html, re.I):
        a = _attrs(m.group(0))
        name = (a.get("property") or a.get("name") or "").lower()
        if name in ("og:image", "og:image:url", "og:image:secure_url") and not og and a.get("content", "").strip():
            og = urljoin(basis, a["content"].strip())
        elif name == "twitter:image" and not tw and a.get("content", "").strip():
            tw = urljoin(basis, a["content"].strip())
    meta_alt = " ".join(_attrs(m.group(0)).get("content", "") for m in re.finditer(r"<meta\b[^>]*>", html, re.I)
                        if re.search(r"(?:og|twitter):image:alt", m.group(0), re.I))
    for u in (og, tw):
        if u:
            kandidaten.append((u, meta_alt))
    return kandidaten, og, tw


def _register(settings: Settings, host: str) -> Bildquelle | None:
    treffer = [b for b in settings.bildquellen if _unter(host, b.host)]
    return max(treffer, key=lambda b: len(b.host)) if treffer else None


def _quelle_vorpruefen(store: Store, settings: Settings, eintrag: dict, story_id: int) -> Bildquelle:
    seite_url = eintrag["seite_url"].strip()
    host = _host(seite_url)
    if gesperrt(host):
        raise Abgelehnt(f"Host gesperrt (soziales Netzwerk oder Bildagentur): {host}")
    _intern_pruefen(seite_url)
    if eintrag.get("bild_url"):
        if gesperrt(_host(eintrag["bild_url"])):
            raise Abgelehnt(f"Host gesperrt (soziales Netzwerk oder Bildagentur): {_host(eintrag['bild_url'])}")
        _intern_pruefen(eintrag["bild_url"])
    quelle = _register(settings, host)
    if quelle is None:
        raise Abgelehnt(f"Host nicht im Bildquellen-Register: {host}")
    norm = repo.normalize_url(seite_url)
    if not any(norm in (r["url_norm"], repo.normalize_url(r["url"] or "")) for r in store.db.execute(
            "SELECT url, url_norm FROM source_documents WHERE story_id = ?", (story_id,))):
        raise Abgelehnt("seite_url ist kein Dokument dieser Story")
    return quelle


def _quelle(store: Store, settings: Settings, eintrag: dict, story_id: int, abrufen: Callable) -> dict:
    quelle = _quelle_vorpruefen(store, settings, eintrag, story_id)
    seite = abrufen(eintrag["seite_url"].strip(), bild=False)
    if not _unter(_host(seite.url or eintrag["seite_url"]), quelle.host):  # auch nicht zu einem anderen Registerhost
        raise Abgelehnt(f"Seite wird auf einen anderen Host umgeleitet: {_host(seite.url)} statt {quelle.host}")
    kandidaten, og, tw = bilder_der_seite(seite.text, seite.url or eintrag["seite_url"])
    if eintrag.get("bild_url"):
        bild_url = eintrag["bild_url"].strip()
        if not any(_gleich(bild_url, k) for k, _ in kandidaten):
            raise Abgelehnt("bild_url steht nicht auf der Seite (img, srcset, og:image, twitter:image)")
    else:
        bild_url = og or tw
        if not bild_url:
            raise Abgelehnt("kein Bild auf der Seite (og:image, twitter:image)")
    bild_host = _host(bild_url)
    if gesperrt(bild_host):
        raise Abgelehnt(f"Bild-Host gesperrt (soziales Netzwerk oder Bildagentur): {bild_host}")
    erlaubt = (quelle.host, *quelle.bild_hosts)
    if not any(_unter(bild_host, h) for h in erlaubt):
        raise Abgelehnt(f"Bild liegt nicht beim eingetragenen Host ({bild_host} statt {', '.join(erlaubt)})")
    # Umfeld: Dateiname, das Bild selbst und alle <img> mit gleichem Dateistamm (andere Größen desselben Bildes)
    stamm = _stamm(bild_url)
    gleich = [(k, u) for k, u in kandidaten if _gleich(k, bild_url) or (stamm and _stamm(k) == stamm)]
    umfeld = " ".join([unquote(urlsplit(bild_url).path.rsplit("/", 1)[-1])] + [u for _, u in gleich])
    treffer = agentur(umfeld)
    if treffer:
        raise Abgelehnt(f"Agenturbild ({treffer}) – nur eigenes Material der Quelle")
    seite_agentur = next((agentur(t) for t in nachweise_der_seite(seite.text) if agentur(t)), "")
    if seite_agentur:
        # Agentur-Nachweis irgendwo auf der Seite: nur ein Bild mit eigener, agenturfreier Unterschrift geht durch
        eigene = [_figcaption(seite.text, m.start()) for m in re.finditer(r"<img\b[^>]*>", seite.text, re.I)
                  if any(_gleich(urljoin(seite.url or eintrag["seite_url"], u), k) for k, _ in gleich
                         for u in _img_adressen(_attrs(m.group(0))))]
        if (og and _gleich(bild_url, og)) or not any(c and not agentur(c) for c in eigene):
            raise Abgelehnt(f"Agenturbild nicht ausgeschlossen ({seite_agentur} auf der Seite)")
    _intern_pruefen(bild_url)
    got = abrufen(bild_url, bild=True)
    ziel = _host(got.url or bild_url)  # nach Umleitungen: nie gesperrt, sonst derselbe oder der eingetragene Host
    if gesperrt(ziel) or not any(_unter(ziel, h) for h in erlaubt):
        raise Abgelehnt(f"Bild leitet auf einen anderen Host um: {ziel}")
    img = _bild_lesen(got.content, streng=True)
    # „Bildquelle öffnen“ im Cockpit zeigt auf die Seite, auf der das Bild steht (dort prüft der Mensch die Herkunft)
    if quelle.art in ("kino", "festival"):  # Plakate und Filmbilder gehören dem Verleih bzw. der Produktion
        rechteinhaber = f"Verleih bzw. Produktion (über {quelle.betreiber})"
        lizenz = (f"Werbematerial des Verleihs (Plakat oder Filmbild), über {quelle.betreiber}; redaktionelle Nutzung "
                  "mit Bildnachweis; keine ausdrückliche Lizenz")
    else:
        rechteinhaber = quelle.betreiber
        lizenz = f"Material der Quelle ({quelle.art}), redaktionelle Nutzung mit Bildnachweis; keine ausdrückliche Lizenz"
    return {"img": img, "nachweis": quelle.nachweis, "rechteinhaber": rechteinhaber, "lizenz": lizenz,
            "quelle_url": eintrag["seite_url"].strip(), "bild_url": bild_url}


# ---- Entwurf und Ablauf -------------------------------------------------------------------------------

def _wartender_entwurf(store: Store, story_id: int) -> dict:
    rows = [dict(r) for r in store.db.execute(
        "SELECT id, status, uid, titel, bild_datei FROM drafts WHERE story_id = ? ORDER BY id DESC", (story_id,))]
    offen = [r for r in rows if r["status"] in OPEN_STATES]
    if offen:
        return offen[0]
    if any(r["status"] not in ("abgelehnt",) for r in rows):
        raise Abgelehnt("schon freigegeben (veröffentlichte Beiträge ändert dieser Weg nicht)")
    raise Abgelehnt("kein wartender Entwurf")


def _setzen(store: Store, settings: Settings, entwurf: dict, story_id: int, weg: str, bild: dict,
            alt: str | None, von: str) -> dict:
    data = images._encode(ImageOps.fit(bild["img"].convert("RGB"), SIZE, Image.Resampling.LANCZOS))
    basis = (entwurf.get("bild_datei") or f"{(entwurf.get('uid') or 'bild')[:12]}-{entwurf['id']}.jpg")
    basis = re.sub(r"(?:-e\d+)?-(?:\d+|[0-9a-f]{8})$", "", basis.removesuffix(".jpg"))
    # Entwurfsnummer fest im Namen: zwei Entwürfe teilen nie eine Datei (und nie einen Lizenz-Datensatz)
    stem = f"{basis}-e{entwurf['id']}-{hashlib.sha256(data).hexdigest()[:8]}"
    fi = FeaturedImage(data, f"{stem}.jpg", "image/jpeg", bild["nachweis"], weg)
    name, thumb = images.save_pair(fi, settings.bilder_dir, stem)
    felder = {"bild_datei": name, "bild_credit": bild["nachweis"], "bild_origin": weg}
    if alt is not None:
        felder["bild_alt"] = alt
    sets = ", ".join(f"{k} = ?" for k in felder)
    marks = ",".join("?" for _ in OPEN_STATES)
    alt_datei = entwurf.get("bild_datei")
    # Lizenz-Datensatz und Bild am Entwurf in einer Transaktion; das UPDATE gilt nur, solange der Entwurf noch wartet
    # und noch das Bild trägt, von dem dieser Vorschlag ausging (zwischen Prüfung und hier lagen die Abrufe).
    gesetzt = False
    with store.lock:
        db = store.db
        try:
            if db.in_transaction:
                db.commit()
            db.execute("BEGIN IMMEDIATE")
            asset_id = db.execute(
                "INSERT INTO assets (datei, sha256, herkunft, rechteinhaber, lizenz, umfang, attribution, ablauf, "
                "quelle_url, ki, story_id, draft_id, erstellt) VALUES (?,?,?,?,?,?,?,'',?,0,?,?,?)",
                (name, hashlib.sha256(data).hexdigest(), weg, bild["rechteinhaber"], bild["lizenz"],
                 bild.get("umfang") or UMFANG,
                 bild["nachweis"], bild["quelle_url"], story_id, entwurf["id"], now_iso())).lastrowid
            cur = db.execute(
                f"UPDATE drafts SET {sets}, updated_at = ?, bearbeitet_von = ? "
                f"WHERE id = ? AND status IN ({marks}) AND bild_datei IS ?",
                (*felder.values(), now_iso(), von, entwurf["id"], *OPEN_STATES, alt_datei))
            if cur.rowcount == 1:
                db.commit()
                gesetzt = True
            else:
                db.rollback()  # nimmt den Lizenz-Datensatz mit zurück
        except sqlite3.OperationalError as exc:  # Datenbank belegt o. Ä.: nichts gesetzt, später erneut
            db.rollback()
            gesetzt = False
            raise NichtBearbeitet(f"Datenbank belegt ({str(exc)[:60]}) – später erneut senden") from None
        except BaseException:
            db.rollback()
            gesetzt = False
            raise
        finally:
            if not gesetzt:
                aktuell = (store.get_draft(entwurf["id"]) or {}).get("bild_datei")
                if name not in (alt_datei, aktuell):
                    for neu in (name, thumb):
                        (settings.bilder_dir / neu).unlink(missing_ok=True)
    if not gesetzt:
        raise Abgelehnt("Entwurf hat sich während des Abrufs geändert (freigegeben oder anderes Bild)")
    andere = alt_datei and store.db.execute(  # nie eine Datei löschen, auf die ein anderer Entwurf zeigt
        "SELECT 1 FROM drafts WHERE bild_datei = ? AND id != ? LIMIT 1", (alt_datei, entwurf["id"])).fetchone()
    for alt_pfad in (() if andere else (alt_datei, (alt_datei or "").replace(".jpg", "-thumb.jpg"))):
        if alt_pfad and alt_pfad not in (name, thumb):
            (settings.bilder_dir / alt_pfad).unlink(missing_ok=True)
    # Protokoll ohne Personendaten: Host, Asset-Nummer und kurzer Hash; die volle Adresse steht im Lizenz-Datensatz
    host, kurz = _host(bild.get("bild_url", "")), adress_hash(bild.get("bild_url", ""))
    store.event("bild", id=entwurf["id"], aktion=f"agent_{weg}", origin=weg, von=von, asset=asset_id, bild_host=host,
                bild_hash=kurz)
    repo.aktion(store, wer=von, aktion="bild", draft_id=entwurf["id"], story_id=story_id, kanal="redaktion",
                ausloeser="agent", notiz=f"Bild mit Nachweis ({weg}): Asset {asset_id}, {host}, #{kurz}")
    return {"ergebnis": "gesetzt", "grund": "Bild gesetzt", "entwurf_id": entwurf["id"],
            "nachweis": bild["nachweis"], "lizenz": bild["lizenz"]}


def _eins(store: Store, settings: Settings, raw, nr: int, von: str, abrufen: Callable) -> dict:
    out: dict = {"nr": nr, "story_id": raw.get("story_id") if isinstance(raw, dict) else None}
    try:
        if not isinstance(raw, dict):
            raise Abgelehnt("Eintrag muss ein Objekt sein")
        if raw.get("weg") not in WEGE:
            raise Abgelehnt("weg muss „commons“ oder „quelle“ sein")
        sid = raw.get("story_id")
        if not isinstance(sid, int) or isinstance(sid, bool):
            raise Abgelehnt("story_id fehlt")
        for feld in ("seite_url", "bild_url"):
            wert = raw.get(feld)
            if feld == "bild_url" and wert in (None, ""):
                continue
            if not isinstance(wert, str) or len(wert) > 2000 or not wert.strip().lower().startswith(("http://", "https://")):
                raise Abgelehnt(f"{feld}: nur http/https-Adressen")
            teile = urlsplit(wert.strip())
            try:
                port = teile.port
            except ValueError:
                port = -1
            if feld == "bild_url" and (port is not None or "@" in teile.netloc):
                raise Abgelehnt("bild_url: keine Adresse mit Port oder Benutzerteil")
        alt = _alt(raw.get("alt"))
        if raw["weg"] == "commons":
            commons_datei(raw["seite_url"])  # Form prüfen, bevor etwas abgerufen wird
        entwurf = _wartender_entwurf(store, sid)
        if raw["weg"] == "commons":
            bild = _commons(raw, abrufen)
        else:
            bild = _quelle(store, settings, raw, sid, abrufen)
        return {**out, **_setzen(store, settings, entwurf, sid, raw["weg"], bild, alt, von)}
    except Abgelehnt as exc:
        return {**out, "ergebnis": "abgelehnt", "grund": str(exc)[:300]}


ERGEBNISSE = ("gesetzt", "abgelehnt", "nicht_bearbeitet")


def _protokoll_ohne_bild(store: Store, von: str, ergebnis: dict, eintrag, abgerufen: bool) -> None:
    """Protokollzeile für jeden Eintrag, bei dem etwas nach außen abgerufen wurde, auch ohne Bild (gesetzte Bilder
    schreibt _setzen). Nur Ergebnis, Weg und Grund – keine Personendaten (Urhebernamen stehen nie im Grund)."""
    if not abgerufen or ergebnis["ergebnis"] == "gesetzt":
        return
    try:
        _protokoll_schreiben(store, von, ergebnis, eintrag)
    except sqlite3.OperationalError as exc:  # Protokoll belegt: nicht als 500 enden, aber im Log festhalten
        logging.getLogger(__name__).warning("Protokollzeile Bild nicht geschrieben: %s", exc)


def _protokoll_schreiben(store: Store, von: str, ergebnis: dict, eintrag) -> None:
    sid = ergebnis.get("story_id") if isinstance(ergebnis.get("story_id"), int) else None
    weg = eintrag.get("weg") if isinstance(eintrag, dict) and eintrag.get("weg") in WEGE else "?"
    repo.aktion(store, wer=von, aktion=f"bild_{ergebnis['ergebnis']}", story_id=sid, kanal="redaktion",
                ausloeser="agent", notiz=f"{weg}: {ergebnis.get('grund') or ''}"[:300])


def annehmen(store: Store, settings: Settings, raw, *, von: str = "agent", abruf: Callable | None = None,
             max_bilder: int = MAX_BILDER, frist_gesamt: float | None = None, frist_abruf: float = FRIST_ABRUF,
             uhr: Callable[[], float] = time.monotonic) -> dict:
    """Bildvorschläge annehmen. Hält der Schalter „redaktion“ schon vorher an, wirft schalter.Gestoppt (nichts getan);
    hält er mitten im Stapel an, enthält die Antwort die bisherigen Ergebnisse und „angehalten“."""
    schalter.pruefen(store, "redaktion")
    items = raw.get("bilder") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError('Bilder: erwartet {"bilder": [...]} oder eine Liste')
    if len(items) > max_bilder:
        raise ValueError(f"höchstens {max_bilder} Bilder je Aufruf")
    if not isinstance(von, str) or not re.fullmatch(r"[a-z0-9-]{1,40}", von):
        raise ValueError("von: nur a-z, 0-9 und Bindestrich, höchstens 40 Zeichen")
    abruf = abruf or (lambda url, frist=None, bild=False: standard_abruf(url, frist=frist, bild=bild))
    ende = uhr() + frist_gesamt if frist_gesamt is not None else None

    abgerufen = [0]  # Abrufe nach außen (gezählt unmittelbar vor dem Aufruf, nach Schalter und Frist)

    def abrufen(url: str, *, bild: bool) -> net.Fetched:
        return _abrufen(store, abruf, url, bild=bild, uhr=uhr, ende=ende, frist_abruf=frist_abruf, zaehler=abgerufen)

    ergebnisse: list[dict] = []
    angehalten = None
    for nr, eintrag in enumerate(items, 1):
        vorher = abgerufen[0]
        if angehalten is None and (ende is None or uhr() < ende):
            try:
                ergebnisse.append(_eins(store, settings, eintrag, nr, von, abrufen))
                _protokoll_ohne_bild(store, von, ergebnisse[-1], eintrag, abgerufen[0] > vorher)
                continue
            except Zeitlimit:
                pass
            except NichtBearbeitet as exc:
                sid = eintrag.get("story_id") if isinstance(eintrag, dict) else None
                ergebnisse.append({"nr": nr, "story_id": sid, "ergebnis": "nicht_bearbeitet",
                                   "grund": f"nicht bearbeitet: {exc}"})
                _protokoll_ohne_bild(store, von, ergebnisse[-1], eintrag, abgerufen[0] > vorher)
                continue
            except schalter.Gestoppt as exc:
                angehalten = {"kanal": exc.sperre["kanal"], "seit": exc.sperre["seit"]}
        grund = "nicht bearbeitet: angehalten" if angehalten else "nicht bearbeitet: Zeitlimit"
        sid = eintrag.get("story_id") if isinstance(eintrag, dict) else None
        ergebnisse.append({"nr": nr, "story_id": sid, "ergebnis": "nicht_bearbeitet", "grund": grund})
        _protokoll_ohne_bild(store, von, ergebnisse[-1], eintrag, abgerufen[0] > vorher)
    out = {"ergebnisse": ergebnisse, **{k: sum(1 for e in ergebnisse if e["ergebnis"] == k) for k in ERGEBNISSE}}
    if angehalten:
        out["angehalten"] = angehalten
    return out
