"""Baut die Linie A „Tagesblatt“ (hm-eigen) aus echtem Material.

Aufruf vom Repo-Root: python3 design/richtungen/hm-eigen/bauen.py
Liest design/inhalte/ und docs/redaktion/rueckblick-2026.md, schreibt alle HTML-Seiten in diesen Ordner und kopiert
Bilder und Logo. Nichts wird erfunden: wo Material fehlt (Kontakte, Preise, Impressum), steht ein sichtbarer Platzhalter.
"""
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
HEUTE = dt.date(2026, 11, 13)
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
FESTTAGE = {dt.date(2026, 1, 14): "Thai Pongal", dt.date(2026, 4, 14): "Tamilisches Neujahr", dt.date(2026, 11, 8): "Deepavali"}
e = html.escape

rb = json.loads((INH / "rueckblick/rueckblick.json").read_text(encoding="utf-8"))["beitraege"]
BEI = {b["story_id"]: b for b in rb}
inh = json.loads((INH / "inhalte.json").read_text(encoding="utf-8"))
kino = inh["diese_woche"]["kino"]
SCENE, RAMA = kino[0], kino[1]

# Chronik aus der Stand-Doku: Spalte „Ereignis“ ist das Datum des Ereignisses
doku = (ROOT / "docs/redaktion/rueckblick-2026.md").read_text(encoding="utf-8")
teil = doku.split("## Entwürfe, die auf Freigabe warten")[1].split("## Recherche nötig")[0]
CHRONIK = []
for z in teil.splitlines():
    m = re.match(r"\| (2026-\d\d-\d\d) \| (\d+) \| \d+ \| (.+?) \| \d+ \|", z)
    if m:
        CHRONIK.append((dt.date.fromisoformat(m.group(1)), int(m.group(2)), m.group(3).strip()))

# Nur echte Termine in den Festkalender (Feste, Feiern, Aufführungen, Filmstarts, Festivals).
# Nicht: Studien, Apps, Konsulartage, Meistertitel, Restaurants, Gerichte, Behörden, Pläne.
TERMIN_IDS = {30, 108, 102, 107, 33, 82, 104, 106, 84, 83, 42, 71, 43, 46, 75, 76, 78, 47, 48, 101, 49, 100, 77, 80,
              81, 53, 56, 57, 79, 94, 59, 60, 64, 96, 65, 66, 95, 68, 69}
KINO_IDS = {84, 46, 53, 57, 94, 64, 96, 66, 69, 43}

KOMMEND = [
    (dt.date(2026, 11, 15), "Deepavali-Feier des Düsseldorf Tamil Sangam", "Düsseldorf", "artikel.html"),
    (dt.date(2026, 11, 21), "Diwali in Basel mit dem Basel Tamil Sangam", "Aula Lysbüchel, Basel", None),
    (dt.date(2026, 12, 13), "THADAM 2026: Networking- und Gala-Nacht", "Bern", None),
]

# Verzeichnis: nur Einrichtungen, die in den Rückblick-Beiträgen vorkommen; keine erfundenen Kontaktdaten.
VERZ = [
    dict(slug="sri-ganesha-berlin", name="Sri Ganesha Hindu Temple", art="Tempel", kat="Hindu-Tempel", stadt="Berlin",
         land="DE", region="Berlin", bild=49, quellen=[49, 30], premium=True,
         lage="Am nordöstlichen Rand des Volksparks Hasenheide, Berlin-Neukölln",
         text="Hindu-Tempel am Volkspark Hasenheide in Neukölln, geweiht am 7. Juni 2026 mit der Maha Kumbhabhishekam. "
              "Der bunt bemalte Turm ist rund 17 Meter hoch. Zu Deepavali steht das Lichterfest mit Lakshmi Pooja im "
              "Kalender des Tempels."),
    dict(slug="sivaalayam-muenchen", name="Sivaalayam-Tempel", art="Tempel", kat="Hindu-Tempel", stadt="München",
         land="DE", region="Bayern", quellen=[30],
         text="Tempel in München, der für Deepavali am 8. November 2026 Feierlichkeiten angekündigt hatte."),
    dict(slug="kamadchi-hamm", name="Sri-Kamadchi-Ampal-Tempel", art="Tempel", kat="Hindu-Tempel", stadt="Hamm",
         land="DE", region="Nordrhein-Westfalen", bild=71, quellen=[71], lage="Hamm-Uentrop",
         text="Tempel der Göttin Kamadchi in Hamm-Uentrop mit bunt bemaltem Tempelturm. Beim Großen Tempelfest 2026 "
              "sprach Bundespräsident Frank-Walter Steinmeier als Ehrengast der hinduistischen Gemeinde."),
    dict(slug="sivan-kovil-glattbrugg", name="Arulmigu Sivan Kovil", art="Tempel", kat="Hindu-Tempel",
         stadt="Glattbrugg", land="CH", region="Kanton Zürich", bild=76, quellen=[76],
         text="Tempel in Glattbrugg bei Zürich für Linganatha Parameswarar und Parvathi Ambal. Das jährliche "
              "Mahotsavam dauerte 2026 zwölf Festtage, vom 19. bis 30. Juni, mit dem Wagenfest am 27. Juni."),
    dict(slug="duesseldorf-tamil-sangam", name="Düsseldorf Tamil Sangam", art="Verein", kat="Kultur",
         stadt="Düsseldorf", land="DE", region="Nordrhein-Westfalen", quellen=[30],
         text="Verein in Düsseldorf, der für Sonntag, 15. November 2026, zu seiner Deepavali-Feier einlädt."),
    dict(slug="tks-emsdetten", name="Tamilischer Kultur- und Sportverein (TKS e.V.)", art="Verein", kat="Kultur",
         stadt="Emsdetten", land="DE", region="Nordrhein-Westfalen", quellen=[38],
         text="Verein aus Emsdetten, gegründet 2025, mit mehr als 30 Mitgliedern. Er will zu Deepavali, Thai Pongal und "
              "Chithirai Puthandu einladen und setzt auf Musik, Tanz, gemeinsames Kochen und Sport."),
    dict(slug="munich-tamil-kudumbam", name="Munich Tamil Kudumbam e.V.", art="Verein", kat="Kultur",
         stadt="München", land="DE", region="Bayern", quellen=[48],
         text="Verein in München, der am 20. Juni 2026 zum Namma Tamil Nadu Food Fest mit sechs Regionalküchen einlud."),
    dict(slug="tamilschule-aarau", name="Tamilschule Aarau", art="Verein", kat="Tamilschule", stadt="Aarau",
         land="CH", region="Kanton Aargau", quellen=[60],
         text="Tamilische Schule in Aarau, gegründet vor 30 Jahren von Parameswary Nadarajah. Heute unterrichten "
              "13 Lehrpersonen 78 Kinder, vom Kindergarten bis zur neunten Klasse."),
    dict(slug="ceylon-palace-bremen", name="Ceylon Palace", art="Business", kat="Restaurant und Imbiss",
         stadt="Bremen", land="DE", region="Bremen", quellen=[37],
         text="Restaurant mit Küche aus Sri Lanka, geführt von Suthakar Thiruchelvam und seinem Sohn Anoj. Auf der "
              "Karte stehen Currys, Biryani, Dosa, Idly, Kottu und Parotta."),
    dict(slug="aiya-zuerich", name="Restaurant AiYA", art="Business", kat="Restaurant und Imbiss", stadt="Zürich",
         land="CH", region="Kanton Zürich", quellen=[62], lage="Langstrasse, nahe dem Limmatplatz",
         text="Restaurant an der Langstrasse, eröffnet im März 2026 von Saran und Anitha. Küche aus der Vanni-Region im "
              "Norden Sri Lankas; die Gewürze röstet und mahlt das Team im Haus."),
    dict(slug="skt-boutique-zuerich", name="SKT-Boutique", art="Business", kat="Textil und Schmuck", stadt="Zürich",
         land="CH", region="Kanton Zürich", quellen=[39], lage="Hardturmstrasse (neuer Standort)",
         text="Geschäft für Saris und Schmuck von SK Trading. Es zieht von der Josefstrasse 137 an die Hardturmstrasse."),
    dict(slug="sk-trading-zuerich", name="Supermarkt von SK Trading", art="Business", kat="Lebensmittel",
         stadt="Zürich", land="CH", region="Kanton Zürich", quellen=[39], lage="Quellenstrasse",
         text="Supermarkt an der Quellenstrasse. SK Trading hat die Familie Kathirgamanathan in den Neunzigern gegründet."),
]
LAENDER = {"DE": "Deutschland", "AT": "Österreich", "CH": "Schweiz"}
ARTEN = ["Business", "Dienstleister", "Verein", "Tempel"]

