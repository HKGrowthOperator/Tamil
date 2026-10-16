"""CLI: python -m news_radar <befehl>

  run       Ein Lauf (für cron / systemd-Timer alle 5 Minuten)
  loop      Dauerbetrieb, Lauf alle --interval Sekunden (Standard 300)
  scan      Nur einsammeln + filtern, nichts schreiben (Test der Quellen)
  style     Stilbeispiele aus veröffentlichten Tamil.de-Beiträgen lernen
  export    Protokoll als JSONL exportieren
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

import requests

from . import filtering, pipeline, sources
from .config import load_settings
from .store import Store
from .writer import STYLE_FILE


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
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    loop = sub.add_parser("loop")
    loop.add_argument("--interval", type=int, default=300)
    sub.add_parser("scan")
    style = sub.add_parser("style")
    style.add_argument("--site", default="https://www.tamil.de")
    style.add_argument("--count", type=int, default=6)
    exp = sub.add_parser("export")
    exp.add_argument("--file", default="radar-protokoll.jsonl")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("httpx", "urllib3", "anthropic"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    if args.cmd == "style":
        return cmd_style(args.site, args.count)

    settings = load_settings()

    if args.cmd == "scan":
        store = Store(settings.data_dir / "radar.sqlite")
        items = sources.fetch_all(settings)
        picked = filtering.select(items, settings, store.seen_uids(), store.recent_titles())
        print(f"\n{len(items)} gesammelt · {len(picked)} relevant\n")
        for i in picked[:30]:
            print(f"{i.score:3}  {i.category_hint:13} {i.published:%d.%m %H:%M}  {i.title[:90]}")
        return 0

    if args.cmd == "export":
        n = Store(settings.data_dir / "radar.sqlite").export_log(Path(args.file))
        print(f"{n} Protokolleinträge → {args.file}")
        return 0

    if not settings.wordpress_enabled:
        logging.info("Keine WordPress-Zugangsdaten → Dry-Run, Entwürfe landen in %s", settings.out_dir)

    if args.cmd == "run":
        print(pipeline.summary(pipeline.run(settings)))
        return 0

    while True:  # loop
        started = time.monotonic()
        try:
            print(pipeline.summary(pipeline.run(settings)), flush=True)
        except Exception:  # noqa: BLE001 - Dauerbetrieb nicht abbrechen
            logging.exception("Lauf fehlgeschlagen")
        time.sleep(max(5, args.interval - (time.monotonic() - started)))


if __name__ == "__main__":
    sys.exit(main())
