"""Baut die Linie hm-aushang (Arbeitstitel „Aushang“) aus echtem Material.

Aufruf vom Repo-Root: python3 design/richtungen/hm-aushang/bauen.py
Quellen: design/inhalte/rueckblick/rueckblick.json (Beiträge, Bilder, Nachweise), design/inhalte/inhalte.json (Kino,
Termin Basel), docs/redaktion/rueckblick-2026.md (Jahreschronik), docs/vertrag/festlegung-*.md (Formulare, Verzeichnis,
Werbeplätze). Nichts wird erfunden; fehlende Angaben stehen als sichtbarer Platzhalter.
"""
import datetime as dt
import html
import json
import pathlib
import re
import shutil
import urllib.parse

from PIL import Image

HIER = pathlib.Path(__file__).resolve().parent
ROOT = HIER.parents[2]
INH = ROOT / "design/inhalte"
SCHRIFT_QUELLE = pathlib.Path("/tmp/claude-0/-home-user/328bcd38-019d-5546-955b-7fea86a20fa1/scratchpad/fonts-aushang/package")
HEUTE = dt.date(2026, 11, 13)
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
FESTTAGE = {dt.date(2026, 1, 14): "Thai Pongal", dt.date(2026, 4, 14): "Tamilisches Neujahr", dt.date(2026, 11, 8): "Deepavali"}
WA_KANAL = "https://whatsapp.com/channel/0029VaFIN43KWEKo3BGoE13t"  # aus wordpress/plugins/tamil-site/includes/ads.php
e = html.escape

RB = json.loads((INH / "rueckblick/rueckblick.json").read_text(encoding="utf-8"))["beitraege"]
BEI = {b["story_id"]: b for b in RB}
INHALT = json.loads((INH / "inhalte.json").read_text(encoding="utf-8"))
KINO = INHALT["diese_woche"]["kino"]
BASEL = INHALT["diese_woche"]["termine"][0]

# Jahreschronik: Tabelle „Entwürfe, die auf Freigabe warten“
_doku = (ROOT / "docs/redaktion/rueckblick-2026.md").read_text(encoding="utf-8")
_teil = _doku.split("## Entwürfe, die auf Freigabe warten")[1].split("## Recherche nötig")[0]
CHRONIK = []
for _z in _teil.splitlines():
    _m = re.match(r"\| (2026-\d\d-\d\d) \| (\d+) \| \d+ \| (.+?) \| \d+ \|", _z)
    if _m:
        CHRONIK.append((dt.date.fromisoformat(_m.group(1)), int(_m.group(2)), _m.group(3).strip()))

# Kommende Termine, nur belegt: Artikel 30 (Düsseldorf), inhalte.json (Basel), wartende Radar-Entwürfe 4 und 5
KOMMEND = [
    dict(d=dt.date(2026, 11, 15), titel="Deepavali-Feier des Düsseldorf Tamil Sangam", ort="Düsseldorf", href="artikel.html"),
    dict(d=dt.date(2026, 11, 15), titel="„Jailer 2“ zum Spezialpreis im Kino Claudia", ort="Kloten", href="kino.html#kloten"),
    dict(d=dt.date(2026, 11, 21), titel="Diwali in Basel mit dem Basel Tamil Sangam", ort=BASEL["ort"], href=None),
    dict(d=dt.date(2026, 12, 13), titel="THADAM 2026: Tamilische Networking- und Gala-Nacht", ort="Bern", href=None),
]
NAECHSTER = min(k["d"] for k in KOMMEND)


# ---------------------------------------------------------------- Hilfen
def wa(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text + " | tamil.de")


def datum_lang(d, jahr=True):
    return f"{TAGE[d.weekday()]}, {d.day}.\u00a0{MONATE[d.month - 1]}" + (f"\u00a0{d.year}" if jahr else "")


def bis_wann(d):
    n = (d - HEUTE).days
    return {0: "Heute", 1: "Morgen", 2: "Übermorgen"}.get(n, f"In {n} Tagen")


def link_zu(sid):
    if sid == 30:
        return "artikel.html"
    return f"artikel-{sid}.html" if sid in BEI else None


def bildmasse(datei):
    return Image.open(INH / "rueckblick" / datei).size


def figur(b, cls="bild", prio=False, sizes="(min-width: 64rem) 50vw, 100vw", fakt=None):
    w, h = bildmasse(b["bild"])
    fakt = fakt or ""
    quelle = b.get("quelle_bild")
    nach = e(b["nachweis"])
    if quelle:
        nach = f'<a href="{e(quelle)}">{nach}</a>'
    lade = ' fetchpriority="high"' if prio else ' loading="lazy"'
    return (f'<figure class="{cls}"><div class="rahmen"><img src="{e(b["bild"])}" alt="{e(b["alt"])}" width="{w}" height="{h}" sizes="{sizes}"{lade}></div>'
            f'<figcaption>{(e(fakt) + " ") if fakt else ""}<span class="nachweis">{nach}</span></figcaption></figure>')


def datumsblock(d, extra=None, naechster=False):
    zusatz = f"<span>{e(extra)}</span>" if extra else ""
    return (f'<time class="datum{" datum--naechster" if naechster else ""}" datetime="{d.isoformat()}">'
            f'<span class="ziffer">{d.day}</span><span class="mw"><span class="monat">{MONATE[d.month - 1]}</span>'
            f'<span class="wochentag">{TAGE[d.weekday()]}</span>{zusatz}</span></time>')


def notiz(d, titel, ort=None, href=None, teilen=False, zustand=None, rot=False, fest=None, klasse=""):
    t = f'<a href="{e(href)}">{e(titel)}</a>' if href else e(titel)
    zeilen = [datumsblock(d, naechster=rot), f'<div class="notiz-text"><h3>{t}</h3>']
    unter = []
    if fest:
        unter.append(f'<span class="fest">Festtag: {e(fest)}</span>')
    if ort:
        unter.append(f'<span class="ort">{e(ort)}</span>')
    if unter:
        zeilen.append(f'<p class="notiz-ort">{"".join(unter)}</p>')
    zeilen.append("</div>")
    if zustand:
        zeilen.append(f'<p class="zustand{" zustand--signal" if rot else ""}">{e(zustand)}</p>')
    if teilen:
        zeilen.append(f'<a class="teilen" href="{e(wa(titel + ", " + datum_lang(d, False) + (", " + ort if ort else "")))}">Per WhatsApp schicken</a>')
    k = " ".join(x for x in ("notiz", klasse) if x)
    return f'<li class="{k}">{"".join(zeilen)}</li>'


NAV = [("Nachrichten", "index.html#nachrichten"), ("Community", "rubrik.html"), ("Kultur", "index.html#kultur"),
       ("Küche", "index.html#kueche"), ("Kino", "kino.html"), ("Termine", "termine.html"), ("Verzeichnis", "verzeichnis.html")]


def kopf(aktiv=""):
    def li(n, h):
        cur = ' aria-current="page"' if n == aktiv else ""
        return f'<li><a href="{h}"{cur}>{n}</a></li>'
    links = "".join(li(n, h) for n, h in NAV)
    k = KOMMEND[0]
    return (f'<a class="skip" href="#inhalt">Zum Inhalt</a>'
            f'<header class="kopf"><div class="naechstes"><div class="container"><p>Als Nächstes: '
            f'<time datetime="{k["d"].isoformat()}">{datum_lang(k["d"], False)}</time>, Deepavali-Feier in {e(k["ort"])}. '
            f'<a href="termine.html">Zum Festkalender</a></p></div></div>'
            f'<div class="leiste"><div class="container leiste-innen">'
            f'<a class="logo" href="index.html" aria-label="tamil.de, zur Startseite"><img src="bilder/logo.png" alt="tamil.de" width="300" height="121"></a>'
            f'<nav class="hauptnav" aria-label="Rubriken"><ul>{links}</ul></nav>'
            f'<a class="btn btn--still kopf-aktion" href="einreichen.html">Termin einreichen</a>'
            f'<details class="menue"><summary>Menü</summary><nav aria-label="Rubriken"><ul>{links}<li><a href="einreichen.html">Termin einreichen</a></li></ul></nav></details>'
            f'</div></div></header>')


