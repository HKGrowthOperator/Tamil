"""Blindbewertung im Pilot: Sonnet und Opus schreiben dieselben Storys, die Redaktion bewertet ohne zu wissen, welches
Modell welchen Text geschrieben hat.

  python -m news_radar bewertung vergleich --anzahl 10      (braucht ANTHROPIC_API_KEY; kostet ca. 10 × 2 Textaufrufe)
  → data/bewertung/bogen.csv   (Texte A/B in zufälliger Reihenfolge, Spalten für Noten und Kommentar)
  → data/bewertung/schluessel.json   (welcher Buchstabe welches Modell – erst nach der Bewertung öffnen)
  python -m news_radar bewertung auswerten --bogen data/bewertung/bogen.csv

Grundlage sind fertige Storys der Redaktion v2: dieselben bestätigten Claims, dieselbe Längenregel, nur das Modell der
Text-Rolle wechselt. Die Kosten beider Fassungen landen wie jeder Aufruf in agent_usage.
"""

from __future__ import annotations

import csv
import json
import random
import re
from pathlib import Path

from .agents import Kontext, schreiben
from .config import Settings
from .store import Store
from .workflow import repo

SPALTEN = ("nr", "story_id", "fassung", "titel", "teaser", "text", "richtigkeit_1_5", "stil_1_5", "verstaendlichkeit_1_5",
           "laenge_passt_ja_nein", "wuerde_freigeben_ja_nein", "kommentar")


def _klartext(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def vergleich(ctx: Kontext, ordner: Path, anzahl: int = 10, modelle: tuple[str, str] = ("claude-sonnet-5-5", "claude-opus-5-5"),
              seed: int | None = None) -> dict:
    store = ctx.store
    storys = [s for s in repo.stories(store, "fertig", limit=200) if s["typ"] in ("news", "event")][:anzahl]
    rnd = random.Random(seed)
    zeilen, schluessel = [], {}
    for nr, story in enumerate(storys, 1):
        claims = repo.claims(store, story["id"])
        docs = repo.dokumente(store, story["id"])
        fassungen = []
        for modell in modelle:
            ctx.settings.modelle["text"] = modell
            text = schreiben.schreiben(ctx, story, claims, docs, story.get("laenge") or "normal")
            fassungen.append((modell, text))
        rnd.shuffle(fassungen)
        for buchstabe, (modell, text) in zip("AB", fassungen):
            schluessel[f"{nr}{buchstabe}"] = modell
            zeilen.append({"nr": nr, "story_id": story["id"], "fassung": buchstabe, "titel": text.titel,
                           "teaser": text.teaser, "text": _klartext(text.inhalt_html), "richtigkeit_1_5": "",
                           "stil_1_5": "", "verstaendlichkeit_1_5": "", "laenge_passt_ja_nein": "",
                           "wuerde_freigeben_ja_nein": "", "kommentar": ""})
    ordner.mkdir(parents=True, exist_ok=True)
    with (ordner / "bogen.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=SPALTEN, delimiter=";")
        w.writeheader()
        w.writerows(zeilen)
    (ordner / "schluessel.json").write_text(json.dumps(schluessel, indent=1), encoding="utf-8")
    return {"storys": len(storys), "fassungen": len(zeilen), "bogen": ordner / "bogen.csv"}


def auswerten(bogen: Path, schluessel: Path) -> dict:
    zuordnung = json.loads(schluessel.read_text(encoding="utf-8"))
    summen: dict[str, dict[str, float]] = {}
    with bogen.open(encoding="utf-8-sig") as fh:
        for z in csv.DictReader(fh, delimiter=";"):
            modell = zuordnung.get(f"{z['nr']}{z['fassung']}", "?")
            s = summen.setdefault(modell, {"n": 0, "richtigkeit": 0, "stil": 0, "verstaendlichkeit": 0, "freigabe": 0})
            try:
                s["richtigkeit"] += float(z["richtigkeit_1_5"] or 0)
                s["stil"] += float(z["stil_1_5"] or 0)
                s["verstaendlichkeit"] += float(z["verstaendlichkeit_1_5"] or 0)
            except ValueError:
                continue
            s["freigabe"] += 1 if (z["wuerde_freigeben_ja_nein"] or "").strip().lower().startswith("j") else 0
            s["n"] += 1
    return {m: {k: round(v / s["n"], 2) if k != "n" and s["n"] else v for k, v in s.items()} for m, s in summen.items()}


def bogen_aus_entwuerfen(store: Store, settings: Settings, ordner: Path, anzahl: int = 10) -> Path:
    """Bewertungsbogen ohne Modellvergleich: die letzten Entwürfe der Redaktion v2 zum Benoten (z. B. ohne Schlüssel)."""
    zeilen = []
    for nr, d in enumerate([d for d in store.list_drafts(limit=200) if d.get("story_id")][:anzahl], 1):
        zeilen.append({"nr": nr, "story_id": d["story_id"], "fassung": "A", "titel": d["titel"], "teaser": d["teaser"],
                       "text": _klartext(d["inhalt_html"]), "richtigkeit_1_5": "", "stil_1_5": "",
                       "verstaendlichkeit_1_5": "", "laenge_passt_ja_nein": "", "wuerde_freigeben_ja_nein": "",
                       "kommentar": ""})
    ordner.mkdir(parents=True, exist_ok=True)
    pfad = ordner / "bogen-entwuerfe.csv"
    with pfad.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=SPALTEN, delimiter=";")
        w.writeheader()
        w.writerows(zeilen)
    return pfad
