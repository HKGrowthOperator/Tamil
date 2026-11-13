#!/usr/bin/env python3
"""Erzeugt die Cockpit-Screens der Linie hm-eigen („Tagesblatt“) als statische Seiten.

Nur Statik: HTML und CSS, Verhalten (Kopieren) in app.js. Daten sind Beispieldaten nach
`design/linien-auftrag.md`: echte Entwurfs-Titel aus `docs/redaktion/rueckblick-2026.md`, echte Beitragstexte aus
`design/inhalte/rueckblick/rueckblick.json`; Personen, Adressen, Nummern, Firmen und Zahlen sind erfunden und als
Beispiel erkennbar (E-Mail nur @example.org).

Aufruf: python3 design/cockpit/hm-eigen/bauen.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parents[2]
RB = json.loads((ROOT / "design/inhalte/rueckblick/rueckblick.json").read_text(encoding="utf-8"))
BEITRAG = {str(b["story_id"]): b for b in RB["beitraege"]}

e = html.escape

ZIELE_ARBEIT = [
    ("uebersicht", "Übersicht", "uebersicht.html", ""),
    ("entwuerfe", "Entwürfe", "uebersicht.html#entwuerfe", "65"),
    ("eingang", "Eingang", "eingang.html", "5"),
    ("social", "Social", "social.html", "3"),
    ("verzeichnis", "Verzeichnis", "verzeichnis.html", "2"),
    ("buchungen", "Buchungen", "buchungen.html", "2"),
]
ZIELE_BETRIEB = [
    ("kosten", "Kosten", "/kosten", ""),
    ("quellen", "Quellen", "/quellen", ""),
    ("protokoll", "Protokoll", "/protokoll", ""),
    ("zeitplan", "Zeitplan", "/zeitplan", ""),
    ("schalter", "Schalter", "uebersicht.html#schalter", "2"),
    ("nutzer", "Benutzer", "/nutzer", ""),
]


def ziele(aktiv: str) -> str:
    def liste(eintraege):
        out = []
        for key, name, href, n in eintraege:
            cur = ' aria-current="page"' if key == aktiv else ""
            zahl = f'<span class="n">{n}</span>' if n else ""
            out.append(f'<li><a href="{href}"{cur}><span>{name}</span>{zahl}</a></li>')
        return '<ul class="ziele">' + "".join(out) + "</ul>"
    return f"<h2>Arbeit</h2>{liste(ZIELE_ARBEIT)}<h2>Betrieb</h2>{liste(ZIELE_BETRIEB)}"


def seite(datei: str, titel: str, beschreibung: str, aktiv: str, inhalt: str, skript: bool = False) -> None:
    js = '<script src="app.js" defer></script>' if skript else ""
    doc = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titel)}, Redaktion tamil.de</title>
<meta name="description" content="{e(beschreibung)}">
<meta name="robots" content="noindex">
<link rel="preload" href="schriften/golos-text-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="cockpit.css">
{js}
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="leiste">
  <a class="marke" href="uebersicht.html" aria-label="Redaktion tamil.de, zur Übersicht"><img src="bilder/logo.png" alt="tamil.de" width="300" height="121"><span>Redaktion</span></a>
  <p class="heute"><time datetime="2026-11-13"><span class="ziffer">13</span><span class="datum">Freitag<br>November 2026</span></time></p>
  <p class="radar"><b>Radar läuft.</b> Letzter Lauf 9:33 Uhr mit 2 neuen Meldungen, der nächste um 9:36 Uhr.</p>
  <div class="wer"><span>redaktion1</span><form action="/logout" method="post"><button type="submit" class="knopf still">Abmelden</button></form></div>
  <details class="menue"><summary>Menü</summary><nav aria-label="Cockpit, mobil">{ziele(aktiv)}</nav><form class="menue-ab" action="/logout" method="post"><p class="klein leise">Angemeldet als redaktion1</p><button type="submit" class="knopf">Abmelden</button></form></details>
</header>
<div class="banner" role="status"><p><b>Angehalten: Instagram und Facebook.</b> Grund: Das Regelwerk Social, Fassung 1, wartet auf die Freigabe durch KBS. Bearbeiten und Freigeben von Hand gehen weiter. <a href="uebersicht.html#schalter">Schalter ansehen</a></p></div>
<div class="rahmen">
<nav class="seitenleiste" aria-label="Cockpit">{ziele(aktiv)}</nav>
<main id="inhalt" class="haupt">
{inhalt}
</main>
</div>
<footer class="fussnote"><p>Probe der Linie „Tagesblatt“ mit Beispieldaten. Titel und Texte der Entwürfe sind echt; Personen, Firmen, Adressen, Nummern und Zahlen sind erfunden, E-Mail-Adressen enden auf example.org.</p></footer>
</body>
</html>
"""
    (HIER / datei).write_text(doc, encoding="utf-8")


def tag(ziffer: str, klein: str, iso: str) -> str:
    return f'<span class="tag"><time datetime="{iso}"><b>{ziffer}</b></time><small>{klein}</small></span>'


