#!/usr/bin/env python3
"""Erzeugt die App-Screens des Redaktions-Cockpits, Linie B „Kalenderblatt“ (hm-almanac).

Aufruf vom Repo-Root:  python3 design/cockpit/hm-almanac/bauen.py
Echte Werte (Entwurf 36 / Story 67, Läufe, Budget, Warteschlange, Zähler) stammen aus dem Live-Bericht vom
12.11.2026, 18:57 (Berlin). Eingang, Social, Verzeichnis und Buchungen sind Beispieldaten: die Funktionen sind
spezifiziert (datenmodell.md §12 bis §15), aber nicht gebaut.
"""
from pathlib import Path
from html import escape as e

HIER = Path(__file__).resolve().parent
LOGO = "../../inhalte/logo.png"
BILD_67 = "../../inhalte/rueckblick/bilder/rb-67.jpg"

NAV = [
    ("uebersicht", "Übersicht", None),
    ("entwurf", "Entwürfe", 65),
    ("eingang", "Eingang", 5),
    ("social", "Social", 1),
    ("verzeichnis", "Verzeichnis", 3),
    ("buchungen", "Buchungen", 1),
]
MEHR = [("/recherche", "Recherche nötig", 19), ("/warteschlange", "Warteschlange", 6), ("/kosten", "Kosten", None),
        ("/quellen", "Quellen", None), ("/protokoll", "Protokoll", None), ("/zeitplan", "Zeitplan", None),
        ("/schalter", "Schalter", None), ("/nutzer", "Benutzer", None)]

FUSS_ECHT = ("Zahlen zu Entwürfen, Recherche, Läufen, Budget und Warteschlange: Live-Bericht vom 12.11.2026, 18:57. "
             "Eingang, Social, Verzeichnis und Buchungen: Beispieldaten für die Gestaltung; Personen, Kunden, Telefon "
             "und E-Mail sind erfunden (E-Mail nur @example.org).")


def zahl(n):
    return f' <span class="num">{n}</span>' if n is not None else ""


def seite(datei, titel, beschreibung, aktiv, inhalt, js=False):
    nav = "\n".join(
        f'<li><a href="{d}.html"{" aria-current=\"page\"" if d == aktiv else ""}>{e(t)}{zahl(n)}</a></li>'
        for d, t, n in NAV)
    mehr = "\n".join(f'<li><a href="{h}">{e(t)}{zahl(n)}</a></li>' for h, t, n in MEHR)
    menue = "\n".join(
        f'<li><a href="{d}.html"{" aria-current=\"page\"" if d == aktiv else ""}><span>{e(t)}</span>{zahl(n)}</a></li>'
        for d, t, n in NAV) + "\n" + "\n".join(
        f'<li><a href="{h}"><span>{e(t)}</span>{zahl(n)}</a></li>' for h, t, n in MEHR)
    skript = '\n<script src="app.js" defer></script>' if js else ""
    html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titel)} | Redaktion tamil.de</title>
<meta name="description" content="{e(beschreibung)}">
<meta name="robots" content="noindex">
<link rel="stylesheet" href="cockpit.css">{skript}
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="kopf">
<div class="container kopf__in">
<a class="marke" href="uebersicht.html" aria-label="tamil.de Redaktion, zur Übersicht"><img src="{LOGO}" width="300" height="121" alt="tamil.de"><span>Redaktion</span></a>
<nav aria-label="Bereiche"><ul class="nav">
{nav}
<li><details class="mehr"><summary>Mehr</summary><ul>
{mehr}
</ul></details></li>
</ul></nav>
<div class="lage"><span><b>Radar läuft</b><span class="lage__lauf">, letzter Lauf <time datetime="2026-11-13T18:55">18:55</time></span></span><span class="lage__wer">Redaktion A</span><button class="btn btn--text" type="button">Abmelden</button></div>
<details class="menue"><summary>Menü</summary>
<div class="menue__panel"><nav aria-label="Bereiche, Handy"><ul>
{menue}
</ul></nav>
<p>Radar läuft, letzter Lauf <time datetime="2026-11-13T18:55">18:55</time>. Angemeldet als Redaktion A.</p>
<p><button class="btn btn--quiet" type="button">Abmelden</button></p>
</div></details>
</div>
</header>
<main id="inhalt" class="container">
{inhalt}
<footer class="fuss"><p>{FUSS_ECHT}</p></footer>
</main>
</body>
</html>
"""
    (HIER / f"{datei}.html").write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- Übersicht
LAEUFE = [  # id, Start (Berlin), gesammelt, relevant, Entwürfe, verworfen, Fehler  (Live-Bericht)
    (1600, "18:04", 75, 3), (1601, "18:07", 169, 3), (1602, "18:10", 76, 3), (1603, "18:13", 74, 3),
    (1604, "18:16", 75, 3), (1605, "18:19", 77, 3), (1606, "18:22", 81, 5), (1607, "18:25", 72, 3),
    (1608, "18:28", 86, 3), (1609, "18:31", 73, 3), (1610, "18:33", 103, 5), (1611, "18:36", 77, 3),
    (1612, "18:36", 77, 3), (1613, "18:39", 158, 3), (1614, "18:42", 72, 3), (1615, "18:45", 74, 3),
    (1616, "18:48", 73, 3), (1617, "18:49", 73, 3), (1618, "18:52", 75, 3), (1619, "18:55", 77, 3),
]


def chart(breite, hoehe, links, rechts, oben, unten, beschriftung):
    n = len(LAEUFE)
    vmax = 180
    def x(i): return links + i * (breite - links - rechts) / (n - 1)
    def y(v): return hoehe - unten - v / vmax * (hoehe - oben - unten)
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, (_, _, v, _) in enumerate(LAEUFE))
    gitter = "".join(
        f'<line class="gitter" x1="{links}" x2="{breite - rechts}" y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
        f'<text x="{links - 8}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>' for v in (50, 100, 150))
    marken = ""
    for i, (lid, zeit, v, _) in enumerate(LAEUFE):
        if lid in beschriftung:
            marken += (f'<circle class="punkt" cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.5"/>'
                       f'<text x="{x(i):.1f}" y="{y(v) - 10:.1f}" text-anchor="middle">{v}</text>')
    achse = "".join(
        f'<text class="lbl" x="{x(i):.1f}" y="{hoehe - unten + 20}" text-anchor="{a}">#{LAEUFE[i][0]}, {LAEUFE[i][1]}</text>'
        for i, a in ((0, "start"), (n - 1, "end")))
    return (f'<svg class="chart" viewBox="0 0 {breite} {hoehe}" role="img" '
            f'aria-label="Diagramm: gesammelte Meldungen je Lauf, Lauf 1600 bis 1619, meist 72 bis 86, Spitzen 169 und 158">'
            f'{gitter}<line class="achse" x1="{links}" x2="{breite - rechts}" y1="{hoehe - unten}" y2="{hoehe - unten}"/>'
            f'<polyline class="series" points="{pts}"/>{marken}{achse}</svg>')


def uebersicht():
    warten = [
        ("is-zuerst", "Social: Karenz läuft", "„Diwali in Basel“ geht um 19:04 auf Instagram. Bis dahin ändern oder stoppen.", "1", "social.html", "Ansehen", True),
        ("", "Entwürfe prüfen", "neu angelegt, warten auf Freigabe", "65", "entwurf.html", "Prüfen", False),
        ("", "Recherche nötig", "Storys mit zu wenig Belegen für einen Entwurf", "19", "/recherche", "Ansehen", False),
        ("", "Eingang", "Einsendungen, vom Agenten vorbereitet", "5", "eingang.html", "Bearbeiten", False),
        ("", "Social von Hand", "eine Regel ist verletzt oder unklar", "1", "social.html#von-hand", "Entscheiden", False),
        ("", "WhatsApp-Entwurf", "liegt zum Kopieren bereit, gepostet wird von Hand", "1", "social.html#whatsapp", "Kopieren", False),
        ("", "Verzeichnis", "eine Änderung, zwei neue Einträge, davon eine mögliche Dublette", "3", "verzeichnis.html", "Prüfen", False),
        ("", "Werbemittel prüfen", "bezahlt, wartet auf die Freigabe durch KBS", "1", "buchungen.html#pruefen", "Prüfen", False),
    ]
    zeilen = "\n".join(
        f'<tr class="{k}"><td><span class="titel">{e(t)}</span><span class="unter">{e(u)}</span>'
        f'{"<span class=\"zuerst\">zuerst</span>" if z else ""}</td>'
        f'<td class="num ecke">{n}</td><td class="aktion"><a href="{h}">{a}</a></td></tr>'
        for k, t, u, n, h, a, z in warten)
    schalter = [("alles", "jeden Kanal"), ("redaktion", "Scan, Agenten, Abrufe"), ("website", "Übertragung nach WordPress"),
                ("eingang", "Abholen der Einsendungen"), ("verzeichnis", "Verzeichnis-Einsendungen"),
                ("instagram", "Trockenmodus, keine Konten"), ("facebook", "Trockenmodus, keine Konten"), ("whatsapp", "nur Entwürfe")]
    sz = "\n".join(
        f'<tr><td><span class="titel">{k}</span><span class="unter">{u}</span></td><td class="ecke"><span class="zustand">läuft</span></td>'
        f'<td class="aktion"><a href="/schalter?kanal={k}">Anhalten</a></td></tr>' for k, u in schalter)
    laeufe = "\n".join(
        f'<tr><td class="num l" data-l="Lauf">#{lid}</td><td data-l="Start"><time datetime="2026-11-12T{z}">{z}</time></td>'
        f'<td class="num" data-l="gesammelt">{g}</td><td class="num" data-l="relevant">{r}</td>'
        f'<td class="num" data-l="Entwürfe">0</td><td class="num" data-l="Fehler">0</td></tr>'
        for lid, z, g, r in reversed(LAEUFE[-8:]))
    inhalt = f"""
