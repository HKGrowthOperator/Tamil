#!/usr/bin/env python3
"""Migration des Altbestands von tamil.de in die neue Website (Plugin tamil-radar + tamil-site).

Liest den Export (tools/export_site.py: posts/pages/media/categories.json) und schreibt in die NEUE Website:
Beiträge mit Originaldatum und Original-Slug, Rubriken, Beitragsbild und Bilder im Text als Medien, Seiten und die
301-Tabelle. Die alte tamil.de wird nur gelesen (Bilder laden, falls nicht im Medien-Ordner). Idempotent: Beiträge
über radar_uid ``alt-<ID>`` (Seiten-Beiträge ``altseite-<ID>``), Seiten über den Slug, Medien im Text über den Slug.

    python tools/migration.py --export <ordner> --url https://<neue-website> --benutzer <admin> \\
        --passwort-datei <datei> [--trocken] [--limit 50] [--bericht bericht.json]

Passwort: aus der Datei (--passwort-datei) oder $MIGRATION_APP_PASSWORD; wird nie ausgegeben. Beispielwerte aus
prototyp/content/site.json (Telefon, E-Mail, WhatsApp) füllen nie die Kontaktfelder der neuen Website; Texte bleiben
unverändert, der Bericht zählt nur, wo Kontaktangaben vorkommen.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import ipaddress
import html as html_mod
import importlib.util
import io
import json
import mimetypes
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import nh3  # noqa: E402
import requests  # noqa: E402
from requests.models import PreparedRequest  # noqa: E402
import export_site  # noqa: E402  (Kategorien-/Seiten-Abbildung und Weiterleitungen: eine Quelle der Wahrheit)

NEUE_RUBRIKEN = ("news", "entertainment", "events", "community", "kueche", "kino", "sport", "kultur")
EXTRA_SCHLAGWORT = {"kritik": "Kritik", "anirudh": "Anirudh"}  # laut CATEGORY_MAP „+ Schlagwort …“
ALTE_HOSTS = ("tamil.de", "www.tamil.de")
UPLOAD_RE = re.compile(r"https?://(?:www\.)?tamil\.de/wp-content/uploads/([^\"'\s<>?#)]+)", re.I)
INTERN_RE = re.compile(r"""(href=["'])https?://(?:www\.)?tamil\.de(/(?!wp-content/)[^"']*|/?)(["'])""", re.I)
OFFENE_UPLOAD_HREF_RE = re.compile(r"""href=["']https?://(?:www\.)?tamil\.de/wp-content/""", re.I)
SRCSET_RE = re.compile(r"""\s(?:srcset|sizes)=(["']).*?\1""", re.I | re.S)
YT_IFRAME_RE = re.compile(r"""<iframe\b[^>]*\bsrc=["']https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([\w-]{6,})[^"']*["'][^>]*>\s*</iframe>""", re.I)
IFRAME_RE = re.compile(r"<iframe\b", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def _lade_wp_klasse():
    """Die REST-Hilfsklasse WP aus dem Prototyp-Importer wiederverwenden (keine zweite Kopie)."""
    spec = importlib.util.spec_from_file_location("import_prototype", REPO / "wordpress" / "dev" / "import_prototype.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.WP


# ---------------------------------------------------------------- reine Logik (ohne Netz, getestet)

def text(html: str) -> str:
    """HTML-Fragment (Titel, Auszug) als reiner Text."""
    return re.sub(r"\s+", " ", html_mod.unescape(TAG_RE.sub("", html or ""))).strip()


def post_uid(old_id: int, aus_seite: bool = False) -> str:
    """Idempotenz-Schlüssel eines Beitrags (derselbe wie im Prototyp-Snapshot: alt-<ID>)."""
    return f"{'altseite' if aus_seite else 'alt'}-{int(old_id)}"


def map_kategorien(alte_slugs: list[str]) -> tuple[str | None, list[str], list[str]]:
    """Alte Kategorie-Slugs -> (Hauptrubrik, weitere Rubriken, zusätzliche Schlagworte).

    Abbildung kommt aus export_site.CATEGORY_MAP. Hauptrubrik ist die spezifischste (news zuletzt). Nur „test“ ->
    (None, [], []) = Beitrag wird nicht übernommen. Unbekannte Slugs ohne Ziel landen in news.
    """
    ziele: list[str] = []
    tags: list[str] = []
    for slug in alte_slugs:
        neu, _ = export_site.CATEGORY_MAP.get(slug, (slug, ""))
        if neu is None:
            continue
        if neu not in NEUE_RUBRIKEN:
            neu = "news"
        if neu not in ziele:
            ziele.append(neu)
        if slug in EXTRA_SCHLAGWORT:
            tags.append(EXTRA_SCHLAGWORT[slug])
    if not ziele:
        return None, [], []
    ziele.sort(key=lambda z: z == "news")
    return ziele[0], ziele[1:], tags


def beispielwerte(site_json: dict) -> list[str]:
    """Telefon, E-Mail, WhatsApp-Nummer aus dem Prototyp (alles Beispielwerte, nie übernehmen)."""
    k = site_json.get("kontakt", {})
    return [v for v in (k.get("telefon"), k.get("email"), k.get("whatsapp")) if v]


def kontaktangaben(html: str, werte: list[str]) -> list[str]:
    """Welche Kontaktangaben (E-Mail, Telefon, WhatsApp aus site.json) kommen im Text vor? Es wird nichts verändert:
    die E-Mail steht auch auf der alten Seite in Texten. Nur die Kontaktfelder der neuen Website (Customizer) bleiben
    ohne die Beispielwerte."""
    flach = html.replace(" ", "")
    return [v for v in werte if v and (v in html or v.replace(" ", "") in flach)]


def upload_urls(html: str) -> list[str]:
    """Alle Adressen auf alte Uploads (Bilder, Dateien) in src/href, in Reihenfolge, ohne Doppelte."""
    seen: dict[str, None] = {}
    for m in UPLOAD_RE.finditer(html or ""):
        seen[m.group(0)] = None
    return list(seen)


def media_slug(url: str) -> str:
    """Stabiler Medien-Slug aus alter Adresse (Dateiname + Kurzprüfsumme): gleiche Dateinamen aus verschiedenen
    Monaten kollidieren nicht, und ein zweiter Lauf findet das Medium wieder (Idempotenz-Schlüssel der Bilder im Text)."""
    stem = re.sub(r"[^a-z0-9]+", "-", Path(urlsplit(url).path).stem.lower()).strip("-")[:60] or "bild"
    pfad = UPLOAD_RE.sub(lambda m: m.group(1), url)  # Schema und Host spielen keine Rolle (http/https, mit/ohne www)
    return "alt-%s-%s" % (stem, hashlib.sha1(pfad.encode()).hexdigest()[:8])


def upload_dateiname(url: str) -> str:
    return Path(urlsplit(url).path).name


def rewrite_html(html: str, url_map: dict[str, str]) -> str:
    """Bildadressen auf die neue Website umschreiben, srcset/sizes (zeigen auf alte Größen) entfernen,
    interne Links relativ machen, YouTube-iframes als Embed-URL (kses des Plugins entfernt iframes)."""
    for alt, neu in sorted(url_map.items(), key=lambda kv: -len(kv[0])):
        html = html.replace(alt, neu)
        html = re.sub(re.escape(alt.replace("https://", "http://", 1)), lambda _m: neu, html, flags=re.I)
    html = SRCSET_RE.sub("", html)
    html = YT_IFRAME_RE.sub(
        lambda m: f'<figure class="wp-block-embed is-type-video"><div class="wp-block-embed__wrapper">\nhttps://www.youtube.com/watch?v={m.group(1)}\n</div></figure>',
        html,
    )

    def intern(m: re.Match) -> str:
        pfad = m.group(2) or "/"
        return f"{m.group(1)}{pfad}{m.group(3)}"

    return INTERN_RE.sub(intern, html)


def fremde_bilder(html: str) -> list[str]:
    """Bilder im Text, die weder auf tamil.de noch relativ-neu liegen (bleiben Fremdverweise; werden gemeldet)."""
    out = []
    for src in re.findall(r"<img[^>]+src=[\"']([^\"']+)", html or ""):
        host = urlsplit(src).netloc
        if host and host not in ALTE_HOSTS and not UPLOAD_RE.match(src):
            out.append(src)
    return out


def idempotenz_pruefen(posts: list[dict]) -> list[str]:
    """Doppelte Slugs im Export (würden beim Import umbenannt)."""
    zaehler = Counter(p["slug"] for p in posts)
    return sorted(s for s, n in zaehler.items() if n > 1)


def redirect_csv(site: str, categories: list[dict], pages: list[dict], extra: list[tuple[str, str]] = ()) -> str:
    """301-Tabelle als CSV (Spalten alt, neu): Kategorien und Seiten aus export_site, plus Slug-Abweichungen."""
    rows = [(r["alt"], r["neu"]) for r in export_site.redirect_rows(site.rstrip("/"), categories, pages)]
    rows += list(extra)
    # Pfade statt voller Adressen: das Plugin leitet mit wp_safe_redirect auf die eigene Domain (home_url), fremde Hosts
    # würden auf /wp-admin/ fallen – auch auf der Übergangsadresse vor der Domain-Umschaltung.
    rows = [(urlsplit(a).path or "/", urlsplit(n).path or "/") for a, n in rows]
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["alt", "neu"])
    gesehen = set()
    for alt, neu in rows:
        if alt not in gesehen:
            gesehen.add(alt)
            w.writerow([alt, neu])
    return out.getvalue()


def seiten_plan(pages: list[dict]) -> dict[str, list[dict]]:
    """Seiten des Exports nach Aktion: seite / beitrag / redirect / loeschen (export_site.PAGE_MAP)."""
    plan: dict[str, list[dict]] = {"seite": [], "beitrag": [], "redirect": [], "loeschen": []}
    for p in pages:
        slug = p.get("slug")
        if slug in export_site.DELETE_PAGE_SLUGS:
            plan["loeschen"].append(p)
        else:
            plan[export_site.PAGE_MAP.get(slug, ("seite", slug))[0]].append(p)
    return plan


SEITEN_TAGS = {"a", "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "strong", "b", "em", "i", "u",
               "blockquote", "figure", "figcaption", "img", "table", "thead", "tbody", "tr", "th", "td", "div", "span",
               "details", "summary", "small", "sub", "sup", "pre", "code", "caption", "tfoot", "colgroup", "col", "s",
               "mark", "abbr", "cite"}
SEITEN_ATTRIBUTE = {"a": {"href", "title", "rel", "target"}, "img": {"src", "alt", "width", "height", "title"},
                    "*": {"class", "id", "lang", "dir"}, "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan"}, "col": {"span"}, "colgroup": {"span"}}