def fuss():
    links = [("Termine", "termine.html"), ("Kino", "kino.html"), ("Verzeichnis", "verzeichnis.html"), ("Termin einreichen", "einreichen.html"),
             ("Werben", "werben.html"), ("Kontakt", "kontakt.html"), ("Impressum", "kontakt.html#impressum")]
    li = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in links)
    return (f'<footer class="fuss"><div class="container fuss-innen">'
            f'<a class="logo" href="index.html" aria-label="tamil.de, zur Startseite"><img src="bilder/logo.png" alt="tamil.de" width="300" height="121" loading="lazy"></a>'
            f'<p class="fuss-satz">tamil.de ist das Nachrichten- und Terminblatt der tamilischen Gemeinden in Deutschland, Österreich und der Schweiz. '
            f'Die Bildnachweise stehen an jedem Bild. Impressum und Datenschutzerklärung folgen, sobald KBS sie liefert.</p>'
            f'<nav aria-label="Seiten"><ul class="fuss-links">{li}</ul></nav></div></footer>')


def seite(name, titel, beschreibung, body, aktiv="", extra_css=None, skript=False):
    css = '<link rel="stylesheet" href="hm-aushang.css">' + (f'<link rel="stylesheet" href="{extra_css}">' if extra_css else "")
    js = '<script src="aushang.js" defer></script>' if skript else ""
    doc = (f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
           f'<title>{e(titel)}</title><meta name="description" content="{e(beschreibung)}">'
           f'<link rel="preload" href="schriften/epilogue-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
           f'{css}<script>document.documentElement.classList.add("js")</script>{js}</head>'
           f'<body>{kopf(aktiv)}<main id="inhalt">{body}</main>{fuss()}</body></html>\n')
    (HIER / name).write_text(doc, encoding="utf-8")


def anzeige(platz, ziel, titel, satz, extern=False):
    ext = ' rel="noopener"' if extern else ""
    return (f'<aside class="anzeige anzeige--{platz}" aria-label="Anzeige"><p class="anzeige-marke">Anzeige</p>'
            f'<a class="anzeige-flaeche" href="{e(ziel)}"{ext}><span class="anzeige-titel">{e(titel)}</span>'
            f'<span class="anzeige-satz">{e(satz)}</span></a></aside>')


def datum_iso(sid):
    return dt.date.fromisoformat(BEI[sid]["datum"])


# ---------------------------------------------------------------- Startseite
def startseite():
    a = BEI[30]
    hero = (f'<section class="aufmacher" aria-labelledby="h-auf"><div class="container aufmacher-raster">'
            f'<div class="aufmacher-text"><h1 id="h-auf">{e(a["titel"])}</h1>'
            f'<p class="lead">Tempel und Vereine feierten am 8.\u00a0November, Düsseldorf folgt am\u00a015.</p>'
            f'<div class="aktionen"><a class="btn" href="artikel.html">Beitrag lesen</a>'
            f'<a class="btn btn--still" href="{e(wa(a["titel"]))}">Per WhatsApp schicken</a></div></div>'
            f'{figur(a, "bild bild--aufmacher", prio=True, sizes="(min-width: 64rem) 55vw, 100vw", fakt="Sri Ganesha Hindu Temple an der Hasenheide, Berlin.")}'
            f'</div></section>')

    zeilen = "".join(notiz(k["d"], k["titel"], k["ort"], k["href"], teilen=True, zustand=bis_wann(k["d"]), rot=k["d"] == NAECHSTER) for k in KOMMEND)
    aushang = (f'<section class="abschnitt" aria-labelledby="h-aus"><div class="container">'
               f'<div class="kopfblock kopfblock--geteilt"><h2 id="h-aus">Was als Nächstes aushängt</h2>'
               f'<p class="lead">Feste, Abende und Vorstellungen, die Vereine und Kinos angekündigt haben.</p></div>'
               f'<ol class="tafel">{zeilen}</ol>'
               f'<p class="weiter"><a href="termine.html">Ganzer Festkalender 2026</a><a href="einreichen.html">Termin einreichen</a></p></div></section>')

    n_ids = [85, 87, 51]
    lead = BEI[85]
    nachrichten = (f'<section class="abschnitt" id="nachrichten" aria-labelledby="h-nach"><div class="container">'
                   f'<div class="kopfblock"><h2 id="h-nach">Nachrichten</h2>'
                   f'<p class="lead">Was Behörden in Deutschland, der Schweiz und Sri Lanka entschieden haben.</p></div>'
                   f'<div class="paar paar--7-5"><article class="stueck">{figur(lead, "bild bild--breit", sizes="(min-width: 64rem) 55vw, 100vw")}'
                   f'<h3><a href="{link_zu(85)}">{e(lead["titel"])}</a></h3><p class="stueck-satz">{e(lead["teaser"].split(". ")[0])}.</p>'
                   f'<p class="meta"><time datetime="{lead["datum"]}">{datum_lang(datum_iso(85))}</time></p></article>'
                   f'<ol class="tafel tafel--knapp">{"".join(notiz(datum_iso(i), BEI[i]["titel"], BEI[i]["ort"], link_zu(i)) for i in n_ids[1:])}</ol>'
                   f'</div></div></section>')

    scene, rama = KINO
    def film(f, zustand):
        orte = "".join(f"<li>{e(o)}</li>" for o in f["orte"])
        weitere = f'<li>und {f["weitere_staedte"]} weitere Städte</li>' if f["weitere_staedte"] else ""
        return (f'<article class="film"><h3>{e(f["titel"])}</h3><p class="film-zahl"><span class="figur">{f["kinos"]}</span> '
                f'{"Kinos" if f["kinos"] != 1 else "Kino"}</p><p class="zustand zustand--signal">{zustand}</p>'
                f'<ul class="orte">{orte}{weitere}</ul></article>')
    kino = (f'<section class="abschnitt abschnitt--well" aria-labelledby="h-kino"><div class="container paar paar--4-8">'
            f'<div class="kopfblock kopfblock--seite"><h2 id="h-kino">Tamilisches Kino diese Woche</h2>'
            f'<p class="lead">Aus den Programmen der Kinos, Stand 9. November 2026.</p>'
            f'<p class="weiter"><a href="kino.html">Alle Spielorte nach Stadt</a></p></div>'
            f'<div class="filme">{film(scene, "Läuft")}{film(rama, "Läuft")}</div></div></section>')

    c_ids = [38, 71, 76, 49, 60]
    community = (f'<section class="abschnitt" id="community" aria-labelledby="h-com"><div class="container">'
                 f'<div class="kopfblock kopfblock--geteilt"><h2 id="h-com">Community</h2>'
                 f'<p class="lead">Tempel, Vereine und Schulen der Gemeinden in diesem Jahr.</p></div>'
                 f'<div class="paar paar--7-5"><ol class="tafel">{"".join(notiz(datum_iso(i), BEI[i]["titel"], BEI[i]["ort"], link_zu(i)) for i in c_ids)}</ol>'
                 f'{figur(BEI[71], "bild bild--hoch", sizes="(min-width: 64rem) 40vw, 100vw", fakt="Sri-Kamadchi-Ampal-Tempel, Hamm-Uentrop.")}</div>'
                 f'<p class="weiter"><a href="rubrik.html">Alle Beiträge aus der Community</a></p></div></section>')

    werbung = (f'<div class="abschnitt abschnitt--knapp"><div class="container">'
               f'{anzeige("billboard", "einreichen.html", "Event melden: Dein Fest im Kalender", "Vereine und Tempel tragen ihre Termine selbst ein.")}</div></div>')

    k_ids = [37, 62, 39]
    ku_ids = [33, 83, 67, 78]
    rubriken = (f'<section class="abschnitt" aria-labelledby="h-rub"><div class="container">'
                f'<div class="kopfblock"><h2 id="h-rub">Küche, Kultur und Sport</h2></div>'
                f'<div class="paar paar--7-5"><div id="kueche" class="spalte">{figur(BEI[48], "bild bild--breit", sizes="(min-width: 64rem) 55vw, 100vw")}'
                f'<h3 class="spalte-titel"><a href="{link_zu(48)}">{e(BEI[48]["titel"])}</a></h3>'
                f'<ol class="tafel tafel--knapp">{"".join(notiz(datum_iso(i), BEI[i]["titel"], BEI[i]["ort"], link_zu(i)) for i in k_ids)}</ol></div>'
                f'<div id="kultur" class="spalte"><ol class="tafel tafel--knapp">{"".join(notiz(datum_iso(i), BEI[i]["titel"], BEI[i]["ort"], link_zu(i)) for i in ku_ids)}</ol></div>'
                f'</div></div></section>')

    verz = [v for v in VERZ if v["slug"] in ("sri-ganesha", "ceylon-palace", "tamilschule-aarau")]
    schluss = (f'<section class="abschnitt abschnitt--well abschnitt--schluss" aria-labelledby="h-verz"><div class="container paar paar--5-7">'
               f'<div class="kopfblock kopfblock--seite"><h2 id="h-verz">Tempel, Vereine und Läden finden</h2>'
               f'<p class="lead">Das Verzeichnis nach Art und Ort, für Deutschland, Österreich und die Schweiz.</p>'
               f'<div class="aktionen"><a class="btn btn--still" href="verzeichnis.html">Ins Verzeichnis</a></div></div>'
               f'<ul class="eintraege">{"".join(eintrag_zeile(v) for v in verz)}</ul></div></section>')

    body = hero + aushang + nachrichten + kino + community + werbung + rubriken + schluss
    seite("index.html", "tamil.de: Nachrichten, Termine und Kino der tamilischen Gemeinden",
          "Nachrichten, Feste, Kino und Verzeichnis der tamilischen Gemeinden in Deutschland, Österreich und der Schweiz.", body)


