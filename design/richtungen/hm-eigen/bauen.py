"""Baut die Probe hm-eigen (Tagesblatt) aus echtem Material. Aufruf: python3 design/richtungen/hm-eigen/bauen.py"""
import datetime as dt
import html
import json
import pathlib
import re
import shutil
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "design/richtungen/hm-eigen"
INH = ROOT / "design/inhalte"
FONTS = pathlib.Path(__file__).resolve().parent / "_schriftquellen"  # nur zum Erneuern der Schriften (Fontsource-Pakete)
HEUTE = dt.date(2026, 11, 13)
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
FESTTAGE = {dt.date(2026, 1, 14): "Thai Pongal", dt.date(2026, 4, 14): "Tamilisches Neujahr", dt.date(2026, 11, 8): "Deepavali"}
e = html.escape

rb = json.loads((INH / "rueckblick/rueckblick.json").read_text(encoding="utf-8"))["beitraege"]
BEI = {b["story_id"]: b for b in rb}
inh = json.loads((INH / "inhalte.json").read_text(encoding="utf-8"))

# Jahreschronik aus der Stand-Doku (nur die Tabelle der wartenden Entwürfe, nicht „Recherche nötig“)
doku = (ROOT / "docs/redaktion/rueckblick-2026.md").read_text(encoding="utf-8")
teil = doku.split("## Entwürfe, die auf Freigabe warten")[1].split("## Recherche nötig")[0]
CHRONIK = []
for z in teil.splitlines():
    m = re.match(r"\| (2026-\d\d-\d\d) \| (\d+) \| \d+ \| (.+?) \| \d+ \|", z)
    if m:
        CHRONIK.append((dt.date.fromisoformat(m.group(1)), int(m.group(2)), m.group(3).strip()))

# Kommende Termine: nur belegtes Material
KOMMEND = [
    (dt.date(2026, 11, 15), "Deepavali-Feier des Düsseldorf Tamil Sangam", "Düsseldorf", "artikel.html"),
    (dt.date(2026, 11, 21), "Diwali in Basel mit dem Basel Tamil Sangam", "Aula Lysbüchel, Basel", None),
    (dt.date(2026, 12, 13), "THADAM 2026: Networking- und Gala-Nacht", "Bern", None),
]

def rot(d):
    return d.weekday() == 6 or d in FESTTAGE

def wa(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text + " | tamil.de")

def link_zu(sid):
    if sid == 30:
        return "artikel.html"
    return f"artikel-{sid}.html" if sid in BEI else None

def zeile(d, was, wo=None, href=None, teilen=True, heute=False, aside=False):
    klasse = " ".join(k for k in ("rot" if rot(d) else "", "heute" if heute else "") if k)
    z = f'<span class="z"><time datetime="{d.isoformat()}">{d.day}</time><small>{TAGE[d.weekday()][:2]}, {MONATE[d.month-1][:3]}{"." if len(MONATE[d.month-1])>3 else ""}</small></span>'
    w = f'<a href="{href}">{e(was)}</a>' if href else e(was)
    teile = [z, f'<span class="was">{w}</span>']
    if not aside:
        teile.append(f'<span class="wo">{e(wo or "")}</span>')
        if teilen:
            teile.append(f'<a class="teilen" href="{e(wa(was))}">Per WhatsApp schicken</a>')
    return f'<li{f" class=\"{klasse}\"" if klasse else ""}>{"".join(teile)}</li>'

def blatt(d, klein=False, extra=""):
    return (f'<p class="tag{" rot" if rot(d) else ""}"><time datetime="{d.isoformat()}"><span class="ziffer">{d.day}</span></time>'
            f'<span class="monat">{MONATE[d.month-1]} {d.year}</span><span class="wochentag">{TAGE[d.weekday()]}{extra}</span></p>')

