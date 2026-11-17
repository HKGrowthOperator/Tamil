"""Rubrik-Pool für das Theme bauen: je Rubrik vier echte Fotos als Symbolbilder (Luis, 17.11.2026: jeder Anreißer
mit Bild).

Quelle der Wahrheit ist `kandidaten.json` (Rubrik, Commons-Dateiname, Alternativtext, Bildmitte, optional ein lokales
Original aus `design/inhalte/rueckblick/bilder/`). Das Skript

1. liest Urheber, Lizenz, Lizenz-Adresse und Hinweise jeder Datei selbst aus der Commons-API (`extmetadata`), nie aus
   dem Kandidaten (Spezifikation `docs/spezifikation/bilder-und-lizenzen.md` 2.3, G2). Erlaubt: CC0, CC BY, CC BY-SA
   mit Lizenz-Adresse bei creativecommons.org; Dateien mit Hinweisen (Persönlichkeitsrecht, Marke) fallen weg;
2. lädt die Vorschau in Standardgröße (1280 px) oder nimmt das lokale Original, schneidet höchstens auf 4:3 zu
   (um die Bildmitte) und speichert 960 px breit als WebP (Qualität 78) unter
   `wordpress/themes/tamil/assets/img/rubrik/<rubrik>-<n>.webp`;
3. schreibt `bildpool.json` (mit Beleg: Abrufzeit der API), `inc/bildpool.php` und `assets/img/rubrik/NACHWEIS.md`.

Langsam und höflich: höchstens eine Anfrage alle 2,2 Sekunden, User-Agent mit Projekt, jede Antwort im
Zwischenspeicher (ein Abbruch wiederholt beim nächsten Lauf nichts). Sperrt die API (429), liest das Skript die
Angaben aus der Dateiseite selbst (HTML: Informationstabelle und die maschinenlesbaren Felder der Lizenzvorlage) und
lädt die Vorschau in einer Standardgröße von thumb.wikimedia.org.

Neben jedem Bild entsteht eine kleine Fassung `<rubrik>-<n>-320.webp` (320 px) für kleine Rahmen (srcset).

    python design/inhalte/bildpool/holen.py            # alles (API, bei 429 die Dateiseiten)
    python design/inhalte/bildpool/holen.py --html     # API auslassen: neue Dateien aus der Dateiseite, Archivbilder
                                                       # wie --archiv
    python design/inhalte/bildpool/holen.py --offline  # nur aus vorhandenem bildpool.json neu schreiben
    python design/inhalte/bildpool/holen.py --archiv   # Commons gesperrt: nur Archivbilder, Angaben aus
                                                       # rueckblick.json (dort aus der Commons-API übernommen)
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import io
import json
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

HIER = Path(__file__).resolve().parent
REPO = HIER.parents[2]
THEME = REPO / "wordpress" / "themes" / "tamil"
ZIEL = THEME / "assets" / "img" / "rubrik"
ARCHIV = REPO / "design" / "inhalte" / "rueckblick" / "bilder"
API = "https://commons.wikimedia.org/w/api.php"
UA = "tamil-de-relaunch/1.0 (bildpool; repo HKGrowthOperator/Tamil)"
RUBRIKEN = ["news", "entertainment", "events", "community", "kueche", "kino", "sport", "kultur", "allgemein"]
NAMEN = {
    "news": "Nachrichten", "entertainment": "Entertainment", "events": "Events", "community": "Community",
    "kueche": "Küche", "kino": "Kino", "sport": "Sport", "kultur": "Kultur", "allgemein": "alle übrigen",
}
LIZENZ_OK = re.compile(r"^https?://creativecommons\.org/(licenses/(by|by-sa)/[\d.]+(/[a-z-]+)?|publicdomain/zero/1\.0)/?$")
BREITE = 960
KLEIN = 320
# Standardgrößen der Vorschauen auf thumb.wikimedia.org (andere Breiten beantwortet Wikimedia mit 429)
VORSCHAU = (1280, 960)
# Zwischenspeicher für API-Antworten und Vorschauen, damit ein Abbruch (429) beim nächsten Lauf nichts wiederholt
CACHE = Path(tempfile.gettempdir()) / "tamil-bildpool"
_letzte = 0.0


def _warte() -> None:
    global _letzte
    pause = 2.2 - (time.monotonic() - _letzte)
    if pause > 0:
        time.sleep(pause)
    _letzte = time.monotonic()


def _cachedatei(url: str) -> Path:
    return CACHE / re.sub(r"[^A-Za-z0-9._-]+", "_", url)[-180:]


def holen(url: str) -> bytes:
    CACHE.mkdir(parents=True, exist_ok=True)
    datei = _cachedatei(url)
    if datei.exists():
        return datei.read_bytes()
    _warte()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 - feste Commons-Adressen
        daten = r.read()
    datei.write_bytes(daten)
    return daten


def text(wert: str) -> str:
    """HTML aus extmetadata zu Text (Urheber steht oft als Link)."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", wert or ""))).strip()