RUBRIKEN = [
    ("Nachrichten", "rubrik-nachrichten.html", [85, 87, 51],
     "Was Politik, Gerichte und Behörden für Tamilinnen und Tamilen in Deutschland, Österreich und der Schweiz entscheiden."),
    ("Community", "rubrik.html", [30, 38, 71, 76, 78, 49, 80, 60],
     "Tempel, Vereine, Schulen und Feste in Deutschland, Österreich und der Schweiz."),
    ("Kultur", "rubrik-kultur.html", [33, 83, 43], "Musik, Tanz, Film und Sprache."),
    ("Küche", "rubrik-kueche.html", [37, 39, 48, 62], "Restaurants, Läden und Feste rund ums Essen."),
    ("Sport", "rubrik-sport.html", [67], "Sportlerinnen und Sportler mit tamilischen Wurzeln."),
]

# Pro Seite gesammelte Bildnachweise (für den Fuß)
NW = []


def merk(b):
    if b not in NW:
        NW.append(b)


def rot(d, termin=True):
    return d in FESTTAGE or (termin and d.weekday() == 6)


def wa(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text + " | tamil.de")


def link_zu(sid):
    if sid == 30:
        return "artikel.html"
    return f"artikel-{sid}.html" if sid in BEI else None


def datum(d, jahr=True):
    return f"{d.day}. {MONATE[d.month-1]}{' ' + str(d.year) if jahr else ''}"


def mon_kurz(d):
    m = MONATE[d.month - 1]
    return m[:3] + ("." if len(m) > 3 else "")


def nachweis(b):
    return re.sub(r"\s*\(https?://[^)]*\)", "", b["nachweis"]).replace("Narasimhan Silverscreen", "Narasimhan, Silverscreen")


def bildgroesse(b):
    from PIL import Image
    return Image.open(INH / "rueckblick" / b["bild"]).size


# ---------- Bausteine ----------

def zeile(d, was, wo=None, href=None, teilen=True, heute=False, termin=True, kompakt=False):
    klasse = " ".join(k for k in ("rot" if rot(d, termin) else "", "heute" if heute else "") if k)
    z = (f'<span class="z"><time datetime="{d.isoformat()}">{d.day}</time>'
         f'<small>{TAGE[d.weekday()][:2]}, {mon_kurz(d)}</small></span>')
    w = f'<a href="{href}">{e(was)}</a>' if href else e(was)
    teile = [z, f'<span class="was">{w}</span>']
    if wo:
        teile.append(f'<span class="wo">{e(wo)}</span>')
    if teilen and not kompakt:
        teile.append(f'<a class="teilen" href="{e(wa(was))}">Per WhatsApp schicken</a>')
    return f'<li{f" class=\"{klasse}\"" if klasse else ""}>{"".join(teile)}</li>'


def tage(zeilen, kompakt=False, cls=""):
    k = " ".join(c for c in ("tage", "kompakt" if kompakt else "", cls) if c)
    return f'<ul class="{k}">{"".join(zeilen)}</ul>'


def blatt(d, extra=""):
    marke = ""
    if d in FESTTAGE:
        marke = f'<span class="marke">{TAGE[d.weekday()]}, {FESTTAGE[d]}</span>'
    elif d.weekday() == 6:
        marke = f'<span class="marke">{TAGE[d.weekday()]}</span>'
    wt = marke or f'<span class="wochentag">{TAGE[d.weekday()]}</span>'
    return (f'<p class="tag"><time class="ziffer" datetime="{d.isoformat()}">{d.day}</time>'
            f'<span class="tag-rest"><span class="monat">{MONATE[d.month-1]} {d.year}</span>{wt}{extra}</span></p>')


def figur(b, cls="bild", lazy=True, link=None, quelle=True):
    merk(b)
    w, h = bildgroesse(b)
    q = b.get("quelle_bild") or ""
    img = (f'<img src="{e(b["bild"])}" alt="{e(b["alt"])}" width="{w}" height="{h}"'
           f'{" loading=\"lazy\"" if lazy else " fetchpriority=\"high\""}>')
    if link:
        img = f'<a class="bild-link" href="{link}" tabindex="-1" aria-hidden="true">{img}</a>'
    cap = e(nachweis(b))
    if quelle and q:
        cap += f' <a class="quelle" href="{e(q)}">Quelle</a>'
    return f'<figure class="{cls}">{img}<figcaption>{cap}</figcaption></figure>'


def daumen(b, link):
    """Kleines Bild in Listen; Nachweis steht gesammelt im Fuß."""
    merk(b)
    w, h = bildgroesse(b)
    return (f'<a class="daumen" href="{link}" tabindex="-1" aria-hidden="true"><img src="{e(b["bild"])}" alt="" '
            f'width="{w}" height="{h}" loading="lazy"></a>')


def bericht(sid, bild=True, teaser=False, hn="h3"):
    b = BEI[sid]
    d = dt.date.fromisoformat(b["datum"])
    href = link_zu(sid)
    t = f'<p class="teaser">{e(b["teaser"])}</p>' if teaser else ""
    return (f'<li{"" if bild else " class=\"ohne-bild\""}>{daumen(b, href) if bild else ""}<div>'
            f'<{hn} class="b-titel"><a href="{href}">{e(b["titel"])}</a></{hn}>{t}'
            f'<p class="meta"><time datetime="{d.isoformat()}">{datum(d)}</time>, {e(b["ort"])}</p></div></li>')


def berichte(ids, bild=True, teaser=False, cls="", hn="h3"):
    return f'<ul class="berichte{" " + cls if cls else ""}">{"".join(bericht(i, bild, teaser, hn) for i in ids)}</ul>'


def kopfzeile(hid, titel, mehr=None, mehr_text=None, hn="h2"):
    m = f'<a class="mehr" href="{mehr}">{e(mehr_text)}</a>' if mehr else ""
    return f'<div class="kopfzeile"><{hn} id="{hid}">{e(titel)}</{hn}>{m}</div>'


def filme():
    def film(f):
        orte = ", ".join(f["orte"])
        if f["weitere_staedte"]:
            orte += f" und {f['weitere_staedte']} weiteren Städten"
        return (f'<li><span class="z"><span class="n">{f["kinos"]}</span><small>{"Kinos" if f["kinos"] != 1 else "Kino"}</small></span>'
                f'<span class="was">{e(f["titel"])}</span><span class="wo">{e(orte)}</span></li>')
    return f'<ul class="tage filme">{film(SCENE)}{film(RAMA)}</ul>'


NAV_R = [(n, h) for n, h, _, _ in RUBRIKEN]
DIENSTE = [("Termine", "termine.html"), ("Kino", "kino.html"), ("Verzeichnis", "verzeichnis.html")]
MITMACHEN = [("Termin einreichen", "einreichen.html"), ("Werben", "werben.html"), ("Kontakt", "kontakt.html")]


