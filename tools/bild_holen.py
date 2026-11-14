#!/usr/bin/env python3
"""Beitragsbilder der alten tamil.de in guter Auflösung holen (nur lesen) und verkleinert ablegen.

    python tools/bild_holen.py --out design/inhalte/bilder --breite 1600 9631 9655

Fragt über die öffentliche WordPress-Schnittstelle (wp-json, kein Login) das Beitragsbild ab, verkleinert es auf
höchstens --breite Pixel (vergrößert nie) und schreibt p<id>.jpg. bilder.json im Zielordner hält je Beitrag Maße,
Originalmaße und Quelle fest; weitere Läufe ergänzen die Datei. Die alte Seite wird dabei nie beschrieben.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

USER_AGENT = "TamilDE-Export/1.0 (+https://www.tamil.de)"
ERLAUBTE_HOSTS = ("tamil.de", "www.tamil.de")


def _json_holen(url: str) -> dict:
    import requests

    antwort = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, timeout=40)
    antwort.raise_for_status()
    return antwort.json()


def _bytes_holen(url: str) -> bytes:
    import requests

    antwort = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    antwort.raise_for_status()
    return antwort.content


def verkleinern(daten: bytes, breite: int) -> tuple[bytes, int, int, int, int]:
    """JPEG mit höchstens `breite` Pixeln Breite; gibt (Bytes, w, h, orig_w, orig_h) zurück. Vergrößert nie."""
    from PIL import Image

    with Image.open(io.BytesIO(daten)) as bild:
        bild = bild.convert("RGB")
        orig_w, orig_h = bild.size
        if orig_w > breite:
            bild = bild.resize((breite, round(orig_h * breite / orig_w)), Image.LANCZOS)
        puffer = io.BytesIO()
        bild.save(puffer, "JPEG", quality=86, optimize=True, progressive=True)
        return puffer.getvalue(), bild.size[0], bild.size[1], orig_w, orig_h


def holen(ids, ziel: Path, breite: int, site: str = "https://www.tamil.de", json_holen=_json_holen,
          bytes_holen=_bytes_holen) -> dict:
    """Holt die Beitragsbilder der genannten Beiträge. Rückgabe: {id: {datei, w, h, orig_w, orig_h, quelle}}."""
    ziel = Path(ziel)
    ziel.mkdir(parents=True, exist_ok=True)
    ergebnis = {}
    for nr in ids:
        beitrag = json_holen(f"{site.rstrip('/')}/wp-json/wp/v2/posts/{int(nr)}?_embed=wp:featuredmedia&_fields=id,_links,_embedded")
        medien = (beitrag.get("_embedded") or {}).get("wp:featuredmedia") or []
        quelle = (medien[0] or {}).get("source_url") if medien else None
        if not quelle:
            print(f"Beitrag {nr}: kein Beitragsbild", file=sys.stderr)
            continue
        teile = urlsplit(quelle)
        if teile.scheme != "https" or teile.hostname not in ERLAUBTE_HOSTS:
            raise ValueError(f"Beitrag {nr}: Bildadresse liegt nicht auf tamil.de ({teile.hostname})")
        daten, w, h, orig_w, orig_h = verkleinern(bytes_holen(quelle), breite)
        (ziel / f"p{int(nr)}.jpg").write_bytes(daten)
        ergebnis[str(int(nr))] = {"datei": f"p{int(nr)}.jpg", "w": w, "h": h, "orig_w": orig_w, "orig_h": orig_h,
                                  "quelle": quelle}
    liste = ziel / "bilder.json"
    gesamt = json.loads(liste.read_text(encoding="utf-8")) if liste.exists() else {}
    gesamt.update(ergebnis)
    liste.write_text(json.dumps(gesamt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ergebnis


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("ids", nargs="+", type=int, help="Beitragsnummern der alten Seite")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--breite", type=int, default=1600)
    p.add_argument("--site", default="https://www.tamil.de")
    a = p.parse_args(argv)
    ergebnis = holen(a.ids, a.out, a.breite, a.site)
    for nr, e in ergebnis.items():
        print(f"{nr}: {e['w']}×{e['h']} (Original {e['orig_w']}×{e['orig_h']})")
    return 0 if len(ergebnis) == len(a.ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
