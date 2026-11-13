"""Cockpit-Probe hm-terrazzo (Linie D „Terrazzo“): erzeugt die Screens als statische HTML-Dateien.

Aufruf vom Repo-Root: python3 design/cockpit/hm-terrazzo/bauen.py
Echt: Titel, Texte, Bilder und Hinweise der Entwürfe (design/inhalte/rueckblick/, docs/redaktion/rueckblick-2026.md),
Regeln (docs/regeln-social.md), Werbeplätze (ads.php). Erfunden und so gekennzeichnet: Personen, Firmen, Adressen,
Nummern, Beträge, Zählwerte, Kennungen.
"""
from __future__ import annotations

import json
import re
from html import escape as e
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parents[2]
RB = json.loads((ROOT / "design/inhalte/rueckblick/rueckblick.json").read_text(encoding="utf-8"))["beitraege"]
BEITRAG = {b["story_id"]: b for b in RB}
BILD = "../../inhalte/rueckblick/"
JETZT = "Freitag, 13. November 2026, 21:40"


def entwuerfe_aus_bericht():
    """Die wartenden Rückblick-Entwürfe aus docs/redaktion/rueckblick-2026.md (Tabelle „Entwürfe, die auf Freigabe warten“)."""
    text = (ROOT / "docs/redaktion/rueckblick-2026.md").read_text(encoding="utf-8")
    teil = text.split("## Entwürfe, die auf Freigabe warten", 1)[1].split("\n## ", 1)[0]
    zeilen = []
    for z in teil.splitlines():
        m = re.match(r"\| (\d{4}-\d\d-\d\d) \| (\d+) \| (\d+) \| (.+?) \| (\d+) \| (.+?) \| (.*?) \|$", z)
        if m:
            zeilen.append(dict(datum=m[1], story=int(m[2]), entwurf=int(m[3]), titel=m[4], woerter=int(m[5]),
                               bild=m[6], vor=m[7].strip()))
    return zeilen


ENTWUERFE = entwuerfe_aus_bericht()
RADAR = [(54, "„OM“ im Kino: 12 Spielorte in Deutschland"),
         (4, "THADAM 2026: Tamilische Networking- und Gala-Nacht am 13. Dezember in Bern"),
         (5, "„Jailer 2“ am 15. November zum Spezialpreis im Kino Claudia in Kloten")]

ARBEIT = [("uebersicht.html", "Übersicht", None), ("entwurf.html", "Entwürfe", len(ENTWUERFE) + 3),
          ("eingang.html", "Eingang", 5), ("social.html", "Social", 3), ("verzeichnis.html", "Verzeichnis", 2),
          ("buchungen.html", "Buchungen", 6)]
BETRIEB = ["Schalter", "Kosten", "Quellen", "Protokoll", "Benutzer"]


def tag(d: str) -> str:
    j, m, t = d.split("-")
    return f"{int(t)}.{int(m)}.{j}"


def nav(aktiv: str) -> str:
    links = "".join(
        f'<li><a href="{h}"{" aria-current=\"page\"" if n == aktiv else ""}>{n}'
        f'{f" <span class=\"code\">{z}</span>" if z else ""}</a></li>' for h, n, z in ARBEIT)
    betrieb = "".join(f'<li><a href="uebersicht.html#betrieb">{n}</a></li>' for n in BETRIEB)
    return (f'<div class="nav"><ul aria-label="Arbeit">{links}</ul>'
            f'<ul class="nav__betrieb" aria-label="Betrieb">{betrieb}</ul></div>')


def seite(datei: str, titel: str, aktiv: str, inhalt: str) -> None:
    html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titel)}: Redaktion tamil.de</title>
<link rel="preload" href="schriften/onest-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="cockpit.css">
<script src="app.js" defer></script>
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="kopf">
  <div class="container kopf__zeile">
    <a class="kopf__marke" href="uebersicht.html"><img src="../../inhalte/logo.png" width="300" height="121" alt="tamil.de"><span>Redaktion</span></a>
    <div class="kopf__stand"><span>Radar läuft, letzter Lauf <span class="code">21:37</span>, nächster <span class="code">21:40</span></span>
      <span>angemeldet als a.beispiel</span>
      <form method="post" action="uebersicht.html"><button class="knopf knopf--zweit" type="submit">Abmelden</button></form></div>
  </div>
  <div class="container"><nav aria-label="Cockpit">{nav(aktiv)}<details class="menue"><summary>Menü</summary>{nav(aktiv)}</details></nav></div>
  <div class="kopf__fuge"></div>
</header>
<div class="banner" role="status"><p class="container"><span class="wort-fehler">Angehalten: Verzeichnis.</span>
  Seit 12.11. 18:20, von l.beispiel, Grund: „Kategorienliste von KBS steht aus“. Neue Verzeichnis-Einsendungen werden nicht abgeholt; Prüfen und Freigeben von Hand gehen weiter.
  <a href="uebersicht.html#schalter">Schalter ansehen</a></p></div>
