#!/usr/bin/env python3
"""Migration des Altbestands von tamil.de in die neue Website (Plugin tamil-radar + tamil-site).

Liest den Export (tools/export_site.py: posts/pages/media/categories.json) und schreibt in die NEUE Website:
Beiträge mit Originaldatum und Original-Slug, Rubriken, Beitragsbild und Bilder im Text als Medien, Seiten und die
301-Tabelle. Die alte tamil.de wird nur gelesen (Bilder laden, falls nicht im Medien-Ordner). Idempotent: Beiträge
über radar_uid ``alt-<ID>`` (Seiten-Beiträge ``altseite-<ID>``), Seiten über den Slug, Medien im Text über den Slug.

    python tools/migration.py --export <ordner> --url https://<neue-website> --benutzer <admin> \\
        --passwort-datei <datei> [--trocken] [--limit 50] [--bericht bericht.json]

Passwort: aus der Datei (--passwort-datei) oder $MIGRATION_APP_PASSWORD; wird nie ausgegeben. Beispielwerte aus
prototyp/content/site.json (Telefon, E-Mail, WhatsApp) werden nie übernommen, sondern aus Texten entfernt und gemeldet.
"""

from __future__ import annotations

import argparse
import base64
import csv
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

import export_site  # noqa: E402  (Kategorien-/Seiten-Abbildung und Weiterleitungen: eine Quelle der Wahrheit)

NEUE_RUBRIKEN = ("news", "entertainment", "events", "community", "kueche", "kino", "sport", "kultur")
EXTRA_SCHLAGWORT = {"kritik": "Kritik", "anirudh": "Anirudh"}  # laut CATEGORY_MAP „+ Schlagwort …“
ALTE_HOSTS = ("tamil.de", "www.tamil.de")
UPLOAD_RE = re.compile(r"https?://(?:www\.)?tamil\.de/wp-content/uploads/([^\"'\s<>?#)]+)", re.I)
INTERN_RE = re.compile(r"""(href=["'])https?://(?:www\.)?tamil\.de(/[^"']*)?(["'])""", re.I)
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


def strip_beispielwerte(html: str, werte: list[str]) -> tuple[str, list[str]]:
    """Beispielwerte aus HTML entfernen; gibt (bereinigtes HTML, gefundene Werte) zurück."""
    gefunden = []
    for v in werte:
        for form in {v, v.replace(" ", "")}:
            if form and form in html:
                html = html.replace(form, "")
                if v not in gefunden:
                    gefunden.append(v)
    return html, gefunden


def upload_urls(html: str) -> list[str]:
    """Alle Adressen auf alte Uploads (Bilder, Dateien) in src/href, in Reihenfolge, ohne Doppelte."""
    seen: dict[str, None] = {}
    for m in UPLOAD_RE.finditer(html or ""):
        seen[m.group(0)] = None
    return list(seen)


def upload_dateiname(url: str) -> str:
    return Path(urlsplit(url).path).name


def rewrite_html(html: str, url_map: dict[str, str]) -> str:
    """Bildadressen auf die neue Website umschreiben, srcset/sizes (zeigen auf alte Größen) entfernen,
    interne Links relativ machen, YouTube-iframes als Embed-URL (kses des Plugins entfernt iframes)."""
    for alt, neu in sorted(url_map.items(), key=lambda kv: -len(kv[0])):
        html = html.replace(alt, neu)
        html = html.replace(alt.replace("https://", "http://", 1), neu)
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


# ---------------------------------------------------------------- Netz (alte Seite nur lesen, neue Seite schreiben)

class Medien:
    """Quelle der Bilder: Medien-Ordner des Exports, sonst lesend von der alten Seite (mit Pause, im Ordner zwischengelagert)."""

    def __init__(self, ordner: Path, pause: float = 0.25):
        self.ordner, self.pause = ordner, pause
        self.session = export_site.make_session()
        self.geladen = 0

    def holen(self, url: str) -> bytes | None:
        ziel = export_site.media_target(self.ordner.parent, url)
        if ziel.exists() and ziel.stat().st_size > 0:
            return ziel.read_bytes()
        try:
            r = self.session.get(re.sub(r"^http://", "https://", url), timeout=60)
            r.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            print(f"  Bild fehlt: {url} ({str(exc)[:80]})", file=sys.stderr)
            return None
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(r.content)
        self.geladen += 1
        time.sleep(self.pause)
        return r.content