<div class="seitenkopf">
<div><h1>Übersicht</h1><p>Freitag, 13. November 2026, <time datetime="2026-11-13T18:57">18:57</time></p></div>
</div>
<div class="raster">
<section class="sheet sp-7" aria-labelledby="h-warten">
<div class="sheet__head"><h2 id="h-warten">Was auf dich wartet</h2><p>nach Dringlichkeit</p></div>
<table class="tafel tafel--stapel">
<thead><tr><th scope="col">Vorgang</th><th scope="col" class="r">Anzahl</th><th scope="col" class="r">Nächster Schritt</th></tr></thead>
<tbody>
{zeilen}
</tbody>
</table>
</section>
<div class="stapel sp-5">
<section class="panel" aria-labelledby="h-schalter">
<div class="sheet__head"><h2 id="h-schalter">Stopp-Schalter</h2><p>alle laufen</p></div>
<table class="tafel tafel--dicht tafel--stapel">
<thead><tr><th scope="col">Kanal</th><th scope="col">Stand</th><th scope="col" class="r">Aktion</th></tr></thead>
<tbody>
{sz}
</tbody>
</table>
<details class="schalter-form">
<summary class="btn btn--quiet">Alles anhalten</summary>
<form class="form" data-endpoint="">
<div class="feld"><label for="grund-alles">Grund <span class="pflicht">(Pflicht)</span></label>
<textarea class="input" id="grund-alles" name="grund" maxlength="300" required aria-describedby="grund-alles-h"></textarea>
<p class="hilfe" id="grund-alles-h">Wirkt sofort auf jeden Kanal und steht mit deinem Namen im Protokoll.</p></div>
<p class="leiste"><button class="btn btn--quiet" type="submit">Jetzt anhalten</button></p>
</form>
</details>
</section>
<section class="sheet" aria-labelledby="h-budget">
<div class="sheet__head"><h2 id="h-budget">Budget</h2><p><a href="/kosten">Kosten ansehen</a></p></div>
<div class="budget">
<div class="budget__zeile"><span>Heute</span><span><span class="num">0,00</span> von <span class="num">2,00</span> USD</span><span class="budget__balken" style="--anteil: 0%"><i></i></span></div>
<div class="budget__zeile"><span>November</span><span><span class="num">0,00</span> von <span class="num">2,00</span> USD</span><span class="budget__balken" style="--anteil: 0%"><i></i></span></div>
<p class="klein muted">In den letzten 7 Tagen 104 Aufrufe im Agent-Modus und 3 Kino-Vorlagen, ohne Kosten im Budget.</p>
</div>
<dl class="dl abschnitt">
<dt>Warteschlange</dt><dd><span class="num">6</span> offen, <span class="num">0</span> laufend</dd>
<dt>Wartet auf Budget</dt><dd><span class="num">0</span></dd>
<dt>Abgebrochen</dt><dd><span class="num">0</span></dd>
<dt>Fertig</dt><dd><span class="num">31</span></dd>
</dl>
</section>
</div>
<section class="sheet sp-12" aria-labelledby="h-laeufe">
<div class="sheet__head"><h2 id="h-laeufe">Läufe</h2><p>gesammelte Meldungen je Lauf, 12.11.2026</p></div>
<figure class="chart-rahmen">
<div class="nur-gross">{chart(1000, 230, 48, 12, 24, 36, (1601, 1610, 1613))}</div>
<div class="nur-klein">{chart(360, 220, 34, 8, 24, 36, (1601, 1613))}</div>
<figcaption>Meist 72 bis 86 Meldungen je Lauf, je Lauf 3 bis 5 relevant. Aussortiert im letzten Lauf: Termin vorbei 3, ohne Bezug 10, Ausland 11, Tageslimit 3.</figcaption>
</figure>
<table class="tafel tafel--dicht tafel--stapel abschnitt tafel--schmal">
<caption>Die letzten acht Läufe</caption>
<thead><tr><th scope="col">Lauf</th><th scope="col">Start</th><th scope="col" class="r">gesammelt</th><th scope="col" class="r">relevant</th><th scope="col" class="r">Entwürfe</th><th scope="col" class="r">Fehler</th></tr></thead>
<tbody>
{laeufe}
</tbody>
</table>
<div class="leer abschnitt">
<h3>Fehler der letzten 7 Tage</h3>
<p>Keine. Übertragungs- und Modellfehler erscheinen hier mit dem betroffenen Entwurf.</p>
</div>
</section>
</div>"""
    seite("uebersicht", "Übersicht", "Was in der Redaktion von tamil.de wartet: Entwürfe, Eingang, Social, Budget und Stopp-Schalter.",
          "uebersicht", inhalt)


# ---------------------------------------------------------------- Entwurf 36 (Story 67)
ABSAETZE = [
    (None, "Rückkehr in die Schweiz: Am 20. Januar 2026 wechselte Ranjan Neelakandan leihweise zu Yverdon-Sport. Der Klub gab bekannt, dass der Angreifer bis zum Saisonende vom französischen Zweitligisten FC Annecy ausgeliehen ist. Für die tamilische Community ist der 21-Jährige besonders interessant: Er wurde in der Schweiz geboren und hat über seine Eltern sri-lankisch-tamilische Wurzeln.",
     [("C1, C2, C3, C9", "bestätigt", "Q1, Q3")], []),
    ("Vom Tessin in die Challenge League", "Geboren am 20. Januar 2005, begann Neelakandan seine Laufbahn im Tessin. Er spielte für Team Ticino, den FC Chiasso und die AC Bellinzona. Bei Chiasso stand er 2022 in zwei Ligaspielen auf dem Platz, ein Jahr später ging er zur U21 des FC Lugano.",
     [("C8, C4, C11", "bestätigt", "Q1, Q3")], []),
    (None, "Mehr Spielpraxis sammelte er in Bellinzona: Ab der Saison 2023/24 bestritt er dort dreiunddreißig Ligaspiele und erzielte zwei Tore. In der Challenge League lernte er den Profifußball kennen.",
     [("C12, C4", "bestätigt", "Q3, Q1")], []),
    ("Erste Schritte in Frankreich", "2025 wechselte Neelakandan zum FC Annecy in die Ligue 2. Der Anfang war zäh: Laut der Regionalzeitung Le Dauphiné kam er zunächst nur auf drei Spiele und 37 Minuten, sogar eine Ausleihe war im Gespräch.",
     [("C19, C16", "bestätigt", "Q3, Q2")], [("C5", "Februar 2025 als Wechselmonat (Q1)"), ("C18", "Januar als Ankunft (Q2)")]),
    (None, "Dann bekam er seine Chance. In Dijon stellte ihn Trainer Laurent Guyot erstmals in die Startelf der Ligue 2. Schon im Testspiel gegen Palermo, das Annecy 2:3 verlor, hatte er ein Tor erzielt und einen Elfmeter herausgeholt. In der Saison 2025/26 kam der Linksaußen bis zu seinem Wechsel auf fünf Einsätze in der Ligue 2 und eine Torvorlage.",
     [("C15, C17", "bestätigt", "Q2"), ("C6", "bestätigt", "Q1")], []),
    ("Junioren-Nationalspieler der Schweiz", "Neelakandan spielt auch für die Schweizer Nachwuchsauswahl. Im März 2024 lief er für die U19 in der Qualifikation zur U19-Europameisterschaft 2025 auf, Le Dauphiné bezeichnete ihn später als U20-Nationalspieler.",
     [("C13, C14", "bestätigt", "Q3, Q2")], []),
    (None, "In Yverdon sollte er die Offensive in der zweiten Saisonhälfte verstärken. Inzwischen führt ihn Wikipedia beim FC Vaduz aus Liechtenstein, der in der Schweizer Super League spielt, weiterhin als Leihspieler von Annecy, im Mittelfeld oder im Sturm. Wir von Tamil.de verfolgen seinen Weg gespannt.",
     [("C7, C10", "bestätigt", "Q1, Q3")], []),
]

CLAIMS = [
    ("C1", "was", True, "Q1", "bestätigt", "Yverdon Sport gab die Ankunft von Ranjan Neelakandan bekannt; der Angreifer ist bis Saisonende vom FC Annecy (Ligue 2) ausgeliehen."),
    ("C2", "wann", True, "Q3", "bestätigt", "Am 20. Januar 2026 kehrte Neelakandan in die Schweiz zurück und schloss sich leihweise Yverdon-Sport an."),
    ("C3", "wer", False, "Q1", "bestätigt", "Neelakandan ist 21 Jahre alt und begann seine Laufbahn in seinem Heimatkanton Tessin."),
    ("C4", "Hintergrund", False, "Q1", "bestätigt", "Er spielte nacheinander bei Team Ticino, beim FC Chiasso und bei der AC Bellinzona, wo er den Profifußball in der Challenge League kennenlernte."),
    ("C5", "wann", False, "Q1", "Widerspruch", "Im Februar 2025 unterschrieb er beim FC Annecy."),
    ("C6", "Zahl", False, "Q1", "bestätigt", "In der Saison 2025/26 kam der Linksaußen auf fünf Einsätze in der Ligue 2 und eine Torvorlage."),
    ("C7", "sonstiges", False, "Q1", "bestätigt", "Yverdon will mit ihm die Offensive für die zweite Saisonhälfte verstärken."),
    ("C8", "wer", True, "Q3", "bestätigt", "Ranjan Neelakandan, geboren am 20. Januar 2005, ist ein Schweizer Profifußballer."),
    ("C9", "wer", True, "Q3", "bestätigt", "Er wurde in der Schweiz geboren und hat über seine Eltern sri-lankisch-tamilische Wurzeln."),
    ("C10", "was", False, "Q3", "bestätigt", "Laut Wikipedia spielt er als Mittelfeldspieler oder Stürmer leihweise von Annecy beim FC Vaduz aus Liechtenstein in der Schweizer Super League."),
    ("C11", "Hintergrund", False, "Q3", "bestätigt", "Bei Chiasso begann er 2022 und kam auf zwei Ligaspiele; ein Jahr später wechselte er zur U21 des FC Lugano."),
    ("C12", "Zahl", False, "Q3", "bestätigt", "Bei Bellinzona bestritt er ab der Saison 2023/24 dreiunddreißig Ligaspiele und erzielte zwei Tore."),
    ("C13", "Hintergrund", False, "Q3", "bestätigt", "Neelakandan ist Schweizer Juniorennationalspieler; im März 2024 spielte er für die U19 in der Qualifikation zur U19-EM 2025."),
    ("C14", "wer", False, "Q2", "bestätigt", "Le Dauphiné bezeichnete ihn als Schweizer U20-Nationalspieler."),
    ("C15", "was", False, "Q2", "bestätigt", "In Dijon gab ihm Trainer Laurent Guyot seinen ersten Startelfeinsatz in der Ligue 2."),
    ("C16", "Zahl", False, "Q2", "bestätigt", "Zuvor hatte er seit seiner Ankunft in Hochsavoyen nur drei Spiele mit 37 Minuten bestritten, und es war über eine Ausleihe gesprochen worden."),
    ("C17", "was", False, "Q2", "bestätigt", "In einem Testspiel gegen Palermo (2:3-Niederlage) erzielte er ein Tor und holte einen Elfmeter heraus."),
    ("C18", "wann", False, "Q2", "Widerspruch", "Le Dauphiné nennt den Januar als Ankunft in Hochsavoyen."),
    ("C19", "wann", False, "Q3", "bestätigt", "Neelakandan wechselte 2025 zum französischen Klub Annecy."),
]


def bogen():
    teile = []
    for kopf, text, belege, widerspr in ABSAETZE:
        rand = "".join(f'<li><span class="num">{e(k)}</span> {s}, {q}</li>' for k, s, q in belege)
        rand += "".join(f'<li class="w"><span class="num">{k}</span> Widerspruch, nicht im Text: {e(g)}</li>' for k, g in widerspr)
        h = f"<h3>{e(kopf)}</h3>" if kopf else ""
        teile.append(f'<div class="absatz"><div>{h}<p>{e(text)}</p></div><ul class="rand">{rand}</ul></div>')
    return "\n".join(teile)


def entwurf(lizenz_fehlt):
    datei = "entwurf" if lizenz_fehlt else "entwurf-freigabe"
    claims = "\n".join(
        f'<tr{" class=\"is-zuerst\"" if s == "Widerspruch" else ""}><td class="num">{k}</td>'
        f'<td>{"<b>" if kern else ""}{e(a)}{"</b>" if kern else ""}</td><td data-l="Art">{art}{", Kern" if kern else ""}</td>'
        f'<td data-l="Quelle">{q}</td><td data-l="Beleg"><span class="zustand{" zustand--warten" if s == "Widerspruch" else " zustand--ruhig"}">{s}</span></td></tr>'
        for k, art, kern, q, s, a in CLAIMS)
    if lizenz_fehlt:
        werkzeug = """<div class="werkzeug" role="group" aria-label="Entscheidung">
