#!/usr/bin/env python3
"""Erzeugt die Cockpit-Screens der Linie hm-aushang („Aushang“) als statische Seiten.

Nur Statik: HTML und CSS, Verhalten („Text kopieren“ beim WhatsApp-Entwurf) in app.js.
Echt sind Titel, Hinweise und Texte der Entwürfe (`docs/redaktion/rueckblick-2026.md`,
`design/inhalte/rueckblick/rueckblick.json`) und die Bildnachweise. Beispieldaten sind Personen („A. Beispiel“),
Firmen („Beispiel Reisen GmbH“), Adressen, Nummern (+49 000 …), Uhrzeiten des Tages, Beträge und Zählwerte;
E-Mail nur @example.org. Der Fuß jeder Seite sagt das.

Aufruf: python3 design/cockpit/hm-aushang/bauen.py
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parents[2]
RB = json.loads((ROOT / "design/inhalte/rueckblick/rueckblick.json").read_text(encoding="utf-8"))
BEITRAG = {str(b["story_id"]): b for b in RB["beitraege"]}
BILD = "../../inhalte/rueckblick/"
LOGO = "../../inhalte/logo.png"

e = html.escape
MONATE = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."]


def rueckblick_zeilen() -> list[dict]:
    """Die wartenden Entwürfe aus dem Rückblick-Bericht (echte Titel und Hinweise)."""
    text = (ROOT / "docs/redaktion/rueckblick-2026.md").read_text(encoding="utf-8")
    zeilen = []
    for z in text.splitlines():
        m = re.match(r"\| (2026-\d\d-\d\d) \| (\d+) \| (\d+) \| (.+?) \| (\d+) \| (\w+) \| (.*?) ?\|$", z)
        if m:
            zeilen.append(dict(datum=m[1], story=m[2], entwurf=m[3], titel=m[4], woerter=m[5], bild=m[6], hinweis=m[7].strip()))
    return zeilen


RUECK = rueckblick_zeilen()
ENTWURF = {z["entwurf"]: z for z in RUECK}


def tag_kurz(iso: str) -> str:
    j, m, t = iso.split("-")
    return f"{int(t)}. {MONATE[int(m) - 1]}"


# ---------------------------------------------------------------- Schale

ARBEIT = [
    ("uebersicht", "Übersicht", "uebersicht.html", ""),
    ("entwurf", "Entwürfe", "entwurf.html", "64"),
    ("eingang", "Eingang", "eingang.html", "5"),
    ("social", "Social", "social.html", "3"),
    ("verzeichnis", "Verzeichnis", "verzeichnis.html", "2"),
    ("buchungen", "Buchungen", "buchungen.html", "1"),
]
BETRIEB = [
    ("Stopp-Schalter", "uebersicht.html#schalter"),
    ("Kosten", "/kosten"),
    ("Quellen", "/quellen"),
    ("Protokoll", "/protokoll"),
    ("Zeitplan", "/zeitplan"),
    ("Benutzer", "/nutzer"),
]


def reiter(aktiv: str, klasse: str = "reiter") -> str:
    out = []
    for key, name, href, n in ARBEIT:
        cur = ' aria-current="page"' if key == aktiv else ""
        zahl = f' <span class="n">{n}</span>' if n else ""
        out.append(f'<li><a href="{href}"{cur}>{name}{zahl}</a></li>')
    return f'<ul class="{klasse}">' + "".join(out) + "</ul>"


def betrieb_liste() -> str:
    return ('<div class="aufklapp-liste"><p class="klein leise wer">Angemeldet als redaktion1</p><ul class="menue-ziele">'
            + "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in BETRIEB) + "</ul></div>")


def seite(datei: str, titel: str, beschreibung: str, aktiv: str, inhalt: str, skript: bool = False) -> None:
    js = '<script src="app.js" defer></script>\n' if skript else ""
    menue_liste = (
        '<div class="aufklapp-liste"><p class="menue-kopf">Arbeit</p>'
        + reiter(aktiv, "menue-ziele")
        + '<p class="menue-kopf">Betrieb</p><ul class="menue-ziele">'
        + "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in BETRIEB)
        + '</ul><form action="/logout" method="post"><p class="klein leise">Angemeldet als redaktion1</p>'
        '<button type="submit" class="knopf still">Abmelden</button></form></div>'
    )
    doc = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titel)}, Redaktion tamil.de</title>
<meta name="description" content="{e(beschreibung)}">
<meta name="robots" content="noindex">
<link rel="preload" href="schriften/epilogue-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="cockpit.css">
{js}</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="kopf">
  <div class="kopf-innen">
    <a class="marke" href="uebersicht.html" aria-label="Redaktion tamil.de, zur Übersicht"><img src="{LOGO}" alt="tamil.de" width="300" height="121"><span>Redaktion</span></a>
    <nav aria-label="Cockpit">{reiter(aktiv)}</nav>
    <div class="rechts">
      <details class="aufklapp"><summary>Betrieb</summary>{betrieb_liste()}</details>
      <form action="/logout" method="post"><button type="submit" class="knopf still" title="Angemeldet als redaktion1">Abmelden</button></form>
    </div>
    <details class="aufklapp menue"><summary>Menü</summary><nav aria-label="Cockpit, Menü">{menue_liste}</nav></details>
  </div>
</header>
<div class="aushang" role="status">
  <div class="aushang-innen">
    <time class="zeit" datetime="2026-11-13T14:20">14:20</time>
    <p><b>Als Nächstes geht hinaus:</b> Instagram, „{e(BEITRAG['49']['titel'])}“, Karenz endet in 8 Minuten. Trockenmodus: nichts geht an Meta.</p>
    <form action="/social/1/stoppen" method="post"><a class="knopf still" href="social.html#karenz">Ansehen</a> <button type="submit" class="knopf halt">Stoppen</button></form>
  </div>
</div>
<main id="inhalt" class="seite">
{inhalt}
</main>
<footer class="fuss"><p>Probe der Linie Aushang, Stand Freitag, 13. November 2026, 14:12 Uhr. Titel, Texte, Hinweise und Bildnachweise der Entwürfe sind echt. Personen, Firmen, Adressen, Telefonnummern, Uhrzeiten des Tages, Beträge und Zählwerte sind Beispieldaten; E-Mail-Adressen enden auf example.org.</p></footer>
</body>
</html>
"""
    (HIER / datei).write_text(doc, encoding="utf-8")


def frist(zeit: str, rel: str, iso: str, naechst: bool = False) -> str:
    k = "frist naechst" if naechst else "frist"
    return f'<div class="{k}"><time class="zeit" datetime="{iso}">{zeit}</time><span class="rel">{rel}</span></div>'


def zeile(fr: str, titel: str, text: str, tun: str = "", aktuell: bool = False) -> str:
    cur = ' aria-current="true"' if aktuell else ""
    tun_html = f'<div class="tun">{tun}</div>' if tun else ""
    return f'<li{cur}>{fr}<div class="zeile"><h3>{titel}</h3><p>{text}</p></div>{tun_html}</li>'