class Migration:
    def __init__(self, wp, export: Path, medien: Medien, site_json: dict, trocken: bool = False):
        self.wp, self.export, self.medien, self.trocken = wp, export, medien, trocken
        self.werte = beispielwerte(site_json)
        self.bericht: dict = {
            "beitraege": Counter(), "seiten": Counter(), "medien": Counter(), "fehlende_bilder": [],
            "beispielwerte_gefunden": {}, "fremde_bilder": 0, "fremde_bilder_beitraege": [],
            "nicht_youtube_iframes": 0, "slug_abweichungen": [], "ohne_rubrik": [], "alt_text_fallback": 0,
            "bilder_unter_1200px": 0, "seiten_ohne_text": [],
        }
        self.media_by_id = {m["id"]: m for m in json.loads((export / "media.json").read_text(encoding="utf-8"))}
        self.media_by_url = {m["source_url"]: m for m in self.media_by_id.values()}

    # -- Medien im Text
    def text_medien(self, html: str) -> dict[str, str]:
        """Alte Upload-Adressen im Text als Medien der neuen Seite anlegen; gibt alt -> neu zurück."""
        mapping: dict[str, str] = {}
        for url in upload_urls(html):
            name = upload_dateiname(url)
            stem = re.sub(r"[^a-z0-9]+", "-", Path(name).stem.lower()).strip("-")
            code, found = self.wp.req("GET", "wp/v2/media", params={"slug": stem, "_fields": "id,source_url"})
            if code == 200 and found:
                mapping[url] = found[0]["source_url"]
                self.bericht["medien"]["vorhanden"] += 1
                continue
            daten = self.medien.holen(url)
            if daten is None:
                self.bericht["fehlende_bilder"].append(url)
                mapping[url] = re.sub(r"^http://", "https://", url)  # Altadresse bleibt, bis das Bild nachgeliefert ist
                continue
            if self.trocken:
                self.bericht["medien"]["neu"] += 1
                continue
            mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
            r = self.wp.http.post(f"{self.wp.url}/wp-json/wp/v2/media", data=daten, timeout=300,
                                  headers={"Content-Disposition": f'attachment; filename="{name}"', "Content-Type": mime})
            if r.status_code >= 400:
                self.bericht["fehlende_bilder"].append(url)
                mapping[url] = re.sub(r"^http://", "https://", url)
                continue
            mapping[url] = r.json()["source_url"]
            self.bericht["medien"]["neu"] += 1
        return mapping

    def inhalt(self, html: str, aus: str) -> str:
        html, gefunden = strip_beispielwerte(html, self.werte)
        for v in gefunden:
            self.bericht["beispielwerte_gefunden"].setdefault(v, []).append(aus)
        self.bericht["nicht_youtube_iframes"] += len(IFRAME_RE.findall(YT_IFRAME_RE.sub("", html)))
        fremd = fremde_bilder(html)
        if fremd:
            self.bericht["fremde_bilder"] += len(fremd)
            self.bericht["fremde_bilder_beitraege"].append(aus)
        return rewrite_html(html, self.text_medien(html))

    # -- Beiträge
    def beitragsbild(self, p: dict, titel: str) -> dict:
        m = self.media_by_id.get(p.get("featured_media"))
        if not m:
            return {}
        daten = self.medien.holen(m["source_url"])
        if daten is None:
            self.bericht["fehlende_bilder"].append(m["source_url"])
            return {}
        if (m.get("media_details") or {}).get("width", 9999) < 1200:
            self.bericht["bilder_unter_1200px"] += 1
        alt = m.get("alt_text") or ""
        if not alt:
            alt = titel
            self.bericht["alt_text_fallback"] += 1
        return {"daten": base64.b64encode(daten).decode("ascii"), "dateiname": upload_dateiname(m["source_url"]), "alt": alt, "credit": ""}

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
            return int(vorhanden.get("id") or 0)
        titel = text(p["title"]["rendered"]) if isinstance(p["title"], dict) else text(p["title"])
        payload = {
            "titel": titel,
            "inhalt": self.inhalt(p["content"]["rendered"], uid),
            "teaser": text((p.get("excerpt") or {}).get("rendered", "")),
            "status": "publish",
            "slug": p["slug"],
            "datum": p["date"].replace("T", " "),
            "kategorie": haupt,
            "kategorien": weitere,
            "schlagworte": extra,
            "meta": {"radar_uid": uid},
            "bild": {} if aus_seite else self.beitragsbild(p, titel),
        }
        if self.trocken:
            self.bericht["beitraege"]["neu (trocken)"] += 1
            return 0
        status, wp_id = self.wp.beitrag(payload)
        self.bericht["beitraege"][status] += 1
        if status == "neu":
            code, data = self.wp.req("GET", f"tamil-radar/v1/beitrag/{uid}")
            if code == 200 and data.get("slug") != p["slug"]:
                self.bericht["slug_abweichungen"].append((p["link"], data.get("link", ""), p["slug"], data.get("slug")))
        return wp_id

    def beitraege(self, posts: list[dict], kategorien: dict[int, str], tags: dict[int, str], limit: int = 0) -> list[tuple[str, str]]:
        extra_redirects: list[tuple[str, str]] = []
        for i, p in enumerate(posts):
            if limit and i >= limit:
                break
            slugs = [kategorien.get(c, str(c)) for c in p.get("categories", [])]
            self.beitrag(p, slugs)
        extra_redirects += [(alt, neu) for alt, neu, _, _ in self.bericht["slug_abweichungen"] if neu]
        return extra_redirects

    # -- Seiten
    def seite(self, slug: str, titel: str, inhalt: str, datum: str) -> None:
        code, data = self.wp.req("GET", "wp/v2/pages", params={"slug": slug, "status": "publish,draft", "context": "edit"})
        if code == 200 and data:
            roh = (data[0].get("content") or {}).get("raw", "").strip()
            if roh or not inhalt.strip() or self.trocken:
                self.bericht["seiten"]["vorhanden"] += 1
                return
            self.wp.req("POST", f"wp/v2/pages/{data[0]['id']}", json={"content": inhalt})
            self.bericht["seiten"]["gefüllt (war leer)"] += 1
            return
        if self.trocken:
            self.bericht["seiten"]["neu (trocken)"] += 1
            return
        code, data = self.wp.req("POST", "wp/v2/pages", json={"slug": slug, "title": titel, "content": inhalt, "status": "publish", "date": datum})
        if code >= 400:
            raise RuntimeError(f"Seite {slug}: {code} {str(data)[:300]}")
        self.bericht["seiten"]["neu"] += 1

    def seiten(self, pages: list[dict]) -> None:
        plan = seiten_plan(pages)
        for p in plan["seite"]:
            slug = p["slug"]
            neu = export_site.PAGE_MAP.get(slug, ("seite", slug))[1]
            html = self.inhalt(p["content"]["rendered"], f"seite-{slug}")
            if slug == "reporter" and html.strip():
                html = "<h2>Mitmachen: Leser-Reporter</h2>\n" + html
            if len(text(html).split()) < 25:
                self.bericht["seiten_ohne_text"].append(neu)
            self.seite(neu, text(p["title"]["rendered"]), html, p["date"].replace("T", " "))
        for p in plan["beitrag"]:
            self.beitrag(p, [], aus_seite=True, ziel_rubrik=export_site.PAGE_MAP[p["slug"]][1])
            self.bericht["seiten"]["als Beitrag"] += 1
        self.bericht["seiten"]["Weiterleitung (kein Inhalt)"] += len(plan["redirect"])
        self.bericht["seiten"]["Altlast nicht übernommen"] += len(plan["loeschen"])

    def weiterleitungen(self, csv_text: str) -> int:
        if self.trocken:
            return 0
        code, data = self.wp.req("POST", "tamil-site/v1/weiterleitungen", json={"csv": csv_text})
        if code >= 400:
            raise RuntimeError(f"Weiterleitungen: {code} {str(data)[:200]}")
        return int(data.get("eintraege", 0))


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
    ap.add_argument("--nur", choices=("beitraege", "seiten", "weiterleitungen"), action="append", help="Teilschritte (Standard: alle)")
    args = ap.parse_args(argv)

    pw = passwort(args.passwort_datei)
    if not (args.url and pw):
        print("Adresse (--url) und Passwort (--passwort-datei oder $MIGRATION_APP_PASSWORD) fehlen.")
        return 2
    host = urlsplit(args.url).netloc.split(":")[0]
    if host in ALTE_HOSTS and os.environ.get("MIGRATION_ZIEL_IST_NEU") != "1":
        print("Abbruch: Ziel ist die alte tamil.de-Adresse. Die alte Seite wird nie beschrieben.")
        return 2
    if args.url.startswith("http://") and host not in ("127.0.0.1", "localhost"):
        print("Hinweis: Anwendungspasswörter funktionieren nur über HTTPS.")

    export = args.export
    site_json = json.loads((REPO / "prototyp" / "content" / "site.json").read_text(encoding="utf-8"))
    posts = json.loads((export / "posts.json").read_text(encoding="utf-8"))
    pages = json.loads((export / "pages.json").read_text(encoding="utf-8"))
    cats = json.loads((export / "categories.json").read_text(encoding="utf-8"))
    kat = {c["id"]: c["slug"] for c in cats}
    schritte = set(args.nur or ("beitraege", "seiten", "weiterleitungen"))

    WP = _lade_wp_klasse()
    m = Migration(WP(args.url, args.benutzer, pw), export, Medien(args.medien or export / "media"), site_json, args.trocken)
    start = time.time()
    extra: list[tuple[str, str]] = []
    if "beitraege" in schritte:
        extra = m.beitraege(sorted(posts, key=lambda p: p["date"]), kat, {}, args.limit)
    if "seiten" in schritte:
        m.seiten(pages)
    eintraege = 0
    if "weiterleitungen" in schritte:
        eintraege = m.weiterleitungen(redirect_csv("https://www.tamil.de", cats, pages, extra))
    b = m.bericht
    b["dauer_sekunden"] = round(time.time() - start, 1)
    b["weiterleitungen_eintraege"] = eintraege
    b["bilder_von_alter_seite_geladen"] = m.medien.geladen
    b["doppelte_slugs_im_export"] = idempotenz_pruefen(posts)
    b["beispielwerte_geprueft"] = m.werte and ["Telefon", "E-Mail", "WhatsApp"]
    out = json.dumps(b, ensure_ascii=False, indent=1, default=dict)
    if args.bericht:
        args.bericht.write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