<main id="inhalt" class="container">
{inhalt}
</main>
<footer class="container fuss"><p>Probe der Linie Terrazzo, Stand 13.11.2026. Titel, Texte, Bilder und Hinweise der Entwürfe sind echt (Rückblick 2026);
Personen, Firmen, Adressen, Nummern, Beträge, Zählwerte und Kennungen sind Beispieldaten. E-Mail nur @example.org. Formulare senden nichts.</p></footer>
</body>
</html>
"""
    (HIER / datei).write_text(html, encoding="utf-8")


def kopf(titel: str, satz: str, pfad: str = "", rechts: str = "") -> str:
    p = f'<p class="pfad">{pfad}</p>' if pfad else ""
    return f'<div class="seitenkopf"><div>{p}<h1>{titel}</h1><p>{satz}</p></div>{rechts}</div>'


# ------------------------------------------------------------------ Übersicht
def uebersicht() -> None:
    zeilen = []
    zeilen.append('<tr aria-current="true"><td data-l="Code"><span class="code">E-7</span></td>'
                  f'<td><a href="entwurf-lizenz-fehlt.html">{e(BEITRAG[30]["titel"])}</a><span class="unter">Entwurf, Story 30, 485 Wörter</span></td>'
                  '<td data-l="Stand"><span class="wort-fehler">Lizenz fehlt</span></td></tr>')
    for nr, t in RADAR:
        zeilen.append(f'<tr><td data-l="Code"><span class="code">E-{nr}</span></td><td><a href="entwurf.html">{e(t)}</a>'
                      f'<span class="unter">Entwurf aus dem laufenden Radar</span></td><td data-l="Stand">neu</td></tr>')
    zeilen += [
        '<tr><td data-l="Code"><span class="code">T-0142</span></td><td><a href="eingang.html">Pongal-Feier des Beispiel-Vereins Hamm</a><span class="unter">Einsendung Termin, Agent: mögliche Dublette</span></td><td data-l="Stand">vorbereitet</td></tr>',
        '<tr><td data-l="Code"><span class="code">S-31</span></td><td><a href="social.html">„Jailer 2“ am 15. November zum Spezialpreis im Kino Claudia in Kloten</a><span class="unter">Instagram, Karenz bis 21:46</span></td><td data-l="Stand">Karenz</td></tr>',
        '<tr><td data-l="Code"><span class="code">VE-0012</span></td><td><a href="verzeichnis.html">Tamil Sangam Düsseldorf</a><span class="unter">Verzeichnis, neu, Agent: Dublette von V-0004</span></td><td data-l="Stand">geprüft</td></tr>',
        '<tr><td data-l="Code"><span class="code">B-0004</span></td><td><a href="buchungen.html">Beispiel Feinkost GmbH, In-Article</a><span class="unter">Werbemittel prüfen, Handy-Format weicht ab</span></td><td data-l="Stand">in Prüfung</td></tr>',
    ]
    weitere = "".join(
        f'<tr><td data-l="Code"><span class="code">E-{z["entwurf"]}</span></td><td>{e(z["titel"])}'
        f'<span class="unter">Ereignis {tag(z["datum"])}, {z["woerter"]} Wörter, Bild: {e(z["bild"])}</span></td>'
        f'<td data-l="Vor der Freigabe">{e(z["vor"]) or "nichts offen"}</td></tr>' for z in ENTWUERFE[1:6])
    kanaele = [("alles", "Alles", "läuft", ""), ("redaktion", "Redaktion (Scan, Agenten)", "läuft", ""),
               ("website", "Website (Übertragung)", "läuft", ""), ("eingang", "Eingang", "läuft", ""),
               ("verzeichnis", "Verzeichnis", "angehalten", "seit 12.11. 18:20, l.beispiel: Kategorienliste von KBS steht aus"),
               ("instagram", "Instagram", "läuft", "Trockenmodus"), ("facebook", "Facebook", "läuft", "Trockenmodus"),
               ("whatsapp", "WhatsApp", "läuft", "nur Entwürfe")]
    schalter = "".join(
        f'<tr><td>{n}<span class="unter">{e(g)}</span></td><td data-l="Stand"><span class="{"wort-fehler" if s == "angehalten" else "wort-gut"}">{s}</span></td>'
        f'<td><form method="post" action="uebersicht.html#schalter"><button class="knopf knopf--zweit" type="submit">{"Fortsetzen" if s == "angehalten" else "Anhalten"}<span class="visually-hidden">: {n}</span></button></form></td></tr>'
        for k, n, s, g in kanaele if k != "alles")
    inhalt = kopf("Übersicht", f"{JETZT}. Was auf eine Entscheidung wartet, links; der Betrieb rechts hinter der Fuge.") + f"""
<div class="felder">
  <section class="feld" aria-labelledby="w-h">
    <div class="block__kopf"><h2 id="w-h">Wartet auf eine Entscheidung</h2><span class="leise">7 Vorgänge, der älteste zuerst</span></div>
    <table class="spec"><thead><tr><th>Code</th><th>Vorgang</th><th>Stand</th></tr></thead><tbody>{''.join(zeilen)}</tbody></table>
    <div class="block">
      <div class="block__kopf"><h2 id="r-h">Rückblick: {len(ENTWUERFE)} Entwürfe warten</h2><a href="entwurf.html">Alle Entwürfe</a></div>
      <table class="spec"><thead><tr><th>Code</th><th>Titel</th><th>Vor der Freigabe</th></tr></thead><tbody>{weitere}</tbody></table>
      <p class="leise klein nach-xs">Hinweise wörtlich aus dem Bericht der Redakteure (Stand 12.11.2026).</p>
    </div>
  </section>
  <section class="feld" id="betrieb" aria-labelledby="b-h">
    <h2 id="b-h">Betrieb</h2>
    <div class="block" id="schalter">
      <h3>Stopp-Schalter</h3>
      <table class="spec spec--knapp"><thead><tr><th>Kanal</th><th>Stand</th><th><span class="visually-hidden">Aktion</span></th></tr></thead><tbody>{schalter}</tbody></table>
      <details class="auf nach-md"><summary>Alles anhalten</summary><div>
        <form method="post" action="uebersicht.html#schalter">
          <label class="feldname" for="grund">Grund <span class="pflicht">*</span> <small>höchstens 300 Zeichen, steht im Protokoll</small></label>
          <input class="eingabe" id="grund" name="grund" maxlength="300" required>
          <div class="knoepfe"><button class="knopf" type="submit">Alles anhalten</button></div></form>
        <p class="leise klein nach-xs">Hält jeden Kanal sofort an, auch Social in der Karenz. Bearbeiten und Freigeben von Hand gehen weiter.</p></div></details>
    </div>
    <div class="block">
      <h3>Budget</h3>
      <dl class="satz"><dt>Heute</dt><dd><span class="code">$1.84</span> von <span class="code">$5.00</span></dd>
        <dt>November</dt><dd><span class="code">$38.20</span> von <span class="code">$100.00</span></dd>
        <dt>Stand</dt><dd><span class="wort-gut">unter der Warnschwelle</span> (80 %)</dd></dl>
    </div>
    <div class="block">
      <h3>Radar</h3>
      <dl class="satz"><dt>Letzter Lauf</dt><dd><span class="code">21:37</span>, 214 Meldungen, 0 neue Entwürfe</dd>
        <dt>Takt</dt><dd>alle 3 Minuten</dd><dt>Quellen mit Fehler</dt><dd><span class="wort-fehler">2</span> von 48, <a href="uebersicht.html#betrieb">Quellen ansehen</a></dd></dl>
    </div>
  </section>