def tabelle(kopf: list[str], reihen: list[list[str]], klasse: str = "tabelle stapel", caption: str = "", zahl: tuple = ()) -> str:
    cap = f"<caption>{caption}</caption>" if caption else ""
    zk = ' class="zahl"'
    th = "".join(f'<th scope="col"{zk if i in zahl else ""}>{k}</th>' for i, k in enumerate(kopf))
    body = []
    for r in reihen:
        zellen = []
        for i, z in enumerate(r):
            kl = ' class="zahl"' if i in zahl else ""
            zellen.append(f'<td data-l="{e(kopf[i])}"{kl}>{z}</td>')
        body.append("<tr>" + "".join(zellen) + "</tr>")
    return f'<table class="{klasse}">{cap}<thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table>'


# ---------------------------------------------------------------- Übersicht

def uebersicht() -> None:
    radar = [("5", "2026-11-15", "15. Nov.", "in 2 Tagen", "„Jailer 2“ am 15. November zum Spezialpreis im Kino Claudia in Kloten", "Termin: vor dem Kinotag freigeben, sonst ist die Meldung überholt."),
             ("4", "2026-12-13", "13. Dez.", "in 30 Tagen", "THADAM 2026: Tamilische Networking- und Gala-Nacht am 13. Dezember in Bern", "Termin aus der Ankündigung des Veranstalters."),
             ("54", "2026-11-12", "12. Nov.", "seit gestern", "„OM“ im Kino: 12 Spielorte in Deutschland", "Kinoliste der Woche; Spielorte gegen die Kinoseiten prüfen.")]
    entw = []
    for i, (nr, iso, kurz, rel, titel, txt) in enumerate(radar):
        entw.append(zeile(frist(kurz, rel, iso, naechst=(i == 0)),
                          f'<a href="entwurf.html">Entwurf {nr}: {e(titel)}</a>', f"Aus dem laufenden Radar. {txt}",
                          '<a class="knopf still" href="entwurf.html">Öffnen</a>'))
    for z in [r for r in RUECK if r["entwurf"] != "17"][:6]:
        hinweis = f"Vor der Freigabe: {e(z['hinweis'])}" if z["hinweis"] else "Keine Hinweise vor der Freigabe."
        entw.append(zeile(frist(tag_kurz(z["datum"]), "Ereignis", z["datum"]),
                          f'<a href="entwurf.html">Entwurf {z["entwurf"]}: {e(z["titel"])}</a>',
                          f'Rückblick, Story {z["story"]}, {z["woerter"]} Wörter, Bild {e(z["bild"])}. {hinweis}',
                          '<a class="knopf still" href="entwurf.html">Öffnen</a>'))

    heute = [
        (frist("14:20", "in 8 Min.", "2026-11-13T14:20", True), '<a href="social.html#karenz">Instagram, danach Facebook: Entwurf 17</a>', f"„{e(BEITRAG['49']['titel'])}“. Karenz seit 14:10 Uhr, Text änderbar, stoppbar. Trockenmodus.", '<a class="knopf still" href="social.html#karenz">Ansehen</a>'),
        (frist("16:00", "heute", "2026-11-13T16:00"), "Kinoliste der Woche wird neu abgerufen", "Zeitplan des Radars, Schalter „redaktion“ läuft. Neue Spielorte landen als Fassung bei Entwurf 54.", '<a class="knopf still" href="/zeitplan">Zeitplan</a>'),
        (frist("22:00", "Ruhezeit", "2026-11-13T22:00"), "Social ruht bis 7 Uhr", "Regel R6: Was danach wartet, geht ab 7 Uhr in der Reihenfolge hinaus.", ""),
        (frist("16. Nov.", "Montag", "2026-11-16"), '<a href="buchungen.html">Werbemittel B-2026-0003 prüfen</a>', "Start am 17. November, zwei Werktage Vorlauf. Das Handy-Format weicht ab.", '<a class="knopf still" href="buchungen.html">Prüfen</a>'),
    ]
    heute_html = "".join(zeile(f, t, x, a) for f, t, x, a in heute)

    eingang = [
        (frist("13:41", "heute", "2026-11-13T13:41"), '<a href="eingang.html">Termin: Pongal-Abend des Beispielvereins Essen</a>', "Agent: mögliche Dublette von E-2026-0409."),
        (frist("11:02", "heute", "2026-11-13T11:02"), '<a href="verzeichnis.html">Verzeichnis: Restaurant AiYA, Zürich</a>', "Agent: ähnlicher Name und gleiche PLZ wie V-0012."),
        (frist("9:15", "heute", "2026-11-13T09:15"), '<a href="buchungen.html">Buchung B-2026-0003, Leaderboard</a>', "Bezahlt, Werbemittel in Prüfung."),
        (frist("12. Nov.", "19:15 Uhr", "2026-11-12T19:15"), '<a href="eingang.html">Termin: Herbstkonzert des Beispielchors</a>', "Agent: Datum liegt in der Vergangenheit."),
    ]
    eingang_html = "".join(zeile(f, t, x) for f, t, x in eingang)

    schalter = [
        ("alles", "läuft", ""),
        ("redaktion", "läuft", "Scan, Modellaufrufe, Agent-Modus"),
        ("website", "läuft", "Übertragung nach WordPress"),
        ("eingang", "läuft", "Abholen der Einsendungen"),
        ("verzeichnis", '<span class="wort halt">angehalten</span>', "seit 12. Nov., 18:40 Uhr, redaktion1: „Formular auf der Website noch nicht live“"),
        ("instagram", '<span class="wort">Trockenmodus</span>', "bis zur Freigabe des Regelwerks durch KBS"),
        ("facebook", '<span class="wort">Trockenmodus</span>', "folgt Instagram mit demselben Inhalt"),
        ("whatsapp", "läuft", "nur Entwürfe, gepostet wird von Hand"),
    ]
    schalter_reihen = [[f"<b>{k}</b>", s, f'<span class="klein">{x}</span>' if x else ""] for k, s, x in schalter]

    inhalt = f"""
<div class="seitenkopf">
  <div><h1>Übersicht</h1><p>Freitag, 13. November 2026. Radar zuletzt um 14:09 Uhr mit 2 neuen Meldungen, nächster Lauf 14:15 Uhr.</p></div>
</div>
<dl class="zahlen">
  <div><dt>Entwürfe warten</dt><dd>64</dd></div>
  <div><dt>Einsendungen neu</dt><dd>5</dd></div>
  <div><dt>Social von Hand</dt><dd>2</dd></div>
  <div><dt>Verzeichnis offen</dt><dd>2</dd></div>
  <div><dt>Werbemittel zu prüfen</dt><dd>1</dd></div>
</dl>
<div class="zwei abschnitt">
  <div class="spalte">
    <section class="abschnitt" aria-labelledby="h-heute">
      <div class="kopfzeile"><h2 id="h-heute">Was als Nächstes geschieht</h2><a href="/zeitplan">Zeitplan</a></div>
      <ol class="brett">{heute_html}</ol>
    </section>
    <section class="abschnitt" id="entwuerfe" aria-labelledby="h-entw">
      <div class="kopfzeile"><h2 id="h-entw">Entwürfe, die auf Freigabe warten</h2><p class="klein">3 aus dem Radar, 61 aus dem Rückblick</p></div>
      <ol class="brett">{"".join(entw)}</ol>
      <a class="mehr" href="entwurf.html">Alle 61 Rückblick-Entwürfe</a>
    </section>
    <section class="abschnitt" aria-labelledby="h-ein">
      <div class="kopfzeile"><h2 id="h-ein">Neu eingegangen</h2><a href="eingang.html">Eingang</a></div>
      <ol class="brett">{eingang_html}</ol>
    </section>
  </div>
  <div class="spalte">
    <section class="abschnitt" id="schalter" aria-labelledby="h-schalter">
      <h2 id="h-schalter">Stopp-Schalter</h2>
      {tabelle(["Kanal", "Stand", "Grund"], schalter_reihen)}
      <form action="/schalter" method="post">
        <div class="feld"><label for="kanal">Kanal</label>
          <select id="kanal" name="kanal">{"".join(f'<option>{k}</option>' for k, _, _ in schalter)}</select></div>
        <div class="feld"><label for="grund">Grund</label><textarea id="grund" name="grund" required maxlength="300" aria-describedby="grund-h"></textarea>
          <p class="hilfe" id="grund-h">Pflicht beim Anhalten, steht im Protokoll mit Name und Zeit.</p></div>
        <div class="knoepfe"><button type="submit" name="aktion" value="an" class="knopf halt">Anhalten</button><button type="submit" name="aktion" value="aus" class="knopf still">Wieder laufen lassen</button></div>
      </form>
    </section>
    <section class="abschnitt" aria-labelledby="h-budget">
      <h2 id="h-budget">Budget</h2>
      {tabelle(["Zeitraum", "Verbraucht", "Grenze"], [["heute", "1,84 €", "5,00 €"], ["November", "23,10 €", "60,00 €"]], zahl=(1, 2))}
      <p class="klein leise">Reserviert für laufende Aufrufe: 0,12 €. Ist die Grenze erreicht, schreibt der Radar nichts Neues.</p>
    </section>
    <section class="abschnitt" aria-labelledby="h-radar">
      <h2 id="h-radar">Radar</h2>
      <p class="klein">Eine Quelle meldet seit gestern einen Fehler beim Abruf. <a href="/quellen">Quellen ansehen</a></p>
    </section>
  </div>
</div>
"""
    seite("uebersicht.html", "Übersicht", "Stand der Redaktion: was als Nächstes hinausgeht, wartende Entwürfe, Eingang, Schalter, Budget.", "uebersicht", inhalt)