def kopf(aktiv=""):
    cur = lambda n: ' aria-current="page"' if aktiv == n else ""
    dien = "".join(f'<a href="{h}"{cur(n)}{" class=\"breit\"" if n == "Verzeichnis" else ""}>{n}</a>' for n, h in DIENSTE)
    rub = "".join(f'<a href="{h}"{cur(n)}>{n}</a>' for n, h in NAV_R)
    menue = "".join(f'<li><a href="{h}"{cur(n)}>{n}</a></li>' for n, h in NAV_R + [DIENSTE[2]] + MITMACHEN)
    return (f'<a class="skip" href="#inhalt">Zum Inhalt</a><header class="kopf"><div class="wrap">'
            f'<a class="logo" href="index.html" aria-label="tamil.de, zur Startseite"><img src="bilder/logo.png" alt="tamil.de" width="300" height="121"></a>'
            f'<nav class="rubriken" aria-label="Rubriken">{rub}</nav><nav class="dienste" aria-label="Dienste">{dien}</nav>'
            f'<details class="menue"><summary>Menü</summary><ul>{menue}</ul></details></div></header>')


def fuss():
    rub = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in NAV_R)
    mit = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in DIENSTE + MITMACHEN)
    nw = "".join(f'<li>{e(nachweis(b))}, <a href="{e(b.get("quelle_bild", ""))}">Wikimedia Commons</a></li>' for b in NW)
    nwblock = f'<div><h2>Bildnachweise</h2><ul class="nachweise">{nw}</ul></div>' if NW else ""
    return (f'<footer class="fuss"><div class="wrap"><div><img src="bilder/logo.png" alt="tamil.de" width="300" height="121" loading="lazy">'
            f'<p>Nachrichten, Termine und Kino der tamilischen Community in Deutschland, Österreich und der Schweiz.</p>'
            f'<p><span class="fill">Impressum und Datenschutz folgen</span></p></div>'
            f'<div><h2>Rubriken</h2><ul>{rub}</ul></div><div><h2>Dienste</h2><ul>{mit}</ul></div>{nwblock}</div></footer>')


def seite(titel, beschreibung, body, aktiv=""):
    return (f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(titel)}</title><meta name="description" content="{e(beschreibung)}">'
            f'<link rel="preload" href="schriften/rethink-sans-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="stylesheet" href="hm-eigen.css"></head><body>{kopf(aktiv)}<main id="inhalt">{body}</main>')


def schreib(name, titel, beschreibung, body, aktiv=""):
    (OUT / name).write_text(seite(titel, beschreibung, body, aktiv) + fuss() + "</body></html>\n", encoding="utf-8")
    NW.clear()


def seitenkopf(titel, satz, extra=""):
    return (f'<header class="seitenkopf"><div class="wrap"><h1>{e(titel)}</h1><p class="satz">{satz}</p>{extra}</div></header>')


# ---------- Formularbausteine ----------

def feld(fid, label, typ="text", pflicht=True, hilfe="", attrs="", wert=""):
    frei = "" if pflicht else ' <span class="frei">(freiwillig)</span>'
    req = ' required aria-required="true"' if pflicht else ""
    v = f' value="{e(wert)}"' if wert else ""
    return (f'<div class="feld"><label for="{fid}">{label}{frei}</label>'
            f'<input id="{fid}" name="{fid}" type="{typ}"{req}{v} aria-describedby="{fid}-h" {attrs}>'
            f'<p class="hilfe" id="{fid}-h">{hilfe}</p></div>')


def textfeld(fid, label, pflicht=True, hilfe="", zeilen=6):
    frei = "" if pflicht else ' <span class="frei">(freiwillig)</span>'
    req = ' required aria-required="true"' if pflicht else ""
    return (f'<div class="feld"><label for="{fid}">{label}{frei}</label>'
            f'<textarea id="{fid}" name="{fid}" rows="{zeilen}"{req} aria-describedby="{fid}-h"></textarea>'
            f'<p class="hilfe" id="{fid}-h">{hilfe}</p></div>')


def auswahl(fid, label, optionen, pflicht=True, hilfe="", zusatz=True):
    frei = "" if pflicht or not zusatz else ' <span class="frei">(freiwillig)</span>'
    req = ' required aria-required="true"' if pflicht else ""
    ops = "".join(o if o.startswith("<") else f'<option>{e(o)}</option>' for o in optionen)
    return (f'<div class="feld"><label for="{fid}">{label}{frei}</label><span class="select">'
            f'<select id="{fid}" name="{fid}"{req} aria-describedby="{fid}-h">{ops}</select></span>'
            f'<p class="hilfe" id="{fid}-h">{hilfe}</p></div>')


def datei(fid, label, pflicht=False, hilfe=""):
    frei = "" if pflicht else ' <span class="frei">(freiwillig)</span>'
    req = ' required aria-required="true"' if pflicht else ""
    return (f'<div class="feld"><span class="label" id="{fid}-l">{label}{frei}</span>'
            f'<span class="datei"><span aria-hidden="true">Bild auswählen</span>'
            f'<input class="datei-input" id="{fid}" name="{fid}" type="file" accept="image/jpeg,image/png"{req} aria-labelledby="{fid}-l" aria-describedby="{fid}-h"></span>'
            f'<p class="hilfe" id="{fid}-h">{hilfe}</p></div>')


def haken(fid, text, pflicht=True, hilfe=""):
    req = ' required aria-required="true"' if pflicht else ""
    h = f'<p class="hilfe" id="{fid}-h">{hilfe}</p>' if hilfe else ""
    db = f' aria-describedby="{fid}-h"' if hilfe else ""
    return f'<div class="haken"><input id="{fid}" name="{fid}" type="checkbox"{req}{db}><label for="{fid}">{text}</label>{h}</div>'


def falle():
    return ('<div class="falle" aria-hidden="true"><label for="webseite">Bitte leer lassen</label>'
            '<input id="webseite" name="webseite" type="text" tabindex="-1" autocomplete="off"></div>')


EINWILLIGUNG = haken(
    "einwilligung",
    'Ich bin einverstanden, dass tamil.de meine Angaben speichert, um die Einsendung zu bearbeiten. '
    'Gelöscht wird 90 Tage nach Abschluss.',
    hilfe='<span class="fill">Wortlaut der Einwilligung und Link zur Datenschutzerklärung folgen von KBS</span>')

PERSON = (feld("name", "Ihr Name", attrs='autocomplete="name"')
          + feld("email", "E-Mail", "email", attrs='autocomplete="email"', hilfe="Für Rückfragen der Redaktion. Wird nicht veröffentlicht.")
          + feld("telefon", "Telefon", "tel", pflicht=False, attrs='autocomplete="tel"'))


# ======================================================================
# Startseite
# ======================================================================
a = BEI[30]
hero = (f'<section class="blatt" aria-label="Heute"><div class="wrap">'
        f'<div class="blatt-tag">{blatt(HEUTE)}</div>'
        f'<article class="aufmacher"><h1><a class="titel-link" href="artikel.html">{e(a["titel"])}</a></h1>'
        f'{figur(a, cls="bild aufmacher-bild", lazy=False, link="artikel.html")}'
        f'<p class="vorspann">{e(a["teaser"])}</p>'
        f'<p class="aktionen"><a class="textlink" href="{e(wa(a["titel"]))}">Per WhatsApp schicken</a></p></article>'
        f'<section class="naechste" aria-labelledby="t-h"><h2 id="t-h">Die nächsten Feste</h2>'
        f'{tage([zeile(d, w, o, h, kompakt=True) for d, w, o, h in KOMMEND], kompakt=True)}'
        f'<p><a class="textlink" href="termine.html">Ganzer Festkalender</a></p></section>'
        f'</div></section>')

