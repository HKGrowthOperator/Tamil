#!/usr/bin/env python3
"""Baut die Vergleichsseite (design/vergleich/index.html) aus den Aufnahmen und Kennzahlen der Proben.

    python3 design/vergleich/bauen.py intern klar blatt bild      # Vorschau für Luis, mit Vermerk und Kennzahlen
    python3 design/vergleich/bauen.py vorlage blatt               # Vorlage für den Auftraggeber, ohne Kennzahlen

Vorher: node design/vergleich/aufnahmen.mjs <slugs>. Die Seite wird als Artifact veröffentlicht (ohne doctype, die
Hülle setzt die Veröffentlichung). dateien.json daneben listet, welche Dateien unter welchem Pfad mitgehen.
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
             f'<div class="probe-kopf"><p class="etikett">Probe {html.escape(p["name"])}</p>'
             f'<h2 id="{slug}-titel">{html.escape(p["kurz"].split(". ")[0])}.</h2>'
             f'<p class="idee">{html.escape(p["kurz"].split(". ", 1)[1])} Familie der Vorbilder: {html.escape(p["familie"])}.</p></div>',
             '<div class="reihe handys">',
             bild(f"img/{slug}-start-handy.jpg", f"Probe {p['name']}, Startseite am Handy, erster Bildschirm", "handy", "Probe, erster Bildschirm am Handy", 780, 1688),
             bild(f"img/{slug}-start-handy-2.jpg", f"Probe {p['name']}, Startseite am Handy, zweiter Bildschirm", "handy", "Probe, zweiter Bildschirm", 780, 1688)]
    if intern:
        teile.append(bild(f"design/referenzen/img/news-{kurzname}-handy-1.jpg", f"Zum Vergleich: {marke} am Handy", "handy vergleich", f"Zum Vergleich: {marke}", 780, 1688))
    teile.append('</div><div class="reihe desktops">')
    teile.append(bild(f"img/{slug}-start-desktop.jpg", f"Probe {p['name']}, Startseite am Desktop, erster Bildschirm", "desktop", "Probe, erster Bildschirm am Desktop", 2560, 1600))
    if intern:
        teile.append(bild(f"design/referenzen/img/news-{kurzname}-desktop-1.jpg", f"Zum Vergleich: {marke} am Desktop", "desktop vergleich", f"Zum Vergleich: {marke}", 1280, 800))
    teile.append('</div>')
    if intern:
        tab, verletzt = tabelle(slug)
        teile.append(f'<h3>Gemessen: {"alle Vorgaben erfüllt" if verletzt == 0 else str(verletzt) + " Vorgabe" + ("n" if verletzt != 1 else "") + " verletzt"}</h3>{tab}')
    teile.append(f'<p class="oeffnen"><a href="design/richtungen/{slug}/index.html">Probe öffnen und selbst scrollen</a></p></section>')
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


STIL = (HIER / "seite.css").read_text(encoding="utf-8") if (HIER / "seite.css").exists() else ""


def seite(modus, slugs):
    intern = modus == "intern"
    kopf = [f'<!-- Erzeugt von design/vergleich/bauen.py ({modus}: {", ".join(slugs)}). Nicht von Hand ändern. -->',
            "<title>Richtungsvergleich tamil.de</title>",
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
                 '<p class="vorspann">Ruhig, klar und aufgeräumt, mit vielen Geschichten auf einen Blick. Die Seite zeigt echte Beiträge. '
                 "Nach der Abnahme wird diese Richtung zur vollständigen Probeseite mit allen Seitentypen ausgebaut.</p>"]
    kopf.append('<nav class="sprung" aria-label="Proben">' + "".join(f'<a href="#{s}">{html.escape(PROBEN[s]["name"])}</a>' for s in slugs)
                + ('<a href="#vorher">Vorher</a>' if intern else "") + "</nav></header>")
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
        koerper.append('<p class="fuss">Stand vom 9. November 2026. Die Beiträge stammen aus dem Archiv der Seite, das im November 2024 endet; '
                       "die Kino- und Termineinträge aus dem News-Radar. Die klickbare Probe öffnet sich im selben Fenster.</p>")
    return "\n".join(kopf + koerper + ["</div>"]) + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("intern", "vorlage"):
        sys.exit(__doc__)
    modus, slugs = sys.argv[1], sys.argv[2:]
    unbekannt = [s for s in slugs if s not in PROBEN]
    if unbekannt:
        sys.exit(f"Unbekannte Probe: {unbekannt}. Bekannt: {sorted(PROBEN)}")
    (HIER / "index.html").write_text(seite(modus, slugs), encoding="utf-8")
    karte = dateien(slugs, modus == "intern")
    fehlend = [q for q in karte.values() if not (WURZEL / q).is_file()]
    (HIER / "dateien.json").write_text(json.dumps(karte, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    groesse = sum((WURZEL / q).stat().st_size for q in karte.values() if (WURZEL / q).is_file())
    print(f"index.html ({modus}: {', '.join(slugs)}), {len(karte)} Dateien, {groesse / 1e6:.1f} MB, fehlend: {fehlend}")