URL_ZEILE_RE = re.compile(r"\s*https?://\S+\s*")
VIDEO_URL_RE = re.compile(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)/\S+", re.I)


def seite_bereinigen(html: str) -> str:
    """Seiteninhalt vor dem Senden bereinigen (Seiten laufen als Administrator ungefiltert durch die Core-REST):
    keine Skripte, keine iframes, keine on*-Attribute, keine javascript:-Adressen (Allowlist nh3)."""
    return nh3.clean(html or "", tags=SEITEN_TAGS, attributes=SEITEN_ATTRIBUTE, url_schemes={"http", "https", "mailto", "tel"},
                     link_rel=None, strip_comments=True)


def bilde_teaser(excerpt_html: str, content_html: str, max_woerter: int = 55) -> tuple[str, bool]:
    """Auszug: der eigene Auszug des alten Beitrags, solange keine nackte Video-Adresse darin steht. Sonst (oder ohne
    Auszug) aus dem Text gebildet – ohne die Zeilen, die nur aus einer Adresse bestehen. Gibt (Teaser, ersetzt) zurück."""
    eigen = text(excerpt_html)
    if eigen and not VIDEO_URL_RE.search(eigen):
        return eigen, False
    roh = re.sub(r"<(script|style|iframe)\b.*?</\1>", " ", content_html or "", flags=re.S | re.I)
    roh = re.sub(r"</(p|div|figure|li|h\d|blockquote)>|<br\s*/?>", "\n", roh, flags=re.I)
    zeilen = [re.sub(r"\s+", " ", html_mod.unescape(TAG_RE.sub("", z))).strip() for z in roh.split("\n")]
    woerter = " ".join(z for z in zeilen if z and not URL_ZEILE_RE.fullmatch(z)).split()
    teaser = " ".join(woerter[:max_woerter]) + ("…" if len(woerter) > max_woerter else "")
    return teaser, bool(eigen)