def figur(b, cls="bild", lazy=True):
    from PIL import Image
    w, h = Image.open(INH / "rueckblick" / b["bild"]).size
    q = b.get("quelle_bild") or ""
    nach = e(b["nachweis"])
    return (f'<figure class="{cls}"><img src="{e(b["bild"])}" alt="{e(b["alt"])}" width="{w}" height="{h}"'
            f'{" loading=\"lazy\"" if lazy else " fetchpriority=\"high\""}>'
            f'<figcaption>{nach}{f" (<a href=\"{e(q)}\">Quelle</a>)" if q else ""}</figcaption></figure>')

NAV_R = ["Nachrichten", "Community", "Kultur", "Küche", "Sport"]

def kopf(aktiv=""):
    dien = "".join(f'<a href="{h}"{" aria-current=\"page\"" if aktiv == n else ""}>{n}</a>' for n, h in (("Termine", "termine.html"), ("Kino", "kino.html")))
    rub = "".join(f'<a href="index.html#{n.lower()}">{n}</a>' for n in NAV_R)
    rubm = "".join(f'<li><a href="index.html#{n.lower()}">{n}</a></li>' for n in NAV_R)
    return (f'<a class="skip" href="#inhalt">Zum Inhalt</a><header class="kopf"><div class="wrap">'
            f'<a class="logo" href="index.html" aria-label="tamil.de, zur Startseite"><img src="bilder/logo.png" alt="tamil.de" width="300" height="121"></a>'
            f'<nav class="rubriken" aria-label="Rubriken">{rub}</nav><nav class="dienste" aria-label="Dienste">{dien}</nav>'
            f'<details class="rubriken-mobil"><summary>Rubriken</summary><ul>{rubm}</ul></details></div></header>')

def fuss(nachweise):
    rub = "".join(f'<li><a href="index.html#{n.lower()}">{n}</a></li>' for n in NAV_R)
    nw = "".join(f'<li>{e(b["nachweis"])}, <a href="{e(b.get("quelle_bild",""))}">Wikimedia Commons</a></li>' for b in nachweise)
    return (f'<footer class="fuss"><div class="wrap"><div><img src="bilder/logo.png" alt="tamil.de" width="300" height="121" loading="lazy">'
            f'<p>Nachrichten, Termine und Kino der tamilischen Community in Deutschland, Österreich und der Schweiz.</p>'
            f'<p>Impressum und Kontakt folgen (Platzhalter).</p></div>'
            f'<div><h2>Rubriken</h2><ul>{rub}<li><a href="termine.html">Termine</a></li><li><a href="kino.html">Kino</a></li></ul></div>'
            f'<div><h2>Bildnachweise</h2><ul class="nachweise">{nw}</ul></div></div></footer>')

def seite(titel, beschreibung, body, aktiv=""):
    return (f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(titel)}</title><meta name="description" content="{e(beschreibung)}">'
            f'<link rel="preload" href="schriften/rethink-sans-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="stylesheet" href="hm-eigen.css"></head><body>{kopf(aktiv)}<main id="inhalt">{body}</main>')

def schreib(name, inhalt, nachweise):
    (OUT / name).write_text(inhalt + fuss(nachweise) + "</body></html>\n", encoding="utf-8")

# ---------- Startseite ----------
a = BEI[30]
naechst = KOMMEND[0][0]
bis = (naechst - HEUTE).days
hero = (f'<section class="blatt"><div class="wrap"><div>{blatt(HEUTE)}'
        f'<p class="bis">Noch {"zwei" if bis == 2 else bis} Tage bis zur Deepavali-Feier in Düsseldorf. <a href="termine.html">Zum Festkalender</a></p></div>'
        f'<article class="aufmacher"><h1>{e(a["titel"])}</h1>'
        f'<p class="vorspann">{e(a["teaser"])}</p>'
        f'<div class="aktionen"><a class="knopf" href="artikel.html">Beitrag lesen</a><a class="textlink" href="{e(wa(a["titel"]))}">Per WhatsApp schicken</a></div>'
        f'{figur(a, lazy=False)}</article></div></section>')

