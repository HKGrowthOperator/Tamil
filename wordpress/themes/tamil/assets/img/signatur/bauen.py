#!/usr/bin/env python3
"""Signet „Tamil Dots 04A“ für das Theme: dekorative Fassungen aus der freigegebenen Form bauen.

Quelle ist die Form, die Luis am 19.11.2026 freigegeben hat: `design/signature/daten/punkte.json` (238 Punkte des
Masters), gebaut mit dem Generator `design/signature/tamil_dots.py` (dieselbe Geometrie wie `master.svg`). Dieses
Skript ändert die Form nicht; es wählt nur Ausschnitt und Farbe und schreibt die Dateien für den Einbau.

Farben: nur die Markenwerte Titan Red #660000, Impact Red #B30000 und Weiß #FFFFFF. Abstufungen entstehen allein über
die Deckkraft (`fill-opacity`) auf der jeweiligen Fläche, nicht über neue Farbwerte. Der Ton jedes Punkts folgt dem
Master (dunkel am großen linken Fuß, hell zum Auslauf).

    python3 wordpress/themes/tamil/assets/img/signatur/bauen.py          # schreibt alle Dateien hierher
    python3 wordpress/themes/tamil/assets/img/signatur/bauen.py --liste  # nur Übersicht

Dateien (alle dekorativ: aria-hidden, focusable="false", ohne Titel, unter 30 KB, die Ecke unter 6 KB):
    flaeche.svg  ganze Kuppel, Impact auf Titan, mit --i je Punkt (inline, Aufbau beim Hineinscrollen)
    band.svg     waagerechter Streifen der Kuppel, Impact auf Titan, leise (Rubrikband, Zeile mit Rechtlichem)
    hell.svg     ganze Kuppel, leise Tönung in Impact auf Weiß (Seitenköpfe)
    raum.svg     03 Spatial, nur an Sonderstellen (404, Production)
    ecke.svg     „an jedem Post“ (Theme 3.6.0): kleiner Bogen für die Ecke unten rechts im Bild, weiß mit Deckkraft
    ecke-rot.svg dieselbe Ecke in Titan (Fuß) und Impact (Bogen, Auslauf) für helle Bildecken

Die Ecke nutzt nicht den Master, sondern die Small-Geometrie (`punkte.json`, Feld „small“) in der Mini-Fassung des
Generators (`mini_aus`): Größenunterschiede leicht gestaucht, sich berührende Punkte ausgedünnt. So bleiben die Punkte
auch bei 20–56 px Breite einzeln sichtbar. Der Ausschnitt schneidet rechts den Auslauf und unten ein Stück vom Fuß ab;
die Datei sitzt bündig in der Bildecke, die Kanten der Datei sind also die Kanten des Bilds.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.abspath(os.path.join(HIER, *[".."] * 6))
GENERATOR = os.path.join(WURZEL, "design", "signature", "tamil_dots.py")

TITAN = "#660000"
IMPACT = "#B30000"
WEISS = "#FFFFFF"
ECKE_AUSSCHNITT = (0.0, 0.0, 0.90, 0.95)   # Anteile der Formbox: links, oben, rechts, unten


def generator():
    spec = importlib.util.spec_from_file_location("tamil_dots", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tamil_dots"] = mod   # dataclass braucht das Modul in sys.modules
    spec.loader.exec_module(mod)
    return mod


def deckkraft(von, bis, stufen):
    """Deckkraft je Farbstufe des Masters (Stufe 0 = dunkler Fuß, letzte Stufe = heller Auslauf)."""
    return [von + (bis - von) * k / (stufen - 1) for k in range(stufen)]


def zahl(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s[1:] if s.startswith("0.") else s


def gruppen(td, punkte, farbe, stufen_deckkraft, extra=lambda p: "", form=None):
    form = form or td.ellipse
    out = []
    for k, a in enumerate(stufen_deckkraft):
        teil = [form(p, extra(p)) for p in punkte if p.stufe == k]
        if teil:
            out.append(f'<g fill="{farbe}" fill-opacity="{zahl(a)}">' + "".join(teil) + "</g>\n")
    return out


def kopf(r, extra=""):
    vb = f"0 0 {round(r.breite)} {round(r.hoehe)}"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" aria-hidden="true" focusable="false"{extra}>\n'


def alle():
    td = generator()
    master = td.lade("master")
    n = td.STUFEN
    d = {}

    # Ganze Kuppel, Impact auf Titan; jeder Punkt mit --i (Reihenfolge des Aufbaus: großer Fuß vorn links zuerst).
    # Gedrehte Punkte stecken in einer Gruppe mit der Drehung, damit `scale` aus dem CSS um die Punktmitte wirkt.
    pm, rm = td.einpassen(master)
    d["flaeche.svg"] = "".join(
        [kopf(rm, f' class="signatur__punkte" style="--n:{len(pm)}"')]
        + gruppen(td, pm, IMPACT, deckkraft(0.3, 0.8, n), lambda p: f' style="--i:{p.i}"', td.ellipse_bewegt)
        + ["</svg>\n"]
    )

    # Waagerechter Streifen durch den Bogen (wie hintergrund/rubrikband-*), ganze Breite: Fuß links, Auslauf rechts
    pb, rb = td.einpassen(master, ausschnitt=(0.0, 0.30, 1.0, 0.66))
    d["band.svg"] = "".join([kopf(rb)] + gruppen(td, pb, IMPACT, deckkraft(0.3, 0.66, n)) + ["</svg>\n"])

    # Leise Tönung auf Weiß (wie vorschlaege/master-hell, aber als Impact mit Deckkraft statt Mischfarbe)
    d["hell.svg"] = "".join([kopf(rm)] + gruppen(td, pm, IMPACT, deckkraft(0.17, 0.08, n)) + ["</svg>\n"])

    # 03 Spatial, dekorativ (ohne Titel); Farben wie im Entwurf spatial.svg
    d["raum.svg"] = td.svg_raeumlich(pm, rm, None)

    # Ecke „an jedem Post“: Small-Geometrie als Mini (Stauchung 0,9, Abstand 1,05), rechts 10 % und unten 5 %
    # abgeschnitten. Weiß von 95 % (Fuß) bis 72 % Deckkraft (Auslauf); für helle Bildecken Titan und Impact.
    pe, re_ = td.einpassen(td.mini_aus(td.lade("small"), 0.9, 1.05), breite=1000, ausschnitt=ECKE_AUSSCHNITT)
    d["ecke.svg"] = "".join([kopf(re_)] + gruppen(td, pe, WEISS, deckkraft(0.95, 0.72, n)) + ["</svg>\n"])
    # Rot nur in den beiden Markenwerten: die dunklen Stufen des Masters (Fuß) Titan, die hellen (Bogen, Auslauf) Impact
    fuss = [p for p in pe if p.stufe <= 3]
    bogen = [p for p in pe if p.stufe > 3]
    d["ecke-rot.svg"] = "".join(
        [kopf(re_)]
        + [f'<g fill="{farbe}">' + "".join(td.ellipse(p) for p in teil) + "</g>\n" for farbe, teil in ((TITAN, fuss), (IMPACT, bogen)) if teil]
        + ["</svg>\n"]
    )
    return d


def main():
    ap = argparse.ArgumentParser(description="Signet-Fassungen für das Theme bauen")
    ap.add_argument("--liste", action="store_true", help="nur Übersicht ausgeben, nichts schreiben")
    a = ap.parse_args()
    for name, text in sorted(alle().items()):
        groesse = len(text.encode("utf-8"))
        if not a.liste:
            with open(os.path.join(HIER, name), "w", encoding="utf-8") as f:
                f.write(text)
        grenze = 6 if name.startswith("ecke") else 30   # die Ecke steht in jedem Bild: klein halten
        warnung = "  ZU GROSS" if groesse >= grenze * 1024 else ""
        print(f"{name:14} {text.count('<ellipse'):4} Punkte {groesse / 1024:5.1f} KB{warnung}")


if __name__ == "__main__":
    main()