# ---------------------------------------------------------------- Artikel
def artikel(sid, name):
    b = BEI[sid]
    d = datum_iso(sid)
    absz = [f"<p>{e(p)}</p>" for p in b["absaetze"]]
    if len(absz) > 2:
        absz.insert(2, anzeige("inarticle", WA_KANAL, "tamil.de auf WhatsApp", "Neue Beiträge und Termine direkt im Kanal.", extern=True))
    kal = ""
    if sid == 30:
        kal = (f'<aside class="randspalte" aria-label="Im Kalender"><p class="rand-titel">Im Kalender</p>'
               f'<ol class="tafel tafel--knapp">{notiz(KOMMEND[0]["d"], KOMMEND[0]["titel"], KOMMEND[0]["ort"], None, teilen=True, zustand=bis_wann(KOMMEND[0]["d"]), rot=True)}</ol>'
               f'<p class="weiter"><a href="termine.html">Ganzer Festkalender 2026</a></p></aside>')
    else:
        kal = (f'<aside class="randspalte" aria-label="Als Nächstes"><p class="rand-titel">Als Nächstes</p>'
               f'<ol class="tafel tafel--knapp">{notiz(KOMMEND[0]["d"], KOMMEND[0]["titel"], KOMMEND[0]["ort"], "artikel.html", zustand=bis_wann(KOMMEND[0]["d"]), rot=True)}</ol>'
               f'<p class="weiter"><a href="termine.html">Ganzer Festkalender 2026</a></p></aside>')
    weiter_ids = [i for i in (49, 33, 71, 76, 60) if i != sid][:3]
    weiter = (f'<section class="abschnitt" aria-labelledby="h-weiter"><div class="container">'
              f'<div class="kopfblock"><h2 id="h-weiter">Weiterlesen</h2></div>'
              f'<ol class="tafel">{"".join(notiz(datum_iso(i), BEI[i]["titel"], BEI[i]["ort"], link_zu(i)) for i in weiter_ids)}</ol></div></section>')
    fest = FESTTAGE.get(d)
    body = (f'<article class="artikel"><header class="artikel-kopf"><div class="container">'
            f'<h1>{e(b["titel"])}</h1><p class="lead">{e(b["teaser"])}</p>'
            f'<div class="aktionen aktionen--artikel"><a class="btn btn--still" href="{e(wa(b["titel"]))}">Per WhatsApp schicken</a>'
            f'<p class="meta"><time datetime="{d.isoformat()}">{datum_lang(d)}</time>{(", " + e(fest)) if fest else ""}<br>{e(b["ort"])}</p></div></div></header>'
            f'<div class="container">{figur(b, "bild bild--artikel", prio=True, sizes="(min-width: 64rem) 66vw, 100vw")}</div>'
            f'<div class="container artikel-raster"><div class="text">{"".join(absz)}'
            f'<p class="teilen-zeile"><a class="btn" href="{e(wa(b["titel"]))}">Per WhatsApp schicken</a></p></div>{kal}</div></article>'
            + weiter)
    seite(name, f'{b["titel"]} | tamil.de', b["teaser"], body, extra_css="wortlaut.css")


# ---------------------------------------------------------------- Rubrik Community
COMMUNITY_SEITE1 = [38, 71, 76, 49, 80]
COMMUNITY_SEITE2 = [60]
# ältere Community-Titel aus der Chronik (Entwürfe ohne Bild in diesem Material); Zuordnung zur Rubrik durch diese Probe
COMMUNITY_ALT = [40, 42, 47, 50, 54, 59, 61, 68, 77, 79, 81, 98, 100]


def seitennav(aktuell):
    def l(n):
        href = "rubrik.html" if n == 1 else "rubrik-2.html"
        cur = ' aria-current="page"' if n == aktuell else ""
        return f'<li><a href="{href}"{cur}>Seite {n}</a></li>'
    vor = '<a class="btn btn--still" href="rubrik-2.html">Ältere Beiträge</a>' if aktuell == 1 else '<a class="btn btn--still" href="rubrik.html">Neuere Beiträge</a>'
    return f'<nav class="seitennav" aria-label="Seiten der Rubrik"><ul>{l(1)}{l(2)}</ul>{vor}</nav>'


def rubrik_zeile(sid):
    b = BEI[sid]
    d = datum_iso(sid)
    return (f'<li class="rubrik-zeile">{figur(b, "bild bild--klein", sizes="(min-width: 64rem) 25vw, 100vw")}'
            f'<div class="rubrik-text">{datumsblock(d)}<div><h3><a href="{link_zu(sid)}">{e(b["titel"])}</a></h3>'
            f'<p class="stueck-satz">{e(b["teaser"].split(". ")[0])}.</p><p class="notiz-ort"><span class="ort">{e(b["ort"])}</span></p></div></div></li>')


def rubrik():
    lead = BEI[COMMUNITY_SEITE1[0]]
    d = datum_iso(lead["story_id"])
    kopf_ = (f'<section class="seitenkopf" aria-labelledby="h-rub"><div class="container kopfblock kopfblock--geteilt">'
             f'<h1 id="h-rub">Community</h1><p class="lead">Tempel, Vereine, Schulen und Feste der Gemeinden in Deutschland, Österreich und der Schweiz.</p></div></section>')
    aufm = (f'<section class="abschnitt abschnitt--direkt" aria-label="Neuester Beitrag"><div class="container paar paar--7-5">'
            f'{figur(lead, "bild bild--breit", prio=True, sizes="(min-width: 64rem) 55vw, 100vw")}'
            f'<div class="stueck stueck--gross">{datumsblock(d)}<h2 class="stueck-titel"><a href="{link_zu(lead["story_id"])}">{e(lead["titel"])}</a></h2>'
            f'<p class="stueck-satz">{e(lead["teaser"])}</p><p class="notiz-ort"><span class="ort">{e(lead["ort"])}</span></p></div></div></section>')
    liste = (f'<section class="abschnitt" aria-labelledby="h-mehr"><div class="container">'
             f'<div class="kopfblock"><h2 id="h-mehr">Aus den Gemeinden</h2></div>'
             f'<ol class="rubrik-liste">{"".join(rubrik_zeile(i) for i in COMMUNITY_SEITE1[1:])}</ol>{seitennav(1)}</div></section>')
    termine = [k for k in KOMMEND if "Kino" not in k["titel"] and "Jailer" not in k["titel"]][:2]
    bord = (f'<section class="abschnitt abschnitt--well" aria-labelledby="h-gt"><div class="container paar paar--4-8">'
            f'<div class="kopfblock kopfblock--seite"><h2 id="h-gt">Feste der Gemeinden</h2><p class="lead">Die nächsten Termine der Vereine.</p>'
            f'<p class="weiter"><a href="termine.html">Ganzer Festkalender 2026</a></p></div>'
            f'<ol class="tafel">{"".join(notiz(k["d"], k["titel"], k["ort"], k["href"], teilen=True, zustand=bis_wann(k["d"]), rot=k["d"] == NAECHSTER) for k in termine)}</ol></div></section>')
    seite("rubrik.html", "Community | tamil.de", "Tempel, Vereine, Schulen und Feste der tamilischen Gemeinden.", kopf_ + aufm + liste + bord, aktiv="Community")

    # Seite 2
    alt = sorted([(d, sid, t) for d, sid, t in CHRONIK if sid in COMMUNITY_ALT], reverse=True)
    kopf2 = (f'<section class="seitenkopf" aria-labelledby="h-rub2"><div class="container kopfblock kopfblock--geteilt">'
             f'<h1 id="h-rub2">Community, Seite 2</h1><p class="lead">Ältere Beiträge aus den Gemeinden, die neuesten zuerst.</p></div></section>')
    liste2 = (f'<section class="abschnitt abschnitt--direkt" aria-label="Beiträge"><div class="container">'
              f'<ol class="rubrik-liste">{"".join(rubrik_zeile(i) for i in [80] + COMMUNITY_SEITE2)}</ol>'
              f'<ol class="tafel tafel--knapp">{"".join(notiz(d, t) for d, sid, t in alt)}</ol>{seitennav(2)}</div></section>')
    seite("rubrik-2.html", "Community, Seite 2 | tamil.de", "Ältere Beiträge aus den tamilischen Gemeinden.", kopf2 + liste2, aktiv="Community", extra_css="wortlaut.css")


