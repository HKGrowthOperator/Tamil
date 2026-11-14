#!/usr/bin/env python3
"""Kontrast heller Schrift auf Bildern und dunklen Flächen, gemessen am Bildschirmfoto.

    python3 design/vergleich/kontrast.py seite-ohne-schrift.png texte.json 2

`seite-ohne-schrift.png` ist die ganze Seite mit durchsichtig gestellter Schrift, `texte.json` eine Liste
{x, y, w, h, hell, px, fett, text} in CSS-Pixeln der Seite (hell = relative Leuchtdichte der Schriftfarbe), die Zahl
ist die Pixeldichte der Aufnahme. Gerechnet wird gegen die hellste Stelle unter der Schrift (95. Perzentil), also der
ungünstigste Fall: (hell + 0,05) / (Grund + 0,05) nach WCAG. Ausgabe: je Text das Verhältnis, schlechtestes zuerst.
"""
import json
import sys

from PIL import Image


def leuchtdichte(r: int, g: int, b: int) -> float:
    def kanal(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * kanal(r) + 0.7152 * kanal(g) + 0.0722 * kanal(b)


def messen(bild_pfad: str, texte: list, dichte: float) -> list:
    ergebnis = []
    with Image.open(bild_pfad) as bild:
        bild = bild.convert("RGB")
        for t in texte:
            kasten = (max(0, int(t["x"] * dichte)), max(0, int(t["y"] * dichte)),
                      min(bild.width, int((t["x"] + t["w"]) * dichte)), min(bild.height, int((t["y"] + t["h"]) * dichte)))
            if kasten[2] - kasten[0] < 2 or kasten[3] - kasten[1] < 2:
                continue
            stueck = bild.crop(kasten)
            stueck.thumbnail((160, 160))
            roh = stueck.tobytes()
            werte = sorted(leuchtdichte(roh[i], roh[i + 1], roh[i + 2]) for i in range(0, len(roh), 3))
            grund = werte[min(len(werte) - 1, int(len(werte) * 0.95))]
            ergebnis.append({"text": t["text"], "px": t["px"], "fett": t["fett"],
                             "verhaeltnis": round((t["hell"] + 0.05) / (grund + 0.05), 2)})
    return sorted(ergebnis, key=lambda e: e["verhaeltnis"])


if __name__ == "__main__":
    print(json.dumps(messen(sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8")), float(sys.argv[3])), ensure_ascii=False))
