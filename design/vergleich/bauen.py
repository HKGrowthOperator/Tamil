#!/usr/bin/env python3
"""Baut die Vergleichsseite (design/vergleich/index.html) aus den Aufnahmen und Kennzahlen der Proben.

    python3 design/vergleich/bauen.py intern klar blatt bild      # Vorschau für Luis, mit Vermerk und Kennzahlen
    python3 design/vergleich/bauen.py vorlage klar                # Vorlage für den Auftraggeber, ohne Kennzahlen
    python3 design/vergleich/bauen.py vorher-nachher klar klar2   # Vorschau für Luis: alte und neue Fassung nebeneinander

Vorher: node design/vergleich/aufnahmen.mjs <slugs>. „intern“ und „vorher-nachher“ schreiben index.html und dateien.json
(dieselbe interne Seite, derselbe Link), „vorlage“ schreibt
vorlage.html und dateien-vorlage.json: zwei getrennte Artifacts, damit die Bilder fremder Nachrichtenseiten intern
bleiben. Die Seiten haben kein doctype, die Hülle setzt die Veröffentlichung.
"""
import html
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WURZEL = HIER.parent.parent
ABGELEHNT = ".claude/skills/tamil-marke/references/abgelehnt"

PROBEN = {
    "klar": {"name": "Klar", "kurz": "Nüchtern und kompakt. Schlagzeilen in einer klaren Grotesk, das Bild neben dem Text, viele Meldungen auf einen Blick.",
             "familie": "Tagesschau und BBC", "vorbild": ("BBC News", "bbc")},
    "blatt": {"name": "Blatt", "kurz": "Wie ein Qualitätsblatt. Schlagzeilen in einer Serife, alles andere serifenlos, mehr Luft und feine Linien.",
              "familie": "Zeit, Guardian und NZZ", "vorbild": ("NZZ", "nzz")},
    "bild": {"name": "Bild", "kurz": "Das Foto führt. Großes Aufmacherbild, kräftige Schlagzeile darunter, dann ein dichter Block mit weiteren Geschichten.",
             "familie": "Spiegel", "vorbild": ("Der Spiegel", "spiegel")},
}
PROBEN["klar2"] = {
    "name": "Klar", "kurz": "Klar, mit mehr Bild. Ein großes Aufmacherbild mit der Schlagzeile im Bild, ein Foto an jeder Geschichte, "
    "ein dunkler Bereich für Kino und Termine und ein Kopf, der mehr zeigt.",
    "familie": "Tagesschau und BBC, in den Bildern Spiegel", "vorbild": ("Der Spiegel", "spiegel"),
    "aenderungen": [
        ("Überall ein Bild", "Jede Meldung hat jetzt ein Foto. Zwei Beiträge, deren Bild eine Landkarte und eine Werbegrafik war, sind gegen Beiträge mit Foto getauscht."),
        ("Großes Aufmacherbild", "Das Foto der wichtigsten Geschichte ist groß, Rubrik und Schlagzeile stehen im Bild."),
        ("Kräftiger Balken", "Die Rubriken stehen in einem dunklen Band. Es bleibt beim Scrollen oben stehen."),
        ("Mehr Inhalt im Kopf", "Über dem Logo steht eine schmale Zeile mit Datum, zwei Hinweisen auf diese Woche und der Suche."),
        ("Größer und klarer", "Das Logo ist größer, die aktive Rubrik ist deutlich markiert."),
        ("Rubriken mit Bild", "Unter dem Aufmacher führt eine Reihe kleiner Bildkacheln in die Rubriken; am Handy wischt man sie zur Seite."),
        ("Dunkler Kino-Bereich", "„Diese Woche“ ist ein dunkles Band: Kino-Beiträge als große Bildkacheln, daneben Spielorte und Termine."),
        ("Bildstarke Blöcke", "Die Küche zeigt große Bildkacheln mit dem Titel im Bild, eine davon größer."),
        ("Sanfte Bewegung", "Bilder zoomen leicht, wenn man mit der Maus darüberfährt. Nichts bewegt sich von selbst."),
    ],
}


def _zweite(m):
    liste = m.get("schriftgroessen_seite") or []
    return round(liste[1]["px"]) if len(liste) > 1 else None


