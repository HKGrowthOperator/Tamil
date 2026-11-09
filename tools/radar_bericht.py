"""Stand des Live-Radars aus GET /api/bericht als kurze Übersicht (nur lesen).

    RADAR_LESE_TOKEN=… python tools/radar_bericht.py [--url https://tamil.hk-growthoperator.de] [--tage 7] [--json]
    python tools/radar_bericht.py --token-datei /pfad/lese-token

Zeigt Gesundheit, Budget, Warteschlange, Entwürfe (Status, Typ, Titel, Hinweise), Storys je Status und Kosten. Der
Token wird nie ausgegeben.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path


def holen(url: str, token: str | None = None) -> dict:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.load(r)


def zusammenfassen(b: dict) -> str:
    z = []
    bud = b.get("budget") or {}
    z.append(f"Budget heute {bud.get('tag_usd', 0):.2f}/{bud.get('tag_limit', 0):.2f} $, Monat "
             f"{bud.get('monat_usd', 0):.2f}/{bud.get('monat_limit', 0):.2f} $"
             + ("  · STOPP" if bud.get("stopp") else "") + ("  · Warnung" if bud.get("warnung") else ""))
    z.append(f"Warteschlange: {json.dumps(b.get('warteschlange') or {}, ensure_ascii=False)}")
    storys = b.get("storys") or []
    z.append(f"Storys ({b.get('tage')} Tage): {len(storys)} · " + ", ".join(
        f"{k} {v}" for k, v in Counter(s.get("status") for s in storys).most_common()))
    entw = b.get("entwuerfe") or []
    z.append(f"Entwürfe: {len(entw)}")
    for d in entw:
        hin = d.get("hinweise") or ""
        hin = hin if isinstance(hin, str) else "; ".join(map(str, hin))
        z.append(f"  #{d.get('id')} [{d.get('status')}] {d.get('typ')}: {d.get('titel')}"
                 + (f"  · {d.get('event_datum')}" if d.get("event_datum") else "")
                 + (f"\n      Hinweise: {hin[:160]}" if hin else ""))
    kosten = b.get("kosten") or {}
    if kosten:
        z.append(f"Kosten: {json.dumps(kosten, ensure_ascii=False)[:400]}")
    return "\n".join(z)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--url", default=os.environ.get("RADAR_URL", "https://tamil.hk-growthoperator.de"))
    p.add_argument("--tage", type=int, default=7)
    p.add_argument("--token-datei")
    p.add_argument("--json", action="store_true", help="rohen Bericht ausgeben")
    a = p.parse_args(argv)
    token = Path(a.token_datei).read_text().strip() if a.token_datei else os.environ.get("RADAR_LESE_TOKEN")
    if not token:
        print("RADAR_LESE_TOKEN fehlt (oder --token-datei).", file=sys.stderr)
        return 2
    basis = a.url.rstrip("/")
    # Mit --json geht die Gesundheitszeile nach stderr, damit die Standardausgabe reines JSON bleibt.
    kanal = sys.stderr if a.json else sys.stdout
    try:
        gesund = holen(f"{basis}/gesund")
        print(f"Gesundheit: {json.dumps(gesund, ensure_ascii=False)[:300]}", file=kanal)
    except Exception as e:  # noqa: BLE001 – Übersicht soll trotzdem weiterlaufen
        print(f"Gesundheit: nicht erreichbar ({e})", file=kanal)
    bericht = holen(f"{basis}/api/bericht?tage={a.tage}", token)
    print(json.dumps(bericht, ensure_ascii=False, indent=2) if a.json else zusammenfassen(bericht))
    return 0


if __name__ == "__main__":
    sys.exit(main())