kinoteil = (f'<section class="abschnitt" id="kino" aria-labelledby="k-h"><div class="wrap">'
            f'{kopfzeile("k-h", "Kino", "kino.html", "Alle Spielorte nach Stadt")}'
            f'<p class="stand">Stand: 9. November 2026, aus den Programmen der Kinos.</p>{filme()}</div></section>')

gemeinde = (f'<section class="abschnitt" id="community" aria-labelledby="g-h"><div class="wrap">'
            f'{kopfzeile("g-h", "Tempel und Vereine", "rubrik.html", "Alles aus Community")}'
            f'{berichte([71, 76, 49, 80, 38, 60], cls="zweispaltig")}</div></section>')

nachrichten = (f'<section class="abschnitt mulde" id="nachrichten" aria-labelledby="n-h"><div class="wrap">'
               f'{kopfzeile("n-h", "Nachrichten", "rubrik-nachrichten.html", "Alle Nachrichten")}'
               f'{berichte([85, 87, 51], teaser=True, cls="mit-teaser")}</div></section>')

k = BEI[37]
kueche = (f'<section class="abschnitt" id="kueche" aria-labelledby="ku-h"><div class="wrap">'
          f'{kopfzeile("ku-h", "Küche", "rubrik-kueche.html", "Alles aus Küche")}'
          f'<div class="lead">{figur(k, link="artikel-37.html")}<div><h3 class="lead-titel"><a href="artikel-37.html">{e(k["titel"])}</a></h3>'
          f'<p class="teaser">{e(k["teaser"])}</p><p class="meta"><time datetime="{k["datum"]}">{datum(dt.date.fromisoformat(k["datum"]))}</time>, {e(k["ort"])}</p>'
          f'{berichte([62, 39, 48], bild=False)}</div></div></div></section>')

kultur = (f'<section class="abschnitt" id="kultur" aria-labelledby="kk-h"><div class="wrap">'
          f'{kopfzeile("kk-h", "Kultur und Sport")}'
          f'{berichte([33, 83, 43, 67], bild=False, cls="zweispaltig")}'
          f'<p class="weiter-links"><a class="textlink" href="rubrik-kultur.html">Alles aus Kultur</a><a class="textlink" href="rubrik-sport.html">Alles aus Sport</a></p></div></section>')

schreib("index.html", "tamil.de | Nachrichten, Termine und Kino der tamilischen Community",
        "Nachrichten, Termine und Kino der tamilischen Community in Deutschland, Österreich und der Schweiz.",
        hero + kinoteil + gemeinde + nachrichten + kueche + kultur)


# ======================================================================
# Artikel
# ======================================================================
def artikel(sid, name):
    b = BEI[sid]
    d = dt.date.fromisoformat(b["datum"])
    absz = "".join(f"<p>{e(p)}</p>" for p in b["absaetze"])
    kal = ""
    if sid == 30:
        kal = (f'<aside aria-labelledby="ak-h"><h2 id="ak-h">Im Kalender</h2>'
               f'{tage([zeile(dd, w, o, None, kompakt=True) for dd, w, o, _ in KOMMEND[:2]], kompakt=True)}'
               f'<p><a class="textlink" href="termine.html">Zum Festkalender</a></p></aside>')
    weiter_ids = [i for i in (76, 71, 49, 33, 60) if i != sid][:3]
    weiter = (f'<section class="abschnitt" aria-labelledby="w-h"><div class="wrap">{kopfzeile("w-h", "Weiterlesen")}'
              f'{berichte(weiter_ids, cls="dreispaltig")}</div></section>')
    body = (f'<article><header class="artikel-kopf"><div class="wrap">{blatt(d)}'
            f'<div><p class="ort">{e(b["ort"])}</p><h1>{e(b["titel"])}</h1><p class="vorspann">{e(b["teaser"])}</p>'
            f'<p class="aktionen"><a class="textlink" href="{e(wa(b["titel"]))}">Per WhatsApp teilen</a></p></div></div></header>'
            f'<div class="artikel-bild"><div class="wrap">{figur(b, lazy=False)}</div></div>'
            f'<div class="artikel-text"><div class="wrap"><div class="text">{absz}'
            f'<div class="teilen-block"><a class="knopf" href="{e(wa(b["titel"]))}">Per WhatsApp schicken</a>'
            f'<a class="textlink" href="termine.html">Festkalender</a></div></div>{kal}</div></div></article>'
            + weiter)
    schreib(name, f'{b["titel"]} | tamil.de', b["teaser"], body)


artikel(30, "artikel.html")
for sid in BEI:
    if sid != 30:
        artikel(sid, f"artikel-{sid}.html")


# ======================================================================
# Rubriken (Community = rubrik.html, mit Seitennavigation)
# ======================================================================
JE_SEITE = 5
for rname, datei_name, ids, satz in RUBRIKEN:
    ids = sorted(ids, key=lambda i: BEI[i]["datum"], reverse=True)
    seiten = [ids[i:i + JE_SEITE] for i in range(0, len(ids), JE_SEITE)]
    for n, teilids in enumerate(seiten, 1):
        fname = datei_name if n == 1 else datei_name.replace(".html", f"-{n}.html")
        erst = teilids[0]
        b = BEI[erst]
        d = dt.date.fromisoformat(b["datum"])
        lead = (f'<section class="abschnitt rubrik-lead" aria-label="Neuester Beitrag"><div class="wrap lead">'
                f'{figur(b, lazy=False, link=link_zu(erst))}<div><h2 class="lead-titel"><a href="{link_zu(erst)}">{e(b["titel"])}</a></h2>'
                f'<p class="teaser">{e(b["teaser"])}</p><p class="meta"><time datetime="{b["datum"]}">{datum(d)}</time>, {e(b["ort"])}</p>'
                f'<p class="aktionen"><a class="textlink" href="{e(wa(b["titel"]))}">Per WhatsApp schicken</a></p></div></div></section>')
        rest = ""
        if teilids[1:]:
            rest = (f'<section class="abschnitt" aria-label="Weitere Beiträge"><div class="wrap">'
                    f'{berichte(teilids[1:], teaser=True, cls="mit-teaser", hn="h2")}</div></section>')
        nav = ""
        if len(seiten) > 1:
            def seite_link(k):
                f = datei_name if k == 1 else datei_name.replace(".html", f"-{k}.html")
                return f'<a href="{f}"{" aria-current=\"page\"" if k == n else ""}>Seite {k}</a>'
            vor = (f'<a class="textlink" href="{datei_name if n - 1 == 1 else datei_name.replace(".html", f"-{n-1}.html")}">Neuere Beiträge</a>' if n > 1 else "")
            nach = (f'<a class="textlink" href="{datei_name.replace(".html", f"-{n+1}.html")}">Ältere Beiträge</a>' if n < len(seiten) else "")
            nav = (f'<nav class="seiten" aria-label="Seiten"><div class="wrap"><div class="seiten-zeile"><p>Seite {n} von {len(seiten)}</p>'
                   f'<div class="seiten-links">{vor}{"".join(seite_link(k) for k in range(1, len(seiten) + 1))}{nach}</div></div></div></nav>')
        titel = rname if n == 1 else f"{rname}, Seite {n}"
        schreib(fname, f"{titel} | tamil.de", satz, seitenkopf(titel, e(satz)) + lead + rest + nav, rname)