# Grenzen für klar2 (Brief, Abschnitt 10.4): (Bezeichnung, Wert aus Kennzahlen einer Breite und der ganzen Probe, Grenze, Prüfung Handy, Prüfung Desktop)
ZIELE_KLAR2 = [
    ("Schlagzeilen im ersten Bildschirm", lambda m, k: m["schlagzeilen_ganz_sichtbar"], "Handy mind. 2, Desktop mind. 4", lambda v: v >= 2, lambda v: v >= 4),
    ("Geschichten ohne Bild", lambda m, k: len(m["anreisser_ohne_bild"]) if "anreisser_ohne_bild" in m else None, "keine", lambda v: v == 0, lambda v: v == 0),
    ("Größte Schrift (Schlagzeile des Aufmachers)", lambda m, k: round(m["groesste_schrift"]["px"]), "höchstens 34 / 44 px", lambda v: v <= 34, lambda v: v <= 44),
    ("Zweitgrößte Schrift der Seite", lambda m, k: _zweite(m), "höchstens 24 / 28 px", lambda v: v is not None and v <= 24, lambda v: v is not None and v <= 28),
    ("Rot in der Fläche (ohne Bilder)", lambda m, k: round(m["farbanteil_ohne_bilder"]["rot"] * 100, 1), "höchstens 3 %", lambda v: v <= 3, lambda v: v <= 3),
    ("Größte rote Schrift", lambda m, k: round(m["groesste_rote_schrift"]["px"]), "höchstens 20 px", lambda v: v <= 20, lambda v: v <= 20),
    ("Dunkle Flächen auf der Seite", lambda m, k: len(m["dunkle_flaechen"]) if "dunkle_flaechen" in m else None, "genau 2 (Rubrikband, „Diese Woche“)", lambda v: v == 2, lambda v: v == 2),
    ("Dunkel im ersten Bildschirm (ohne Bilder)", lambda m, k: round(m["farbanteil_ohne_bilder"].get("dunkel", 0) * 100, 1), "höchstens 12 %", lambda v: v <= 12, lambda v: v <= 12),
    ("Helle Schrift auf Bild oder Dunkel, kleinster Kontrast", lambda m, k: (m.get("helle_schrift") or {}).get("kleinster_kontrast"), "mindestens 4,5 : 1", lambda v: v is not None and v >= 4.5, lambda v: v is not None and v >= 4.5),
    ("Kopf bis Unterkante Rubrikband", lambda m, k: m.get("kopfleiste_hoehe"), "am Handy höchstens 152 px", lambda v: v is not None and v <= 152, lambda v: True),
    ("Zoom beim Überfahren", lambda m, k: k.get("groesster_massstab"), "höchstens 1,04", lambda v: v is not None and v <= 1.04, lambda v: v is not None and v <= 1.04),
    ("Längster Übergang", lambda m, k: (m.get("bewegung") or {}).get("laengster_uebergang_s"), "höchstens 0,4 s", lambda v: v is not None and v <= 0.4, lambda v: v is not None and v <= 0.4),
    ("Übergänge bei „Bewegung reduzieren“, Animationen", lambda m, k: (m.get("bewegung_bei_reduziert") or {}).get("uebergaenge", 0) + (m.get("bewegung") or {}).get("animationen", 0), "keine", lambda v: v == 0, lambda v: v == 0),
    ("Größte Rundung", lambda m, k: m["groesster_radius"]["px"], "höchstens 2 px", lambda v: v <= 2, lambda v: v <= 2),
    ("Schatten, Drehungen, verstellte Schriftbreite", lambda m, k: m["schatten"] + m["gedreht"] + m["schriftbreite_verstellt"], "keine", lambda v: v == 0, lambda v: v == 0),
    ("Bilder über ihrer Dateibreite", lambda m, k: len(m["bilder_ueber_dateibreite"]) if "bilder_ueber_dateibreite" in m else None, "keine", lambda v: v == 0, lambda v: v == 0),
]