# ---------------------------------------------------------------- Termine
def termine():
    zeilen = "".join(notiz(k["d"], k["titel"], k["ort"], k["href"], teilen=True, zustand=bis_wann(k["d"]), rot=k["d"] == NAECHSTER) for k in KOMMEND)
    kopf_ = (f'<section class="seitenkopf" aria-labelledby="h-fk"><div class="container kopfblock kopfblock--geteilt">'
             f'<h1 id="h-fk">Festkalender 2026</h1><p class="lead">Feste, Tempel, Vereine und Bühnen der tamilischen Gemeinden, Tag für Tag.</p></div></section>'
             f'<section class="abschnitt abschnitt--direkt" aria-labelledby="h-komm"><div class="container">'
             f'<div class="kopfblock"><h2 id="h-komm">Kommende Termine</h2></div><ol class="tafel">{zeilen}</ol>'
             f'<p class="weiter"><a href="einreichen.html">Termin einreichen</a></p></div></section>')
    mon = {}
    for d, sid, titel in CHRONIK:
        mon.setdefault(d.month, []).append((d, sid, titel))
    leiste = "".join(f'<li><a href="#m{m}">{MONATE[m - 1]}</a></li>' for m in range(1, 13) if m in mon)
    bloecke = ""
    for m in sorted(mon, reverse=True):
        zeilen = []
        eintraege = sorted(mon[m], key=lambda x: (x[0], x[1]), reverse=True)
        for d, sid, titel in eintraege:
            ort = BEI[sid]["ort"] if sid in BEI else None
            zeilen.append(notiz(d, titel, ort, link_zu(sid), fest=FESTTAGE.get(d)))
        if m == 11:
            zeilen.insert(0, f'<li class="heute"><span>Heute, {datum_lang(HEUTE, False)}</span></li>')
        bloecke += (f'<section class="monat" id="m{m}" aria-labelledby="mh{m}"><h3 id="mh{m}" class="monat-titel">{MONATE[m - 1]}</h3>'
                    f'<ol class="tafel tafel--knapp">{"".join(zeilen)}</ol></section>')
    jahr = (f'<section class="abschnitt" aria-labelledby="h-jahr"><div class="container">'
            f'<div class="kopfblock kopfblock--geteilt"><h2 id="h-jahr">Das Jahr 2026</h2>'
            f'<p class="lead">Was die Redaktion 2026 berichtet hat, die jüngsten Monate zuerst. Festtage sind vermerkt.</p></div>'
            f'<nav class="monate" aria-label="Monate"><ul>{leiste}</ul></nav>{bloecke}</div></section>')
    seite("termine.html", "Festkalender 2026 | tamil.de", "Feste, Tempel, Vereine und Bühnen der tamilischen Gemeinden 2026, Tag für Tag.",
          kopf_ + jahr, aktiv="Termine", extra_css="wortlaut.css")


# ---------------------------------------------------------------- Kino
def kino():
    scene, rama = KINO
    staedte = [(o, scene, "Deutschland") for o in scene["orte"]] + [(o, rama, "Deutschland") for o in rama["orte"]]
    staedte.sort(key=lambda x: x[0])
    def zeile(stadt, f, land):
        andere = "in 11 Kinos" if f["kinos"] == 11 else f"in {f['kinos']} Kinos"
        return (f'<li class="stadt" data-stadt="{e(stadt.lower())}"><h3 class="stadt-name">{e(stadt)}</h3>'
                f'<div class="stadt-filme"><p class="stadt-film">{e(f["titel"])}</p><p class="notiz-ort"><span class="ort">{land}, {andere}</span></p></div>'
                f'<p class="zustand zustand--signal">Läuft</p></li>')
    kloten = (f'<li class="stadt" id="kloten" data-stadt="kloten"><h3 class="stadt-name">Kloten</h3>'
              f'<div class="stadt-filme"><p class="stadt-film">Jailer 2</p><p class="notiz-ort"><span class="ort">Schweiz, Kino Claudia, '
              f'am {datum_lang(dt.date(2026, 11, 15), False)} zum Spezialpreis</span></p></div><p class="zustand">{bis_wann(dt.date(2026, 11, 15))}</p></li>')
    kopf_ = (f'<section class="seitenkopf" aria-labelledby="h-kino"><div class="container kopfblock kopfblock--geteilt">'
             f'<h1 id="h-kino">Tamilisches Kino diese Woche</h1>'
             f'<div><p class="lead">Welcher Film in welcher Stadt läuft. Stand: 9. November 2026, aus den Programmen der Kinos.</p>'
             f'<div class="aktionen"><a class="btn btn--still" href="{e(wa("Tamilisches Kino diese Woche"))}">Per WhatsApp schicken</a></div></div></div></section>')
    liste = (f'<section class="abschnitt abschnitt--direkt" aria-labelledby="h-st"><div class="container">'
             f'<div class="kopfblock kopfblock--filter"><h2 id="h-st">Nach Stadt</h2>'
             f'<div class="feld feld--filter"><label for="stadt-suche">Ihre Stadt</label>'
             f'<input id="stadt-suche" type="search" name="stadt" autocomplete="address-level2" data-filter="#staedte" aria-describedby="stadt-hinweis">'
             f'<p class="hilfe" id="stadt-hinweis" aria-live="polite"></p></div></div>'
             f'<ol class="staedte" id="staedte">{"".join(zeile(*s) for s in staedte)}{kloten}</ol>'
             f'<p class="hinweis-satz">„{e(scene["titel"])}“ läuft in {scene["kinos"]} Kinos; {scene["weitere_staedte"]} der Städte sind in den Programmen noch nicht genannt.</p></div></section>')
    kino_ids = (84, 43, 46, 53, 57, 94, 64, 66, 69, 96)
    jahr = sorted([(d, sid, t) for d, sid, t in CHRONIK if sid in kino_ids], reverse=True)
    rueck = (f'<section class="abschnitt" aria-labelledby="h-kj"><div class="container">'
             f'<div class="kopfblock"><h2 id="h-kj">Aus dem Kinojahr 2026</h2></div>'
             f'<div class="paar paar--5-7">{figur(BEI[84], "bild bild--hoch", sizes="(min-width: 64rem) 40vw, 100vw", fakt="Karthi, Hauptdarsteller von „Sardar 2“.")}'
             f'<ol class="tafel tafel--knapp">{"".join(notiz(d, t, None, link_zu(sid)) for d, sid, t in jahr)}</ol></div></div></section>')
    seite("kino.html", "Tamilisches Kino diese Woche | tamil.de", "Welcher tamilische Film in welcher Stadt läuft.", kopf_ + liste + rueck,
          aktiv="Kino", skript=True)


