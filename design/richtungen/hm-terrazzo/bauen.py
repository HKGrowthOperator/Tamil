"""Baut die Linie hm-terrazzo (Terrazzo) aus echtem Material.

Aufruf vom Repo-Root: python3 design/richtungen/hm-terrazzo/bauen.py
Liest design/inhalte/ (Rückblick, Kino, Termine, Logo) und docs/redaktion/rueckblick-2026.md,
schreibt die HTML-Seiten in diesen Ordner und kopiert Bilder und Logo nach bilder/.
Schriften liegen fertig in schriften/ (Fontsource-Pakete, OFL).
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
HEUTE = dt.date(2026, 11, 13)
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
KURZ = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
e = html.escape

rb = json.loads((INH / "rueckblick/rueckblick.json").read_text(encoding="utf-8"))["beitraege"]
BEI = {b["story_id"]: b for b in rb}
inh = json.loads((INH / "inhalte.json").read_text(encoding="utf-8"))
KINO = inh["diese_woche"]["kino"]
WA_KANAL = "https://whatsapp.com/channel/0029VaFIN43KWEKo3BGoE13t"  # Standard im Plugin tamil-site (ads.php)

# Jahreschronik aus der Stand-Doku (Tabelle der wartenden Entwürfe)
doku = (ROOT / "docs/redaktion/rueckblick-2026.md").read_text(encoding="utf-8")
teil = doku.split("## Entwürfe, die auf Freigabe warten")[1].split("## Recherche nötig")[0]
CHRONIK = []
for z in teil.splitlines():
    m = re.match(r"\| (2026-\d\d-\d\d) \| (\d+) \| \d+ \| (.+?) \| \d+ \|", z)
    if m:
        CHRONIK.append((dt.date.fromisoformat(m.group(1)), int(m.group(2)), m.group(3).strip()))

# Kommende Termine, nur mit Beleg
KOMMEND = [
    (dt.date(2026, 11, 15), "Deepavali-Feier des Düsseldorf Tamil Sangam", "Düsseldorf", "artikel.html"),
    (dt.date(2026, 11, 21), "Diwali in Basel mit dem Basel Tamil Sangam", "Aula Lysbüchel, Basel", None),
    (dt.date(2026, 12, 13), "THADAM 2026: Networking- und Gala-Nacht", "Bern", None),
]


def datum_lang(d):
    return f"{d.day}. {MONATE[d.month - 1]} {d.year}"


MON_KURZ = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.", "Okt.", "Nov.", "Dez."]


def datum_kurz(d):
    return f"{KURZ[d.weekday()]}, {d.day}. {MON_KURZ[d.month - 1]}"


def wa(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text + " | tamil.de")


def link_zu(sid):
    if sid == 30:
        return "artikel.html"
    return f"artikel-{sid}.html" if sid in BEI else None


def groesse(b):
    return Image.open(INH / "rueckblick" / b["bild"]).size


FOKUS = {30: "50% 8%", 49: "50% 8%", 71: "50% 20%", 85: "50% 55%"}
CH = {"Leuk", "Glattbrugg", "Zürich", "Basel", "Aarau"}


def ort_text(o):
    o = o.replace(", Deutschland", "")
    return f"{o}, Schweiz" if o in CH else o


def figur(b, cls="", lazy=True, fakt=True, href=None):
    w, h = groesse(b)
    q = b.get("quelle_bild") or ""
    quelle = f' <a href="{e(q)}">Quelle</a>' if q else ""
    text = f'{e(b["alt"])}. ' if fakt else ""
    laden = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    fokus = FOKUS.get(b["story_id"])
    stil = f' style="object-position: {fokus}"' if fokus else ""
    img = f'<img src="{e(b["bild"])}" alt="{e(b["alt"])}" width="{w}" height="{h}"{laden}{stil}>'
    if href:
        img = f'<a href="{href}" tabindex="-1" aria-hidden="true">{img}</a>'
    return (f'<figure class="bild {cls}"><div class="bild__rahmen">{img}</div>'
            f'<figcaption>{text}<span class="nachweis">{e(b["nachweis"])}.{quelle}</span></figcaption></figure>')


NAV = [("Nachrichten", "index.html#nachrichten"), ("Community", "rubrik.html"), ("Kultur", "index.html#kultur"), ("Küche", "index.html#kueche")]
DIENSTE = [("Termine", "termine.html"), ("Kino", "kino.html"), ("Verzeichnis", "verzeichnis.html")]


def kopf(aktiv=""):
    def li(n, h, cls=""):
        cur = ' aria-current="page"' if n == aktiv else ""
        return f'<li{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}><a href="{h}"{cur}>{n}</a></li>'
    items = "".join(li(n, h) for n, h in NAV) + "".join(li(n, h, "dienst" if i == 0 else "") for i, (n, h) in enumerate(DIENSTE))
    return ('<a class="skip" href="#inhalt">Zum Inhalt</a>'
            '<header class="kopf"><div class="container kopf__zeile">'
            '<a class="logo" href="index.html"><img src="bilder/logo.png" alt="tamil.de, zur Startseite" width="300" height="121"></a>'
            f'<a class="kopf__aktion" href="einreichen.html"{" aria-current=" + chr(34) + "page" + chr(34) if aktiv == "Einreichen" else ""}>Termin einreichen</a></div>'
            f'<nav class="hauptnav" aria-label="Hauptnavigation"><div class="container"><ul>{items}</ul></div></nav></header>')


def fuss(nachweise):
    nw = "".join(f'<li>{e(b["alt"])}: {e(b["nachweis"])}. <a href="{e(b.get("quelle_bild", ""))}">Quelle</a></li>' for b in nachweise)
    nw_block = (f'<div class="fuss__nachweise"><h2 class="fuss__kopf">Bildnachweise</h2><ul>{nw}</ul></div>' if nachweise else "")
    links = [("Nachrichten", "index.html#nachrichten"), ("Community", "rubrik.html"), ("Kultur", "index.html#kultur"), ("Küche", "index.html#kueche"),
             ("Festkalender", "termine.html"), ("Kino", "kino.html"), ("Verzeichnis", "verzeichnis.html"),
             ("Termin einreichen", "einreichen.html"), ("Werben", "werben.html"), ("Kontakt", "kontakt.html")]
    li = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in links)
    return (f'<footer class="fuss"><div class="container"><div class="fuss__oben">'
            f'<div class="fuss__marke"><img src="bilder/logo.png" alt="tamil.de" width="300" height="121" loading="lazy">'
            f'<p>Nachrichten, Termine und Kino der tamilischen Community in Deutschland, Österreich und der Schweiz.</p></div>'
            f'<nav class="fuss__links" aria-label="Seiten"><ul>{li}</ul></nav></div>{nw_block}'
            f'<p class="fuss__recht">Impressum und Datenschutz: <span class="fill">Texte folgen von KBS Digitalmedia</span></p></div></footer>')


FORM_SKRIPT = """<script>
document.querySelectorAll('form[data-endpoint]').forEach((form) => {
  const help = form.querySelector('[data-hilfe]');
  form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    const falsch = [...form.querySelectorAll('input, textarea, select')].filter((f) => !f.checkValidity());
    form.querySelectorAll('[aria-invalid]').forEach((f) => f.removeAttribute('aria-invalid'));
    falsch.forEach((f) => f.setAttribute('aria-invalid', 'true'));
    if (falsch.length) { help.textContent = 'Bitte die markierten Felder ausfüllen; Pflichtfelder tragen einen Stern.'; falsch[0].focus(); return; }
    if (!form.dataset.endpoint) { help.textContent = 'Nichts gesendet: Dieses Formular ist in der Probe noch nicht angeschlossen.'; return; }
  });
});
</script>"""


def seite(name, titel, beschreibung, body, nachweise=(), aktiv="", skript=False):
    doc = (f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
           f'<title>{e(titel)}</title><meta name="description" content="{e(beschreibung)}">'
           f'<link rel="preload" href="schriften/onest-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
           f'<link rel="preload" href="schriften/wix-madefor-display-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>'
           f'<link rel="stylesheet" href="terrazzo.css"></head><body>{kopf(aktiv)}<main id="inhalt">{body}</main>'
           f'{fuss(list(nachweise))}{FORM_SKRIPT if skript else ""}</body></html>\n')
    (HIER / name).write_text(doc, encoding="utf-8")


def meta(b):
    d = dt.date.fromisoformat(b["datum"])
    return f'<p class="meta"><time datetime="{d.isoformat()}">{datum_lang(d)}</time> in {e(ort_text(b["ort"]))}</p>'


def reihe(sid, teaser=False, titel_tag="h3"):
    b = BEI[sid]
    t = f'<p class="reihe__text">{e(b["teaser"])}</p>' if teaser else ""
    return (f'<li class="reihe"><{titel_tag} class="titel"><a href="{link_zu(sid)}">{e(b["titel"])}</a></{titel_tag}>{t}{meta(b)}</li>')


def termin_zeile(d, was, wo, href=None, teilen=True, heute=False, kompakt=False):
    w = f'<a href="{href}">{e(was)}</a>' if href else e(was)
    if kompakt:
        tl = f'<a class="textlink" href="{e(wa(datum_lang(d) + ": " + was))}">Per WhatsApp schicken</a>' if teilen else ""
        return (f'<tr><td class="zahl"><time datetime="{d.isoformat()}">{datum_kurz(d)}</time></td>'
                f'<td class="spec__titel">{w}<span class="spec__zusatz">{e(wo)}</span>{tl}</td></tr>')
    tl = f'<a class="textlink" href="{e(wa(datum_lang(d) + ": " + was))}">Per WhatsApp schicken</a>' if teilen else ""
    return (f'<tr{" class=" + chr(34) + "ist-heute" + chr(34) if heute else ""}><td class="zahl"><time datetime="{d.isoformat()}">{datum_kurz(d)}</time></td>'
            f'<td class="spec__titel">{w}</td><td class="spec__ort">{e(wo)}</td><td class="spec__aktion">{tl}</td></tr>')


def termin_tabelle(zeilen, caption, kopf_aktion="Weitersagen", kompakt=False):
    if kompakt:
        return (f'<table class="spec spec--kompakt"><caption class="visually-hidden">{e(caption)}</caption>'
                f'<thead><tr><th scope="col">Datum</th><th scope="col">Was und wo</th></tr></thead><tbody>{"".join(zeilen)}</tbody></table>')
    return (f'<table class="spec"><caption class="visually-hidden">{e(caption)}</caption>'
            f'<thead><tr><th scope="col">Datum</th><th scope="col">Was</th><th scope="col">Wo</th><th scope="col"><span class="visually-hidden">{kopf_aktion}</span></th></tr></thead>'
            f'<tbody>{"".join(zeilen)}</tbody></table>')


def anzeige_event():
    return ('<aside class="anzeige" aria-label="Anzeige"><p class="anzeige__hinweis">Anzeige</p>'
            '<a class="anzeige__flaeche anzeige__flaeche--billboard" href="einreichen.html">'
            '<span class="anzeige__claim">Dein Fest im Kalender.</span>'
            '<span class="anzeige__sub">Tempelfest, Konzert, Turnier: kostenlos melden, die Redaktion trägt es ein.</span>'
            '<span class="anzeige__cta">Termin einreichen</span></a></aside>')


def anzeige_whatsapp():
    return ('<aside class="anzeige anzeige--artikel" aria-label="Eigenanzeige"><p class="anzeige__hinweis">Eigenanzeige von tamil.de</p>'
            f'<a class="anzeige__flaeche" href="{WA_KANAL}" rel="noopener">'
            '<span class="anzeige__claim">Tamil.de auf WhatsApp</span>'
            '<span class="anzeige__sub">Neue Beiträge und Termine im Kanal von tamil.de.</span>'
            '<span class="anzeige__cta">Kanal abonnieren</span></a></aside>')


# ---------------------------------------------------------------- Kalenderboden
FESTE = {d: (w, o, h) for d, w, o, h in KOMMEND}
FESTE[dt.date(2026, 11, 8)] = ("Deepavali", "Berlin, Düsseldorf, München", "artikel.html")


def kalenderboden(jahr, monat, gross=False):
    erster = dt.date(jahr, monat, 1)
    tage = (dt.date(jahr + (monat == 12), monat % 12 + 1, 1) - erster).days
    zellen_ = ['<td class="kb__leer"></td>'] * erster.weekday()
    for t in range(1, tage + 1):
        d = dt.date(jahr, monat, t)
        cls = []
        inhalt = f'<span class="kb__tag">{t}</span>'
        if d in FESTE:
            w, o, h = FESTE[d]
            cls.append("fest")
            inhalt = f'<a href="{h or "termine.html"}"><span class="kb__tag">{t}</span><span class="visually-hidden">: {e(w)}</span></a>'
        if d == HEUTE:
            cls.append("heute")
        if d < HEUTE:
            cls.append("vorbei")
        c = f' class="{" ".join(cls)}"' if cls else ""
        zellen_.append(f'<td{c}>{inhalt}</td>')
    while len(zellen_) % 7:
        zellen_.append('<td class="kb__leer"></td>')
    rows = "".join("<tr>" + "".join(zellen_[i:i + 7]) + "</tr>" for i in range(0, len(zellen_), 7))
    kopf_ = "".join(f'<th scope="col"><abbr title="{TAGE[i]}">{KURZ[i]}</abbr></th>' for i in range(7))
    return (f'<table class="kb{" kb--gross" if gross else ""}"><caption>{MONATE[monat - 1]} {jahr}</caption>'
            f'<thead><tr>{kopf_}</tr></thead><tbody>{rows}</tbody></table>')


def feste_des_monats(monat):
    return "".join(f'<li><time class="zahl" datetime="{d.isoformat()}">{datum_kurz(d)}</time>'
                   f'<span>{f"<a href={chr(34)}{h}{chr(34)}>{e(w)}</a>" if h else e(w)}<span class="meta"> in {e(o)}</span></span></li>'
                   for d, (w, o, h) in sorted(FESTE.items()) if d.month == monat and d >= HEUTE)


# ---------------------------------------------------------------- Startseite
# Feldplan: jede Inhaltsart hat ihr eigenes Feld und ihre eigene Form (Aufmacher: großes Bild; Nachrichten: nur
# Text; Feste: Daten; Kino: Film und Städte; Community: Hochformat und Liste; Küche: kleine Bilder in Reihe).
a = BEI[30]
scene, rama = KINO[0], KINO[1]


def nachricht(sid):
    b = BEI[sid]
    d = dt.date.fromisoformat(b["datum"])
    return (f'<li class="reihe"><h3 class="titel"><a href="{link_zu(sid)}">{e(b["titel"])}</a></h3>'
            f'<p class="meta"><time datetime="{d.isoformat()}">{datum_lang(d)}</time></p></li>')


NACHRICHTEN = sorted((85, 87, 51, 39), key=lambda i: BEI[i]["datum"], reverse=True)
erster_satz, rest = re.split(r"(?<=[a-zäöüß])\. ", a["teaser"], maxsplit=1)
hero = (f'<section class="feldplan" aria-label="Aufmacher und Festkalender"><div class="container steine">'
        f'<article class="stein stein--auf aufmacher" aria-labelledby="a-h">{figur(a, "bild--16-9", lazy=False, fakt=False, href="artikel.html")}'
        f'<h1 id="a-h"><a href="artikel.html">{e(a["titel"])}</a></h1>'
        f'<div class="aufmacher__fuss"><p class="meta"><time datetime="2026-11-08">8. November 2026</time><span class="nur-gross"> in Berlin, Düsseldorf und München</span></p>'
        f'<a class="textlink" href="{e(wa(a["titel"]))}">Per WhatsApp schicken</a></div>'
        f'<p class="lead aufmacher__lead">{e(erster_satz)}.<span class="nur-gross"> {e(rest)}</span></p></article>'
        f'<div class="stein stein--kal" aria-labelledby="kal-h"><h2 id="kal-h" class="feld__kopf">Festkalender</h2>{kalenderboden(2026, 11)}'
        f'<ul class="kb__liste">{feste_des_monats(11)}</ul><p class="weiter"><a class="textlink" href="termine.html">Alle Feste 2026</a></p></div>'
        f'</div></section>')
nach_feld = (f'<div class="feld stein--nach" id="nachrichten"><h2 class="feld__kopf feld__kopf--still">Nachrichten</h2>'
             f'<ul class="reihen">{"".join(nachricht(i) for i in NACHRICHTEN)}</ul></div>')

def kino_zeile(k):
    weiter = f" und {k['weitere_staedte']} weitere Städte" if k["weitere_staedte"] else ""
    return (f'<li><p class="kino__film">„{e(k["titel"])}“</p><p class="kino__orte">{e(", ".join(k["orte"]))}{weiter}</p>'
            f'<p class="meta">{k["kinos"]} Kinos</p></li>')


kino_liste = "".join(kino_zeile(k) for k in KINO)
dienst = (f'<section class="abschnitt abschnitt--fuge zweit" aria-label="Nachrichten und Kino"><div class="container feldreihe feldreihe--7-5">{nach_feld}'
          f'<div class="feld"><h2 class="feld__kopf">Tamilisches Kino</h2><p>„{e(scene["titel"])}“ läuft in {scene["kinos"]} Kinos, „{e(rama["titel"])}“ in {rama["kinos"]}.</p>'

          f'<ul class="kino">{kino_liste}</ul>'
          f'<p class="meta">Stand: 9. November 2026, aus den Programmen der Kinos.</p>'
          f'<p class="weiter"><a class="textlink" href="kino.html">Alle Städte</a></p></div></div></section>')

gemeinde = (f'<section class="abschnitt abschnitt--fuge" id="community" aria-labelledby="g-h"><div class="container feldreihe feldreihe--5-7">'
            f'<div class="feld">{figur(BEI[71], "bild--4-5", href=link_zu(71))}</div>'
            f'<div class="feld"><h2 id="g-h" class="feld__kopf">Tempel, Vereine und Schulen</h2>'
            f'<ul class="reihen reihen--dicht">{"".join(reihe(i) for i in sorted((71, 76, 49, 80, 60, 38), key=lambda i: BEI[i]["datum"], reverse=True))}</ul>'
            f'<p class="weiter"><a class="textlink" href="rubrik.html">Alle Beiträge aus der Community</a></p></div></div></section>')

werbung = f'<section class="abschnitt abschnitt--well" aria-label="Anzeige"><div class="container">{anzeige_event()}</div></section>'


def kachel(sid):
    b = BEI[sid]
    return (f'<li class="klein">{figur(b, "bild--1-1 klein__bild", fakt=False, href=link_zu(sid))}'
            f'<div><h3 class="titel"><a href="{link_zu(sid)}">{e(b["titel"])}</a></h3>{meta(b)}</div></li>')


kueche = (f'<section class="abschnitt abschnitt--fuge" aria-label="Küche, Kultur und Sport"><div class="container feldreihe feldreihe--7-5">'
          f'<div class="feld" id="kueche"><h2 class="feld__kopf">Küche</h2><ul class="kleine">{"".join(kachel(i) for i in (62, 48))}</ul><ul class="reihen reihen--nach">{"".join(reihe(i) for i in (37,))}</ul></div>'
          f'<div class="feld feld--text" id="kultur"><h2 class="feld__kopf">Kultur und Sport</h2>'
          f'<ul class="reihen">{"".join(reihe(i) for i in (33, 83, 43, 67))}</ul></div></div></section>')

seite("index.html", "tamil.de | Nachrichten, Termine und Kino der tamilischen Community",
      "Nachrichten, Termine und Kino der tamilischen Community in Deutschland, Österreich und der Schweiz.",
      hero + dienst + gemeinde + kueche, [a, BEI[71], BEI[62], BEI[48]])

# ---------------------------------------------------------------- Artikel
WEITER = {30: (71, 76, 33)}


def artikel(sid, name):
    b = BEI[sid]
    absz = [f"<p>{e(p)}</p>" for p in b["absaetze"]]
    if len(absz) > 2:
        absz.insert(2, anzeige_whatsapp())
    rand = ""
    if sid == 30:
        rand = (f'<aside class="artikel__rand" aria-labelledby="ak-h"><h2 id="ak-h" class="rand__kopf">Im Festkalender</h2>'
                f'<ul class="rand__termine">{"".join(f"<li><time class={chr(34)}zahl{chr(34)} datetime={chr(34)}{d.isoformat()}{chr(34)}>{datum_kurz(d)}</time><span>{e(w)}</span><span class={chr(34)}meta{chr(34)}>{e(o)}</span></li>" for d, w, o, _ in KOMMEND[:2])}</ul>'
                f'<a class="textlink" href="termine.html">Zum Festkalender</a></aside>')
    weiter_ids = [i for i in WEITER.get(sid, (30, 49, 76, 33)) if i != sid][:3]
    weiter = (f'<section class="abschnitt abschnitt--fuge" aria-labelledby="w-h"><div class="container">'
              f'<h2 id="w-h" class="abschnitt__kopf">Weiterlesen</h2><div class="feldreihe feldreihe--drei">'
              + "".join(f'<article class="feld">{figur(BEI[i], "bild--3-2", fakt=False)}<h3 class="titel"><a href="{link_zu(i)}">{e(BEI[i]["titel"])}</a></h3>{meta(BEI[i])}</article>' for i in weiter_ids)
              + '</div></div></section>')
    body = (f'<article class="artikel"><header class="container artikel__kopf"><h1>{e(b["titel"])}</h1>'
            f'<p class="lead">{e(b["teaser"])}</p>{meta(b)}'
            f'<a class="textlink" href="{e(wa(b["titel"]))}">Per WhatsApp teilen</a></header>'
            f'<div class="container">{figur(b, "bild--artikel", lazy=False)}</div>'
            f'<div class="container artikel__raster"><div class="artikel__text">{"".join(absz)}'
            f'<div class="teilen"><p>Für die Familie oder die Vereinsgruppe:</p><a class="btn btn--primaer" href="{e(wa(b["titel"]))}">Per WhatsApp schicken</a></div></div>{rand}</div></article>'
            + weiter)
    seite(name, f'{b["titel"]} | tamil.de', b["teaser"], body, [b] + [BEI[i] for i in weiter_ids])


artikel(30, "artikel.html")
for sid in BEI:
    if sid != 30:
        artikel(sid, f"artikel-{sid}.html")

# ---------------------------------------------------------------- Rubrik Community
COMM = sorted([b for b in rb if b["kategorie"] == "community"], key=lambda b: b["datum"], reverse=True)
SEITEN = [COMM[:4], COMM[4:]]


def rubrik(nr):
    posten = SEITEN[nr - 1]
    zeilen = []
    for i, b in enumerate(posten):
        lead = nr == 1 and i == 0
        zeilen.append(f'<li class="liste__eintrag{" liste__eintrag--lead" if lead else ""}">'
                      f'{figur(b, "bild--3-2" if lead else "bild--4-3", lazy=not lead, fakt=False, href=link_zu(b["story_id"]))}'
                      f'<div class="liste__text"><h2 class="titel{" titel--gross" if lead else ""}"><a href="{link_zu(b["story_id"])}">{e(b["titel"])}</a></h2>'
                      f'<p class="reihe__text">{e(b["teaser"])}</p>{meta(b)}</div></li>')
    seiten = []
    for n in (1, 2):
        href = "rubrik.html" if n == 1 else "rubrik-2.html"
        cur = ' aria-current="page"' if n == nr else ""
        seiten.append(f'<li><a href="{href}"{cur}><span class="visually-hidden">Seite </span>{n}</a></li>')
    vor = ('<li><a class="seiten__schritt" href="rubrik-2.html">Ältere Beiträge</a></li>' if nr == 1
           else '<li><a class="seiten__schritt" href="rubrik.html">Neuere Beiträge</a></li>')
    pag = f'<nav class="seiten" aria-label="Seiten der Rubrik"><ul>{"".join(seiten)}{vor}</ul><p class="meta">Seite {nr} von 2</p></nav>'
    body = (f'<section class="seitenkopf"><div class="container seitenkopf__raster"><h1>Community</h1>'
            f'<div><p class="lead">Tempel, Vereine, Schulen und Begegnungen in Deutschland, Österreich und der Schweiz.</p><p class="meta">{len(COMM)} Beiträge seit Januar 2026</p></div></div></section>'
            f'<section class="abschnitt abschnitt--eng" aria-label="Beiträge"><div class="container"><ol class="liste">{"".join(zeilen)}</ol>{pag}</div></section>')
    seite("rubrik.html" if nr == 1 else "rubrik-2.html", f"Community{' (Seite 2)' if nr == 2 else ''} | tamil.de",
          "Beiträge aus der tamilischen Community: Tempel, Vereine, Schulen.", body, posten, aktiv="Community")


rubrik(1)
rubrik(2)

# ---------------------------------------------------------------- Termine
mon = {}
for d, sid, titel in CHRONIK:
    mon.setdefault(d.month, []).append((d, sid, titel, BEI[sid]["ort"] if sid in BEI else ""))
for d, w, o, h in KOMMEND:
    mon.setdefault(d.month, []).append((d, None, w, o))
bloecke = ""
for m in sorted(mon):
    zeilen = []
    heute_drin = False
    for d, sid, titel, ort in sorted(mon[m], key=lambda x: x[0]):
        if m == HEUTE.month and not heute_drin and d > HEUTE:
            zeilen.append(f'<tr class="ist-heute"><td class="zahl"><time datetime="{HEUTE.isoformat()}">{datum_kurz(HEUTE)}</time></td><td class="spec__titel">Heute</td><td class="spec__ort"></td><td class="spec__aktion"></td></tr>')
            heute_drin = True
        href = link_zu(sid) if sid else ("artikel.html" if d == dt.date(2026, 11, 15) else None)
        zeilen.append(termin_zeile(d, titel, ort, href, teilen=d > HEUTE))
    bloecke += (f'<section class="monat" id="m{m}" aria-labelledby="mh{m}"><h3 id="mh{m}" class="monat__kopf">{MONATE[m - 1]}</h3>'
                f'{termin_tabelle(zeilen, MONATE[m - 1] + " 2026")}</section>')
naechst = KOMMEND[0]
zellen = "".join(f'<li><a href="#m{m}">{MONATE[m - 1]}</a></li>' for m in range(1, 13) if m in mon)
termine_body = (f'<section class="seitenkopf seitenkopf--termin"><div class="container feldreihe feldreihe--5-7">'
                f'<div class="feld"><h1>Festkalender 2026</h1><p class="lead">Feste, Tempel, Vereine und Bühnen der Community, Tag für Tag.</p>'
                f'<div class="aktionen"><a class="btn btn--primaer" href="einreichen.html">Termin einreichen</a></div></div>'
                f'<div class="feld"><div class="kb-paar">{kalenderboden(2026, 11, True)}{kalenderboden(2026, 12, True)}</div>'
                f'<p class="meta">Belegt sind die Tage mit Fest. Heute ist {TAGE[HEUTE.weekday()]}, {datum_lang(HEUTE)}.</p></div></div></section>'
                f'<section class="abschnitt abschnitt--eng" aria-labelledby="n-h"><div class="container">'
                f'<h2 id="n-h" class="feld__kopf">Als Nächstes</h2>'
                f'{termin_tabelle([termin_zeile(d, w, o, h) for d, w, o, h in KOMMEND], "Kommende Termine")}</div></section>'
                f'<section class="abschnitt abschnitt--fuge" aria-labelledby="j-h"><div class="container">'
                f'<div class="kopfblock"><h2 id="j-h">Das Jahr 2026</h2><p class="kopfblock__satz">Was die Redaktion aus diesem Jahr berichtet. Verlinkt ist, was schon als Beitrag vorliegt.</p></div>'
                f'<nav aria-label="Monate"><ul class="monatsleiste">{zellen}</ul></nav>{bloecke}</div></section>')
seite("termine.html", "Festkalender 2026 | tamil.de", "Feste, Tempel, Vereine und Bühnen der tamilischen Community 2026, Tag für Tag.",
      termine_body, aktiv="Termine")

# ---------------------------------------------------------------- Kino
staedte = {}
for k in KINO:
    for o in k["orte"]:
        staedte.setdefault(o, []).append(k["titel"])
kino_zeilen = "".join(f'<tr><th scope="row" class="spec__titel">{e(st)}</th><td>{" und ".join("„" + e(f) + "“" for f in fs)}</td></tr>' for st, fs in sorted(staedte.items()))
kino_zeilen += (f'<tr><th scope="row" class="spec__titel spec__titel--leise">{scene["weitere_staedte"]} weitere Städte</th>'
                f'<td>„{e(scene["titel"])}“; die Namen der Städte liegen der Redaktion nicht vor</td></tr>')
staedte_links = "".join(f'<li>{e(st)}</li>' for st in sorted(staedte))
KINOJAHR = [(d, sid, t) for d, sid, t in CHRONIK if sid in (84, 43, 46, 53, 57, 64, 66, 69, 94, 96)]
kino_body = (f'<section class="seitenkopf seitenkopf--kino"><div class="container feldreihe feldreihe--7-5">'
             f'<div class="feld"><h1>Tamilisches Kino diese Woche</h1>'
             f'<p class="lead">„{e(scene["titel"])}“ läuft in {scene["kinos"]} Kinos, „{e(rama["titel"])}“ in {rama["kinos"]}. Alle Spielorte liegen in Deutschland.</p>'
             f'<p class="meta">Stand: 9. November 2026, aus den Programmen der Kinos.</p>'
             f'<div class="aktionen"><a class="textlink" href="{e(wa("Tamilisches Kino diese Woche"))}">Per WhatsApp schicken</a></div></div>'
             f'<div class="feld"><h2 class="feld__kopf">Städte</h2><ul class="stadtliste">{staedte_links}</ul></div></div></section>'
             f'<section class="abschnitt abschnitt--eng" aria-labelledby="s-h"><div class="container">'
             f'<h2 id="s-h" class="feld__kopf">Was in welcher Stadt läuft</h2>'
             f'<table class="spec spec--kino"><caption class="visually-hidden">Filme nach Stadt</caption><thead><tr><th scope="col">Stadt</th><th scope="col">Film</th></tr></thead>'
             f'<tbody>{kino_zeilen}</tbody></table></div></section>'
             f'<section class="abschnitt abschnitt--fuge" aria-labelledby="kj-h"><div class="container feldreihe feldreihe--5-7">'
             f'<div class="feld">{figur(BEI[84], "bild--4-3", href=link_zu(84))}</div>'
             f'<div class="feld"><h2 id="kj-h" class="feld__kopf">Aus dem Kinojahr 2026</h2>'
             f'<table class="spec spec--schmal"><caption class="visually-hidden">Kinomeldungen 2026</caption><thead><tr><th scope="col">Datum</th><th scope="col">Meldung</th></tr></thead><tbody>'
             + "".join(f'<tr><td class="zahl"><time datetime="{d.isoformat()}">{d.day}. {MON_KURZ[d.month - 1]}</time></td><td class="spec__titel">{f"<a href={chr(34)}{link_zu(sid)}{chr(34)}>{e(t)}</a>" if link_zu(sid) else e(t)}</td></tr>' for d, sid, t in sorted(KINOJAHR, reverse=True))
             + '</tbody></table></div></div></section>')
seite("kino.html", "Tamilisches Kino diese Woche | tamil.de", "Welcher tamilische Film in welcher Stadt läuft.", kino_body, [BEI[84]], aktiv="Kino")

# ---------------------------------------------------------------- Verzeichnis
# Nur Einrichtungen, die in den Rückblick-Beiträgen (oder inhalte.json) vorkommen; keine Kontaktdaten.
VZ = [
    dict(slug="sri-ganesha-hindu-temple-berlin", name="Sri Ganesha Hindu Temple", art="Tempel", kat="Hindu-Tempel", stadt="Berlin", region="Berlin", land="DE", quelle=49,
         text="Hindu-Tempel am nordöstlichen Rand des Volksparks Hasenheide in Neukölln, benannt nach Ganesha. Gebaut seit 2010 und bezahlt aus Spenden; geweiht am 7. Juni 2026 mit der Maha Kumbhabhishekam.", premium=True),
    dict(slug="sri-kamadchi-ampal-tempel-hamm", name="Sri-Kamadchi-Ampal-Tempel", art="Tempel", kat="Hindu-Tempel", stadt="Hamm", region="Nordrhein-Westfalen", land="DE", quelle=71,
         text="Tempel der Göttin Kamadchi in Hamm-Uentrop. Zum Großen Tempelfest 2026 kam Bundespräsident Frank-Walter Steinmeier als Ehrengast."),
    dict(slug="sivaalayam-muenchen", name="Sivaalayam-Tempel", art="Tempel", kat="Hindu-Tempel", stadt="München", region="Bayern", land="DE", quelle=30,
         text="Tempel in München; für Deepavali am 8. November 2026 hatte er Feierlichkeiten angekündigt."),
    dict(slug="arulmigu-sivan-kovil-glattbrugg", name="Arulmigu Sivan Kovil", art="Tempel", kat="Hindu-Tempel", stadt="Glattbrugg", region="Kanton Zürich", land="CH", quelle=76,
         text="Tempel bei Zürich, geweiht Linganatha Parameswarar und Parvathi Ambal. Das Jahresfest Mahotsavam war für den 19. bis 30. Juni 2026 angekündigt."),
    dict(slug="duesseldorf-tamil-sangam", name="Düsseldorf Tamil Sangam", art="Verein", kat="Kultur", stadt="Düsseldorf", region="Nordrhein-Westfalen", land="DE", quelle=30,
         text="Verein in Düsseldorf; lädt am Sonntag, 15. November 2026, zur eigenen Deepavali-Feier ein."),
    dict(slug="basel-tamil-sangam", name="Basel Tamil Sangam", art="Verein", kat="Kultur", stadt="Basel", region="Kanton Basel-Stadt", land="CH", quelle=None,
         text="Verein in Basel; lädt am Samstag, 21. November 2026, Familien zur Diwali-Feier in die Aula Lysbüchel ein."),
    dict(slug="tks-emsdetten", name="Tamilischer Kultur- und Sportverein (TKS e.V.)", art="Verein", kat="Kultur", stadt="Emsdetten", region="Nordrhein-Westfalen", land="DE", quelle=38,
         text="Gegründet 2025, mehr als 30 Mitglieder. Plant Feste zu Deepavali, Thai Pongal und dem tamilischen Neujahr und sucht ein eigenes Vereinsheim."),
    dict(slug="munich-tamil-kudumbam", name="Munich Tamil Kudumbam e.V.", art="Verein", kat="Kultur", stadt="München", region="Bayern", land="DE", quelle=48,
         text="Verein in München; lud am 20. Juni 2026 zum Namma Tamil Nadu Food Fest „Virunthombal 2026“ mit sechs Regionalküchen."),
    dict(slug="tamilschule-aarau", name="Tamilschule Aarau", art="Verein", kat="Tamilschule", stadt="Aarau", region="Kanton Aargau", land="CH", quelle=60,
         text="Seit 30 Jahren in Aarau: 13 Lehrpersonen unterrichten 78 Kinder, vom Kindergarten bis zur neunten Klasse."),
    dict(slug="ceylon-palace-bremen", name="Ceylon Palace", art="Business", kat="Restaurant und Imbiss", stadt="Bremen", region="Bremen", land="DE", quelle=37,
         text="Restaurant mit tamilischer Küche aus Sri Lanka, geführt von Suthakar Thiruchelvam und seinem Sohn Anoj: Kottu, Parotta, Dosa und Devil-Gerichte."),
    dict(slug="aiya-zuerich", name="Restaurant AiYA", art="Business", kat="Restaurant und Imbiss", stadt="Zürich", region="Kanton Zürich", land="CH", quelle=62,
         text="Seit März 2026 an der Langstrasse nahe dem Limmatplatz: Küche aus der Vanni-Region im Norden Sri Lankas."),
    dict(slug="skt-boutique-zuerich", name="SKT-Boutique", art="Business", kat="Textil und Schmuck", stadt="Zürich", region="Kanton Zürich", land="CH", quelle=39,
         text="Saris und Schmuck; zog laut Bericht von der Josefstrasse an die Hardturmstrasse."),
]
LAND = {"DE": "Deutschland", "AT": "Österreich", "CH": "Schweiz"}
ARTEN = ["Business", "Dienstleister", "Verein", "Tempel"]


def vz_href(v):
    return "verzeichnis-eintrag.html" if v.get("premium") else f"verzeichnis-{v['slug']}.html"


def zellen_auswahl(name, werte, gewaehlt, legend, zaehlen=None):
    out = [f'<fieldset class="wahl"><legend>{legend}</legend><div class="zellen">']
    for i, (wert, text) in enumerate(werte):
        anz = f' <span class="zahl">{zaehlen(wert)}</span>' if zaehlen else ""
        out.append(f'<input type="radio" name="{name}" id="{name}-{i}" value="{e(wert)}"{" checked" if wert == gewaehlt else ""}>'
                   f'<label for="{name}-{i}">{e(text)}{anz}</label>')
    out.append("</div></fieldset>")
    return "".join(out)


def auswahl(name, label, optionen):
    opts = "".join(f'<option value="{e(v)}">{e(t)}</option>' for v, t in optionen)
    return f'<div class="eingabe"><label for="{name}">{label}</label><select id="{name}" name="{name}">{opts}</select></div>'


reg = sorted({(v["land"], v["region"]) for v in VZ})
filter_form = (f'<form class="filter" action="verzeichnis.html" method="get" role="search" aria-label="Verzeichnis durchsuchen">'
               f'<div class="filter__suche"><label for="q">Suchen nach Name, Ort oder Stichwort</label><div class="filter__zeile">'
               f'<input id="q" name="q" type="search" autocomplete="off"><button class="btn btn--zweit" type="submit">Suchen</button></div></div>'
               + zellen_auswahl("art", [("", "Alle")] + [(a_, a_) for a_ in ARTEN], "", "Art",
                                lambda w: len(VZ) if not w else sum(1 for v in VZ if v["art"] == w))
               + '<fieldset class="ort"><legend>Ort</legend><div class="ort__felder">'
               + auswahl("land", "Land", [("", "Alle Länder")] + [(k, f"{n} ({sum(1 for v in VZ if v['land'] == k)})") for k, n in LAND.items()])
               + auswahl("region", "Bundesland oder Kanton", [("", "Alle")] + [(r, r) for _, r in reg])
               + auswahl("stadt", "Stadt", [("", "Alle Städte")] + [(s, s) for s in sorted({v["stadt"] for v in VZ})])
               + '</div></fieldset><div class="filter__fuss"><button class="btn btn--primaer" type="submit">Einträge zeigen</button></div></form>')


def vz_zeile(v):
    prem = '<span class="premium">Premium</span>' if v.get("premium") else ""
    return (f'<tr{" class=" + chr(34) + "ist-premium" + chr(34) if v.get("premium") else ""}>'
            f'<td class="spec__titel"><a href="{vz_href(v)}">{e(v["name"])}</a>{prem}</td>'
            f'<td>{v["art"]}<span class="spec__zusatz">{e(v["kat"])}</span></td>'
            f'<td>{e(v["stadt"])}<span class="spec__zusatz">{e(v["region"])}</span></td><td class="zahl">{v["land"]}</td></tr>')


liste = sorted(VZ, key=lambda v: (not v.get("premium"), v["name"]))
vz_body = (f'<section class="seitenkopf seitenkopf--suche" aria-labelledby="vz-h"><div class="container">'
           f'<div class="kopfblock"><h1 id="vz-h">Verzeichnis</h1><p class="kopfblock__satz">Tempel, Vereine, Läden und Dienste der Community, nach Ort. '
           f'<a class="textlink" href="kontakt.html#nachricht">Eintrag vorschlagen</a></p></div>{filter_form}</div></section>'
           f'<section class="abschnitt abschnitt--fuge" aria-labelledby="e-h"><div class="container">'
           f'<div class="kopfblock"><h2 id="e-h">{len(VZ)} Einträge</h2><p class="kopfblock__satz">Premium-Einträge stehen oben und sind so gekennzeichnet. '
           f'<span class="fill">In dieser Probe zeigt der erste Eintrag die Markierung nur zur Darstellung.</span></p></div>'
           f'<table class="spec spec--vz"><caption class="visually-hidden">Einträge im Verzeichnis</caption><thead><tr><th scope="col">Name</th><th scope="col">Art</th><th scope="col">Ort</th><th scope="col">Land</th></tr></thead>'
           f'<tbody>{"".join(vz_zeile(v) for v in liste)}</tbody></table>'
           f'<div class="leer"><h3 class="titel">Dienstleister: noch keine Einträge</h3><p>Übersetzung, Recht, Catering, Fahrschule: Wer Dienste für die Community anbietet, kann sich vorschlagen. Die Redaktion prüft jeden Eintrag vor der Veröffentlichung.</p>'
           f'<a class="textlink" href="kontakt.html#nachricht">Eintrag vorschlagen</a></div></div></section>')
seite("verzeichnis.html", "Verzeichnis | tamil.de", "Tempel, Vereine, Läden und Dienste der tamilischen Community in Deutschland, Österreich und der Schweiz.",
      vz_body, aktiv="Verzeichnis")


def profil(v):
    b = BEI.get(v["quelle"]) if v["quelle"] else None
    bild = figur(b, "bild--4-3", lazy=False, fakt=False) if b else ""
    prem = ('<p class="premium-zeile"><span class="premium">Premium</span> '
            '<span class="fill">Darstellungsbeispiel: Premium setzt nur die Verwaltung.</span></p>') if v.get("premium") else ""
    quelle = (f'<p>Mehr dazu: <a class="textlink" href="{link_zu(v["quelle"])}">{e(BEI[v["quelle"]]["titel"])}</a></p>' if b
              else '<p>Mehr dazu: <a class="textlink" href="termine.html">Festkalender 2026</a></p>')
    gleiche = [w for w in VZ if w["art"] == v["art"] and w is not v][:4]
    weitere = "".join(f'<li><a href="{vz_href(w)}">{e(w["name"])}</a><span class="meta">{e(w["stadt"])}, {LAND[w["land"]]}</span></li>' for w in gleiche)
    akt = (f'<div class="aktionen"><a class="btn btn--zweit" href="kontakt.html#nachricht">Änderung melden</a>'
           f'<a class="textlink" href="{e(wa(v["name"] + ", " + v["stadt"]))}">Per WhatsApp schicken</a></div>')
    body = (f'<section class="profil" aria-labelledby="pr-h"><div class="container"><p class="brotkrumen"><a href="verzeichnis.html">Verzeichnis</a></p></div>'
            f'<div class="container feldreihe feldreihe--7-5 profil__raster">'
            f'<div class="feld"><h1 id="pr-h">{e(v["name"])}</h1>{prem}<p class="lead">{e(v["text"])}</p>{akt}'
            f'<dl class="angaben"><div><dt>Art</dt><dd>{v["art"]}</dd></div><div><dt>Kategorie</dt><dd>{e(v["kat"])}</dd></div>'
            f'<div><dt>Ort</dt><dd>{e(v["stadt"])}, {e(v["region"])}, {LAND[v["land"]]}</dd></div>'
            f'<div><dt>Adresse und Kontakt</dt><dd><span class="fill">Folgen, sobald die Einrichtung sie einreicht</span></dd></div></dl>'
            f'{quelle}</div>'
            f'<div class="feld">{bild}</div></div></section>'
            f'<section class="abschnitt abschnitt--fuge" aria-labelledby="wt-h"><div class="container feldreihe feldreihe--5-7">'
            f'<div class="feld"><h2 id="wt-h">Weitere Einträge: {v["art"]}</h2></div><div class="feld"><ul class="verweise">{weitere}</ul>'
            f'<a class="textlink" href="verzeichnis.html">Ganzes Verzeichnis</a></div></div></section>')
    seite(vz_href(v), f'{v["name"]}, {v["stadt"]} | Verzeichnis | tamil.de', v["text"], body, [b] if b else [], aktiv="Verzeichnis")


for v in VZ:
    profil(v)

# ---------------------------------------------------------------- Formulare


def eingabe(name, label, typ="text", pflicht=False, auto=None, hilfe=None, extra=""):
    st = ' <span class="stern" aria-hidden="true">*</span>' if pflicht else ' <span class="frei">(freiwillig)</span>'
    req = " required" if pflicht else ""
    ac = f' autocomplete="{auto}"' if auto else ""
    h = f'<p class="eingabe__hilfe" id="{name}-hilfe">{hilfe}</p>' if hilfe else ""
    desc = f' aria-describedby="{name}-hilfe"' if hilfe else ""
    if typ == "textarea":
        feld = f'<textarea id="{name}" name="{name}" rows="5"{req}{desc}{extra}></textarea>'
    else:
        feld = f'<input id="{name}" name="{name}" type="{typ}"{req}{ac}{desc}{extra}>'
    return f'<div class="eingabe"><label for="{name}">{label}{st}</label>{feld}{h}</div>'


FALLE = ('<div class="falle" aria-hidden="true"><label for="webseite">Bitte leer lassen</label>'
         '<input id="webseite" name="webseite" type="text" tabindex="-1" autocomplete="off"></div>')

EINWILLIGUNG = ('<div class="haken"><input id="einwilligung" name="einwilligung" type="checkbox" required>'
                '<label for="einwilligung">Ich willige ein, dass tamil.de meine Angaben verarbeitet, um die Einsendung zu prüfen. '
                '<span class="fill">Einwilligungstext und Link zur Datenschutzerklärung folgen von KBS</span> <span class="stern" aria-hidden="true">*</span></label></div>')

ihre = ('<fieldset class="gruppe"><legend>Ihre Angaben</legend><p class="gruppe__satz">Nur für Rückfragen der Redaktion; nie öffentlich.</p>'
        + eingabe("name", "Name", pflicht=True, auto="name") + eingabe("email", "E-Mail", "email", True, "email")
        + eingabe("telefon", "Telefon", "tel", auto="tel") + "</fieldset>")

termin_form = ('<form class="karte formular" action="" method="post" data-endpoint="" enctype="multipart/form-data" novalidate aria-labelledby="ein-h">'
               '<fieldset class="gruppe"><legend>Der Termin</legend>'
               + eingabe("titel", "Titel", pflicht=True, hilfe="So, wie er im Kalender stehen soll, z. B. „Deepavali-Feier des Vereins“.")
               + '<div class="eingabe-paar">' + eingabe("beginn", "Datum und Uhrzeit", "datetime-local", True) + eingabe("ende", "Ende", "datetime-local") + '</div>'
               + eingabe("ort", "Ort mit Adresse", pflicht=True, auto="street-address")
               + '<div class="eingabe-paar">' + eingabe("stadt", "Stadt", pflicht=True, auto="address-level2")
               + zellen_auswahl("land", [("DE", "Deutschland"), ("AT", "Österreich"), ("CH", "Schweiz")], "DE", 'Land <span class="stern" aria-hidden="true">*</span>') + '</div>'
               + eingabe("veranstalter", "Veranstalter", pflicht=True, auto="organization")
               + eingabe("beschreibung", "Beschreibung", "textarea", True, hilfe="Was erwartet die Gäste? Höchstens drei Links.")
               + '<div class="eingabe-paar">' + eingabe("eintritt", "Eintritt") + eingabe("tickets", "Ticket-Link", "url", extra=' inputmode="url"') + '</div>'
               + eingabe("bild", "Bild", "file", hilfe="JPEG oder PNG bis 5 MB. Wird ohne versteckte Angaben neu gespeichert und bleibt bis zur Übernahme intern.", extra=' accept="image/jpeg,image/png"')
               + '<div class="haken"><input id="bildrecht" name="bildrecht" type="checkbox"><label for="bildrecht">Das Bild darf tamil.de verwenden (nur nötig, wenn Sie ein Bild schicken).</label></div>'
               + '</fieldset>' + ihre + FALLE + EINWILLIGUNG
               + '<div class="formular__fuss"><button class="btn btn--primaer" type="submit">Termin einreichen</button>'
               + '<p class="eingabe__hilfe" data-hilfe aria-live="polite"></p></div></form>')

schritte_ein = ('<ol class="schritte"><li><span class="schritte__titel">Sie schicken den Termin</span><span>Pflichtfelder tragen einen Stern.</span></li>'
                '<li><span class="schritte__titel">Die Redaktion prüft</span><span>Datum, Ort und mögliche Doppelungen; bei Fragen meldet sie sich.</span></li>'
                '<li><span class="schritte__titel">Der Termin steht im Kalender</span><span>Mit Ort, Eintritt und Veranstalter.</span></li></ol>')

ein_body = (f'<section class="seitenkopf"><div class="container seitenkopf__raster"><h1 id="ein-h">Termin einreichen</h1>'
            f'<div><p class="lead">Tempelfest, Vereinsfest, Konzert oder Turnier: kostenlos melden, die Redaktion trägt es in den Festkalender ein.</p></div></div></section>'
            f'<section class="abschnitt abschnitt--formular" aria-label="Formular"><div class="container formular-raster">'
            f'<div class="formular-raster__text"><h2 class="rand__kopf">So geht es weiter</h2>{schritte_ein}<p class="meta">Es geht keine automatische E-Mail hinaus. Ihre Angaben werden 90 Tage nach Abschluss gelöscht.</p></div>'
            f'{termin_form}</div></section>')
seite("einreichen.html", "Termin einreichen | tamil.de", "Einen Termin der tamilischen Community für den Festkalender von tamil.de melden.", ein_body,
      aktiv="Einreichen", skript=True)

best_body = (f'<section class="seitenkopf"><div class="container seitenkopf__raster"><h1 id="b-h">Danke, die Redaktion meldet sich.</h1>'
             f'<div><p class="lead">Ihr Termin ist angekommen. Bitte notieren Sie die Vorgangsnummer, falls Sie nachfragen möchten.</p></div></div></section>'
             f'<section class="abschnitt abschnitt--formular" aria-label="Vorgang"><div class="container formular-raster">'
             f'<div class="formular-raster__text"><p class="meta">Diese Seite zeigt die Website nach dem Absenden. Es geht keine E-Mail hinaus.</p></div>'
             f'<div class="karte quittung"><p class="quittung__label">Vorgangsnummer</p>'
             f'<p class="quittung__nummer"><span class="fill">Vergibt die Website beim Absenden</span></p>'
             f'<ol class="schritte"><li><span class="schritte__titel">Angekommen</span><span>Heute, {datum_lang(HEUTE)}.</span></li>'
             f'<li><span class="schritte__titel">Die Redaktion prüft</span><span>Bei Fragen schreibt sie Ihnen von Hand.</span></li>'
             f'<li><span class="schritte__titel">Im Festkalender</span><span>Sobald der Termin freigegeben ist.</span></li></ol>'
             f'<div class="aktionen"><a class="btn btn--primaer" href="termine.html">Zum Festkalender</a><a class="textlink" href="einreichen.html">Weiteren Termin einreichen</a></div></div>'
             f'</div></section>')
seite("einreichen-bestaetigung.html", "Termin eingegangen | tamil.de", "Bestätigung nach dem Einreichen eines Termins (Zustand).", best_body, aktiv="Einreichen")

# ---------------------------------------------------------------- Werben
PLAETZE = [
    ("leaderboard", "Leaderboard", "Unter der Navigation, auf allen Seiten", (728, 90), (320, 50)),
    ("sidebar", "Half Page", "In der Seitenspalte", (300, 600), None),
    ("inarticle", "Im Artikel", "Nach dem zweiten Absatz", (728, 90), (300, 250)),
    ("billboard", "Billboard", "Startseite, zwischen den Rubriken", (970, 250), (300, 250)),
    ("footer", "Fuß", "Über dem Fuß der Seite", (728, 90), (320, 100)),
    ("mobile", "Mobil", "Am Handy fest am unteren Rand", None, (320, 50)),
]


def mass(m):
    return f"{m[0]}&#8239;×&#8239;{m[1]}" if m else "–"


def mass_txt(m):
    return f'<span class="zahl">{mass(m)}</span>' if m else '<span class="spec__zusatz">nicht am Desktop</span>'


formate = "".join(
    f'<figure class="format"><div class="format__flaeche" style="--w:{(d or h)[0]};--h:{(d or h)[1]}"></div>'
    f'<figcaption><span>{n}</span><span class="zahl">{mass(d or h)}</span></figcaption></figure>' for k, n, wo, d, h in PLAETZE)
plaetze_zeilen = "".join(
    f'<tr><th scope="row" class="spec__titel">{n}<span class="spec__zusatz">{wo}</span></th><td data-label="Desktop">{mass_txt(d)}</td>'
    f'<td data-label="Handy">{mass_txt(h) if h else "<span class=spec__zusatz>nur Desktop</span>"}</td>'
    f'<td data-label="Preis"><span class="fill fill--klein">Preis folgt</span></td></tr>' for k, n, wo, d, h in PLAETZE)
werben_body = (f'<section class="seitenkopf seitenkopf--werben"><div class="container feldreihe feldreihe--5-7">'
               f'<div class="feld"><h1>Werben auf tamil.de</h1><p class="lead">Sechs Plätze auf der Website, online gebucht und bezahlt. Jede Anzeige ist als „Anzeige“ gekennzeichnet.</p>'
               f'<div class="aktionen"><a class="btn btn--primaer" href="buchen.html">Werbeplatz buchen</a><a class="textlink" href="kontakt.html#nachricht">Erst eine Frage stellen</a></div></div>'
               f'<div class="feld"><div class="formate diagramm" role="img" aria-label="Diagramm: die sechs Werbeformate maßstabsgetreu zueinander, Desktop-Maß, beim Platz Mobil das Handy-Maß">{formate}</div>'
               f'<p class="meta">Die sechs Formate maßstabsgetreu zueinander; gezeigt ist das Desktop-Maß, bei Mobil das Handy-Maß.</p></div></div></section>'
               f'<section class="abschnitt abschnitt--eng" aria-labelledby="p-h"><div class="container">'
               f'<div class="kopfblock"><h2 id="p-h">Die sechs Plätze</h2><p class="kopfblock__satz">Maße in Pixeln. Laufzeiten und Preise legt KBS fest; bis dahin steht dort ein Platzhalter.</p></div>'
               f'<table class="spec spec--plaetze"><caption class="visually-hidden">Werbeplätze, Maße und Preise</caption><thead><tr><th scope="col">Platz</th><th scope="col">Desktop</th><th scope="col">Handy</th><th scope="col">Preis je Laufzeit</th></tr></thead>'
               f'<tbody>{plaetze_zeilen}</tbody></table></div></section>'
               f'<section class="abschnitt" aria-labelledby="ab-h"><div class="container feldreihe feldreihe--5-7">'
               f'<div class="feld"><h2 id="ab-h">So läuft eine Buchung</h2><p class="lead">In fünf Schritten, ohne Konto.</p></div>'
               f'<div class="feld"><ol class="schritte schritte--gross">'
               f'<li><span class="schritte__titel">Platz und Laufzeit wählen</span><span>Sie sehen den nächsten freien Termin.</span></li>'
               f'<li><span class="schritte__titel">Startdatum wählen</span><span>Belegte Tage sind gesperrt.</span></li>'
               f'<li><span class="schritte__titel">Ihre Angaben</span><span>Firma, Ansprechperson, Rechnungsadresse, E-Mail.</span></li>'
               f'<li><span class="schritte__titel">Werbemittel hochladen</span><span>Ein Bild je Maß, JPEG oder PNG, dazu die Zieladresse.</span></li>'
               f'<li><span class="schritte__titel">Prüfen und bezahlen</span><span>Bei Stripe; die Tage bleiben 35 Minuten reserviert.</span></li></ol>'
               f'<p>Danach prüft KBS das Werbemittel. Die Anzeige startet am gebuchten Tag von selbst und endet von selbst. '
               f'Lehnt KBS ab, wird der volle Betrag erstattet. Den Stand sehen Sie über einen eigenen Link zu Ihrer Buchung.</p>'
               f'<div class="aktionen"><a class="btn btn--zweit" href="buchen.html">Zur Buchung</a></div></div></div></section>')
seite("werben.html", "Werben auf tamil.de", "Werbeplätze, Maße und Ablauf der Buchung auf tamil.de.", werben_body)

# ---------------------------------------------------------------- Buchen
START, LAUFZEIT = dt.date(2026, 11, 23), 14
ENDE = START + dt.timedelta(days=LAUFZEIT - 1)
FRUEHESTENS = dt.date(2026, 11, 17)  # Vorlauf zwei Werktage ab heute (Vorschlag der Festlegung)
BELEGT = {dt.date(2026, 11, d) for d in range(17, 23)}  # Beispiel


def monat_tabelle(jahr, monat):
    erster = dt.date(jahr, monat, 1)
    tage = (dt.date(jahr + (monat == 12), monat % 12 + 1, 1) - erster).days
    zellen_ = ["<td></td>"] * erster.weekday()
    for t in range(1, tage + 1):
        d = dt.date(jahr, monat, t)
        idf = f"tag-{d.isoformat()}"
        if d < FRUEHESTENS or d in BELEGT:
            cls = "tag--belegt" if d in BELEGT else "tag--vorbei"
            grund = "belegt (Beispiel)" if d in BELEGT else "nicht mehr buchbar"
            zellen_.append(f'<td class="{cls}"><input type="radio" name="start" id="{idf}" value="{d.isoformat()}" disabled><label for="{idf}"><span class="visually-hidden">{datum_lang(d)}, {grund}</span><span aria-hidden="true">{t}</span></label></td>')
        else:
            im = START <= d <= ENDE
            cls = "tag--gewaehlt" if d == START else ("tag--zeitraum" if im else "")
            zellen_.append(f'<td{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}><input type="radio" name="start" id="{idf}" value="{d.isoformat()}"{" checked" if d == START else ""}>'
                           f'<label for="{idf}"><span class="visually-hidden">{datum_lang(d)}</span><span aria-hidden="true">{t}</span></label></td>')
    while len(zellen_) % 7:
        zellen_.append("<td></td>")
    rows = "".join("<tr>" + "".join(zellen_[i:i + 7]) + "</tr>" for i in range(0, len(zellen_), 7))
    kopf_ = "".join(f'<th scope="col"><abbr title="{TAGE[i]}">{KURZ[i]}</abbr></th>' for i in range(7))
    return f'<table class="kalender"><caption>{MONATE[monat - 1]} {jahr}</caption><thead><tr>{kopf_}</tr></thead><tbody>{rows}</tbody></table>'


platz_wahl = zellen_auswahl("platz", [(k, n) for k, n, *_ in PLAETZE], "billboard", "Platz")
lauf_wahl = zellen_auswahl("laufzeit", [("7", "7 Tage"), ("14", "14 Tage"), ("30", "30 Tage")], "14", "Laufzeit")
schritte_nav = "".join(f'<li><a href="#s{i}"{" aria-current=" + chr(34) + "step" + chr(34) if i == 1 else ""}><span class="zahl">{i}</span> {t}</a></li>'
                       for i, t in enumerate(["Platz und Laufzeit", "Startdatum", "Ihre Angaben", "Werbemittel", "Prüfen und bezahlen"], 1))
buchen_form = ('<form class="karte formular buchung" action="" method="post" data-endpoint="" enctype="multipart/form-data" novalidate aria-labelledby="bu-h">'
               f'<fieldset class="gruppe" id="s1"><legend><span class="zahl">1</span> Platz und Laufzeit</legend>{platz_wahl}{lauf_wahl}'
               '<p class="gruppe__satz">Billboard: Startseite, zwischen den Rubriken; Desktop <span class="zahl">970&#8239;×&#8239;250</span>, Handy <span class="zahl">300&#8239;×&#8239;250</span>.</p></fieldset>'
               '<fieldset class="gruppe" id="s2"><legend><span class="zahl">2</span> Startdatum</legend>'
               f'<p class="gruppe__satz">Frühester Start: {datum_lang(FRUEHESTENS)}. Gewählt: {datum_lang(START)} bis {datum_lang(ENDE)}.</p>'
               f'<div class="kalender-paar">{monat_tabelle(2026, 11)}{monat_tabelle(2026, 12)}</div>'
               '<p class="legende"><span class="legende__muster legende__muster--gewaehlt" aria-hidden="true"></span>gewählter Zeitraum '
               '<span class="legende__muster legende__muster--belegt" aria-hidden="true"></span>belegt <span class="fill fill--klein">belegte Tage hier nur als Beispiel</span></p></fieldset>'
               '<fieldset class="gruppe" id="s3"><legend><span class="zahl">3</span> Ihre Angaben</legend>'
               + eingabe("firma", "Firma", pflicht=True, auto="organization") + eingabe("person", "Ansprechperson", pflicht=True, auto="name")
               + eingabe("adresse", "Rechnungsadresse", "textarea", True, extra=' autocomplete="street-address"')
               + '<div class="eingabe-paar">' + eingabe("b-email", "E-Mail", "email", True, "email") + eingabe("b-telefon", "Telefon", "tel", auto="tel") + '</div>'
               + eingabe("ustid", "USt-ID") + '</fieldset>'
               '<fieldset class="gruppe" id="s4"><legend><span class="zahl">4</span> Werbemittel</legend>'
               + eingabe("wm-desktop", 'Bild für den Desktop, <span class="zahl">970&#8239;×&#8239;250</span> Pixel', "file", True, hilfe="JPEG oder PNG; Maße und Größe prüft die Website beim Hochladen.", extra=' accept="image/jpeg,image/png"')
               + eingabe("wm-handy", 'Bild für das Handy, <span class="zahl">300&#8239;×&#8239;250</span> Pixel', "file", True, extra=' accept="image/jpeg,image/png"')
               + eingabe("ziel", "Zieladresse", "url", True, hilfe="Wohin die Anzeige führt, mit https://", extra=' inputmode="url"') + '</fieldset>'
               '<fieldset class="gruppe" id="s5"><legend><span class="zahl">5</span> Prüfen und bezahlen</legend>'
               f'<dl class="angaben angaben--summe"><div><dt>Platz</dt><dd>Billboard, Startseite</dd></div>'
               f'<div><dt>Zeitraum</dt><dd><span class="zahl">{START:%d.%m.}–{ENDE:%d.%m.%Y}</span>, {LAUFZEIT} Tage</dd></div>'
               f'<div><dt>Betrag</dt><dd><span class="fill">Preis folgt von KBS</span></dd></div></dl>'
               '<div class="haken"><input id="bedingungen" name="bedingungen" type="checkbox" required><label for="bedingungen">Ich nehme die Verkaufsbedingungen an. '
               '<span class="fill fill--klein">Bedingungen folgen</span> <span class="stern" aria-hidden="true">*</span></label></div>'
               + FALLE +
               '<div class="formular__fuss"><button class="btn btn--primaer" type="submit">Weiter zur Zahlung bei Stripe</button>'
               '<p class="eingabe__hilfe" data-hilfe aria-live="polite">Die Tage bleiben 35 Minuten für Sie reserviert. Kartendaten gibt es nur bei Stripe; tamil.de sieht sie nie.</p></div>'
               '</fieldset></form>')
buchen_body = (f'<section class="seitenkopf"><div class="container seitenkopf__raster"><h1 id="bu-h">Werbeplatz buchen</h1>'
               f'<div><p class="lead">Fünf Schritte, ohne Konto. Bezahlt wird bei Stripe, freigeschaltet nach der Prüfung durch KBS.</p></div></div></section>'
               f'<section class="abschnitt abschnitt--formular" aria-label="Buchung"><div class="container buchung-raster">'
               f'<nav class="schrittfolge" aria-label="Schritte der Buchung"><ol>{schritte_nav}</ol></nav>{buchen_form}</div></section>')
seite("buchen.html", "Werbeplatz buchen | tamil.de", "Einen Werbeplatz auf tamil.de Schritt für Schritt buchen.", buchen_body, skript=True)

# ---------------------------------------------------------------- Kontakt
kontakt_form = ('<form class="karte formular" id="nachricht" action="" method="post" data-endpoint="" novalidate aria-labelledby="na-h">'
                '<h2 id="na-h" class="formular__kopf">Nachricht an die Redaktion</h2>'
                + eingabe("k-name", "Name", pflicht=True, auto="name") + eingabe("k-email", "E-Mail", "email", True, "email")
                + eingabe("k-telefon", "Telefon", "tel", auto="tel")
                + eingabe("k-nachricht", "Nachricht", "textarea", True, hilfe="Höchstens drei Links.")
                + FALLE + EINWILLIGUNG.replace('id="einwilligung"', 'id="k-einwilligung"').replace('for="einwilligung"', 'for="k-einwilligung"').replace("die Einsendung zu prüfen", "meine Nachricht zu beantworten")
                + '<div class="formular__fuss"><button class="btn btn--primaer" type="submit">Nachricht senden</button>'
                + '<p class="eingabe__hilfe" data-hilfe aria-live="polite"></p></div></form>')
kontakt_body = (f'<section class="seitenkopf"><div class="container seitenkopf__raster"><h1 id="ko-h">Kontakt</h1>'
                f'<div><p class="lead">Hinweise, Fragen und Kritik an die Redaktion. Geantwortet wird von Hand.</p></div></div></section>'
                f'<section class="abschnitt abschnitt--formular" aria-label="Kontaktwege und Formular"><div class="container formular-raster">'
                f'<div class="formular-raster__text">'
                f'<dl class="angaben"><div><dt>E-Mail, Telefon und WhatsApp der Redaktion</dt><dd><span class="fill">Folgen von KBS Digitalmedia</span></dd></div>'
                f'<div><dt>Herausgeber</dt><dd>KBS Digitalmedia; Anschrift im Impressum</dd></div></dl>'
                f'<h2 class="rand__kopf">Für bestimmte Anliegen</h2><ul class="verweise">'
                f'<li><a href="einreichen.html">Termin einreichen</a><span class="meta">für den Festkalender</span></li>'
                f'<li><a href="werben.html">Werben</a><span class="meta">Plätze, Maße und Buchung</span></li>'
                f'<li><a href="verzeichnis.html">Verzeichnis</a><span class="meta">Eintrag vorschlagen oder Änderung melden: hier im Formular</span></li></ul></div>'
                f'{kontakt_form}</div></section>')
seite("kontakt.html", "Kontakt | tamil.de", "Kontakt zur Redaktion von tamil.de.", kontakt_body, skript=True)

# ---------------------------------------------------------------- Material
(HIER / "bilder").mkdir(exist_ok=True)
for b in rb:
    shutil.copy(INH / "rueckblick" / b["bild"], HIER / b["bild"])
shutil.copy(INH / "logo.png", HIER / "bilder/logo.png")
print("ok:", len(list(HIER.glob("*.html"))), "Seiten,", len(CHRONIK), "Chronik-Einträge")