<button class="btn btn--quiet" type="button" aria-disabled="true" aria-describedby="sperre">Freigeben</button>
<p class="grund" id="sperre"><b>Lizenz fehlt.</b> Ohne Lizenz-Datensatz geht kein Bild auf tamil.de; Freigeben und Direkt posten sind gesperrt.</p>
<div class="rechts">
<a class="btn btn--quiet" href="#lizenz">Lizenz nachtragen</a>
<button class="btn btn--quiet" type="button">Zurückstellen</button>
WEITERE
</div>
</div>"""
        bild_panel = f"""<section class="panel" id="lizenz" aria-labelledby="h-bild">
<div class="sheet__head"><h2 id="h-bild">Bild</h2><p>Wikimedia Commons</p></div>
<figure class="bild"><div class="bild__rahmen" data-slot="artikel"><img src="{BILD_67}" width="1280" height="960" alt="Das Stade Municipal in Yverdon-les-Bains, Heimstadion von Yverdon-Sport (Archivbild 2022)" loading="lazy"></div>
<figcaption>Foto: Vincenzo.togni / Wikimedia Commons, CC BY-SA 4.0</figcaption></figure>
<div class="meldung meldung--fehler lizenz-fehlt" role="status">
<p><b>Lizenz fehlt.</b> Zu diesem Bild gibt es keinen Lizenz-Datensatz. Trag ihn nach oder ersetze das Bild.</p>
<p class="klein">Die Commons-Seite nennt: Vincenzo.togni, CC BY-SA 4.0.</p>
<p class="leiste"><button class="btn btn--quiet" type="button">Commons-Angaben übernehmen</button></p>
</div>
<form class="form abschnitt" data-endpoint="" novalidate aria-labelledby="h-lizenzform">
<h3 id="h-lizenzform">Lizenz-Datensatz</h3>
<div class="feld"><label for="l-herkunft">Herkunft</label>
<select class="input" id="l-herkunft" name="herkunft"><option>Wikimedia Commons</option><option>Archiv</option><option>Bildquelle aus dem Register</option><option>eigenes Bild</option><option>Bildpool</option><option>KI-Bild</option><option>Bildkarte</option></select></div>
<div class="feld"><label for="l-inhaber">Rechteinhaber <span class="pflicht">(Pflicht)</span></label>
<input class="input" id="l-inhaber" name="rechteinhaber" autocomplete="off" required>
<p class="hilfe">Wem das Bild gehört, wie auf der Bildquelle genannt.</p></div>
<div class="feld"><label for="l-lizenz">Lizenz <span class="pflicht">(Pflicht)</span></label>
<select class="input" id="l-lizenz" name="lizenz" required aria-invalid="true" aria-describedby="l-lizenz-h"><option value="">Bitte wählen</option><option>CC BY 4.0</option><option>CC BY-SA 4.0</option><option>CC0 oder gemeinfrei</option><option>Plattformlizenz</option><option>eigene Vereinbarung</option></select>
<p class="hilfe hilfe--fehler" id="l-lizenz-h">Lizenz fehlt. Wähle sie aus der Bildquelle; NC und ND sind nicht erlaubt.</p></div>
<div class="feld"><label for="l-url">Lizenz-Adresse</label>
<input class="input" id="l-url" name="lizenz_url" type="url" inputmode="url" placeholder="https://creativecommons.org/licenses/by-sa/4.0/">
<p class="hilfe"></p></div>
<div class="feld"><label for="l-umfang">Umfang</label>
<input class="input" id="l-umfang" name="umfang" value="Online-Veröffentlichung auf tamil.de">
<p class="hilfe"></p></div>
<fieldset><legend>Nutzung in sozialen Netzen</legend>
<div class="wahl"><label><input type="radio" name="social" value="ja"><span>erlaubt</span></label><label><input type="radio" name="social" value="nein"><span>nicht erlaubt</span></label><label><input type="radio" name="social" value="offen" checked><span>ungeklärt</span></label></div>
<p class="hilfe">Ohne Recht für soziale Netze nimmt Social die Bildkarte.</p></fieldset>
<div class="feld"><label for="l-ablauf">Nutzbar bis</label>
<input class="input" id="l-ablauf" name="ablauf" type="date">
<p class="hilfe">Leer lassen, wenn die Lizenz nicht abläuft.</p></div>
<div class="feld"><label for="l-nachweis">Bildnachweis</label>
<input class="input" id="l-nachweis" name="attribution" value="Foto: Vincenzo.togni / Wikimedia Commons, CC BY-SA 4.0">
<p class="hilfe"></p></div>
<div class="feld"><label for="l-quelle">Bildquelle</label>
<input class="input" id="l-quelle" name="quelle_url" type="url" inputmode="url" value="https://commons.wikimedia.org/wiki/File:The_Stade_Municipal_of_Yverdon_in_2022.jpg">
<p class="hilfe"></p></div>
<p class="leiste"><button class="btn btn--primary" type="submit">Datensatz speichern</button><button class="btn btn--quiet" type="button">Bildkarte erzeugen</button><span class="grund">Speichern schreibt eine Protokollzeile und gibt die Freigabe frei.</span></p>
</form>
</section>"""
    else:
        werkzeug = """<div class="werkzeug" role="group" aria-label="Entscheidung">