ZIELE = [  # (Bezeichnung, Schlüssel-Funktion Handy/Desktop, Ziel-Text, Prüfung Handy, Prüfung Desktop, Marken-Spanne)
    ("Schlagzeilen im ersten Bildschirm", lambda m: m["schlagzeilen_ganz_sichtbar"], "Handy mind. 2, Desktop mind. 4",
     lambda v: v >= 2, lambda v: v >= 4, "1–3 / 0–4"),
    ("Größte Schrift", lambda m: round(m["groesste_schrift"]["px"]), "höchstens 32 / 38 px",
     lambda v: v <= 32, lambda v: v <= 38, "18–32 / 18–36 px"),
    ("Rot in der Fläche (ohne Bilder)", lambda m: round(m["farbanteil_ohne_bilder"]["rot"] * 100, 1), "höchstens 3 %",
     lambda v: v <= 3, lambda v: v <= 3, "meist unter 8 % Farbe"),
    ("Größte rote Schrift", lambda m: round(m["groesste_rote_schrift"]["px"]), "höchstens 20 px",
     lambda v: v <= 20, lambda v: v <= 20, "–"),
    ("Kopf mit Logo und Rubriken", lambda m: m.get("kopfleiste_hoehe"), "am Handy höchstens 120 px",
     lambda v: v is not None and v <= 120, lambda v: True, "–"),
    ("Größte Rundung", lambda m: m["groesster_radius"]["px"], "höchstens 2 px",
     lambda v: v <= 2, lambda v: v <= 2, "0–1,5 px"),
    ("Schatten, Drehungen, verstellte Schriftbreite", lambda m: m["schatten"] + m["gedreht"] + m["schriftbreite_verstellt"], "keine",
     lambda v: v == 0, lambda v: v == 0, "keine"),
]


def zahl(wert):
    return "–" if wert is None else str(wert).replace(".", ",")


def kennzahlen(slug):
    datei = HIER / "kennzahlen" / f"{slug}.json"
    return json.loads(datei.read_text(encoding="utf-8")) if datei.exists() else None


def runde4(funktion, breite):
    werte = [funktion(k[breite]) for k in (kennzahlen(s) for s in ("zine", "raster", "feed")) if k and breite in k]
    werte = [w for w in werte if w is not None]
    return "–" if not werte else (zahl(min(werte)) if min(werte) == max(werte) else f"{zahl(min(werte))}–{zahl(max(werte))}")


def tabelle(slug):
    k = kennzahlen(slug)
    if not k or "handy" not in k or "desktop" not in k:
        return '<p class="leise">Kennzahlen fehlen.</p>', 0
    zeilen, verletzt = [], 0
    for name, wert, ziel, ok_h, ok_d, marken in ZIELE:
        h, d = wert(k["handy"]), wert(k["desktop"])
        gut = ok_h(h) and ok_d(d)
        verletzt += 0 if gut else 1
        zeilen.append(
            f'<tr><th scope="row">{html.escape(name)}</th><td>{zahl(h)} / {zahl(d)}</td>'
            f'<td class="{"gut" if gut else "schlecht"}">{"erfüllt" if gut else "verletzt"}</td>'
            f'<td>{html.escape(ziel)}</td><td>{html.escape(marken)}</td>'
            f'<td>{runde4(wert, "handy")} / {runde4(wert, "desktop")}</td></tr>')
    kopf = ('<thead><tr><th scope="col">Messwert</th><th scope="col">Probe (Handy / Desktop)</th><th scope="col">Ergebnis</th>'
            '<th scope="col">Vorgabe</th><th scope="col">Echte Marken</th><th scope="col">Abgelehnte Skizzen</th></tr></thead>')
    return f'<div class="tabellenrahmen"><table>{kopf}<tbody>{"".join(zeilen)}</tbody></table></div>', verletzt


def bild(src, alt, klasse, unterschrift, w, h):
    return (f'<figure class="aufnahme {klasse}"><img src="{src}" width="{w}" height="{h}" alt="{html.escape(alt)}">'
            f'<figcaption>{html.escape(unterschrift)}</figcaption></figure>')