_SEITEN: dict = {}


def metadaten_vorab(titel: list[str]) -> None:
    """Angaben aller Dateien in Anfragen zu je 50 Titeln holen (schont die Commons-Grenzen)."""
    for i in range(0, len(titel), 50):
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2", "titles": "|".join(titel[i:i + 50]),
            "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1280",
        })
        daten = json.loads(holen(f"{API}?{q}"))
        abruf = dt.datetime.fromtimestamp(_cachedatei(f"{API}?{q}").stat().st_mtime, dt.timezone.utc)
        namen = {n["to"]: n["from"] for n in daten["query"].get("normalized", [])}
        for seite in daten["query"]["pages"]:
            seite["_abruf"] = abruf
            _SEITEN[namen.get(seite["title"], seite["title"])] = seite
            _SEITEN[seite["title"]] = seite


def metadaten(titel: str) -> dict:
    if titel not in _SEITEN:
        metadaten_vorab([titel])
    seite = _SEITEN[titel]
    abruf = seite["_abruf"]
    if seite.get("missing"):
        raise ValueError(f"{titel}: Datei fehlt")
    info = seite["imageinfo"][0]
    meta = info.get("extmetadata") or {}
    lizenz_url = (meta.get("LicenseUrl") or {}).get("value", "").replace("http://", "https://")
    lizenz = text((meta.get("LicenseShortName") or {}).get("value", ""))
    urheber = text((meta.get("Artist") or {}).get("value", ""))
    hinweise = text((meta.get("Restrictions") or {}).get("value", ""))
    if (meta.get("NonFree") or {}).get("value"):
        raise ValueError(f"{titel}: NonFree")
    if not LIZENZ_OK.match(lizenz_url):
        raise ValueError(f"{titel}: Lizenz nicht erlaubt ({lizenz}, {lizenz_url or 'ohne Adresse'})")
    if hinweise:
        raise ValueError(f"{titel}: Hinweise {hinweise!r}")
    if not urheber or urheber.lower() in {"unknown", "unbekannt", "anonymous"}:
        raise ValueError(f"{titel}: Urheber unbekannt")
    if "/zero/" in lizenz_url:
        lizenz = "CC0 1.0"
    return {
        "titel": seite["title"],
        "seite": info["descriptionurl"],
        "urheber": urheber,
        "lizenz": lizenz,
        "lizenz_url": lizenz_url,
        "vorschau": info.get("thumburl") or info["url"],
        "breite_original": info["width"],
        "hoehe_original": info["height"],
        "beleg": "commons-api " + abruf.strftime("%Y-%m-%dT%H:%MZ"),
    }


def seite_url(titel: str) -> str:
    return "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(titel.replace(" ", "_"), safe=":()',-._~")


