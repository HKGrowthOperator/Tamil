"""Baut die Seiten der Linie hm-almanac („Kalenderblatt“), die aus Daten entstehen, und setzt Kopf und Fuß aller Seiten.

Aufruf (vom Repo-Root): python3 design/richtungen/hm-almanac/bauen.py

Handgeschrieben bleiben index.html, artikel.html (Deepavali, Beitrag 30), termine.html, kino.html; dort ersetzt das
Skript nur Kopfleiste und Fußspalten. Erzeugt werden: artikel-<id>.html (die übrigen 19 Rückblick-Beiträge),
rubrik.html und rubrik-2.html (Community), verzeichnis.html, verzeichnis-eintrag.html, einreichen.html,
einreichen-danke.html, werben.html, buchen.html, kontakt.html.
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
INH = HIER.parents[1] / "inhalte"
HEUTE = dt.date(2026, 11, 13)
e = html.escape

MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
TAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
RUBRIK = {"events": "Events", "kultur": "Kultur", "kueche": "Küche", "community": "Community", "news": "Nachrichten", "sport": "Sport", "kino": "Kino"}
LIZENZ = {
    "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/deed.de",
    "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/deed.de",
}

RB = json.loads((INH / "rueckblick/rueckblick.json").read_text(encoding="utf-8"))["beitraege"]
BEI = {b["story_id"]: b for b in RB}
CHRONO = sorted(RB, key=lambda b: b["datum"])


def datum(b):
    return dt.date.fromisoformat(b["datum"])


def kurz(d):
    return f"{d.day:02d}.{d.month:02d}."


def lang(d):
    return f"{d.day}. {MONATE[d.month - 1]} {d.year}"


def wa(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text + " (tamil.de)")


def link(sid):
    return "artikel.html" if sid == 30 else f"artikel-{sid}.html"


def nachweis(b):
    """„Foto: X / Wikimedia Commons, CC BY-SA 4.0“ → verlinkter Nachweis."""
    text, lic = b["nachweis"].rsplit(", ", 1)
    q = b.get("quelle_bild") or ""
    t = f'<a href="{e(q)}">{e(text)}</a>' if q else e(text)
    lz = f'<a href="{LIZENZ[lic]}">{e(lic)}</a>' if lic in LIZENZ else e(lic)
    return f"{t}, {lz}"


def bild_kopieren(b):
    ziel = HIER / "bilder" / pathlib.Path(b["bild"]).name
    if not ziel.exists():
        shutil.copy2(INH / "rueckblick" / b["bild"], ziel)
    with Image.open(ziel) as im:
        return im.size


def img(b, lazy=True, pos="50% 45%"):
    w, h = bild_kopieren(b)
    ladung = 'loading="lazy"' if lazy else 'fetchpriority="high"'
    return (f'<img src="bilder/{pathlib.Path(b["bild"]).name}" width="{w}" height="{h}" {ladung} '
            f'style="object-position: {pos}" alt="{e(b["alt"])}">')


# ---------------------------------------------------------------- Kopf und Fuß

NAV = [("Termine", "termine.html"), ("Kino", "kino.html"), ("Community", "rubrik.html"), ("Verzeichnis", "verzeichnis.html")]


def leiste(aktiv=""):
    li = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if n == aktiv else ""}>{n}</a></li>' for n, h in NAV)
    return f'''<header class="bar" data-bar>
  <div class="container bar__in">
    <a class="bar__logo" href="index.html" aria-label="tamil.de, zur Startseite"><img src="bilder/logo.png" width="300" height="121" alt=""></a>
    <nav aria-label="Hauptnavigation">
      <ul>{li}</ul>
    </nav>
  </div>
</header>'''


FUSS_NAV = '''<nav class="foot__col" aria-labelledby="f-dienste">
        <p class="foot__h" id="f-dienste">Dienste</p>
        <ul><li><a href="termine.html">Festkalender</a></li><li><a href="kino.html">Kino</a></li><li><a href="verzeichnis.html">Verzeichnis</a></li><li><a href="index.html#jahr">Rückblick 2026</a></li></ul>
      </nav>
      <nav class="foot__col" aria-labelledby="f-mit">
        <p class="foot__h" id="f-mit">Mitmachen</p>
        <ul><li><a href="einreichen.html">Termin einreichen</a></li><li><a href="werben.html">Werben</a></li><li><a href="kontakt.html">Kontakt</a></li></ul>
      </nav>
      <nav class="foot__col" aria-labelledby="f-rubriken">
        <p class="foot__h" id="f-rubriken">Rubriken</p>
        <ul><li><a href="index.html#jahr">Nachrichten</a></li><li><a href="rubrik.html">Community</a></li><li><a href="index.html#jahr">Kultur</a></li><li><a href="termine.html">Events</a></li><li><a href="kino.html">Kino</a></li><li><a href="index.html#jahr">Küche</a></li><li><a href="index.html#jahr">Sport</a></li></ul>
      </nav>'''


def fuss(credits_html, titel="Bildnachweis"):
    cred = (f'<div class="foot__credits" data-credits>\n        <p class="foot__h">{titel}</p>\n        {credits_html}\n      </div>'
            if credits_html else '<div class="foot__credits"><p class="foot__h">Bildnachweis</p><p>Auf dieser Seite steht kein Foto.</p></div>')
    return f'''<footer class="foot">
  <div class="container">
    <div class="grid foot__cols">
      <div class="foot__brand">
        <img src="bilder/logo.png" width="300" height="121" alt="tamil.de">
        <p>Das Magazin der tamilischen Community.</p>
      </div>
      {FUSS_NAV}
      {cred}
    </div>
    <div class="foot__legal">
      <span class="fill" data-fill="impressum">Impressum folgt</span>
      <span class="fill" data-fill="datenschutz">Datenschutz folgt</span>
      <span>© 2026 tamil.de, KBS Digitalmedia</span>
    </div>
  </div>
</footer>'''


SLOTS = '''<script src="site.js"></script>
<script>window.hallmarkSlots = (m) => { for (const [k, v] of Object.entries(m)) { const s = document.querySelector(`[data-slot="${k}"]`); if (!s) continue; const im = new Image(); im.src = typeof v === 'string' ? v : v.src; im.alt = (typeof v === 'object' && v.alt) || s.dataset.alt || ''; s.querySelectorAll(':scope > img').forEach((o) => o.remove()); s.prepend(im); } };
document.querySelectorAll('[data-slot] img').forEach((i) => { if (i.complete && !i.naturalWidth) i.remove(); else i.addEventListener('error', () => i.remove(), { once: true }); });</script>'''


def seite(datei, titel, beschreibung, css, aktiv, main, credits_html="", credits_titel="Bildnachweis"):
    doc = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschreibung)}">
<link rel="stylesheet" href="{css}">
</head>
<body>
<a class="skip" href="#main">Zum Inhalt springen</a>
<div class="banner"><div class="container"><a href="index.html#jahr">Rückblick 2026 in zwanzig Berichten</a></div></div>
{leiste(aktiv)}

<main id="main">
{main}
</main>

{fuss(credits_html, credits_titel)}
{SLOTS}
</body>
</html>
'''
    (HIER / datei).write_text(doc, encoding="utf-8")


def kopf_ersetzen(datei, aktiv):
    p = HIER / datei
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'<header class="bar" data-bar>.*?</header>', lambda m: leiste(aktiv), s, count=1, flags=re.S)
    s = re.sub(r'<nav class="foot__col" aria-labelledby="f-dienste">.*?(?=\n      <div class="foot__credits")',
               lambda m: FUSS_NAV, s, count=1, flags=re.S)
    p.write_text(s, encoding="utf-8")


# ---------------------------------------------------------------- Artikel

def artikel(b):
    sid = b["story_id"]
    d = datum(b)
    w, h = bild_kopieren(b)
    hoch = h > w
    rub = RUBRIK.get(b["kategorie"], b["kategorie"])
    rub_html = f'<a href="rubrik.html">{rub}</a>' if b["kategorie"] == "community" else rub
    i = CHRONO.index(b)
    zeilen = []
    for nb, wort in ((CHRONO[i - 1] if i > 0 else None, "davor"), (b, "hier"), (CHRONO[i + 1] if i + 1 < len(CHRONO) else None, "danach")):
        if nb is None:
            continue
        nd = datum(nb)
        if wort == "hier":
            zeilen.append(f'<tr class="is-hier"><td class="tag">{TAGE[nd.weekday()]} <time class="num" datetime="{nd.isoformat()}">{kurz(nd)}</time></td>'
                          f'<td>Dieser Bericht</td></tr>')
        else:
            zeilen.append(f'<tr><td class="tag">{TAGE[nd.weekday()]} <time class="num" datetime="{nd.isoformat()}">{kurz(nd)}</time></td>'
                          f'<td><a href="{link(nb["story_id"])}">{e(nb["titel"])}</a></td></tr>')
    gleich = [x for x in sorted(RB, key=lambda x: x["datum"], reverse=True) if x["kategorie"] == b["kategorie"] and x is not b]
    if len(gleich) >= 2:
        weiter_titel, weiter = f"Mehr aus {rub}", gleich[:3]
    else:
        weiter_titel = "Mehr aus dem Rückblick"
        weiter = (gleich + [x for x in sorted(RB, key=lambda x: abs((datum(x) - d).days)) if x is not b and x not in gleich])[:3]
    weiter_li = "".join(
        f'<li><time class="num" datetime="{x["datum"]}">{kurz(datum(x))}</time><a href="{link(x["story_id"])}">{e(x["titel"])}</a></li>' for x in weiter)
    prosa = "\n        ".join(f"<p>{e(a)}</p>" for a in b["absaetze"])
    bildklasse = "photo" if hoch else "photo photo--219"
    main = f'''  <article>
    <header class="container grid kopf">
      <div class="kopf__text">
        <h1>{e(b["titel"])}</h1>
        <p class="lead">{e(b["teaser"])}</p>
      </div>
      <dl class="kopf__meta">
        <dt>Datum</dt><dd><time datetime="{d.isoformat()}">{lang(d)}</time></dd>
        <dt>Ort</dt><dd>{e(b["ort"])}</dd>
        <dt>Rubrik</dt><dd>{rub_html}</dd>
        <dd class="share"><a href="{e(wa(b["titel"]))}">Per WhatsApp teilen</a></dd>
      </dl>
      <figure class="pic bild{" bild--hoch" if hoch else ""}">
        <div class="{bildklasse}" data-slot="artikel" data-alt="Ein eigenes Bild zum Bericht">
          {img(b, lazy=False, pos="50% 35%")}
        </div>
        <figcaption>{e(b["alt"])}.
          <small>{nachweis(b)}</small>
        </figcaption>
      </figure>
    </header>

    <section class="container grid text" aria-label="Beitrag">
      <div class="prosa">
        {prosa}
      </div>
      <aside class="rand" aria-label="Im Rückblick davor und danach">
        <figure class="sheet">
          <figcaption class="sheet__head"><span class="sheet__title">Im Rückblick 2026</span></figcaption>
          <table class="tafel">
            <thead><tr><th scope="col">Tag</th><th scope="col">Bericht</th></tr></thead>
            <tbody>
              {"".join(zeilen)}
            </tbody>
          </table>
          <p class="sheet__note"><a href="index.html#jahr">Alle zwanzig Berichte</a></p>
        </figure>
        <a class="btn btn--primary" href="{e(wa(b["titel"]))}">Per WhatsApp teilen</a>
      </aside>
    </section>
  </article>

  <section class="container grid weiter" aria-labelledby="w-weiter">
    <h2 id="w-weiter">{weiter_titel}</h2>
    <ol class="weiter__liste">
      {weiter_li}
    </ol>
  </section>'''
    seite(f"artikel-{sid}.html", f"{b['titel']} | tamil.de", b["teaser"], "artikel.css",
          "Community" if b["kategorie"] == "community" else "", main,
          f'<p>{e(b["alt"].split(" (")[0])}: {nachweis(b)}.</p>')


# ---------------------------------------------------------------- Rubrik Community

def rubrik():
    posts = sorted([b for b in RB if b["kategorie"] == "community"], key=lambda b: b["datum"], reverse=True)
    je = 4
    seiten = [posts[i:i + je] for i in range(0, len(posts), je)]
    n = len(seiten)

    def zeile(b):
        d = datum(b)
        return f'''<li class="eintrag">
          <time class="num" datetime="{d.isoformat()}">{kurz(d)}</time>
          <div class="eintrag__text">
            <h2><a href="{link(b["story_id"])}">{e(b["titel"])}</a></h2>
            <p>{e(b["teaser"])}</p>
            <p class="byline">{e(b["ort"])}</p>
          </div>
          <figure class="pic eintrag__bild"><div class="photo">{img(b)}</div></figure>
        </li>'''

    for k, teil in enumerate(seiten, start=1):
        datei = "rubrik.html" if k == 1 else f"rubrik-{k}.html"
        nr = lambda j: "rubrik.html" if j == 1 else f"rubrik-{j}.html"
        nummern = "".join(
            f'<li><a href="{nr(j)}"{" aria-current=\"page\"" if j == k else ""}><span class="visually-hidden">Seite </span>{j}</a></li>' for j in range(1, n + 1))
        weiter = []
        if k > 1:
            weiter.append(f'<a class="btn" href="{nr(k - 1)}">Neuere Beiträge</a>')
        if k < n:
            weiter.append(f'<a class="btn" href="{nr(k + 1)}">Ältere Beiträge</a>')
        lead = ""
        rest = teil
        if k == 1:
            a = teil[0]
            d = datum(a)
            rest = teil[1:]
            lead = f'''<article class="grid aufmacher-r">
        <figure class="pic">
          <div class="photo">{img(a, lazy=False, pos="50% 50%")}</div>
          <figcaption>{e(a["alt"])}.</figcaption>
        </figure>
        <div class="split__text">
          <h2><a href="{link(a["story_id"])}">{e(a["titel"])}</a></h2>
          <p class="lead">{e(a["teaser"])}</p>
          <p class="byline"><time datetime="{d.isoformat()}">{lang(d)}</time>, {e(a["ort"])}</p>
          <p class="actions"><a class="btn" href="{link(a["story_id"])}">Beitrag lesen</a><a class="share" href="{e(wa(a["titel"]))}">Per WhatsApp teilen</a></p>
        </div>
      </article>'''
        zeilen = "\n        ".join(zeile(b) for b in rest)
        main = f'''  <section class="hero" aria-labelledby="titel">
    <div class="container grid kopfzeile">
      <div class="kopfzeile__text">
        <h1 id="titel">Community</h1>
        <p class="lead">Vereine, Tempel und Schulen in Deutschland und der Schweiz: {len(posts)} Berichte aus dem Jahr 2026.</p>
      </div>
      <p class="kopfzeile__stand">Seite <span class="num">{k}</span> von <span class="num">{n}</span></p>
    </div>
  </section>

  <section class="container liste" aria-label="Berichte, die neuesten zuerst">
      {lead}
      <ol class="eintraege">
        {zeilen}
      </ol>
      <nav class="seiten" aria-label="Seiten der Rubrik">
        <ol>{nummern}</ol>
        <p class="actions">{"".join(weiter)}</p>
      </nav>
  </section>'''
        credits = " ".join(f'{e(b["alt"].split(" (")[0])}: {nachweis(b)}.' for b in teil)
        seite(datei, f"Community{'' if k == 1 else f', Seite {k}'} | tamil.de",
              "Berichte über Vereine, Tempel und Schulen der tamilischen Community in Deutschland und der Schweiz.",
              "rubrik.css", "Community", main, f"<p>{credits}</p>", "Bildnachweise")


# ---------------------------------------------------------------- Verzeichnis

# Nur Einrichtungen, die in Rückblick-Beiträgen vorkommen; Name, Art, Ort aus dem Bericht. Keine Kontaktdaten.
VZ = [
    ("Arulmigu Sivan Kovil", "tempel", "Hindu-Tempel", "Glattbrugg", "Zürich", "CH", 76),
    ("Basel Tamil Sangam", "verein", "Kultur", "Basel", "Basel-Stadt", "CH", None),
    ("Ceylon Palace", "business", "Restaurant und Imbiss", "Bremen", "Bremen", "DE", 37),
    ("Düsseldorf Tamil Sangam", "verein", "Kultur", "Düsseldorf", "Nordrhein-Westfalen", "DE", 30),
    ("Munich Tamil Kudumbam e.V.", "verein", "Kultur", "München", "Bayern", "DE", 48),
    ("Restaurant AiYA", "business", "Restaurant und Imbiss", "Zürich", "Zürich", "CH", 62),
    ("Sivaalayam-Tempel", "tempel", "Hindu-Tempel", "München", "Bayern", "DE", 30),
    ("Sri Ganesha Hindu Temple", "tempel", "Hindu-Tempel", "Berlin", "Berlin", "DE", 49),
    ("Sri-Kamadchi-Ampal-Tempel", "tempel", "Hindu-Tempel", "Hamm", "Nordrhein-Westfalen", "DE", 71),
    ("Tamilische Katholische Mission Aargau", "tempel", "Kirche", "", "Aargau", "CH", 80),
    ("Tamilischer Kultur- und Sportverein (TKS e.V.)", "verein", "Kultur", "Emsdetten", "Nordrhein-Westfalen", "DE", 38),
    ("Tamilschule Aarau", "verein", "Tamilschule", "Aarau", "Aargau", "CH", 60),
]
ART = {"business": "Business", "dienstleister": "Dienstleister", "verein": "Verein", "tempel": "Tempel"}
LAND = {"DE": "Deutschland", "AT": "Österreich", "CH": "Schweiz"}


def verzeichnis():
    zaehl = {a: sum(1 for x in VZ if x[1] == a) for a in ART}
    arten = '<input type="radio" name="art" id="art-alle" value="" checked><label for="art-alle">Alle <span class="num">' + str(len(VZ)) + '</span></label>'
    arten += "".join(
        f'<input type="radio" name="art" id="art-{a}" value="{a}"><label for="art-{a}">{n} <span class="num">{zaehl[a]}</span></label>' for a, n in ART.items())
    laender = "".join(f'<option value="{k}">{v}</option>' for k, v in LAND.items())
    regionen = sorted({x[4] for x in VZ})
    staedte = sorted({x[3] for x in VZ if x[3]})
    reg_opt = "".join(f'<option>{r}</option>' for r in regionen)
    st_opt = "".join(f'<option>{s}</option>' for s in staedte)
    zeilen = []
    for name, art, kat, stadt, region, land, sid in VZ:
        nm = f'<a href="verzeichnis-eintrag.html">{e(name)}</a>' if name == "Ceylon Palace" else e(name)
        ort = f"{e(stadt)}, {LAND[land]}" if stadt else f"Kanton {e(region)}, {LAND[land]}"
        if sid:
            bd = datum(BEI[sid])
            ber = f'<a href="{link(sid)}"><time class="num" datetime="{bd.isoformat()}">{kurz(bd)}</time><span class="visually-hidden"> {e(BEI[sid]["titel"])}</span></a>'
        else:
            ber = '<a href="termine.html#basel">Festkalender</a>'
        zeilen.append(
            f'<tr data-art="{art}" data-land="{land}" data-region="{e(region)}" data-stadt="{e(stadt)}">'
            f'<td class="was">{nm}</td><td>{ART[art]}<span class="hinweis">{e(kat)}</span></td><td>{ort}</td><td class="zu">{ber}</td></tr>')
    main = f'''  <section class="hero" aria-labelledby="titel">
    <div class="container grid kopfzeile">
      <div class="kopfzeile__text">
        <h1 id="titel">Tempel, Vereine und Geschäfte der Community</h1>
        <p class="lead">Jede Einrichtung hier kommt in einem Bericht auf tamil.de vor; Kontaktdaten tragen die Einrichtungen selbst ein.</p>
      </div>
      <p class="actions kopfzeile__aktion"><a class="btn btn--primary" href="kontakt.html?anliegen=verzeichnis">Eintrag vorschlagen</a></p>
    </div>
  </section>

  <section class="container grid vz" aria-label="Suche und Liste">
    <form class="filter" action="verzeichnis.html" method="get" role="search" aria-label="Verzeichnis durchsuchen" data-filter>
      <div class="feld">
        <label for="q">Name oder Stichwort</label>
        <input id="q" name="q" type="search" autocomplete="off">
      </div>
      <fieldset class="seg seg--art">
        <legend>Art</legend>
        {arten}
      </fieldset>
      <fieldset class="ort">
        <legend>Ort</legend>
        <div class="feld"><label for="land">Land</label><select id="land" name="land"><option value="">Alle Länder</option>{laender}</select></div>
        <div class="feld"><label for="region">Bundesland oder Kanton</label><select id="region" name="region"><option value="">Alle</option>{reg_opt}</select></div>
        <div class="feld"><label for="stadt">Stadt</label><select id="stadt" name="stadt"><option value="">Alle Städte</option>{st_opt}</select></div>
      </fieldset>
      <p class="actions"><button class="btn" type="submit">Filtern</button></p>
    </form>

    <figure class="sheet vz__liste" aria-labelledby="vz-titel">
      <figcaption class="sheet__head">
        <span class="sheet__title" id="vz-titel"><span class="num" data-anzahl>{len(VZ)}</span> Einträge, nach Name</span>
        <span class="sheet__stand"><time datetime="{HEUTE.isoformat()}">Stand: 13. November 2026</time></span>
      </figcaption>
      <table class="tafel">
        <thead><tr><th scope="col">Name</th><th scope="col">Art</th><th scope="col">Ort</th><th scope="col" class="zu">Im Bericht</th></tr></thead>
        <tbody>
          {"".join(zeilen)}
        </tbody>
      </table>
      <p class="sheet__leer" data-leer hidden>Für diese Auswahl gibt es noch keinen Eintrag. <a href="kontakt.html?anliegen=verzeichnis">Eintrag vorschlagen</a></p>
      <p class="sheet__note">Dienstleister: noch kein Eintrag. Premium-Einträge stünden oben und trügen das Wort Premium; bisher hat kein Eintrag Premium.</p>
    </figure>
  </section>'''
    seite("verzeichnis.html", "Verzeichnis: Tempel, Vereine und Geschäfte | tamil.de",
          "Tempel, Vereine und Geschäfte der tamilischen Community in Deutschland, Österreich und der Schweiz.",
          "verzeichnis.css", "Verzeichnis", main)


def verzeichnis_eintrag():
    b = BEI[37]
    d = datum(b)
    fehlt = lambda t: f'<span class="fill">{t}</span>'
    main = f'''  <section class="container profil-kopf" aria-labelledby="titel">
    <p class="zurueck"><a href="verzeichnis.html">Zum Verzeichnis</a></p>
    <div class="grid">
      <div class="profil-kopf__text">
        <p class="premium" id="premium">Premium</p>
        <h1 id="titel">Ceylon Palace</h1>
        <p class="lead">Restaurant mit Küche aus Sri Lanka in Bremen, geführt von Suthakar Thiruchelvam und seinem Sohn Anoj.</p>
        <p class="actions"><a class="btn btn--primary" href="kontakt.html?anliegen=verzeichnis&amp;eintrag=ceylon-palace">Änderung melden</a><a class="share" href="{e(wa("Ceylon Palace, Restaurant mit Küche aus Sri Lanka in Bremen, im Verzeichnis"))}">Per WhatsApp teilen</a></p>
      </div>
      <p class="profil-kopf__hinweis">Muster: So erscheint die Markierung Premium. Setzen darf sie allein die Verwaltung; für das Ceylon Palace ist nichts entschieden.</p>
    </div>
  </section>

  <section class="container grid profil" aria-label="Angaben">
    <figure class="sheet angaben" aria-labelledby="a-titel">
      <figcaption class="sheet__head"><span class="sheet__title" id="a-titel">Angaben</span><span class="sheet__stand">Kontakt fehlt noch</span></figcaption>
      <table class="tafel tafel--dl">
        <tbody>
          <tr><th scope="row">Art</th><td>Business</td></tr>
          <tr><th scope="row">Kategorie</th><td>Restaurant und Imbiss</td></tr>
          <tr><th scope="row">Adresse</th><td>{fehlt("folgt vom Inhaber")}</td></tr>
          <tr><th scope="row">Ort</th><td>{fehlt("PLZ folgt")} Bremen</td></tr>
          <tr><th scope="row">Bundesland</th><td>Bremen</td></tr>
          <tr><th scope="row">Land</th><td>Deutschland</td></tr>
          <tr><th scope="row">Telefon</th><td>{fehlt("folgt vom Inhaber")}</td></tr>
          <tr><th scope="row">E-Mail</th><td>{fehlt("folgt vom Inhaber")}</td></tr>
          <tr><th scope="row">Website</th><td>{fehlt("folgt vom Inhaber")}</td></tr>
          <tr><th scope="row">Öffnungszeiten</th><td>{fehlt("folgt vom Inhaber")}</td></tr>
        </tbody>
      </table>
      <p class="sheet__note">Öffentlich wird nur, was der Inhaber als öffentlich freigibt; die Redaktion prüft jede Angabe.</p>
    </figure>
    <div class="profil__text">
      <h2>Über das Restaurant</h2>
      <p>Hinter dem Ceylon Palace stehen Suthakar Thiruchelvam und sein Sohn Anoj. Die Familie blickt auf rund 30 Jahre in der Bremer Gastronomie zurück; in der Küche hat der Sohn das Sagen. Auf der Karte stehen Currys, Biryani, Dosa und Idly, gebratener Reis, Devil-Gerichte und vor allem Parotta.</p>
      <figure class="pic">
        <div class="photo" data-slot="profil" data-alt="Ein Foto aus dem Ceylon Palace">{img(b, pos="50% 50%")}</div>
        <figcaption>Symbolbild: Chicken Kottu, ein Gericht aus Sri Lanka, nicht aus dem Ceylon Palace.</figcaption>
      </figure>
      <h2 class="profil__h">In Berichten auf tamil.de</h2>
      <ol class="weiter__liste">
        <li><time class="num" datetime="{d.isoformat()}">{kurz(d)}</time><a href="artikel-37.html">{e(b["titel"])}</a></li>
      </ol>
    </div>
  </section>'''
    seite("verzeichnis-eintrag.html", "Ceylon Palace, Bremen: Verzeichnis | tamil.de",
          "Ceylon Palace in Bremen: Restaurant mit Küche aus Sri Lanka, im Verzeichnis von tamil.de.",
          "verzeichnis.css", "Verzeichnis", main, f"<p>Chicken Kottu: {nachweis(b)}.</p>")


# ---------------------------------------------------------------- Formulare

EINWILLIGUNG = '''<div class="feld feld--check">
          <input id="{p}-ok" name="einwilligung" type="checkbox" required aria-describedby="{p}-ok-hilfe">
          <label for="{p}-ok">Ich bin einverstanden, dass tamil.de meine Angaben für diese Anfrage speichert und nach 90 Tagen löscht. <span class="fill">Einwilligungstext folgt von KBS</span> <span class="fill">Datenschutzerklärung folgt</span></label>
          <p class="hilfe" id="{p}-ok-hilfe" aria-live="polite"></p>
        </div>'''

FALLE = '<div class="falle" aria-hidden="true"><label for="{p}-web">Nicht ausfüllen</label><input id="{p}-web" name="webseite" type="text" tabindex="-1" autocomplete="off"></div>'


def feld(p, name, label, typ="text", pflicht=False, extra="", hilfe="", auto=""):
    req = " required" if pflicht else ""
    stern = '<span class="pflicht">Pflicht</span>' if pflicht else '<span class="frei">freiwillig</span>'
    ac = f' autocomplete="{auto}"' if auto else ""
    hid = f"{p}-{name}-hilfe"
    hin = f'<p class="hinweis-feld">{hilfe}</p>' if hilfe else ""
    if typ == "textarea":
        inp = f'<textarea id="{p}-{name}" name="{name}" rows="6"{req} aria-describedby="{hid}"{extra}></textarea>'
    else:
        inp = f'<input id="{p}-{name}" name="{name}" type="{typ}"{req}{ac} aria-describedby="{hid}"{extra}>'
    return f'<div class="feld"><label for="{p}-{name}">{label} {stern}</label>{hin}{inp}<p class="hilfe" id="{hid}" aria-live="polite"></p></div>'


def einreichen():
    p = "t"
    laender = "".join(
        f'<input type="radio" name="land" id="t-land-{k}" value="{k}"{" required" if i == 0 else ""}><label for="t-land-{k}">{v}</label>' for i, (k, v) in enumerate(LAND.items()))
    main = f'''  <section class="hero" aria-labelledby="titel">
    <div class="container grid kopfzeile">
      <div class="kopfzeile__text">
        <h1 id="titel">Termin einreichen</h1>
        <p class="lead">Vereine und Tempel melden hier ihr Fest; die Redaktion prüft jeden Termin, bevor er im Festkalender steht.</p>
      </div>
    </div>
  </section>

  <section class="container grid formular-seite">
    <form class="formular" action="einreichen-danke.html" method="get" data-form data-danke="einreichen-danke.html" novalidate aria-labelledby="titel">
      <p class="formular__fehler" data-fehler tabindex="-1" hidden></p>
      <fieldset>
        <legend>Der Termin</legend>
        {feld(p, "titel", "Titel", pflicht=True)}
        <div class="reihe">
          {feld(p, "datum", "Datum", "date", True, ' min="2026-11-13"')}
          {feld(p, "zeit", "Beginn", "time", True)}
        </div>
        <div class="reihe">
          {feld(p, "ende-datum", "Ende, Datum", "date")}
          {feld(p, "ende-zeit", "Ende, Uhrzeit", "time")}
        </div>
        {feld(p, "veranstalter", "Veranstalter", pflicht=True, hilfe="Verein, Tempel oder Person, die einlädt.")}
        {feld(p, "beschreibung", "Beschreibung", "textarea", True, hilfe="Was erwartet die Gäste? Höchstens drei Links.")}
      </fieldset>
      <fieldset>
        <legend>Der Ort</legend>
        {feld(p, "adresse", "Ort mit Adresse", pflicht=True, hilfe="Zum Beispiel Saal, Straße und Hausnummer.", auto="street-address")}
        <div class="reihe">
          {feld(p, "stadt", "Stadt", pflicht=True, auto="address-level2")}
          <fieldset class="seg seg--klein" aria-describedby="t-land-hilfe">
            <legend>Land <span class="pflicht">Pflicht</span></legend>
            {laender}
            <p class="hilfe" id="t-land-hilfe" aria-live="polite"></p>
          </fieldset>
        </div>
      </fieldset>
      <fieldset>
        <legend>Eintritt und Bild</legend>
        <div class="reihe">
          {feld(p, "eintritt", "Eintritt", hilfe="Zum Beispiel frei oder ein Betrag.")}
          {feld(p, "tickets", "Link zu den Tickets", "url", auto="url")}
        </div>
        {feld(p, "bild", "Bild", "file", extra=' accept="image/jpeg,image/png"', hilfe="JPEG oder PNG, höchstens 5 MB. Bis zur Freigabe sieht es niemand.")}
        <div class="feld feld--check">
          <input id="t-bildrecht" name="bildrecht" type="checkbox">
          <label for="t-bildrecht">Ich darf dieses Bild weitergeben, und tamil.de darf es zum Termin zeigen.</label>
        </div>
      </fieldset>
      <fieldset>
        <legend>Für Rückfragen</legend>
        <p class="legende-satz">Nur für die Redaktion, nie öffentlich.</p>
        <div class="reihe">
          {feld(p, "name", "Name", pflicht=True, auto="name")}
          {feld(p, "email", "E-Mail", "email", True, auto="email")}
        </div>
        {feld(p, "telefon", "Telefon", "tel", auto="tel")}
        {EINWILLIGUNG.format(p=p)}
        {FALLE.format(p=p)}
      </fieldset>
      <p class="actions"><button class="btn btn--primary" type="submit">Termin einreichen</button></p>
    </form>

    <aside class="rand" aria-labelledby="r-danach">
      <figure class="sheet">
        <figcaption class="sheet__head"><span class="sheet__title" id="r-danach">Was danach passiert</span></figcaption>
        <ol class="ablauf">
          <li>Die Redaktion sieht Ihre Angaben im Eingang.</li>
          <li>Sie prüft Datum und Ort und fragt bei Bedarf nach.</li>
          <li>Nach der Freigabe steht der Termin im <a href="termine.html">Festkalender</a>, mit Ort, Eintritt und Veranstalter.</li>
        </ol>
        <p class="sheet__note">Es geht keine automatische E-Mail hinaus. Jeder Termin wird einzeln eingereicht.</p>
      </figure>
    </aside>
  </section>'''
    seite("einreichen.html", "Termin einreichen | tamil.de",
          "Vereine und Tempel melden hier ihr Fest für den Festkalender von tamil.de.",
          "formular.css", "", main)

    main2 = '''  <section class="hero" aria-labelledby="titel">
    <div class="container grid kopfzeile">
      <div class="kopfzeile__text">
        <h1 id="titel">Danke, die Redaktion meldet sich.</h1>
        <p class="lead">Ihr Termin ist angekommen und wartet im Eingang der Redaktion.</p>
        <p class="actions"><a class="btn btn--primary" href="termine.html">Zum Festkalender</a><a class="btn" href="einreichen.html">Weiteren Termin einreichen</a></p>
      </div>
    </div>
  </section>

  <section class="container grid formular-seite">
    <figure class="sheet quittung" aria-labelledby="q-titel">
      <figcaption class="sheet__head"><span class="sheet__title" id="q-titel">Ihre Einsendung</span></figcaption>
      <table class="tafel tafel--dl">
        <tbody>
          <tr><th scope="row">Vorgangsnummer</th><td><span class="fill">wird beim Absenden vergeben</span></td></tr>
          <tr><th scope="row">Art</th><td>Termin</td></tr>
          <tr><th scope="row">Stand</th><td>eingegangen</td></tr>
        </tbody>
      </table>
      <p class="sheet__note">Bitte die Vorgangsnummer notieren, falls Sie nachfragen. Eine Bestätigung per E-Mail gibt es nicht.</p>
    </figure>
    <aside class="rand" aria-labelledby="r-danach">
      <h2 id="r-danach" class="rand__h">Was jetzt passiert</h2>
      <ol class="ablauf">
        <li>Die Redaktion prüft Datum und Ort und fragt bei Bedarf nach.</li>
        <li>Nach der Freigabe steht der Termin im Festkalender.</li>
        <li>Nach 90 Tagen löscht tamil.de Ihre Kontaktdaten.</li>
      </ol>
    </aside>
  </section>'''
    seite("einreichen-danke.html", "Danke für Ihren Termin | tamil.de",
          "Ihr Termin ist bei der Redaktion von tamil.de angekommen.", "formular.css", "", main2)


def kontakt():
    p = "k"
    main = f'''  <section class="hero" aria-labelledby="titel">
    <div class="container grid kopfzeile">
      <div class="kopfzeile__text">
        <h1 id="titel">Kontakt zur Redaktion</h1>
        <p class="lead">Für Hinweise, Fragen und Kooperationen; Termine bitte über <a href="einreichen.html">Termin einreichen</a>.</p>
      </div>
    </div>
  </section>

  <section class="container grid formular-seite">
    <form class="formular" action="kontakt.html" method="get" data-form novalidate aria-labelledby="f-titel" id="nachricht">
      <p class="formular__fehler" data-fehler tabindex="-1" hidden></p>
      <fieldset>
        <legend id="f-titel">Ihre Nachricht</legend>
        <div class="feld"><label for="k-anliegen">Worum geht es <span class="frei">freiwillig</span></label><select id="k-anliegen" name="anliegen" data-anliegen><option value="">Bitte wählen</option><option value="hinweis">Hinweis auf ein Thema</option><option value="frage">Frage an die Redaktion</option><option value="kooperation">Kooperation</option><option value="werbung">Werbeanfrage</option><option value="verzeichnis">Verzeichnis: Eintrag vorschlagen oder ändern</option></select></div>
        {feld(p, "nachricht", "Nachricht", "textarea", True, hilfe="Höchstens drei Links.")}
        <div class="reihe">
          {feld(p, "name", "Name", pflicht=True, auto="name")}
          {feld(p, "email", "E-Mail", "email", True, auto="email")}
        </div>
        {feld(p, "telefon", "Telefon", "tel", auto="tel")}
        {EINWILLIGUNG.format(p=p)}
        {FALLE.format(p=p)}
      </fieldset>
      <p class="actions"><button class="btn btn--primary" type="submit">Nachricht senden</button></p>
      <p class="formular__stand" data-stand aria-live="polite"></p>
    </form>

    <aside class="rand" aria-labelledby="r-wege">
      <figure class="sheet">
        <figcaption class="sheet__head"><span class="sheet__title" id="r-wege">Andere Wege</span></figcaption>
        <table class="tafel tafel--dl">
          <tbody>
            <tr><th scope="row">E-Mail</th><td><span class="fill">Adresse der Redaktion folgt von KBS</span></td></tr>
            <tr><th scope="row">WhatsApp</th><td><span class="fill">Nummer folgt von KBS</span></td></tr>
            <tr><th scope="row">Anschrift</th><td>KBS Digitalmedia <span class="fill">Anschrift folgt mit dem Impressum</span></td></tr>
            <tr><th scope="row">Werbung</th><td><a href="werben.html">Werbeplätze und Buchung</a></td></tr>
            <tr><th scope="row">Verzeichnis</th><td><a href="verzeichnis.html">Eintrag vorschlagen oder ändern</a></td></tr>
          </tbody>
        </table>
        <p class="sheet__note">Die Redaktion antwortet von Hand, meist innerhalb weniger Tage. Es geht keine automatische E-Mail hinaus.</p>
      </figure>
    </aside>
  </section>'''
    seite("kontakt.html", "Kontakt | tamil.de", "Kontakt zur Redaktion von tamil.de: Hinweise, Fragen, Kooperationen.",
          "formular.css", "", main)


# ---------------------------------------------------------------- Werben und Buchen

PLAETZE = [
    ("leaderboard", "Leaderboard", "unter der Navigation, auf allen Seiten", "728 × 90", "320 × 50"),
    ("sidebar", "Half Page", "in der Seitenspalte", "300 × 600", "300 × 600"),
    ("inarticle", "Im Artikel", "nach dem zweiten Absatz", "728 × 90", "300 × 250"),
    ("billboard", "Billboard", "Startseite, zwischen den Rubriken", "970 × 250", "300 × 250"),
    ("footer", "Fuß", "über dem Fuß der Seite", "728 × 90", "320 × 100"),
    ("mobile", "Mobil", "am Handy fest am unteren Rand", "nur Handy", "320 × 50"),
]
LAUF = [7, 14, 30]
# Vorlauf zwei Werktage ab Freitag, 13.11.: frühester Start Dienstag, 17.11.
FRUEH = dt.date(2026, 11, 17)


def mass(t):
    return f'<span class="num">{t}</span>' if "×" in t else t


def werben():
    zeilen = "".join(
        f'<tr><th scope="row">{n}<span class="hinweis">{w}</span></th><td class="m">{mass(dd)}</td><td class="m">{mass(hh)}</td>'
        + "".join('<td class="preis"><span class="fill">Preis folgt</span></td>' for _ in LAUF)
        + f'<td class="m"><time class="num" datetime="{FRUEH.isoformat()}">{kurz(FRUEH)}</time></td></tr>'
        for k, n, w, dd, hh in PLAETZE)
    main = f'''  <section class="hero" aria-labelledby="titel">
    <div class="container grid kopfzeile">
      <div class="kopfzeile__text">
        <h1 id="titel">Werben bei der tamilischen Community</h1>
        <p class="lead">Sechs Plätze, buchbar für sieben, 14 oder 30 Tage, jeder als Anzeige gekennzeichnet.</p>
      </div>
      <p class="actions kopfzeile__aktion"><a class="btn btn--primary" href="buchen.html">Platz buchen</a><a class="btn" href="kontakt.html?anliegen=werbung">Lieber anfragen</a></p>
    </div>
  </section>

  <section class="container plaetze" aria-labelledby="p-titel">
    <figure class="sheet" aria-labelledby="p-titel">
      <figcaption class="sheet__head">
        <span class="sheet__title" id="p-titel">Werbeplätze und Preise</span>
        <span class="sheet__stand">Maße in Pixeln, Preise je Laufzeit</span>
      </figcaption>
      <div class="tafel-rahmen" tabindex="0" role="region" aria-labelledby="p-titel">
      <table class="karte">
        <thead><tr><th scope="col">Platz</th><th scope="col" class="m">Desktop</th><th scope="col" class="m">Handy</th>{"".join(f'<th scope="col" class="preis">{t} Tage</th>' for t in LAUF)}<th scope="col" class="m">Frühester Start</th></tr></thead>
        <tbody>{zeilen}</tbody>
      </table>
      </div>
      <p class="sheet__note">Preise, Laufzeiten und Bedingungen legt KBS fest. Je Platz läuft eine Anzeige zur selben Zeit; zwischen Buchung und Start liegen zwei Werktage für die Prüfung.</p>
    </figure>
  </section>

  <section class="container grid ablauf-sek" aria-labelledby="a-titel">
    <div class="ablauf-sek__kopf">
      <h2 id="a-titel">So läuft eine Buchung</h2>
      <p class="lead">Ohne Konto und ohne Vertrag am Telefon, bezahlt über Stripe.</p>
    </div>
    <ol class="schritte">
      <li><h3>Platz und Laufzeit wählen</h3><p>Sieben, 14 oder 30 Tage auf einem der sechs Plätze.</p></li>
      <li><h3>Startdatum wählen</h3><p>Belegte Tage sind gesperrt; die gewählten Tage bleiben 35 Minuten für Sie reserviert.</p></li>
      <li><h3>Angaben zur Firma</h3><p>Firma, Ansprechperson, Rechnungsadresse und E-Mail; USt-ID freiwillig.</p></li>
      <li><h3>Werbemittel hochladen</h3><p>Je ein Bild für Desktop und Handy in den Maßen des Platzes, JPEG oder PNG, dazu die Zieladresse.</p></li>
      <li><h3>Prüfen und bezahlen</h3><p>Zusammenfassung, Bedingungen annehmen, Zahlung bei Stripe.</p></li>
    </ol>
    <div class="danach">
      <h3>Nach der Zahlung</h3>
      <p>KBS prüft das Werbemittel und gibt es frei oder lehnt mit Grund ab; bei Ablehnung kommt der volle Betrag zurück. Die Anzeige läuft nur, wenn sie bezahlt, geprüft und im gebuchten Zeitraum ist. Den Stand zeigt ein geheimer Link zur Buchung, mit Einblendungen und Klicks.</p>
      <p class="actions"><a class="btn btn--primary" href="buchen.html">Platz buchen</a></p>
    </div>
  </section>'''
    seite("werben.html", "Werben auf tamil.de: Plätze und Preise", "Sechs Werbeplätze auf tamil.de, Maße, Laufzeiten und der Ablauf der Buchung.",
          "werben.css", "", main)


def monat(jahr, mon, start, lauf, name):
    erster = dt.date(jahr, mon, 1)
    naechst = dt.date(jahr + (mon == 12), mon % 12 + 1, 1)
    tage = (naechst - erster).days
    ende = start + dt.timedelta(days=lauf - 1)
    zellen = ['<td></td>'] * erster.weekday()
    for t in range(1, tage + 1):
        d = dt.date(jahr, mon, t)
        id_ = f"tag-{d.isoformat()}"
        if d < FRUEH:
            zellen.append(f'<td class="zu-frueh"><span class="tagzahl num" aria-label="{d.day}. {MONATE[d.month-1]}, gesperrt">{t}</span></td>')
            continue
        cls = []
        if start <= d <= ende:
            cls.append("im-zeitraum")
        chk = " checked" if d == start else ""
        zellen.append(f'<td{" class=\"" + " ".join(cls) + "\"" if cls else ""}><input type="radio" name="{name}" id="{id_}" value="{d.isoformat()}"{chk}>'
                      f'<label for="{id_}" class="tagzahl num"><span class="visually-hidden">{TAGE[d.weekday()]}, </span>{t}<span class="visually-hidden">. {MONATE[d.month-1]}</span></label></td>')
    while len(zellen) % 7:
        zellen.append("<td></td>")
    reihen = "".join("<tr>" + "".join(zellen[i:i + 7]) + "</tr>" for i in range(0, len(zellen), 7))
    kopf = "".join(f'<th scope="col"><abbr title="{n}">{n}</abbr></th>' for n in TAGE)
    return f'<table class="monat"><caption>{MONATE[mon-1]} {jahr}</caption><thead><tr>{kopf}</tr></thead><tbody>{reihen}</tbody></table>'


def buchen():
    p = "b"
    start = dt.date(2026, 11, 23)
    lauf = 7
    ende = start + dt.timedelta(days=lauf - 1)
    plaetze = "".join(
        f'<input type="radio" name="platz" id="pl-{k}" value="{k}"{" checked" if k == "leaderboard" else ""}>'
        f'<label for="pl-{k}"><span class="pl-name">{n}</span><span class="pl-wo">{w}</span><span class="pl-mass">{mass(dd)} und {mass(hh)}</span></label>'
        for k, n, w, dd, hh in PLAETZE)
    laufz = "".join(f'<input type="radio" name="laufzeit" id="lz-{t}" value="{t}"{" checked" if t == 7 else ""}><label for="lz-{t}"><span class="num">{t}</span> Tage</label>' for t in LAUF)
    main = f'''  <section class="hero" aria-labelledby="titel">
    <div class="container grid kopfzeile">
      <div class="kopfzeile__text">
        <h1 id="titel">Werbeplatz buchen</h1>
        <p class="lead">Fünf Schritte auf einer Seite; bezahlt wird am Ende bei Stripe.</p>
      </div>
      <nav class="kopfzeile__aktion schrittleiste" aria-label="Schritte der Buchung">
        <ol>
          <li><a href="#s1">Platz</a></li><li><a href="#s2">Start</a></li><li><a href="#s3">Angaben</a></li><li><a href="#s4">Werbemittel</a></li><li><a href="#s5">Bezahlen</a></li>
        </ol>
      </nav>
    </div>
  </section>

  <form class="container buchung" action="buchen.html" method="get" data-form novalidate aria-labelledby="titel">
    <p class="formular__fehler" data-fehler tabindex="-1" hidden></p>
    <section class="schritt grid" id="s1" aria-labelledby="s1-h">
      <h2 id="s1-h" class="schritt__h"><span class="num">1</span> Platz und Laufzeit</h2>
      <div class="schritt__inhalt">
        <fieldset class="wahl wahl--platz"><legend class="visually-hidden">Platz</legend>{plaetze}</fieldset>
        <fieldset class="seg"><legend>Laufzeit</legend>{laufz}</fieldset>
      </div>
    </section>

    <section class="schritt grid" id="s2" aria-labelledby="s2-h">
      <h2 id="s2-h" class="schritt__h"><span class="num">2</span> Startdatum</h2>
      <div class="schritt__inhalt">
        <fieldset class="kalender"><legend class="visually-hidden">Startdatum</legend>
          {monat(2026, 11, start, lauf, "start")}
          {monat(2026, 12, start, lauf, "start")}
        </fieldset>
        <p class="legende-satz"><span class="muster muster--zu"></span> gesperrt: zwei Werktage Vorlauf für die Prüfung <span class="muster muster--zeit"></span> Ihr Zeitraum, <time datetime="{start.isoformat()}">{kurz(start)}</time> bis <time datetime="{ende.isoformat()}">{kurz(ende)}</time></p>
        <p class="legende-satz">Belegt ist auf diesem Platz noch kein Tag. Die gewählten Tage bleiben 35 Minuten für Sie reserviert.</p>
      </div>
    </section>

    <section class="schritt grid" id="s3" aria-labelledby="s3-h">
      <h2 id="s3-h" class="schritt__h"><span class="num">3</span> Ihre Angaben</h2>
      <div class="schritt__inhalt">
        <div class="reihe">{feld(p, "firma", "Firma", pflicht=True, auto="organization")}{feld(p, "person", "Ansprechperson", pflicht=True, auto="name")}</div>
        {feld(p, "adresse", "Rechnungsadresse", "textarea", True)}
        <div class="reihe">{feld(p, "email", "E-Mail", "email", True, auto="email")}{feld(p, "telefon", "Telefon", "tel", auto="tel")}</div>
        {feld(p, "ustid", "USt-ID")}
      </div>
    </section>

    <section class="schritt grid" id="s4" aria-labelledby="s4-h">
      <h2 id="s4-h" class="schritt__h"><span class="num">4</span> Werbemittel</h2>
      <div class="schritt__inhalt">
        <div class="reihe">
          {feld(p, "desktop", "Bild für Desktop", "file", True, ' accept="image/jpeg,image/png"', 'Leaderboard: <span class="num">728 × 90</span> Pixel, JPEG oder PNG.')}
          {feld(p, "handy", "Bild für das Handy", "file", True, ' accept="image/jpeg,image/png"', 'Leaderboard: <span class="num">320 × 50</span> Pixel, JPEG oder PNG.')}
        </div>
        {feld(p, "ziel", "Zieladresse", "url", True, ' placeholder="https://"', "Wohin die Anzeige führt.", "url")}
        <p class="legende-satz">Keine bewegten Banner, kein Video, keine fremden Skripte. Gestalten müssen Sie das Werbemittel selbst.</p>
      </div>
    </section>

    <section class="schritt grid" id="s5" aria-labelledby="s5-h">
      <h2 id="s5-h" class="schritt__h"><span class="num">5</span> Prüfen und bezahlen</h2>
      <div class="schritt__inhalt">
        <figure class="sheet">
          <figcaption class="sheet__head"><span class="sheet__title">Ihre Buchung</span><span class="sheet__stand">reserviert für 35 Minuten</span></figcaption>
          <table class="tafel tafel--dl">
            <tbody>
              <tr><th scope="row">Platz</th><td>Leaderboard, unter der Navigation</td></tr>
              <tr><th scope="row">Laufzeit</th><td><span class="num">7</span> Tage</td></tr>
              <tr><th scope="row">Zeitraum</th><td>Mo <time class="num" datetime="{start.isoformat()}">{kurz(start)}</time> bis So <time class="num" datetime="{ende.isoformat()}">{kurz(ende)}</time></td></tr>
              <tr><th scope="row">Betrag</th><td><span class="fill">Preis folgt von KBS</span></td></tr>
            </tbody>
          </table>
        </figure>
        <div class="feld feld--check">
          <input id="b-bed" name="bedingungen" type="checkbox" required aria-describedby="b-bed-hilfe">
          <label for="b-bed">Ich nehme die Bedingungen für Anzeigen an. <span class="fill">Bedingungen folgen von KBS</span></label>
          <p class="hilfe" id="b-bed-hilfe" aria-live="polite"></p>
        </div>
        <p class="actions"><button class="btn btn--primary" type="submit" aria-disabled="true" disabled>Weiter zu Stripe</button></p>
        <p class="legende-satz">Bezahlen ist noch nicht möglich: Preise, Bedingungen und das Stripe-Konto folgen von KBS. Kartendaten sieht tamil.de nie.</p>
      </div>
    </section>
  </form>'''
    seite("buchen.html", "Werbeplatz buchen | tamil.de", "Einen Werbeplatz auf tamil.de in fünf Schritten buchen.",
          "werben.css", "", main)


if __name__ == "__main__":
    for b in RB:
        if b["story_id"] != 30:
            artikel(b)
    rubrik()
    verzeichnis()
    verzeichnis_eintrag()
    einreichen()
    kontakt()
    werben()
    buchen()
    for datei, aktiv in (("index.html", ""), ("artikel.html", ""), ("termine.html", "Termine"), ("kino.html", "Kino")):
        kopf_ersetzen(datei, aktiv)
    print("fertig")