<button class="btn btn--primary" type="button">Freigeben</button>
<button class="btn btn--quiet" type="button">Direkt posten</button>
<p class="grund">Freigegeben wird genau diese Fassung, <code>fb2bf86a</code>, Stand 1.</p>
<div class="rechts">
<button class="btn btn--quiet" type="button">Zurückstellen</button>
WEITERE
</div>
</div>"""
        bild_panel = f"""<section class="panel" id="lizenz" aria-labelledby="h-bild">
<div class="sheet__head"><h2 id="h-bild">Bild</h2><p>Wikimedia Commons</p></div>
<figure class="bild"><div class="bild__rahmen" data-slot="artikel"><img src="{BILD_67}" width="1280" height="960" alt="Das Stade Municipal in Yverdon-les-Bains, Heimstadion von Yverdon-Sport (Archivbild 2022)" loading="lazy"></div>
<figcaption>Foto: Vincenzo.togni / Wikimedia Commons, CC BY-SA 4.0</figcaption></figure>
<h3 class="abschnitt">Lizenz-Datensatz</h3>
<dl class="dl">
<dt>Herkunft</dt><dd>Wikimedia Commons</dd>
<dt>Rechteinhaber</dt><dd>Vincenzo.togni</dd>
<dt>Lizenz</dt><dd><a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="license">CC BY-SA 4.0</a></dd>
<dt>Umfang</dt><dd>Online-Veröffentlichung auf tamil.de</dd>
<dt>Soziale Netze</dt><dd>ungeklärt; Social nimmt die Bildkarte</dd>
<dt>Nutzbar bis</dt><dd>ohne Ablauf</dd>
<dt>KI-Bild</dt><dd>nein</dd>
<dt>Bildquelle</dt><dd><a href="https://commons.wikimedia.org/wiki/File:The_Stade_Municipal_of_Yverdon_in_2022.jpg">Commons-Seite öffnen</a></dd>
<dt>Eingetragen</dt><dd>13.11.2026, <time datetime="2026-11-13T18:52">18:52</time>, Redaktion A</dd>
</dl>
<p class="leiste abschnitt"><button class="btn btn--quiet" type="button">Datensatz ändern</button><button class="btn btn--quiet" type="button">Bild ersetzen</button></p>
</section>"""
    weitere = """<details class="weitere"><summary class="btn btn--quiet">Weitere</summary><div class="weitere__panel">
<a class="btn" href="/vorschau/36">Vorschau</a>
<button class="btn" type="button">In WordPress bearbeiten</button>
<button class="btn" type="button">Als Dossier recherchieren</button>
<button class="btn gefahr" type="button">Ablehnen</button>
</div></details>"""
    werkzeug = werkzeug.replace("WEITERE", weitere)
    inhalt = f"""
