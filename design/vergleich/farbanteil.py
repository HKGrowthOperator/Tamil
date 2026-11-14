#!/usr/bin/env python3
"""Anteil bunter, roter und dunkler Pixel in einem Bildschirmfoto (für die Kennzahlen der Proben).

    python3 design/vergleich/farbanteil.py bild.png  →  {"bunt": 0.021, "rot": 0.018, "dunkel": 0.06}

Bunt heißt: Sättigung über 0,35 und Helligkeit über 0,2 (HSV). Rot heißt: bunt und Farbton nahe Rot. Dunkel heißt:
Helligkeit unter 0,3 (dunkle Bänder; Schrift fällt wegen der Verkleinerung kaum ins Gewicht).
Dieselbe Regel gilt für die Messung der Vorbilder in design/referenzen/news-marken.md.
"""
import json
import sys

from PIL import Image


def anteile(pfad: str) -> dict:
    with Image.open(pfad) as bild:
        bild = bild.convert("RGB")
        bild.thumbnail((640, 2000))
        roh = bild.convert("HSV").tobytes()
    hsv = [roh[i:i + 3] for i in range(0, len(roh), 3)]
    bunt = [p for p in hsv if p[1] > 0.35 * 255 and p[2] > 0.2 * 255]
    rot = [p for p in bunt if p[0] <= 14 or p[0] >= 244]  # Farbton 0–255; Rot liegt um 0
    dunkel = [p for p in hsv if p[2] < 0.3 * 255]
    n = len(hsv) or 1
    return {"bunt": round(len(bunt) / n, 4), "rot": round(len(rot) / n, 4), "dunkel": round(len(dunkel) / n, 4)}


if __name__ == "__main__":
    print(json.dumps(anteile(sys.argv[1])))