# ---------------------------------------------------------------- Übersicht
def uebersicht() -> None:
    inhalt = f"""
<header class="seitenkopf"><div><h1>Übersicht</h1><p class="unter">Was heute wartet, Stand 9:34 Uhr.</p></div>
<div class="aktionen"><a class="knopf" href="/protokoll">Protokoll von heute</a></div></header>

<dl class="stand">
  <div><dt>Entwürfe warten</dt><dd><a href="#entwuerfe">65</a></dd></div>
  <div><dt>Eingang, neu</dt><dd><a href="eingang.html">5</a></dd></div>
  <div><dt>Social, von Hand</dt><dd><a href="social.html">2</a></dd></div>
  <div><dt>Verzeichnis</dt><dd><a href="verzeichnis.html">2</a></dd></div>
  <div><dt>Werbemittel prüfen</dt><dd><a href="buchungen.html">1</a></dd></div>
</dl>

<div class="spalten">
<div>
<section class="block" id="entwuerfe" aria-labelledby="h-entw">
  <header><h2 id="h-entw">Entwürfe, die auf Freigabe warten</h2><p>3 aus dem laufenden Radar, 62 für den Rückblick. Freigeben veröffentlicht sofort.</p></header>
  <ul class="tagesliste">
    <li>{tag("15", "So, Nov.", "2026-11-15")}<div class="was"><a href="/entwurf/5">„Jailer 2“ am 15. November zum Spezialpreis im Kino Claudia in Kloten</a><p>Entwurf 5, Kino, Kloten. Der Termin ist übermorgen.</p></div><a class="knopf tun" href="/entwurf/5">Öffnen</a></li>
    <li>{tag("13", "So, Dez.", "2026-12-13")}<div class="was"><a href="/entwurf/4">THADAM 2026: Tamilische Networking- und Gala-Nacht am 13. Dezember in Bern</a><p>Entwurf 4, Events, Bern.</p></div><a class="knopf tun" href="/entwurf/4">Öffnen</a></li>
    <li><span class="tag ohne">Kino&shy;woche</span><div class="was"><a href="/entwurf/54">„OM“ im Kino: 12 Spielorte in Deutschland</a><p>Entwurf 54, Kinotermine aus den Programmen der Kinos.</p></div><a class="knopf tun" href="/entwurf/54">Öffnen</a></li>
  </ul>
  <h3 class="tage-kopf">Rückblick, neueste zuerst</h3>
  <ul class="tagesliste">
    <li>{tag("8", "So, Nov.", "2026-11-08")}<div class="was"><a href="entwurf.html">Deepavali 2026: Lichterfest in Berlin, Bayern und Düsseldorf</a><p>Entwurf 7, 485 Wörter. Vor der Freigabe: Berlin ohne Datum (nicht belegt).</p></div><a class="knopf tun" href="entwurf.html">Öffnen</a></li>
    <li>{tag("7", "Sa, Nov.", "2026-11-07")}<div class="was"><a href="/entwurf/68">Deepavali 2026: Tamilische Vereine luden in fünf Städten zum Lichterfest</a><p>Entwurf 68, 448 Wörter. Vor der Freigabe: Ankündigungen als Einladung formulieren.</p></div><a class="knopf tun" href="/entwurf/68">Öffnen</a></li>
    <li>{tag("25", "So, Okt.", "2026-10-25")}<div class="was"><a href="/entwurf/8">Karate in der Schweiz: Zweimal Bronze in Sursee, Shihan-Titel in Zürich</a><p>Entwurf 8, 400 Wörter. Vor der Freigabe: Schreibweisen der Namen prüfen.</p></div><a class="knopf tun" href="/entwurf/8">Öffnen</a></li>
  </ul>
  <p class="weiter"><a href="/?filter=rueckblick">Alle 62 Rückblick-Entwürfe</a></p>
</section>

<section class="block" aria-labelledby="h-eing">
  <header><h2 id="h-eing">Eingang</h2><a href="eingang.html">Zum Eingang</a></header>
  <ul class="tagesliste">
    <li>{tag("13", "Fr, Nov.", "2026-11-13")}<div class="was"><a href="eingang.html">Termin: Diwali in Basel</a><p>Vom Agenten vorbereitet. Hinweis: mögliche Dublette im Festkalender.</p></div><a class="knopf tun" href="eingang.html">Prüfen</a></li>
    <li>{tag("12", "Do, Nov.", "2026-11-12")}<div class="was"><a href="eingang.html?vorgang=E-0411">Termin: Laternenabend der Tamilschule Beispielstadt</a><p>Hinweis: Datum liegt in der Vergangenheit.</p></div><a class="knopf tun" href="eingang.html?vorgang=E-0411">Prüfen</a></li>
    <li>{tag("12", "Do, Nov.", "2026-11-12")}<div class="was"><a href="eingang.html?art=werbung">Werbung: Beispiel Catering GmbH</a><p>Leaderboard im Dezember. Antwort von Hand aus dem Mailprogramm.</p></div><a class="knopf tun" href="eingang.html?art=werbung">Prüfen</a></li>
  </ul>
</section>

<section class="block" aria-labelledby="h-soc">
  <header><h2 id="h-soc">Social</h2><a href="social.html">Zu Social</a></header>
  <ul class="tagesliste">
    <li>{tag("13", "Fr, Nov.", "2026-11-13")}<div class="was"><a href="social.html">Vaani Vizha: In den Tamilalayams schrieben Kinder ihren ersten Buchstaben</a><p>Karenz bis 9:41 Uhr. Instagram ist angehalten; der Beitrag bleibt danach im Trockenmodus.</p></div><a class="knopf tun" href="social.html">Ansehen</a></li>
    <li>{tag("13", "Fr, Nov.", "2026-11-13")}<div class="was"><a href="social.html#von-hand">2 Beiträge von Hand entscheiden</a><p>Regel R2 (heikles Thema) und Regel R4 (Bild ohne Recht für soziale Netze).</p></div><a class="knopf tun" href="social.html#von-hand">Entscheiden</a></li>
  </ul>
</section>

<section class="block" aria-labelledby="h-vb">
  <header><h2 id="h-vb">Verzeichnis und Buchungen</h2></header>
  <ul class="tagesliste">
    <li>{tag("12", "Do, Nov.", "2026-11-12")}<div class="was"><a href="verzeichnis.html">Verzeichnis: Restaurant Ceylon Palace, Bremen</a><p>Neuer Eintrag. Hinweis: mögliche Dublette von Eintrag V-0031.</p></div><a class="knopf tun" href="verzeichnis.html">Prüfen</a></li>
    <li>{tag("11", "Mi, Nov.", "2026-11-11")}<div class="was"><a href="buchungen.html">Werbemittel: Buchung W-2026-0007, Billboard</a><p>Bezahlt, wartet auf die Prüfung. Start am 16. November.</p></div><a class="knopf tun" href="buchungen.html">Prüfen</a></li>
    <li>{tag("10", "Di, Nov.", "2026-11-10")}<div class="was"><a href="buchungen.html?buchung=W-2026-0005">Erstattung fehlgeschlagen: W-2026-0005</a><p class="warnung-text">Geht an einen Menschen. Stripe meldet einen Fehler bei der Rückzahlung.</p></div><a class="knopf tun" href="buchungen.html?buchung=W-2026-0005">Ansehen</a></li>
  </ul>
</section>
</div>

<aside aria-label="Betrieb">
<section class="seite-teil" id="schalter" aria-labelledby="h-sch">
  <h2 id="h-sch">Stopp-Schalter</h2>
  <table class="tabelle">
    <thead><tr><th>Kanal</th><th>Stand</th></tr></thead>
    <tbody>
      <tr><td>Alles</td><td><span class="st ok">läuft</span></td></tr>
      <tr><td>Redaktion</td><td><span class="st ok">läuft</span></td></tr>
      <tr><td>Website</td><td><span class="st ok">läuft</span></td></tr>
      <tr><td>Eingang</td><td><span class="st ok">läuft</span></td></tr>
      <tr><td>Verzeichnis</td><td><span class="st ok">läuft</span></td></tr>
      <tr><td>Instagram</td><td><span class="st halt">angehalten</span><br><span class="klein leise">seit 13.11., 8:02 Uhr, redaktion1</span></td></tr>
      <tr><td>Facebook</td><td><span class="st halt">angehalten</span><br><span class="klein leise">seit 13.11., 8:02 Uhr, redaktion1</span></td></tr>
      <tr><td>WhatsApp</td><td><span class="st ok">läuft</span></td></tr>
    </tbody>
  </table>
  <form class="anhalten" action="/schalter/alles/an" method="post">
    <label class="feld"><span>Alles anhalten, Grund (Pflicht)</span><input name="grund" required maxlength="300" autocomplete="off" placeholder="zum Beispiel: Kosten prüfen"><small>Es beginnt nichts Neues. Wieder einschalten darf nur die Rolle admin.</small></label>
    <button type="submit" class="knopf gefahr">Alles anhalten</button>
  </form>
</section>

<section class="seite-teil" aria-labelledby="h-bud">
  <h2 id="h-bud">Budget</h2>
  <dl class="daten">
    <dt>Heute</dt><dd class="zahl">$1.38 von $5.00</dd>
    <dt>November</dt><dd class="zahl">$41.70 von $150.00</dd>
  </dl>
  <div class="balken" role="img" aria-label="Monatsbudget zu 28 Prozent verbraucht"><i class="w28"></i></div>
  <p class="klein leise">Ab 80 Prozent erscheint eine Warnung, bei 100 Prozent warten neue bezahlte Schritte. <a href="/kosten">Kosten ansehen</a></p>
</section>

<section class="seite-teil" aria-labelledby="h-lauf">
  <h2 id="h-lauf">Radar</h2>
  <dl class="daten">
    <dt>Letzter Lauf</dt><dd>9:33 Uhr, 41 Quellen, 2 neue Meldungen</dd>
    <dt>Nächster Lauf</dt><dd>9:36 Uhr</dd>
    <dt>Quellen mit Fehler</dt><dd>1 (<a href="/quellen">ansehen</a>)</dd>
  </dl>
</section>
</aside>
</div>
"""
    seite("uebersicht.html", "Übersicht", "Stand der Redaktion: wartende Entwürfe, Eingang, Social, Budget und Stopp-Schalter.", "uebersicht", inhalt)


