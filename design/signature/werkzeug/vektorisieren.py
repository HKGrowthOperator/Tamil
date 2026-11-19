#!/usr/bin/env python3
"""Misst die Punkte der Vorlage aus und schreibt sie als bereinigte Ellipsen nach daten/punkte.json.

ENTWURF, VORLÄUFIG – Abgleich mit der Originalreferenz Feld A steht aus. Quelle ist die einzige vorliegende
Vorlage `vorlage/tamil-dots-04a-vorlage.jpg` (Felder „01 Master“ und „02 Small“).

Ablauf je Feld:
1. Rotanteil je Bildpunkt (R − (G+B)/2); zusammenhängende Flächen über einer Schwelle sind Punkte.
2. Ellipse aus den zweiten Momenten (Lage, Halbachsen, Drehung); Fläche mit Kantenanteil (Kantenglättung der JPG).
3. Verschmolzene Nachbarn (Füllgrad < 0,9) werden durch schrittweises Abtragen getrennt.
4. Zweiter Durchgang mit niedriger Schwelle für die feinen Punkte im Auslauf.
5. Bereinigung: auffällig lange Doppelpunkte teilen, Rauschen verwerfen.
6. Farbton je Punkt: Rotkanal der Vorlage auf Titan (102) … Impact (179) abgebildet und als glattes Feld
   (quadratisch in x, y) ausgeglichen; im SVG in Stufen zwischen #660000 und #B30000.

Braucht numpy und Pillow (nur dieses Werkzeug; der Generator selbst kommt mit der Standardbibliothek aus).
Aufruf: python3 design/signature/werkzeug/vektorisieren.py
"""
import json
import os
from collections import deque

import numpy as np
from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))
SIG = os.path.dirname(HIER)
SRC = os.path.join(SIG, "vorlage", "tamil-dots-04a-vorlage.jpg")
FELDER = {"master": (30, 305, 575, 665), "small": (600, 380, 925, 580)}

BILD = np.asarray(Image.open(SRC).convert("RGB")).astype(float)
ROT = BILD[..., 0] - (BILD[..., 1] + BILD[..., 2]) / 2