# ---------------------------------------------------------------- Entwurf

QUELLEN = [
    ("Q1", "Sivaalayam München, Ankündigung der Feier zu Deepavali", "Primärquelle, Veranstalter"),
    ("Q2", "Sri Ganesha Hindu Temple Berlin, Festkalender", "Veranstalter, Kalender ohne Datum für Lakshmi Pooja"),
    ("Q3", "Düsseldorf Tamil Sangam, Einladung zur Feier am 15. November", "Veranstalter, Einladung"),
]
CLAIMS = [
    [("C1", "Deepavali fiel 2026 auf Sonntag, 8. November.", "Q1", "belegt"),
     ("C2", "Sivaalayam München kündigte Feierlichkeiten für diesen Tag an.", "Q1", "belegt"),
     ("C3", "Der Sri Ganesha Hindu Temple in Berlin hat das Lichterfest mit Lakshmi Pooja im Kalender.", "Q2", '<span class="wort halt">Datum nicht belegt</span>'),
     ("C4", "Der Düsseldorf Tamil Sangam lädt am Sonntag, 15. November, zur eigenen Feier ein.", "Q3", "belegt, als Einladung")],
    [("C5", "Der Name kommt aus dem Sanskrit und heißt ungefähr „Reihe von Lichtern“.", "", '<span class="wort wartet">Hintergrund</span>')],
    [("C6", "Den Termin bestimmt der hinduistische Mondkalender, meist eine Neumondnacht im Oktober oder November.", "", '<span class="wort wartet">Hintergrund</span>')],
    [("C7", "Bräuche: Diyas, Lichterketten, Rangoli, Tempelbesuch.", "", '<span class="wort wartet">Hintergrund</span>')],
]