</div>"""
    seite("uebersicht.html", "Übersicht", "Übersicht", inhalt)


# ------------------------------------------------------------------ Entwurf
CLAIMS = [
    [("C1", "Deepavali war am Sonntag, 8. November 2026.", "belegt", "Q1"),
     ("C2", "Der Sivaalayam-Tempel in München hatte für diesen Tag Feierlichkeiten angekündigt.", "belegt", "Q2"),
     ("C3", "Der Sri Ganesha Hindu Temple in Berlin hat das Lichterfest mit Lakshmi Pooja im Kalender.", "teilweise", "Q3, ohne Datum"),
     ("C4", "Der Düsseldorf Tamil Sangam lädt am Sonntag, 15. November, zu seiner Feier ein.", "belegt", "Q4")],
    [("C5", "Der Name kommt aus dem Sanskrit und heißt ungefähr „Reihe von Lichtern“.", "Hintergrund", "Q5")],
    [("C6", "Den Termin bestimmt der hinduistische Mondkalender; meist eine Neumondnacht im Oktober oder November.", "Hintergrund", "Q5")],
    [],
]
QUELLEN = [("Q1", "Festkalender 2026 (Hintergrund)", "Primärquelle nein"),
           ("Q2", "Sivaalayam München, Ankündigung auf der eigenen Seite", "Primärquelle"),
           ("Q3", "Sri Ganesha Hindu Temple Berlin, Festkalender", "Primärquelle"),
           ("Q4", "Düsseldorf Tamil Sangam, Einladung", "Primärquelle"),
           ("Q5", "Lexikon-Eintrag Deepavali", "Hintergrund")]


def entwurf(lizenz_fehlt: bool) -> None:
    b = BEITRAG[30]
    absaetze = ""
    for i, (p, cl) in enumerate(zip(b["absaetze"], CLAIMS), 1):
        if cl:
            items = "".join(
                f'<li><span class="code">{c}</span> {e(t)}<br><span class="{"wort-gut" if s == "belegt" else ("wort-fehler" if s == "teilweise" else "leise")}">{s}</span>'
                f' <span class="leise">{e(q)}</span></li>' for c, t, s, q in cl)
        else:
            items = '<li class="leise">Keine prüfbare Aussage: beschreibt Bräuche.</li>'
        absaetze += (f'<div class="absatz"><p><span class="absatz__kopf">Absatz {i}</span><br>{e(p)}</p>'
                     f'<ul aria-label="Aussagen in Absatz {i}">{items}</ul></div>')
    quellen = "".join(f'<tr><td data-l="Code"><span class="code">{q}</span></td><td>{e(n)}</td><td data-l="Art">{a}</td></tr>' for q, n, a in QUELLEN)
    if lizenz_fehlt:
        bild = f"""<div class="bild bild--fehlt">
  <figure><img src="{BILD}{b['bild']}" width="1200" height="800" alt="{e(b['alt'])}"><figcaption>Bild der Medien-Rolle, ohne Lizenz-Datensatz nicht verwendbar</figcaption></figure>
  <div class="meldung meldung--fehler" role="alert"><p><span class="wort-fehler">Lizenz fehlt.</span> Zu diesem Bild gibt es keinen Lizenz-Datensatz. Ohne Datensatz kein Bild (Abnahmekriterium K6); Freigeben ist gesperrt, bis Lizenz eingetragen, Bild ersetzt oder die Bildkarte gewählt ist.</p>
  <p>Gefunden: Commons-Datei <a href="{e(b['quelle_bild'])}">Sri_Ganesha_Hindutempel_1_Berlin_2026.jpg</a>; der Abruf der Lizenzangaben ist um 21:12 abgebrochen.</p></div>
</div>"""
        rechts_bild = f"""<form class="karte" method="post" action="entwurf.html" aria-labelledby="l-h">
  <h3 id="l-h">Lizenz eintragen</h3>
  <p class="grund">Pflicht sind Herkunft, Rechteinhaber und Lizenz. NC- und ND-Lizenzen sind nicht zulässig.</p>
  <div class="reihe nach-md"><label class="feldname" for="l-herkunft">Herkunft <span class="pflicht">*</span></label>
    <select class="eingabe" id="l-herkunft" required><option>Wikimedia Commons</option><option>Archiv</option><option>Quelle der Story (Register)</option><option>Upload</option><option>KI-Bild</option></select></div>
  <div class="reihe"><label class="feldname" for="l-inhaber">Rechteinhaber <span class="pflicht">*</span></label><input class="eingabe" id="l-inhaber" value="18quirl08" required></div>
  <div class="reihe reihe--zwei"><div><label class="feldname" for="l-lizenz">Lizenz <span class="pflicht">*</span></label>
    <select class="eingabe" id="l-lizenz" required><option>CC BY-SA 4.0</option><option>CC BY 4.0</option><option>gemeinfrei, CC0</option><option>Plattformlizenz</option><option>eigene Vereinbarung</option></select></div>
    <div><label class="feldname" for="l-ablauf">Ablauf <small>falls befristet</small></label><input class="eingabe" id="l-ablauf" type="date"></div></div>
  <div class="reihe"><label class="feldname" for="l-url">Lizenz- oder Quellseite</label><input class="eingabe" id="l-url" type="url" value="{e(b['quelle_bild'])}"></div>
  <div class="reihe"><label class="feldname" for="l-umfang">Umfang</label><input class="eingabe" id="l-umfang" value="Online-Veröffentlichung auf tamil.de"></div>
  <fieldset class="reihe"><legend>Nutzung in sozialen Netzen</legend><div class="zellen">
    <input type="radio" name="l-social" id="ls-ja" checked><label for="ls-ja">erlaubt</label>
    <input type="radio" name="l-social" id="ls-nein"><label for="ls-nein">nicht erlaubt, Bildkarte</label></div></fieldset>
  <div class="reihe"><label class="feldname" for="l-nachweis">Bildnachweis <span class="pflicht">*</span></label><input class="eingabe" id="l-nachweis" value="{e(b['nachweis'])}" required></div>
  <label class="haken"><input type="checkbox" id="l-ki"><span>KI-Bild (Nachweis „Symbolbild: KI-generiert“)</span></label>
  <div class="knoepfe"><button class="knopf" type="submit">Lizenz speichern</button><button class="knopf knopf--zweit" type="submit">Erneut abrufen</button><button class="knopf knopf--leise" type="submit">Bildkarte nehmen</button></div>
