"""CLI: python -m news_radar <befehl>

  run       Ein Lauf (für den systemd-Timer alle 3 Minuten); --max-age-hours 336 für die Erstbefüllung;
            --ohne-ki legt Rohfassungen ohne Claude an (Titel + Quellentext, klar markiert)
  loop      Dauerbetrieb, Lauf alle --interval Sekunden (Standard 180)
  scan      Nur einsammeln + filtern, nichts schreiben (Test der Quellen)
  publish   Alle freigegebenen Entwürfe nach WordPress veröffentlichen
  digest    Tageszusammenfassung senden (für den Digest-Timer)
  web       Freigabe-App lokal starten (Entwicklung; Produktion: gunicorn)
  style     Stilbeispiele aus veröffentlichten Tamil.de-Beiträgen lernen
  export    Protokoll als JSONL exportieren
  export-drafts  Entwürfe + Bilder für den HTML-Prototyp exportieren (--quellbilder lädt Vorschaubilder der Quellen)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import requests

from . import filtering, notify, pipeline, sources
from .config import load_settings
from .store import Store
from .writer import STYLE_FILE, RawWriter

KEY_HINT = ("ANTHROPIC_API_KEY fehlt – Schlüssel in .env oder als Secret setzen, "
            "oder `run --ohne-ki` für Rohfassungen ohne KI.")


def pick_writer(ohne_ki: bool, settings):
    """None = Standard-Writer (Claude) wird im Lauf gebaut; RawWriter bei --ohne-ki.

    Ohne Schlüssel und ohne --ohne-ki brechen wir mit Hinweis ab – ein stiller Fallback würde die
    Warteschlange im Betrieb unbemerkt mit Rohfassungen füllen.
    """
    if ohne_ki:
        return RawWriter(settings)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(KEY_HINT)
    return None


def cmd_style(site: str, count: int) -> int:
    resp = requests.get(
        f"{site.rstrip('/')}/wp-json/wp/v2/posts",
        params={"per_page": 30, "_fields": "title,content"},
        headers={"User-Agent": sources.USER_AGENT},
        timeout=20,
    )
    resp.raise_for_status()
    examples = []
    for post in resp.json():
        text = sources.clean_text(re.sub(r"</p>", "\n", post["content"]["rendered"]))
        text = re.sub(r"Share on:.*$", "", text).strip()
        words = len(text.split())
        if 150 <= words <= 700:
            examples.append({"title": sources.clean_text(post["title"]["rendered"]), "text": text[:2200]})
        if len(examples) >= count:
            break
    STYLE_FILE.write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(examples)} Stilbeispiele gespeichert in {STYLE_FILE}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="news_radar", description="Tamil.de News-Radar")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--max-age-hours", type=int, help="z. B. 336 für die Erstbefüllung (14 Tage)")
    run.add_argument("--ohne-ki", action="store_true", help="Rohfassungen ohne Claude (Titel + Quellentext, markiert)")
    loop = sub.add_parser("loop")
    loop.add_argument("--interval", type=int, default=180)
    loop.add_argument("--ohne-ki", action="store_true", help=argparse.SUPPRESS)
    expd = sub.add_parser("export-drafts")
    expd.add_argument("--file", default="prototyp/content/radar.json")
    expd.add_argument("--bilder", help="Zielordner für die Beitragsbilder (z. B. prototyp/static/img/radar)")
    expd.add_argument("--quellbilder", action="store_true", help="Vorschaubilder der Quellen laden (nur Prototyp)")
    expd.add_argument("--limit", type=int, default=60)
    sub.add_parser("scan")
    sub.add_parser("publish")
    sub.add_parser("digest")
    web = sub.add_parser("web")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8787)
    style = sub.add_parser("style")
    style.add_argument("--site", default="https://www.tamil.de")
    style.add_argument("--count", type=int, default=6)
    exp = sub.add_parser("export")
    exp.add_argument("--file", default="radar-protokoll.jsonl")
    pool = sub.add_parser("bildpool", help="Reserve-Bilder je Thema (prompts/bildpool.md)")
    pool.add_argument("aktion", choices=("status", "fuellen"))
    pool.add_argument("--thema", help="nur dieses Thema füllen")
    pool.add_argument("--anzahl", type=int, default=3, help="Zielbestand je Thema")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("httpx", "urllib3", "anthropic", "werkzeug"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    if args.cmd == "style":
        return cmd_style(args.site, args.count)

    settings = load_settings()

    if args.cmd == "scan":
        with Store(settings.db_path) as store:
            items = sources.fetch_all(settings, store)
            picked = filtering.select(items, settings, store.seen_uids(), store.recent_titles())
        print(f"\n{len(items)} gesammelt · {len(picked)} relevant\n")
        for i in picked[:40]:
            print(f"{i.score:3} {i.dach_score:2} {i.kind:5} {i.category_hint:13} {i.ort[:12]:12} {i.published:%d.%m %H:%M}  {i.title[:80]}")
        return 0

    if args.cmd == "export":
        with Store(settings.db_path) as store:
            n = store.export_log(Path(args.file))
        print(f"{n} Protokolleinträge → {args.file}")
        return 0

    if args.cmd == "bildpool":
        from .bilder import BildPool

        pool = BildPool(settings.bildpool_dir)
        if args.aktion == "fuellen":
            if not settings.gemini_key:
                raise SystemExit("GEMINI_API_KEY fehlt – ohne Bild-KI lässt sich der Pool nicht füllen.")
            erzeugt = pool.fuellen(settings, thema=args.thema, anzahl=args.anzahl)
            print(f"{sum(erzeugt.values())} Bilder erzeugt: " + (", ".join(f"{t} +{n}" for t, n in erzeugt.items()) or "nichts fehlte"))
        status = pool.status()
        print(f"Bildpool {settings.bildpool_dir}: {sum(s['anzahl'] for s in status.values())} Bilder in {len(status)} Themen")
        for thema, s in status.items():
            print(f"  {thema:20} {s['anzahl']:3} Bilder · {s['genutzt']:3}× genutzt")
        return 0

    if args.cmd == "export-drafts":
        from .export import export_drafts

        with Store(settings.db_path) as store:
            stats = export_drafts(store, Path(args.file), Path(args.bilder) if args.bilder else None,
                                  quellbilder=args.quellbilder, limit=args.limit, bilder_quelle=settings.bilder_dir)
        print(f"{stats['entwuerfe']} Entwürfe → {args.file} · {stats['quellbilder']} Quellbilder, "
              f"{stats['bildkarten']} Bildkarten, {stats['ohne_bild']} ohne Bild")
        return 0

    if args.cmd == "publish":
        if not settings.wordpress_enabled:
            print("Keine WordPress-Zugangsdaten in .env (WP_URL, WP_USER, WP_APP_PASSWORD).")
            return 1
        from .publisher import publish_approved

        with Store(settings.db_path) as store:
            print(pipeline.summary(publish_approved(settings, store, limit=50)))
        return 0

    if args.cmd == "digest":
        with Store(settings.db_path) as store:
            print(notify.digest(settings, store))
        return 0

    if args.cmd == "web":
        from .web import create_app

        create_app(settings).run(host=args.host, port=args.port, debug=args.verbose)
        return 0

    if not settings.wordpress_enabled:
        logging.info("Keine WordPress-Zugangsdaten → Entwürfe warten in der Freigabe-App (%s)", settings.web_url)

    writer = pick_writer(args.ohne_ki, settings)
    if writer is not None:
        logging.info("Rohfassungen ohne KI – jeder Entwurf wird als „Rohfassung“ markiert")

    if args.cmd == "run":
        if args.max_age_hours:
            settings.max_age_hours = args.max_age_hours
        print(pipeline.summary(pipeline.run(settings, writer=writer)))
        return 0

    while True:  # loop
        started = time.monotonic()
        try:
            print(pipeline.summary(pipeline.run(settings, writer=writer)), flush=True)
        except Exception:  # noqa: BLE001 - Dauerbetrieb nicht abbrechen
            logging.exception("Lauf fehlgeschlagen")
        time.sleep(max(5, args.interval - (time.monotonic() - started)))


if __name__ == "__main__":
    sys.exit(main())