def entwurf(lizenz_fehlt: bool) -> None:
    b = BEITRAG["30"]
    z = ENTWURF["7"]
    absaetze = []
    for i, text in enumerate(b["absaetze"]):
        reihen = [[f'<span class="c">{c}</span>', e(aus), q or '<span class="leise">ohne</span>', st] for c, aus, q, st in CLAIMS[i]]
        absaetze.append(f'<div class="absatz"><p class="prosa">{e(text)}</p>'
                        f'{tabelle(["Aussage", "Wortlaut", "Beleg", "Stand"], reihen, caption=f"Aussagen in Absatz {i + 1}")}</div>')
    quellen = tabelle(["Quelle", "Was", "Art"], [[f'<span class="c">{q}</span>', e(w), e(a)] for q, w, a in QUELLEN])
    hinweise = "".join(f"<li>{e(h.strip())}</li>" for h in z["hinweis"].split(";"))

    if lizenz_fehlt:
        bild_dl = f"""<dl class="datensatz">
  <dt>Herkunft</dt><dd>upload, von redaktion1 um 13:58 Uhr</dd>
  <dt>Datei</dt><dd>deepavali-berlin.jpg</dd>
  <dt>Rechteinhaber</dt><dd class="fehlt">fehlt</dd>
  <dt>Lizenz</dt><dd class="fehlt">fehlt</dd>
  <dt>Bildnachweis</dt><dd class="fehlt">fehlt</dd>
  <dt>Soziale Netze</dt><dd>nicht eingetragen</dd>
</dl>"""
        meldung = """<div class="meldung fehler" role="alert"><strong>Lizenz fehlt.</strong>
  <p>Zum hochgeladenen Bild gibt es keinen Lizenz-Datensatz. Ohne Datensatz kein Bild (K6), deshalb ist Freigeben gesperrt.</p>
  <div class="knoepfe"><a class="knopf" href="#lizenz">Lizenz eintragen</a></div></div>"""
        freigabe_knopf = '<button type="submit" class="knopf" disabled aria-describedby="sperre">Veröffentlichen</button>'
        sperre = '<p class="klein signal" id="sperre">Gesperrt, bis der Lizenz-Datensatz vollständig ist oder die Bildkarte gewählt ist.</p>'
        formular = f"""<section class="abschnitt" id="lizenz" aria-labelledby="h-lizenz">
  <h2 id="h-lizenz">Lizenz eintragen</h2>
  <p class="klein">Commons nur gemeinfrei, CC0, CC BY oder CC BY-SA. Pressebilder nur mit Erlaubnis im Register.</p>
  <form action="/entwurf/7/lizenz" method="post">
    <div class="felder2">
      <div class="feld"><label for="l-herkunft">Herkunft</label><select id="l-herkunft" name="herkunft">{"".join(f"<option{' selected' if o == 'upload' else ''}>{o}</option>" for o in ["archiv", "quelle", "commons", "stock", "pool", "upload", "karte", "ki"])}</select></div>
      <div class="feld"><label for="l-inhaber">Rechteinhaber, Pflicht</label><input id="l-inhaber" name="rechteinhaber" type="text" required></div>
      <div class="feld"><label for="l-lizenz">Lizenz, Pflicht</label><select id="l-lizenz" name="lizenz" required aria-describedby="l-lizenz-h"><option value="">Bitte wählen</option><option>gemeinfrei oder CC0</option><option>CC BY</option><option>CC BY-SA</option><option>Plattformlizenz</option><option>eigene Vereinbarung</option></select><p class="hilfe" id="l-lizenz-h">NC und ND sind nicht zulässig und fehlen deshalb.</p></div>
      <div class="feld"><label for="l-version">Version</label><input id="l-version" name="version" type="text" placeholder="etwa 4.0"></div>
      <div class="feld"><label for="l-adresse">Lizenz-Adresse</label><input id="l-adresse" name="lizenz_url" type="url"></div>
      <div class="feld"><label for="l-quelle">Quelle des Bildes</label><input id="l-quelle" name="quelle_url" type="url"></div>
      <div class="feld"><label for="l-umfang">Umfang</label><input id="l-umfang" name="umfang" type="text" value="Online-Veröffentlichung auf tamil.de"></div>
      <div class="feld"><label for="l-ablauf">Ablauf</label><input id="l-ablauf" name="ablauf" type="date"></div>
    </div>
    <fieldset><legend>Recht für soziale Netze</legend>
      <div class="wahl"><label><input type="radio" name="social" value="ja"> ja</label><label><input type="radio" name="social" value="nein"> nein</label><label><input type="radio" name="social" value="offen" checked> ungeklärt</label></div>
      <p class="hilfe">Ohne Ja nimmt Social die Bildkarte „Grafik: Tamil.de“ (Regel R4).</p></fieldset>
    <div class="feld"><label for="l-nachweis">Bildnachweis, wie er unter dem Bild steht</label><input id="l-nachweis" name="attribution" type="text" placeholder="Foto: Name / Herkunft, Lizenz"></div>
    <label class="haken"><input type="checkbox" name="ki"> Das Bild stammt aus einer KI</label>
    <div class="knoepfe"><button type="submit" class="knopf">Lizenz speichern</button><button type="submit" formaction="/entwurf/7/bildkarte" class="knopf still">Bildkarte nehmen</button><button type="submit" formaction="/entwurf/7/bild-neu" class="knopf still">Bild neu suchen lassen</button></div>
  </form>
</section>"""
        bildunterschrift = "Hochgeladen, ohne Nachweis"
    else:
        bild_dl = f"""<dl class="datensatz">
  <dt>Herkunft</dt><dd>commons</dd>
  <dt>Rechteinhaber</dt><dd>18quirl08</dd>
  <dt>Lizenz</dt><dd>CC BY-SA 4.0</dd>
  <dt>Umfang</dt><dd>Online-Veröffentlichung auf tamil.de</dd>
  <dt>Quelle</dt><dd><a href="{e(b['quelle_bild'])}">Wikimedia Commons</a></dd>
  <dt>Soziale Netze</dt><dd>nicht eingetragen</dd>
  <dt>KI</dt><dd>nein</dd>
</dl>"""
        meldung = ""
        freigabe_knopf = '<button type="submit" class="knopf">Veröffentlichen</button>'
        sperre = ""
        formular = ""
        bildunterschrift = e(b["nachweis"])

    status = "neu, Stand 3" if not lizenz_fehlt else "bearbeitet, Stand 4"
    vorn = " vorn" if lizenz_fehlt else ""
    datei = "entwurf-lizenz-fehlt.html" if lizenz_fehlt else "entwurf.html"
    andere = ('<a href="entwurf.html">Zustand mit Lizenz</a>' if lizenz_fehlt else '<a href="entwurf-lizenz-fehlt.html">Zustand „Lizenz fehlt“</a>')
    inhalt = f"""
<div class="seitenkopf">
  <div><p class="pfad"><a href="uebersicht.html#entwuerfe">Entwürfe</a></p>
  <h1>Entwurf 7</h1><p>Story 30, Rückblick, Rubrik Events, Ereignis 8. November 2026, {z['woerter']} Wörter. {status}.</p></div>
  <p class="klein">{andere}</p>
</div>
<div class="zwei">
  <div class="spalte">
    <section class="abschnitt" aria-labelledby="h-text">
      <div class="kopfzeile"><h2 id="h-text">Text mit Belegen je Absatz</h2><p class="klein">Gezeigt sind die ersten vier Absätze.</p></div>
      <h3 class="titelzeile">{e(b['titel'])}</h3>
      <p class="vorspann">{e(b['teaser'])}</p>
      <div style="margin-top: var(--space-lg)">{"".join(absaetze)}</div>
    </section>
    <section class="abschnitt" aria-labelledby="h-quellen"><h2 id="h-quellen">Quellen</h2>{quellen}</section>
    <section class="abschnitt" aria-labelledby="h-bearb">
      <h2 id="h-bearb">Bearbeiten</h2>
      <details class="mehrteil"><summary>Titel, Vorspann und Rubrik ändern</summary>
        <form action="/entwurf/7/speichern" method="post">
          <input type="hidden" name="stand" value="3">
          <div class="feld"><label for="e-titel">Titel, höchstens 90 Zeichen</label><input id="e-titel" name="titel" type="text" maxlength="90" value="{e(b['titel'])}"></div>
          <div class="feld"><label for="e-teaser">Vorspann, höchstens 220 Zeichen</label><textarea id="e-teaser" name="teaser" maxlength="220">{e(b['teaser'])}</textarea></div>
          <div class="feld"><label for="e-alt">Alternativtext, höchstens 125 Zeichen</label><input id="e-alt" name="bild_alt" type="text" maxlength="125" value="{e(b['alt'])}"></div>
          <div class="knoepfe"><button type="submit" class="knopf">Speichern</button></div>
        </form>
      </details>
      <details class="mehrteil"><summary>Fassungen (3)</summary>
        {tabelle(["Stand", "Wann", "Wer"], [["3", "12. Nov., 18:03 Uhr", "radar"], ["2", "12. Nov., 17:51 Uhr", "radar, Gate"], ["1", "12. Nov., 17:40 Uhr", "agent"]])}
      </details>
    </section>
  </div>
  <aside class="spalte{vorn}" aria-label="Freigabe und Bild">
    <section class="freigabe" aria-labelledby="h-frei">
      <h2 id="h-frei">Freigabe</h2>
      {meldung}
      <p class="klein" style="margin-top: var(--space-sm)">Vor der Freigabe, aus dem Bericht des Redakteurs:</p>
      <ul>{hinweise}</ul>
      <form action="/entwurf/7/freigeben" method="post">
        <input type="hidden" name="stand" value="3">
        <div class="knoepfe">{freigabe_knopf}<button type="submit" formaction="/entwurf/7/zurueck" class="knopf still">Zurückstellen</button></div>
        {sperre}
        <p class="klein leise" style="margin-top: var(--space-xs)">Freigeben veröffentlicht sofort auf tamil.de. Gilt nur für den gesehenen Stand.</p>
      </form>
    </section>
    <section class="abschnitt" aria-labelledby="h-bild">
      <h2 id="h-bild">Bild</h2>
      <figure class="bild" style="margin-top: var(--space-md)"><img src="{BILD}{b['bild']}" alt="{e(b['alt'])}" width="960" height="1280"><figcaption>{bildunterschrift}</figcaption></figure>
      {bild_dl}
    </section>
    {formular}
  </aside>
</div>
"""
    titel = "Entwurf 7, Lizenz fehlt" if lizenz_fehlt else "Entwurf 7"
    seite(datei, titel, "Entwurf mit Aussagen und Belegen je Absatz, Bild mit Lizenz-Datensatz und Freigabe.", "entwurf", inhalt)