# ---------------------------------------------------------------- Entwurf
QUELLEN = [
    ("Q1", "Sivaalayam München, Ankündigung der Deepavali-Feier", "Veranstalter, Primärquelle, Volltext, Rechte: Zitat"),
    ("Q2", "Sri Ganesha Hindu Temple Berlin, Festkalender 2026", "Veranstalter, Volltext, Rechte: Zitat"),
    ("Q3", "Düsseldorf Tamil Sangam, Einladung zur Deepavali-Feier", "Veranstalter, Primärquelle, Volltext, Rechte: Zitat"),
]
BELEGE = [
    [("C1", "ok", "bestätigt", "Deepavali fiel 2026 auf Sonntag, 8. November.", "Q1"),
     ("C2", "ok", "bestätigt", "Sivaalayam München kündigte Feierlichkeiten für den Tag an.", "Q1"),
     ("C3", "halt", "offen", "Berliner Tempel: Lakshmi Pooja im Kalender, ein Datum fehlt in Q2.", "Q2"),
     ("C4", "ok", "bestätigt", "Düsseldorf Tamil Sangam lädt am Sonntag, 15. November, ein.", "Q3")],
    [("C5", "wartet", "Hintergrund", "Name aus dem Sanskrit, ungefähr „Reihe von Lichtern“.", "Q1")],
    [("C6", "wartet", "Hintergrund", "Termin nach dem Mondkalender, meist Neumond im Oktober oder November.", "Q1")],
    [("C7", "wartet", "Hintergrund", "Bräuche: Diyas, Lichterketten, Rangoli, Tempelbesuch.", "Q1")],
]


