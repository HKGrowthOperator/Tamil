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
    return '<ul class="aufklapp-liste">' + "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in BETRIEB) + "</ul>"


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
      <span>redaktion1</span>
      <form action="/logout" method="post"><button type="submit" class="knopf still">Abmelden</button></form>
    </div>
    <details class="aufklapp menue"><summary>Menü</summary><nav aria-label="Cockpit, Menü">{menue_liste}</nav></details>
  </div>
</header>
<div class="aushang" role="status">
  <div class="aushang-innen">
    <time class="zeit" datetime="2026-11-13T14:20">14:20</time>
    <p><b>Als Nächstes geht hinaus:</b> Instagram, „{e(BEITRAG['49']['titel'])}“. Die Karenz endet in 8 Minuten. Social läuft im Trockenmodus, bis KBS das Regelwerk freigibt; nichts geht an Meta.</p>
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