# ---------------------------------------------------------------- Verzeichnis
LAENDER = {"DE": "Deutschland", "AT": "Österreich", "CH": "Schweiz"}
VERZ = [
    dict(slug="sri-ganesha", name="Sri Ganesha Hindu Temple", art="Tempel", kat="Hindu-Tempel", stadt="Berlin", region="Berlin", land="DE",
         lage="Volkspark Hasenheide, Neukölln", bild=49, belege=[49, 30],
         text="Hindu-Tempel am nordöstlichen Rand des Volksparks Hasenheide in Neukölln, benannt nach Ganesha. Geweiht am 7. Juni 2026 mit der Maha Kumbhabhishekam; gebaut wurde seit 2010, bezahlt aus Spenden. Zu Deepavali steht das Lichterfest mit Lakshmi Pooja im Kalender."),
    dict(slug="sivaalayam-muenchen", name="Sivaalayam-Tempel", art="Tempel", kat="Hindu-Tempel", stadt="München", region="Bayern", land="DE",
         lage=None, bild=None, belege=[30], text="Hindu-Tempel in München. Für Deepavali am 8. November 2026 hatte der Tempel Feierlichkeiten angekündigt."),
    dict(slug="kamadchi-hamm", name="Sri-Kamadchi-Ampal-Tempel", art="Tempel", kat="Hindu-Tempel", stadt="Hamm", region="Nordrhein-Westfalen", land="DE",
         lage="Uentrop", bild=71, belege=[71], text="Tempel der Göttin Kamadchi in Hamm-Uentrop. Zum Großen Tempelfest 2026 kam Bundespräsident Frank-Walter Steinmeier als Ehrengast."),
    dict(slug="sivan-kovil-glattbrugg", name="Arulmigu Sivan Kovil", art="Tempel", kat="Hindu-Tempel", stadt="Glattbrugg", region="Zürich", land="CH",
         lage=None, bild=76, belege=[76], text="Tempel bei Zürich zu Ehren von Linganatha Parameswarar und Parvathi Ambal. Das Jahresfest Mahotsavam war für den 19. bis 30. Juni 2026 angekündigt."),
    dict(slug="duesseldorf-tamil-sangam", name="Düsseldorf Tamil Sangam", art="Verein", kat="Kultur", stadt="Düsseldorf", region="Nordrhein-Westfalen", land="DE",
         lage=None, bild=None, belege=[30], text="Tamilischer Verein in Düsseldorf. Lädt am Sonntag, 15. November 2026, zur eigenen Deepavali-Feier ein."),
    dict(slug="tks-emsdetten", name="Tamilischer Kultur- und Sportverein (TKS e.V.)", art="Verein", kat="Kultur", stadt="Emsdetten", region="Nordrhein-Westfalen", land="DE",
         lage=None, bild=None, belege=[38], text="Gegründet 2025, mehr als 30 Mitglieder. Der Verein plant Feste zu Deepavali und Thai Pongal und sucht ein eigenes Vereinsheim."),
    dict(slug="munich-tamil-kudumbam", name="Munich Tamil Kudumbam e.V.", art="Verein", kat="Kultur", stadt="München", region="Bayern", land="DE",
         lage=None, bild=None, belege=[48], text="Verein in München. Lud am 20. Juni 2026 zum Namma Tamil Nadu Food Fest „Virunthombal 2026“ mit sechs Regionalküchen."),
    dict(slug="basel-tamil-sangam", name="Basel Tamil Sangam", art="Verein", kat="Kultur", stadt="Basel", region="Basel-Stadt", land="CH",
         lage=None, bild=None, belege=[], text="Verein in Basel. Lädt Familien am 21. November 2026 zur Diwali-Feier in die Aula Lysbüchel; Mitglieder erhalten Tickets günstiger."),
    dict(slug="tamilschule-aarau", name="Tamilschule Aarau", art="Verein", kat="Tamilschule", stadt="Aarau", region="Aargau", land="CH",
         lage=None, bild=60, belege=[60], text="Gegründet vor 30 Jahren von Parameswary Nadarajah. Heute unterrichten 13 Lehrpersonen 78 Kinder, vom Kindergarten bis zur neunten Klasse."),
    dict(slug="ceylon-palace", name="Ceylon Palace", art="Business", kat="Restaurant und Imbiss", stadt="Bremen", region="Bremen", land="DE",
         lage=None, bild=None, belege=[37], text="Restaurant mit Küche aus Sri Lanka von Suthakar Thiruchelvam und seinem Sohn Anoj. Auf der Karte: Currys, Biryani, Dosa, Idly, Kottu und Parotta."),
    dict(slug="aiya-zuerich", name="Restaurant AiYA", art="Business", kat="Restaurant und Imbiss", stadt="Zürich", region="Zürich", land="CH",
         lage="Langstrasse, nahe dem Limmatplatz", bild=None, belege=[62], text="Küche aus der Vanni-Region im Norden Sri Lankas, eröffnet im März 2026 von Saran und Anitha."),
    dict(slug="skt-boutique", name="SKT-Boutique", art="Business", kat="Textil und Schmuck", stadt="Zürich", region="Zürich", land="CH",
         lage="Hardturmstrasse", bild=None, belege=[39], text="Saris und Schmuck. Die Boutique zog laut Bericht von der Josefstrasse an die Hardturmstrasse; sie gehört zu SK Trading."),
    dict(slug="sk-trading", name="SK Trading", art="Business", kat="Lebensmittel", stadt="Zürich", region="Zürich", land="CH",
         lage="Quellenstrasse", bild=None, belege=[39], text="Supermarkt, gegründet in den Neunzigern von der Familie Kathirgamanathan."),
]


def eintrag_href(v):
    return "verzeichnis-eintrag.html" if v["slug"] == "sri-ganesha" else f"verzeichnis-{v['slug']}.html"


def eintrag_zeile(v):
    such = " ".join([v["name"], v["art"], v["kat"], v["stadt"], v["region"], LAENDER[v["land"]]]).lower()
    return (f'<li class="eintrag" data-art="{e(v["art"].lower())}" data-land="{v["land"]}" data-region="{e(v["region"])}" data-stadt="{e(v["stadt"])}" data-such="{e(such)}">'
            f'<h3><a href="{eintrag_href(v)}">{e(v["name"])}</a></h3>'
            f'<p class="eintrag-art">{e(v["art"])}<br><span>{e(v["kat"])}</span></p>'
            f'<p class="eintrag-ort">{e(v["stadt"])}<br><span>{e(v["region"])}, {LAENDER[v["land"]]}</span></p></li>')


def verzeichnis():
    regionen = sorted({v["region"] for v in VERZ})
    staedte = sorted({v["stadt"] for v in VERZ})
    opt = lambda werte: "".join(f'<option value="{e(w)}">{e(w)}</option>' for w in werte)
    arten = ["Alle", "Business", "Dienstleister", "Verein", "Tempel"]
    seg = "".join(f'<input type="radio" name="art" id="art-{a.lower()}" value="{"" if a == "Alle" else a.lower()}"{" checked" if a == "Alle" else ""}><label for="art-{a.lower()}">{a}</label>' for a in arten)
    kopf_ = (f'<section class="seitenkopf" aria-labelledby="h-vz"><div class="container kopfblock kopfblock--geteilt">'
             f'<h1 id="h-vz">Verzeichnis</h1><div><p class="lead">Tempel, Vereine, Geschäfte und Dienstleister der tamilischen Gemeinden. Jeder Eintrag ist von der Redaktion geprüft.</p>'
             f'<div class="aktionen"><a class="btn btn--still" href="kontakt.html#nachricht">Eintrag vorschlagen</a></div></div></div></section>')
    filter_ = (f'<form class="filter" action="verzeichnis.html" method="get" role="search" aria-label="Verzeichnis durchsuchen">'
               f'<div class="feld feld--breit"><label for="q">Suche</label><input id="q" name="q" type="search" autocomplete="off"></div>'
               f'<fieldset class="seg"><legend>Art</legend>{seg}</fieldset>'
               f'<div class="feld"><label for="land">Land</label><select id="land" name="land"><option value="">Alle Länder</option>'
               f'{"".join(f"<option value=\"{k}\">{n}</option>" for k, n in LAENDER.items())}</select></div>'
               f'<div class="feld"><label for="region">Bundesland oder Kanton</label><select id="region" name="region"><option value="">Alle</option>{opt(regionen)}</select></div>'
               f'<div class="feld"><label for="stadt">Stadt</label><select id="stadt" name="stadt"><option value="">Alle Städte</option>{opt(staedte)}</select></div>'
               f'<div class="feld feld--knopf"><button class="btn" type="submit">Einträge zeigen</button></div></form>')
    liste = (f'<section class="abschnitt abschnitt--direkt" aria-label="Einträge"><div class="container">{filter_}'
             f'<p class="zaehler" role="status" data-zaehler>{len(VERZ)} Einträge</p>'
             f'<ul class="eintraege eintraege--liste" id="eintraege">{"".join(eintrag_zeile(v) for v in VERZ)}</ul>'
             f'<div class="leer" data-leer hidden><p class="leer-titel">Für diese Auswahl gibt es noch keinen Eintrag.</p>'
             f'<p>Das Verzeichnis beginnt mit Einrichtungen, über die tamil.de 2026 berichtet hat. Wer fehlt, kann sich selbst eintragen lassen.</p>'
             f'<p><a href="kontakt.html#nachricht">Eintrag vorschlagen</a></p></div>'
             f'<p class="hinweis-satz">Kontaktdaten, Öffnungszeiten und Bilder tragen die Einrichtungen selbst ein; die Redaktion gibt jede Änderung frei.</p></div></section>')
    seite("verzeichnis.html", "Verzeichnis | tamil.de", "Tempel, Vereine, Geschäfte und Dienstleister der tamilischen Gemeinden in Deutschland, Österreich und der Schweiz.",
          kopf_ + liste, aktiv="Verzeichnis", skript=True)
    for v in VERZ:
        eintrag(v)