ZAHLENHOST_RE = re.compile(r"^(?:0x[0-9a-f]*|[0-9]+)(?:\.(?:0x[0-9a-f]*|[0-9]+))*\.?$", re.I)
ERLAUBTE_ZIELE = ("tamil-web.167.233.76.202.sslip.io", "localhost", "127.0.0.1", "::1")


def ziel_normalisieren(url: str, nach_umschaltung: bool = False, bestaetigt: bool = False, ziel_host: str = "") -> tuple[str, str]:
    """Ziel-Adresse so normalisieren, wie `requests` es tut, und erst dann prüfen. Gibt (Adresse, Fehlermeldung) zurück;
    bei Fehler ist die Adresse leer. Nur die normalisierte Adresse darf verwendet werden.

    - `%`, Leerzeichen und Nicht-ASCII im Host-Teil: immer abgelehnt (sonst wird aus https://%74amil.de die alte Seite).
    - Anmeldedaten, Host mit Punkt am Ende, IP-Adressen (außer 127.0.0.1 und ::1): abgelehnt.
    - tamil.de und alle Unterdomains: abgelehnt; Ausnahme nur mit nach_umschaltung UND bestaetigt für genau
      tamil.de/www.tamil.de.
    - Positivliste: sslip-Host der neuen Website, localhost, 127.0.0.1, ::1; jeder andere Host nur mit ziel_host, der
      dem normalisierten Host exakt entspricht.
    - http nur für localhost, 127.0.0.1 und ::1.
    """
    roh = urlsplit(url).netloc
    if any(c in roh for c in "% \t\r\n") or not roh.isascii():
        return "", "Host enthält %, Leerzeichen oder Nicht-ASCII-Zeichen."
    try:
        pr = PreparedRequest()
        pr.prepare_url(url, None)
        norm = urlsplit(pr.url)
    except Exception:  # noqa: BLE001
        return "", "Adresse unbrauchbar."
    if norm.scheme not in ("http", "https") or not norm.hostname:
        return "", "Adresse unbrauchbar (http/https mit Host nötig)."
    if norm.username is not None or norm.password is not None or "@" in norm.netloc:
        return "", "Adressen mit Anmeldedaten sind nicht erlaubt."
    roh_teile = urlsplit(url)
    if roh_teile.path not in ("", "/") or roh_teile.query or roh_teile.fragment or "?" in url or "#" in url:
        return "", "Nur scheme://host[:port] ist erlaubt (kein Pfad, keine Query, kein Fragment)."
    host = norm.hostname.lower()
    if host not in ("127.0.0.1", "::1") and ZAHLENHOST_RE.match(host):
        return "", "Hosts aus Ziffern, Punkten oder 0x… (Kurz- und Dezimalformen von IP-Adressen) sind nie erlaubt."
    if host.endswith("."):
        return "", "Host mit Punkt am Ende ist nicht erlaubt."
    ist_ip = True
    try:
        ipaddress.ip_address(host)
    except ValueError:
        ist_ip = False
    if ist_ip and host not in ("127.0.0.1", "::1"):
        return "", "IP-Adressen sind als Ziel nicht erlaubt (außer 127.0.0.1 und ::1)."
    freigegeben = False
    if host == "tamil.de" or host.endswith(".tamil.de"):
        if not (nach_umschaltung and bestaetigt and host in ALTE_HOSTS):
            return "", "Ziel ist die alte tamil.de-Adresse. Die alte Seite wird nie beschrieben."
        freigegeben = True
    if not freigegeben and host not in ERLAUBTE_ZIELE and host != ziel_host.strip().lower():
        return "", f"Host {host} steht nicht auf der Positivliste; ausdrücklich mit --ziel-host {host} freigeben."
    if norm.scheme == "http" and host not in ("localhost", "127.0.0.1", "::1"):
        return "", "http nur für 127.0.0.1, localhost und ::1: das Anwendungspasswort ginge sonst im Klartext hinaus."
    return norm.geturl().rstrip("/"), ""