</form>"""
        freigabe = """<p class="grund"><span class="wort-fehler">Gesperrt:</span> Lizenz fehlt. Erst den Datensatz eintragen.</p>
  <div class="knoepfe"><button class="knopf" type="button" disabled>Freigeben (Stand 4)</button><button class="knopf knopf--zweit" type="submit">Zurückstellen</button><button class="knopf knopf--leise" type="submit">Ablehnen</button></div>"""
        stand_wort = '<span class="wort-fehler">Lizenz fehlt</span>'
    else:
        bild = f"""<div class="bild">
  <figure><img src="{BILD}{b['bild']}" width="1200" height="800" alt="{e(b['alt'])}"><figcaption>{e(b['nachweis'])}</figcaption></figure>
  <dl class="satz"><dt>Herkunft</dt><dd>Wikimedia Commons</dd><dt>Rechteinhaber</dt><dd>18quirl08</dd>
    <dt>Lizenz</dt><dd><a href="https://creativecommons.org/licenses/by-sa/4.0/deed.de" rel="license">CC BY-SA 4.0</a></dd>
    <dt>Umfang</dt><dd>Online-Veröffentlichung auf tamil.de</dd><dt>Soziale Netze</dt><dd>erlaubt</dd>
    <dt>Quelle</dt><dd><a href="{e(b['quelle_bild'])}">Commons-Seite der Datei</a></dd><dt>KI</dt><dd>nein</dd>
    <dt>Bildnachweis</dt><dd>{e(b['nachweis'])}</dd><dt>Alt-Text</dt><dd>{e(b['alt'])}</dd></dl>
</div>"""
        rechts_bild = ""
        freigabe = """<p class="grund">Du gibst Stand 4 frei, so wie er hier steht. Ändert jemand vorher etwas, wird die Freigabe abgewiesen.</p>
  <div class="knoepfe"><button class="knopf" type="submit">Freigeben (Stand 4)</button><button class="knopf knopf--zweit" type="submit">Zurückstellen</button><button class="knopf knopf--leise" type="submit">Ablehnen</button></div>"""
        stand_wort = "neu"
    hinweise = "".join(f"<li>{e(h)}</li>" for h in ENTWUERFE[0]["vor"].split("; "))
    inhalt = kopf(f'Entwurf <span class="code">E-7</span>', f"Story 30, Rückblick-Nachtrag zum 8.11.2026, Rubrik Events, Stand 4, zuletzt vom Radar um 21:12. Status: {stand_wort}.",
                  '<a href="uebersicht.html">Übersicht</a> / Entwürfe') + f"""
<div class="felder felder--8-4">
  <article class="feld" aria-labelledby="t-h">
    <h2 class="entwurf__titel" id="t-h">{e(b['titel'])}</h2>
    <p class="entwurf__teaser">{e(b['teaser'])}</p>
    <div class="block">{bild}</div>
    <div class="block"><div class="block__kopf"><h2>Text und Aussagen</h2><span class="leise">links der Absatz, rechts was der Radar darin belegt hat</span></div>
      <div class="fuge-oben">{absaetze}</div></div>
    <div class="block"><h2>Quellen</h2><table class="spec spec--knapp"><thead><tr><th>Code</th><th>Quelle</th><th>Art</th></tr></thead><tbody>{quellen}</tbody></table></div>
    <div class="block">
      <details class="auf"><summary>Bearbeiten: Titel, Vorspann, Rubrik, Schlagworte</summary><div>
        <div class="reihe"><label class="feldname" for="f-titel">Titel <small>höchstens 90 Zeichen</small></label><input class="eingabe" id="f-titel" maxlength="90" value="{e(b['titel'])}"></div>
        <div class="reihe"><label class="feldname" for="f-teaser">Vorspann <small>höchstens 220 Zeichen</small></label><textarea class="eingabe" id="f-teaser" maxlength="220">{e(b['teaser'])}</textarea></div>
        <div class="knoepfe"><button class="knopf knopf--zweit" type="button">Speichern (wird Stand 5)</button></div></div></details>
      <details class="auf"><summary>Fassungen</summary><div><ul class="hinweise">
        <li><span class="code">12.11. 17:58</span> Text, Radar, <span class="code">a3f9c1</span></li>
        <li><span class="code">12.11. 18:01</span> Faktencheck, Radar, <span class="code">a3f9c1</span></li>
        <li><span class="code">13.11. 21:12</span> Medien, Radar, <span class="code">7be240</span></li></ul></div></details>
    </div>
  </article>
  <aside class="feld" aria-labelledby="p-h">
    <h2 id="p-h">Prüfung</h2>
    <div class="block"><h3>Vor der Freigabe</h3><ul class="hinweise">{hinweise}</ul>
      <p class="leise klein nach-xs">Aus dem Bericht der Redakteure; C3 ist nur teilweise belegt.</p></div>
    <div class="block"><h3>Faktencheck</h3><dl class="satz"><dt>Aussagen</dt><dd><span class="code">6</span></dd><dt>belegt</dt><dd><span class="code">3</span></dd><dt>teilweise</dt><dd><span class="code">1</span> (C3)</dd><dt>Hintergrund</dt><dd><span class="code">2</span></dd><dt>sensibel</dt><dd>nein</dd></dl></div>
    {rechts_bild}
    <form class="karte" method="post" action="entwurf.html" aria-labelledby="fr-h">
      <h3 id="fr-h">Freigabe</h3>{freigabe}
    </form>
  </aside>