def entwurf(lizenz_fehlt: bool) -> None:
    b = BEITRAG["30"]
    absaetze = []
    for i, text in enumerate(b["absaetze"]):
        li = "".join(
            f'<li><span class="id">{cid}</span><span><span class="st {kl}">{wort}</span>, {e(aussage)} Quelle {q}.</span></li>'
            for cid, kl, wort, aussage, q in BELEGE[i]
        )
        absaetze.append(f'<div class="absatz"><p>{e(text)}</p><ul class="belege" aria-label="Belege zu Absatz {i + 1}">{li}</ul></div>')
    quellen = "".join(f"<li><b>{k}</b> {e(n)}<br><span class=\"klein leise\">{e(m)}</span></li>" for k, n, m in QUELLEN)

    if lizenz_fehlt:
        meldung = """<div class="meldung" role="status"><h2>Bild ohne Lizenz-Datensatz</h2><p>Der Abruf bei Wikimedia Commons ist um 17:41 Uhr fehlgeschlagen (Zeitüberschreitung). Ohne Datensatz geht kein Bild nach WordPress. Lizenz eintragen, erneut abrufen oder die Bildkarte nehmen; erst dann lässt sich freigeben.</p></div>"""
        freigabe_knopf = '<button type="submit" class="knopf" disabled aria-describedby="frei-grund">Freigeben</button><p class="klein leise" id="frei-grund">Freigeben geht erst mit Lizenz-Datensatz.</p>'
        bild = f"""<section class="seite-teil" aria-labelledby="h-bild">
  <h2 id="h-bild">Bild</h2>
  <figure class="bild"><img src="bilder/rb-30.jpg" alt="{e(b['alt'])}" width="1280" height="960"><figcaption>Datei sri-ganesha-hindutempel-berlin.jpg, Herkunft Wikimedia Commons. Nachweis fehlt.</figcaption></figure>
  <dl class="daten klein">
    <dt>Rechteinhaber</dt><dd class="fehlt">fehlt</dd>
    <dt>Lizenz</dt><dd class="fehlt">fehlt</dd>
    <dt>Quelle</dt><dd><a href="{e(b['quelle_bild'])}">bei Commons</a></dd>
  </dl>
</section>
<section class="seite-teil" aria-labelledby="h-liz">
  <h2 id="h-liz">Lizenz eintragen</h2>
  <form action="/entwurf/7/lizenz" method="post">
    <label class="feld"><span>Herkunft</span><select name="herkunft" autocomplete="off"><option value="commons" selected>Wikimedia Commons</option><option value="quelle">Bildquelle aus dem Register</option><option value="archiv">Archiv</option><option value="upload">eigenes Bild (Upload)</option><option value="stock">Stockfoto</option><option value="pool">Bildpool</option><option value="ki">KI-Bild</option><option value="karte">Bildkarte</option></select></label>
    <label class="feld"><span>Rechteinhaber (Pflicht)</span><input name="rechteinhaber" required autocomplete="off" aria-invalid="true" aria-describedby="f-rechte"><small class="fehler" id="f-rechte">Bitte eintragen, wie auf der Seite der Quelle angegeben.</small></label>
    <label class="feld"><span>Lizenz (Pflicht)</span><select name="lizenz" required aria-invalid="true" aria-describedby="f-lizenz"><option value="">Bitte wählen</option><option>gemeinfrei oder CC0</option><option>CC BY</option><option>CC BY-SA</option><option>Plattformlizenz</option><option>eigene Vereinbarung</option></select><small id="f-lizenz">NC und ND sind nicht erlaubt.</small></label>
    <div class="zwei">
      <label class="feld"><span>Version</span><input name="version" autocomplete="off" placeholder="zum Beispiel 4.0"><small></small></label>
      <label class="feld"><span>Läuft ab am</span><input name="ablauf" type="date" autocomplete="off"><small>leer, wenn unbefristet</small></label>
    </div>
    <label class="feld"><span>Lizenz-Adresse</span><input name="lizenz_url" type="url" inputmode="url" autocomplete="off" placeholder="https://creativecommons.org/licenses/by-sa/4.0/"><small></small></label>
    <label class="feld"><span>Umfang</span><input name="umfang" value="Online-Veröffentlichung auf tamil.de" autocomplete="off"><small></small></label>
    <fieldset class="feld"><legend>Auch in sozialen Netzen nutzen?</legend><div class="wahl"><label><input type="radio" name="social" value="ja"><span>ja</span></label><label><input type="radio" name="social" value="nein" checked><span>nein, dann Bildkarte</span></label></div><small>Regel R4 im Regelwerk Social.</small></fieldset>
    <label class="feld"><span>Bildnachweis (Pflicht)</span><input name="attribution" required autocomplete="off" placeholder="Foto: Name / Wikimedia Commons, Lizenz"><small>Steht unter dem Bild auf tamil.de.</small></label>
    <div class="wahl"><label><input type="checkbox" name="ki" value="1"><span>Das Bild ist KI-generiert</span></label></div>
    <div class="aktionen formende"><button type="submit" class="knopf primaer">Lizenz speichern</button><button type="submit" class="knopf" formaction="/entwurf/7/lizenz/abrufen">Bei Commons erneut abrufen</button><button type="submit" class="knopf" formaction="/entwurf/7/bild/karte" formnovalidate>Bildkarte nehmen</button></div>
  </form>
</section>"""
        datei, titel = "entwurf-lizenz-fehlt.html", "Entwurf 7, Lizenz fehlt"
        zustand = '<p class="st halt">Bild ohne Lizenz</p>'
    else:
        meldung = ""
        freigabe_knopf = '<button type="submit" class="knopf primaer">Freigeben und veröffentlichen</button>'
        bild = f"""<section class="seite-teil" aria-labelledby="h-bild">
  <h2 id="h-bild">Bild</h2>
  <figure class="bild"><img src="bilder/rb-30.jpg" alt="{e(b['alt'])}" width="1280" height="960"><figcaption>{e(b['nachweis'])}</figcaption></figure>
  <dl class="daten klein">
    <dt>Herkunft</dt><dd>Wikimedia Commons</dd>
    <dt>Rechteinhaber</dt><dd>18quirl08</dd>
    <dt>Lizenz</dt><dd><a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="license">CC BY-SA 4.0</a></dd>
    <dt>Umfang</dt><dd>Online-Veröffentlichung auf tamil.de</dd>
    <dt>Soziale Netze</dt><dd>nein, dort die Bildkarte</dd>
    <dt>KI-Bild</dt><dd>nein</dd>
    <dt>Quelle</dt><dd><a href="{e(b['quelle_bild'])}">bei Commons</a></dd>
  </dl>
  <p class="klein leise">Dasselbe Tempelbild steht schon an Story 49. <a href="entwurf-lizenz-fehlt.html">Zustand „Lizenz fehlt“ ansehen</a></p>
</section>"""
        datei, titel = "entwurf.html", "Entwurf 7"
        zustand = '<p class="st neu">neu, Stand 3</p>'

    inhalt = f"""
<a class="zurueck" href="uebersicht.html#entwuerfe">Zurück zu den Entwürfen</a>
<header class="seitenkopf"><div><h1>Entwurf 7</h1><p class="unter">Story 30, Rubrik Events. Nachtrag für den Rückblick, erscheint mit dem Datum 8. November 2026.</p></div>{zustand}</header>
{meldung}
<div class="spalten">
<div>
<article class="beitrag" aria-labelledby="t-beitrag">
  <h2 class="titel" id="t-beitrag">{e(b['titel'])}</h2>
  <p class="teaser">{e(b['teaser'])}</p>
  {''.join(absaetze)}
</article>

<section class="block quellen" aria-labelledby="h-q">
  <header><h2 id="h-q">Quellen</h2><p>Faktencheck: 4 Sätze gedeckt, 1 offen (C3), 3 Hintergrund.</p></header>
  <ol class="hinweise">{quellen}</ol>
</section>

<details class="aufklapp">
  <summary>Text bearbeiten</summary>
  <form action="/entwurf/7" method="post">
    <input type="hidden" name="stand" value="3">
    <label class="feld"><span>Überschrift</span><input name="titel" value="{e(b['titel'])}" maxlength="120" required autocomplete="off"><small>höchstens 90 Zeichen, jetzt 60</small></label>
    <label class="feld"><span>Vorspann</span><textarea name="teaser" rows="3" maxlength="300">{e(b['teaser'])}</textarea><small>höchstens 220 Zeichen</small></label>
    <div class="zwei">
      <label class="feld"><span>Rubrik</span><select name="kategorie"><option>Nachrichten</option><option selected>Events</option><option>Kino</option><option>Community</option><option>Kultur</option><option>Küche</option><option>Sport</option></select><small></small></label>
      <label class="feld"><span>Schlagworte, mit Komma</span><input name="schlagworte" value="Deepavali, Berlin, München, Düsseldorf" autocomplete="off"><small></small></label>
    </div>
    <label class="feld"><span>Haupttext</span><textarea name="inhalt_html" rows="10">{e(''.join('<p>' + t + '</p>' for t in b['absaetze']))}</textarea><small>Erlaubt sind Absätze, Zwischentitel und Fettung; Links nur auf Quellen der Story.</small></label>
    <div class="zwei">
      <label class="feld"><span>SEO-Titel</span><input name="seo_titel" value="Deepavali 2026 in Berlin, Bayern und Düsseldorf" maxlength="70" autocomplete="off"><small></small></label>
      <label class="feld"><span>Alt-Text des Bildes</span><input name="bild_alt" value="{e(b['alt'])}" maxlength="125" autocomplete="off"><small></small></label>
    </div>
    <button type="submit" class="knopf">Speichern</button>
  </form>
</details>
<details class="aufklapp">
  <summary>Fassungen und Aktionen</summary>
  <table class="tabelle stapel">
    <thead><tr><th>Zeit</th><th>Rolle</th><th>von</th><th>Hash</th></tr></thead>
    <tbody>
      <tr><td class="kopf">12.11., 17:31 Uhr</td><td data-l="Rolle">Text</td><td data-l="von">Agent Redakteur</td><td data-l="Hash"><code>3f9a0c</code></td></tr>
      <tr><td class="kopf">12.11., 17:36 Uhr</td><td data-l="Rolle">Faktencheck</td><td data-l="von">Agent Prüfer</td><td data-l="Hash"><code>3f9a0c</code></td></tr>
      <tr><td class="kopf">12.11., 17:40 Uhr</td><td data-l="Rolle">Entwurf</td><td data-l="von">Radar</td><td data-l="Hash"><code>b71e42</code></td></tr>
    </tbody>
  </table>
</details>
</div>

<aside aria-label="Freigabe und Bild">
<section class="freigabe" aria-labelledby="h-frei">
  <h2 id="h-frei">Freigabe</h2>
  <dl class="daten">
    <dt>Stand</dt><dd>3, angelegt vom Radar am 12.11., 17:40 Uhr</dd>
    <dt>Kosten</dt><dd class="zahl">$0.41 für diese Story</dd>
  </dl>
  <h3>Vor der Freigabe</h3>
  <ul class="hinweise">
    <li class="offen"><b>Offen:</b> Berlin ohne Datum, nicht belegt (C3).</li>
    <li><b>Prüfen:</b> Düsseldorf am 15. November ist als Einladung formuliert.</li>
    <li><b>Prüfen:</b> Dasselbe Tempelbild wie bei Story 49.</li>
  </ul>
  <form action="/entwurf/7/status" method="post">
    <input type="hidden" name="stand" value="3">
    <div class="aktionen">{freigabe_knopf}</div>
    <div class="aktionen"><button type="submit" class="knopf" name="aktion" value="zurueckstellen">Zurückstellen</button><button type="submit" class="knopf gefahr" name="aktion" value="ablehnen">Ablehnen</button><a class="knopf still" href="/vorschau/7">Vorschau</a></div>
  </form>
</section>
{bild}
</aside>
</div>
"""
    seite(datei, titel, "Entwurf mit Text, Belegen je Absatz, Bild mit Lizenz-Datensatz und Freigabe.", "entwuerfe", inhalt)