def abschnitt(slug, intern):
    p = PROBEN[slug]
    marke, kurzname = p["vorbild"]
    teile = [f'<section class="probe" id="{slug}" aria-labelledby="{slug}-titel">',
             f'<div class="probe-kopf"><p class="etikett">{"Probe" if intern else "Richtung"} {html.escape(p["name"])}</p>'
             f'<h2 id="{slug}-titel">{html.escape(p["kurz"].split(". ")[0])}.</h2>'
             f'<p class="idee">{html.escape(p["kurz"].split(". ", 1)[1])} Vorbilder dieser Richtung: {html.escape(p["familie"])}.</p></div>',
             '<div class="reihe handys">',
             bild(f"img/{slug}-start-handy.jpg", f"{p['name']}, Startseite am Handy, erster Bildschirm", "handy", "Startseite am Handy, erster Bildschirm", 780, 1688),
             bild(f"img/{slug}-start-handy-2.jpg", f"{p['name']}, Startseite am Handy, zweiter Bildschirm", "handy", "Startseite am Handy, weiter unten", 780, 1688)]
    if not intern and (HIER / "img" / f"{slug}-woche-handy.jpg").exists():
        teile.append(bild(f"img/{slug}-woche-handy.jpg", f"{p['name']}, Kino und Termine am Handy", "handy", "Diese Woche: Kino und Termine", 780, 1688))
    if not intern and (HIER / "img" / f"{slug}-artikel-handy.jpg").exists():
        teile.append(bild(f"img/{slug}-artikel-handy.jpg", f"{p['name']}, Artikel am Handy", "handy", "Artikel am Handy", 780, 1688))
    if intern:
        teile.append(bild(f"design/referenzen/img/news-{kurzname}-handy-1.jpg", f"Zum Vergleich: {marke} am Handy", "handy vergleich", f"Zum Vergleich: {marke}", 780, 1688))
    teile.append('</div><div class="reihe desktops">')
    teile.append(bild(f"img/{slug}-start-desktop.jpg", f"{p['name']}, Startseite am Desktop, erster Bildschirm", "desktop", "Startseite am Desktop, erster Bildschirm", 2560, 1600))
    if intern:
        teile.append(bild(f"design/referenzen/img/news-{kurzname}-desktop-1.jpg", f"Zum Vergleich: {marke} am Desktop", "desktop vergleich", f"Zum Vergleich: {marke}", 1280, 800))
    if not intern:
        for teil, text in (("woche-desktop", "Diese Woche: Kino und Termine am Desktop"), ("kueche-desktop", "Küche am Desktop")):
            if (HIER / "img" / f"{slug}-{teil}.jpg").exists():
                teile.append(bild(f"img/{slug}-{teil}.jpg", f"{p['name']}, {text}", "desktop", text, 2560, 1600))
    teile.append('</div>')
    if intern:
        tab, verletzt = tabelle(slug)
        teile.append(f'<h3>Gemessen: {"alle Vorgaben erfüllt" if verletzt == 0 else str(verletzt) + " Vorgabe" + ("n" if verletzt != 1 else "") + " verletzt"}</h3>{tab}')
    links = [f'<a href="design/richtungen/{slug}/index.html">Startseite öffnen und selbst scrollen</a>']
    if (WURZEL / "design" / "richtungen" / slug / "artikel.html").exists():
        links.append(f'<a href="design/richtungen/{slug}/artikel.html">Artikel öffnen</a>')
    teile.append(f'<p class="oeffnen">{" ".join(links)}</p></section>')
    return "\n".join(teile)


def dateien(slugs, intern):
    karte = {}
    for slug in slugs:
        ordner = WURZEL / "design" / "richtungen" / slug
        for f in sorted(ordner.rglob("*")):
            rel = f.relative_to(WURZEL).as_posix()
            if not f.is_file() or "/shots/" in rel or f.name == "begruendung.md" or f.name.startswith(("_", ".")):
                continue
            karte[rel] = rel
            if f.suffix in (".html", ".css"):
                for m in re.findall(r"\.\./\.\./(inhalte/[A-Za-z0-9_./\-]+)", f.read_text(encoding="utf-8")):
                    karte[f"design/{m}"] = f"design/{m}"
        for f in sorted((HIER / "img").glob(f"{slug}-*.jpg")):
            karte[f"img/{f.name}"] = f.relative_to(WURZEL).as_posix()
        if intern:
            kurzname = PROBEN[slug]["vorbild"][1]
            for teil in ("handy-1", "desktop-1"):
                rel = f"design/referenzen/img/news-{kurzname}-{teil}.jpg"
                karte[rel] = rel
    if intern:
        for name in ("r2-community-magazin-390.jpg", "r4-raster-390.jpg", "r4-feed-390.jpg"):
            karte[f"img/abgelehnt-{name}"] = f"{ABGELEHNT}/{name}"
    return karte