def metadaten_html(titel: str) -> dict:
    """Angaben aus der Dateiseite (HTML), wenn die API sperrt: Urheber aus der Informationstabelle („Author“),
    Lizenz aus den maschinenlesbaren Feldern der Lizenzvorlage (licensetpl_short, licensetpl_link; die erste erlaubte
    gilt), Hinweise aus den Vorlagen zu Persönlichkeitsrecht, Marke und Einwilligung. Dieselben Regeln wie bei der
    API: nur CC0, CC BY, CC BY-SA; Datei mit Hinweis oder ohne Urheber fällt weg."""
    url = seite_url(titel)
    h = holen(url).decode("utf-8", "replace")
    abruf = dt.datetime.fromtimestamp(_cachedatei(url).stat().st_mtime, dt.timezone.utc)
    # Jede Lizenzvorlage schreibt erst licensetpl_link, dann licensetpl_short (unsichtbare Felder); paarweise lesen
    lizenzen, link = [], ""
    for art, wert in re.findall(r'class="licensetpl(?:&#95;|_)(link|short)"[^>]*>(.*?)</span>', h, re.S):
        if art == "link":
            link = text(wert)
        else:
            lizenzen.append((text(wert), link))
            link = ""
    lizenz, lizenz_url = next(((n, u.replace("http://", "https://").rstrip("/") + "/") for n, u in lizenzen
                               if LIZENZ_OK.match(u.replace("http://", "https://"))), ("", ""))
    if not lizenz:
        raise ValueError(f"{titel}: Lizenz nicht erlaubt ({lizenzen or 'ohne Angabe'})")
    m = re.search(r'id="fileinfotpl(?:&#95;|_)aut"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', h, re.S)
    urheber = text(m.group(1)) if m else ""
    if not urheber or urheber.lower() in {"unknown", "unbekannt", "anonymous"} or "no machine-readable" in urheber.lower():
        raise ValueError(f"{titel}: Urheber unbekannt")
    hinweise = sorted({x.lower() for x in re.findall(r"personality rights|trademark|consent|non-free", h, re.I)})
    if hinweise:
        raise ValueError(f"{titel}: Hinweise {hinweise!r}")
    masse = re.search(r'class="fileInfo">.*?([\d,.]+)\s*×\s*([\d,.]+)\s*pixels', h, re.S)
    w, hh = (int(re.sub(r"\D", "", masse.group(1))), int(re.sub(r"\D", "", masse.group(2)))) if masse else (0, 0)
    bild = re.search(r'<div class="fullImageLink" id="file"><a href="([^"]+)"[^>]*>\s*<img[^>]+src="([^"]+)"', h, re.S)
    if not bild:
        raise ValueError(f"{titel}: kein Bild auf der Dateiseite")
    original, anzeige = html.unescape(bild.group(1)).split("?")[0], html.unescape(bild.group(2)).split("?")[0]
    breite = next((b for b in VORSCHAU if b < w), 0)
    vorschau = re.sub(r"/\d+px-", f"/{breite}px-", anzeige) if "/thumb/" in anzeige and breite else original
    if "/zero/" in lizenz_url:
        lizenz = "CC0 1.0"
    return {
        "titel": titel, "seite": url, "urheber": urheber, "lizenz": lizenz, "lizenz_url": lizenz_url,
        "vorschau": vorschau, "breite_original": w, "hoehe_original": hh,
        "beleg": "commons-dateiseite " + abruf.strftime("%Y-%m-%dT%H:%MZ"),
    }


