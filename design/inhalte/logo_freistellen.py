#!/usr/bin/env python3
"""Neues Logo tamil.de (Luis, 20.11.2026) freistellen: weißen Grund entfernen, nichts neu zeichnen.

Quelle: `design/inhalte/logo-2026-11.webp` (1969 × 799, RGB, weißer Grund). Luis: „genau so übernehmen“, auch die
Schreibweise der Zeilen „portal • lifestyle • entertainment“ und „& KOMMUNITYPLATTFORM DER COMMUNITY“.

Verfahren (je Bildpunkt, ohne Neuzeichnen): Die Quelle besteht aus zwei Druckfarben auf Weiß, dem Rot von „tamil“ und
dem Dunkelgrau von „.de“ und den Zeilen darunter. Jeder Punkt liegt auf der Strecke zwischen Weiß und einer der beiden
Farben; die Lage auf dieser Strecke ist seine Deckkraft (so entstehen die geglätteten Kanten). Punkte, die voll decken,
behalten ihre Farbe aus der Quelle unverändert; Kantenpunkte bekommen die Druckfarbe mit ihrer Deckkraft und sehen auf
Weiß genau wie vorher aus. Reste des Grunds (Kompressionsrauschen unter 6 % Deckkraft) werden durchsichtig. Danach wird
auf die Schrift zugeschnitten (ohne Rand) und mit vormultipliziertem Alpha verkleinert (keine dunklen Säume).

    python3 design/inhalte/logo_freistellen.py

Schreibt:
    design/inhalte/logo.png                          volle Auflösung, freigestellt (Social-Karten, Druckvorlagen)
    wordpress/themes/tamil/assets/img/logo.webp      Kopf 1x (72 px hoch)
    wordpress/themes/tamil/assets/img/logo-2x.webp   Kopf 2x (144 px hoch)
    wordpress/themes/tamil/assets/img/logo.png       144 px hoch (Schema, Teilen, Rückfall)
"""

from __future__ import annotations

import os

import numpy as np
from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.abspath(os.path.join(HIER, "..", ".."))
QUELLE = os.path.join(HIER, "logo-2026-11.webp")
THEME = os.path.join(WURZEL, "wordpress", "themes", "tamil", "assets", "img")
KOPF = 72            # Höhe im Kopf am Desktop (CSS: 56 / 64 / 72 px)
SCHWELLE = 0.06      # darunter ist es Rauschen des weißen Grunds
VOLL = 0.97          # darüber deckt der Punkt voll und behält seine Farbe


def druckfarben(rgb: np.ndarray) -> list[np.ndarray]:
    """Rot und Grau aus der Quelle selbst: Median der kräftigen Punkte je Farbe."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    rot = rgb[(r - g > 60) & (r < 160)]
    grau = rgb[(np.abs(r - g) < 12) & (np.abs(g - b) < 12) & (rgb.max(axis=2) < 90)]
    return [np.median(rot, axis=0), np.median(grau, axis=0)]


def freistellen(rgb: np.ndarray) -> np.ndarray:
    weiss = np.array([255.0, 255.0, 255.0])
    farben = druckfarben(rgb)
    d = weiss - rgb                                   # Abstand vom Weiß je Punkt
    beste_a = None
    beste_rest = None
    beste_k = None
    for k, farbe in enumerate(farben):
        v = weiss - farbe
        a = np.clip((d @ v) / (v @ v), 0.0, 1.0)      # Lage auf der Strecke Weiß → Druckfarbe
        rest = np.linalg.norm(d - a[..., None] * v, axis=-1)
        if beste_a is None:
            beste_a, beste_rest, beste_k = a, rest, np.zeros(a.shape, dtype=int)
        else:
            besser = rest < beste_rest
            beste_a = np.where(besser, a, beste_a)
            beste_rest = np.where(besser, rest, beste_rest)
            beste_k = np.where(besser, k, beste_k)
    alpha = np.where(beste_a < SCHWELLE, 0.0, beste_a)
    farbe = np.stack([farben[0], farben[1]])[beste_k]
    voll = alpha >= VOLL
    farbe = np.where(voll[..., None], rgb, farbe)     # voll deckende Punkte: Farbe der Quelle unverändert
    alpha = np.where(voll, 1.0, alpha)
    out = np.dstack([farbe, alpha * 255.0])
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


def zuschnitt(rgba: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(rgba[..., 3])
    return rgba[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]


def verkleinert(bild: Image.Image, hoehe: int) -> Image.Image:
    breite = round(bild.width * hoehe / bild.height)
    return bild.convert("RGBa").resize((breite, hoehe), Image.LANCZOS).convert("RGBA")


def main() -> None:
    rgb = np.asarray(Image.open(QUELLE).convert("RGB")).astype(float)
    gross = Image.fromarray(zuschnitt(freistellen(rgb)), "RGBA")
    gross.save(os.path.join(HIER, "logo.png"), optimize=True)
    eins = verkleinert(gross, KOPF)
    zwei = verkleinert(gross, 2 * KOPF)
    eins.save(os.path.join(THEME, "logo.webp"), lossless=True, method=6)
    zwei.save(os.path.join(THEME, "logo-2x.webp"), lossless=True, method=6)
    zwei.save(os.path.join(THEME, "logo.png"), optimize=True)
    for name, b in (("design/inhalte/logo.png", gross), ("logo.webp", eins), ("logo-2x.webp", zwei), ("logo.png", zwei)):
        pfad = os.path.join(HIER, "logo.png") if name.startswith("design") else os.path.join(THEME, name)
        print(f"{name:26} {b.width} × {b.height}  {os.path.getsize(pfad) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