# ======================================================================
# Festkalender: ab heute zuerst, darunter das Jahr 2026
# ======================================================================
ab_heute = [zeile(HEUTE, "Heute", None, None, teilen=False, heute=True, termin=False)]
ab_heute += [zeile(d, w, o, h) for d, w, o, h in KOMMEND]
mon = {}
for d, sid, titel in CHRONIK:
    if sid in TERMIN_IDS and d <= HEUTE:
        mon.setdefault(d.month, []).append((d, sid, titel))
vorbei = ""
for m in sorted(mon, reverse=True):
    eintr = sorted(mon[m], key=lambda x: x[0], reverse=True)
    zeilen = [zeile(d, t, BEI[sid]["ort"] if sid in BEI else None, link_zu(sid), teilen=False) for d, sid, t in eintr]
    vorbei += (f'<details class="monat-block"{" open" if m == max(mon) else ""}><summary><span class="monat-name">{MONATE[m-1]}</span>'
               f'<span class="anzahl">{len(eintr)} {"Termin" if len(eintr) == 1 else "Termine"}</span></summary>{tage(zeilen)}</details>')
termine_body = (seitenkopf("Festkalender", "Feste, Feiern und Bühnen der tamilischen Community, ab heute.",
                           '<p class="aktionen"><a class="textlink" href="einreichen.html">Termin einreichen</a></p>')
                + f'<section class="abschnitt" aria-labelledby="ah-h"><div class="wrap">{kopfzeile("ah-h", "Ab heute")}'
                + tage(ab_heute)
                + '<p class="legende">Rot steht für einen Termin an einem Sonntag oder an einem Festtag (Thai Pongal, Tamilisches Neujahr, Deepavali).</p></div></section>'
                + f'<section class="abschnitt" aria-labelledby="zl-h"><div class="wrap">{kopfzeile("zl-h", "Zurückliegend in 2026")}'
                + f'<p class="satz">Worüber wir berichtet haben, nach Monaten.</p>{vorbei}</div></section>')
schreib("termine.html", "Festkalender | tamil.de", "Feste, Feiern und Bühnen der tamilischen Community, ab heute.", termine_body, "Termine")


# ======================================================================
# Kino
# ======================================================================
staedte = {}
for f in (SCENE, RAMA):
    for o in f["orte"]:
        staedte.setdefault(o, []).append(f["titel"])
stadtzeilen = "".join(
    f'<li><span class="stadt">{e(s)}</span><span class="was">{e(" und ".join(fs))}</span>'
    f'<span class="wo">Kino und Uhrzeiten folgen</span></li>' for s, fs in sorted(staedte.items()))
kinojahr = sorted([(d, sid, t) for d, sid, t in CHRONIK if sid in KINO_IDS], reverse=True)
kino_body = (seitenkopf("Kino", "Welcher tamilische Film in welcher Stadt läuft. Stand: 9. November 2026, aus den Programmen der Kinos.",
                        f'<p class="aktionen"><a class="textlink" href="#staedte">Meine Stadt finden</a>'
                        f'<a class="textlink" href="{e(wa("Tamilisches Kino, Stand 9. November 2026"))}">Per WhatsApp schicken</a></p>')
             + f'<section class="abschnitt" aria-labelledby="f-h"><div class="wrap">{kopfzeile("f-h", "Im Programm")}{filme()}</div></section>'
             + f'<section class="abschnitt" id="staedte" aria-labelledby="s-h"><div class="wrap">{kopfzeile("s-h", "Nach Stadt")}'
             + f'<p class="satz"><span class="fill">Namen der Kinos und Uhrzeiten folgen, sobald die Kinos sie veröffentlichen</span></p>'
             + f'<ul class="staedte">{stadtzeilen}</ul>'
             + f'<p class="satz">„{e(SCENE["titel"])}“ läuft außerdem in {SCENE["weitere_staedte"]} weiteren Städten, die noch nicht erfasst sind.</p></div></section>'
             + f'<section class="abschnitt" aria-labelledby="kj-h"><div class="wrap">{kopfzeile("kj-h", "Aus dem Kinojahr 2026")}'
             + f'<div class="lead lead-schmal">{figur(BEI[84], link="artikel-84.html")}'
             + tage([zeile(d, t, BEI[sid]["ort"] if sid in BEI else None, link_zu(sid), teilen=False) for d, sid, t in kinojahr], kompakt=True)
             + '</div></div></section>')
schreib("kino.html", "Kino | tamil.de", "Welcher tamilische Film in welcher Stadt läuft.", kino_body, "Kino")


# ======================================================================
# Verzeichnis
# ======================================================================
def eintrag_datei(v):
    return "verzeichnis-eintrag.html" if v["slug"] == "sri-ganesha-berlin" else f"verzeichnis-{v['slug']}.html"


def zaehl(**kw):
    return sum(1 for v in VERZ if all(v[k] == w for k, w in kw.items()))


regionen = {}
for v in VERZ:
    regionen.setdefault(v["land"], set()).add(v["region"])
art_seg = (f'<span class="opt"><input type="radio" name="art" id="art-alle" value="" checked><label for="art-alle">Alle ({len(VERZ)})</label></span>'
           + "".join(f'<span class="opt"><input type="radio" name="art" id="art-{a.lower()}" value="{a.lower()}"><label for="art-{a.lower()}">{a} ({zaehl(art=a)})</label></span>' for a in ARTEN))
land_ops = ['<option value="">Alle Länder</option>'] + [f'<option value="{c}">{n} ({zaehl(land=c)})</option>' for c, n in LAENDER.items()]
reg_ops = ['<option value="">Alle</option>'] + [
    f'<optgroup label="{LAENDER[c]}">' + "".join(f'<option>{e(r)}</option>' for r in sorted(regionen[c])) + '</optgroup>'
    for c in LAENDER if c in regionen]
stadt_ops = ['<option value="">Alle Städte</option>'] + [f'<option>{e(s)}</option>' for s in sorted({v["stadt"] for v in VERZ})]
filter_form = (f'<form class="filter" action="verzeichnis.html" method="get" role="search" aria-label="Verzeichnis durchsuchen">'
               f'<div class="feld suche"><label for="q">Suche nach Name, Ort oder Stichwort</label>'
               f'<div class="zeile-feld"><input id="q" name="q" type="search" aria-describedby="q-h"><button class="knopf" type="submit">Suchen</button></div>'
               f'<p class="hilfe" id="q-h">Zum Beispiel Tempel, Zürich oder Tamilschule.</p></div>'
               f'<fieldset class="seg"><legend>Art</legend>{art_seg}</fieldset>'
               f'<fieldset class="ort"><legend>Ort</legend><div class="ort-felder">'
               f'{auswahl("land", "Land", land_ops, pflicht=False, zusatz=False)}{auswahl("region", "Bundesland oder Kanton", reg_ops, pflicht=False, zusatz=False)}'
               f'{auswahl("stadt", "Stadt", stadt_ops, pflicht=False, zusatz=False)}</div></fieldset>'
               f'<p class="filter-fuss"><button class="knopf knopf-leise" type="submit">Filter anwenden</button>'
               f'<a class="textlink" href="verzeichnis.html">Filter zurücksetzen</a></p></form>')
sortiert = sorted(VERZ, key=lambda v: (not v.get("premium"), v["name"].lower()))
eintraege = "".join(
    f'<li{" class=\"premium\"" if v.get("premium") else ""}><div class="e-name"><h2><a href="{eintrag_datei(v)}">{e(v["name"])}</a></h2>'
    f'<p class="meta">{v["art"]}, {e(v["kat"])}</p></div><p class="e-ort">{e(v["stadt"])}<small>{e(v["region"])}, {LAENDER[v["land"]]}</small></p>'
    f'{"<p class=\"e-marke\">Premium</p>" if v.get("premium") else ""}</li>' for v in sortiert)