termine = (f'<section class="abschnitt" aria-labelledby="t-h"><div class="wrap"><div class="kopfzeile"><div><h2 id="t-h">Die nächsten Feste</h2>'
           f'<p class="satz">Was die Vereine angekündigt haben, Tag für Tag.</p></div><a class="mehr" href="termine.html">Ganzer Festkalender 2026</a></div>'
           f'<ul class="tage">{"".join(zeile(d, w, o, h) for d, w, o, h in KOMMEND)}</ul></div></section>')

kino = inh["diese_woche"]["kino"]
scene, rama = kino[0], kino[1]
kinoteil = (f'<section class="abschnitt feld" aria-labelledby="k-h"><div class="wrap"><h2 id="k-h" class="feld-titel">Tamilisches Kino diese Woche</h2>'
            f'<div class="plakat"><p class="film">{e(scene["titel"])}</p><div><p class="zahl">In {scene["kinos"]} Kinos</p>'
            f'<ul>{"".join(f"<li>{e(o)}</li>" for o in scene["orte"])}<li>und {scene["weitere_staedte"]} weiteren Städten</li></ul></div></div>'
            f'<div class="weiter"><div><h3>{e(rama["titel"])}</h3><p class="satz">In {e(" und ".join(rama["orte"]))}.</p></div>'
            f'<div><p class="klein">Stand: 9. November 2026, aus den Programmen der Kinos.</p><a class="textlink" href="kino.html">Alle Spielorte nach Stadt</a></div></div></div></section>')

def stories(ids):
    return [(dt.date.fromisoformat(BEI[i]["datum"]), i) for i in ids]

gem_ids = [71, 76, 49, 80, 60, 38]
gemeinde = (f'<section class="abschnitt" id="community" aria-labelledby="g-h"><div class="wrap paar">{figur(BEI[71])}'
            f'<div><h2 id="g-h">Tempel und Vereine</h2><p class="satz">Feste, Jubiläen und neue Räume der Gemeinden in diesem Jahr.</p>'
            f'<ul class="tage tage-luft">{"".join(zeile(d, BEI[i]["titel"], BEI[i]["ort"], link_zu(i), teilen=False) for d, i in sorted(stories(gem_ids), reverse=True))}</ul></div></div></section>')

nach_ids = [85, 87, 51]
nachrichten = (f'<section class="abschnitt mulde" id="nachrichten" aria-labelledby="n-h"><div class="wrap"><div class="kopfzeile"><h2 id="n-h">Nachrichten</h2></div>'
               f'<ul class="tage">{"".join(zeile(d, BEI[i]["titel"], BEI[i]["ort"], link_zu(i), teilen=False) for d, i in sorted(stories(nach_ids), reverse=True))}</ul></div></section>')

kue_ids = [37, 39, 48, 62]
kueche = (f'<section class="abschnitt" id="küche" aria-labelledby="ku-h"><div class="wrap paar"><div><h2 id="ku-h">Küche</h2>'
          f'<p class="satz">Restaurants, Läden und Feste rund ums Essen.</p>'
          f'<ul class="tage tage-luft">{"".join(zeile(d, BEI[i]["titel"], BEI[i]["ort"], link_zu(i), teilen=False) for d, i in sorted(stories(kue_ids), reverse=True))}</ul></div>'
          f'{figur(BEI[37])}</div></section>')

body = hero + termine + kinoteil + gemeinde + nachrichten + kueche
schreib("index.html", seite("tamil.de | Nachrichten, Termine und Kino der tamilischen Community", "Nachrichten, Termine und Kino der tamilischen Community in Deutschland, Österreich und der Schweiz.", body), [a, BEI[71], BEI[37]])

