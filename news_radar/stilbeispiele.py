"""Stilbeispiele aus dem Altbestand der alten tamil.de – Auswahl, Bereinigung und Zuordnung je Beitragstyp.

Die Auswahl ist wiederholbar: `python -m news_radar style --export <ordner>` liest `posts.json` und `categories.json`
eines WordPress-REST-Exports (nur Daten, nichts daraus wird ausgeführt), nimmt die Beiträge aus `AUSWAHL`, prüft jeden
gegen dieselben Mindestanforderungen wie die Kandidatenliste (`--kandidaten`) und schreibt `style_examples.json`.
Fällt ein ausgewählter Beitrag durch, bricht das Skript ab, statt still weniger Beispiele zu liefern.

Art je Beispiel: nachricht | kino | event | portraet | kueche. Die schreibende Rolle bekommt Beispiele der passenden Art
(`passende`), aufgefüllt mit Nachrichten.
"""

from __future__ import annotations

import html
import json
import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

STYLE_FILE = Path(__file__).with_name("style_examples.json")
ARTEN = ("nachricht", "kino", "event", "portraet", "kueche")
MIN_WOERTER = 300
MAX_ZEICHEN = 4000  # je Beispiel im Prompt; geschnitten an einer Absatzgrenze

# Kuratierte Auswahl (Beitrags-ID im Export → Art). Kriterien: mindestens 300 Wörter sauberer Fließtext, keine reinen
# Trailer-, Video- oder Listenbeiträge, keine Kontaktdaten Dritter, verteilt über Rubriken und Jahre; Zwischen-
# überschriften und Service-Angaben bevorzugt, weil lange Beiträge so aufgebaut sein sollen. Küche hat im Altbestand
# nur einen längeren Beitrag (Rezept mit Listen, dort sind Listen richtig).
AUSWAHL: dict[int, str] = {
    9688: "nachricht",  # Ist Sri Lanka bereit für einen Neuanfang? (2024, Zwischenüberschriften)
    9670: "nachricht",  # Kamala Harris: tamilische Wurzeln (2024, Zwischenüberschriften)
    8932: "nachricht",  # Wirtschaftskrise in Sri Lanka (2022, Zwischenüberschriften)
    8468: "nachricht",  # Hindu-Kulturzentrum Uentrop (2021, viele Zwischenüberschriften)
    4059: "nachricht",  # Tamilische Schüler im Berufskolleg Solingen (Zwischenüberschriften)
    7340: "nachricht",  # Familie Krishnapillai zurück in Hamm
    9697: "kino",       # Prashath Lokeshwarans Debüt in „Rathamaarey“ (2024, eigener Text)
    6704: "kino",       # Das Geschäft hinter Vijays „Sarkar“
    6062: "kino",       # M.I.A.-Dokumentation kommt ins Kino
    1754: "kino",       # „Bahubali“: Regisseur über den Erfolg (Zwischenüberschriften)
    6296: "event",      # IndoGerman Filmweek Berlin (Zwischenüberschriften, Service am Schluss)
    7716: "event",      # Tamilen-Wallfahrt Kevelaer (Zwischenüberschriften)
    7521: "event",      # Tempelfest in Hamm-Uentrop
    4451: "event",      # Tanzfest Nadiyamail in Biberist
    1613: "event",      # Erstes Pongal-Fest in Werne
    9118: "portraet",   # Vithya Visvendra
    1603: "portraet",   # Jeyakumar Thurairajah: Erst Papierloser, jetzt Politiker
    1652: "portraet",   # Silvia Thuraisingam: Das Flüchtlingsmädchen, das seinen Traum erkämpfte
    4711: "kueche",     # Kothu Rotti
}