def tabelle_vorher_nachher(alt, neu):
    ka, kn = kennzahlen(alt), kennzahlen(neu)
    if not kn or "handy" not in kn or "desktop" not in kn:
        return '<p class="leise">Kennzahlen fehlen.</p>', 0

    def wert(funktion, k, breite):
        try:
            return funktion(k[breite], k) if k and breite in k else None
        except (KeyError, TypeError):
            return None
    zeilen, verletzt = [], 0
    for name, funktion, grenze, ok_h, ok_d in ZIELE_KLAR2:
        h, d = wert(funktion, kn, "handy"), wert(funktion, kn, "desktop")
        gut = h is not None and d is not None and ok_h(h) and ok_d(d)
        verletzt += 0 if gut else 1
        zeilen.append(
            f'<tr><th scope="row">{html.escape(name)}</th><td>{zahl(h)} / {zahl(d)}</td>'
            f'<td class="{"gut" if gut else "schlecht"}">{"eingehalten" if gut else "verletzt"}</td>'
            f'<td>{html.escape(grenze)}</td><td>{zahl(wert(funktion, ka, "handy"))} / {zahl(wert(funktion, ka, "desktop"))}</td></tr>')
    kopf = ('<thead><tr><th scope="col">Messwert</th><th scope="col">Neu (Handy / Desktop)</th><th scope="col">Ergebnis</th>'
            '<th scope="col">Grenze</th><th scope="col">Vorher (Handy / Desktop)</th></tr></thead>')
    return f'<div class="tabellenrahmen"><table>{kopf}<tbody>{"".join(zeilen)}</tbody></table></div>', verletzt


