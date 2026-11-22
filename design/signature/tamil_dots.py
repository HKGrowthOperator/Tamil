#!/usr/bin/env python3
"""Tamil Dots 04A – Generator für das Signature-Element von tamil.de.

ENTWURF, VORLÄUFIG – Abgleich mit der Originalreferenz Feld A steht aus.

Grundlage ist die einzige vorliegende Vorlage `vorlage/tamil-dots-04a-vorlage.jpg` (Felder „01 Master“ und
„02 Small“). Die von Luis genannte Referenz „vier_rote_punktmarken_für_tamil.de.png“ (Feld A) liegt nicht vor.

Woher die Form kommt
--------------------
Jeder Punkt der Vorlage ist als Ellipse ausgemessen (Lage, große und kleine Halbachse, Drehung, Farbton) und
bereinigt: `werkzeug/vektorisieren.py` schreibt `daten/punkte.json` (Einheit: Bildpunkte der Vorlage). Ein rein
rechnerischer Nachbau (Kugelraster in Perspektive) wurde erprobt, traf Silhouette, Auslauf und Punktgrößen aber nicht
genau genug (Überdeckung mit der Vorlage nur rund 30 %); für das Signet zählt die Treue zur Vorlage. Dieser Generator
macht aus den Messwerten saubere Vektoren und baut alle Fassungen daraus: Farben, Ausschnitte, Small und Mini,
Spatial, Aufbau-Animation und Variante C.

Nur Python-Standardbibliothek. Aufruf vom Repo-Wurzelverzeichnis:

    python3 design/signature/tamil_dots.py            # schreibt alle Dateien (siehe README.md)
    python3 design/signature/tamil_dots.py --liste    # Dateien, Punktzahl, Größe
    python3 design/signature/tamil_dots.py --fassung weiss --ausschnitt 0 0 .6 1 --aus /tmp/x.svg

Alle SVG: `viewBox`, keine feste Breite/Höhe, keine Metadaten, jede Datei unter 30 KB.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass, replace

HIER = os.path.dirname(os.path.abspath(__file__))
HINWEIS = "Entwurf, vorläufig – Abgleich mit der Originalreferenz Feld A steht aus"

# ---------------------------------------------------------------------------------------------------------------------
# Farben (Branding Master Handoff v1.1, 19.11.2026). Der Master nutzt ausschließlich Titan und Impact und Stufen
# dazwischen. Alle anderen Fassungen sind Vorschläge (Ordner vorschlaege/ und hintergrund/).

TITAN = (0x66, 0x00, 0x00)
IMPACT = (0xB3, 0x00, 0x00)
WEISS = (0xFF, 0xFF, 0xFF)
SCHWARZ = (0x00, 0x00, 0x00)


def mischen(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def hexfarbe(c):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)


# Name -> (Farbe für Ton 0, Farbe für Ton 1, Fläche dahinter oder None = transparent)
FASSUNGEN = {
    "titan-impact": (TITAN, IMPACT, None),                                          # Master
    "rot-auf-weiss": (TITAN, IMPACT, WEISS),                                        # Master auf weißer Platte
    "weiss": (mischen(WEISS, IMPACT, 0.18), WEISS, None),                           # für rote Flächen
    "hell": (mischen(WEISS, IMPACT, 0.17), mischen(WEISS, IMPACT, 0.08), None),     # leise Tönung auf Weiß
    "impact-auf-titan": (mischen(TITAN, IMPACT, 0.42), IMPACT, None),               # für Titan-Flächen
    "titan-auf-impact": (TITAN, mischen(TITAN, IMPACT, 0.5), None),                 # für Impact-Flächen
}
STUFEN = 7


def farbstufen(fassung, stufen=STUFEN):
    a, b, _ = FASSUNGEN[fassung]
    return [hexfarbe(mischen(a, b, k / (stufen - 1))) for k in range(stufen)]


# ---------------------------------------------------------------------------------------------------------------------
# Punkte

@dataclass
class Punkt:
    x: float
    y: float
    ra: float          # große Halbachse
    rb: float          # kleine Halbachse
    winkel: float      # Drehung der großen Halbachse in Grad (Bild, y nach unten)
    ton: float         # 0 = Titan … 1 = Impact
    lauf: float = 0.0  # 0 = vorn links … 1 = hinten rechts (Reihenfolge des Aufbaus)
    stufe: int = 0
    i: int = 0


def lade(feld="master"):
    with open(os.path.join(HIER, "daten", "punkte.json"), encoding="utf-8") as f:
        daten = json.load(f)
    pk = [Punkt(x, y, a, b, w, t) for x, y, a, b, w, t in daten[feld]]
    x0 = min(p.x for p in pk)
    x1 = max(p.x for p in pk)
    y0 = min(p.y for p in pk)
    y1 = max(p.y for p in pk)
    for p in pk:
        # Aufbau entlang des Bogens: vom großen linken Fuß (vorn) zum feinen Auslauf (hinten rechts)
        p.lauf = 0.88 * (p.x - x0) / (x1 - x0) + 0.12 * (1 - (p.y - y0) / (y1 - y0))
    return pk


@dataclass
class Rahmen:
    x0: float          # linke obere Ecke der viewBox in Vorlagen-Bildpunkten
    y0: float
    s: float           # viewBox-Einheiten je Vorlagen-Bildpunkt
    breite: float
    hoehe: float


def einpassen(punkte, breite=1000.0, rand=0.012, ausschnitt=None, rmin=0.0, skala=1.0):
    """Legt die Punkte in eine viewBox der Breite `breite`.

    ausschnitt = (x0, y0, x1, y1) in Anteilen der Formbox; Punkte ganz außerhalb entfallen, die anderen werden am
    Rand der viewBox beschnitten. `skala` vergrößert jeden Punkt um seinen Mittelpunkt (für Mini).
    Gibt (punkte, Rahmen) zurück; Reihenfolge = Aufbau.
    """
    x0 = min(p.x - p.ra for p in punkte)
    x1 = max(p.x + p.ra for p in punkte)
    y0 = min(p.y - p.ra for p in punkte)
    y1 = max(p.y + p.ra for p in punkte)
    if ausschnitt:
        ax0, ay0, ax1, ay1 = ausschnitt
        w, h = x1 - x0, y1 - y0
        x0, x1, y0, y1 = x0 + ax0 * w, x0 + ax1 * w, y0 + ay0 * h, y0 + ay1 * h
    else:
        r = rand * (x1 - x0)
        x0, y0, x1, y1 = x0 - r, y0 - r, x1 + r, y1 + r
    s = breite / (x1 - x0)
    rahmen = Rahmen(x0, y0, s, breite, (y1 - y0) * s)
    aus = []
    for p in punkte:
        q = replace(p, x=(p.x - x0) * s, y=(p.y - y0) * s, ra=p.ra * s * skala, rb=p.rb * s * skala)
        if q.rb < rmin:
            continue
        if q.x + q.ra < 0 or q.x - q.ra > breite or q.y + q.ra < 0 or q.y - q.ra > rahmen.hoehe:
            continue
        aus.append(q)
    aus.sort(key=lambda p: p.lauf)
    for i, p in enumerate(aus):
        p.i = i
        p.stufe = min(int(p.ton * STUFEN), STUFEN - 1)
    return aus, rahmen


# ---------------------------------------------------------------------------------------------------------------------
# SVG

def z(v, nachkomma=1):
    """Zahl kurz schreiben: 12.0 -> 12, 0.5 -> .5"""
    s = f"{v:.{nachkomma}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        return "0"
    if s.startswith("0."):
        return s[1:]
    if s.startswith("-0."):
        return "-" + s[2:]
    return s


def ellipse(p, extra=""):
    n = 0 if p.rb >= 6 else (1 if p.rb >= 1.5 else 2)     # große Punkte ganzzahlig (≤ 0,05 % der Breite)
    cx, cy = z(p.x, n), z(p.y, n)
    w = p.winkel % 180
    if w > 90:
        w -= 180
    rot = ""
    if abs(w) >= 0.5 and p.ra - p.rb > 0.05 * p.ra:
        rot = f' transform="rotate({z(w, 0)} {cx} {cy})"'
    return f'<ellipse{extra} cx="{cx}" cy="{cy}" rx="{z(p.ra, n)}" ry="{z(p.rb, n)}"{rot}/>'


def ellipse_bewegt(p, extra=""):
    """Für Animationen: Drehung auf einer umschließenden Gruppe, damit `scale` (CSS) um die Punktmitte wirkt und die
    Datei auch ohne CSS richtig aussieht."""
    e = ellipse(p, extra)
    if ' transform="rotate(' not in e:
        return e
    vor, rot = e.split(' transform="', 1)
    return f'<g transform="{rot[:-3]}">{vor}/></g>'


def kopf(r, titel=None, extra=""):
    vb = f"0 0 {z(r.breite, 0)} {z(r.hoehe, 0)}"
    if titel is None:      # dekorativ (Hintergrund): für Hilfsmittel unsichtbar
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" aria-hidden="true" focusable="false"{extra}>\n'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{titel}"{extra}>\n'
            f"<title>{titel}</title>\n")


def gruppen(punkte, farben, extra=lambda p: "", form=ellipse):
    out = []
    for k, farbe in enumerate(farben):
        teil = [form(p, extra(p)) for p in punkte if p.stufe == k]
        if teil:
            out.append(f'<g fill="{farbe}">' + "".join(teil) + "</g>\n")
    return out


def svg_flach(punkte, r, fassung="titan-impact", titel=None):
    """Flach: ein <g fill> je Farbstufe, jeder Punkt ein eigenes <ellipse> (einzeln editierbar)."""
    out = [kopf(r, titel)]
    grund = FASSUNGEN[fassung][2]
    if grund:
        out.append(f'<rect width="100%" height="100%" fill="{hexfarbe(grund)}"/>\n')
    out.extend(gruppen(punkte, farbstufen(fassung)))
    out.append("</svg>\n")
    return "".join(out)


AUFBAU_CSS = (
    ".td{--dauer:1500ms;--takt:calc(var(--dauer)*.6/var(--n))}"
    ".td ellipse{transform-box:fill-box;transform-origin:center}"
    "@media (prefers-reduced-motion:no-preference){"
    ".td.an ellipse{animation:td-auf calc(var(--dauer)*.4) cubic-bezier(.16,1,.3,1) calc(var(--i)*var(--takt)) both}}"
    "@keyframes td-auf{from{scale:0;opacity:0}40%{opacity:1}to{scale:1;opacity:1}}"
)


def svg_animiert(punkte, r, titel, fassung="titan-impact"):
    """„Punkte bauen die Form auf“: jeder Punkt trägt --i (Reihenfolge vorn links -> hinten rechts).

    Die Klasse `an` an der Wurzel startet den Aufbau; ohne `an` oder bei „Bewegung reduzieren“ steht die fertige
    Form da. Diese Datei trägt `an` und spielt beim Öffnen einmal ab; auf der Website setzt ein Skript `an`
    beim Hineinscrollen.
    """
    out = [kopf(r, titel, extra=f' class="td an" style="--n:{len(punkte)}"'), f"<style>{AUFBAU_CSS}</style>\n"]
    out.extend(gruppen(punkte, farbstufen(fassung), lambda p: f' style="--i:{p.i}"', ellipse_bewegt))
    out.append("</svg>\n")
    return "".join(out)


WELLE_CSS = (
    ".tdc{--dauer:2200ms;--takt:calc(var(--dauer)*.45/var(--n))}"
    ".tdc ellipse{transform-box:fill-box;transform-origin:center}"
    "@media (prefers-reduced-motion:no-preference){"
    ".tdc.an ellipse{animation:tdc-welle var(--dauer) cubic-bezier(.33,1,.68,1) calc(var(--i)*var(--takt)) 2 both}}"
    "@keyframes tdc-welle{0%{scale:1;opacity:1}25%{scale:.3;opacity:.55}60%{scale:1.15;opacity:1}100%{scale:1}}"
)


def svg_variante_c(punkte, r, titel):
    """Variante C: die unterste Punktreihe des Bogens als Welle (Bewegungselement, nicht als stehendes Zeichen)."""
    out = [kopf(r, titel, extra=f' class="tdc an" style="--n:{len(punkte)}"'), f"<style>{WELLE_CSS}</style>\n"]
    out.extend(gruppen(punkte, farbstufen("titan-impact"), lambda p: f' style="--i:{p.i}"', ellipse_bewegt))
    out.append("</svg>\n")
    return "".join(out)


def svg_raeumlich(punkte, r, titel, dicke=0.15, schatten=True):
    """03 Spatial: Scheiben mit sichtbarer Kante und weichem Bodenschatten (nur für besondere Orte).

    schatten=False lässt den Bodenschatten weg (Theme, raum.svg: Prüfung 21.11., N-13); die Höhe bleibt gleich.

    Kante = dieselbe Ellipse nach links unten versetzt, in abgedunkeltem Titan; der Versatz wächst mit der
    Schräglage (flache Punkte am Umriss zeigen mehr Kante). Schatten = Radialverlauf in Schwarz, kein Filter.
    """
    farben = farbstufen("titan-impact")
    kanten = [hexfarbe(mischen(mischen(TITAN, IMPACT, k / (STUFEN - 1) * 0.35), SCHWARZ, 0.3)) for k in range(STUFEN)]
    xs0 = min(p.x - p.ra for p in punkte)
    xs1 = max(p.x + p.ra for p in punkte)
    ymax = max(p.y + p.rb for p in punkte)
    extra = r.hoehe * 0.14
    r2 = replace(r, hoehe=r.hoehe + extra)
    out = [kopf(r2, titel)]
    if schatten:
        out += ['<defs><radialGradient id="s" fx=".22" fr=".02"><stop offset="0" stop-opacity=".3"/>'
           '<stop offset=".45" stop-opacity=".1"/><stop offset="1" stop-opacity="0"/></radialGradient></defs>\n',
           f'<ellipse cx="{z(xs0 + (xs1 - xs0) * 0.42, 0)}" cy="{z(ymax + extra * 0.02, 0)}" '
           f'rx="{z((xs1 - xs0) * 0.5, 0)}" ry="{z(extra * 0.42, 0)}" fill="url(#s)"/>\n']
    hinten = sorted(punkte, key=lambda p: -p.lauf)
    # Kanten zuerst als <use> auf die Flächen (versetzt, eigene Farbe), danach die Flächen selbst mit id.
    # Die Flächen tragen keine eigene Füllung; die Farbe kommt aus der umgebenden Gruppe.
    ids = {id(p): f"e{k}" for k, p in enumerate(hinten)}
    for k in range(STUFEN):
        teil = []
        for p in hinten:
            if p.stufe != k:
                continue
            schraeg = math.sqrt(max(0.0, 1 - (p.rb / max(p.ra, 1e-9)) ** 2))
            t = dicke * p.ra * (0.4 + 0.6 * schraeg)
            teil.append(f'<use href="#{ids[id(p)]}" x="{z(-0.45 * t)}" y="{z(0.9 * t)}"/>')
        if teil:
            out.append(f'<g fill="{kanten[k]}">' + "".join(teil) + "</g>\n")
    out.extend(gruppen(hinten, farben, lambda p: f' id="{ids[id(p)]}"'))
    out.append("</svg>\n")
    return "".join(out)


# ---------------------------------------------------------------------------------------------------------------------
# Mini und Variante C

def mini_aus(punkte, stauch=0.7, abstand=1.0):
    """Größen zum größten Punkt hin stauchen (r' = r_max · (r/r_max)^stauch) und Berührungen ausdünnen."""
    rmax = max(p.ra for p in punkte)
    neu = []
    for p in sorted(punkte, key=lambda p: -p.ra * p.rb):
        f = (p.ra / rmax) ** stauch * rmax / p.ra
        q = replace(p, ra=p.ra * f, rb=min(p.rb * f, p.ra * f))
        if all(math.hypot(q.x - o.x, q.y - o.y) > abstand * (math.sqrt(q.ra * q.rb) + math.sqrt(o.ra * o.rb)) for o in neu):
            neu.append(q)
    return neu


# Auswahl für Variante C

def unterste_reihe(punkte):
    """Punkte ohne Nachbarn zur freien Fläche hin: die Reihe am unteren Rand des Bogens."""
    mx = sum(p.x for p in punkte) / len(punkte)
    my = max(p.y for p in punkte) + 60          # Punkt unter dem Bogen, zu dem „unten“ zeigt
    aus = []
    for p in punkte:
        dx, dy = mx - p.x, my - p.y
        n = math.hypot(dx, dy)
        dx, dy = dx / n, dy / n
        frei = True
        for q in punkte:
            if q is p:
                continue
            vx, vy = q.x - p.x, q.y - p.y
            d = math.hypot(vx, vy)
            if d == 0 or d > 3.2 * max(p.ra, q.ra):
                continue
            if (vx * dx + vy * dy) / d > 0.55:   # Nachbar liegt in Richtung der freien Fläche
                frei = False
                break
        if frei:
            aus.append(p)
    return aus


# ---------------------------------------------------------------------------------------------------------------------
# Seiten

def html_animation(svg_aufbau, svg_c):
    aufbau = svg_aufbau.replace('class="td an"', 'class="td" id="aufbau"', 1)
    welle = svg_c.replace('class="tdc an"', 'class="tdc" id="welle"', 1)
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tamil Dots – Animation (Entwurf)</title>
<style>
@font-face {{ font-family: "Libre Franklin"; src: url("../social/schriften/libre-franklin-latin-wght-normal.woff2") format("woff2");
  font-weight: 100 900; font-display: swap; }}
:root {{ --titan:#660000; --impact:#B30000; --tinte:#15191E; --leise:#51565C; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #fff; color: var(--tinte); font: 17px/1.5 "Libre Franklin", system-ui, sans-serif; }}
main {{ max-width: 1080px; margin: 0 auto; padding: 28px 16px 64px; }}
h1 {{ font-size: 28px; line-height: 1.15; margin: 0 0 8px; color: var(--titan); }}
h2 {{ font-size: 19px; margin: 40px 0 8px; }}
p {{ margin: 0 0 12px; max-width: 68ch; }}
.hinweis {{ display: inline-block; background: var(--titan); color: #fff; font-size: 14px; padding: 6px 10px; margin: 0 0 18px; }}
.buehne {{ border: 1px solid #e6e6e6; padding: 24px; }}
.buehne svg {{ display: block; width: 100%; height: auto; }}
button {{ font: inherit; min-height: 44px; padding: 10px 18px; margin: 14px 12px 0 0; border: 2px solid var(--titan);
  background: #fff; color: var(--titan); cursor: pointer; }}
button:hover, button:focus-visible {{ background: var(--titan); color: #fff; }}
code, pre {{ font: 14px/1.45 ui-monospace, Menlo, monospace; }}
pre {{ background: #f4f4f4; padding: 14px; overflow-x: auto; white-space: pre-wrap; }}
.leise {{ color: var(--leise); font-size: 15px; }}
</style>
</head>
<body>
<main>
<p class="hinweis">{HINWEIS}</p>
<h1>Tamil Dots 04A – „Punkte bauen die Form auf“</h1>
<p>Die Punkte wachsen vom großen linken Fuß (vorn) zum feinen Auslauf (hinten rechts) von 0 auf volle Größe,
weich auslaufend (ease-out-expo), in rund 1,5 Sekunden. Bewegt werden nur <code>scale</code> und <code>opacity</code>.
Bei „Bewegung reduzieren“ steht die fertige Form sofort da.</p>
<div class="buehne">{aufbau}</div>
<button type="button" data-ziel="aufbau">Aufbau abspielen</button>
<p class="leise">Steuerung: <code>--dauer</code> an der Wurzel (Vorgabe 1500 ms). Jeder Punkt trägt
<code>style="--i:n"</code> (Reihenfolge), die Wurzel <code>--n</code> (Anzahl). Gestartet wird mit der Klasse
<code>an</code>.</p>

<h2>Variante C – abgeleitetes Bewegungselement</h2>
<p>Die unterste Punktreihe des Bogens, vom großen Fuß bis zum feinen Auslauf, als Welle. Nur in Bewegung einsetzen
(Übergang, Laden), nicht als stehendes Zeichen.</p>
<div class="buehne">{welle}</div>
<button type="button" data-ziel="welle">Welle abspielen</button>

<h2>Einbau auf der Website (erst nach Freigabe durch Luis)</h2>
<pre>&lt;!-- inline und dekorativ: role/title entfernen, aria-hidden setzen --&gt;
&lt;svg class="td" aria-hidden="true" focusable="false" viewBox="…" style="--n:…"&gt;…&lt;/svg&gt;

// einmal beim Hineinscrollen starten, keine automatisch startende Animation
new IntersectionObserver((e, o) =&gt; e.forEach(x =&gt; {{
  if (x.isIntersecting) {{ x.target.classList.add('an'); o.unobserve(x.target); }}
}}), {{ threshold: .35 }}).observe(document.querySelector('svg.td'));</pre>
</main>
<script>
document.querySelectorAll('button[data-ziel]').forEach(function (b) {{
  b.addEventListener('click', function () {{
    var s = document.getElementById(b.dataset.ziel);
    s.classList.remove('an'); void s.getBoundingClientRect(); s.classList.add('an');
  }});
}});
var io = new IntersectionObserver(function (e, o) {{
  e.forEach(function (x) {{ if (x.isIntersecting) {{ x.target.classList.add('an'); o.unobserve(x.target); }} }});
}}, {{ threshold: .35 }});
io.observe(document.getElementById('aufbau')); io.observe(document.getElementById('welle'));
</script>
</body>
</html>
"""


def html_hintergruende():
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tamil Dots – Hintergründe (Vorschlag)</title>
<style>
@font-face {{ font-family: "Libre Franklin"; src: url("../../social/schriften/libre-franklin-latin-wght-normal.woff2") format("woff2");
  font-weight: 100 900; font-display: swap; }}
:root {{ --titan:#660000; --impact:#B30000; --weiss:#FFFFFF; --schwarz:#000000; --tinte:#15191E; --leise:#51565C; --rand:16px; }}
@media (min-width:600px) {{ :root {{ --rand:24px; }} }}
@media (min-width:1024px) {{ :root {{ --rand:40px; }} }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #E9E9E9; }}
body {{ font: 17px/1.5 "Libre Franklin", system-ui, sans-serif; color: var(--tinte); -webkit-font-smoothing: antialiased; }}
.seite {{ max-width: 1280px; margin: 0 auto; background: var(--weiss); }}
.marke {{ padding: 10px var(--rand); background: var(--schwarz); color: #fff; font-size: 14px; line-height: 1.4; }}
.kopfzeile {{ padding: 20px var(--rand) 4px; }}
.kopfzeile h1 {{ margin: 0; font-size: 24px; line-height: 1.2; color: var(--titan); }}
.kopfzeile p {{ margin: 4px 0 0; color: var(--leise); font-size: 15px; }}
.etikett {{ display: block; padding: 22px var(--rand) 8px; font-size: 13px; font-weight: 650; color: var(--leise); }}

/* 1  Kopf auf Weiß: leise Kuppel unten rechts angeschnitten */
.kopf {{ height: 104px; padding: 0 var(--rand); display: flex; align-items: center;
  background: var(--weiss) url("kopf-hell-auf-weiss.svg") right -12px bottom / auto 118% no-repeat; border-bottom: 1px solid #EEE6E6; }}
.kopf img {{ height: 50px; width: auto; display: block; }}
@media (min-width:1024px) {{ .kopf {{ height: 128px; background-size: auto 132%; background-position: right 4% bottom; }} .kopf img {{ height: 62px; }} }}

/* 2  Rubrikband: Impact, Punkte rechts angeschnitten */
.band {{ height: 46px; display: flex; align-items: center; gap: 22px; padding: 0 var(--rand); overflow: hidden;
  background: var(--impact) url("rubrikband-titan-auf-impact.svg") right -20px center / auto 100% no-repeat;
  color: #fff; font-size: 16px; font-weight: 600; white-space: nowrap; }}
.band.weiss {{ background-image: url("rubrikband-weiss-auf-impact.svg"); }}
/* weiße Punkte nur, wo rechts im Band Platz frei bleibt (ab 1024 px); darunter liefe Schrift über die Punkte */
@media (max-width:1023px) {{ .band.weiss {{ background-image: none; }} }}
.band span:first-child {{ box-shadow: inset 0 -3px 0 #fff; padding: 12px 0; }}
@media (min-width:1024px) {{ .band {{ height: 48px; }} }}

/* 3  Große Titan-Fläche („Diese Woche“, Kino, Termine): Punkte rechts unten angeschnitten */
.titan {{ color: #fff; padding: 28px var(--rand) 34px;
  background: var(--titan) url("flaeche-impact-auf-titan.svg") right -10% bottom -26% / auto 110% no-repeat; }}
.titan h2 {{ margin: 0 0 14px; font-size: 22px; }}
.titan ol {{ list-style: none; margin: 0; padding: 0; max-width: 520px; }}
.titan li {{ padding: 12px 0; border-top: 1px solid rgb(255 255 255 / .22); }}
.titan li b {{ display: block; font-size: 15px; font-weight: 600; color: rgb(255 255 255 / .84); }}
@media (max-width:599px) {{ .titan {{ background-size: 92% auto; background-position: right -18% bottom -10px; padding-bottom: 170px; }} }}

/* 4  Fuß auf Weiß */
.fuss {{ min-height: 210px; padding: 30px var(--rand); color: var(--leise); font-size: 15px;
  background: var(--weiss) url("fuss-hell-auf-weiss.svg") right 3% bottom -6px / auto 86% no-repeat; border-top: 4px solid var(--titan); }}
.fuss b {{ color: var(--titan); }}
.fuss p {{ max-width: 420px; margin: 0 0 8px; }}
@media (max-width:599px) {{ .fuss {{ background-size: 80% auto; padding-bottom: 150px; }} }}

/* 5  Sonderseite (404): Spatial */
.sonder {{ text-align: center; padding: 36px var(--rand) 56px; }}
.sonder img {{ width: min(680px, 100%); height: auto; display: block; margin: 0 auto 10px; }}
.sonder h2 {{ margin: 0 0 6px; font-size: 26px; color: var(--titan); }}
.sonder p {{ margin: 0; color: var(--leise); }}
</style>
</head>
<body>
<div class="seite">
<div class="marke">VORSCHLAG, NICHT FREIGEGEBEN · {HINWEIS}</div>
<div class="kopfzeile"><h1>Tamil Dots als Hintergrund</h1><p>Die Punkte rahmen und gliedern; sie liegen nie unter Schrift oder Gesichtern.</p></div>

<span class="etikett">1 · Kopf auf Weiß · kopf-hell-auf-weiss.svg</span>
<header class="kopf"><img src="../../inhalte/logo.png" alt="tamil.de"></header>

<span class="etikett">2 · Rubrikband Impact · rubrikband-titan-auf-impact.svg</span>
<nav class="band" aria-label="Rubriken (Beispiel)"><span>Start</span><span>Nachrichten</span><span>Kino</span><span>Events</span><span>Community</span><span>Küche</span></nav>
<span class="etikett">2b · Rubrikband mit weißen Punkten · rubrikband-weiss-auf-impact.svg</span>
<nav class="band weiss" aria-label="Rubriken (Beispiel)"><span>Start</span><span>Nachrichten</span><span>Kino</span><span>Events</span><span>Community</span><span>Küche</span></nav>

<span class="etikett">3 · Titan-Fläche („Diese Woche“, Kino, Termine) · flaeche-impact-auf-titan.svg</span>
<section class="titan">
<h2>Diese Woche</h2>
<ol>
<li><b>So 15.11. · Düsseldorf</b>Deepavali-Feier des Düsseldorf Tamil Sangam</li>
<li><b>Berlin</b>Sri Ganesha Hindu Temple: Lichterfest mit Lakshmi Pooja</li>
<li><b>München</b>Sivaalayam-Tempel und Sri-Pillaiyar-Tempel</li>
</ol>
</section>

<span class="etikett">4 · Fuß auf Weiß · fuss-hell-auf-weiss.svg</span>
<footer class="fuss"><p><b>tamil.de</b> · Magazin der tamilischen Diaspora in Deutschland, Österreich und der Schweiz</p><p>Impressum · Datenschutz · Kontakt</p></footer>

<span class="etikett">5 · Sonderseite 404 · ../spatial.svg</span>
<section class="sonder"><img src="../spatial.svg" alt=""><h2>Diese Seite gibt es nicht</h2><p>Zur Startseite von tamil.de</p></section>
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------------------------------------------------
# Ausgabe

def alle():
    """Alle Dateien als {Pfad relativ zu design/signature: Text}."""
    master = lade("master")
    small = lade("small")
    d = {}
    titel = "tamil.de Signet Tamil Dots 04A (Entwurf)"

    # 01 Master: nur Titan, Impact und Stufen dazwischen, transparent
    pm, rm = einpassen(master)
    d["master.svg"] = svg_flach(pm, rm, "titan-impact", titel)

    # Vorschläge in anderen Farben (gleiche Geometrie, nicht Teil des Masters)
    for fassung in ("rot-auf-weiss", "weiss", "hell", "impact-auf-titan", "titan-auf-impact"):
        d[f"vorschlaege/master-{fassung}.svg"] = svg_flach(pm, rm, fassung, f"{titel}, Vorschlag {fassung}")

    # 02 Small (eigene Messung des Feldes „02 Small“) und Mini (aus Small abgeleitet, für 16 bis 48 px)
    ps, rs = einpassen(small)
    d["small-entwurf.svg"] = svg_flach(ps, rs, "titan-impact", "tamil.de Signet Tamil Dots, klein (Entwurf)")
    # Mini (aus Small): Größenunterschiede gestaucht, damit auch der feine Auslauf bei 16–48 px sichtbar bleibt und
    # der Bogen mit der freien Fläche erkennbar ist; Punkte, die sich dann berühren würden, entfallen.
    for name, stauch, abstand in (("mini-entwurf.svg", 0.8, 1.05), ("mini-16-entwurf.svg", 0.6, 1.2)):
        pmi, rmi = einpassen(mini_aus(small, stauch, abstand), breite=48, rand=0.05)
        d[name] = svg_flach(pmi, rmi, "titan-impact", "tamil.de Signet Tamil Dots, Mini (Entwurf)")

    # 03 Spatial
    d["spatial.svg"] = svg_raeumlich(pm, rm, "tamil.de Signet Tamil Dots, räumlich (Entwurf)")

    # Aufbau-Animation und Variante C
    d["animiert.svg"] = svg_animiert(pm, rm, "tamil.de Signet Tamil Dots, Aufbau (Entwurf)")
    pc, rc = einpassen(unterste_reihe(master), rand=0.02)
    d["variante-c.svg"] = svg_variante_c(pc, rc, "tamil.de Tamil Dots, Variante C Welle (Entwurf)")
    d["animation.html"] = html_animation(d["animiert.svg"], d["variante-c.svg"])

    # Hintergründe (Vorschlag): dekorativ, transparent, Flächenfarbe kommt aus CSS
    for pfad, fassung, aus in [
        ("hintergrund/rubrikband-titan-auf-impact.svg", "titan-auf-impact", (0.0, 0.30, 0.66, 0.66)),
        ("hintergrund/rubrikband-weiss-auf-impact.svg", "weiss", (0.0, 0.30, 0.66, 0.66)),
        ("hintergrund/flaeche-impact-auf-titan.svg", "impact-auf-titan", None),
        ("hintergrund/kopf-hell-auf-weiss.svg", "hell", (0.0, 0.0, 1.0, 0.72)),
        ("hintergrund/fuss-hell-auf-weiss.svg", "hell", None),
    ]:
        pb, rb = einpassen(master, ausschnitt=aus)
        d[pfad] = "".join([kopf(rb)] + gruppen(pb, farbstufen(fassung)) + ["</svg>\n"])
    d["hintergrund/vorschau.html"] = html_hintergruende()
    return d


def main():
    ap = argparse.ArgumentParser(description="Tamil Dots 04A – Generator (Entwurf)")
    ap.add_argument("--liste", action="store_true", help="nur Übersicht ausgeben, nichts schreiben")
    ap.add_argument("--feld", default="master", choices=["master", "small"])
    ap.add_argument("--fassung", choices=sorted(FASSUNGEN), help="einzelne Datei in dieser Farbfassung")
    ap.add_argument("--ausschnitt", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"),
                    help="Ausschnitt in Anteilen der Formbox, z. B. 0 0 .6 1")
    ap.add_argument("--dekorativ", action="store_true", help="aria-hidden statt role=img")
    ap.add_argument("--aus", help="Ausgabedatei für --fassung (sonst Standardausgabe)")
    a = ap.parse_args()

    if a.fassung:
        pk, r = einpassen(lade(a.feld), ausschnitt=tuple(a.ausschnitt) if a.ausschnitt else None)
        text = svg_flach(pk, r, a.fassung, None if a.dekorativ else "tamil.de Signet Tamil Dots 04A (Entwurf)")
        if a.aus:
            with open(a.aus, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            print(text, end="")
        return

    for pfad, text in sorted(alle().items()):
        groesse = len(text.encode("utf-8"))
        if not a.liste:
            ziel = os.path.join(HIER, pfad)
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            with open(ziel, "w", encoding="utf-8") as f:
                f.write(text)
        warnung = "  ZU GROSS" if pfad.endswith(".svg") and groesse >= 30 * 1024 else ""
        print(f"{pfad:48} {text.count('<ellipse'):4} Ellipsen {groesse / 1024:6.1f} KB{warnung}")


if __name__ == "__main__":
    main()