def eintrag(v):
    premium = v["slug"] == "sri-ganesha"
    marke = '<span class="marke">Premium</span>' if premium else ""
    premium_satz = ('<p class="hinweis-satz"><span class="fill">Beispielansicht der Premium-Markierung. Premium setzt nur die Verwaltung; '
                    'dieser Eintrag hat sie bisher nicht.</span></p>') if premium else ""
    def fehlt(was):
        return f'<span class="fill">{was}</span>'
    belege = "".join(f'<li><a href="{link_zu(i)}">{e(BEI[i]["titel"])}</a></li>' for i in v["belege"])
    if not belege and v["slug"] == "basel-tamil-sangam":
        belege = '<li><a href="termine.html">Diwali in Basel, Samstag, 21. November 2026</a></li>'
    bild = figur(BEI[v["bild"]], "bild bild--breit", prio=True, sizes="(min-width: 64rem) 50vw, 100vw") if v["bild"] else ""
    angaben = (f'<dl class="angaben">'
               f'<div><dt>Art</dt><dd>{e(v["art"])}, {e(v["kat"])}</dd></div>'
               f'<div><dt>Ort</dt><dd>{(e(v["lage"]) + "<br>") if v["lage"] else ""}{e(v["stadt"])}, {e(v["region"])}, {LAENDER[v["land"]]}</dd></div>'
               f'<div><dt>Telefon, E-Mail, Website</dt><dd>{fehlt("Noch nicht eingetragen")}</dd></div>'
               f'<div><dt>Öffnungszeiten</dt><dd>Nicht angegeben</dd></div></dl>')
    body = (f'<section class="seitenkopf" aria-labelledby="h-e"><div class="container"><p class="zurueck"><a href="verzeichnis.html">Zum Verzeichnis</a></p>'
            f'<div class="kopfblock kopfblock--geteilt"><div><h1 id="h-e">{e(v["name"])}</h1>{marke}</div>'
            f'<div><p class="lead">{e(v["text"])}</p>{premium_satz}</div></div></div></section>'
            f'<section class="abschnitt abschnitt--direkt" aria-label="Angaben"><div class="container paar {"paar--7-5" if bild else "paar--5-7"}">'
            f'{bild or ""}<div>{angaben}<div class="aktionen"><a class="btn btn--still" href="kontakt.html#nachricht">Änderung melden</a></div></div>'
            f'{"" if bild else "<div></div>"}</div></section>'
            f'<section class="abschnitt" aria-labelledby="h-bel"><div class="container"><div class="kopfblock"><h2 id="h-bel">In Beiträgen von tamil.de</h2></div>'
            f'<ul class="belege">{belege}</ul></div></section>')
    seite(eintrag_href(v), f'{v["name"]}, {v["stadt"]} | Verzeichnis | tamil.de', v["text"], body, aktiv="Verzeichnis")


# ---------------------------------------------------------------- Formulare
EINWILLIGUNG = ('<div class="feld feld--check"><input id="{p}-ok" name="einwilligung" type="checkbox" required>'
                '<label for="{p}-ok">Ich bin einverstanden, dass tamil.de meine Angaben verarbeitet, um die Einsendung zu bearbeiten. '
                '<span class="fill">Wortlaut der Einwilligung folgt von KBS</span>, mit Link zur Datenschutzerklärung.</label></div>')
FALLE = '<div class="falle" aria-hidden="true"><label for="{p}-web">Website</label><input id="{p}-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>'


def feld(fid, label, typ="text", pflicht=False, auto=None, hilfe=None, extra="", breit=False):
    req = " required" if pflicht else ""
    stern = ' <span class="pflicht">Pflicht</span>' if pflicht else ""
    ac = f' autocomplete="{auto}"' if auto else ""
    h = f'<p class="hilfe" id="{fid}-h">{hilfe}</p>' if hilfe else f'<p class="hilfe" id="{fid}-h"></p>'
    if typ == "textarea":
        ctrl = f'<textarea id="{fid}" name="{fid}" rows="6"{req} aria-describedby="{fid}-h"{extra}></textarea>'
    else:
        ctrl = f'<input id="{fid}" name="{fid}" type="{typ}"{req}{ac} aria-describedby="{fid}-h"{extra}>'
    return f'<div class="feld{" feld--breit" if breit else ""}"><label for="{fid}">{label}{stern}</label>{ctrl}{h}</div>'


def einreichen():
    land = ('<fieldset class="seg"><legend>Land <span class="pflicht">Pflicht</span></legend>'
            + "".join(f'<input type="radio" name="land" id="land-{k}" value="{k}" required><label for="land-{k}">{n}</label>' for k, n in LAENDER.items())
            + "</fieldset>")
    form = (f'<form class="formular" data-endpoint="" novalidate aria-labelledby="h-form">'
            f'<fieldset class="gruppe"><legend id="h-form">Der Termin</legend>'
            + feld("titel", "Titel", pflicht=True, breit=True)
            + feld("beginn", "Datum und Uhrzeit", "datetime-local", pflicht=True)
            + feld("ende", "Ende", "datetime-local")
            + feld("ort", "Ort mit Adresse", pflicht=True, auto="street-address", breit=True)
            + feld("stadt-ein", "Stadt", pflicht=True, auto="address-level2")
            + land
            + feld("veranstalter", "Veranstalter", pflicht=True, breit=True)
            + feld("beschreibung", "Beschreibung", "textarea", pflicht=True, breit=True, hilfe="Was, für wen, in welcher Sprache. Höchstens drei Links.")
            + feld("eintritt", "Eintritt", hilfe="Zum Beispiel frei, oder der Preis mit Währung.")
            + feld("ticket", "Ticket-Link", "url", auto="url")
            + feld("bild", "Bild", "file", hilfe="JPEG oder PNG, höchstens 5 MB.", extra=' accept="image/jpeg,image/png"', breit=True)
            + '<div class="feld feld--check feld--breit"><input id="bild-recht" name="bild_recht" type="checkbox"><label for="bild-recht">Ich darf dieses Bild verwenden und tamil.de zur Veröffentlichung überlassen.</label></div>'
            + '</fieldset><fieldset class="gruppe"><legend>Wer einreicht</legend>'
            + feld("name", "Name", pflicht=True, auto="name")
            + feld("email", "E-Mail", "email", pflicht=True, auto="email")
            + feld("telefon", "Telefon", "tel", auto="tel", hilfe="Freiwillig, für Rückfragen der Redaktion.")
            + EINWILLIGUNG.format(p="ev") + FALLE.format(p="ev")
            + '</fieldset><div class="absenden"><button class="btn" type="submit">Termin einreichen</button>'
            + '<p class="hilfe hilfe--form" aria-live="polite" data-meldung></p></div></form>')
    seite_ = (f'<section class="seitenkopf" aria-labelledby="h-ein"><div class="container kopfblock kopfblock--geteilt">'
              f'<h1 id="h-ein">Termin einreichen</h1><p class="lead">Die Redaktion prüft jeden Termin, bevor er im Festkalender aushängt.</p></div></section>'
              f'<section class="abschnitt abschnitt--direkt" aria-label="Formular"><div class="container paar paar--8-4">{form}'
              f'<aside class="randspalte" aria-label="So geht es weiter"><p class="rand-titel">So geht es weiter</p>'
              f'<ol class="schritte schritte--klein"><li>Sie bekommen auf der Seite eine Vorgangsnummer.</li>'
              f'<li>Die Redaktion prüft Datum, Ort und Angaben.</li><li>Nach der Freigabe steht der Termin im Festkalender.</li></ol>'
              f'<p class="rand-satz">Eine E-Mail schicken wir nicht. Bei Rückfragen meldet sich die Redaktion von Hand.</p>'
              f'<p class="weiter"><a href="kontakt.html#nachricht">Beitrag oder Thema vorschlagen</a><a href="werben.html">Werbung anfragen</a></p></aside>'
              f'</div></section>')
    seite("einreichen.html", "Termin einreichen | tamil.de", "Feste, Tempelfeste und Vereinsabende für den Festkalender von tamil.de einreichen.",
          seite_, skript=True)

    # Zustand nach dem Absenden
    danke = (f'<section class="seitenkopf" aria-labelledby="h-dk"><div class="container kopfblock kopfblock--geteilt">'
             f'<h1 id="h-dk">Danke, die Redaktion meldet sich.</h1>'
             f'<div><p class="lead">Ihr Termin ist eingegangen und wird geprüft. Bitte notieren Sie die Vorgangsnummer.</p>'
             f'<p class="vorgang"><span class="vorgang-label">Vorgangsnummer</span><span class="figur fill">T-2026-0000</span></p>'
             f'<p class="hinweis-satz">Ansicht nach dem Absenden. In dieser Probe ist das Formular nicht angeschlossen; die Nummer ist ein Platzhalter.</p></div></div></section>'
             f'<section class="abschnitt abschnitt--direkt" aria-labelledby="h-dw"><div class="container paar paar--5-7">'
             f'<div class="kopfblock kopfblock--seite"><h2 id="h-dw">Wie es weitergeht</h2></div>'
             f'<ol class="schritte"><li><strong>Prüfung.</strong> Die Redaktion liest Datum, Ort und Angaben.</li>'
             f'<li><strong>Freigabe.</strong> Erst danach steht der Termin im Festkalender.</li>'
             f'<li><strong>Rückfrage.</strong> Fehlt etwas, meldet sich die Redaktion von Hand; automatische E-Mails gibt es nicht.</li></ol></div></section>'
             f'<section class="abschnitt" aria-label="Weiter"><div class="container"><p class="weiter"><a href="termine.html">Zum Festkalender</a><a href="einreichen.html">Weiteren Termin einreichen</a></p></div></section>')
    seite("einreichen-danke.html", "Termin eingegangen | tamil.de", "Bestätigung nach dem Einreichen eines Termins.", danke)