def seite_vorher_nachher(alt, neu):
    p = PROBEN[neu]

    def da(slug, teil):
        return (HIER / "img" / f"{slug}-{teil}.jpg").exists()

    def handy(slug, teil, text, vorher=False):
        return bild(f"img/{slug}-{teil}.jpg", text, "handy vergleich" if vorher else "handy", text, 780, 1688) if da(slug, teil) else ""

    def desktop(slug, teil, text, vorher=False):
        return bild(f"img/{slug}-{teil}.jpg", text, "desktop vergleich" if vorher else "desktop", text, 2560, 1600) if da(slug, teil) else ""

    tab, verletzt = tabelle_vorher_nachher(alt, neu)
    sprung = [("start", "Erster Blick"), ("unten", "Weiter unten"), ("woche", "Kino und Termine"), ("kueche", "Küche"),
              ("artikel", "Artikel"), ("geaendert", "Was neu ist"), ("gemessen", "Gemessen")]
    teile = [f'<!-- Erzeugt von design/vergleich/bauen.py (vorher-nachher: {alt}, {neu}). Nicht von Hand ändern. -->',
             "<title>Richtungsvergleich tamil.de</title>", '<meta name="claude:viewport-fit-sides" content="cover">',
             f"<style>\n{STIL}</style>", '<div class="rahmen">', '<header class="kopf">',
             '<p class="vermerk">Interne Vorschau · nicht für den Auftraggeber</p>',
             "<h1>Klar mit mehr Wow: vorher und nachher</h1>",
             '<p class="vorspann">Deine Rückmeldung zur ersten Fassung: gut vom Design, aber noch zu classic; mehr Wow, überall ein Bild, '
             "der Kopf zu schlicht. Die neue Fassung behält Schrift, Farben und die Ordnung der Nachrichten und legt Bild und Bühne dazu. "
             "Zu sehen ist jeweils zuerst der alte Stand, dann der neue.</p>",
             '<nav class="sprung" aria-label="Abschnitte">' + "".join(f'<a href="#{a}">{html.escape(t)}</a>' for a, t in sprung) + "</nav>",
             f'<p class="oeffnen"><a href="design/richtungen/{neu}/index.html">Neue Startseite öffnen und selbst scrollen</a> '
             f'<a href="design/richtungen/{neu}/artikel.html">Neuen Artikel öffnen</a> '
             f'<a href="design/richtungen/{alt}/index.html">Alte Startseite zum Vergleich</a></p>',
             "</header>",
             '<section class="probe" id="start" aria-labelledby="start-titel"><div class="probe-kopf"><p class="etikett">Erster Blick</p>'
             '<h2 id="start-titel">Der erste Bildschirm, am Handy und am Desktop.</h2>'
             '<p class="idee">Neu: eine Zeile mit Datum und Hinweisen über dem Logo, das dunkle Band mit den Rubriken und das große '
             "Foto mit der Schlagzeile im Bild.</p></div>",
             '<div class="reihe handys">' + handy(alt, "start-handy", "Vorher: Startseite am Handy", True) + handy(neu, "start-handy", "Neu: Startseite am Handy") + "</div>",
             '<div class="reihe desktops">' + desktop(alt, "start-desktop", "Vorher: Startseite am Desktop", True) + desktop(neu, "start-desktop", "Neu: Startseite am Desktop") + "</div></section>",
             '<hr class="trenner">',
             '<section class="probe" id="unten" aria-labelledby="unten-titel"><div class="probe-kopf"><p class="etikett">Weiter unten</p>'
             '<h2 id="unten-titel">Jede Geschichte hat jetzt ein Bild.</h2>'
             '<p class="idee">Vorher standen die Meldungen als reine Textliste. Das dunkle Band bleibt beim Scrollen oben stehen.</p></div>',
             '<div class="reihe handys">' + handy(alt, "start-handy-2", "Vorher: am Handy weiter unten", True) + handy(neu, "start-handy-2", "Neu: zweiter Bildschirm am Handy")
             + handy(neu, "start-handy-3", "Neu: dritter Bildschirm am Handy") + "</div></section>",
             '<hr class="trenner">',
             '<section class="probe" id="woche" aria-labelledby="woche-titel"><div class="probe-kopf"><p class="etikett">Diese Woche</p>'
             '<h2 id="woche-titel">Kino und Termine im dunklen Bereich.</h2>'
             '<p class="idee">Die Kino-Beiträge sind große Bildkacheln. Spielorte und Termine kommen aus dem News-Radar und haben kein Foto; '
             "sie stehen als gestaltete Kacheln daneben, ohne erfundenes Bild.</p></div>",
             '<div class="reihe desktops">' + desktop(neu, "woche-desktop", "Neu: Diese Woche am Desktop") + "</div>",
             '<div class="reihe handys">' + handy(neu, "woche-handy", "Neu: Diese Woche am Handy") + "</div></section>",
             '<hr class="trenner">',
             '<section class="probe" id="kueche" aria-labelledby="kueche-titel"><div class="probe-kopf"><p class="etikett">Küche</p>'
             '<h2 id="kueche-titel">Große Bildkacheln statt vier gleicher Karten.</h2></div>',
             '<div class="reihe desktops">' + desktop(neu, "kueche-desktop", "Neu: Küche am Desktop") + "</div></section>",
             '<hr class="trenner">',
             '<section class="probe" id="artikel" aria-labelledby="artikel-titel"><div class="probe-kopf"><p class="etikett">Artikel</p>'
             '<h2 id="artikel-titel">Der Artikel: derselbe Kopf, das Bild groß, der Text ruhig.</h2></div>',
             '<div class="reihe handys">' + handy(alt, "artikel-handy", "Vorher: Artikel am Handy", True) + handy(neu, "artikel-handy", "Neu: Artikel am Handy") + "</div></section>",
             '<hr class="trenner">',
             '<section class="probe" id="geaendert" aria-labelledby="geaendert-titel"><div class="probe-kopf"><p class="etikett">Was neu ist</p>'
             '<h2 id="geaendert-titel">Deine Punkte, einer nach dem anderen.</h2></div><dl class="punkte">'
             + "".join(f"<div><dt>{html.escape(a)}</dt><dd>{html.escape(b)}</dd></div>" for a, b in p.get("aenderungen", [])) + "</dl></section>",
             '<hr class="trenner">',
             '<section class="probe" id="gemessen" aria-labelledby="gemessen-titel"><div class="probe-kopf"><p class="etikett">Gemessen</p>'
             f'<h2 id="gemessen-titel">{"Alle Grenzen eingehalten." if verletzt == 0 else str(verletzt) + (" Grenze" if verletzt == 1 else " Grenzen") + " verletzt."}</h2>'
             '<p class="idee">Mehr Wow darf nicht wieder laut werden. Deshalb hat jede Verstärkung eine Grenze, die das Skript nachmisst: '
             "Rot bleibt ein kleiner Akzent, die Schrift bleibt gedeckelt, dunkel sind nur zwei Flächen.</p></div>" + tab + "</section>",
             '<hr class="trenner">',
             '<section class="abschluss" aria-label="Rückmeldung"><div><h2>Was ich von dir brauche</h2><ol>'
             "<li>Passt das Wow jetzt, oder ist es immer noch zu classic?</li>"
             "<li>Ist etwas zu viel geworden?</li><li>Fehlt etwas?</li></ol></div>"
             "<div><h2>Wie es weitergeht</h2><ul>"
             "<li>Die neue Fassung wird unabhängig geprüft; was die Prüfung findet, wird eingearbeitet.</li>"
             "<li>Der Auftraggeber bekommt sie erst, wenn du zustimmst und kein schwerer Befund offen ist.</li></ul></div></section>",
             '<p class="fuss">Stand vom 10. November 2026. Die Beiträge stammen aus dem Archiv der Seite, das im November 2024 endet; die Kino- '
             "und Termineinträge aus dem News-Radar. Das Logo liegt bisher nur als kleines Bild vor. Die klickbaren Seiten öffnen sich im "
             "selben Fenster; zurück geht es mit der Zurück-Taste.</p>",
             "</div>"]
    return "\n".join(t for t in teile if t) + "\n"