# ---------- Artikel ----------
def artikel(sid, name):
    b = BEI[sid]
    d = dt.date.fromisoformat(b["datum"])
    absz = "".join(f"<p>{e(p)}</p>" for p in b["absaetze"])
    kal = ""
    if sid == 30:
        kal = (f'<aside aria-labelledby="ak-h"><h2 id="ak-h">Im Kalender</h2><ul class="tage">'
               f'{"".join(zeile(dd, w, o, None, aside=True) for dd, w, o, _ in KOMMEND[:2])}</ul>'
               f'<p><a class="textlink" href="termine.html">Zum Festkalender</a></p></aside>')
    weiter_ids = [i for i in (33, 76, 71, 49, 60) if i != sid][:3]
    weiter = (f'<section class="abschnitt" aria-labelledby="w-h"><div class="wrap"><div class="kopfzeile"><h2 id="w-h">Weiterlesen</h2></div>'
              f'<ul class="tage">{"".join(zeile(dt.date.fromisoformat(BEI[i]["datum"]), BEI[i]["titel"], BEI[i]["ort"], link_zu(i), teilen=False) for i in weiter_ids)}</ul></div></section>')
    body = (f'<article><header class="artikel-kopf"><div class="wrap">{blatt(d, extra=(", " + FESTTAGE[d]) if d in FESTTAGE else "")}'
            f'<div><p class="ort">{e(b["ort"])}</p><h1>{e(b["titel"])}</h1><p class="vorspann">{e(b["teaser"])}</p>'
            f'<div class="aktionen"><a class="textlink" href="{e(wa(b["titel"]))}">Per WhatsApp teilen</a></div></div></div></header>'
            f'<div class="artikel-bild"><div class="wrap">{figur(b, lazy=False)}</div></div>'
            f'<div class="artikel-text"><div class="wrap"><div class="text">{absz}'
            f'<div class="teilen-block"><a class="knopf" href="{e(wa(b["titel"]))}">Per WhatsApp schicken</a><a class="textlink" href="termine.html">Festkalender 2026</a></div></div>{kal}</div></div></article>'
            + weiter)
    schreib(name, seite(f'{b["titel"]} | tamil.de', b["teaser"], body), [b])

artikel(30, "artikel.html")
for sid in BEI:
    if sid != 30:
        artikel(sid, f"artikel-{sid}.html")

# ---------- Termine ----------
mon = {}
for d, sid, titel in CHRONIK:
    mon.setdefault(d.month, []).append((d, sid, titel))
for d, w, o, h in KOMMEND:
    mon.setdefault(d.month, []).append((d, None, w))
leiste = "".join(f'<li><a href="#m{m}">{MONATE[m-1][:3]}</a></li>' for m in range(1, 13) if m in mon)
bloecke = ""
for m in sorted(mon):
    eintraege = sorted(mon[m], key=lambda x: x[0])
    zeilen = []
    heute_drin = False
    for d, sid, titel in eintraege:
        if m == 11 and not heute_drin and d > HEUTE:
            zeilen.append(zeile(HEUTE, "Heute", "", None, teilen=False, heute=True))
            heute_drin = True
        fest = FESTTAGE.get(d)
        wo = BEI[sid]["ort"] if sid in BEI else (next((o for dd, w, o, _ in KOMMEND if dd == d), "") if sid is None else "")
        if fest and sid is None:
            pass
        zeilen.append(zeile(d, titel, wo, link_zu(sid) if sid else ("artikel.html" if d == dt.date(2026, 11, 15) else None), teilen=d > HEUTE))
    bloecke += f'<section class="monat-block" id="m{m}" aria-labelledby="mh{m}"><h2 id="mh{m}">{MONATE[m-1]}</h2><ul class="tage">{"".join(zeilen)}</ul></section>'