<p class="pfad"><a href="/">Entwürfe</a></p>
<div class="entwurfkopf">
<h1>Ranjan Neelakandan: Schweizer Talent mit tamilischen Wurzeln kehrt nach Yverdon zurück</h1>
<p class="teaser">Der 21-jährige Angreifer aus dem Tessin wechselte im Januar 2026 leihweise vom FC Annecy zu Yverdon-Sport. Sein Weg vom Tessin über Frankreich zurück in die Schweiz.</p>
<dl class="meta">
<div><dt>Stand</dt><dd><span class="zustand">neu</span></dd></div>
<div><dt>Rubrik</dt><dd>Sport</dd></div>
<div><dt>Herkunft</dt><dd>Nachtrag für den Rückblick, Ereignis 20.01.2026</dd></div>
<div><dt>Ort</dt><dd>Yverdon-les-Bains, Schweiz</dd></div>
<div><dt>Relevanz</dt><dd><span class="num">7</span></dd></div>
<div><dt>Angelegt</dt><dd>11.11.2026, <time datetime="2026-11-11T20:28">20:28</time></dd></div>
</dl>
</div>
{werkzeug}
<div class="raster abschnitt">
<div class="stapel sp-8">
<section class="panel" aria-labelledby="h-hinweise">
<div class="sheet__head"><h2 id="h-hinweise">Hinweise</h2><p>vom Gate, Faktencheck und Agent-Modus</p></div>
<ul class="hinweise">
<li class="w"><b>C5 Widerspruch</b> bleibt aus dem Text: Im Februar 2025 unterschrieb er beim FC Annecy.</li>
<li class="w"><b>C18 Widerspruch</b> bleibt aus dem Text: Le Dauphiné nennt den Januar als Ankunft in Hochsavoyen.</li>
<li><b>Länge</b> 304 Wörter; die Regel „lang“ sieht 450 bis 750 vor. Nur mit weiteren belegten Einzelheiten verlängern, nicht strecken.</li>
<li><b>Agent-Modus</b> (redakteur-r6-3): Text und Faktencheck aus der Cloud-Sitzung, Gate und Regeln vom Radar.</li>
</ul>
</section>
<section class="sheet" aria-labelledby="h-bogen">
<div class="sheet__head"><h2 id="h-bogen">Prüfbogen</h2><p>17 Claims bestätigt, 2 Widersprüche, 3 Quellen</p></div>
<div class="bogen">
<div class="bogen__kopf" aria-hidden="true"><span>Text</span><span>Belege</span></div>
{bogen()}
</div>
<div class="abschnitt">
<h3>Quellen</h3>
<table class="tafel tafel--dicht tafel--stapel">
<thead><tr><th scope="col"></th><th scope="col">Herausgeber</th><th scope="col">Art</th><th scope="col">Rechte</th><th scope="col" class="r">Datum</th></tr></thead>
<tbody>
<tr><td class="num">Q1</td><td><a href="https://www.yverdonsport.ch/ranjan-neelakandan-prete-a-ys/">Yverdon Sport FC</a></td><td data-l="Art">Volltext, Primärquelle</td><td data-l="Rechte">Zitat</td><td class="num r" data-l="Datum">20.01.2026</td></tr>
<tr><td class="num">Q2</td><td><a href="https://www.ledauphine.com/sport/2025/08/17/une-premiere-pleine-de-promesses-pour-ranjan-neelakandan-au-fc-annecy">Le Dauphiné</a></td><td data-l="Art">Volltext, Primärquelle</td><td data-l="Rechte">Zitat</td><td class="num r" data-l="Datum">17.08.2025</td></tr>
<tr><td class="num">Q3</td><td><a href="https://en.wikipedia.org/wiki/Ranjan_Neelakandan">en.wikipedia.org</a></td><td data-l="Art">Volltext, Primärquelle</td><td data-l="Rechte">Zitat</td><td class="r muted" data-l="Datum">ohne Datum</td></tr>
</tbody>
</table>
</div>
<details class="abschnitt aufklapp">
<summary class="btn btn--quiet">Alle 19 Claims</summary>
<table class="tafel tafel--dicht tafel--stapel abschnitt">
<thead><tr><th scope="col"></th><th scope="col">Aussage</th><th scope="col">Art</th><th scope="col">Quelle</th><th scope="col">Beleg</th></tr></thead>
<tbody>
{claims}
</tbody>
</table>
</details>
</section>
<section class="sheet" aria-label="Text bearbeiten"><details class="aufklapp">
<summary class="btn btn--quiet">Text bearbeiten</summary>
<form class="form form--zwei abschnitt" data-endpoint="">
<div class="feld ganz"><label for="f-titel">Überschrift</label><input class="input" id="f-titel" name="titel" maxlength="120" value="Ranjan Neelakandan: Schweizer Talent mit tamilischen Wurzeln kehrt nach Yverdon zurück"><p class="hilfe">höchstens 90 Zeichen empfohlen</p></div>
<div class="feld ganz"><label for="f-teaser">Teaser</label><textarea class="input" id="f-teaser" name="teaser" maxlength="300">Der 21-jährige Angreifer aus dem Tessin wechselte im Januar 2026 leihweise vom FC Annecy zu Yverdon-Sport. Sein Weg vom Tessin über Frankreich zurück in die Schweiz.</textarea><p class="hilfe"></p></div>
<div class="feld"><label for="f-rubrik">Rubrik</label><select class="input" id="f-rubrik" name="kategorie"><option>Sport</option><option>Community</option><option>Events</option><option>Kino</option><option>Nachrichten</option></select><p class="hilfe"></p></div>
<div class="feld"><label for="f-schlag">Schlagworte</label><input class="input" id="f-schlag" name="schlagworte" placeholder="durch Komma getrennt"><p class="hilfe"></p></div>
<div class="feld"><label for="f-seo">SEO-Titel</label><input class="input" id="f-seo" name="seo_titel" maxlength="70"><p class="hilfe">höchstens 60 Zeichen</p></div>
<div class="feld"><label for="f-alt">Alt-Text des Bildes</label><input class="input" id="f-alt" name="bild_alt" value="Das Stade Municipal in Yverdon-les-Bains, Heimstadion von Yverdon-Sport (Archivbild 2022)"><p class="hilfe"></p></div>
<p class="leiste ganz"><button class="btn btn--quiet" type="submit">Speichern</button><span class="grund">Speichern erhöht den Stand; freigegeben wird dann der neue Stand.</span></p>
</form>
</details></section>
</div>
<div class="stapel sp-4">
{bild_panel}
<section class="sheet" aria-labelledby="h-kosten">
<div class="sheet__head"><h2 id="h-kosten">Kosten und Fassungen</h2></div>
<dl class="dl">
<dt>Diese Story</dt><dd><span class="num">0,000</span> USD, 1 Aufruf</dd>
<dt>Fassung text</dt><dd><code>c3918e9d</code>, 11.11., 20:28, redakteur-r6-3</dd>
<dt>Fassung entwurf</dt><dd><code>fb2bf86a</code>, 11.11., 20:28, radar</dd>
<dt>Neu geschrieben</dt><dd>noch nie</dd>
</dl>
<details class="abschnitt">
<summary class="btn btn--quiet">Neu schreiben lassen</summary>
<form class="form abschnitt" data-endpoint="">
<div class="feld"><label for="f-anw">Anweisung</label><textarea class="input" id="f-anw" name="anweisung" placeholder="z. B. Hintergrund zur Leihe nach Vaduz ergänzen"></textarea><p class="hilfe">Kostet einen Modellaufruf aus dem Budget.</p></div>
<p class="leiste"><button class="btn btn--quiet" type="submit">Neu schreiben</button></p>
</form>
</details>
</section>
</div>
</div>"""
    titel = "Entwurf 36, Lizenz fehlt" if lizenz_fehlt else "Entwurf 36, bereit zur Freigabe"
    seite(datei, titel, "Prüfbogen zum Entwurf über Ranjan Neelakandan: Text mit Belegen je Absatz, Bild und Lizenz, Freigabe.",
          "entwurf", inhalt)


# ---------------------------------------------------------------- Eingang
def eingang():
    liste = [
        ("is-sel", "E-0141", "Termin", "Deepavali-Feier des Düsseldorf Tamil Sangam", "Einsender A, 18:42", "3 Hinweise"),
        ("", "E-0140", "Beitrag", "Frage nach einer Fortsetzung zur Tamilschule Aarau", "Einsender B, 17:58", "1 Hinweis"),
        ("", "E-0139", "Kooperation", "Vereinstermine regelmäßig melden", "Einsenderin C, 16:30", "keine Hinweise"),
        ("", "E-0138", "Werbung", "Platz auf der Startseite im Dezember", "Person D, 15:12", "1 Hinweis"),
        ("", "E-0137", "Kontakt", "Fotos vom Lichterfest einsenden", "Person E, 11:05", "keine Hinweise"),
    ]
    zeilen = "\n".join(
        f'<tr class="zeile-link {k}"{" aria-current=\"true\"" if k else ""}><td class="num">{n}</td>'
        f'<td><a class="titel" href="eingang.html?vorgang={n}">{e(b)}</a><span class="unter">{a}, {e(w)}</span></td>'
        f'<td class="ecke r"><span class="zustand zustand--ruhig">{h}</span></td></tr>'
        for k, n, a, b, w, h in liste)
    inhalt = f"""