# ---------------------------------------------------------------- Eingang

def eingang() -> None:
    liste = [
        (frist("13:41", "heute", "2026-11-13T13:41"), '<a href="eingang.html?nr=E-2026-0418">E-2026-0418, Termin: Pongal-Abend des Beispielvereins Essen</a>', "Agent: mögliche Dublette von E-2026-0409. Entwurf 69 vorbereitet.", True),
        (frist("12:20", "heute", "2026-11-13T12:20"), '<a href="eingang.html?nr=E-2026-0417">E-2026-0417, Beitrag: Tamilschule Beispielstadt sucht Lehrkräfte</a>', "Agent: ein Link im Text, keine Hinweise. Entwurf 70 vorbereitet.", False),
        (frist("9:02", "heute", "2026-11-13T09:02"), '<a href="eingang.html?nr=E-2026-0416">E-2026-0416, Werbung: Beispiel Reisen GmbH fragt nach Dezember</a>', "Wunsch: Leaderboard, 1. bis 14. Dezember. An KBS weitergeben.", False),
        (frist("12. Nov.", "19:15 Uhr", "2026-11-12T19:15"), '<a href="eingang.html?nr=E-2026-0415">E-2026-0415, Termin: Herbstkonzert des Beispielchors</a>', '<span class="wort halt">Datum liegt in der Vergangenheit</span> (7. November 2026).', False),
        (frist("11. Nov.", "8:30 Uhr", "2026-11-11T08:30"), '<a href="eingang.html?nr=E-2026-0414">E-2026-0414, Kontakt: Frage zum Impressum</a>', "Antwort nur von Hand.", False),
    ]
    brett = "".join(zeile(f, t, x, aktuell=a) for f, t, x, a in liste)
    filt = [("alle", "Alle", "5", True), ("event", "Termin", "2", False), ("beitrag", "Beitrag", "1", False), ("kooperation", "Kooperation", "0", False), ("werbung", "Werbung", "1", False), ("kontakt", "Kontakt", "1", False)]
    filt_html = '<ul class="filter">' + "".join(
        f'<li><a href="eingang.html?art={k}"{" aria-current=\"page\"" if c else ""}>{n} <span class="n">{z}</span></a></li>'.replace('\\"', '"')
        for k, n, z, c in filt) + "</ul>"
    angaben = [
        ["Titel", "Pongal-Abend des Beispielvereins Essen"], ["Datum und Uhrzeit", "Samstag, 16. Januar 2027, 17:00 Uhr"], ["Ende", "22:00 Uhr"],
        ["Ort mit Adresse", "Beispielhalle, Beispielstraße 1"], ["Stadt und Land", "Essen, DE"], ["Veranstalter", "Beispielverein Essen e. V."],
        ["Beschreibung", "Pongal-Feier mit Kolam, Musik und Essen für Familien. Eintritt frei, Spenden für den Verein."],
        ["Eintritt", "frei"], ["Ticket-Link", '<a href="https://example.org/pongal">example.org/pongal</a>'],
        ["Bild", "pongal-essen.jpg, JPEG, 1,2 MB, ohne Metadaten gespeichert; Recht vom Einsender bestätigt"],
        ["Einsender", 'A. Beispiel, <a href="mailto:a.beispiel@example.org">a.beispiel@example.org</a>, Telefon +49 000 0000000'],
        ["Einwilligung", "ja, Fassung „Platzhalter, Text von KBS folgt“"],
    ]
    angaben_html = '<table class="tabelle stapel"><thead><tr><th scope="col">Feld</th><th scope="col">Angabe des Einsenders</th></tr></thead><tbody>' + "".join(
        f'<tr><td data-l="Feld"><b>{k}</b></td><td data-l="Angabe">{v}</td></tr>' for k, v in angaben) + "</tbody></table>"
    inhalt = f"""
<div class="seitenkopf"><div><h1>Eingang</h1><p>Einsendungen von der Website. Der Agent prüft und bereitet vor, entscheiden tut die Redaktion.</p></div></div>
<h2 class="visually-hidden">Einsendungen</h2>
<nav aria-label="Filter nach Art">{filt_html}</nav>
<ol class="brett">{brett}</ol>

<div class="zwei abschnitt">
  <section class="spalte" aria-labelledby="h-vorgang">
    <div class="abschnitt">
      <div class="kopfzeile"><h2 id="h-vorgang">E-2026-0418, Termin</h2><p class="klein">eingegangen 13:41 Uhr, abgeholt 13:42 Uhr, vorbereitet 13:44 Uhr</p></div>
      {angaben_html}
    </div>
    <div class="abschnitt">
      <h2>Entwurf 69</h2>
      <p class="prosa" style="margin-top: var(--space-md)">Der Beispielverein Essen lädt am Samstag, 16. Januar 2027, ab 17 Uhr zum Pongal-Abend in die Beispielhalle ein. Geplant sind Kolam, Musik und Essen für Familien; der Eintritt ist frei.</p>
      <p class="klein" style="margin-top: var(--space-sm)">Vermerk am Entwurf: Angaben des Einsenders, ungeprüft.</p>
    </div>
  </section>
  <aside class="spalte" aria-label="Prüfung und Entscheidung">
    <section class="freigabe" aria-labelledby="h-pruef">
      <h2 id="h-pruef">Prüfung des Agenten</h2>
      <ul class="regeln">
        <li><b>Datum</b><span>liegt in der Zukunft, plausibel</span></li>
        <li><b>Ort</b><span>Essen, innerhalb von DE, AT, CH</span></li>
        <li class="halt"><b>Dublette</b><span><span class="wort halt">möglich:</span> E-2026-0409 hat denselben Titel und dasselbe Datum, anderer Einsender. <a href="eingang.html?nr=E-2026-0409">Vergleichen</a></span></li>
        <li><b>Links</b><span>einer, erlaubt sind drei</span></li>
      </ul>
      <form action="/eingang/E-2026-0418" method="post">
        <div class="feld"><label for="notiz">Notiz der Redaktion</label><textarea id="notiz" name="notiz"></textarea></div>
        <div class="knoepfe">
          <button type="submit" name="aktion" value="uebernehmen" class="knopf">Übernehmen</button>
          <button type="submit" name="aktion" value="erledigt" class="knopf still">Erledigt</button>
          <button type="submit" name="aktion" value="ablehnen" class="knopf still">Ablehnen</button>
          <button type="submit" name="aktion" value="spam" class="knopf halt">Spam</button>
        </div>
      </form>
      <p class="klein" style="margin-top: var(--space-md)">Keine Mail an den Einsender. <a href="mailto:a.beispiel@example.org?subject=Ihr%20Termin%20E-2026-0418">Von Hand antworten</a></p>
      <p class="klein leise" style="margin-top: var(--space-xs)">Gelöscht 90 Tage nach Abschluss, Spam nach 7 Tagen.</p>
    </section>
  </aside>
</div>

<section class="abschnitt" aria-labelledby="h-leer">
  <h2 id="h-leer">Kooperation</h2>
  <div class="leer"><p>Keine Anfragen zur Kooperation. Neue erscheinen hier, sobald der Radar den Eingang abholt; der Schalter „eingang“ läuft.</p>
  <div class="knoepfe"><a class="knopf still" href="eingang.html?art=alle">Alle Einsendungen</a></div></div>
</section>
"""
    seite("eingang.html", "Eingang", "Einsendungen mit Prüfung des Agenten, Entwurf und Entscheidung.", "eingang", inhalt)