def aus_rueckblick(k: dict) -> dict:
    """Angaben eines Archivbilds aus rueckblick.json (dort beim Rückblick aus der Commons-API übernommen)."""
    daten = json.loads((ARCHIV.parent / "rueckblick.json").read_text(encoding="utf-8"))["beitraege"]
    e = next(b for b in daten if b["bild"].endswith("/" + k["archiv"]))
    m = re.match(r"^Foto: (.+) / Wikimedia Commons, (CC BY(?:-SA)? [\d.]+|CC0 1\.0)$", e["nachweis"])
    if not m:
        raise ValueError(f"{k['archiv']}: Nachweis nicht lesbar")
    art, version = m.group(2).rsplit(" ", 1)
    pfad = {"CC BY": "licenses/by", "CC BY-SA": "licenses/by-sa", "CC0": "publicdomain/zero"}[art]
    return {
        "titel": "File:" + urllib.parse.unquote(e["quelle_bild"].split("File:", 1)[1]).replace("_", " "),
        "seite": urllib.parse.quote(e["quelle_bild"], safe=":/%()',-._~"), "urheber": m.group(1), "lizenz": m.group(2),
        "lizenz_url": f"https://creativecommons.org/{pfad}/{version}/",
        "beleg": "rueckblick.json (Commons-API beim Rückblick)",
    }


def zuschneiden(im: Image.Image, fokus_y: float) -> tuple[Image.Image, float]:
    """Höchstens 4:3 hoch (um die Bildmitte), dann 960 px breit. Gibt die neue Bildmitte (y, 0..1) zurück."""
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    neu_y = fokus_y
    if h / w > 0.75:
        nh = round(w * 0.75)
        oben = min(max(0, round(fokus_y * h - nh / 2)), h - nh)
        im = im.crop((0, oben, w, oben + nh))
        neu_y = min(1.0, max(0.0, (fokus_y * h - oben) / nh))
        h = nh
    if w > BREITE:
        im = im.resize((BREITE, round(h * BREITE / w)), Image.LANCZOS)
    return im, neu_y


def bauen(kandidaten: list[dict], offline: bool, archiv: bool = False, nur_html: bool = False) -> list[dict]:
    alt = {}
    if (HIER / "bildpool.json").exists():
        alt = {b["titel"]: b for b in json.loads((HIER / "bildpool.json").read_text(encoding="utf-8"))["bilder"]}
    zaehler = {r: 0 for r in RUBRIKEN}
    bilder = []
    if not offline and not archiv and not nur_html:
        try:
            metadaten_vorab([k["titel"] for k in kandidaten])
        except urllib.error.HTTPError as f:
            if f.code != 429:
                raise
            print("Commons-API: 429 – Angaben aus den Dateiseiten, Archivbilder aus rueckblick.json")
            nur_html = True
    for k in kandidaten:
        titel = k["titel"]
        if archiv and not k.get("archiv"):
            continue
        try:
            if offline:
                m = alt[titel]
            elif archiv or (nur_html and k.get("archiv")):
                m = aus_rueckblick(k)
            elif nur_html:
                m = metadaten_html(titel)
            else:
                m = metadaten(titel)
        except urllib.error.HTTPError as f:
            if f.code == 429:
                sys.exit("Commons: 429 (zu viele Anfragen) – später erneut versuchen")
            raise
        except (ValueError, KeyError) as f:
            print("übersprungen:", f)
            continue
        zaehler[k["rubrik"]] += 1
        datei = f"{k['rubrik']}-{zaehler[k['rubrik']]}.webp"
        fy = float(k.get("fokus_y", 0.5))
        if not offline:
            roh = (ARCHIV / k["archiv"]).read_bytes() if k.get("archiv") else holen(m["vorschau"])
            im, fy = zuschneiden(Image.open(io.BytesIO(roh)), fy)
            ZIEL.mkdir(parents=True, exist_ok=True)
            im.save(ZIEL / datei, "WEBP", quality=78, method=6)
        else:
            fy = float(alt[titel].get("fokus_y_datei", fy))
        klein_schreiben(datei)
        with Image.open(ZIEL / datei) as fertig:
            w, h = fertig.size
        bilder.append({
            **{x: m[x] for x in ("titel", "seite", "urheber", "lizenz", "lizenz_url", "beleg")},
            "rubrik": k["rubrik"], "datei": datei, "w": w, "h": h, "alt": k["alt"],
            "fokus": f"50% {round(fy * 100)}%", "fokus_y_datei": round(fy, 3), "archiv": k.get("archiv", ""),
        })
        print(f"{datei:20} {m['lizenz']:14} {m['urheber'][:40]}")
    return bilder