def flaechen(maske):
    h, w = maske.shape
    lab = np.zeros((h, w), int)
    n = 0
    teile = []
    for y in range(h):
        for x in range(w):
            if maske[y, x] and not lab[y, x]:
                n += 1
                q = deque([(y, x)])
                lab[y, x] = n
                pts = []
                while q:
                    cy, cx = q.popleft()
                    pts.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and maske[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n
                            q.append((ny, nx))
                teile.append(np.array(pts))
    return teile


def abtragen(m):
    e = m.copy()
    e[1:, :] &= m[:-1, :]
    e[:-1, :] &= m[1:, :]
    e[:, 1:] &= m[:, :-1]
    e[:, :-1] &= m[:, 1:]
    return e


def ellipse(pts):
    p = pts[:, ::-1].astype(float)
    c = p.mean(0)
    d = p - c
    ev, evec = np.linalg.eigh(d.T @ d / len(p))
    a = 2 * np.sqrt(max(ev[1], 1e-6))
    b = 2 * np.sqrt(max(ev[0], 1e-6))
    return c, a, b, np.degrees(np.arctan2(evec[1, 1], evec[0, 1]))


def punkt(pts, rot, x0, y0, gewicht_teiler=100.0):
    ww = np.clip(rot[pts[:, 0], pts[:, 1]] / gewicht_teiler, 0.0, 1.0)
    flaeche = ww.sum()
    c, a, b, ang = ellipse(pts)
    if len(pts) < 7 or b < 0.6:
        c = (pts[:, ::-1] * ww[:, None]).sum(0) / max(ww.sum(), 1e-6)
        a = b = np.sqrt(max(flaeche, 0.4) / np.pi)
        ang = 0.0
    else:
        k = np.sqrt(max(flaeche, 0.4) / (np.pi * a * b))
        a, b = a * k, b * k
    farbe = BILD[y0 + pts[:, 0], x0 + pts[:, 1]].mean(0)
    return dict(x=float(c[0] + x0), y=float(c[1] + y0), a=float(a), b=float(b), w=float(ang), r=float(farbe[0]))


def messen(feld, schwelle=40, schwelle2=20, spitze=28):
    x0, y0, x1, y1 = feld
    rot = ROT[y0:y1, x0:x1]
    maske = rot > schwelle
    punkte = []
    for pts in flaechen(maske):
        if len(pts) < 2:
            continue
        c, a, b, ang = ellipse(pts)
        teile = [pts]
        if len(pts) / (np.pi * a * b) < 0.9 and len(pts) > 25:
            sub = np.zeros(maske.shape, bool)
            sub[pts[:, 0], pts[:, 1]] = True
            for _ in range(12):
                sub = abtragen(sub)
                if not sub.any():
                    break
                kerne = [s for s in flaechen(sub) if len(s) >= 2]
                if len(kerne) > 1:
                    mitten = np.array([s.mean(0) for s in kerne])
                    zu = ((pts[:, None, :] - mitten[None]) ** 2).sum(-1).argmin(1)
                    teile = [pts[zu == i] for i in range(len(kerne))]
                    break
        punkte += [punkt(t, rot, x0, y0) for t in teile if len(t) >= 2]
    # zweiter Durchgang: feine Punkte, die die erste Schwelle nicht erreicht haben
    h, w = rot.shape
    yy, xx = np.mgrid[0:h, 0:w]
    besetzt = np.zeros((h, w), bool)
    for p in punkte:
        r = max(p["a"], 1) + 2.5
        besetzt |= ((xx - (p["x"] - x0)) ** 2 + (yy - (p["y"] - y0)) ** 2) < r * r
    for pts in flaechen((rot > schwelle2) & ~besetzt):
        if len(pts) >= 2 and rot[pts[:, 0], pts[:, 1]].max() >= spitze:
            p = punkt(pts, rot, x0, y0)
            p["fein"] = 1
            punkte.append(p)
    return punkte


def bereinigen(punkte):
    pos = np.array([[p["x"], p["y"]] for p in punkte])
    a = np.array([p["a"] for p in punkte])
    b = np.array([p["b"] for p in punkte])
    fl = np.pi * a * b
    vh = a / np.maximum(b, 0.3)
    aus = []
    for i, p in enumerate(punkte):
        nb = np.argsort(np.hypot(*(pos - pos[i]).T))[1:7]
        if vh[i] > 1.75 * np.median(vh[nb]) and fl[i] > 1.5 * np.median(fl[nb]) and p["a"] > 4:
            t = np.radians(p["w"])
            for s in (-1, 1):
                q = dict(p)
                q["x"] = p["x"] + s * np.cos(t) * p["a"] * 0.5
                q["y"] = p["y"] + s * np.sin(t) * p["a"] * 0.5
                q["a"], q["b"] = p["a"] * 0.47, min(p["b"], p["a"] * 0.47)
                aus.append(q)
        elif p["a"] < 0.55 and p.get("fein"):
            continue
        else:
            aus.append(p)
    return aus


def farbfeld(punkte):
    """Ton 0 (Titan) … 1 (Impact) als glattes quadratisches Feld über x, y."""
    x = np.array([p["x"] for p in punkte])
    y = np.array([p["y"] for p in punkte])
    t = np.clip((np.array([p["r"] for p in punkte]) - 102.0) / (179.0 - 102.0), 0, 1)
    gew = np.array([p["a"] * p["b"] for p in punkte])          # große Punkte messen sicherer
    mx, my, s = x.mean(), y.mean(), max(x.std(), y.std())
    u, v = (x - mx) / s, (y - my) / s
    m = np.c_[np.ones_like(u), u, v, u * u, u * v, v * v]
    k = np.linalg.lstsq(m * np.sqrt(gew)[:, None], t * np.sqrt(gew), rcond=None)[0]
    return np.clip(m @ k, 0, 1)


def main():
    daten = {"hinweis": "Entwurf, vorläufig – Abgleich mit der Originalreferenz Feld A steht aus",
             "quelle": "vorlage/tamil-dots-04a-vorlage.jpg", "einheit": "Bildpunkte der Vorlage",
             "felder": FELDER}
    for name, feld in FELDER.items():
        pkt = bereinigen(messen(feld))
        ton = farbfeld(pkt)
        daten[name] = [[round(p["x"], 2), round(p["y"], 2), round(p["a"], 2), round(p["b"], 2),
                        round(p["w"], 1), round(float(t), 3)] for p, t in zip(pkt, ton)]
        print(name, len(pkt), "Punkte")
    daten["spalten"] = ["x", "y", "a (große Halbachse)", "b (kleine Halbachse)", "Drehung in Grad", "Ton 0..1"]
    with open(os.path.join(SIG, "daten", "punkte.json"), "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")


if __name__ == "__main__":
    main()