_SCHLUSS_RE = re.compile(r"^(quelle|source|mehr|text|übersetzt)\s*:", re.I)
_KALENDER_RE = re.compile(r"\s@\s\d")  # Terminliste eines Kalender-Plugins („Juli 7 @ 9:00 am – 5:00 pm“)
_URL_RE = re.compile(r"https?://\S+")
_KONTAKT_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d /-]{7,}\d")
_TEILEN = {"whatsapp", "facebook", "twitter", "telegram", "linkedin", "pinterest", "e-mail", "email", "teilen"}
# Fremde Nachweise: Bildnachweise, Agenturkürzel, Autorenzeilen. Das Modell soll weder Fotografen noch Agenturen
# übernehmen; Bildnachweise stehen bei uns unter dem Bild, nie im Fließtext.
_AGENTUR = r"(?:red|dpa|kna|ots|epd|afp|ap|sda|apa|reuters|kipa|idea)"
_NACHWEIS_ABSATZ_RE = re.compile(r"^(?:\(?\s*(?:fotos?|bild(?:er)?|grafik)\s*:|©)", re.I)
_NACHWEIS_KLAMMER_RE = re.compile(r"\s*\(\s*(?:fotos?|bild(?:er)?|grafik)\s*:[^)]*\)", re.I)
_COPYRIGHT_RE = re.compile(r"\s*©[^–.]*(?:–|\.|$)")
_ORTSMARKE_RE = re.compile(rf"^[A-ZÄÖÜ][\w.\- ÄÖÜäöüß]{{0,40}}?\s*\(\s*{_AGENTUR}\s*\)\s*[–-]\s*", re.I)
_AGENTUR_ZEILE_RE = re.compile(rf"^[^.]{{0,40}}\(\s*{_AGENTUR}\s*\)$", re.I)
_AGENTUR_AM_ENDE_RE = re.compile(rf"\s+[A-ZÄÖÜ][\w\-]+(?:\s+[A-ZÄÖÜ][\w\-]+){{0,2}}\s*\(\s*{_AGENTUR}\s*\)$", re.I)
_AUTOR_RE = re.compile(r"^(?:von|text|text von|autor|autorin)\s*:?\s+[A-ZÄÖÜ][\w\-]+(?:\s+[A-ZÄÖÜ][\w\-]+){0,2}$", re.I)
_NAME_RE = re.compile(r"^[A-ZÄÖÜ][\wÄÖÜäöüß\-]+(?:\s+[A-ZÄÖÜ][\wÄÖÜäöüß\-]+){1,2}$")
_ORTSMARKE_GEKLEBT_RE = re.compile(r"^[A-ZÄÖÜ][a-zäöüß]{2,}(?=[A-ZÄÖÜ][a-zäöüß]+\s)")  # „LützelflühVor 26 Jahren“
_MEDIUM_AM_ENDE_RE = re.compile(r"(?<=[.!?»“\"])\s*\([A-ZÄÖÜ][^()]{1,40}\)$")
_EINBETTUNG = ("Share on:", "Sieh dir diesen Beitrag auf Instagram an", "A post shared by", "Ein Beitrag geteilt von")