# ---------------------------------------------------------------- Eingang
def eingang() -> None:
    zeilen = [
        ("E-0412", "Termin", "Diwali in Basel", "13.11., 7:58 Uhr", "vorbereitet", "wartet", "mögliche Dublette", True),
        ("E-0411", "Termin", "Laternenabend der Tamilschule Beispielstadt", "12.11., 21:40 Uhr", "vorbereitet", "wartet", "Datum in der Vergangenheit", False),
        ("E-0410", "Beitrag", "Neue Räume für die Tamilschule Beispielstadt", "12.11., 18:05 Uhr", "vorbereitet", "wartet", "", False),
        ("E-0409", "Werbung", "Beispiel Catering GmbH, Leaderboard im Dezember", "12.11., 10:22 Uhr", "vorbereitet", "wartet", "", False),
        ("E-0408", "Kontakt", "Frage zum Kinoprogramm in Wien", "11.11., 16:30 Uhr", "vorbereitet", "wartet", "", False),
        ("E-0405", "Termin", "Pongal-Treffen in Chennai", "10.11., 12:14 Uhr", "abgelehnt", "halt", "Ort außerhalb von DE, AT, CH", False),
    ]
    rows = []
    for nr, art, betreff, zeit, st, kl, hinweis, aktiv in zeilen:
        cur = ' aria-current="true"' if aktiv else ""
        h = f'<span class="warnung">{hinweis}</span>' if hinweis else '<span class="leise">keine</span>'
        rows.append(f'<tr{cur}><td class="kopf"><a href="eingang.html?vorgang={nr}">{art}: {e(betreff)}</a></td><td data-l="Vorgang" class="zahl nw">{nr}</td><td data-l="Eingang" class="nw">{zeit}</td><td data-l="Stand"><span class="st {kl}">{st}</span></td><td data-l="Hinweise">{h}</td></tr>')
    inhalt = f"""
<header class="seitenkopf"><div><h1>Eingang</h1><p class="unter">Einsendungen von tamil.de. Der Agent prüft und bereitet vor; entscheiden und antworten tut die Redaktion.</p></div></header>
<ul class="reiter" aria-label="Nach Art filtern">
  <li><a href="eingang.html" aria-current="page">Alle <span class="n">5</span></a></li>
  <li><a href="eingang.html?art=termin">Termin <span class="n">2</span></a></li>
  <li><a href="eingang.html?art=beitrag">Beitrag <span class="n">1</span></a></li>
  <li><a href="eingang.html?art=kooperation">Kooperation <span class="n">0</span></a></li>
  <li><a href="eingang.html?art=werbung">Werbung <span class="n">1</span></a></li>
  <li><a href="eingang.html?art=kontakt">Kontakt <span class="n">1</span></a></li>
  <li><a href="eingang.html?stand=erledigt">Erledigt und abgelehnt</a></li>
</ul>
<table class="tabelle stapel liste-eingang">
  <thead><tr><th>Einsendung</th><th>Vorgang</th><th>Eingang</th><th>Stand</th><th>Hinweise des Agenten</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>

<section class="vorgang" aria-labelledby="h-vorgang">
<header class="seitenkopf unterkopf"><div><h2 id="h-vorgang">Termin: Diwali in Basel</h2><p class="unter">Vorgang E-0412, eingegangen am 13. November um 7:58 Uhr, abgeholt um 8:00 Uhr.</p></div><p class="st wartet">vorbereitet</p></header>
<div class="spalten">
<div>
  <section class="seite-teil" aria-labelledby="h-angaben">
    <h3 id="h-angaben" class="teil-kopf">Angaben des Einsenders</h3>
    <dl class="daten">
      <dt>Titel</dt><dd>Diwali in Basel</dd>
      <dt>Datum und Uhrzeit</dt><dd>Samstag, 21. November 2026, 18 Uhr</dd>
      <dt>Ende</dt><dd>23 Uhr</dd>
      <dt>Ort mit Adresse</dt><dd>Aula Lysbüchel, Beispielstraße 1</dd>
      <dt>Stadt und Land</dt><dd>Basel, CH</dd>
      <dt>Veranstalter</dt><dd>Basel Tamil Sangam</dd>
      <dt>Beschreibung</dt><dd>Diwali-Abend mit Tanz, Musik und Essen für Familien. Eintritt frei, Spenden willkommen.</dd>
      <dt>Eintritt</dt><dd>frei</dd>
      <dt>Ticket-Link</dt><dd class="leise">keiner</dd>
      <dt>Bild</dt><dd>keins</dd>
      <dt>Einsender</dt><dd>A. Beispiel, <a href="mailto:termine@example.org?subject=Ihre%20Einsendung%20E-0412">termine@example.org</a></dd>
      <dt>Einwilligung</dt><dd>ja, Fassung vom 1. November 2026</dd>
    </dl>
  </section>
  <section class="seite-teil" aria-labelledby="h-entw-e">
    <h3 id="h-entw-e" class="teil-kopf">Entwurf aus der Einsendung</h3>
    <p class="klein leise">Vermerk: Angaben des Einsenders, ungeprüft. Der Agent ergänzt nichts, was nicht in der Einsendung steht.</p>
    <p class="entwurf-titel"><b>Diwali in Basel mit dem Basel Tamil Sangam</b></p>
    <p>Der Basel Tamil Sangam lädt am Samstag, 21. November 2026, ab 18 Uhr in die Aula Lysbüchel in Basel ein. Auf dem Programm stehen Tanz, Musik und Essen für Familien. Der Eintritt ist frei.</p>
  </section>
</div>
<aside aria-label="Prüfung und Entscheidung">
  <section class="freigabe" aria-labelledby="h-pruef">
    <h3 id="h-pruef">Prüfung des Agenten</h3>
    <ul class="hinweise">
      <li><b>Pflichtfelder:</b> vollständig.</li>
      <li><b>Datum:</b> in der Zukunft, ein Samstag.</li>
      <li><b>Ort:</b> in der Schweiz.</li>
      <li class="offen"><b>Mögliche Dublette:</b> „Diwali in Basel mit dem Basel Tamil Sangam“ steht schon im Festkalender (21. November, Aula Lysbüchel). <a href="/entwurf/41">Vorhandenen Termin ansehen</a></li>
    </ul>
    <p class="klein">Zusammenfassung: Gleicher Termin wie im Kalender, neu sind Uhrzeit, Ende und Eintritt.</p>
    <form action="/eingang/E-0412" method="post">
      <label class="feld"><span>Notiz</span><textarea name="notiz" rows="2">Uhrzeit und Eintritt in den vorhandenen Termin übernehmen.</textarea><small></small></label>
      <div class="aktionen"><button type="submit" class="knopf primaer" name="aktion" value="uebernehmen">Übernehmen</button><button type="submit" class="knopf" name="aktion" value="erledigt">Erledigt</button></div>
      <div class="aktionen zweite"><button type="submit" class="knopf gefahr" name="aktion" value="ablehnen">Ablehnen</button><button type="submit" class="knopf gefahr" name="aktion" value="spam">Spam</button></div>
    </form>
    <p class="klein leise">Antwort nur von Hand: <a href="mailto:termine@example.org?subject=Ihre%20Einsendung%20E-0412">im Mailprogramm öffnen</a>. Das Cockpit verschickt keine E-Mail.</p>
  </section>
</aside>
</div>
</section>

<section class="block" aria-labelledby="h-leer">
  <header><h2 id="h-leer">Kooperation</h2></header>
  <div class="leer"><p>Keine offenen Anfragen zur Kooperation.</p><p class="klein">Anfragen kommen über das Formular „Kooperation“ auf tamil.de und erscheinen hier nach dem nächsten Abholen.</p></div>
</section>
"""
    seite("eingang.html", "Eingang", "Einsendungen mit Prüfung des Agenten, Entwurf und Entscheidung.", "eingang", inhalt)