</div>"""
    seite("entwurf-lizenz-fehlt.html" if lizenz_fehlt else "entwurf.html", "Entwurf E-7", "Entwürfe", inhalt)


# ------------------------------------------------------------------ Eingang
EINGANG = [
    ("T-0142", "13.11. 19:02", "Termin", "Pongal-Feier des Beispiel-Vereins Hamm, 16.1.2027", "mögliche Dublette von T-0131", "vorbereitet"),
    ("B-0139", "13.11. 16:47", "Beitrag", "Hinweis: neue Tamilschule im Beispielort", "Link ohne Datum", "vorbereitet"),
    ("W-0138", "13.11. 11:20", "Werbung", "Beispiel Reisen GmbH fragt nach dem Platz Billboard im Dezember", "", "vorbereitet"),
    ("K-0137", "12.11. 22:05", "Kontakt", "Frage zu einem Bildnachweis", "", "vorbereitet"),
    ("T-0136", "12.11. 09:31", "Termin", "Navarathri-Abend, 3.10.2026", "Datum in der Vergangenheit", "vorbereitet"),
]
ARTEN = [("alle", "Alle", 5, "eingang.html"), ("termin", "Termin", 2, "eingang.html"), ("beitrag", "Beitrag", 1, "eingang.html"),
         ("kooperation", "Kooperation", 0, "eingang-kooperation.html"), ("werbung", "Werbung", 1, "eingang.html"), ("kontakt", "Kontakt", 1, "eingang.html")]


def filter_zellen(aktiv: str) -> str:
    return ('<nav class="zellen zellen--filter" aria-label="Art der Einsendung">' + "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if k == aktiv else ""}>{n} <span class="code">{z}</span></a>' for k, n, z, h in ARTEN) + "</nav>")


def eingang() -> None:
    rows = "".join(
        f'<tr{" aria-current=\"true\"" if i == 0 else ""}><td data-l="Code"><span class="code">{c}</span></td><td data-l="Eingang"><span class="code">{t}</span></td>'
        f'<td data-l="Art">{a}</td><td><a href="eingang.html#vorgang">{e(ti)}</a></td><td data-l="Agent">{f"<span class=\"wort-fehler\">{e(h)}</span>" if h else "<span class=\"leise\">nichts markiert</span>"}</td><td data-l="Stand">{s}</td></tr>'
        for i, (c, t, a, ti, h, s) in enumerate(EINGANG))
    inhalt = kopf("Eingang", "Einsendungen von der Website. Der Agent prüft und markiert, entscheiden tust du. Antworten nur von Hand per E-Mail.",
                  rechts=filter_zellen("alle")) + f"""
<div class="felder felder--voll"><section class="feld" aria-labelledby="l-h"><h2 id="l-h" class="visually-hidden">Einsendungen</h2>
<table class="spec"><thead><tr><th>Code</th><th>Eingang</th><th>Art</th><th>Betreff</th><th>Agent</th><th>Stand</th></tr></thead><tbody>{rows}</tbody></table></section></div>
<div class="felder" id="vorgang">
  <section class="feld" aria-labelledby="v-h">
    <div class="block__kopf"><h2 id="v-h">Termin <span class="code">T-0142</span></h2><span class="leise">Angaben des Einsenders, ungeprüft</span></div>
    <dl class="satz"><dt>Titel</dt><dd>Pongal-Feier des Beispiel-Vereins Hamm</dd><dt>Beginn</dt><dd><span class="code">16.01.2027 15:00</span></dd><dt>Ende</dt><dd><span class="code">16.01.2027 21:00</span></dd>
      <dt>Ort</dt><dd>Gemeindesaal, Beispielstraße 1, 59000 Hamm, DE</dd><dt>Veranstalter</dt><dd>Beispiel-Verein Hamm e. V.</dd>
      <dt>Beschreibung</dt><dd>Thai Pongal mit gemeinsamem Kochen, Tanz der Kindergruppe und Abendessen. Eintritt frei, Anmeldung erbeten.</dd>
      <dt>Eintritt</dt><dd>frei</dd><dt>Ticket-Link</dt><dd class="leise">keiner</dd><dt>Bild</dt><dd>keins</dd>
      <dt>Einsender</dt><dd>A. Beispiel, <a href="mailto:a.beispiel@example.org?subject=Ihre%20Einsendung%20T-0142">a.beispiel@example.org</a></dd>
      <dt>Einwilligung</dt><dd>ja, Fassung 1 vom 13.11.2026</dd></dl>
  </section>
  <aside class="feld" aria-labelledby="a-h">
    <h2 id="a-h">Prüfung des Agenten</h2>
    <ul class="hinweise"><li><span class="wort-fehler">Mögliche Dublette</span> von <a href="eingang.html#vorgang"><span class="code">T-0131</span></a>: gleicher Veranstalter, gleiches Datum, eingegangen am 2.11.</li>
      <li><span class="wort-gut">Datum in der Zukunft</span>, Ort in DE</li><li>Zusammenfassung: Thai-Pongal-Feier eines Vereins in Hamm am 16. Januar 2027, Eintritt frei.</li></ul>
    <form class="karte" method="post" action="eingang.html" aria-labelledby="e-h">
      <h3 id="e-h">Entscheidung</h3>
      <p class="grund">Übernehmen legt einen Entwurf an, vermerkt als „Angaben des Einsenders, ungeprüft“. Vorher T-0131 ansehen.</p>
      <div class="reihe"><label class="feldname" for="notiz">Notiz <small>intern</small></label><input class="eingabe" id="notiz"></div>
      <div class="knoepfe"><button class="knopf" type="submit">Übernehmen</button><button class="knopf knopf--zweit" type="submit">Erledigt</button>
        <button class="knopf knopf--leise" type="submit">Ablehnen</button><button class="knopf knopf--leise" type="submit">Spam</button></div>
      <p class="grund">Gelöscht wird 90 Tage nach dem Abschluss, Spam nach 7 Tagen.</p>
    </form>
  </aside>
