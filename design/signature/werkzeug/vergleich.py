#!/usr/bin/env python3
"""Vergleich Vorlage ↔ Nachbau: vergleich.jpg (nebeneinander) und vergleich-overlay.jpg (übereinander).

Rendert master.svg, small-entwurf.svg und spatial.svg mit Playwright (Chromium, werkzeug/render.mjs) in genau der
Größe des jeweiligen Vorlagenfeldes und setzt sie neben bzw. halbtransparent über die Vorlage.
Braucht Pillow und Node mit Playwright. Aufruf vom Repo-Wurzelverzeichnis:
    python3 design/signature/werkzeug/vergleich.py
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageFont

HIER = os.path.dirname(os.path.abspath(__file__))
SIG = os.path.dirname(HIER)
sys.path.insert(0, SIG)
import tamil_dots as td  # noqa: E402

K = 2                                     # Vergrößerung gegenüber der Vorlage
VORLAGE = Image.open(os.path.join(SIG, "vorlage", "tamil-dots-04a-vorlage.jpg")).convert("RGB")
SCHRIFT = os.path.join(SIG, "..", "social", "schriften", "libre-franklin-latin-wght-normal.woff2")


def schrift(gr):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, gr)
    return ImageFont.load_default()


def rendern(jobs):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(jobs, f)
    subprocess.run(["node", os.path.join(HIER, "render.mjs"), "--liste", f.name], check=True, capture_output=True)
    os.unlink(f.name)


def feld_von(punkte):
    """Box (x0, y0, x1, y1) der viewBox in Vorlagen-Bildpunkten und viewBox-Seitenverhältnis."""
    _, r = td.einpassen(punkte)
    return (r.x0, r.y0, r.x0 + r.breite / r.s, r.y0 + r.hoehe / r.s)


def main():
    tmp = tempfile.mkdtemp()
    master = td.lade("master")
    small = td.lade("small")
    fm = feld_von(master)
    fs = feld_von(small)
    # Spatial der Vorlage: Feld rechts; unser Spatial hat die Geometrie des Masters + Schattenraum unten
    # Spatial der Vorlage ist ein eigenes Rendering derselben Kuppel; ausgerichtet an der Punktbox (Feld rechts)
    _, rm = td.einpassen(master)
    bx0, bx1 = min(p.x - p.ra for p in master), max(p.x + p.ra for p in master)
    by0 = min(p.y - p.ra for p in master)
    q = (1558 - 1074) / (bx1 - bx0)
    sx0, sy0 = 1074 - (bx0 - rm.x0) * q, 328 - (by0 - rm.y0) * q
    ref_sp = (sx0, sy0, sx0 + rm.breite / rm.s * q, sy0 + rm.hoehe * 1.14 / rm.s * q)

    teile = [("01 Master", "master.svg", fm), ("02 Small", "small-entwurf.svg", fs), ("03 Spatial", "spatial.svg", ref_sp)]
    jobs = []
    for _, datei, (x0, y0, x1, y1) in teile:
        b, h = round((x1 - x0) * K), round((y1 - y0) * K)
        jobs.append({"datei": os.path.join(SIG, datei), "aus": os.path.join(tmp, datei + ".png"), "b": b, "h": h})
    rendern(jobs)

    zeilen = []
    overlays = []
    f_titel = schrift(26)
    for (name, datei, (x0, y0, x1, y1)), job in zip(teile, jobs):
        ref = VORLAGE.crop((round(x0), round(y0), round(x1), round(y1))).resize((job["b"], job["h"]), Image.LANCZOS)
        neu = Image.open(job["aus"]).convert("RGB").resize((job["b"], job["h"]))
        zeilen.append((name, ref, neu))
        # Überlagerung: Vorlage grau, Nachbau als halbtransparente blaue Fläche darüber
        grau = ref.convert("L").convert("RGB")
        rotanteil = neu.split()[0].point(lambda v: v)  # Punkte: Rot > Grün/Blau; Schatten (grau) bleibt außen vor
        r_, g_, _b = neu.split()
        maske = ImageChops.subtract(r_, g_).point(lambda v: 255 if v > 40 else 0)
        blau = Image.new("RGB", ref.size, (0, 110, 255))
        ov = Image.composite(Image.blend(grau, blau, 0.5), grau, maske)
        overlays.append((name, ov))

    rand, kopf = 30, 70
    breite = max(r.width for _, r, _ in zeilen) * 2 + rand * 3
    hoehe = sum(r.height + kopf for _, r, _ in zeilen) + rand * 2 + 60
    bild = Image.new("RGB", (breite, hoehe), (255, 255, 255))
    dr = ImageDraw.Draw(bild)
    dr.text((rand, 18), "Tamil Dots 04A – Vorlage (links) und Nachbau als SVG (rechts), gleiche Größe · " + td.HINWEIS,
            fill=(102, 0, 0), font=schrift(22))
    y = 60 + rand
    for name, ref, neu in zeilen:
        dr.text((rand, y + 18), f"{name} · Vorlage", fill=(0, 0, 0), font=f_titel)
        dr.text((rand * 2 + ref.width, y + 18), f"{name} · Nachbau (SVG, Chromium)", fill=(0, 0, 0), font=f_titel)
        y += kopf
        bild.paste(ref, (rand, y))
        bild.paste(neu, (rand * 2 + ref.width, y))
        dr.rectangle((rand, y, rand + ref.width - 1, y + ref.height - 1), outline=(220, 220, 220))
        dr.rectangle((rand * 2 + ref.width, y, rand * 2 + 2 * ref.width - 1, y + ref.height - 1), outline=(220, 220, 220))
        y += ref.height
    bild.save(os.path.join(SIG, "vergleich.jpg"), quality=86, optimize=True)

    breite = max(o.width for _, o in overlays) + rand * 2
    hoehe = sum(o.height + kopf for _, o in overlays) + rand * 2 + 60
    bild = Image.new("RGB", (breite, hoehe), (255, 255, 255))
    dr = ImageDraw.Draw(bild)
    dr.text((rand, 10), "Überlagerung: Vorlage grau, Nachbau blau halbtransparent", fill=(102, 0, 0), font=schrift(20))
    dr.text((rand, 36), td.HINWEIS, fill=(102, 0, 0), font=schrift(16))
    y = 60 + rand
    for name, ov in overlays:
        dr.text((rand, y + 18), name, fill=(0, 0, 0), font=f_titel)
        y += kopf
        bild.paste(ov, (rand, y))
        y += ov.height
    bild.save(os.path.join(SIG, "vergleich-overlay.jpg"), quality=86, optimize=True)
    print("geschrieben: vergleich.jpg, vergleich-overlay.jpg")


if __name__ == "__main__":
    main()