# ---------------------------------------------------------------- Social
def social() -> None:
    b = BEITRAG["33"]
    wa = (f"{b['titel']}\n\n{b['teaser']}\n\nhttps://tamil.de/kultur/vaani-vizha-tamilalayams/")
    inhalt = f"""
<header class="seitenkopf"><div><h1>Social</h1><p class="unter">Regelwerk Fassung 1 vom 13. November 2026. Die Freigabe durch KBS steht aus, bis dahin Trockenmodus: Es geht nichts an Meta hinaus.</p></div>
<div class="aktionen"><a class="knopf" href="/regeln/social">Regelwerk lesen</a></div></header>

<section class="block" aria-labelledby="h-karenz">
  <header><h2 id="h-karenz">In der Karenz</h2><p>10 Minuten ändern oder stoppen</p></header>
  <div class="karenz">
    <div>
      <p class="klein leise">Instagram, danach Facebook. Veröffentlicht auf tamil.de um 9:31 Uhr.</p>
      <h3 class="karenz-titel">{e(b['titel'])}</h3>
      <form action="/social/118" method="post">
        <label class="feld"><span>Text für Instagram und Facebook</span><textarea name="text" rows="5">{e(b['teaser'])} Mehr auf tamil.de, Link in der Bio.</textarea><small>Hashtags je Rubrik liefert KBS; bis dahin keine.</small></label>
        <div class="aktionen"><button type="submit" class="knopf">Text speichern</button><button type="submit" class="knopf gefahr" formaction="/social/118/stoppen">Stoppen</button></div>
      </form>
    </div>
    <div>
      <p class="uhr" aria-label="noch sieben Minuten">7 Min.</p>
      <p>Karenz bis 9:41 Uhr.</p>
      <p class="klein"><span class="st halt">Instagram angehalten.</span> Nach der Karenz bleibt der Beitrag im Trockenmodus stehen; die Historie nennt den Grund.</p>
      <ul class="hinweise klein">
        <li><b>R1 bis R9:</b> alle erfüllt.</li>
        <li><b>Bild:</b> Bildkarte „Grafik: Tamil.de“, weil das Recht für soziale Netze nicht eingetragen ist.</li>
      </ul>
    </div>
  </div>
</section>

<section class="block" id="von-hand" aria-labelledby="h-hand">
  <header><h2 id="h-hand">Von Hand entscheiden</h2><p>Eine Regel ist verletzt oder unklar</p></header>
  <table class="tabelle stapel">
    <thead><tr><th>Beitrag</th><th>Kanal</th><th>Grund</th><th class="r">Entscheidung</th></tr></thead>
    <tbody>
      <tr><td class="kopf">Bundestagsdrucksache: 14 Abschiebungen nach Sri Lanka im ersten Halbjahr 2026</td><td data-l="Kanal">Instagram, Facebook</td><td data-l="Grund">R2: heikles Thema (Politik). Geht nie automatisch.</td><td data-l="Entscheidung" class="r tun"><form class="aktionen" action="/social/116" method="post"><button type="submit" class="knopf" name="aktion" value="freigeben">Trotzdem vorbereiten</button><button type="submit" class="knopf gefahr" name="aktion" value="verwerfen">Verwerfen</button></form></td></tr>
      <tr><td class="kopf">Erstmals in Deutschland angekündigt: Yuvan Shankar Raja in der Grugahalle Essen</td><td data-l="Kanal">Instagram, Facebook</td><td data-l="Grund">R4: Bild ohne Recht für soziale Netze.</td><td data-l="Entscheidung" class="r tun"><form class="aktionen" action="/social/117" method="post"><button type="submit" class="knopf" name="aktion" value="karte">Mit Bildkarte vorbereiten</button><button type="submit" class="knopf gefahr" name="aktion" value="verwerfen">Verwerfen</button></form></td></tr>
    </tbody>
  </table>
</section>

<section class="block" aria-labelledby="h-wa">
  <header><h2 id="h-wa">WhatsApp-Entwurf</h2><p>Gepostet wird von Hand im Kanal von tamil.de</p></header>
  <div class="karenz">
    <div>
      <pre class="wa-text" id="wa-text">{e(wa)}</pre>
      <div class="aktionen wa-aktionen"><button type="button" class="knopf" data-kopieren="wa-text">Text kopieren</button><a class="knopf" href="bilder/rb-33.jpg" download="vaani-vizha-tamil-de.jpg">Bild herunterladen</a></div>
      <p class="klein leise" id="wa-meldung" role="status"></p>
    </div>
    <div>
      <div class="social-bild"><img src="bilder/rb-33.jpg" alt="{e(b['alt'])}" width="1280" height="1707"><p class="klein">{e(b['nachweis'])}. Der Nachweis steht im Text des Beitrags auf tamil.de.</p></div>
      <form action="/social/119/gepostet" method="post" class="gepostet">
        <button type="submit" class="knopf primaer">Als gepostet markieren</button>
        <p class="klein leise">Person und Zeit kommen ins Protokoll.</p>
      </form>
    </div>
  </div>
</section>

<section class="block" aria-labelledby="h-hist">
  <header><h2 id="h-hist">Historie</h2></header>
  <ul class="reiter" aria-label="Kanal wählen">
    <li><a href="social.html" aria-current="page">Instagram <span class="n">4</span></a></li>
    <li><a href="social.html?kanal=facebook">Facebook <span class="n">4</span></a></li>
    <li><a href="social.html?kanal=whatsapp">WhatsApp <span class="n">3</span></a></li>
  </ul>
  <table class="tabelle stapel">
    <thead><tr><th>Beitrag</th><th>Stand</th><th>Zeit</th><th>Regelwerk</th><th>Bei Instagram</th></tr></thead>
    <tbody>
      <tr><td class="kopf">Vaani Vizha: In den Tamilalayams schrieben Kinder ihren ersten Buchstaben</td><td data-l="Stand"><span class="st wartet">Karenz</span></td><td data-l="Zeit" class="nw">13.11., 9:31 Uhr</td><td data-l="Regelwerk" class="nw">Fassung 1</td><td data-l="Bei Instagram" class="leise">noch nicht</td></tr>
      <tr><td class="kopf">Bundestagsdrucksache: 14 Abschiebungen nach Sri Lanka im ersten Halbjahr 2026</td><td data-l="Stand"><span class="st wartet">von Hand</span></td><td data-l="Zeit" class="nw">13.11., 9:05 Uhr</td><td data-l="Regelwerk" class="nw">Fassung 1</td><td data-l="Bei Instagram" class="leise">noch nicht</td></tr>
      <tr><td class="kopf">Sri Lanka erlässt Reisenden aus Deutschland, Österreich und der Schweiz die Visagebühr</td><td data-l="Stand"><span class="st halt">angehalten</span></td><td data-l="Zeit" class="nw">13.11., 8:40 Uhr</td><td data-l="Regelwerk" class="nw">Fassung 1</td><td data-l="Bei Instagram">Trockenmodus: Kanal angehalten</td></tr>
      <tr><td class="kopf">Berlin: Sri Ganesha Hindu Temple an der Hasenheide geweiht</td><td data-l="Stand"><span class="st">gestoppt</span></td><td data-l="Zeit" class="nw">12.11., 19:12 Uhr</td><td data-l="Regelwerk" class="nw">Fassung 1</td><td data-l="Bei Instagram">in der Karenz gestoppt von redaktion1</td></tr>
    </tbody>
  </table>
</section>
"""
    seite("social.html", "Social", "Social-Historie je Kanal, Karenz, Entscheidungen von Hand und WhatsApp-Entwurf.", "social", inhalt, skript=True)