verz_body = (seitenkopf("Verzeichnis", "Tempel, Vereine, Geschäfte und Dienstleister der tamilischen Community in Deutschland, Österreich und der Schweiz.",
                        '<p class="aktionen"><a class="textlink" href="kontakt.html">Eintrag vorschlagen</a></p>')
             + f'<section class="abschnitt verz" aria-label="Suche und Ergebnisse"><div class="wrap verz-raster">'
             + f'<div class="verz-filter">{filter_form}</div>'
             + f'<div class="verz-liste"><p class="ergebnis" role="status">{len(VERZ)} Einträge, Premium zuerst</p>'
             + f'<ul class="eintraege">{eintraege}</ul>'
             + f'<p class="hinweis">Für Dienstleister und für Österreich gibt es noch keine Einträge. '
             + f'<a href="kontakt.html">Eintrag vorschlagen</a></p>'
             + f'<p class="hinweis"><span class="fill">Darstellungsbeispiel: Die Premium-Markierung am Sri Ganesha Hindu Temple ist nicht vergeben</span></p></div></div></section>')
schreib("verzeichnis.html", "Verzeichnis | tamil.de", "Tempel, Vereine, Geschäfte und Dienstleister der tamilischen Community.", verz_body, "Verzeichnis")

for v in VERZ:
    bild = figur(BEI[v["bild"]], lazy=False) if v.get("bild") else ""
    quellen = berichte(v["quellen"], cls="dreispaltig")
    lage = e(v["lage"]) if v.get("lage") else '<span class="fill">Adresse folgt</span>'
    prem = '<p class="e-marke">Premium <span class="klein">(Darstellungsbeispiel, nicht vergeben)</span></p>' if v.get("premium") else ""
    angaben = (f'<dl class="angaben"><div><dt>Art</dt><dd>{v["art"]}, {e(v["kat"])}</dd></div>'
               f'<div><dt>Ort</dt><dd>{e(v["stadt"])}, {e(v["region"])}, {LAENDER[v["land"]]}</dd></div>'
               f'<div><dt>Adresse</dt><dd>{lage}</dd></div>'
               f'<div><dt>Telefon, E-Mail, Website</dt><dd><span class="fill">Kontaktdaten folgen, wenn der Eintrag sie freigibt</span></dd></div>'
               f'<div><dt>Öffnungszeiten</dt><dd>nicht angegeben</dd></div></dl>')
    body = (f'<article><header class="seitenkopf eintrag-kopf"><div class="wrap"><p class="zurueck"><a class="textlink" href="verzeichnis.html">Zurück zum Verzeichnis</a></p>'
            f'{prem}<h1>{e(v["name"])}</h1><p class="satz">{e(v["text"])}</p></div></header>'
            f'<section class="abschnitt" aria-label="Angaben"><div class="wrap eintrag{" mit-bild" if bild else ""}">{bild}<div>{angaben}'
            f'<p class="aktionen"><a class="textlink" href="kontakt.html">Änderung melden</a>'
            f'<a class="textlink" href="{e(wa(v["name"] + ", " + v["stadt"]))}">Per WhatsApp schicken</a></p></div></div></section>'
            f'<section class="abschnitt" aria-labelledby="q-h"><div class="wrap">{kopfzeile("q-h", "Bei tamil.de erwähnt")}{quellen}</div></section></article>')
    schreib(eintrag_datei(v), f'{v["name"]}, {v["stadt"]} | Verzeichnis | tamil.de', v["text"], body, "Verzeichnis")


# ======================================================================
# Termin einreichen (mit Bestätigung als eigener Zustand)
# ======================================================================
ablauf_einreichen = ('<aside class="ablauf" aria-labelledby="ab-h"><h2 id="ab-h">So geht es weiter</h2><ol>'
                     '<li>Die Redaktion prüft Datum, Ort und Angaben.</li>'
                     '<li>Passt alles, steht der Termin im Festkalender, mit Eintritt, Ende und Veranstalter.</li>'
                     '<li>Bei Fragen meldet sich die Redaktion von Hand. Automatische E-Mails verschicken wir nicht.</li></ol>'
                     '<p>Nur Termine in Deutschland, Österreich und der Schweiz. Jeder Termin wird einzeln eingereicht.</p></aside>')
einreichen_form = (
    '<form class="formular" action="einreichen-danke.html" method="get">'
    '<p class="pflicht-hinweis">Alle Felder ohne den Zusatz „freiwillig“ sind nötig.</p>'
    '<fieldset><legend>Der Termin</legend>'
    + feld("titel", "Titel", hilfe="So, wie er im Kalender stehen soll.")
    + '<div class="feld-paar">'
    + feld("beginn", "Datum und Uhrzeit", "datetime-local")
    + feld("ende", "Ende", "datetime-local", pflicht=False) + '</div>'
    + feld("ort", "Ort mit Adresse", hilfe="Saal oder Tempel, Straße und Hausnummer.")
    + '<div class="feld-paar">' + feld("stadt", "Stadt")
    + auswahl("land", "Land", ['<option value="">Bitte wählen</option>', '<option value="DE">Deutschland</option>',
                               '<option value="AT">Österreich</option>', '<option value="CH">Schweiz</option>']) + '</div>'
    + feld("veranstalter", "Veranstalter", hilfe="Verein, Tempel oder Person.")
    + textfeld("beschreibung", "Beschreibung", hilfe="Was erwartet die Gäste? Höchstens drei Links.")
    + '<div class="feld-paar">' + feld("eintritt", "Eintritt", pflicht=False, hilfe="Zum Beispiel: frei, 10 Euro, Mitglieder günstiger.")
    + feld("ticket", "Ticket-Link", "url", pflicht=False, attrs='inputmode="url"') + '</div>'
    + datei("bild", "Bild", hilfe="JPEG oder PNG, höchstens 5 MB. Wir speichern es neu, ohne versteckte Angaben.")
    + haken("bildrecht", "Ich darf dieses Bild verwenden und tamil.de zur Veröffentlichung überlassen.", pflicht=False,
            hilfe="Nur nötig, wenn Sie ein Bild schicken.")
    + '</fieldset><fieldset><legend>Ihre Angaben</legend>' + PERSON + '</fieldset>'
    + falle() + EINWILLIGUNG
    + '<p class="absenden"><button class="knopf" type="submit">Termin einreichen</button></p></form>')
schreib("einreichen.html", "Termin einreichen | tamil.de", "Ein Fest, eine Feier oder eine Aufführung für den Festkalender melden.",
        seitenkopf("Termin einreichen", "Ein Fest, eine Feier oder eine Aufführung für den Festkalender.")
        + f'<section class="abschnitt formular-raum"><div class="wrap form-raster">{einreichen_form}{ablauf_einreichen}</div></section>', "Termine")


def danke(name, titel, satz, nummer_art, weiter):
    body = (f'<section class="abschnitt danke" aria-labelledby="d-h"><div class="wrap"><div class="danke-box" role="status">'
            f'<h1 id="d-h">{e(titel)}</h1><p class="satz">{satz}</p>'
            f'<dl class="angaben"><div><dt>Vorgangsnummer</dt><dd><span class="nummer">{nummer_art}-2026-000123</span> '
            f'<span class="fill">Beispielnummer</span></dd></div></dl>'
            f'<p>Bitte notieren Sie die Nummer, falls Sie nachfragen. Wir schicken keine automatische E-Mail.</p>'
            f'<p class="aktionen">{weiter}</p></div></div></section>')
    schreib(name, f"{titel} | tamil.de", satz, body)