</div>"""
    seite("eingang.html", "Eingang", "Eingang", inhalt)
    leer = kopf("Eingang", "Einsendungen von der Website, gefiltert nach Kooperation.", rechts=filter_zellen("kooperation")) + """
<div class="felder felder--voll"><section class="feld" aria-labelledby="k-h"><h2 id="k-h">Keine Anfrage zur Kooperation</h2>
<p class="nach-xs">Hier stehen Anfragen von Vereinen, Veranstaltern und Firmen aus dem Formular „Kooperation“. Neue Einsendungen holt der Radar alle drei Minuten ab.</p>
<div class="knoepfe"><a class="knopf knopf--zweit" href="eingang.html">Alle Einsendungen zeigen</a></div></section></div>"""
    seite("eingang-kooperation.html", "Eingang: Kooperation", "Eingang", leer)


# ------------------------------------------------------------------ Social
def social() -> None:
    hist = [("Instagram", "13.11. 18:02", "Mahotsavam im Sivan Kovil Glattbrugg", "veröffentlicht im Trockenmodus", ""),
            ("Facebook", "13.11. 18:07", "Mahotsavam im Sivan Kovil Glattbrugg", "veröffentlicht im Trockenmodus", ""),
            ("WhatsApp", "13.11. 18:15", "Mahotsavam im Sivan Kovil Glattbrugg", "gepostet von a.beispiel", ""),
            ("Instagram", "12.11. 22:31", "„OM“ im Kino: 12 Spielorte in Deutschland", "geplant für 7:00", "Ruhezeit (R6)"),
            ("Instagram", "12.11. 14:10", "Zürich: Restaurant AiYA bringt Küche aus dem Norden Sri Lankas", "gestoppt von a.beispiel", "in der Karenz")]
    hrows = "".join(f'<tr><td data-l="Kanal">{k}</td><td data-l="Zeit"><span class="code">{z}</span></td><td>{e(t)}</td><td data-l="Stand">{s}{f"<span class=\"unter\">{g}</span>" if g else ""}</td></tr>' for k, z, t, s, g in hist)
    wa = ("„Jailer 2“ am 15. November zum Spezialpreis im Kino Claudia in Kloten\n\n"
          "Alles zum Spezialpreis und zur Vorstellung auf tamil.de:\nhttps://tamil.de/kino/jailer-2-kloten/")
    inhalt = kopf("Social", "Regelwerk Fassung 1 vom 13.11.2026. Trockenmodus: Die Freigabe durch KBS steht aus, nichts geht an Meta hinaus.") + f"""
<div class="felder">
  <section class="feld" aria-labelledby="k-h">
    <div class="block__kopf"><h2 id="k-h">In der Karenz</h2><span class="leise">heute 2 von 6 auf Instagram</span></div>
    <div class="meldung"><p><span class="code">S-31</span> Instagram, danach Facebook. <span class="wort">Noch 6 Minuten</span>, bis <span class="code">21:46</span>; danach geplant.</p>
      <p><a href="entwurf.html">„Jailer 2“ am 15. November zum Spezialpreis im Kino Claudia in Kloten</a>, Entwurf E-5, Rubrik Kino. Regeln R1 bis R9 erfüllt.</p></div>
    <form method="post" action="social.html" class="nach-md">
      <label class="feldname" for="s-text">Text <small>änderbar bis 21:46</small></label>
      <textarea class="eingabe" id="s-text">„Jailer 2“ läuft am 15. November zum Spezialpreis im Kino Claudia in Kloten. Mehr auf tamil.de, Link in der Bio.</textarea>
      <div class="knoepfe"><button class="knopf knopf--zweit" type="submit">Text speichern</button><button class="knopf knopf--zweit" type="submit">Stoppen</button></div></form>
    <div class="block">
      <div class="block__kopf"><h2 id="h-h">Von Hand entscheiden</h2><span class="leise">eine Regel ist verletzt oder unklar</span></div>
      <table class="spec"><thead><tr><th>Code</th><th>Beitrag</th><th>Regel</th><th><span class="visually-hidden">Aktion</span></th></tr></thead><tbody>
        <tr><td data-l="Code"><span class="code">S-29</span></td><td>{e(RB[-1]['titel'])}</td><td data-l="Regel"><span class="wort-fehler">R2 heikles Thema</span><span class="unter">Justiz, geht nie automatisch</span></td>
          <td><form method="post" action="social.html" class="knoepfe ohne-rand"><button class="knopf knopf--zweit" type="submit">Trotzdem vorbereiten</button><button class="knopf knopf--leise" type="submit">Verwerfen</button></form></td></tr>
        <tr><td data-l="Code"><span class="code">S-30</span></td><td>{e(RB[12]['titel'])}</td><td data-l="Regel"><span class="wort-fehler">R4 Bild</span><span class="unter">kein Recht für soziale Netze; Vorschlag Bildkarte</span></td>
          <td><form method="post" action="social.html" class="knoepfe ohne-rand"><button class="knopf knopf--zweit" type="submit">Mit Bildkarte vorbereiten</button><button class="knopf knopf--leise" type="submit">Verwerfen</button></form></td></tr>
      </tbody></table>
    </div>
  </section>
  <aside class="feld" aria-labelledby="w-h">
    <h2 id="w-h">WhatsApp-Entwurf</h2>
    <p class="leise nach-xs">Gepostet wird von Hand im Kanal. <span class="code">S-32</span>, zu E-5; Bild: die Bildkarte „Grafik: Tamil.de“, weil der Beitrag kein Foto hat.</p>
    <div class="wa-text" id="wa-text">{e(wa)}</div>
    <p class="leise klein nach-xs">Beispieladresse; die echte steht nach der Veröffentlichung fest.</p>
    <div class="karte">
      <h3>Posten</h3>
      <div class="knoepfe"><button class="knopf" type="button" data-kopieren="wa-text">Text kopieren</button>
        <a class="knopf knopf--zweit" href="../../inhalte/logo.png" download="bildkarte-s32.png">Bildkarte herunterladen</a></div>
      <p class="grund" id="kopie-meldung" role="status">Ohne Skript: Text markieren und kopieren.</p>
      <form method="post" action="social.html"><div class="knoepfe"><button class="knopf knopf--zweit" type="submit">Als gepostet markieren</button></div></form>
      <p class="grund">Name und Zeit stehen danach im Protokoll.</p>
    </div>
  </aside>