def vorabpruefung(url: str, http, nach_umschaltung: bool = False, bestaetigt: bool = False) -> str:
    """Einmal GET <ziel>/wp-json/ ohne Weiterleitungen: ist das wirklich die neue Website mit beiden Plugins, und zeigen
    `home`/`url` nicht auf die alte Seite? Gibt eine Fehlermeldung zurück ("" = in Ordnung)."""
    try:
        r = http.get(f"{url}/wp-json/", timeout=30, allow_redirects=False)
    except Exception as exc:  # noqa: BLE001
        return f"Ziel nicht erreichbar: {str(exc)[:80]}"
    if 300 <= r.status_code < 400:
        return f"Ziel antwortet mit Weiterleitung {r.status_code}; Adresse prüfen (nicht gefolgt)."
    try:
        d = r.json()
        namen = d.get("namespaces") or []
    except Exception:  # noqa: BLE001
        return "Antwort von /wp-json/ ist kein JSON: das ist nicht die neue WordPress-Website."
    fehlt = [n for n in ("tamil-radar/v1", "tamil-site/v1") if n not in namen]
    if fehlt:
        return "Plugins nicht aktiv, Namensräume fehlen: " + ", ".join(fehlt)
    if not (nach_umschaltung and bestaetigt):
        for feld in ("home", "url"):
            host = (urlsplit(str(d.get(feld) or "")).hostname or "").lower().rstrip(".")
            if host == "tamil.de" or host.endswith(".tamil.de"):
                return f"Die Website meldet {feld} auf {host}: das wäre die alte Seite oder schon umgeschaltet (--nach-umschaltung)."
    return ""


def ziel_pruefen(url: str, nach_umschaltung: bool = False, bestaetigt: bool = False, ziel_host: str = "") -> str:
    """Nur die Fehlermeldung von ziel_normalisieren ("" = zulässig)."""
    return ziel_normalisieren(url, nach_umschaltung, bestaetigt, ziel_host)[1]


def ist_voruebergehend(status) -> bool:
    """Lohnt ein neuer Lauf? 429, 5xx, Netz- und Upload-Fehler ja; 404, andere 4xx und fremde Hosts nein."""
    if isinstance(status, int):
        return status == 429 or status >= 500
    return str(status).startswith(("Netzfehler", "Upload"))


# ---------------------------------------------------------------- Netz (alte Seite nur lesen, neue Seite schreiben)