def klein_datei(datei: str) -> str:
    return datei.replace(".webp", f"-{KLEIN}.webp")


def klein_schreiben(datei: str) -> None:
    """Kleine Fassung (320 px) für kleine Rahmen, aus der fertigen 960-px-Datei."""
    with Image.open(ZIEL / datei) as im:
        im.resize((KLEIN, round(im.height * KLEIN / im.width)), Image.LANCZOS).save(
            ZIEL / klein_datei(datei), "WEBP", quality=78, method=6)


def php_schreiben(bilder: list[dict]) -> None:
    def q(s: str) -> str:
        return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"

    zeilen = []
    breite = max(len(q(b["rubrik"])) for b in bilder)  # Pfeile untereinander (WPCS)
    for r in RUBRIKEN:
        eintraege = [b for b in bilder if b["rubrik"] == r]
        if not eintraege:
            continue
        zeilen.append(f"\t\t{q(r).ljust(breite)} => array(")
        for b in eintraege:
            felder = ", ".join(f"{q(x)} => {q(b[x]) if x not in ('w', 'h') else int(b[x])}" for x in (
                "datei", "w", "h", "alt", "urheber", "lizenz", "lizenz_url", "seite", "fokus"))
            zeilen.append(f"\t\t\tarray( {felder} ),")
        zeilen.append("\t\t),")
    php = f"""<?php
/**
 * Rubrik-Pool: je Rubrik bis zu vier echte Fotos von Wikimedia Commons (CC0, CC BY, CC BY-SA) als Symbolbilder für
 * Beiträge ohne eigenes Foto (inc/bildkette.php, Stufe d). Urheber, Lizenz und Lizenz-Adresse stammen aus Commons
 * (API oder Dateiseite; Beleg je Bild in design/inhalte/bildpool/bildpool.json). Zu jedem Bild gibt es eine kleine
 * Fassung „<datei>-320.webp“ für kleine Rahmen.
 * Erzeugt von design/inhalte/bildpool/holen.py aus kandidaten.json – nicht von Hand ändern; Nachweise auch in
 * assets/img/rubrik/NACHWEIS.md.
 */

defined( 'ABSPATH' ) || exit;

/**
 * Alle Pool-Bilder je Rubrik.
 *
 * @return array<string,array<int,array{{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}}>>
 */
function tamil_bildpool(): array {{
	// phpcs:disable WordPress.Arrays.ArrayDeclarationSpacing.AssociativeArrayFound -- Tabelle, eine Zeile je Bild
	return array(
{chr(10).join(zeilen)}
	);
	// phpcs:enable
}}

/**
 * Die Pool-Bilder, die für eine Rubrik in Frage kommen. Ohne eigenen Pool: Kino und Entertainment nehmen den Pool
 * „kino“ bzw. „events“, nie den allgemeinen (Stadtansichten, Kirchen, Rathäuser passen nicht zu Filmen und Bühnen);
 * alle übrigen den allgemeinen Pool.
 *
 * @return array<int,array{{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}}>
 */
function tamil_pool_liste( string $slug ): array {{
	$pool   = tamil_bildpool();
	$ersatz = array(
		'kino'          => array( 'kino', 'entertainment', 'events' ),
		'entertainment' => array( 'entertainment', 'events', 'kino' ),
	);
	foreach ( $ersatz[ $slug ] ?? array( $slug ) as $versuch ) {{
		if ( ! empty( $pool[ $versuch ] ) ) {{
			return $pool[ $versuch ];
		}}
	}}
	return $pool['allgemein'];
}}

/**
 * Ein Bild aus dem Pool einer Rubrik, fest nach Nummer gewählt. Auf einer Seite vergibt tamil_pool_seite() die Bilder
 * reihum, damit keines doppelt erscheint.
 *
 * @return array{{datei:string,w:int,h:int,alt:string,urheber:string,lizenz:string,lizenz_url:string,seite:string,fokus:string}}
 */
function tamil_pool_bild( string $slug, int $n = 0 ): array {{
	$liste = tamil_pool_liste( $slug );
	return $liste[ abs( $n ) % count( $liste ) ];
}}
"""
    (THEME / "inc" / "bildpool.php").write_text(php, encoding="utf-8")


