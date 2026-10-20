"""Screenshots des lokalen WordPress (Theme + Backend) in 390, 820 und 1280 px – mit Prüfung auf horizontales Scrollen.

    set -a; . "$WP_DIR/.env.local"; set +a
    python wordpress/dev/shots.py --out "$WP_DIR/shots" [--only start] [--widths 390,1280] [--ohne-admin]

Die Seiten werden per REST gesucht (Aufmacher, Rezept, Kinoliste, Termin, Rubriken, Seiten). Für das Backend meldet
sich das Skript mit WP_ADMIN_USER/WP_ADMIN_PASSWORD an (Dashboard mit Radar-Widget, Plugin-Seiten, Beitragseditor).
Rückgabewert 1, wenn eine Seite horizontal scrollt.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

CHROMIUM = Path("/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
WIDTHS = (390, 820, 1280)


def take_shots(pages: list[tuple[str, str]], out: Path, widths=WIDTHS, login: tuple[str, str, str] | None = None) -> tuple[list[Path], list[str]]:
    """pages: (Name, URL). login: (Anmelde-URL, Benutzer, Passwort) für Seiten unter /wp-admin/."""
    from playwright.sync_api import sync_playwright

    out.mkdir(parents=True, exist_ok=True)
    files, warnungen = [], []
    with sync_playwright() as pw:
        kwargs = {"args": ["--no-sandbox"]}
        if CHROMIUM.exists():
            kwargs["executable_path"] = str(CHROMIUM)
        browser = pw.chromium.launch(**kwargs)
        for width in widths:
            ctx = browser.new_context(viewport={"width": width, "height": 900}, device_scale_factor=1, locale="de-DE")
            page = ctx.new_page()
            angemeldet = False
            for name, url in pages:
                if "/wp-admin" in url and login and not angemeldet:
                    page.goto(login[0])
                    page.fill("#user_login", login[1])
                    page.fill("#user_pass", login[2])
                    page.click("#wp-submit")
                    page.wait_for_load_state("networkidle")
                    angemeldet = True
                page.goto(url, wait_until="networkidle")
                if "/wp-admin" not in url:
                    # Durchscrollen lädt die verzögerten Bilder (sizes="auto") und startet die Zähler
                    page.evaluate("""async () => { const h = document.body.scrollHeight; for (let y = 0; y < h; y += 400) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } }""")
                    page.wait_for_function("[...document.images].every(i => i.complete && (i.naturalWidth > 0 || !i.currentSrc))", timeout=30000)
                    page.wait_for_timeout(600)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(500)
                    if name == "start" and width <= 600:
                        target = out / f"start-{width}-viewport.png"
                        page.screenshot(path=str(target), full_page=False)
                        files.append(target)
                    page.evaluate("document.querySelectorAll('#ad-mobile, .fab-wa').forEach(e => e.remove())")
                target = out / f"{name}-{width}.png"
                page.screenshot(path=str(target), full_page=True)
                files.append(target)
                scroll_w = page.evaluate("document.documentElement.scrollWidth")
                if scroll_w > width and "/wp-admin" not in url:
                    warnungen.append(f"{name} @{width}: horizontal scrollbar ({scroll_w}px)")
            ctx.close()
        browser.close()
    return files, warnungen


def seiten_finden(url: str) -> list[tuple[str, str]]:
    api = url.rstrip("/") + "/wp-json/wp/v2"

    def erster(path: str, **params) -> str:
        r = requests.get(f"{api}/{path}", params={"per_page": 1, "_fields": "link", **params}, timeout=30)
        data = r.json() if r.ok else []
        return data[0]["link"] if data else ""

    def kategorie(slug: str) -> int:
        r = requests.get(f"{api}/categories", params={"slug": slug, "_fields": "id"}, timeout=30)
        return r.json()[0]["id"] if r.ok and r.json() else 0

    pages = [("start", url.rstrip("/") + "/")]
    for slug in ("kino", "news"):
        cat = kategorie(slug)
        if cat:
            pages.append((f"rubrik-{slug}", requests.get(f"{api}/categories/{cat}", timeout=30).json()["link"]))
    pages += [
        ("artikel", erster("posts", sticky="true")),
        ("rezept", erster("posts", categories=kategorie("kueche"))),
        ("kinoliste", erster("posts", search="läuft in")),
        ("termin", erster("posts", categories=kategorie("events"))),
        ("events", erster("pages", slug="events")),
        ("kontakt", erster("pages", slug="kontakt")),
        ("production", erster("pages", slug="production")),
        ("suche", url.rstrip("/") + "/?s=Kino"),
        ("404", url.rstrip("/") + "/gibt-es-nicht/"),
    ]
    return [(n, u) for n, u in pages if u]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=Path(os.environ.get("WP_SHOTS_DIR", "wordpress-shots")))
    ap.add_argument("--only", default="")
    ap.add_argument("--widths", default=",".join(map(str, WIDTHS)))
    ap.add_argument("--ohne-admin", action="store_true")
    args = ap.parse_args()
    url = os.environ.get("WP_URL", "http://127.0.0.1:8085")
    pages = seiten_finden(url)
    login = None
    user, pw = os.environ.get("WP_ADMIN_USER", ""), os.environ.get("WP_ADMIN_PASSWORD", "")
    if not args.ohne_admin and user and pw:
        admin = url.rstrip("/") + "/wp-admin/"
        pages += [("admin-dashboard", admin), ("admin-radar", admin + "admin.php?page=tamil-radar-einstellungen"),
                  ("admin-website", admin + "options-general.php?page=tamil-site"), ("admin-beitraege", admin + "edit.php")]
        login = (url.rstrip("/") + "/wp-login.php", user, pw)
    if args.only:
        pages = [p for p in pages if args.only in p[0]]
    widths = tuple(int(w) for w in args.widths.split(","))
    files, warnungen = take_shots(pages, args.out, widths, login)
    for w in warnungen:
        print("WARNUNG", w, file=sys.stderr)
    print(f"{len(files)} Screenshots in {args.out}")
    return 1 if warnungen else 0


if __name__ == "__main__":
    sys.exit(main())