class Medien:
    """Quelle der Bilder: Medien-Ordner (Layout JJJJ/MM/datei wie export_site), sonst lesend von der alten Seite.

    Nur https und nur Hosts der alten Seite; Weiterleitungen nur auf dieselben Hosts (höchstens 3); bei 429/5xx bis
    zu drei Versuche mit Wartezeit. `status[url]` hält fest, woran es lag (404 = gibt es auf der alten Seite nicht)."""

    def __init__(self, ordner: Path, pause: float = 0.25, warte: float = 2.0):
        self.ordner, self.pause, self.warte = Path(ordner), pause, warte
        # eigene Sitzung ohne Retry-Adapter: es gelten nur die drei Versuche unten, nichts hängt minutenlang
        self.session = requests.Session()
        self.session.headers["User-Agent"] = export_site.USER_AGENT
        self.session.max_redirects = 3
        self.geladen = 0
        self.status: dict[str, int | str] = {}

    def ziel(self, url: str) -> Path:
        rel = export_site.media_target(Path("."), url).relative_to("media")
        return self.ordner / rel

    def holen(self, url: str) -> bytes | None:
        ziel = self.ziel(url)
        if ziel.exists() and ziel.stat().st_size > 0:
            self.status.pop(url, None)
            return ziel.read_bytes()
        teile = urlsplit(re.sub(r"^http://", "https://", url, flags=re.I))
        if teile.scheme != "https" or (teile.hostname or "").lower() not in ALTE_HOSTS:
            self.status[url] = "fremder Host"
            return None
        adresse = teile.geturl()
        for versuch in range(3):
            try:
                r = None
                for _ in range(4):
                    r = self.session.get(adresse, timeout=30, allow_redirects=False)
                    if r.status_code in (301, 302, 307, 308) and r.headers.get("Location"):
                        nxt = urlsplit(requests_join(adresse, r.headers["Location"]))
                        if nxt.scheme != "https" or (nxt.hostname or "").lower() not in ALTE_HOSTS:
                            self.status[url] = "Weiterleitung auf fremden Host"
                            return None
                        adresse = nxt.geturl()
                        continue
                    break
            except Exception as exc:  # noqa: BLE001
                self.status[url] = f"Netzfehler: {str(exc)[:60]}"
                time.sleep(self.warte * (versuch + 1))
                continue
            if r.status_code == 200 and r.content:
                ziel.parent.mkdir(parents=True, exist_ok=True)
                ziel.write_bytes(r.content)
                self.geladen += 1
                self.status.pop(url, None)
                time.sleep(self.pause)
                return r.content
            self.status[url] = r.status_code
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(self.warte * (versuch + 1))
                continue
            break
        print(f"  Bild fehlt: {url} ({self.status.get(url)})", file=sys.stderr)
        return None


def requests_join(basis: str, ziel: str) -> str:
    from urllib.parse import urljoin
    return urljoin(basis, ziel)