def nachweis_schreiben(bilder: list[dict]) -> None:
    def tage(art: str) -> str:
        return ", ".join(sorted({b["beleg"].split()[-1][:10] for b in bilder if b["beleg"].startswith(art)}))

    teile = []
    if tage("commons-api"):
        teile.append(f"aus der Commons-API gelesen (Abruf {tage('commons-api')})")
    if tage("commons-dateiseite"):
        teile.append(f"aus der Dateiseite auf Commons gelesen (Abruf {tage('commons-dateiseite')})")
    if any(not b["beleg"].startswith("commons-") for b in bilder):
        teile.append("aus `design/inhalte/rueckblick/rueckblick.json` übernommen (dort beim Rückblick aus der Commons-API)")
    herkunft = " bzw. ".join(teile)
    zeilen = [
        "# Rubrik-Pool (Symbolbilder für Beiträge ohne eigenes Foto)",
        "",
        "Je Rubrik bis zu vier echte Fotos von Wikimedia Commons, nur CC0, CC BY und CC BY-SA; eine Rubrik ohne eigene",
        "Bilder nimmt den allgemeinen Pool. Urheber, Lizenz und Lizenz-Adresse hat `design/inhalte/bildpool/holen.py`",
        f"{herkunft}; Beleg je Bild in `design/inhalte/bildpool/bildpool.json`. Auf 960 px Breite verkleinert, höchstens",
        "auf 4:3 zugeschnitten (WebP, Qualität 78). Am Bild steht „Symbolbild“, im Fuß der volle Nachweis mit Links und",
        "„zugeschnitten“.",
        "",
        "| Datei | Rubrik | Nachweis | Lizenz | Dateiseite |",
        "|---|---|---|---|---|",
    ]
    for b in bilder:
        zeilen.append(
            f"| `{b['datei']}` | {NAMEN[b['rubrik']]} | Foto: {b['urheber']} / Wikimedia Commons, zugeschnitten | "
            f"[{b['lizenz']}]({b['lizenz_url']}) | {b['seite']} |"
        )
    (ZIEL / "NACHWEIS.md").write_text("\n".join(zeilen) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="nur aus bildpool.json neu schreiben, ohne Netz")
    ap.add_argument("--archiv", action="store_true", help="nur Archivbilder, Angaben aus rueckblick.json")
    ap.add_argument("--html", action="store_true", help="API auslassen: Angaben aus den Dateiseiten (HTML)")
    args = ap.parse_args()
    kandidaten = json.loads((HIER / "kandidaten.json").read_text(encoding="utf-8"))["kandidaten"]
    bilder = bauen(kandidaten, args.offline, args.archiv, args.html)
    fehlt = [r for r in RUBRIKEN if sum(b["rubrik"] == r for b in bilder) < 4]
    if fehlt:
        print(f"Rubriken mit weniger als vier Bildern (fallen auf „allgemein“ zurück, wenn leer): {fehlt}")
    if not any(b["rubrik"] == "allgemein" for b in bilder):
        sys.exit("Der allgemeine Pool braucht mindestens ein Bild")
    (HIER / "bildpool.json").write_text(json.dumps(
        {"hinweis": "Erzeugt von holen.py; Lizenzangaben aus der Commons-API (Beleg je Bild).", "bilder": bilder},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    php_schreiben(bilder)
    nachweis_schreiben(bilder)
    groesse = sum((ZIEL / b["datei"]).stat().st_size + (ZIEL / klein_datei(b["datei"])).stat().st_size for b in bilder)
    print(f"{len(bilder)} Bilder, {groesse / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
