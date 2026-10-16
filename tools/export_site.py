#!/usr/bin/env python3
"""Export der öffentlichen Inhalte von tamil.de über die WordPress-REST-API (kein Login nötig).

    python tools/export_site.py --site https://www.tamil.de --out export/

Schreibt posts/pages/media/categories/tags.json, lädt alle Medien nach export/media/<jahr>/<monat>/,
erzeugt inventory.csv (Inhaltsinventar) und redirects.csv (301-Tabelle für den Kategorien-Umzug).
Vertrag Pos. A.2.7 (Datenmigration) – läuft ohne Zugang zum alten WordPress.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = "TamilDE-Export/1.0 (+https://www.tamil.de)"
POST_FIELDS = "id,date,modified,slug,link,status,title,content,excerpt,author,featured_media,categories,tags,comment_status"
PAGE_FIELDS = "id,date,modified,slug,link,status,title,content,parent"
MEDIA_FIELDS = "id,date,slug,link,source_url,mime_type,media_details,alt_text,title,post"

# Alte Kategorie (Slug) -> (neuer Slug, Hinweis). None = löschen.
CATEGORY_MAP = {
    "news": ("news", "Nachrichten (Slug bleibt)"),
    "entertainment": ("entertainment", "bleibt"),
    "media": ("kino", "einzeln prüfen: Kino oder Entertainment"),
    "blog": ("community", "Community"),
    "kritik": ("kino", "+ Schlagwort „Kritik“"),
    "anirudh": ("events", "+ Schlagwort „Anirudh“"),
    "kueche": ("kueche", "bleibt"),
    "production": ("kino", "Kino"),
    "test": (None, "löschen"),
    "turniere": ("sport", "Sport"),
}
DELETE_PAGE_SLUGS = {"backup", "backup-2te-week-dc", "fb", "register", "login", "account", "members", "user",
                     "password-reset", "logout", "gd-home", "location", "gd-login"}
_HTTP_IMG_RE = re.compile(r"<img[^>]+src=[\"']http://", re.I)
_YT_RE = re.compile(r"youtube\.com/embed|youtu\.be/|youtube\.com/watch", re.I)
_TAG_RE = re.compile(r"<[^>]+>")


def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=1.5, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET",))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = USER_AGENT
    return s


def paged(session: requests.Session, url: str, pause: float = 0.1, **params):
    """Alle Seiten eines REST-Endpunkts (per_page=100, stoppt bei X-WP-TotalPages)."""
    page = 1
    while True:
        resp = session.get(url, params={"per_page": 100, "page": page, **params}, timeout=60)
        resp.raise_for_status()
        batch = resp.json()
        yield from batch
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1) or 1)
        if page >= total_pages or not batch:
            return
        page += 1
        time.sleep(pause)


def rendered(obj: dict, key: str) -> str:
    val = obj.get(key)
    return val.get("rendered", "") if isinstance(val, dict) else (val or "")


def word_count(html: str) -> int:
    return len(_TAG_RE.sub(" ", html or "").split())


def media_target(out: Path, source_url: str) -> Path:
    """Spiegelt den Upload-Pfad (uploads/JJJJ/MM/datei) – so bleibt die 301-Tabelle für Bilder trivial."""
    path = urlsplit(source_url).path
    m = re.search(r"/uploads/(\d{4})/(\d{2})/([^/]+)$", path)
    if m:
        return out / "media" / m.group(1) / m.group(2) / m.group(3)
    return out / "media" / "sonstige" / (Path(path).name or "datei")


def download_media(session: requests.Session, media: list[dict], out: Path, workers: int = 4) -> tuple[int, int]:
    """Lädt alle Medien (überspringt vorhandene); gibt (geladen, fehlgeschlagen) zurück."""
    todo = [(m["source_url"], media_target(out, m["source_url"])) for m in media if m.get("source_url")]

    def one(job):
        url, target = job
        if target.exists() and target.stat().st_size > 0:
            return True
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            resp = session.get(url, timeout=60)
            resp.raise_for_status()
            target.write_bytes(resp.content)
            return True
        except Exception as exc:  # noqa: BLE001
            print(f"  Medium fehlgeschlagen: {url} ({exc})", file=sys.stderr)
            return False

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(one, todo))
    return sum(results), len(results) - sum(results)


def inventory_rows(posts: list[dict], categories: list[dict], tags: list[dict], media: list[dict]) -> list[dict]:
    cat_by_id = {c["id"]: c for c in categories}
    tag_by_id = {t["id"]: t["name"] for t in tags}
    media_ids = {m["id"] for m in media}
    rows = []
    for p in posts:
        content = rendered(p, "content")
        cats = [cat_by_id.get(c, {}).get("slug", str(c)) for c in p.get("categories", [])]
        targets = {CATEGORY_MAP.get(c, (c, ""))[0] for c in cats}
        targets.discard(None)
        rows.append({
            "id": p["id"], "datum": (p.get("date") or "")[:10], "titel": _TAG_RE.sub("", rendered(p, "title")).strip(),
            "slug": p.get("slug", ""), "link": p.get("link", ""), "kategorien": "|".join(cats),
            "neue_kategorie": "|".join(sorted(targets)) or "löschen",
            "schlagworte": "|".join(tag_by_id.get(t, str(t)) for t in p.get("tags", [])),
            "woerter": word_count(content), "beitragsbild": "ja" if p.get("featured_media") in media_ids else "nein",
            "http_bilder": len(_HTTP_IMG_RE.findall(content)), "youtube": len(_YT_RE.findall(content)),
            "empfehlung": "löschen" if "test" in cats else ("prüfen" if word_count(content) < 80 or _HTTP_IMG_RE.search(content) else "übernehmen"),
        })
    return rows


def redirect_rows(site: str, categories: list[dict], pages: list[dict]) -> list[dict]:
    rows = []
    for c in categories:
        new, note = CATEGORY_MAP.get(c["slug"], (c["slug"], "neu anlegen/prüfen"))
        rows.append({"alt": f"{site}/category/{c['slug']}/", "neu": f"{site}/{new}/" if new else f"{site}/", "typ": "kategorie",
                     "beitraege": c.get("count", 0), "hinweis": note})
    for p in pages:
        if p.get("slug") in DELETE_PAGE_SLUGS:
            rows.append({"alt": p.get("link", f"{site}/{p['slug']}/"), "neu": f"{site}/", "typ": "seite", "beitraege": "", "hinweis": "Altlast löschen"})
    rows.append({"alt": f"{site}/category/anirudh/", "neu": f"{site}/events/", "typ": "menue", "beitraege": "", "hinweis": "EVENTS-Menüpunkt zeigt heute auf diese Kategorie"})
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def export(site: str, out: Path, with_media: bool = True, workers: int = 4, session: requests.Session | None = None) -> dict:
    session = session or make_session()
    out.mkdir(parents=True, exist_ok=True)
    api = f"{site.rstrip('/')}/wp-json/wp/v2"
    report: dict = {}

    def dump(name: str, items: list[dict]) -> list[dict]:
        (out / f"{name}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        report[name] = len(items)
        print(f"{name}: {len(items)}")
        return items

    posts = dump("posts", list(paged(session, f"{api}/posts", _fields=POST_FIELDS, status="publish")))
    pages = dump("pages", list(paged(session, f"{api}/pages", _fields=PAGE_FIELDS)))
    categories = dump("categories", list(paged(session, f"{api}/categories", _fields="id,name,slug,count,parent")))
    tags = dump("tags", list(paged(session, f"{api}/tags", _fields="id,name,slug,count")))
    media = dump("media", list(paged(session, f"{api}/media", _fields=MEDIA_FIELDS)))

    head = session.get(f"{api}/posts", params={"per_page": 1, "_fields": "id"}, timeout=60)
    report["posts_total_laut_api"] = int(head.headers.get("X-WP-Total", 0) or 0)

    if with_media:
        ok, failed = download_media(session, media, out, workers)
        report["media_geladen"], report["media_fehlgeschlagen"] = ok, failed
        print(f"Medien: {ok} geladen, {failed} fehlgeschlagen")

    inv = inventory_rows(posts, categories, tags, media)
    write_csv(out / "inventory.csv", inv)
    write_csv(out / "redirects.csv", redirect_rows(site.rstrip("/"), categories, pages))
    report["inventar"] = {
        "beitraege": len(inv),
        "empfehlung": {k: sum(1 for r in inv if r["empfehlung"] == k) for k in ("übernehmen", "prüfen", "löschen")},
        "http_bilder_posts": sum(1 for r in inv if r["http_bilder"]),
        "ohne_beitragsbild": sum(1 for r in inv if r["beitragsbild"] == "nein"),
        "youtube_posts": sum(1 for r in inv if r["youtube"]),
    }
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="tamil.de über die REST-API exportieren")
    parser.add_argument("--site", default="https://www.tamil.de")
    parser.add_argument("--out", default="export", type=Path)
    parser.add_argument("--no-media", action="store_true", help="Medien nicht herunterladen")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args(argv)
    report = export(args.site, args.out, with_media=not args.no_media, workers=args.workers)
    ok = report["posts"] == report["posts_total_laut_api"]
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("Prüfung Beitragszahl:", "OK" if ok else f"ABWEICHUNG ({report['posts']} ≠ {report['posts_total_laut_api']})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