class Migration:
    def __init__(self, wp, export: Path, medien: Medien, site_json: dict, trocken: bool = False):
        self.wp, self.export, self.medien, self.trocken = wp, export, medien, trocken
        self.werte = beispielwerte(site_json)
        self.bericht: dict = {
            "beitraege": Counter(), "seiten": Counter(), "medien": Counter(), "fehlende_bilder": [], "unvollstaendig": [],
            "kontaktangaben_in_texten": {}, "fremde_bilder": 0, "fremde_bilder_beitraege": [],
            "nicht_youtube_iframes": 0, "slug_abweichungen": [], "slug_kollisionen": [], "alt_text_fallback": 0,
            "bilder_unter_1200px": 0, "seiten_ohne_text": [], "teaser_ohne_videoadresse": 0, "href_alte_uploads_offen": 0,
            "bilder_nachgezogen": 0,
        }
        self.fehlend: dict[str, set] = {}
        self.unvollstaendig: set = set()
        self.media_by_id = {m["id"]: m for m in json.loads((export / "media.json").read_text(encoding="utf-8"))}
        self.media_by_url = {m["source_url"]: m for m in self.media_by_id.values()}

    # -- Medien im Text
    def fehlt(self, url: str, aus: str) -> None:
        self.fehlend.setdefault(url, set()).add(aus)
        self.unvollstaendig.add(aus)

    def text_medien(self, html: str, aus: str = "") -> dict[str, str]:
        """Alte Upload-Adressen im Text als Medien der neuen Seite anlegen; gibt alt -> neu zurück.
        Was nicht zu holen ist, bleibt auf der Altadresse (https) und wird als fehlend/unvollständig gemeldet."""
        mapping: dict[str, str] = {}
        for url in upload_urls(html):
            name = upload_dateiname(url)
            slug = media_slug(url)
            code, found = self.wp.req("GET", "wp/v2/media", params={"slug": slug, "_fields": "id,source_url"})
            if code == 200 and found:
                mapping[url] = found[0]["source_url"]
                self.bericht["medien"]["vorhanden"] += 1
                continue
            alt_https = re.sub(r"^http://", "https://", url, flags=re.I)
            daten = self.medien.holen(url)
            if daten is None:
                self.fehlt(url, aus)
                mapping[url] = alt_https
                continue
            if self.trocken:
                self.bericht["medien"]["neu"] += 1
                continue
            mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
            r = self.wp.http.post(f"{self.wp.url}/wp-json/wp/v2/media", data=daten, timeout=300, params={"slug": slug}, allow_redirects=False,
                                  headers={"Content-Disposition": f'attachment; filename="{name}"', "Content-Type": mime})
            if 300 <= r.status_code < 400:
                raise RuntimeError(f"Weiterleitung {r.status_code} der neuen Website beim Hochladen (Ziel-Adresse prüfen)")
            if r.status_code >= 400:
                self.medien.status[url] = f"Upload {r.status_code}"
                self.fehlt(url, aus)
                mapping[url] = alt_https
                continue
            mapping[url] = r.json()["source_url"]
            self.bericht["medien"]["neu"] += 1
        return mapping

    def inhalt(self, html: str, aus: str, bereinigen: bool = False) -> str:
        gefunden = kontaktangaben(html, self.werte)
        for v in gefunden:
            self.bericht["kontaktangaben_in_texten"].setdefault(v, []).append(aus)
        self.bericht["nicht_youtube_iframes"] += len(IFRAME_RE.findall(YT_IFRAME_RE.sub("", html)))
        fremd = fremde_bilder(html)
        if fremd:
            self.bericht["fremde_bilder"] += len(fremd)
            self.bericht["fremde_bilder_beitraege"].append(aus)
        neu = rewrite_html(html, self.text_medien(html, aus))
        if bereinigen:
            neu = seite_bereinigen(neu)
        self.bericht["href_alte_uploads_offen"] += len(OFFENE_UPLOAD_HREF_RE.findall(neu))
        return neu

    # -- Beiträge
    def beitragsbild(self, p: dict, titel: str, uid: str = "") -> dict:
        m = self.media_by_id.get(p.get("featured_media"))
        if not m:
            return {}
        daten = self.medien.holen(m["source_url"])
        if daten is None:
            self.fehlt(m["source_url"], uid)
            return {}
        if (m.get("media_details") or {}).get("width", 9999) < 1200:
            self.bericht["bilder_unter_1200px"] += 1
        alt = m.get("alt_text") or ""
        if not alt:
            alt = titel
            self.bericht["alt_text_fallback"] += 1
        return {"daten": base64.b64encode(daten).decode("ascii"), "dateiname": upload_dateiname(m["source_url"]), "alt": alt, "credit": ""}

    def nachziehen(self, uid: str, wp_id: int, p: dict, aus_seite: bool) -> None:
        """Vorhandener Beitrag: fehlendes Beitragsbild und nicht übertragene Bilder im Text eines früheren Laufs nachholen."""
        if self.trocken or not wp_id:
            return
        code, d = self.wp.req("GET", f"wp/v2/posts/{wp_id}", params={"context": "edit", "_fields": "content,featured_media"})
        if code != 200:
            return
        upd: dict = {}
        titel = text(p["title"]["rendered"]) if isinstance(p["title"], dict) else text(p["title"])
        if not aus_seite and p.get("featured_media") in self.media_by_id and not d.get("featured_media"):
            bild = self.beitragsbild(p, titel, uid)
            if bild:
                upd["bild"] = bild
                self.bericht["bilder_nachgezogen"] += 1
        roh = (d.get("content") or {}).get("raw", "")
        if UPLOAD_RE.search(roh):
            neu = rewrite_html(roh, self.text_medien(roh, uid))
            if neu != roh:
                upd["inhalt"] = neu
                self.bericht["bilder_nachgezogen"] += 1
        if upd:
            c, data = self.wp.req("PUT", f"tamil-radar/v1/beitrag/{uid}", json=upd)
            if c >= 400:
                raise RuntimeError(f"{uid}: nachziehen {c} {str(data)[:200]}")

    def beitrag(self, p: dict, kat_slugs: list[str], aus_seite: bool = False, ziel_rubrik: str = "") -> int:
        uid = post_uid(p["id"], aus_seite)
        if aus_seite:
            haupt, weitere, extra = ziel_rubrik, [], []
        else:
            haupt, weitere, extra = map_kategorien(kat_slugs)
        if haupt is None:
            self.bericht["beitraege"]["übersprungen (nur Kategorie test)"] += 1
            return 0
        code, vorhanden = self.wp.req("GET", f"tamil-radar/v1/beitrag/{uid}")
        if code == 200:
            self.bericht["beitraege"]["vorhanden"] += 1
            wp_id = int(vorhanden.get("id") or 0)
            self.nachziehen(uid, wp_id, p, aus_seite)
            return wp_id
        titel = text(p["title"]["rendered"]) if isinstance(p["title"], dict) else text(p["title"])
        inhalt = self.inhalt(p["content"]["rendered"], uid)
        teaser, ersetzt = bilde_teaser((p.get("excerpt") or {}).get("rendered", ""), p["content"]["rendered"])
        if ersetzt or (not text((p.get("excerpt") or {}).get("rendered", "")) and VIDEO_URL_RE.search(p["content"]["rendered"])):
            self.bericht["teaser_ohne_videoadresse"] += 1
        payload = {
            "titel": titel,
            "inhalt": inhalt,
            "teaser": teaser,
            "status": "publish",
            "slug": p["slug"],
            "datum": p["date"].replace("T", " "),
            "kategorie": haupt,
            "kategorien": weitere,
            "schlagworte": extra,
            "meta": {"radar_uid": uid},
            "bild": {} if aus_seite else self.beitragsbild(p, titel, uid),
        }
        if self.trocken:
            self.bericht["beitraege"]["neu (trocken)"] += 1
            return 0
        status, wp_id = self.wp.beitrag(payload)
        self.bericht["beitraege"][status] += 1
        return wp_id

    def beitraege(self, posts: list[dict], kategorien: dict[int, str], limit: int = 0) -> None:
        for i, p in enumerate(posts):
            if limit and i >= limit:
                break
            self.beitrag(p, [kategorien.get(c, str(c)) for c in p.get("categories", [])])

    def abweichungen(self, posts: list[dict], kategorien: dict[int, str], pages: list[dict]) -> list[tuple[str, str]]:
        """Weiterleitungen für Beiträge, deren Slug auf der neuen Seite vom alten abweicht – bei JEDEM Lauf für alle
        importierten Beiträge (alt-*, altseite-*) neu ermittelt, unabhängig von --limit und davon, ob sie neu sind.
        Gehört der alte Slug einem fremden Beitrag (ohne alt-Kennung), wird gemeldet und nichts umgeleitet."""
        kandidaten = []
        for p in posts:
            if map_kategorien([kategorien.get(c, str(c)) for c in p.get("categories", [])])[0]:
                kandidaten.append((post_uid(p["id"]), p))
        kandidaten += [(post_uid(p["id"], True), p) for p in seiten_plan(pages)["beitrag"]]
        gefunden: list[tuple[str, dict, dict]] = []
        for uid, p in kandidaten:
            code, d = self.wp.req("GET", f"tamil-radar/v1/beitrag/{uid}")
            if code == 200:
                gefunden.append((uid, p, d))
        eigene_ids = {int(d["id"]) for _, _, d in gefunden}
        rows: list[tuple[str, str]] = []
        self.bericht["slug_abweichungen"], self.bericht["slug_kollisionen"] = [], []
        for uid, p, d in gefunden:
            if d.get("slug") == p["slug"]:
                continue
            code, belegt = self.wp.req("GET", "wp/v2/posts", params={"slug": p["slug"], "status": "any", "context": "edit", "_fields": "id"})
            if code != 200 or not isinstance(belegt, list):
                self.bericht.setdefault("slug_pruefung_fehlgeschlagen", []).append({"uid": uid, "slug": p["slug"], "status": code})
                continue  # nichts umleiten, solange nicht klar ist, wem der alte Slug gehört
            fremd = [int(x["id"]) for x in belegt if int(x["id"]) not in eigene_ids]
            if fremd:
                self.bericht["slug_kollisionen"].append({"uid": uid, "slug": p["slug"], "neu": d.get("slug"), "belegt_von": fremd})
                continue
            self.bericht["slug_abweichungen"].append({"uid": uid, "alt": p["link"], "neu": d.get("link")})
            rows.append((p["link"], d["link"]))
        return rows

    # -- Seiten
    def seite(self, slug: str, titel: str, quelle: dict, aus: str) -> None:
        """Seite anlegen (oder eine leere Hülle füllen). Erst prüfen, ob es sie gibt – dann erst Medien anfassen."""
        code, data = self.wp.req("GET", "wp/v2/pages", params={"slug": slug, "status": "publish,draft", "context": "edit"})
        vorhanden = code == 200 and bool(data)
        leer = vorhanden and not (data[0].get("content") or {}).get("raw", "").strip()
        if vorhanden and not leer:
            self.bericht["seiten"]["vorhanden"] += 1
            return
        inhalt = self.inhalt(quelle["content"]["rendered"], aus, bereinigen=True)
        if aus == "seite-reporter" and inhalt.strip():
            inhalt = "<h2>Mitmachen: Leser-Reporter</h2>\n" + inhalt
        if len(text(inhalt).split()) < 25:
            self.bericht["seiten_ohne_text"].append(slug)
        if self.trocken:
            self.bericht["seiten"]["neu (trocken)"] += 1
            return
        if vorhanden:
            c, antwort = self.wp.req("POST", f"wp/v2/pages/{data[0]['id']}", json={"content": inhalt})
            if c >= 400:
                raise RuntimeError(f"Seite {slug}: Füllen fehlgeschlagen {c} {str(antwort)[:200]}")
            self.bericht["seiten"]["gefüllt (war leer)"] += 1
            return
        code, data = self.wp.req("POST", "wp/v2/pages", json={"slug": slug, "title": titel, "content": inhalt, "status": "publish", "date": quelle["date"].replace("T", " ")})
        if code >= 400:
            raise RuntimeError(f"Seite {slug}: {code} {str(data)[:300]}")
        self.bericht["seiten"]["neu"] += 1

    def seiten(self, pages: list[dict]) -> None:
        plan = seiten_plan(pages)
        for p in plan["seite"]:
            slug = p["slug"]
            neu = export_site.PAGE_MAP.get(slug, ("seite", slug))[1]
            self.seite(neu, text(p["title"]["rendered"]), p, f"seite-{slug}")
        for p in plan["beitrag"]:
            self.beitrag(p, [], aus_seite=True, ziel_rubrik=export_site.PAGE_MAP[p["slug"]][1])
            self.bericht["seiten"]["als Beitrag"] += 1
        self.bericht["seiten"]["Weiterleitung (kein Inhalt)"] += len(plan["redirect"])
        self.bericht["seiten"]["Altlast nicht übernommen"] += len(plan["loeschen"])

    def weiterleitungen(self, csv_text: str) -> dict:
        if self.trocken:
            return {}
        code, data = self.wp.req("POST", "tamil-site/v1/weiterleitungen", json={"csv": csv_text})
        if code >= 400:
            raise RuntimeError(f"Weiterleitungen: {code} {str(data)[:200]}")
        return data