<div class="seitenkopf">
<div><h1>Eingang</h1><p>Einsendungen von tamil.de. Der Agent prüft und bereitet vor, entschieden wird hier.</p></div>
</div>
<div class="meldung meldung--fehler" role="alert">
<p><b>Abholen fehlgeschlagen um <time datetime="2026-11-13T18:54">18:54</time>.</b> Die Website hat nicht geantwortet. Einsendungen bleiben dort liegen und gehen nicht verloren; zuletzt abgeholt um 18:51.</p>
<p class="leiste"><button class="btn btn--quiet" type="button">Erneut abholen</button></p>
</div>
<ul class="tabs abschnitt" aria-label="Filter">
<li><a href="eingang.html?stand=offen" aria-current="true">Offen <span class="num">5</span></a></li>
<li><a href="eingang.html?stand=abgeschlossen">Abgeschlossen <span class="num">0</span></a></li>
<li><a href="eingang.html?stand=spam">Spam <span class="num">1</span></a></li>
</ul>
<div class="zwei">
<div>
<table class="tafel tafel--stapel">
<caption>Offen, neueste zuerst, heute</caption>
<thead><tr><th scope="col">Vorgang</th><th scope="col">Einsendung</th><th scope="col" class="r">Prüfung</th></tr></thead>
<tbody>
{zeilen}
</tbody>
</table>
<div class="leer abschnitt">
<h2>Zuletzt abgeschlossen</h2>
<p>Noch nichts abgeschlossen.</p>
<p>Was du übernimmst, erledigst oder ablehnst, steht hier 90 Tage; danach wird es gelöscht.</p>
</div>
</div>
<section class="sheet" aria-labelledby="h-vorgang">
<div class="sheet__head"><h2 id="h-vorgang">E-2026-0141: Termin einreichen</h2><p>eingegangen 13.11.2026, <time datetime="2026-11-13T18:42">18:42</time>, vorbereitet 18:45</p></div>
<h3>Prüfung des Agenten</h3>
<ul class="hinweise">
<li class="w"><b>Pflichtfeld fehlt:</b> Uhrzeit. Nur das Datum ist angegeben.</li>
<li class="w"><b>Ort unvollständig:</b> nur die Stadt, keine Adresse.</li>
<li><b>Mögliche Dublette:</b> Story 30 (Deepavali 2026, Rückblick) nennt die Feier des Düsseldorf Tamil Sangam am 15. November.</li>
</ul>
<h3 class="abschnitt">Einsendung, wie eingegangen</h3>
<dl class="dl">
<dt>Titel</dt><dd>Deepavali-Feier des Düsseldorf Tamil Sangam</dd>
<dt>Datum und Uhrzeit</dt><dd>So 15.11.2026, <span class="fill">Uhrzeit fehlt</span></dd>
<dt>Ende</dt><dd class="muted">keine Angabe</dd>
<dt>Ort mit Adresse</dt><dd><span class="fill">Adresse fehlt</span></dd>
<dt>Stadt, Land</dt><dd>Düsseldorf, DE</dd>
<dt>Veranstalter</dt><dd>Düsseldorf Tamil Sangam</dd>
<dt>Beschreibung</dt><dd>Einladung zur Deepavali-Feier des Vereins.</dd>
<dt>Eintritt, Tickets</dt><dd class="muted">keine Angabe</dd>
<dt>Bild</dt><dd class="muted">kein Bild</dd>
<dt>Einsender</dt><dd>Einsender A, einsender.a@example.org</dd>
<dt>Einwilligung</dt><dd>ja, Fassung 1 (Text von KBS steht aus)</dd>
</dl>
<h3 class="abschnitt">Entwurf des Agenten</h3>
<p>„Deepavali-Feier des Düsseldorf Tamil Sangam am 15. November“, Typ Event, mit dem Vermerk „Angaben des Einsenders, ungeprüft“. <a href="entwurf.html">Entwurf ansehen</a></p>
<form class="form abschnitt" data-endpoint="">
<div class="feld"><label for="notiz">Notiz für die Redaktion</label><textarea class="input" id="notiz" name="notiz" placeholder="z. B. Uhrzeit beim Verein erfragt"></textarea><p class="hilfe">Bleibt intern, wird mit der Einsendung nach 90 Tagen gelöscht.</p></div>
<p class="leiste"><button class="btn btn--primary" type="button">Übernehmen</button><button class="btn btn--quiet" type="button">Erledigt</button>
<details class="weitere"><summary class="btn btn--quiet">Weitere</summary><div class="weitere__panel"><button class="btn" type="button">Als Dublette zu Story 30 markieren</button><button class="btn gefahr" type="button">Ablehnen</button><button class="btn gefahr" type="button">Als Spam</button></div></details>
<a class="btn btn--text" href="mailto:einsender.a@example.org?subject=Ihre%20Einsendung%20E-2026-0141">Im Mailprogramm antworten</a>
<span class="grund">Übernehmen legt einen Entwurf an; ab da gilt der normale Weg mit Prüfen und Freigeben. Das System schreibt dem Einsender nichts.</span></p>
</form>
</section>
</div>"""
    seite("eingang", "Eingang", "Einsendungen an tamil.de mit der Prüfung des Agenten und der Übernahme in einen Entwurf.",
          "eingang", inhalt)


# ---------------------------------------------------------------- Social
def social():
    regeln = [
        ("R1", "Rubrik", "Events"), ("R2", "Heikle Themen", "nicht heikel"), ("R3", "Alter", "Termin 21.11. liegt in der Zukunft"),
        ("R4", "Bild", "Bildkarte, Grafik: Tamil.de"), ("R5", "Menge", "heute 0 von 6"), ("R6", "Ruhezeit", "19:04 liegt außerhalb"),
        ("R7", "Dubletten", "erstmals auf Instagram"), ("R8", "Kennzeichnung", "kein KI-Bild"), ("R9", "Herkunft", "nach dem Start veröffentlicht"),
    ]
    rz = "\n".join(f'<tr><td class="num">{n}</td><td>{t}</td><td data-l="Ergebnis">erfüllt, {e(g)}</td></tr>' for n, t, g in regeln)
    wa_text = ("Diwali in Basel: Basel Tamil Sangam feiert am 21. November\n\n"
               "Der Basel Tamil Sangam lädt Familien zur Diwali-Feier in die Aula Lysbüchel ein. Mitglieder erhalten Tickets günstiger.\n\n"
               "Mehr auf tamil.de: ")
    inhalt = f"""