</div>
<div class="felder felder--voll"><section class="feld" aria-labelledby="hi-h"><div class="block__kopf"><h2 id="hi-h">Historie</h2><span class="leise">alle Kanäle, neueste zuerst</span></div>
<table class="spec"><thead><tr><th>Kanal</th><th>Zeit</th><th>Beitrag</th><th>Stand</th></tr></thead><tbody>{hrows}</tbody></table></section></div>"""
    seite("social.html", "Social", "Social", inhalt)


# ------------------------------------------------------------------ Verzeichnis
def verzeichnis() -> None:
    felder = [("Name", "Düsseldorf Tamil Sangam", "Tamil Sangam Düsseldorf e. V.", True),
              ("Art", "Verein", "Verein", False),
              ("Beschreibung", "Tamilischer Kulturverein in Düsseldorf.", "Tamilischer Kulturverein in Düsseldorf mit Festen zu Deepavali und Pongal, Tanz- und Sprachkursen.", True),
              ("Adresse", "leer", "Beispielstraße 12", True),
              ("PLZ, Stadt", "40000 Düsseldorf", "40000 Düsseldorf", False),
              ("Land, Bundesland", "DE, Nordrhein-Westfalen", "DE, Nordrhein-Westfalen", False),
              ("E-Mail", "leer", "verein@example.org (öffentlich)", True),
              ("Telefon", "leer", "+49 000 0000000 (nicht öffentlich)", True)]
    rows = ""
    for i, (f, alt, neu, anders) in enumerate(felder):
        wahl = (f'<div class="zellen"><input type="radio" name="f{i}" id="f{i}a" checked><label for="f{i}a">neu</label>'
                f'<input type="radio" name="f{i}" id="f{i}b"><label for="f{i}b">bisher</label></div>') if anders else '<span class="leise">gleich</span>'
        rows += (f'<tr><td>{f}</td><td data-l="Bisher"{" class=\"leise\"" if alt == "leer" else ""}>{e(alt)}</td>'
                 f'<td data-l="Neu">{"<b>" if anders else ""}{e(neu)}{"</b>" if anders else ""}</td><td data-l="Übernehmen">{wahl}</td></tr>')
    liste = [("VE-0012", "Tamil Sangam Düsseldorf", "neu", "Hinweis", "Dublette von V-0004", "geprüft"),
             ("VE-0011", "Sivaalayam München", "Änderung", "Inhaber", "Öffnungszeiten neu", "geprüft")]
    lrows = "".join(f'<tr{" aria-current=\"true\"" if i == 0 else ""}><td data-l="Code"><span class="code">{c}</span></td><td><a href="verzeichnis.html#vorgang">{n}</a></td>'
                    f'<td data-l="Typ">{t}</td><td data-l="Berechtigung">{b}</td><td data-l="Agent">{"<span class=\"wort-fehler\">" + p + "</span>" if "Dublette" in p else p}</td><td data-l="Stand">{s}</td></tr>'
                    for i, (c, n, t, b, p, s) in enumerate(liste))
    inhalt = kopf("Verzeichnis", "Einsendungen für das Verzeichnis. Öffentlich wird nur, was freigegeben und als öffentlich markiert ist. Premium setzt nur der Administrator in WordPress.") + f"""
<div class="felder felder--voll"><section class="feld" aria-labelledby="l-h"><h2 id="l-h" class="visually-hidden">Einsendungen</h2>
<table class="spec"><thead><tr><th>Code</th><th>Name</th><th>Typ</th><th>Berechtigung</th><th>Agent</th><th>Stand</th></tr></thead><tbody>{lrows}</tbody></table></section></div>
<div class="felder felder--8-4" id="vorgang">
  <section class="feld" aria-labelledby="v-h">
    <div class="block__kopf"><h2 id="v-h">Bisher gegen neu</h2><span class="leise"><span class="code">V-0004</span> gegen <span class="code">VE-0012</span></span></div>
    <table class="spec"><thead><tr><th>Feld</th><th>Bisher (V-0004)</th><th>Neu (VE-0012)</th><th>Übernehmen</th></tr></thead><tbody>{rows}</tbody></table>
  </section>
  <aside class="feld" aria-labelledby="p-h">
    <h2 id="p-h">Prüfung</h2>
    <div class="meldung meldung--fehler nach-sm"><p><span class="wort-fehler">Dublette.</span> Eingereicht als neuer Eintrag, aber ähnlich zu <span class="code">V-0004</span> Düsseldorf Tamil Sangam: ähnlicher Name, gleiche PLZ.</p></div>
    <dl class="satz nach-md"><dt>Einsender</dt><dd>B. Beispiel, <a href="mailto:b.beispiel@example.org">b.beispiel@example.org</a></dd><dt>Berechtigung</dt><dd>Hinweis, nicht Inhaber</dd>
      <dt>Fehlt</dt><dd>nichts</dd><dt>Formfehler</dt><dd>keine</dd><dt>Kategorie</dt><dd class="leise">kein Vorschlag (Liste von KBS fehlt)</dd></dl>
    <form class="karte" method="post" action="verzeichnis.html" aria-labelledby="f-h">
      <h3 id="f-h">Freigabe</h3>
      <p class="grund">Übernommen werden die Felder, die links auf „neu“ stehen.</p>
      <div class="knoepfe"><button class="knopf" type="submit">Als Änderung an V-0004 freigeben</button><button class="knopf knopf--zweit" type="submit">Als neuen Eintrag freigeben</button><button class="knopf knopf--leise" type="submit">Ablehnen</button></div>
    </form>
  </aside>