danke("einreichen-danke.html", "Danke, die Redaktion meldet sich",
      "Ihr Termin ist angekommen. Die Redaktion prüft ihn und trägt ihn in den Festkalender ein, wenn alles passt.", "T",
      '<a class="textlink" href="termine.html">Zum Festkalender</a><a class="textlink" href="einreichen.html">Noch einen Termin einreichen</a>')


# ======================================================================
# Werben, Buchen, Kontakt
# ======================================================================
PLAETZE = [
    ("leaderboard", "Leaderboard", "Unter der Navigation, auf allen Seiten", (728, 90), (320, 50)),
    ("halfpage", "Half Page", "In der Seitenspalte", (300, 600), None),
    ("artikel", "Im Artikel", "Nach dem zweiten Absatz", (728, 90), (300, 250)),
    ("billboard", "Billboard", "Startseite, zwischen den Rubriken", (970, 250), (300, 250)),
    ("fuss", "Fuß", "Über dem Fuß der Seite", (728, 90), (320, 100)),
    ("mobil", "Mobil", "Am Handy fest am unteren Rand", None, (320, 50)),
]


def format_bild(wh, wort):
    if not wh:
        return f'<div class="format leer"><p>{wort}: nicht angeboten</p></div>'
    w, h = wh
    return (f'<figure class="format"><div class="rahmen f-{w}-{h}" aria-hidden="true"></div>'
            f'<figcaption>{wort} {w} × {h} px</figcaption></figure>')


platz_liste = "".join(
    f'<li><div class="platz-text"><h3>{n}</h3><p>{e(wo)}</p></div><div class="formate">{format_bild(d, "Desktop")}{format_bild(m, "Handy")}</div></li>'
    for _, n, wo, d, m in PLAETZE)
preis_zeilen = "".join(f'<tr><th scope="row">{n}</th><td>folgt</td><td>folgt</td><td>folgt</td><td>folgt</td></tr>' for _, n, _, _, _ in PLAETZE)
werben_body = (
    seitenkopf("Werben auf tamil.de", "Sechs Plätze für Ihre Anzeige, online gebucht und bezahlt. Jede Anzeige wird vor dem Start von Hand geprüft.",
               '<p class="aktionen"><a class="knopf" href="buchen.html">Platz buchen</a><a class="textlink" href="kontakt.html">Lieber erst fragen</a></p>')
    + f'<section class="abschnitt" aria-labelledby="p-h"><div class="wrap">{kopfzeile("p-h", "Die Plätze")}'
    + '<p class="satz">Die Rahmen zeigen die Formate im richtigen Verhältnis zueinander. Jede Anzeige trägt auf der Seite den Hinweis „Anzeige“.</p>'
    + f'<ul class="plaetze">{platz_liste}</ul></div></section>'
    + f'<section class="abschnitt mulde" aria-labelledby="pr-h"><div class="wrap">{kopfzeile("pr-h", "Preise und freie Termine")}'
    + '<p class="satz"><span class="fill">Preise je Laufzeit und der nächste freie Termin folgen von KBS</span> Preise werden mit Umsatzsteuer angezeigt.</p>'
    + '<div class="tabelle-rahmen" tabindex="0" role="region" aria-label="Preise je Platz und Laufzeit"><table class="preise"><thead><tr><th scope="col">Platz</th><th scope="col">7 Tage</th><th scope="col">14 Tage</th>'
    + f'<th scope="col">30 Tage</th><th scope="col">Nächster freier Termin</th></tr></thead><tbody>{preis_zeilen}</tbody></table></div></div></section>'
    + f'<section class="abschnitt" aria-labelledby="b-h"><div class="wrap zwei">{kopfzeile("b-h", "So läuft die Buchung")}'
    + '<ol class="schrittliste"><li><b>Platz und Laufzeit wählen.</b> 7, 14 oder 30 Tage.</li>'
    + '<li><b>Startdatum wählen.</b> Belegte Tage sind gesperrt; zwei Werktage Vorlauf.</li>'
    + '<li><b>Ihre Angaben.</b> Firma, Ansprechperson, Rechnungsadresse, E-Mail.</li>'
    + '<li><b>Werbemittel hochladen.</b> Ein Bild für Desktop und eins für das Handy, JPEG oder PNG, dazu die Zieladresse.</li>'
    + '<li><b>Prüfen und bezahlen.</b> Bedingungen annehmen, Zahlung bei Stripe.</li></ol>'
    + '<div class="danach"><h3>Danach</h3><p>Die gewählten Tage sind 35 Minuten für Sie reserviert. Nach der Zahlung prüft KBS die Anzeige. '
    + 'Sie läuft nur, wenn sie bezahlt und freigegeben ist, und nur an den gebuchten Tagen. Wird sie abgelehnt, erstatten wir den vollen Betrag.</p>'
    + '<p>Kartendaten sieht tamil.de nie; sie bleiben bei Stripe. Gezählt werden Einblendungen und Klicks, ohne Cookies.</p>'
    + '<p>Nicht möglich: bewegte Banner, Video und fremde Skripte.</p></div></div></section>')
schreib("werben.html", "Werben | tamil.de", "Werbeplätze auf tamil.de: Formate, Preise und Buchung.", werben_body)

# Buchen: fünf Schritte auf einer Seite
def fmt(d, m):
    return " / ".join(f"{a} × {b}" for a, b in (x for x in (d, m) if x)) + " px"


platz_radios = "".join(
    f'<div class="wahl"><input type="radio" name="platz" id="pl-{k}" value="{k}"{" checked" if k == "billboard" else ""} required>'
    f'<label for="pl-{k}"><span class="wahl-titel">{n}</span><span class="wahl-text">{e(wo)}, {fmt(d, m)}</span></label></div>'
    for k, n, wo, d, m in PLAETZE)
lauf_radios = "".join(
    f'<span class="opt"><input type="radio" name="laufzeit" id="lz-{t}" value="{t}"{" checked" if t == 14 else ""}><label for="lz-{t}">{t} Tage</label></span>'
    for t in (7, 14, 30))
BELEGT = {dt.date(2026, 12, d) for d in list(range(1, 8)) + list(range(19, 27))}
tage_kal = []
erster = dt.date(2026, 12, 1)
for _ in range(erster.weekday()):
    tage_kal.append('<span class="leer" aria-hidden="true"></span>')
for t in range(1, 32):
    d = dt.date(2026, 12, t)
    so = " so" if d.weekday() == 6 else ""
    lab = f"{TAGE[d.weekday()]}, {t}. Dezember"
    if d in BELEGT:
        tage_kal.append(f'<span class="tagfeld belegt{so}"><input type="radio" name="start" id="st-{t}" value="{d.isoformat()}" disabled>'
                        f'<label for="st-{t}" aria-label="{lab}, belegt">{t}</label></span>')
    else:
        tage_kal.append(f'<span class="tagfeld{so}"><input type="radio" name="start" id="st-{t}" value="{d.isoformat()}"{" checked" if t == 8 else ""}>'
                        f'<label for="st-{t}" aria-label="{lab}">{t}</label></span>')