termine_body = (f'<section class="blatt"><div class="wrap"><div><h1 class="seitentitel">Festkalender 2026</h1>'
                f'<p class="bis">Feste, Tempel, Vereine und Bühnen der tamilischen Community, Tag für Tag.</p>'
                f'<div class="aktionen"><a class="textlink" href="#m11">Zum November</a></div></div>'
                f'<div>{blatt(naechst, extra=", Düsseldorf")}<p class="bis">Deepavali-Feier des Düsseldorf Tamil Sangam.</p></div></div></section>'
                f'<section class="abschnitt" aria-label="Jahr 2026"><div class="wrap"><ul class="monate">{leiste}</ul>'
                f'<p class="legende"><b>Rot</b>: Sonntag oder Festtag (Thai Pongal, Tamilisches Neujahr, Deepavali).</p>{bloecke}</div></section>')
schreib("termine.html", seite("Festkalender 2026 | tamil.de", "Feste, Tempel, Vereine und Bühnen der tamilischen Community 2026, Tag für Tag.", termine_body, "Termine"), [])

# ---------- Kino ----------
staedte = [(o, scene["titel"]) for o in scene["orte"]] + [(o, rama["titel"]) for o in rama["orte"]]
kino_ids = [84, 43]
kinojahr = [(d, sid, t) for d, sid, t in CHRONIK if sid in (84, 43, 46, 64, 57, 94, 69, 66, 53)]
kino_body = (f'<section class="abschnitt feld oben"><div class="wrap">'
             f'<h1 class="seitentitel">Tamilisches Kino diese Woche</h1>'
             f'<p class="satz">Welcher Film in welcher Stadt läuft. Stand: 9. November 2026.</p>'
             f'<div class="aktionen"><a class="textlink" href="#staedte">Meine Stadt finden</a><a class="textlink" href="{e(wa("Tamilisches Kino diese Woche"))}">Per WhatsApp schicken</a></div>'
             f'<div class="plakat plakat-luft"><p class="film">{e(scene["titel"])}</p><div><p class="zahl">In {scene["kinos"]} Kinos</p>'
             f'<p class="klein">Fünf Städte sind bekannt, dazu {scene["weitere_staedte"]} weitere.</p></div></div></div></section>'
             f'<section class="abschnitt" id="staedte" aria-labelledby="s-h"><div class="wrap"><div class="kopfzeile"><h2 id="s-h">Nach Stadt</h2></div>'
             f'<ul class="staedte">{"".join(f"<li><span class=\"stadt\">{e(s)}</span><span>{e(f)}</span></li>" for s, f in sorted(staedte))}</ul>'
             f'<p class="satz">„{e(scene["titel"])}“ läuft außerdem in {scene["weitere_staedte"]} weiteren Städten.</p></div></section>'
             f'<section class="abschnitt" aria-labelledby="kj-h"><div class="wrap paar">{figur(BEI[84])}<div><h2 id="kj-h">Aus dem Kinojahr 2026</h2>'
             f'<ul class="tage tage-luft">{"".join(zeile(d, t, BEI[sid]["ort"] if sid in BEI else "", link_zu(sid), teilen=False) for d, sid, t in sorted(kinojahr, reverse=True))}</ul></div></div></section>')
schreib("kino.html", seite("Tamilisches Kino diese Woche | tamil.de", "Welcher tamilische Film in welcher Stadt läuft.", kino_body, "Kino"), [BEI[84]])

# Material kopieren
(OUT / "bilder").mkdir(exist_ok=True)
for b in rb:
    shutil.copy(INH / "rueckblick" / b["bild"], OUT / b["bild"])
shutil.copy(INH / "logo.png", OUT / "bilder/logo.png")
(OUT / "schriften").mkdir(exist_ok=True)
for f in FONTS.glob("*/package/files/*latin*wght-normal.woff2"):
    if "ext" in f.name or True:
        shutil.copy(f, OUT / "schriften" / f.name)
for lic in FONTS.glob("*/package/LICENSE"):
    shutil.copy(lic, OUT / "schriften" / (lic.parent.parent.name.split("-5")[0] + "-OFL.txt"))
print("ok", len(CHRONIK), "Chronik", len(list(OUT.glob("*.html"))), "Seiten")