# ---------------------------------------------------------------- Social

def social() -> None:
    b = BEITRAG["49"]
    text = f"{b['titel']}\n\n{b['teaser']}\n\nMehr auf tamil.de: https://tamil.de/berlin-sri-ganesha-hindu-temple-geweiht/"
    regeln = [("R1", "Rubrik Community, nicht heikel"), ("R2", "kein heikles Thema"), ("R3", "veröffentlicht heute 14:10 Uhr, jünger als 48 Stunden"),
              ("R4", "Bild CC BY-SA, Recht für soziale Netze nicht eingetragen: Bildkarte"), ("R5", "zweiter Beitrag heute, letzter um 12:50 Uhr"),
              ("R6", "außerhalb der Ruhezeit"), ("R7", "noch nie auf Instagram"), ("R8", "kein KI-Bild"), ("R9", "kein Altbestand")]
    regeln_html = "".join(f"<li><b>{r}</b><span>erfüllt: {e(t)}</span></li>" for r, t in regeln)
    von_hand = [
        (frist("13:05", "seit 1 Std.", "2026-11-13T13:05"), f'Entwurf 34: {e(ENTWURF["34"]["titel"])}', '<span class="wort halt">R2 verletzt:</span> Politik, heikles Thema, geht nie automatisch.',
         '<button type="submit" class="knopf still" form="vh-34">Freigeben</button><button type="submit" class="knopf still" form="vh-34" formaction="/social/34/verwerfen">Verwerfen</button>'),
        (frist("11:40", "seit 2 Std.", "2026-11-13T11:40"), f'Entwurf 31: {e(ENTWURF["31"]["titel"])}', '<span class="wort halt">R2 unklar:</span> im Bericht als „sensibel, zweite Person lesen“ markiert.',
         '<button type="submit" class="knopf still" form="vh-31">Freigeben</button><button type="submit" class="knopf still" form="vh-31" formaction="/social/31/verwerfen">Verwerfen</button>'),
    ]
    vh = "".join(zeile(f, t, x, a) for f, t, x, a in von_hand)
    hist = {
        "Instagram": [["14:10", "Entwurf 17, Sri Ganesha Hindu Temple", "Karenz bis 14:20 Uhr", "Trockenmodus"],
                      ["13:05", "Entwurf 34, Steinmeier in Hamm-Uentrop", "von Hand", "R2"],
                      ["12:50", "Entwurf 12, Ceylon Palace Bremen", "trocken gesendet", "wäre an Meta gegangen"],
                      ["11:40", "Entwurf 31, Restaurant AiYA", "von Hand", "R2 unklar"]],
        "Facebook": [["12:51", "Entwurf 12, Ceylon Palace Bremen", "trocken gesendet", "folgt Instagram"]],
        "WhatsApp": [["12:02", "Entwurf 12, Ceylon Palace Bremen", "gepostet", "von redaktion1 markiert"]],
    }
    hist_html = "".join(f'<div class="abschnitt" style="margin-top: var(--space-xl)">{tabelle(["Zeit", "Beitrag", "Stand", "Grund"], r, caption=k)}</div>' for k, r in hist.items())
    inhalt = f"""
<div class="seitenkopf"><div><h1>Social</h1><p>Regelwerk Fassung 1 vom 13. November 2026. Trockenmodus, bis KBS die Fassung freigibt: alles läuft bis vor den letzten Aufruf an Meta.</p></div>
<p class="klein"><a href="/social/regelwerk">Regelwerk lesen</a></p></div>

<section class="abschnitt" id="karenz" aria-labelledby="h-karenz">
  <div class="kopfzeile"><h2 id="h-karenz">In der Karenz</h2><p class="klein">zehn Minuten änderbar und stoppbar</p></div>
  <div class="karenz">
    <div>
      <ol class="brett"><li>{frist("14:20", "noch 8 Min.", "2026-11-13T14:20", True)}<div class="zeile"><h3>Instagram, danach Facebook: Entwurf 17</h3><p>{e(b['titel'])}. Erkannt 14:10 Uhr nach der Freigabe.</p></div></li></ol>
      <form action="/social/17/text" method="post">
        <div class="feld"><label for="s-text">Text für Instagram und Facebook</label><textarea id="s-text" name="text" rows="6">{e(text)}</textarea>
        <p class="hilfe">Hashtags je Rubrik liefert KBS; bis dahin keine.</p></div>
        <div class="knoepfe"><button type="submit" class="knopf">Text speichern</button><button type="submit" formaction="/social/17/stoppen" class="knopf halt">Stoppen</button></div>
      </form>
      <details class="mehrteil"><summary>Regelprüfung R1 bis R9: alle erfüllt</summary><ul class="regeln">{regeln_html}</ul></details>
    </div>
    <figure class="vorschau"><div class="flaeche"><img class="foto" src="{BILD}{b['bild']}" alt="{e(b['alt'])}" width="960" height="1280"><div class="leiste-logo"><img src="{LOGO}" alt="tamil.de" width="300" height="121"></div></div>
      <figcaption>Vorschau 1080 × 1350. Ohne Social-Recht geht stattdessen die Bildkarte. {e(b['nachweis'])}</figcaption></figure>
  </div>
</section>

<section class="abschnitt" aria-labelledby="h-hand">
  <div class="kopfzeile"><h2 id="h-hand">Von Hand entscheiden</h2><p class="klein">Eine Regel ist verletzt oder unklar</p></div>
  <form id="vh-34" action="/social/34/freigeben" method="post"></form><form id="vh-31" action="/social/31/freigeben" method="post"></form>
  <ol class="brett">{vh}</ol>
</section>

<section class="abschnitt" id="whatsapp" aria-labelledby="h-wa">
  <div class="kopfzeile"><h2 id="h-wa">WhatsApp-Entwurf: Entwurf 17</h2><p class="klein">gepostet wird von Hand</p></div>
  <pre class="wa-text" id="wa-17">{e(text)}</pre>
  <div class="knoepfe" style="margin-top: var(--space-md)">
    <button type="button" class="knopf" data-kopieren="wa-17">Text kopieren</button>
    <a class="knopf still" href="{BILD}{b['bild']}" download="tamil-de-entwurf-17.jpg">Bild herunterladen</a>
    <form action="/social/17/whatsapp-gepostet" method="post"><button type="submit" class="knopf still">Als gepostet markieren</button></form>
  </div>
  <p class="klein" id="wa-meldung" role="status" style="margin-top: var(--space-xs)">Ohne Skript den Text markieren und kopieren.</p>
</section>

<section class="abschnitt" aria-labelledby="h-hist">
  <h2 id="h-hist">Historie heute je Kanal</h2>
  {hist_html}
</section>
"""
    seite("social.html", "Social", "Social-Beiträge in Karenz, von Hand zu entscheiden, WhatsApp-Entwurf, Historie je Kanal.", "social", inhalt, skript=True)