def _klartext(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def bereinigen(inhalt_html: str) -> str:
    """Fließtext aus WordPress-HTML: Absätze getrennt, Zwischenüberschriften als „## …“, ohne Quellenzeilen, Links,
    Teilen-Knöpfe, Einbettungen und Kontaktdaten."""
    s = re.sub(r"<(script|style|iframe|figure)[^>]*>.*?</\1>", " ", inhalt_html or "", flags=re.S | re.I)
    s = re.sub(r"<h[2-4][^>]*>(.*?)</h[2-4]>", lambda m: f"\n\n## {_klartext(m.group(1))}\n\n", s, flags=re.S | re.I)
    s = re.sub(r"</(p|div|li|blockquote)>|<br\s*/?>", "\n\n", s, flags=re.I)
    absaetze = []
    for roh in s.split("\n\n"):
        text = _klartext(roh) if not roh.strip().startswith("## ") else roh.strip()
        for marke in _EINBETTUNG:
            if marke in text:
                text = text[:text.index(marke)].strip()
        if (not text or text == "##" or _SCHLUSS_RE.match(text) or text.lower().strip(" :") in _TEILEN
                or _KALENDER_RE.search(text)):
            continue
        text = _KONTAKT_RE.sub("", _URL_RE.sub("", text)).strip()
        if not text.startswith("## "):
            if (_NACHWEIS_ABSATZ_RE.match(text) or _AGENTUR_ZEILE_RE.match(text) or _AUTOR_RE.match(text)
                    or (_NAME_RE.match(text) and text.isupper())):
                continue
            text = _MEDIUM_AM_ENDE_RE.sub("", _ORTSMARKE_RE.sub("", _NACHWEIS_KLAMMER_RE.sub("", text)))
            text = _AGENTUR_AM_ENDE_RE.sub("", _ORTSMARKE_GEKLEBT_RE.sub("", text))
            text = re.sub(r"\s{2,}", " ", _COPYRIGHT_RE.sub(" ", text)).strip()
        if text and text != "##":
            absaetze.append(text)
    # Eine reine Namenszeile am Schluss ist die Autorenzeile (mitten im Text kann es eine Zwischenzeile sein)
    # Ebenso ein loses Etikett („Templefest:“), dessen Inhalt (Kalender) schon entfernt ist
    while absaetze and (_NAME_RE.match(absaetze[-1]) or (absaetze[-1].endswith(":") and len(absaetze[-1].split()) <= 3)):
        absaetze.pop()
    return "\n\n".join(absaetze)


def kuerzen(text: str, max_zeichen: int = MAX_ZEICHEN) -> str:
    """Kürzt an Absatzgrenzen und behält Einstieg und Schluss (dort stehen Kern und Service), dazwischen „[…]“."""
    if len(text) <= max_zeichen:
        return text
    absaetze = text.split("\n\n")
    schluss = absaetze[-1] if len(absaetze[-1]) < max_zeichen // 3 else ""
    budget = max_zeichen - len(schluss) - 8
    out = ""
    for absatz in absaetze[:-1] if schluss else absaetze:
        if len(out) + len(absatz) + 2 > budget:
            break
        out += ("\n\n" if out else "") + absatz
    out = out or text[:budget]
    return f"{out}\n\n[…]\n\n{schluss}" if schluss else f"{out}\n\n[…]"


def _rubriken(post: dict, kategorien: dict[int, str]) -> list[str]:
    return [kategorien.get(c, str(c)) for c in post.get("categories", [])]


def tauglich(post: dict) -> str:
    """Leer, wenn der Beitrag als Stilbeispiel taugt, sonst der Grund."""
    roh = post["content"]["rendered"]
    text = bereinigen(roh)
    woerter = len(text.split())
    if woerter < MIN_WOERTER:
        return f"nur {woerter} Wörter"
    if roh.count("<iframe") + roh.lower().count("youtube") >= 3:
        return "Videobeitrag"
    absaetze = [a for a in text.split("\n\n") if not a.startswith("## ")]
    if len(absaetze) < 3:
        return "kein gegliederter Fließtext"
    if roh.count("<li") > 5 and roh.count("<li") * 2 > len(absaetze) and "Zutaten" not in text:
        return "Listenbeitrag"
    return ""


def beispiel(post: dict, kategorien: dict[int, str], art: str) -> dict:
    text = bereinigen(post["content"]["rendered"])
    return {"id": post["id"], "title": _klartext(post["title"]["rendered"]), "art": art,
            "rubrik": ", ".join(_rubriken(post, kategorien)), "datum": (post.get("date") or "")[:10],
            "woerter": len(text.split()), "text": kuerzen(text)}


class ExportFehler(ValueError):
    """Export der alten Seite fehlt, ist kein JSON oder hat nicht die WordPress-REST-Form."""


def laden_export(ordner: Path) -> tuple[list[dict], dict[int, str]]:
    try:
        posts = json.loads((ordner / "posts.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ExportFehler(f"{ordner / 'posts.json'} fehlt") from exc
    except (OSError, ValueError) as exc:
        raise ExportFehler(f"{ordner / 'posts.json'} ist kein lesbares JSON: {exc}") from exc
    if not isinstance(posts, list) or not all(
            isinstance(p, dict) and {"id", "title", "content"} <= p.keys() for p in posts):
        raise ExportFehler(f"{ordner / 'posts.json'} hat nicht die Form eines WordPress-REST-Exports "
                           "(Liste mit id, title, content)")
    kat_datei = ordner / "categories.json"
    kategorien = {}
    if kat_datei.exists():
        try:
            kategorien = {c["id"]: html.unescape(c.get("name", ""))
                          for c in json.loads(kat_datei.read_text(encoding="utf-8"))}
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ExportFehler(f"{kat_datei} ist nicht lesbar: {exc}") from exc
    return posts, kategorien


def auswaehlen(posts: list[dict], kategorien: dict[int, str], auswahl: dict[int, str] | None = None) -> list[dict]:
    auswahl = AUSWAHL if auswahl is None else auswahl
    nach_id = {p["id"]: p for p in posts if isinstance(p, dict) and "id" in p}
    fehler, out = [], []
    for pid, art in auswahl.items():
        if art not in ARTEN:
            fehler.append(f"{pid}: unbekannte Art {art}")
        elif pid not in nach_id:
            fehler.append(f"{pid}: nicht im Export")
        elif grund := tauglich(nach_id[pid]):
            fehler.append(f"{pid}: {grund}")
        else:
            out.append(beispiel(nach_id[pid], kategorien, art))
    if fehler:
        raise ValueError("Stilbeispiele nicht tauglich: " + "; ".join(fehler))
    return out


def kandidaten(posts: list[dict], kategorien: dict[int, str]) -> list[dict]:
    """Alle tauglichen Beiträge, längste zuerst – Grundlage, um `AUSWAHL` zu ergänzen."""
    out = [{"id": p["id"], "title": _klartext(p["title"]["rendered"]), "rubrik": ", ".join(_rubriken(p, kategorien)),
            "datum": (p.get("date") or "")[:10], "woerter": len(bereinigen(p["content"]["rendered"]).split())}
           for p in posts if not tauglich(p)]
    return sorted(out, key=lambda k: -k["woerter"])


# ---- Zuordnung je Story ------------------------------------------------------------------------------------------

def art_fuer(typ: str, kategorie: str = "") -> str:
    if typ in ("event", "kino"):
        return typ
    return {"kueche": "kueche", "community": "portraet", "kino": "kino", "events": "event"}.get(kategorie or "",
                                                                                                "nachricht")


def laden(path: Path = STYLE_FILE) -> list[dict]:
    """Gespeicherte Beispiele; fehlt oder bricht die Datei, geht es ohne Beispiele weiter (mit Warnung im Log)."""
    if not path.exists():
        return []
    try:
        daten = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        log.warning("Stilbeispiele nicht lesbar (%s): %s – weiter ohne Beispiele", path.name, exc)
        return []
    if not isinstance(daten, list):
        log.warning("Stilbeispiele in %s sind keine Liste – weiter ohne Beispiele", path.name)
        return []
    return [b for b in daten if isinstance(b, dict) and b.get("title") and b.get("text")]


def passende(typ: str, kategorie: str = "", n: int = 3, path: Path = STYLE_FILE) -> list[dict]:
    """n Beispiele der passenden Art (in der Reihenfolge der Auswahl), aufgefüllt mit Nachrichten."""
    alle = laden(path)
    art = art_fuer(typ, kategorie)
    treffer = [b for b in alle if b.get("art") == art]
    rest = [b for b in alle if b.get("art") == "nachricht" and b not in treffer]
    rest += [b for b in alle if b not in treffer and b not in rest]
    return (treffer + rest)[:n]