</div>"""
    seite("verzeichnis.html", "Verzeichnis", "Verzeichnis", inhalt)


# ------------------------------------------------------------------ Buchungen
def buchungen() -> None:
    liste = [("B-0006", "Beispiel Verlag GmbH", "Leaderboard", "16.11. bis 29.11.", "reserviert", "bis 22:15 ohne Zahlung", "", "", ""),
             ("B-0005", "Muster Events GbR", "Sidebar", "23.11. bis 6.12.", "geplant", "", "", "", ""),
             ("B-0004", "Beispiel Feinkost GmbH", "In-Article", "16.11. bis 22.11.", "in Prüfung", "", "", "", "Handy-Format weicht ab"),
             ("B-0003", "Beispiel Reisen GmbH", "Leaderboard", "2.11. bis 15.11.", "läuft", "", "18 240", "212", ""),
             ("B-0002", "Muster Studio", "Billboard", "9.11. bis 15.11.", "erstattet", "abgelehnt: Werbemittel unscharf", "", "", "Erstattung fehlgeschlagen, liegt bei a.beispiel"),
             ("B-0001", "Beispiel Kino GmbH", "Footer", "19.10. bis 1.11.", "beendet", "", "9 870", "64", "")]
    rows = "".join(
        f'<tr{" aria-current=\"true\"" if c == "B-0004" else ""}><td data-l="Code"><span class="code">{c}</span></td><td><a href="buchungen.html#vorgang">{f}</a><span class="unter">{p}</span></td>'
        f'<td data-l="Zeitraum"><span class="code">{z}</span></td><td data-l="Stand">{s}{f"<span class=\"unter\">{n}</span>" if n else ""}</td>'
        f'<td class="zahl" data-l="Einblendungen"><span class="code">{ei or "0"}</span></td><td class="zahl" data-l="Klicks"><span class="code">{kl or "0"}</span></td>'
        f'<td data-l="Warnung">{f"<span class=\"wort-fehler\">{w}</span>" if w else "<span class=\"leise\">keine</span>"}</td></tr>'
        for c, f, p, z, s, n, ei, kl, w in liste)
    inhalt = kopf("Buchungen", "Werbebuchungen der Website. Aktiv ist eine Buchung nur, wenn sie bezahlt, freigegeben, nicht pausiert und im Zeitraum ist.") + f"""
<div class="felder felder--voll"><section class="feld" aria-labelledby="l-h"><h2 id="l-h" class="visually-hidden">Buchungen</h2>
<table class="spec"><thead><tr><th>Code</th><th>Firma und Platz</th><th>Zeitraum</th><th>Stand</th><th class="zahl">Einblendungen</th><th class="zahl">Klicks</th><th>Warnung</th></tr></thead><tbody>{rows}</tbody></table>
<p class="leise klein nach-xs">Einblendung: mindestens die halbe Fläche eine Sekunde sichtbar. Gezählt ohne Cookies und ohne Personendaten.</p></section></div>
<div class="felder felder--8-4" id="vorgang">
  <section class="feld" aria-labelledby="v-h">
    <div class="block__kopf"><h2 id="v-h">Werbemittel <span class="code">B-0004</span></h2><span class="leise">In-Article, nach dem zweiten Absatz</span></div>
    <div class="massreihe">
      <figure><div class="mass mass--728">feinkost-728x90.jpg</div><figcaption>Desktop: erwartet <span class="code">728 × 90</span>, geliefert <span class="code">728 × 90</span>, <span class="wort-gut">passt</span></figcaption></figure>
      <figure><div class="mass mass--300">erwartet 300 × 250</div><figcaption>Handy: erwartet <span class="code">300 × 250</span>, geliefert <span class="code">320 × 100</span>, <span class="wort-fehler">weicht ab</span></figcaption></figure>
    </div>
    <dl class="satz nach-lg"><dt>Ziel-Adresse</dt><dd><a href="https://example.org/angebot">https://example.org/angebot</a></dd>
      <dt>Firma</dt><dd>Beispiel Feinkost GmbH, Beispielweg 3, 50000 Köln</dd><dt>Ansprechperson</dt><dd>C. Beispiel, <a href="mailto:c.beispiel@example.org">c.beispiel@example.org</a></dd>
      <dt>Zeitraum</dt><dd><span class="code">16.11. bis 22.11.2026</span>, 7 Tage</dd><dt>Betrag</dt><dd class="leise">Preis folgt (legt KBS fest)</dd>
      <dt>Zahlung</dt><dd><span class="wort-gut">bezahlt</span> 13.11. 20:14, Stripe <span class="code">cs_beispiel_04</span></dd>
      <dt>Bedingungen</dt><dd>angenommen, Fassung als Platzhalter</dd></dl>
  </section>
  <aside class="feld" aria-labelledby="p-h">
    <h2 id="p-h">Prüfung</h2>
    <ul class="hinweise nach-sm"><li>Dateien: JPEG, je unter 1 MB</li><li><span class="wort-fehler">Handy-Werbemittel hat 320 × 100</span>, der Platz braucht 300 × 250</li><li>Ziel-Adresse erreichbar</li></ul>
    <form class="karte" method="post" action="buchungen.html" aria-labelledby="f-h">
      <h3 id="f-h">Entscheidung</h3>
      <div class="reihe"><label class="feldname" for="grund">Grund <small>Pflicht beim Ablehnen, geht an den Kunden</small></label><textarea class="eingabe" id="grund">Das Werbemittel für das Handy hat 320 × 100 Pixel. Der Platz braucht 300 × 250.</textarea></div>
      <div class="knoepfe"><button class="knopf" type="submit">Freigeben</button><button class="knopf knopf--zweit" type="submit">Ablehnen</button></div>
      <p class="grund">Ablehnen erstattet den vollen Betrag automatisch und gibt die Tage frei.</p>
    </form>
  </aside>
</div>"""
    seite("buchungen.html", "Buchungen", "Buchungen", inhalt)


if __name__ == "__main__":
    uebersicht(); entwurf(False); entwurf(True); eingang(); social(); verzeichnis(); buchungen()
    print("geschrieben:", ", ".join(sorted(p.name for p in HIER.glob("*.html"))))
