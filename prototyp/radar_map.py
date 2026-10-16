"""DACH-Punktkarte für die Radar-Bühne: Länderumrisse (Natural-Earth-Vereinfachung) → Punktraster → SVG.

Die Karte ist das Leitmotiv des Prototyps: Punkte wie ein Kolam-Raster, darüber ein rotierender Radar-Sweep,
Blips an den Orten, an denen der News-Radar diese Woche etwas gefunden hat.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

GEO = Path(__file__).resolve().parent / "content" / "geo"
LON0, LON1, LAT0, LAT1 = 5.6, 17.4, 45.6, 55.2
COS = math.cos(math.radians(50.5))
STEP = 0.28  # Grad zwischen zwei Punkten


def _polygons(path: Path) -> list[list[tuple[float, float]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    polys = []
    for f in data["features"]:
        g = f["geometry"]
        rings = g["coordinates"] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
        if g["type"] == "Polygon":
            rings = [rings[0]]
        polys += [[(x, y) for x, y in r] for r in rings]
    return polys


def _inside(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    ok = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            ok = not ok
        j = i
    return ok


def project(lon: float, lat: float) -> tuple[float, float]:
    """Plattkarte mit Breitenkorrektur, Ausgabe in SVG-Einheiten (0–1000 breit)."""
    w = (LON1 - LON0) * COS
    x = (lon - LON0) * COS / w * 1000
    y = (LAT1 - lat) / w * 1000
    return round(x, 1), round(y, 1)


def viewbox() -> str:
    _, h = project(LON0, LAT0)
    return f"0 0 1000 {h:.0f}"


def dots(step: float = STEP) -> list[tuple[float, float, str]]:
    countries = {c: _polygons(GEO / f"{c}.geo.json") for c in ("DEU", "AUT", "CHE")}
    out = []
    lat = LAT0
    row = 0
    while lat <= LAT1:
        lon = LON0 + (step / 2 if row % 2 else 0)
        while lon <= LON1:
            for code, polys in countries.items():
                if any(_inside(lon, lat, p) for p in polys):
                    x, y = project(lon, lat)
                    out.append((x, y, code))
                    break
            lon += step
        lat += step * 0.86
        row += 1
    return out


def svg(orte: list[dict], sweep: bool = True) -> str:
    """Komplette Karte als Inline-SVG: Raster, Sweep, Blips mit Beschriftung (title) und Stagger-Index."""
    vb = viewbox()
    parts = [f'<svg class="radar-map" viewBox="{vb}" role="img" aria-label="Karte: Deutschland, Österreich, Schweiz mit den Orten, an denen der News-Radar diese Woche Meldungen gefunden hat">']
    parts.append('<g class="raster">')
    for x, y, code in dots():
        parts.append(f'<circle cx="{x}" cy="{y}" r="3.2" data-l="{code[:2]}"/>')
    parts.append("</g>")
    if sweep:
        cx, cy = project(10.6, 50.3)
        parts.append(f'<g class="sweep" style="transform-origin:{cx}px {cy}px"><path d="M{cx} {cy} L{cx + 900} {cy - 520} A1040 1040 0 0 1 {cx + 1040} {cy}Z"/></g>')
    parts.append('<g class="blips">')
    for i, o in enumerate(orte):
        x, y = project(o["lon"], o["lat"])
        parts.append(f'<g class="blip {o.get("art", "news")}" style="--i:{i}" transform="translate({x} {y})"><title>{o["name"]}: {o.get("label", "")}</title>'
                     f'<circle class="ring" r="18"/><circle class="dot" r="6"/></g>')
    parts.append("</g></svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    import sys
    orte = [{"name": "Bremen", "lat": 53.08, "lon": 8.80, "art": "kino"}, {"name": "Wien", "lat": 48.21, "lon": 16.37, "art": "kino"}, {"name": "Basel", "lat": 47.56, "lon": 7.59, "art": "event"}]
    out = svg(orte)
    print(f"{len(dots())} Punkte, {len(out)} Zeichen", file=sys.stderr)
    print(out)