# ---------------------------------------------------------------- Verzeichnis

def verzeichnis() -> None:
    liste = [
        (frist("11:02", "heute", "2026-11-13T11:02"), "V-E-0007, neu: Restaurant AiYA, Zürich", '<span class="wort halt">Mögliche Dublette</span> von V-0012. Einsender gibt an, Inhaber zu sein.', True),
        (frist("10. Nov.", "16:45 Uhr", "2026-11-10T16:45"), "V-E-0006, Änderung: Ceylon Palace, Bremen", "Hinweis eines Lesers: Öffnungszeiten. Berechtigung: Hinweis, nicht Inhaber.", False),
    ]
    brett = "".join(zeile(f, f'<a href="verzeichnis.html">{t}</a>', x, aktuell=a) for f, t, x, a in liste)
    nh = '<span class="leise">nicht hinterlegt</span>'
    felder = [
        ("Name", "AiYA", "Restaurant AiYA", True), ("Art", "Business", "Business", True), ("Kategorie", "Restaurant", "Restaurant", True),
        ("Adresse", nh, "Beispielstrasse 1", True), ("PLZ und Stadt", "8004 Zürich", "8004 Zürich", True), ("Land, Kanton", "CH, Zürich", "CH, Zürich", True),
        ("Telefon", nh, "+41 00 000 00 00", True), ("E-Mail", nh, "aiya@example.org", False), ("Website", nh, "https://example.org", True),
        ("Öffnungszeiten", nh, "Dienstag bis Sonntag, 11 bis 22 Uhr", True),
        ("Beschreibung", "Küche aus dem Norden Sri Lankas an der Langstrasse.", "Küche aus dem Norden Sri Lankas an der Langstrasse, mittags und abends.", True),
    ]
    reihen = []
    for i, (f, alt, neu, oeff) in enumerate(felder):
        gleich = alt == neu
        neu_html = f'<span class="gleich">{neu}</span>' if gleich else f'<span class="neu">{neu}</span>'
        if gleich:
            ents = '<span class="leise">unverändert</span>'
        else:
            ents = (f'<div class="wahl"><label><input type="radio" name="f{i}" value="an" checked> annehmen</label>'
                    f'<label><input type="radio" name="f{i}" value="ab"> ablehnen</label></div>')
        reihen.append(f'<tr><th scope="row" data-l="Feld">{f}</th><td data-l="Bisher">{alt}</td><td data-l="Neu">{neu_html}</td>'
                      f'<td data-l="Öffentlich">{"ja" if oeff else "nein, nur intern"}</td><td data-l="Entscheidung">{ents}</td></tr>')
    vergleich = ('<table class="tabelle stapel"><thead><tr><th scope="col">Feld</th><th scope="col">Bisher, V-0012</th><th scope="col">Neu, V-E-0007</th>'
                 '<th scope="col">Öffentlich</th><th scope="col">Entscheidung</th></tr></thead><tbody>' + "".join(reihen) + "</tbody></table>")
    inhalt = f"""
<div class="seitenkopf"><div><h1>Verzeichnis</h1><p>Einsendungen für das Verzeichnis. Der Schalter „verzeichnis“ ist angehalten: freigegebene Einträge gehen erst nach dem Lösen auf die Website.</p></div></div>
<h2 class="visually-hidden">Einsendungen für das Verzeichnis</h2>
<nav aria-label="Filter nach Stand"><ul class="filter"><li><a href="verzeichnis.html?stand=neu" aria-current="page">Offen <span class="n">2</span></a></li><li><a href="verzeichnis.html?stand=freigegeben">Freigegeben <span class="n">13</span></a></li><li><a href="verzeichnis.html?stand=abgelehnt">Abgelehnt <span class="n">0</span></a></li></ul></nav>
<ol class="brett">{brett}</ol>

<section class="abschnitt" aria-labelledby="h-v7">
  <div class="kopfzeile"><h2 id="h-v7">V-E-0007: bisher gegen neu</h2><p class="klein">Einsender B. Beispiel, <a href="mailto:b.beispiel@example.org">b.beispiel@example.org</a>, Berechtigung: Inhaber</p></div>
  <div class="meldung fehler" role="alert" style="margin-top: var(--space-md)"><strong>Mögliche Dublette.</strong>
    <p>Eintrag V-0012 „AiYA“ in Zürich hat einen ähnlichen Namen und dieselbe PLZ. Die Einsendung wird deshalb als Änderung an V-0012 gezeigt.</p></div>
  <form action="/verzeichnis/V-E-0007" method="post">
    <fieldset><legend>Behandeln als</legend><div class="wahl"><label><input type="radio" name="als" value="aenderung" checked> Änderung an V-0012</label><label><input type="radio" name="als" value="neu"> neuer Eintrag</label></div></fieldset>
    <div style="margin-top: var(--space-md)">{vergleich}</div>
    <p class="klein" style="margin-top: var(--space-md)">Premium setzt nur der Administrator in WordPress; über Formular und Radar ist es nicht änderbar. Kategorie „Restaurant“ ist ein Vorschlag des Agenten.</p>
    <div class="knoepfe">
      <button type="submit" name="aktion" value="freigeben" class="knopf">Änderung freigeben</button>
      <button type="submit" name="aktion" value="ablehnen" class="knopf still">Ablehnen</button>
      <a class="knopf still" href="mailto:b.beispiel@example.org?subject=Ihr%20Eintrag%20im%20Verzeichnis">Von Hand antworten</a>
    </div>
  </form>
</section>
"""
    seite("verzeichnis.html", "Verzeichnis", "Verzeichnis-Einsendung: bisher gegen neu, Dublettenhinweis, Entscheidung je Feld, Freigabe.", "verzeichnis", inhalt)