PLAETZE = [
    dict(k="leaderboard", name="Leaderboard", wo="Unter der Navigation, auf allen Seiten", d=(728, 90), m=(320, 50)),
    dict(k="sidebar", name="Half Page", wo="In der Seitenspalte", d=(300, 600), m=None),
    dict(k="inarticle", name="Im Artikel", wo="Nach dem zweiten Absatz", d=(728, 90), m=(300, 250)),
    dict(k="billboard", name="Billboard", wo="Startseite, zwischen den Rubriken", d=(970, 250), m=(300, 250)),
    dict(k="footer", name="Fuß", wo="Über dem Fuß der Seite", d=(728, 90), m=(320, 100)),
    dict(k="mobile", name="Mobil", wo="Am Handy fest am unteren Rand", d=None, m=(320, 50)),
]
ERSTER_FREIER = dt.date(2026, 11, 17)  # Vorschlag F3: zwei Werktage Vorlauf ab heute; noch keine Buchung vorhanden


def masse(p):
    def kasten(wh, was):
        if not wh:
            return f'<div class="mass mass--leer"><span>{was}: nicht vorgesehen</span></div>'
        w, h = wh
        return (f'<div class="mass"><div class="mass-flaeche" style="--w:{w};--h:{h}" role="img" aria-label="{was}, {w} mal {h} Pixel"></div>'
                f'<span>{was}: {w} × {h}</span></div>')
    return f'<div class="masse">{kasten(p["d"], "Desktop")}{kasten(p["m"], "Handy")}</div>'


def werben():
    zeilen = "".join(
        f'<li class="platz"><h3>{p["name"]}</h3><p class="platz-wo">{p["wo"]}</p>{masse(p)}'
        f'<dl class="platz-daten"><div><dt>Preis</dt><dd><span class="fill">Preis folgt</span></dd></div>'
        f'<div><dt>Frei ab</dt><dd>{datum_lang(ERSTER_FREIER)}</dd></div></dl></li>' for p in PLAETZE)
    body = (f'<section class="seitenkopf" aria-labelledby="h-wb"><div class="container kopfblock kopfblock--geteilt">'
            f'<h1 id="h-wb">Werben auf tamil.de</h1><div><p class="lead">Sechs Plätze, gebucht für feste Tage und vor dem Start von Hand geprüft.</p>'
            f'<div class="aktionen"><a class="btn" href="buchen.html">Platz buchen</a><a class="btn btn--still" href="kontakt.html#nachricht">Werbung anfragen</a></div></div></div></section>'
            f'<section class="abschnitt abschnitt--direkt" aria-labelledby="h-pl"><div class="container">'
            f'<div class="kopfblock kopfblock--geteilt"><h2 id="h-pl">Die sechs Plätze</h2>'
            f'<p class="lead">Die Flächen sind maßstäblich gezeichnet. Preise je Laufzeit liefert KBS.</p></div>'
            f'<ol class="plaetze">{zeilen}</ol></div></section>'
            f'<section class="abschnitt abschnitt--well" aria-labelledby="h-ab"><div class="container">'
            f'<div class="kopfblock"><h2 id="h-ab">So läuft eine Buchung</h2></div>'
            f'<ol class="schritte schritte--quer"><li><strong>Platz und Laufzeit</strong> 7, 14 oder 30 Tage, nach Vorschlag.</li>'
            f'<li><strong>Startdatum</strong> Belegte Tage sind gesperrt.</li><li><strong>Ihre Angaben</strong> Firma, Rechnungsadresse, E-Mail.</li>'
            f'<li><strong>Werbemittel</strong> Bild für Desktop und Handy, dazu die Zieladresse.</li>'
            f'<li><strong>Bezahlen</strong> Bei Stripe; die Tage sind 35 Minuten reserviert.</li></ol></div></section>'
            f'<section class="abschnitt" aria-labelledby="h-da"><div class="container paar paar--5-7">'
            f'<div class="kopfblock kopfblock--seite"><h2 id="h-da">Nach der Zahlung</h2></div>'
            f'<dl class="angaben angaben--gross"><div><dt>Prüfung</dt><dd>KBS prüft jedes Werbemittel vor dem Start und gibt es frei oder lehnt mit Grund ab.</dd></div>'
            f'<div><dt>Ablehnung</dt><dd>Der volle Betrag wird über Stripe erstattet, die Tage sind wieder frei.</dd></div>'
            f'<div><dt>Laufzeit</dt><dd>Die Anzeige startet und endet nach Datum; danach steht wieder die Eigenanzeige.</dd></div>'
            f'<div><dt>Übersicht</dt><dd>Ein geheimer Link zeigt Prüfung, Zahlung, Einblendungen und Klicks, ohne Konto.</dd></div></dl></div></section>')
    seite("werben.html", "Werben auf tamil.de", "Werbeplätze, Maße und Ablauf der Buchung auf tamil.de.", body)


def kalender(jahr, monat, start, laenge):
    erster = dt.date(jahr, monat, 1)
    naechster = dt.date(jahr + (monat == 12), monat % 12 + 1, 1)
    tage = (naechster - erster).days
    kopf_ = "".join(f'<th scope="col"><abbr title="{t}">{t[:2]}</abbr></th>' for t in TAGE)
    zellen = ['<td></td>'] * erster.weekday()
    for n in range(1, tage + 1):
        d = dt.date(jahr, monat, n)
        gesperrt = d < start
        gewaehlt = start <= d < start + dt.timedelta(days=laenge)
        rid = f"tag-{d.isoformat()}"
        klasse = "gesperrt" if gesperrt else ("gewaehlt" if gewaehlt else "frei")
        zustand = "nicht buchbar" if gesperrt else ("gewählt" if gewaehlt else "frei")
        ctrl = (f'<input type="radio" name="start" id="{rid}" value="{d.isoformat()}"{" disabled" if gesperrt else ""}{" checked" if d == start else ""}>'
                f'<label for="{rid}"><span class="figur">{n}</span><span class="visually-hidden">. {MONATE[monat - 1]}, {zustand}</span></label>')
        zellen.append(f'<td class="{klasse}">{ctrl}</td>')
    while len(zellen) % 7:
        zellen.append('<td></td>')
    reihen = "".join("<tr>" + "".join(zellen[i:i + 7]) + "</tr>" for i in range(0, len(zellen), 7))
    return (f'<table class="kalender"><caption>{MONATE[monat - 1]} {jahr}</caption><thead><tr>{kopf_}</tr></thead><tbody>{reihen}</tbody></table>')