<div class="seitenkopf">
<div><h1>Social</h1><p>Instagram, Facebook und WhatsApp-Entwurf nach dem Regelwerk, Fassung 1</p></div>
</div>
<div class="meldung" role="status">
<p><b>Trockenmodus.</b> Die Konten von KBS fehlen, und Fassung 1 des Regelwerks wartet auf die Freigabe durch KBS. Alles läuft bis vor den Aufruf an Meta; nichts geht hinaus.</p>
</div>
<div class="raster abschnitt">
<div class="stapel sp-7">
<section class="sheet" aria-labelledby="h-karenz">
<div class="sheet__head"><h2 id="h-karenz">In der Karenz</h2><p>Instagram, danach Facebook</p></div>
<div class="karenz"><span class="num">6:42</span><span>Minuten bis <time datetime="2026-11-13T19:04">19:04</time>. Bis dahin ändern oder stoppen.</span></div>
<h3 class="abschnitt">Diwali in Basel: Basel Tamil Sangam feiert am 21. November</h3>
<p class="klein muted">Beitrag 3, veröffentlicht auf tamil.de am 13.11.2026, <time datetime="2026-11-13T18:54">18:54</time></p>
<form class="form abschnitt" data-endpoint="">
<div class="feld"><label for="s-text">Text für Instagram und Facebook</label>
<textarea class="input" id="s-text" name="text" rows="5">Diwali in Basel: Basel Tamil Sangam feiert am 21. November. Der Basel Tamil Sangam lädt Familien zur Diwali-Feier in die Aula Lysbüchel ein. Mitglieder erhalten Tickets günstiger. Mehr auf tamil.de</textarea>
<p class="hilfe">Hashtags je Rubrik: <span class="fill">liefert KBS</span>. Der Link ist bei Instagram nicht anklickbar; der Text verweist auf tamil.de.</p></div>
<p class="leiste"><button class="btn btn--primary" type="button">Stoppen</button><button class="btn btn--quiet" type="submit">Text speichern</button><span class="grund">Stoppen hält nur diesen Beitrag an, auf beiden Kanälen.</span></p>
</form>
<details class="abschnitt">
<summary class="btn btn--quiet">Regelprüfung: alle 9 erfüllt</summary>
<table class="tafel tafel--dicht tafel--stapel abschnitt">
<thead><tr><th scope="col">Regel</th><th scope="col">Was</th><th scope="col">Ergebnis</th></tr></thead>
<tbody>
{rz}
</tbody>
</table>
</details>
</section>
<section class="sheet" id="von-hand" aria-labelledby="h-hand">
<div class="sheet__head"><h2 id="h-hand">Von Hand entscheiden</h2><p>1 Beitrag</p></div>
<h3>„Ramayana: Rise of a Legend“ im Kino: 2 Spielorte in Deutschland</h3>
<ul class="hinweise">
<li class="w"><b>R3 unklar:</b> Kinotermine zählen nur in der Zukunft; die Spielzeiten in Gütersloh und Ravensburg sind im Beitrag nicht datiert.</li>
</ul>
<p class="leiste"><button class="btn btn--quiet" type="button">Trotzdem vorbereiten</button><button class="btn btn--quiet" type="button">Verwerfen</button><span class="grund">Deine Entscheidung steht mit Grund und Namen im Protokoll.</span></p>
</section>
<section class="sheet" aria-labelledby="h-historie">
<div class="sheet__head"><h2 id="h-historie">Historie</h2><p>Regelwerk Fassung 1</p></div>
<ul class="tabs" aria-label="Kanal">
<li><a href="social.html?kanal=instagram" aria-current="true">Instagram <span class="num">3</span></a></li>
<li><a href="social.html?kanal=facebook">Facebook <span class="num">3</span></a></li>
<li><a href="social.html?kanal=whatsapp">WhatsApp <span class="num">1</span></a></li>
</ul>
<table class="tafel tafel--stapel">
<thead><tr><th scope="col">Beitrag</th><th scope="col">Stand</th><th scope="col" class="r">Zeit</th></tr></thead>
<tbody>
<tr class="is-zuerst"><td><span class="titel">Diwali in Basel: Basel Tamil Sangam feiert am 21. November</span></td><td data-l="Stand"><span class="zustand zustand--warten">Karenz</span></td><td class="num ecke">19:04</td></tr>
<tr><td><span class="titel">„Scene“ im Kino: 11 Spielorte in Deutschland</span><span class="unter">60 Minuten Abstand nach dem vorigen</span></td><td data-l="Stand"><span class="zustand">geplant</span></td><td class="num ecke">20:04</td></tr>
<tr><td><span class="titel">„Ramayana: Rise of a Legend“ im Kino</span><span class="unter">R3 unklar</span></td><td data-l="Stand"><span class="zustand">von Hand</span></td><td class="num ecke muted">offen</td></tr>
</tbody>
</table>
<div class="leer abschnitt">
<h3>Veröffentlicht</h3>
<p>Noch nichts.</p>
<p>Im Trockenmodus endet jeder Beitrag vor dem Aufruf an Meta. Kennung und Link von Meta stehen hier, sobald die Konten da sind.</p>
</div>
</section>
</div>
<div class="stapel sp-5">
<section class="panel" id="whatsapp" aria-labelledby="h-wa">
<div class="sheet__head"><h2 id="h-wa">WhatsApp-Entwurf</h2><p>gepostet wird von Hand</p></div>
<div class="wa">
<div><p class="wa__text" id="wa-text">{e(wa_text)}<span class="fill">Link folgt</span></p>
<p class="leiste abschnitt"><button class="btn btn--quiet" type="button" data-kopiere="wa-text" aria-describedby="wa-h">Text kopieren</button><a class="btn btn--quiet" href="#whatsapp-bild">Bild herunterladen</a></p>
<p class="hilfe" id="wa-h" aria-live="polite"></p></div>
<figure class="bild" id="whatsapp-bild"><div class="bildkarte"><img src="{LOGO}" width="300" height="121" alt="tamil.de"><b>Diwali in Basel: Basel Tamil Sangam feiert am 21. November</b><span>Grafik: Tamil.de</span></div>
<figcaption>Bildkarte 1080 × 1350, Vorschau</figcaption></figure>
</div>
<details class="abschnitt">
<summary class="btn btn--quiet">Als gepostet markieren</summary>
<form class="form abschnitt" data-endpoint="">
<p class="klein">Erst markieren, wenn der Beitrag im WhatsApp-Kanal steht. Person und Zeit gehen ins Protokoll.</p>
<p class="leiste"><button class="btn btn--quiet" type="submit">Ja, ist gepostet</button></p>
</form>
</details>
</section>
<section class="panel" aria-labelledby="h-kanaele">
<div class="sheet__head"><h2 id="h-kanaele">Kanäle</h2><p>Stopp wirkt sofort, auch in der Karenz</p></div>
<table class="tafel tafel--dicht tafel--stapel">
<thead><tr><th scope="col">Kanal</th><th scope="col">Stand</th><th scope="col" class="r">Aktion</th></tr></thead>
<tbody>
<tr><td><span class="titel">Instagram</span><span class="unter">Trockenmodus</span></td><td class="ecke"><span class="zustand">läuft</span></td><td class="aktion"><a href="/schalter?kanal=instagram">Anhalten</a></td></tr>
<tr><td><span class="titel">Facebook</span><span class="unter">Trockenmodus</span></td><td class="ecke"><span class="zustand">läuft</span></td><td class="aktion"><a href="/schalter?kanal=facebook">Anhalten</a></td></tr>
<tr><td><span class="titel">WhatsApp</span><span class="unter">nur Entwürfe</span></td><td class="ecke"><span class="zustand">läuft</span></td><td class="aktion"><a href="/schalter?kanal=whatsapp">Anhalten</a></td></tr>
</tbody>
</table>
</section>
<section class="sheet" aria-labelledby="h-regeln">
<div class="sheet__head"><h2 id="h-regeln">Regelwerk</h2><p><a href="/social/regelwerk">Ansehen</a></p></div>
<dl class="dl">
<dt>Fassung</dt><dd>1 vom 13.11.2026</dd>
<dt>Freigabe KBS</dt><dd><span class="fill">steht aus</span></dd>
<dt>Menge</dt><dd>höchstens 6 je Kanal und Tag, 60 Minuten Abstand</dd>
<dt>Ruhezeit</dt><dd>22 bis 7 Uhr</dd>
<dt>Alter</dt><dd>höchstens 48 Stunden</dd>
<dt>Karenz</dt><dd>10 Minuten</dd>
</dl>
</section>
</div>
</div>"""
    seite("social", "Social", "Social-Beiträge von tamil.de: Karenz, Entscheidungen von Hand, Historie je Kanal und WhatsApp-Entwurf.",
          "social", inhalt, js=True)


# ---------------------------------------------------------------- Verzeichnis
def verzeichnis():
    liste = [
        ("is-sel", "V-E-031", "Änderung", "Ceylon Palace, Bremen", "Inhaber, 2 Felder geändert"),
        ("", "V-E-030", "neu", "Sri Ganesha Hindu Temple, Berlin", "mögliche Dublette von V-0004"),
        ("", "V-E-029", "neu", "Tamilischer Kultur- und Sportverein Emsdetten", "Kontaktweg fehlt"),
    ]
    zeilen = "\n".join(
        f'<tr class="zeile-link {k}"{" aria-current=\"true\"" if k else ""}><td class="num">{n}</td>'
        f'<td><a class="titel" href="verzeichnis.html?vorgang={n}">{e(b)}</a><span class="unter">{t}, {e(h)}</span></td></tr>'
        for k, n, t, b, h in liste)
    felder = [
        ("Name", "Ceylon Palace", "Ceylon Palace", False),
        ("Art, Kategorie", "Business, Restaurant", "Business, Restaurant", False),
        ("PLZ, Stadt", "28195 Bremen", "28195 Bremen", False),
        ("Telefon", "0421 0000 000", "0421 0000 001", True),
        ("Öffnungszeiten", "keine Angabe", "Di bis So, 12 bis 22 Uhr", True),
        ("Website", "ceylon-palace.example.org", "ceylon-palace.example.org", False),
    ]
    fz = []
    for i, (f, alt, neu, geaendert) in enumerate(felder):
        wahl = (f'<fieldset><legend class="visually-hidden">{f} übernehmen</legend><div class="wahl">'
                f'<label><input type="radio" name="f{i}" value="ja" checked><span>ja</span></label>'
                f'<label><input type="radio" name="f{i}" value="nein"><span>nein</span></label></div></fieldset>') if geaendert else '<span class="muted">unverändert</span>'
        fz.append(f'<tr class="{"geaendert" if geaendert else ""}"><td class="titel">{f}</td><td class="alt" data-l="Bisher">{e(alt)}</td>'
                  f'<td class="neu" data-l="Neu">{e(neu)}</td><td class="wahl-zelle">{wahl}</td></tr>')
    fz = "\n".join(fz)
    inhalt = f"""