STIL = (HIER / "seite.css").read_text(encoding="utf-8") if (HIER / "seite.css").exists() else ""


def seite(modus, slugs):
    intern = modus == "intern"
    kopf = [f'<!-- Erzeugt von design/vergleich/bauen.py ({modus}: {", ".join(slugs)}). Nicht von Hand ändern. -->',
            f"<title>{'Richtungsvergleich tamil.de' if intern else 'Redesign tamil.de'}</title>",
            '<meta name="claude:viewport-fit-sides" content="cover">',
            f"<style>\n{STIL}</style>", '<div class="rahmen">', '<header class="kopf">']
    if intern:
        kopf += ['<p class="vermerk">Interne Vorschau · noch ohne unabhängige Prüfung · nicht für den Auftraggeber</p>',
                 "<h1>Drei Proben: tamil.de wie eine große Nachrichtenmarke</h1>",
                 '<p class="vorspann">Ruhig statt laut, Rot nur als kleiner Akzent, normale Schrift, viele Geschichten auf einen Blick. '
                 "Alle drei zeigen dieselben echten Beiträge und nur die Startseite. Gesucht ist die eine Probe, die weiter ausgearbeitet wird, "
                 "oder eine Mischung, zum Beispiel die Schrift der einen mit dem Aufmacher der anderen.</p>"]
    else:
        kopf += ['<p class="etikett">Redesign tamil.de · Abnahme der Richtung</p>', "<h1>tamil.de wie eine große Nachrichtenmarke</h1>",
                 '<p class="vorspann">Ruhig, klar und aufgeräumt: ein deutlicher Aufmacher und viele Geschichten auf einen Blick. '
                 "Rot bleibt die Farbe des Logos und kleiner Marken, die Schrift ist ruhig und gut lesbar. Zu sehen sind die Startseite "
                 "und ein Artikel mit echten Beiträgen. Gefragt ist, ob diese Richtung stimmt.</p>"]
    if intern or len(slugs) > 1:
        kopf.append('<nav class="sprung" aria-label="Proben">' + "".join(f'<a href="#{s}">{html.escape(PROBEN[s]["name"])}</a>' for s in slugs)
                    + ('<a href="#vorher">Vorher</a>' if intern else "") + "</nav>")
    kopf.append("</header>")
    koerper = ['\n<hr class="trenner">\n'.join(abschnitt(s, intern) for s in slugs)]
    if intern:
        koerper.append('<hr class="trenner"><section class="probe" id="vorher" aria-label="Die abgelehnten Stände"><div class="probe-kopf">'
                       '<p class="etikett">Zum Vergleich</p><h2>So sah es vorher aus.</h2>'
                       '<p class="idee">Links der Stand, der als „altbacken“ durchfiel. Daneben zwei der Skizzen von heute, die als zu rot, zu laut '
                       "und wie aus dem Baukasten durchfielen. Die neuen Proben sollen von beidem deutlich Abstand halten.</p></div>"
                       '<div class="reihe handys">'
                       + bild("img/abgelehnt-r2-community-magazin-390.jpg", "Abgelehnt: Community-Magazin, Handy", "handy vergleich", "Abgelehnt: Community-Magazin („altbacken“)", 390, 844)
                       + bild("img/abgelehnt-r4-raster-390.jpg", "Abgelehnt: Skizze Raster, Handy", "handy vergleich", "Abgelehnt: Skizze Raster", 780, 1688)
                       + bild("img/abgelehnt-r4-feed-390.jpg", "Abgelehnt: Skizze Feed, Handy", "handy vergleich", "Abgelehnt: Skizze Feed", 780, 1688)
                       + "</div></section>")
        koerper.append('<p class="fuss">Die Bilder zeigen den Stand vom 9. November 2026. Die Beiträge stammen aus dem Archiv der Seite, das im '
                       "November 2024 endet; die Kino- und Termineinträge aus dem News-Radar. Die Bilder der Nachrichtenseiten dienen nur dem "
                       "internen Vergleich. Die klickbaren Proben öffnen sich im selben Fenster; zurück geht es mit der Zurück-Taste.</p>")
    else:
        koerper.append('<hr class="trenner"><section class="abschluss" aria-label="Entscheidung"><div><h2>Was für die Entscheidung gebraucht wird</h2><ol>'
                       "<li>Stimmt die Richtung: ja, nein oder ja mit Änderungen.</li>"
                       "<li>Was gefällt und was stört, gern in Stichworten.</li></ol></div>"
                       "<div><h2>Wie es danach weitergeht</h2><ul>"
                       "<li>Die Richtung wird zur Probeseite mit allen Seitentypen ausgebaut: Start, Artikel, Rubrik, Events, Kinoliste, Kontakt.</li>"
                       "<li>Erst nach der Abnahme der Probeseite wird die echte Website umgebaut.</li></ul></div></section>")
        koerper.append('<p class="fuss">Stand vom 10. November 2026. Die Beiträge stammen aus dem Archiv der Seite, das im November 2024 endet; '
                       "die Kino- und Termineinträge aus dem News-Radar. Das Logo liegt bisher nur als kleines Bild vor; mit einer "
                       "Vektordatei wird es schärfer. Die klickbaren Seiten öffnen sich im selben Fenster; zurück geht es mit der Zurück-Taste.</p>")
    return "\n".join(kopf + koerper + ["</div>"]) + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("intern", "vorlage", "vorher-nachher"):
        sys.exit(__doc__)
    modus, slugs = sys.argv[1], sys.argv[2:]
    if modus == "vorher-nachher" and len(slugs) != 2:
        sys.exit("vorher-nachher braucht genau zwei Proben: <alt> <neu>")
    unbekannt = [s for s in slugs if s not in PROBEN]
    if unbekannt:
        sys.exit(f"Unbekannte Probe: {unbekannt}. Bekannt: {sorted(PROBEN)}")
    ziel, liste = ("vorlage.html", "dateien-vorlage.json") if modus == "vorlage" else ("index.html", "dateien.json")
    (HIER / ziel).write_text(seite_vorher_nachher(*slugs) if modus == "vorher-nachher" else seite(modus, slugs), encoding="utf-8")
    karte = dateien(slugs, modus == "intern")
    fehlend = [q for q in karte.values() if not (WURZEL / q).is_file()]
    (HIER / liste).write_text(json.dumps(karte, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    groesse = sum((WURZEL / q).stat().st_size for q in karte.values() if (WURZEL / q).is_file())
    print(f"{ziel} ({modus}: {', '.join(slugs)}), {len(karte)} Dateien, {groesse / 1e6:.1f} MB, fehlend: {fehlend}")