def buchen():
    plaetze = "".join(
        f'<input type="radio" name="platz" id="p-{p["k"]}" value="{p["k"]}"{" checked" if p["k"] == "billboard" else ""}>'
        f'<label for="p-{p["k"]}"><span class="wahl-name">{p["name"]}</span><span class="wahl-wo">{p["wo"]}</span></label>' for p in PLAETZE)
    laufzeit = "".join(f'<input type="radio" name="laufzeit" id="l-{n}" value="{n}"{" checked" if n == 14 else ""}><label for="l-{n}">{n} Tage</label>' for n in (7, 14, 30))
    ende = ERSTER_FREIER + dt.timedelta(days=13)
    form = (f'<form class="formular buchung" data-endpoint="" novalidate aria-label="Werbeplatz buchen"><ol class="buchung-schritte">'
            f'<li><fieldset class="gruppe"><legend>Platz und Laufzeit</legend><div class="wahl">{plaetze}</div>'
            f'<fieldset class="seg"><legend>Laufzeit, Vorschlag</legend>{laufzeit}</fieldset></fieldset></li>'
            f'<li><fieldset class="gruppe"><legend>Startdatum</legend>'
            f'<p class="rand-satz">Bis zum {datum_lang(ERSTER_FREIER - dt.timedelta(days=1), False)} ist nichts buchbar: Werbemittel brauchen zwei Werktage Vorlauf für die Prüfung. Alle späteren Tage sind frei.</p>'
            f'<div class="kalender-paar">{kalender(2026, 11, ERSTER_FREIER, 14)}{kalender(2026, 12, ERSTER_FREIER, 14)}</div>'
            f'<p class="legende">Schwarz ist der Starttag, grau hinterlegt sind die gebuchten Tage, durchgestrichen die Tage, die nicht buchbar sind.</p></fieldset></li>'
            f'<li><fieldset class="gruppe"><legend>Ihre Angaben</legend>'
            + feld("firma", "Firma", pflicht=True, auto="organization")
            + feld("person", "Ansprechperson", pflicht=True, auto="name")
            + feld("adresse", "Rechnungsadresse", "textarea", pflicht=True, breit=True)
            + feld("b-email", "E-Mail", "email", pflicht=True, auto="email")
            + feld("b-telefon", "Telefon", "tel", auto="tel")
            + feld("ust", "USt-ID", hilfe="Freiwillig.")
            + f'</fieldset></li>'
            f'<li><fieldset class="gruppe"><legend>Werbemittel</legend>'
            + feld("wm-desktop", "Bild für Desktop, 970 × 250", "file", pflicht=True, hilfe="JPEG oder PNG in genau diesen Maßen.", extra=' accept="image/jpeg,image/png"')
            + feld("wm-mobil", "Bild für das Handy, 300 × 250", "file", pflicht=True, hilfe="JPEG oder PNG in genau diesen Maßen.", extra=' accept="image/jpeg,image/png"')
            + feld("ziel", "Zieladresse", "url", pflicht=True, auto="url", hilfe="Beginnt mit https://", breit=True)
            + f'</fieldset></li>'
            f'<li><fieldset class="gruppe"><legend>Zusammenfassung und Zahlung</legend>'
            f'<dl class="angaben"><div><dt>Platz</dt><dd data-zf="platz">Billboard, Startseite</dd></div>'
            f'<div><dt>Zeitraum</dt><dd data-zf="zeit">{datum_lang(ERSTER_FREIER, False)} bis {datum_lang(ende)}</dd></div>'
            f'<div><dt>Betrag</dt><dd><span class="fill">Preis folgt</span></dd></div></dl>'
            f'<div class="feld feld--check feld--breit"><input id="agb" name="bedingungen" type="checkbox" required><label for="agb">Ich nehme die '
            f'<span class="fill">Verkaufsbedingungen (folgen von KBS)</span> an.</label></div>'
            f'<div class="absenden"><button class="btn" type="submit">Weiter zur Zahlung bei Stripe</button>'
            f'<p class="hilfe hilfe--form" aria-live="polite" data-meldung>Kartendaten sieht tamil.de nie; bezahlt wird bei Stripe.</p></div></fieldset></li></ol></form>')
    body = (f'<section class="seitenkopf" aria-labelledby="h-bu"><div class="container kopfblock kopfblock--geteilt">'
            f'<h1 id="h-bu">Werbeplatz buchen</h1><p class="lead">Fünf Schritte; erst die Zahlung bei Stripe reserviert die Tage.</p></div></section>'
            f'<section class="abschnitt abschnitt--direkt" aria-label="Buchung"><div class="container">{form}</div></section>')
    seite("buchen.html", "Werbeplatz buchen | tamil.de", "Einen Werbeplatz auf tamil.de Schritt für Schritt buchen.", body, skript=True)


def kontakt():
    form = (f'<form class="formular" id="nachricht" data-endpoint="" novalidate aria-labelledby="h-na">'
            f'<fieldset class="gruppe"><legend id="h-na">Nachricht an die Redaktion</legend>'
            + feld("k-name", "Name", pflicht=True, auto="name")
            + feld("k-email", "E-Mail", "email", pflicht=True, auto="email")
            + feld("k-telefon", "Telefon", "tel", auto="tel", hilfe="Freiwillig.")
            + feld("k-text", "Nachricht", "textarea", pflicht=True, breit=True, hilfe="Ein Hinweis, ein Thema, ein Eintrag für das Verzeichnis oder eine Frage.")
            + EINWILLIGUNG.format(p="k") + FALLE.format(p="k")
            + '</fieldset><div class="absenden"><button class="btn" type="submit">Nachricht senden</button>'
            + '<p class="hilfe hilfe--form" aria-live="polite" data-meldung></p></div></form>')
    def fehlt(t):
        return f'<span class="fill">{t}</span>'
    body = (f'<section class="seitenkopf" aria-labelledby="h-ko"><div class="container kopfblock kopfblock--geteilt">'
            f'<h1 id="h-ko">Kontakt</h1><p class="lead">Hinweise, Themen und Fragen an die Redaktion. Geantwortet wird von Hand.</p></div></section>'
            f'<section class="abschnitt abschnitt--direkt" aria-label="Kontakt"><div class="container paar paar--5-7">'
            f'<div><dl class="angaben angaben--gross"><div><dt>E-Mail der Redaktion</dt><dd>{fehlt("Adresse folgt von KBS")}</dd></div>'
            f'<div><dt>Telefon und WhatsApp</dt><dd>{fehlt("Nummer folgt von KBS")}</dd></div>'
            f'<div><dt>WhatsApp-Kanal</dt><dd><a href="{WA_KANAL}" rel="noopener">tamil.de auf WhatsApp</a></dd></div></dl>'
            f'<p class="weiter"><a href="einreichen.html">Termin einreichen</a><a href="werben.html">Werben</a></p></div>{form}</div></section>'
            f'<section class="abschnitt abschnitt--well" id="impressum" aria-labelledby="h-im"><div class="container paar paar--5-7">'
            f'<div class="kopfblock kopfblock--seite"><h2 id="h-im">Impressum</h2></div>'
            f'<div><p>Herausgeber, Anschrift und Verantwortliche nach Medienrecht: {fehlt("Angaben folgen von KBS")}</p>'
            f'<p>Die Datenschutzerklärung folgt mit den Rechtstexten; bis dahin sind die Formulare im Echtbetrieb ausgeschaltet.</p></div></div></section>')
    seite("kontakt.html", "Kontakt | tamil.de", "Kontakt zur Redaktion von tamil.de, Impressum.", body, skript=True)


# ---------------------------------------------------------------- Material
def material():
    (HIER / "bilder").mkdir(exist_ok=True)
    for b in RB:
        shutil.copy(INH / "rueckblick" / b["bild"], HIER / b["bild"])
    shutil.copy(INH / "logo.png", HIER / "bilder/logo.png")
    ziel = HIER / "schriften"
    ziel.mkdir(exist_ok=True)
    if SCHRIFT_QUELLE.exists():
        for n in ("epilogue-latin-wght-normal.woff2", "epilogue-latin-ext-wght-normal.woff2"):
            shutil.copy(SCHRIFT_QUELLE / "files" / n, ziel / n)
        shutil.copy(SCHRIFT_QUELLE / "LICENSE", ziel / "Epilogue-OFL.txt")


if __name__ == "__main__":
    material()
    startseite()
    artikel(30, "artikel.html")
    for _sid in BEI:
        if _sid != 30:
            artikel(_sid, f"artikel-{_sid}.html")
    rubrik()
    termine()
    kino()
    verzeichnis()
    einreichen()
    werben()
    buchen()
    kontakt()
    print("ok", len(CHRONIK), "Chronik", len(list(HIER.glob("*.html"))), "Seiten")