# ---------------------------------------------------------------- Buchungen

def mittel(w: int, h: int, text: str, ab: bool = False) -> str:
    k = "mittel ab" if ab else "mittel"
    return f'<div class="{k}" style="width: {w // 2}px; height: {h // 2}px">{text}</div>'


def buchungen() -> None:
    liste = [
        (frist("17. Nov.", "Start in 4 Tagen", "2026-11-17", True), "B-2026-0003, Beispiel Reisen GmbH: Leaderboard, 14 Tage", "Bezahlt. Werbemittel in Prüfung; das Handy-Format weicht ab.", '<span class="wort">in Prüfung</span>', True),
        (frist("2. Nov.", "läuft", "2026-11-02"), "B-2026-0002, Beispiel Catering: Billboard, 30 Tage bis 1. Dez.", "3.412 Einblendungen, 41 Klicks bis gestern.", '<span class="wort">läuft</span>', False),
        (frist("9. Nov.", "abgelehnt", "2026-11-09"), "B-2026-0001, Beispiel Laden: Half Page, 7 Tage", '<span class="wort halt">Erstattung fehlgeschlagen.</span> Stripe meldet einen Fehler; geht an KBS.', '<span class="wort halt">Warnung</span>', False),
    ]
    brett = "".join(zeile(f, f'<a href="buchungen.html">{t}</a>', x, a, aktuell=c) for f, t, x, a, c in liste)
    angaben = [["Platz", "Leaderboard, unter der Navigation"], ["Zeitraum", "17. bis 30. November 2026, 14 Tage"], ["Firma", "Beispiel Reisen GmbH, Beispielstraße 1, 00000 Beispielstadt"],
               ["Ansprechperson", 'C. Beispiel, <a href="mailto:c.beispiel@example.org">c.beispiel@example.org</a>'], ["Ziel-Adresse", '<a href="https://example.org/angebot">example.org/angebot</a>'],
               ["Betrag", "Preis folgt (KBS)"], ["Zahlung", "bezahlt am 13. Nov., 9:15 Uhr, über Stripe"], ["Bedingungen", "angenommen, Fassung „Platzhalter, Text von KBS folgt“"]]
    angaben_html = '<table class="tabelle stapel"><thead><tr><th scope="col">Feld</th><th scope="col">Angabe</th></tr></thead><tbody>' + "".join(
        f'<tr><td data-l="Feld"><b>{k}</b></td><td data-l="Angabe">{v}</td></tr>' for k, v in angaben) + "</tbody></table>"
    stat = [["12. Nov.", "498", "6"], ["11. Nov.", "463", "5"], ["10. Nov.", "441", "7"], ["9. Nov.", "520", "4"], ["8. Nov.", "612", "9"], ["2. bis 7. Nov.", "878", "10"]]
    inhalt = f"""
<div class="seitenkopf"><div><h1>Buchungen</h1><p>Werbebuchungen von der Website. Aktiv ist eine Buchung nur, wenn sie bezahlt, freigegeben, nicht pausiert und im Zeitraum ist.</p></div></div>
<h2 class="visually-hidden">Buchungen</h2>
<nav aria-label="Filter nach Stand"><ul class="filter"><li><a href="buchungen.html?stand=alle" aria-current="page">Alle <span class="n">3</span></a></li><li><a href="buchungen.html?stand=pruefung">In Prüfung <span class="n">1</span></a></li><li><a href="buchungen.html?stand=laeuft">Läuft <span class="n">1</span></a></li><li><a href="buchungen.html?stand=pausiert">Pausiert <span class="n">0</span></a></li><li><a href="buchungen.html?stand=warnung">Warnung <span class="n">1</span></a></li></ul></nav>
<ol class="brett">{brett}</ol>

<div class="zwei abschnitt">
  <section class="spalte" aria-labelledby="h-b3">
    <div class="abschnitt">
      <div class="kopfzeile"><h2 id="h-b3">B-2026-0003: Werbemittel prüfen</h2><p class="klein">bis Montag, 16. November</p></div>
      <p class="klein" style="margin-top: var(--space-md)">Maßstäblich, halbe Größe.</p>
      <div class="masse">
        <figure>{mittel(728, 90, "Desktop 728 × 90")}<figcaption>Desktop: geliefert 728 × 90, passt. JPEG, 84 KB.</figcaption></figure>
        <figure>{mittel(320, 100, "320 × 100", ab=True)}<figcaption><span class="signal">Handy: geliefert 320 × 100, erwartet 320 × 50.</span> Wird so gestaucht oder abgeschnitten.</figcaption></figure>
      </div>
      <div style="margin-top: var(--space-xl)">{angaben_html}</div>
    </div>
  </section>
  <aside class="spalte" aria-label="Entscheidung">
    <section class="freigabe" aria-labelledby="h-entsch">
      <h2 id="h-entsch">Entscheidung</h2>
      <form action="/buchungen/B-2026-0003/pruefung" method="post">
        <fieldset><legend>Werbemittel</legend><div class="wahl"><label><input type="radio" name="pruefung" value="frei"> freigeben</label><label><input type="radio" name="pruefung" value="ab" checked> ablehnen</label></div></fieldset>
        <div class="feld"><label for="b-grund">Grund der Ablehnung, Pflicht</label><textarea id="b-grund" name="grund" required>Das Handy-Format muss 320 × 50 Pixel haben. Bitte neu hochladen.</textarea></div>
        <p class="hilfe klein" style="margin-top: var(--space-xs)">Ablehnen erstattet automatisch den vollen Betrag und gibt die Tage frei.</p>
        <div class="knoepfe"><button type="submit" class="knopf">Entscheidung speichern</button></div>
      </form>
    </section>
    <section class="abschnitt" aria-labelledby="h-warn">
      <h2 id="h-warn">Warnung B-2026-0001</h2>
      <div class="meldung fehler" role="alert" style="margin-top: var(--space-md)"><strong>Erstattung fehlgeschlagen.</strong><p>Stripe hat die Erstattung am 9. Nov. um 15:02 Uhr abgelehnt. Nichts wird wiederholt, bevor jemand den Stand bei Stripe abgeglichen hat.</p>
        <div class="knoepfe"><button type="button" class="knopf still">Abgleichen</button></div></div>
    </section>
  </aside>
</div>

<section class="abschnitt" aria-labelledby="h-stat">
  <div class="kopfzeile"><h2 id="h-stat">B-2026-0002: Einblendungen und Klicks</h2><p class="klein">ohne Cookies und ohne Personendaten</p></div>
  {tabelle(["Tag", "Einblendungen", "Klicks"], stat, zahl=(1, 2))}
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
    print("gebaut:", ", ".join(sorted(p.name for p in HIER.glob("*.html"))))