<div class="seitenkopf">
<div><h1>Verzeichnis</h1><p>Einsendungen zu Einträgen. Öffentlich wird nur, was du freigibst.</p></div>
</div>
<ul class="tabs" aria-label="Filter">
<li><a href="verzeichnis.html?stand=offen" aria-current="true">Offen <span class="num">3</span></a></li>
<li><a href="verzeichnis.html?stand=freigegeben">Freigegeben</a></li>
<li><a href="verzeichnis.html?stand=abgelehnt">Abgelehnt</a></li>
</ul>
<div class="zwei">
<table class="tafel tafel--stapel">
<caption>Offen, neueste zuerst</caption>
<thead><tr><th scope="col">Vorgang</th><th scope="col">Eintrag</th></tr></thead>
<tbody>
{zeilen}
</tbody>
</table>
<div class="stapel">
<section class="sheet" aria-labelledby="h-aend">
<div class="sheet__head"><h2 id="h-aend">V-E-031: Änderung an Ceylon Palace</h2><p>eingegangen 13.11.2026, <time datetime="2026-11-13T17:20">17:20</time>, vom Inhaber</p></div>
<ul class="hinweise">
<li><b>Geändert:</b> Telefon und Öffnungszeiten. Alles andere bleibt.</li>
<li><b>Form geprüft:</b> Telefon mit Vorwahl, Öffnungszeiten lesbar.</li>
<li><b>Keine Dublette</b> gefunden; Kategorie bleibt Restaurant.</li>
</ul>
<form data-endpoint="">
<table class="tafel tafel--stapel vergleich abschnitt">
<caption>Bisher gegen neu, alle Felder öffentlich</caption>
<thead><tr><th scope="col">Feld</th><th scope="col">Bisher</th><th scope="col">Neu</th><th scope="col">Übernehmen</th></tr></thead>
<tbody>
{fz}
</tbody>
</table>
<dl class="dl abschnitt">
<dt>Premium</dt><dd>nein; setzt nur ein Administrator in WordPress</dd>
<dt>Einsender</dt><dd>Person F, inhaber@example.org</dd>
</dl>
<p class="leiste abschnitt"><button class="btn btn--primary" type="submit">Auswahl freigeben</button><button class="btn btn--quiet" type="button">Ablehnen</button><a class="btn btn--text" href="mailto:inhaber@example.org?subject=Ihr%20Verzeichniseintrag">Im Mailprogramm antworten</a>
<span class="grund">Freigegeben werden nur die Felder mit „ja“. Danach zeigt das Profil die neue Nummer.</span></p>
</form>
</section>
<section class="sheet" aria-labelledby="h-dub">
<div class="sheet__head"><h2 id="h-dub">V-E-030: mögliche Dublette</h2><p>ähnlicher Name, gleiche PLZ</p></div>
<table class="tafel tafel--stapel vergleich">
<thead><tr><th scope="col">Feld</th><th scope="col">Einsendung V-E-030</th><th scope="col">Eintrag V-0004</th></tr></thead>
<tbody>
<tr class="geaendert"><td class="titel">Name</td><td class="neu" data-l="Einsendung">Sri Ganesha Hindu Temple</td><td data-l="Eintrag">Sri Ganesha Hindutempel</td></tr>
<tr><td class="titel">Art</td><td data-l="Einsendung">Tempel</td><td data-l="Eintrag">Tempel</td></tr>
<tr><td class="titel">PLZ, Stadt</td><td data-l="Einsendung">10967 Berlin</td><td data-l="Eintrag">10967 Berlin</td></tr>
<tr class="geaendert"><td class="titel">Website</td><td class="neu" data-l="Einsendung">tempel-berlin.example.org</td><td class="alt" data-l="Eintrag">keine Angabe</td></tr>
</tbody>
</table>
<p class="leiste abschnitt"><button class="btn btn--quiet" type="button">Als Änderung zu V-0004 führen</button><button class="btn btn--quiet" type="button">Trotzdem neu anlegen</button><button class="btn btn--quiet" type="button">Ablehnen</button></p>
</section>
</div>
</div>"""
    seite("verzeichnis", "Verzeichnis", "Verzeichnis-Einsendungen: bisher gegen neu, Dublettenhinweis und Freigabe je Feld.",
          "verzeichnis", inhalt)


# ---------------------------------------------------------------- Buchungen
def buchungen():
    rows = [
        ("is-zuerst", "B-0012", "Startseite zwischen Rubriken", "970 × 250", "23.11. bis 06.12.", "Kunde C", "bezahlt", "offen", "in Prüfung", "zustand--warten"),
        ("", "B-0011", "unter der Navigation", "728 × 90", "09.11. bis 15.11.", "Kunde B", "bezahlt", "freigegeben", "läuft", ""),
        ("", "B-0010", "Seitenspalte", "300 × 600", "01.12. bis 30.12.", "Kunde A", "bezahlt", "freigegeben", "geplant", ""),
        ("", "B-0009", "im Artikel", "728 × 90", "16.11. bis 22.11.", "Kunde D", "offen", "offen", "reserviert bis 19:21", "zustand--ruhig"),
        ("", "B-0008", "über dem Fuß", "728 × 90", "02.11. bis 08.11.", "Kunde E", "Erstattung fehlgeschlagen", "abgelehnt", "abgelehnt", "zustand--fehler"),
        ("", "B-0007", "Handy, fest unten", "320 × 50", "26.10. bis 25.11.", "Kunde F", "bezahlt", "freigegeben", "pausiert", ""),
    ]
    zr = "\n".join(
        f'<tr class="{k}"><td class="num">{n}</td><td><span class="titel">{e(p)}</span><span class="unter">{f}</span></td>'
        f'<td data-l="Zeitraum">{z}</td><td data-l="Kunde">{c}</td><td data-l="Zahlung">{za}</td><td data-l="Prüfung">{pr}</td>'
        f'<td data-l="Stand"><span class="zustand {zk}">{s}</span></td><td data-l="Betrag"><span class="fill">Preis folgt</span></td></tr>'
        for k, n, p, f, z, c, za, pr, s, zk in rows)
    statistik = [("09.11.", "1.204", "9"), ("10.11.", "1.388", "12"), ("11.11.", "1.150", "7"), ("12.11.", "1.312", "11")]
    st = "\n".join(f'<tr><td>{t}</td><td class="num r" data-l="Einblendungen">{a}</td><td class="num r" data-l="Klicks">{b}</td></tr>' for t, a, b in statistik)
    inhalt = f"""
<div class="seitenkopf">
<div><h1>Buchungen</h1><p>Werbeplätze auf tamil.de. Aktiv ist eine Buchung nur, wenn sie bezahlt, geprüft, nicht pausiert und heute im Zeitraum ist.</p></div>
</div>
<div class="meldung meldung--fehler" role="alert">
<p><b>B-0008: Erstattung fehlgeschlagen.</b> Stripe hat die Erstattung nicht ausgeführt. Bitte im Stripe-Konto von Hand prüfen; die Tage sind wieder frei.</p>
</div>
<ul class="tabs abschnitt" aria-label="Filter">
<li><a href="buchungen.html" aria-current="true">Alle <span class="num">6</span></a></li>
<li><a href="buchungen.html?stand=pruefung">In Prüfung <span class="num">1</span></a></li>
<li><a href="buchungen.html?stand=laeuft">Läuft <span class="num">1</span></a></li>
<li><a href="buchungen.html?stand=geplant">Geplant <span class="num">1</span></a></li>
<li><a href="buchungen.html?stand=warnung">Warnungen <span class="num">1</span></a></li>
</ul>
<table class="tafel tafel--stapel">
<thead><tr><th scope="col">Nummer</th><th scope="col">Platz</th><th scope="col">Zeitraum</th><th scope="col">Kunde</th><th scope="col">Zahlung</th><th scope="col">Prüfung</th><th scope="col">Stand</th><th scope="col">Betrag</th></tr></thead>
<tbody>
{zr}
</tbody>
</table>
<div class="raster abschnitt">
<section class="sheet sp-7" id="pruefen" aria-labelledby="h-pruefen">
<div class="sheet__head"><h2 id="h-pruefen">B-0012: Werbemittel prüfen</h2><p>Startseite zwischen Rubriken, 14 Tage</p></div>
<div class="werbemittel">
<figure><div class="slot-wm slot-wm--d">Werbemittel Desktop, 970 × 250</div><figcaption>Desktop, JPEG, 182 KB</figcaption></figure>
<figure><div class="slot-wm slot-wm--m">Handy, 300 × 250</div><figcaption>Handy, JPEG, 64 KB</figcaption></figure>
</div>
<h3 class="abschnitt">Technische Prüfung</h3>
<ul class="hinweise pruef">
<li><span>Format JPEG</span><span class="zustand">passt</span></li>
<li><span>Maße Desktop 970 × 250, Handy 300 × 250</span><span class="zustand">passt</span></li>
<li><span>Zieladresse kunde-c.example.org, antwortet</span><span class="zustand">passt</span></li>
<li><span>Inhalt: Anzeige erkennbar, keine Täuschung</span><span class="zustand zustand--warten">von Hand prüfen</span></li>
</ul>
<form class="form abschnitt" data-endpoint="">
<div class="feld"><label for="b-grund">Grund bei Ablehnung</label><textarea class="input" id="b-grund" name="ablehnungsgrund" placeholder="z. B. Zieladresse führt nicht zum beworbenen Angebot"></textarea><p class="hilfe">Bei Ablehnung wird automatisch voll erstattet; die Tage werden frei.</p></div>
<p class="leiste"><button class="btn btn--primary" type="submit">Freigeben</button><button class="btn btn--quiet" type="button">Ablehnen</button></p>
</form>
</section>
<section class="sheet sp-5" aria-labelledby="h-stat">
<div class="sheet__head"><h2 id="h-stat">B-0011: Einblendungen und Klicks</h2><p>läuft bis 15.11.</p></div>
<table class="tafel tafel--dicht tafel--stapel">
<caption>Beispielwerte, gezählt ohne Cookies</caption>
<thead><tr><th scope="col">Tag</th><th scope="col" class="r">Einblendungen</th><th scope="col" class="r">Klicks</th></tr></thead>
<tbody>
{st}
</tbody>
</table>
<div class="skelett" aria-busy="true" aria-label="Heute wird geladen"><i></i><i></i></div>
<p class="klein muted">Eine Einblendung zählt, wenn die halbe Fläche eine Sekunde sichtbar war.</p>
<h3 class="abschnitt">Protokoll</h3>
<dl class="dl">
<dt>Reserviert</dt><dd>02.11., 10:14, Kunde</dd>
<dt>Bezahlt</dt><dd>02.11., 10:21, Stripe</dd>
<dt>Geprüft</dt><dd>04.11., 09:40, KBS</dd>
<dt>Gestartet</dt><dd>09.11., 00:00, Dienst</dd>
</dl>
<p class="leiste abschnitt"><button class="btn btn--quiet" type="button">Pausieren</button><button class="btn btn--quiet" type="button">Vorzeitig beenden</button></p>
</section>
</div>"""
    seite("buchungen", "Buchungen", "Werbebuchungen auf tamil.de: Liste, Prüfung des Werbemittels, Stand, Einblendungen und Klicks.",
          "buchungen", inhalt)


if __name__ == "__main__":
    uebersicht()
    entwurf(True)
    entwurf(False)
    eingang()
    social()
    verzeichnis()
    buchungen()
    print("gebaut:", ", ".join(sorted(p.name for p in HIER.glob("*.html"))))