def passwort(datei: str) -> str:
    if datei:
        return Path(datei).read_text(encoding="utf-8").strip()
    return os.environ.get("MIGRATION_APP_PASSWORD", "").strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--export", type=Path, required=True, help="Ordner des Exports (posts.json, pages.json, media.json, …)")
    ap.add_argument("--url", default=os.environ.get("WP_URL", ""), help="Adresse der NEUEN Website")
    ap.add_argument("--benutzer", default=os.environ.get("WP_ADMIN_USER", "admin"))
    ap.add_argument("--passwort-datei", default="", help="Datei mit dem Anwendungspasswort (sonst $MIGRATION_APP_PASSWORD)")
    ap.add_argument("--medien", type=Path, default=None, help="Medien-Ordner (Standard: <export>/media)")
    ap.add_argument("--trocken", action="store_true", help="nichts schreiben, nur zählen")
    ap.add_argument("--limit", type=int, default=0, help="nur die ersten N Beiträge (Zeitmessung)")
    ap.add_argument("--bericht", type=Path, default=None, help="Bericht als JSON schreiben")
    ap.add_argument("--nach-umschaltung", action="store_true", help="erlaubt nach der Domain-Umschaltung das Ziel tamil.de/www.tamil.de (nur mit --bestaetigt-von-luis)")
    ap.add_argument("--bestaetigt-von-luis", action="store_true", help="ausdrückliche Bestätigung zu --nach-umschaltung")
    ap.add_argument("--ziel-host", default="", help="Host der neuen Website, falls nicht auf der Positivliste (muss dem normalisierten Host exakt entsprechen)")
    ap.add_argument("--nur", choices=("beitraege", "seiten", "weiterleitungen"), action="append", help="Teilschritte (Standard: alle)")
    args = ap.parse_args(argv)

    if args.nach_umschaltung and not args.bestaetigt_von_luis:
        print("Abbruch: --nach-umschaltung verlangt --bestaetigt-von-luis.")
        return 2
    url, fehler = ziel_normalisieren(args.url, args.nach_umschaltung, args.bestaetigt_von_luis, args.ziel_host)
    if fehler:  # vor dem Lesen des Passworts
        print("Abbruch: " + fehler)
        return 2
    pw = passwort(args.passwort_datei)
    if not pw:
        print("Passwort fehlt (--passwort-datei oder $MIGRATION_APP_PASSWORD).")
        return 2
    vor = vorabpruefung(url, requests.Session(), args.nach_umschaltung, args.bestaetigt_von_luis)  # auch bei --trocken
    if vor:
        print("Abbruch (Vorabprüfung): " + vor)
        return 4

    export = args.export
    site_json = json.loads((REPO / "prototyp" / "content" / "site.json").read_text(encoding="utf-8"))
    posts = json.loads((export / "posts.json").read_text(encoding="utf-8"))
    pages = json.loads((export / "pages.json").read_text(encoding="utf-8"))
    cats = json.loads((export / "categories.json").read_text(encoding="utf-8"))
    kat = {c["id"]: c["slug"] for c in cats}
    schritte = set(args.nur or ("beitraege", "seiten", "weiterleitungen"))

    WP = _lade_wp_klasse()
    m = Migration(WP(url, args.benutzer, pw), export, Medien(args.medien or export / "media"), site_json, args.trocken)
    start = time.time()
    alle = sorted(posts, key=lambda p: p["date"])
    if "beitraege" in schritte:
        m.beitraege(alle, kat, args.limit)
    if "seiten" in schritte:
        m.seiten(pages)
    eintraege = 0
    if "weiterleitungen" in schritte:
        extra = m.abweichungen(alle, kat, pages)  # immer über alle Beiträge, nie nur über die dieses Laufs
        antwort = m.weiterleitungen(redirect_csv("https://www.tamil.de", cats, pages, extra))
        eintraege = antwort.get("eintraege", 0)
        m.bericht["weiterleitungen_verworfen"] = antwort.get("verworfen", [])
    b = m.bericht
    b["unvollstaendig"] = sorted(m.unvollstaendig)
    b["fehlende_bilder"] = [{"url": u, "status": m.medien.status[u]} for u in sorted(m.fehlend) if u in m.medien.status]
    b["fehlende_bilder_404"] = sum(1 for f in b["fehlende_bilder"] if f["status"] == 404)
    b["dauer_sekunden"] = round(time.time() - start, 1)
    b["weiterleitungen_eintraege"] = eintraege
    b["bilder_von_alter_seite_geladen"] = m.medien.geladen
    b["doppelte_slugs_im_export"] = idempotenz_pruefen(posts)
    out = json.dumps(b, ensure_ascii=False, indent=1, default=dict)
    if args.bericht:
        args.bericht.write_text(out, encoding="utf-8")
    print(out)
    # Bilder, die auf der alten Seite da wären, aber nicht geholt wurden (429/5xx/Netz): Lauf wiederholen
    return 3 if any(ist_voruebergehend(f["status"]) for f in b["fehlende_bilder"]) else 0


if __name__ == "__main__":
    sys.exit(main())