# ---------------------------------------------------------------- Verzeichnis
def verzeichnis() -> None:
    felder = [
        ("Name", "Ceylon Palace", "Restaurant Ceylon Palace", "neu"),
        ("Art", "Business", "Business", "gleich"),
        ("Kategorie", "Restaurant", "Restaurant (Vorschlag des Agenten)", "gleich"),
        ("Adresse", "Beispielweg 4", "Beispielweg 4", "gleich"),
        ("PLZ und Stadt", "28000 Bremen", "28000 Bremen", "gleich"),
        ("Telefon", "+49 000 1112223", "+49 000 1112245", "neu"),
        ("Website", "keine", "ceylon-palace.example.org", "neu"),
        ("Öffnungszeiten", "Di bis So, 12 bis 22 Uhr", "täglich 11:30 bis 22 Uhr", "neu"),
        ("Beschreibung", "Küche aus Sri Lanka in Bremen.", "Kottu, Parotta, Dosa und Devil-Gerichte aus Sri Lanka, von Vater und Sohn gekocht.", "neu"),
    ]
    rows = []
    for i, (feld, alt, neu, art) in enumerate(felder):
        if art == "gleich":
            wahl = '<span class="leise">unverändert</span>'
            rows.append(f'<tr><td class="kopf">{feld}</td><td data-l="Bisher (V-0031)" class="alt">{e(alt)}</td><td data-l="Einsendung" class="neu gleich">{e(neu)}</td><td data-l="Entscheidung">{wahl}</td></tr>')
        else:
            wahl = (f'<fieldset class="wahl"><legend class="visually-hidden">{feld}</legend>'
                    f'<label><input type="radio" name="f{i}" value="neu" checked><span>neu</span></label>'
                    f'<label><input type="radio" name="f{i}" value="alt"><span>bisher</span></label></fieldset>')
            rows.append(f'<tr><td class="kopf">{feld}</td><td data-l="Bisher (V-0031)" class="alt">{e(alt)}</td><td data-l="Einsendung" class="neu">{e(neu)}</td><td data-l="Entscheidung">{wahl}</td></tr>')
    inhalt = f"""
<header class="seitenkopf"><div><h1>Verzeichnis</h1><p class="unter">Einsendungen für das Verzeichnis. Öffentlich wird nur, was freigegeben ist; Premium setzt allein der Administrator in WordPress.</p></div></header>
<ul class="reiter" aria-label="Nach Stand filtern">
  <li><a href="verzeichnis.html" aria-current="page">Offen <span class="n">2</span></a></li>
  <li><a href="verzeichnis.html?stand=freigegeben">Freigegeben</a></li>
  <li><a href="verzeichnis.html?stand=abgelehnt">Abgelehnt</a></li>
</ul>
<table class="tabelle stapel">
  <thead><tr><th>Einsendung</th><th>Typ</th><th>Art und Ort</th><th>Eingang</th><th>Hinweise</th></tr></thead>
  <tbody>
    <tr aria-current="true"><td class="kopf"><a href="verzeichnis.html?vorgang=VE-0019">Restaurant Ceylon Palace</a></td><td data-l="Typ">neu</td><td data-l="Art und Ort">Business, Bremen</td><td data-l="Eingang" class="nw">12.11., 14:02 Uhr</td><td data-l="Hinweise"><span class="warnung">mögliche Dublette von V-0031</span></td></tr>
    <tr><td class="kopf"><a href="verzeichnis.html?vorgang=VE-0018">Sri Kamadchi Ampal Tempel</a></td><td data-l="Typ">Änderung</td><td data-l="Art und Ort">Tempel, Hamm</td><td data-l="Eingang" class="nw">11.11., 9:47 Uhr</td><td data-l="Hinweise">Telefon geändert</td></tr>
  </tbody>
</table>

<section class="vorgang" aria-labelledby="h-ve">
<header class="seitenkopf unterkopf"><div><h2 id="h-ve">Restaurant Ceylon Palace, Bremen</h2><p class="unter">Einsendung VE-0019 vom 12. November, Typ neu. Eingereicht als Inhaber von B. Beispiel, <a href="mailto:inhaber@example.org">inhaber@example.org</a> (intern, nie öffentlich).</p></div><p class="st wartet">geprüft</p></header>
<div class="meldung" role="status"><h2>Mögliche Dublette</h2><p>Ähnlicher Name wie Eintrag V-0031 „Ceylon Palace“, dazu gleiche PLZ und gleiche Adresse. Wahrscheinlich ist das eine Änderung am vorhandenen Eintrag, kein neuer. <a href="/verzeichnis/V-0031">Eintrag V-0031 ansehen</a></p></div>
<form action="/verzeichnis/VE-0019" method="post">
<table class="tabelle stapel vergleich">
  <thead><tr><th>Feld</th><th>Bisher (V-0031)</th><th>Einsendung</th><th>Entscheidung</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<dl class="daten klein abstand">
  <dt>Öffentlich</dt><dd>alle Felder außer der E-Mail des Einsenders</dd>
  <dt>Premium</dt><dd>nein, setzt nur der Administrator in WordPress</dd>
  <dt>Einwilligung</dt><dd>ja, Fassung vom 1. November 2026</dd>
</dl>
<div class="aktionen formende"><button type="submit" class="knopf primaer" name="ergebnis" value="aenderung">Als Änderung an V-0031 freigeben</button><button type="submit" class="knopf" name="ergebnis" value="neu">Als neuen Eintrag freigeben</button><button type="submit" class="knopf gefahr" name="ergebnis" value="ablehnen">Ablehnen</button></div>
</form>
</section>
"""
    seite("verzeichnis.html", "Verzeichnis", "Verzeichnis-Einsendung: bisher gegen neu, Dublettenhinweis und Freigabe je Feld.", "verzeichnis", inhalt)