kal_kopf = "".join(f'<abbr title="{w}" class="{"so" if w == "Sonntag" else ""}">{w[:2]}</abbr>' for w in TAGE)
schritte = [("s1", "Platz und Laufzeit"), ("s2", "Startdatum"), ("s3", "Ihre Angaben"), ("s4", "Werbemittel"), ("s5", "Prüfen und bezahlen")]
buchen_form = (
    '<form class="formular buchung" action="buchen-danke.html" method="get">'
    '<p class="pflicht-hinweis">Alle Felder ohne den Zusatz „freiwillig“ sind nötig.</p>'
    f'<fieldset id="s1"><legend><span class="schritt-nr">Schritt 1 von 5</span>Platz und Laufzeit</legend>'
    f'<div class="wahlen">{platz_radios}</div>'
    f'<fieldset class="seg"><legend>Laufzeit</legend>{lauf_radios}</fieldset>'
    f'<p class="hilfe">Preis je Laufzeit: <span class="fill">folgt von KBS</span></p></fieldset>'
    f'<fieldset id="s2"><legend><span class="schritt-nr">Schritt 2 von 5</span>Startdatum</legend>'
    f'<p class="kal-monat">Dezember 2026</p><div class="kal" role="radiogroup" aria-label="Starttag im Dezember 2026">'
    f'<div class="kal-kopf">{kal_kopf}</div><div class="kal-tage">{"".join(tage_kal)}</div></div>'
    f'<p class="hilfe">Durchgestrichen: belegt (Beispieldaten). Bei 14 Tagen ab dem 8. Dezember endet die Anzeige am 21. Dezember.</p></fieldset>'
    f'<fieldset id="s3"><legend><span class="schritt-nr">Schritt 3 von 5</span>Ihre Angaben</legend>'
    + feld("firma", "Firma", attrs='autocomplete="organization"')
    + feld("person", "Ansprechperson", attrs='autocomplete="name"')
    + textfeld("rechnung", "Rechnungsadresse", zeilen=3)
    + '<div class="feld-paar">' + feld("b-email", "E-Mail", "email", attrs='autocomplete="email"')
    + feld("b-telefon", "Telefon", "tel", pflicht=False, attrs='autocomplete="tel"') + '</div>'
    + feld("ust", "USt-ID", pflicht=False) + '</fieldset>'
    f'<fieldset id="s4"><legend><span class="schritt-nr">Schritt 4 von 5</span>Werbemittel</legend>'
    + datei("wm-desktop", "Bild für Desktop", pflicht=True, hilfe="JPEG oder PNG, genau in den Maßen des Platzes; beim Billboard 970 × 250 px.")
    + datei("wm-handy", "Bild für das Handy", pflicht=True, hilfe="Beim Billboard 300 × 250 px.")
    + feld("ziel", "Zieladresse", "url", attrs='inputmode="url" placeholder="https://"', hilfe="Wohin ein Klick auf die Anzeige führt.")
    + '</fieldset>'
    f'<fieldset id="s5"><legend><span class="schritt-nr">Schritt 5 von 5</span>Prüfen und bezahlen</legend>'
    '<dl class="angaben zusammenfassung"><div><dt>Platz</dt><dd>Billboard, Startseite zwischen den Rubriken</dd></div>'
    '<div><dt>Zeitraum</dt><dd>8. bis 21. Dezember 2026, 14 Tage</dd></div>'
    '<div><dt>Preis</dt><dd><span class="fill">folgt von KBS</span></dd></div></dl>'
    + haken("bedingungen", "Ich habe die Verkaufsbedingungen gelesen und nehme sie an.",
            hilfe="Die Verkaufsbedingungen liefert KBS; bis dahin ist hier kein Text verlinkt.")
    + '<p class="hilfe">Die Tage sind ab jetzt 35 Minuten reserviert. Bezahlt wird bei Stripe; danach kommen Sie hierher zurück.</p>'
    '<p class="absenden"><button class="knopf" type="submit">Zur Zahlung bei Stripe</button></p></fieldset></form>')
schritt_nav = '<nav class="schritte" aria-label="Schritte der Buchung"><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in schritte) + '</ol></nav>'
schreib("buchen.html", "Werbeplatz buchen | tamil.de", "Einen Werbeplatz auf tamil.de buchen.",
        seitenkopf("Werbeplatz buchen", "In fünf Schritten zur Anzeige. Die Werte unten sind Beispiele, bis KBS Preise und Termine liefert.")
        + f'<section class="abschnitt formular-raum"><div class="wrap form-raster">{buchen_form}<aside class="ablauf">{schritt_nav}</aside></div></section>')

buchen_danke = (
    '<section class="abschnitt danke" aria-labelledby="bd-h"><div class="wrap"><div class="danke-box" role="status">'
    '<h1 id="bd-h">Bezahlt, jetzt in Prüfung</h1>'
    '<p class="satz">Ihre Buchung ist eingegangen. KBS prüft die Anzeige; danach läuft sie an den gebuchten Tagen.</p>'
    '<p><span class="fill">Beispiel einer Kundenübersicht mit erfundenen Werten</span></p>'
    '<dl class="angaben"><div><dt>Buchungsnummer</dt><dd><span class="nummer">W-2026-000123</span></dd></div>'
    '<div><dt>Platz</dt><dd>Billboard</dd></div><div><dt>Zeitraum</dt><dd>8. bis 21. Dezember 2026</dd></div>'
    '<div><dt>Zahlung</dt><dd>bezahlt, Beleg bei Stripe</dd></div><div><dt>Einblendungen und Klicks</dt><dd>ab dem Start</dd></div></dl>'
    '<ol class="stand"><li class="erledigt">Reserviert</li><li class="erledigt">Bezahlt</li><li class="jetzt" aria-current="step">In Prüfung</li>'
    '<li>Geplant</li><li>Läuft</li><li>Beendet</li></ol>'
    '<p>Diese Seite hat eine geheime Adresse. Speichern Sie sie als Lesezeichen; verloren finden Sie die Buchung mit Buchungsnummer und E-Mail wieder.</p>'
    '<p class="aktionen"><a class="textlink" href="werben.html">Zurück zu Werben</a></p></div></div></section>')
schreib("buchen-danke.html", "Buchung in Prüfung | tamil.de", "Stand Ihrer Werbebuchung.", buchen_danke)

kontakt_form = (
    '<form class="formular" action="kontakt-danke.html" method="get">'
    '<p class="pflicht-hinweis">Alle Felder ohne den Zusatz „freiwillig“ sind nötig.</p>'
    '<fieldset><legend>Ihre Nachricht</legend>' + textfeld("nachricht", "Nachricht", hilfe="Höchstens drei Links.", zeilen=8)
    + PERSON + '</fieldset>' + falle() + EINWILLIGUNG
    + '<p class="absenden"><button class="knopf" type="submit">Nachricht senden</button></p></form>')
kontakt_aside = (
    '<aside class="ablauf" aria-labelledby="r-h"><h2 id="r-h">Redaktion</h2>'
    '<p><span class="fill">Anschrift, E-Mail und Telefon der Redaktion folgen</span></p>'
    '<p>Antworten schreibt die Redaktion von Hand. Automatische E-Mails verschicken wir nicht.</p>'
    '<h2>Andere Wege</h2><ul class="wege"><li><a href="einreichen.html">Termin einreichen</a></li>'
    '<li><a href="werben.html">Werben und Werbeplatz buchen</a></li><li><a href="verzeichnis.html">Verzeichnis</a></li></ul></aside>')
schreib("kontakt.html", "Kontakt | tamil.de", "Nachricht an die Redaktion von tamil.de.",
        seitenkopf("Kontakt", "Hinweise, Fragen und Anliegen an die Redaktion. Auch für Einträge im Verzeichnis.")
        + f'<section class="abschnitt formular-raum"><div class="wrap form-raster">{kontakt_form}{kontakt_aside}</div></section>')
danke("kontakt-danke.html", "Danke für Ihre Nachricht", "Die Redaktion liest jede Nachricht und antwortet von Hand.", "K",
      '<a class="textlink" href="index.html">Zur Startseite</a>')


# ---------- Material ----------
(OUT / "bilder").mkdir(exist_ok=True)
for b in rb:
    shutil.copy(INH / "rueckblick" / b["bild"], OUT / b["bild"])
shutil.copy(INH / "logo.png", OUT / "bilder/logo.png")
print("ok", len(CHRONIK), "Chronik,", len(list(OUT.glob("*.html"))), "Seiten")