# ---------------------------------------------------------------- Buchungen
def buchungen() -> None:
    inhalt = """
<header class="seitenkopf"><div><h1>Buchungen</h1><p class="unter">Werbebuchungen von tamil.de. Aktiv ist eine Buchung nur, wenn sie bezahlt, geprüft, nicht pausiert und heute im Zeitraum ist. Preise sind Platzhalter, bis KBS sie nennt.</p></div></header>
<ul class="reiter" aria-label="Nach Stand filtern">
  <li><a href="buchungen.html" aria-current="page">Alle <span class="n">5</span></a></li>
  <li><a href="buchungen.html?stand=pruefung">In Prüfung <span class="n">1</span></a></li>
  <li><a href="buchungen.html?stand=laeuft">Läuft <span class="n">1</span></a></li>
  <li><a href="buchungen.html?stand=warnung">Mit Warnung <span class="n">1</span></a></li>
</ul>
<table class="tabelle stapel">
  <thead><tr><th>Buchung</th><th>Platz</th><th>Zeitraum</th><th>Stand</th><th class="r">Einblendungen</th><th class="r">Klicks</th></tr></thead>
  <tbody>
    <tr aria-current="true"><td class="kopf"><a href="buchungen.html?buchung=W-2026-0007">W-2026-0007, Beispiel Reisen GmbH</a></td><td data-l="Platz">Billboard</td><td data-l="Zeitraum" class="nw">16.11. bis 29.11.</td><td data-l="Stand"><span class="st wartet">bezahlt, in Prüfung</span></td><td data-l="Einblendungen" class="r zahl">0</td><td data-l="Klicks" class="r zahl">0</td></tr>
    <tr><td class="kopf"><a href="buchungen.html?buchung=W-2026-0006">W-2026-0006, Musterkino Beispielstadt</a></td><td data-l="Platz">Leaderboard</td><td data-l="Zeitraum" class="nw">9.11. bis 15.11.</td><td data-l="Stand"><span class="st ok">läuft</span></td><td data-l="Einblendungen" class="r zahl">4.812</td><td data-l="Klicks" class="r zahl">37</td></tr>
    <tr><td class="kopf"><a href="buchungen.html?buchung=W-2026-0005">W-2026-0005, Beispiel Handel KG</a></td><td data-l="Platz">Im Artikel</td><td data-l="Zeitraum" class="nw">abgelehnt am 10.11.</td><td data-l="Stand"><span class="warnung">Erstattung fehlgeschlagen</span></td><td data-l="Einblendungen" class="r zahl">0</td><td data-l="Klicks" class="r zahl">0</td></tr>
    <tr><td class="kopf"><a href="buchungen.html?buchung=W-2026-0004">W-2026-0004, Beispiel Reisen GmbH</a></td><td data-l="Platz">Seitenspalte</td><td data-l="Zeitraum" class="nw">26.10. bis 8.11.</td><td data-l="Stand"><span class="st">beendet</span></td><td data-l="Einblendungen" class="r zahl">9.640</td><td data-l="Klicks" class="r zahl">71</td></tr>
    <tr><td class="kopf"><a href="buchungen.html?buchung=W-2026-0008">W-2026-0008, Beispiel Catering GmbH</a></td><td data-l="Platz">Fuß</td><td data-l="Zeitraum" class="nw">1.12. bis 7.12.</td><td data-l="Stand"><span class="st wartet">reserviert bis 9:52 Uhr</span></td><td data-l="Einblendungen" class="r zahl">0</td><td data-l="Klicks" class="r zahl">0</td></tr>
  </tbody>
</table>

<section class="vorgang" aria-labelledby="h-bu">
<header class="seitenkopf unterkopf"><div><h2 id="h-bu">W-2026-0007, Beispiel Reisen GmbH</h2><p class="unter">Billboard auf der Startseite, 14 Tage vom 16. bis 29. November. Bezahlt am 11. November über Stripe.</p></div><p class="st wartet">in Prüfung</p></header>
<div class="spalten">
<div>
  <section class="seite-teil" aria-labelledby="h-wm">
    <h3 id="h-wm" class="teil-kopf">Werbemittel</h3>
    <div class="werbemittel">
      <figure class="bild"><div class="flaeche desktop">Werbemittel Desktop, geliefert 970 × 250<br>billboard-desktop.jpg (Beispiel, Vorschau nicht enthalten)</div><figcaption>Desktop, erwartet 970 × 250</figcaption></figure>
      <figure class="bild"><div class="flaeche mobil">Werbemittel Handy, geliefert 320 × 100<br>billboard-mobil.jpg (Beispiel)</div><figcaption>Handy, erwartet 300 × 250</figcaption></figure>
    </div>
  </section>
  <section class="seite-teil" aria-labelledby="h-tech">
    <h3 id="h-tech" class="teil-kopf">Technische Prüfung</h3>
    <ul class="pruefliste">
      <li><span class="st ok">in Ordnung</span><span>Desktop: JPEG, 970 × 250, 112 KB</span></li>
      <li><span class="st halt">abweichend</span><span>Handy: JPEG, 320 × 100 statt 300 × 250. Ablehnen mit Grund oder den Kunden um eine neue Datei bitten.</span></li>
      <li><span class="st ok">in Ordnung</span><span>Zieladresse: https://reisen.example.org/sri-lanka, erreichbar</span></li>
      <li><span class="st ok">in Ordnung</span><span>Zahlung: bezahlt, Kennung der Stripe-Meldung einmalig</span></li>
    </ul>
  </section>
</div>
<aside aria-label="Entscheidung">
  <section class="freigabe" aria-labelledby="h-ent">
    <h3 id="h-ent">Entscheidung</h3>
    <dl class="daten">
      <dt>Betrag</dt><dd>Preis folgt (Platzhalter)</dd>
      <dt>Kunde</dt><dd>C. Beispiel, <a href="mailto:anzeigen@example.org">anzeigen@example.org</a></dd>
      <dt>Vorlauf</dt><dd>2 Werktage, Start am Montag</dd>
    </dl>
    <form action="/buchungen/W-2026-0007" method="post">
      <label class="feld"><span>Grund bei Ablehnung</span><textarea name="grund" rows="2">Werbemittel für das Handy hat das falsche Format.</textarea><small>Bei Ablehnung wird voll erstattet und die Tage werden frei.</small></label>
      <div class="aktionen"><button type="submit" class="knopf primaer" name="aktion" value="freigeben">Werbemittel freigeben</button><button type="submit" class="knopf gefahr" name="aktion" value="ablehnen">Ablehnen</button></div>
    </form>
  </section>
  <section class="seite-teil" aria-labelledby="h-st">
    <h3 id="h-st" class="teil-kopf">Einblendungen und Klicks</h3>
    <div class="leer"><p>Noch keine Zahlen. Gezählt wird ab dem Start, ohne Cookies und ohne Personendaten.</p></div>
  </section>
</aside>
</div>
</section>
"""
    seite("buchungen.html", "Buchungen", "Werbebuchungen: Liste, Prüfung des Werbemittels, Stand, Einblendungen und Klicks.", "buchungen", inhalt)


if __name__ == "__main__":
    uebersicht()
    entwurf(False)
    entwurf(True)
    eingang()
    social()
    verzeichnis()
    buchungen()
    print("geschrieben:", ", ".join(sorted(p.name for p in HIER.glob("*.html"))))
