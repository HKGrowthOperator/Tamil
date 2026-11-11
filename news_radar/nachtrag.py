"""Nachtrag (Rückblick): eine Story aus einem Vorschlag mit Quellen anlegen – ohne Scan, ohne Modell, ohne Kosten.

  POST /api/agent/vorschlag  (Bearer RADAR_AGENT_TOKEN)   ·   python -m news_radar agent vorschlag --datei v.json

Eingabe: {"vorschlaege": [...]} oder eine Liste (Web höchstens 5, CLI höchstens 100 je Aufruf). Je Vorschlag:
arbeitstitel, datum (JJJJ-MM-TT, Tag des Ereignisses oder der Meldung), rubrik, ort, bezug, heikel, quellen
[{url, titel, herausgeber, datum, sprache, art}], optional kernfakten, bild_hinweis (nur Hinweise für den Agenten,
nie Belege) und erzwingen (legt trotz „vielleicht schon vorhanden“ an).

Ergebnis je Vorschlag: angelegt · vorhanden (alle Adressen sind schon Beleg derselben Story) · vielleicht_vorhanden
(ähnlicher Titel, gleicher oder unbekannter Ort, im selben Zeitraum) · abgelehnt · nicht_bearbeitet (Zeitlimit oder
Stopp). Dublettenprüfung und Anlegen laufen zusammen in einer Schreibtransaktion.

Der Radar holt jede Quelle selbst (net.safe_get, Stopp-Schalter vor jedem Abruf) und legt sie als source_documents
an; Text und Titel eines Dokuments stammen nie aus dem Vorschlag, sondern aus der abgerufenen Seite (Titel aus
og:title bzw. <title>, sonst leer) – sonst würde ein erfundener „Titel“ zur Fundstelle im Gate. PDF-Quellen
(Drucksachen, Urteile, Berichte) liest pypdf: höchstens 8 MB, ab der Seite aus dem Anker „#page=N“ (sonst Seite 1),
höchstens 40 Seiten bzw. TEXT_MAX; Titel aus den PDF-Metadaten; der Anker bleibt im Link und in der Adresse für die
Dublettenprüfung. Danach steht die Story im Agent-Export
(Herkunft „nachtrag“, Status „neu“, kein Job) und läuft durch Import und Gate wie jede andere.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import date, timedelta
from difflib import SequenceMatcher
from html import unescape
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, ValidationError, field_validator

from . import net, schalter, sources
from .agents import Kontext
from .agents.research import VOLLTEXT_MIN
from .config import Settings
from .store import Store, now_iso
from .workflow import repo

RUBRIKEN = ("news", "community", "entertainment", "kino", "events", "kueche", "sport", "kultur")
MAX_QUELLEN = 6
MAX_VORSCHLAEGE = 100  # CLI je Aufruf; die Web-Route erlaubt höchstens WEB_MAX_VORSCHLAEGE
WEB_MAX_VORSCHLAEGE = 5
WEB_FRIST_GESAMT = 90.0  # Sekunden je Web-Aufruf (der Webserver bricht nach 120 s ab)
FRIST_ABRUF = 20.0  # Sekunden je Seitenabruf (gesamt, nicht je Socket-Operation)
FRUEHESTES = date(2020, 1, 1)
ZEITRAUM_TAGE = 14  # Titel-Ähnlichkeit: im Abstand von höchstens so vielen Tagen zum Ereignisdatum
AEHNLICH = 0.82
TEXT_MAX = 20000


class Quelle(BaseModel):
    url: str = Field(max_length=2000)
    titel: str = Field(default="", max_length=300)  # nur zur Orientierung, wird nie Dokument-Titel
    herausgeber: str = Field(default="", max_length=120)
    datum: str = Field(default="", max_length=40)
    sprache: str = Field(default="de", max_length=8)
    art: str = Field(default="", max_length=40)


class Vorschlag(BaseModel):
    arbeitstitel: str = Field(min_length=3, max_length=200)
    datum: str
    rubrik: str
    ort: str = Field(default="", max_length=120)
    bezug: str = Field(default="", max_length=1000)
    heikel: bool = False
    quellen: list[Quelle] = Field(min_length=1)
    kernfakten: list[str] = Field(default_factory=list, max_length=12)
    bild_hinweis: str = Field(default="", max_length=300)
    erzwingen: bool = False

    @field_validator("datum")
    @classmethod
    def _datum(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v or ""):
            raise ValueError("datum muss JJJJ-MM-TT sein")
        date.fromisoformat(v)  # wirft bei 2026-02-30
        return v

    @field_validator("rubrik")
    @classmethod
    def _rubrik(cls, v: str) -> str:
        if v not in RUBRIKEN:
            raise ValueError(f"rubrik muss eine von {', '.join(RUBRIKEN)} sein")
        return v

    @field_validator("kernfakten")
    @classmethod
    def _kernfakten(cls, v: list[str]) -> list[str]:
        if any(len(k) > 300 for k in v):
            raise ValueError("je Kernfakt höchstens 300 Zeichen")
        return v

    @field_validator("quellen")
    @classmethod
    def _quellen(cls, v: list[Quelle]) -> list[Quelle]:
        if len(v) > MAX_QUELLEN:
            raise ValueError(f"höchstens {MAX_QUELLEN} Quellen")
        for q in v:
            if not q.url.lower().startswith(("http://", "https://")):
                raise ValueError(f"nur http/https-Adressen ({q.url[:80]})")
        return v


class VorschlagAbgelehnt(ValueError):
    pass


_TITEL_RES = (
    re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', re.I),
    re.compile(r"<title[^>]*>(.*?)</title\s*>", re.I | re.S),
)


SEITE_MAX = 3_000_000  # Bytes je HTML-Seite
PDF_MAX = 8_000_000  # Bytes je PDF-Datei
PDF_SEITEN_MAX = 40  # gelesen ab der Anker-Seite, bis TEXT_MAX (pdf_kind.SEITEN_MAX)
PDF_TYPES = ("application/pdf",)
_ANKER_RE = re.compile(r"#page=([0-9]{1,5})\Z")


class Unlesbar(ValueError):
    """Die Quelle ist abgerufen, aber nicht lesbar; der Text der Ausnahme ist der Grund für den Bericht."""


def standard_abruf(url: str, frist: float | None = None) -> net.Fetched:
    """Seite oder PDF holen: SSRF-Schutz, Umleitungen geprüft, Größenlimit (net.safe_get). HTML höchstens SEITE_MAX,
    PDF höchstens PDF_MAX Bytes."""
    seite = net.safe_get(url, accept=net.TEXT_TYPES + PDF_TYPES, timeout=8, max_bytes=PDF_MAX, frist=frist)
    if not ist_pdf(seite) and len(seite.content) > SEITE_MAX:
        raise net.ResponseTooLarge(f"mehr als {SEITE_MAX} Bytes: {seite.url}")
    return seite


def anker_seite(url: str) -> int:
    """Seite aus dem Anker „#page=N“ (ab 1); 0 ohne Anker."""
    m = _ANKER_RE.search(url or "")
    return int(m.group(1)) if m and int(m.group(1)) > 0 else 0


def adresse_norm(url: str) -> str:
    """Normalisierte Adresse; ein Seitenanker bleibt Teil davon (dieselbe Datei, andere Seite = andere Adresse)."""
    n = anker_seite(url)
    return repo.normalize_url(url) + (f"#page={n}" if n else "")


def ist_pdf(seite: net.Fetched) -> bool:
    return seite.content_type.lower().startswith(PDF_TYPES) or seite.content[:5] == b"%PDF-"


PDF_ZEIT_MAX = 20.0  # Sekunden je PDF im Kindprozess (höchstens; sonst der Rest der Frist)
PDF_BEFEHL = [sys.executable, "-I", str(Path(__file__).with_name("pdf_kind.py"))]  # austauschbar (Tests)


def pdf_lesen(daten: bytes, ab_seite: int = 1, frist: float | None = None) -> tuple[str, str]:
    """(Text, Titel) eines PDF ab `ab_seite`, höchstens PDF_SEITEN_MAX Seiten bzw. TEXT_MAX Zeichen; Titel nur aus den
    Metadaten (/Title). Gelesen wird in einem eigenen Prozess (pdf_kind.py) mit hartem Zeitlimit (Rest der Frist,
    höchstens PDF_ZEIT_MAX) und Speichergrenze – eine präparierte Datei hält den Web-Worker nicht auf.
    Verschlüsselt, kaputt, zu groß oder zu aufwendig → Unlesbar (nie eine andere Ausnahme)."""
    if len(daten) > PDF_MAX:
        raise Unlesbar(f"PDF zu groß (mehr als {PDF_MAX // 1_000_000} MB)")
    zeit = PDF_ZEIT_MAX if frist is None else min(PDF_ZEIT_MAX, frist - time.monotonic())
    if zeit <= 0:
        raise Unlesbar("PDF zu aufwendig (Zeitlimit)")
    try:
        lauf = subprocess.run([*PDF_BEFEHL, str(max(1, ab_seite))], input=daten, capture_output=True, timeout=zeit,
                              check=False)
    except subprocess.TimeoutExpired:
        raise Unlesbar("PDF zu aufwendig (Zeitlimit)") from None
    except OSError:
        raise Unlesbar("PDF nicht lesbar (Leser nicht startbar)") from None
    try:
        out = json.loads(lauf.stdout.decode("utf-8"))
    except ValueError:
        out = None
    if lauf.returncode != 0 or not isinstance(out, dict):
        raise Unlesbar("PDF zu aufwendig")  # vom Speicherlimit beendet o. Ä.
    if out.get("fehler"):
        raise Unlesbar(str(out["fehler"])[:120])
    return str(out.get("text") or "")[:TEXT_MAX], sources.clean_text(str(out.get("titel") or ""))[:300]


def _flach(s: str) -> str:
    s = (s or "").lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", s)


def herausgeber(name: str, url: str) -> str:
    """Herausgeber für die Quellenangabe: der Host der tatsächlich gelesenen Adresse (nach Umleitungen). Ein Name aus
    dem Vorschlag gilt nur, wenn er zum Host passt („SRF“ ↔ srf.ch), sonst steht der Host da."""
    host = (urlsplit(url).hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host
    if not host:
        return ""
    kern, n = _flach(host.rsplit(".", 1)[0]), _flach(name)
    if n and (n == _flach(host) or (len(n) >= 3 and n in kern) or (len(kern) >= 3 and kern in n)):
        return name.strip()[:120]
    return host[:120]


def _datum_streng(wert: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", wert or ""):
        return ""
    try:
        date.fromisoformat(wert)
    except ValueError:
        return ""
    return wert


LD_BLOECKE_MAX = 20
LD_BYTES_MAX = 200_000  # Zeichen JSON-LD je Seite zusammen
LD_TYPEN = {"Movie", "Event", "ScreeningEvent", "NewsArticle", "Article"}
LD_FELDER = ("name", "description", "startDate", "endDate", "datePublished", "location.name", "location.address",
             "director", "actor", "duration", "inLanguage", "offers.price")
LD_KOPF = "Angaben der Seite (strukturierte Daten)"


def _ld_bloecke(roh: str) -> list[str]:
    """Inhalte der <script type="application/ld+json">-Blöcke – ein linearer Durchlauf mit str.find (kein Regex über
    die Rohseite: „(.*?)</script>“ wäre bei fehlenden Schluss-Tags quadratisch). Höchstens LD_BLOECKE_MAX Blöcke und
    zusammen LD_BYTES_MAX Zeichen; ein Block darüber und alles danach wird ignoriert."""
    klein, pos, bloecke, summe = roh.lower(), 0, [], 0
    while len(bloecke) < LD_BLOECKE_MAX:
        anfang = klein.find("<script", pos)
        tag_ende = klein.find(">", anfang) if anfang >= 0 else -1
        schluss = klein.find("</script", tag_ende) if tag_ende >= 0 else -1
        if schluss < 0:
            break  # kein vollständiger Block mehr
        pos = schluss + 8
        if re.search(r"type\s*=\s*[\"']?application/ld\+json", klein[anfang:tag_ende]):
            inhalt = roh[tag_ende + 1:schluss]
            summe += len(inhalt)
            if summe > LD_BYTES_MAX:
                break
            bloecke.append(inhalt)
    return bloecke


def _ld_objekte(roh: str):
    for block in _ld_bloecke(roh):
        try:
            daten = json.loads(block.strip())
        except ValueError:
            continue
        stapel = daten if isinstance(daten, list) else [daten]
        for obj in stapel:
            if isinstance(obj, dict):
                yield obj
                stapel_graph = obj.get("@graph")
                if isinstance(stapel_graph, list):
                    yield from (o for o in stapel_graph if isinstance(o, dict))


def _ld_werte(wert) -> list[str]:
    """Wörtliche Werte: Text und Zahlen unverändert, Personen/Orte über name, Adressen über ihre Felder."""
    if isinstance(wert, (str, int, float)) and not isinstance(wert, bool):
        return [sources.clean_text(unescape(str(wert)))]
    if isinstance(wert, list):
        return [w for x in wert for w in _ld_werte(x)]
    if isinstance(wert, dict):
        if "name" in wert:
            return _ld_werte(wert["name"])
        teile = [w for k in ("streetAddress", "postalCode", "addressLocality", "addressRegion", "addressCountry")
                 for w in _ld_werte(wert.get(k))]
        return [" ".join(teile)] if teile else []
    return []


def strukturierte_angaben(roh: str) -> str:
    """Notanker für Seiten ohne lesbaren Text: Felder aus JSON-LD (Movie, Event, ScreeningEvent, NewsArticle, Article),
    nur wörtlich übernommene Werte, höchstens TEXT_MAX. Leer, wenn nichts Passendes da ist."""
    zeilen = []
    for obj in _ld_objekte(roh):
        typ = obj.get("@type")
        if not ({typ} if isinstance(typ, str) else set(typ) if isinstance(typ, list) else set()) & LD_TYPEN:
            continue
        for feld in LD_FELDER:
            wert = obj
            for teil in feld.split("."):
                wert = (wert[0] if wert else None) if isinstance(wert, list) else wert
                wert = wert.get(teil) if isinstance(wert, dict) else None
            werte = [w for w in _ld_werte(wert) if w]
            if werte:
                zeilen.append(f"{feld}: {', '.join(werte)}")
        zeilen.append("")
    text = "\n".join(zeilen).strip()
    return f"{LD_KOPF}\n\n{text}"[:TEXT_MAX] if text else ""


def seite_lesen(seite: net.Fetched, adresse: str = "", frist: float | None = None) -> tuple[str, str]:
    """(Text, Titel) der abgerufenen Seite. Der Titel kommt nur aus og:title oder <title>, sonst bleibt er leer.
    PDF: Text ab der Seite aus dem Anker „#page=N“ der Adresse (sonst Seite 1), Titel aus den Metadaten."""
    if ist_pdf(seite):
        return pdf_lesen(seite.content, max(1, anker_seite(adresse or seite.url)), frist=frist)
    roh = seite.text
    titel = ""
    for rx in _TITEL_RES:
        m = rx.search(roh)
        if m and m.group(1).strip():
            titel = sources.clean_text(unescape(m.group(1)))[:300]
            break
    text = sources.extract_paragraphs(roh, TEXT_MAX)
    if len(text or "") < VOLLTEXT_MIN:  # ohne JavaScript kein Text: strukturierte Angaben als Notanker
        text = strukturierte_angaben(roh) or text
    return text, titel


class Zeitlimit(Exception):
    """Die Gesamtfrist des Aufrufs ist abgelaufen."""


def _fehlertext(exc: ValidationError) -> str:
    err = exc.errors()[0]
    feld = ".".join(str(x) for x in err.get("loc", ()))
    return f"{feld}: {err['msg']}".replace("Value error, ", "")


def _norm(titel: str) -> str:
    return " ".join(re.findall(r"\w+", (titel or "").lower()))


def _uid(url: str) -> str:
    return f"nachtrag:{adresse_norm(url)}"


def _alle_adressen_belegt(store: Store, v: Vorschlag) -> int | None:
    """Harte Dublette: **alle** Adressen des Vorschlags sind schon Beleg derselben Story. Eine einzelne gemeinsame
    Adresse (etwa ein Jahresbericht) reicht nicht. Vom Scan verworfene Radar-Storys zählen nicht (ein vergangenes
    Ereignis ist dort oft als „vorbei“ verworfen worden); Nachtrag-Storys zählen in jedem Status."""
    gemeinsam: set[int] | None = None
    for q in v.quellen:
        ids = {r[0] for r in store.db.execute(
            "SELECT DISTINCT s.id FROM source_documents d JOIN stories s ON s.id = d.story_id "
            "WHERE (d.url_norm = ? OR d.uid = ?) AND NOT (s.herkunft = 'radar' AND s.status = 'verworfen')",
            (adresse_norm(q.url), _uid(q.url)))}
        gemeinsam = ids if gemeinsam is None else gemeinsam & ids
        if not gemeinsam:
            return None
    return min(gemeinsam) if gemeinsam else None


def _aehnlicher_titel(store: Store, v: Vorschlag) -> int | None:
    """Weiche Dublette: sehr ähnlicher Titel im selben Zeitraum – nicht bei verschiedenem Ort."""
    tag = date.fromisoformat(v.datum)
    von, bis = (tag - timedelta(days=ZEITRAUM_TAGE)).isoformat(), (tag + timedelta(days=ZEITRAUM_TAGE)).isoformat()
    titel, ort = _norm(v.arbeitstitel), _norm(v.ort)
    for row in store.db.execute(
            "SELECT id, titel, ort FROM stories WHERE (herkunft = 'nachtrag' AND ereignis_datum BETWEEN ? AND ?) "
            "OR (herkunft = 'radar' AND status != 'verworfen' AND substr(erstellt, 1, 10) BETWEEN ? AND ?) ORDER BY id",
            (von, bis, von, bis)):
        anderer_ort = _norm(row["ort"])
        if ort and anderer_ort and ort != anderer_ort:
            continue
        if SequenceMatcher(None, titel, _norm(row["titel"])).ratio() >= AEHNLICH:
            return row["id"]
    return None


def _dublette(store: Store, v: Vorschlag) -> dict | None:
    sid = _alle_adressen_belegt(store, v)
    if sid:
        return {"ergebnis": "vorhanden", "story_id": sid, "grund": f"schon vorhanden: Story {sid}"}
    if not v.erzwingen:
        sid = _aehnlicher_titel(store, v)
        if sid:
            return {"ergebnis": "vielleicht_vorhanden", "story_id": sid,
                    "grund": f"vielleicht schon vorhanden: Story {sid}"}
    return None


def _pruefen(raw, heute: date) -> Vorschlag:
    if not isinstance(raw, dict):
        raise VorschlagAbgelehnt("Vorschlag muss ein Objekt sein")
    try:
        v = Vorschlag.model_validate(raw)
    except ValidationError as exc:
        raise VorschlagAbgelehnt(_fehlertext(exc)) from None
    tag = date.fromisoformat(v.datum)
    if tag > heute:
        raise VorschlagAbgelehnt(f"datum: {v.datum} liegt in der Zukunft")
    if tag < FRUEHESTES:
        raise VorschlagAbgelehnt(f"datum: {v.datum} liegt vor {FRUEHESTES.isoformat()}")
    for q in v.quellen:  # vor jedem Abruf: interne Adressen lehnen den ganzen Vorschlag ab
        try:
            net.check_url(q.url)
        except net.UnsafeURL as exc:
            grund = "interne Adresse" if "Interne Adresse" in str(exc) else "Adresse gesperrt"
            raise VorschlagAbgelehnt(f"{grund}: {q.url[:80]} ({exc})") from None
    return v


def _anlegen(store: Store, v: Vorschlag, geholt: list) -> dict:
    """Dublettenprüfung wiederholen und Story mit Dokumenten anlegen – in einer Schreibtransaktion (BEGIN IMMEDIATE),
    damit zwei gleichzeitige Aufrufe nicht beide anlegen (zwischen erster Prüfung und hier lagen die Abrufe)."""
    hinweise = {"bezug": v.bezug, "kernfakten": v.kernfakten, "bild_hinweis": v.bild_hinweis}
    with store.lock:
        db = store.db
        if db.in_transaction:
            db.commit()
        db.execute("BEGIN IMMEDIATE")
        try:
            dublette = _dublette(store, v)
            if dublette:
                db.rollback()
                return dublette
            ts = now_iso()
            sid = db.execute(
                "INSERT INTO stories (typ, status, titel, kategorie, ort, region, sensibel, schluessel, prioritaet, "
                "laenge, relevanz, begruendung, notiz, herkunft, ereignis_datum, vorschlag, erstellt, aktualisiert) "
                "VALUES ('news', 'neu', ?, ?, ?, '', ?, '', 0, 'normal', 7, 'Nachtrag für den Rückblick', ?, "
                "'nachtrag', ?, ?, ?, ?)",
                (v.arbeitstitel, v.rubrik, v.ort, 1 if v.heikel else 0, f"Nachtrag · Bezug: {v.bezug}"[:900], v.datum,
                 json.dumps(hinweise, ensure_ascii=False), ts, ts)).lastrowid
            for n, (q, text, seitentitel, gelesen) in enumerate(geholt, 1):
                # verlinkt wird die gelesene Adresse; die Ursprungsadresse bleibt als uid für die Dublettenprüfung
                db.execute(
                    "INSERT INTO source_documents (story_id, doc_key, url, url_norm, uid, publisher, quelle, "
                    "published_at, retrieved_at, language, rights, primaer, art, titel, text, text_sha256, auszug) "
                    "VALUES (?,?,?,?,?,?, 'Nachtrag', ?,?,?, 'zitat', 1, 'volltext', ?,?,?,?)",
                    (sid, f"Q{n}", gelesen, adresse_norm(gelesen), _uid(q.url),
                     herausgeber(q.herausgeber, gelesen), _datum_streng(q.datum), ts, (q.sprache or "de")[:8],
                     seitentitel, text, hashlib.sha256(text.encode("utf-8")).hexdigest(), text[:500]))
            db.commit()
        except BaseException:
            db.rollback()
            raise
    return {"ergebnis": "angelegt", "story_id": sid}


def _eins(store: Store, raw, nr: int, von: str, abruf: Callable, heute: date, uhr: Callable[[], float],
          ende: float | None, frist_abruf: float) -> dict:
    titel = raw.get("arbeitstitel", "") if isinstance(raw, dict) else ""
    out: dict = {"nr": nr, "arbeitstitel": str(titel)[:120]}
    try:
        v = _pruefen(raw, heute)
    except VorschlagAbgelehnt as exc:
        return {**out, "ergebnis": "abgelehnt", "grund": str(exc)[:300]}
    dublette = _dublette(store, v)  # vor den Abrufen: nichts holen, was schon da ist
    if dublette:
        return {**out, **dublette}
    geholt, uebersprungen = [], []
    for q in v.quellen:
        jetzt = uhr()
        if ende is not None and jetzt >= ende:
            raise Zeitlimit
        schalter.pruefen(store, "redaktion")  # unmittelbar vor dem Abruf
        frist = jetzt + frist_abruf if ende is None else min(jetzt + frist_abruf, ende)
        try:
            seite = abruf(q.url, frist=frist)
            text, seitentitel = seite_lesen(seite, q.url, frist=frist)
        except Unlesbar as exc:
            uebersprungen.append({"url": q.url, "grund": str(exc)[:80]})
            continue
        except Exception as exc:  # noqa: BLE001 – eine kaputte Seite stoppt den Vorschlag nicht
            uebersprungen.append({"url": q.url, "grund": f"nicht abrufbar ({type(exc).__name__})"[:80]})
            continue
        if len(text or "") < VOLLTEXT_MIN:
            uebersprungen.append({"url": q.url, "grund": "ohne lesbaren Text"})
            continue
        gelesen = seite.url or q.url
        if anker_seite(q.url) and ist_pdf(seite) and "#" not in gelesen:
            gelesen += f"#page={anker_seite(q.url)}"  # der Link führt auf die gelesene Seite
        if any(adresse_norm(g[3]) == adresse_norm(gelesen) for g in geholt):
            uebersprungen.append({"url": q.url, "grund": "doppelt im Vorschlag"})
            continue
        geholt.append((q, text[:TEXT_MAX], seitentitel, gelesen))
    if not geholt:
        return {**out, "ergebnis": "abgelehnt", "grund": "keine Quelle abrufbar", "quellen_uebersprungen": uebersprungen}
    ergebnis = _anlegen(store, v, geholt)
    if ergebnis["ergebnis"] != "angelegt":
        return {**out, **ergebnis}
    sid = ergebnis["story_id"]
    repo.aktion(store, wer=von[:60], aktion="nachtrag_angelegt", story_id=sid, kanal="redaktion", ausloeser="agent",
                notiz=f"{len(geholt)} Quellen geholt, {len(uebersprungen)} übersprungen")
    store.event("nachtrag", story=sid, quellen=len(geholt), uebersprungen=len(uebersprungen), von=von[:60])
    return {**out, "ergebnis": "angelegt", "story_id": sid, "quellen_geholt": len(geholt),
            "quellen_uebersprungen": uebersprungen}


ERGEBNISSE = ("angelegt", "vorhanden", "vielleicht_vorhanden", "abgelehnt", "nicht_bearbeitet")


def annehmen(store: Store, settings: Settings, raw, *, von: str = "agent", ctx: Kontext | None = None,
             abruf: Callable | None = None, max_vorschlaege: int = MAX_VORSCHLAEGE,
             frist_gesamt: float | None = None, frist_abruf: float = FRIST_ABRUF,
             uhr: Callable[[], float] = time.monotonic) -> dict:
    """Vorschläge annehmen. Hält der Schalter „redaktion“ schon vorher an, wirft schalter.Gestoppt (nichts getan);
    hält er mitten im Stapel an, enthält die Antwort die bisherigen Ergebnisse und „angehalten“."""
    schalter.pruefen(store, "redaktion")
    items = raw.get("vorschlaege") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError('Vorschläge: erwartet {"vorschlaege": [...]} oder eine Liste')
    if len(items) > max_vorschlaege:
        raise ValueError(f"höchstens {max_vorschlaege} Vorschläge je Aufruf")
    ctx = ctx or Kontext(settings=settings, store=store)
    abruf = abruf or (lambda url, frist=None: standard_abruf(url, frist=frist))  # zur Laufzeit (austauschbar)
    heute = ctx.uhr().date()
    ende = uhr() + frist_gesamt if frist_gesamt is not None else None
    ergebnisse: list[dict] = []
    angehalten = None
    for nr, raw_v in enumerate(items, 1):
        titel = str(raw_v.get("arbeitstitel", "") if isinstance(raw_v, dict) else "")[:120]
        if angehalten is None and (ende is None or uhr() < ende):
            try:
                ergebnisse.append(_eins(store, raw_v, nr, von, abruf, heute, uhr, ende, frist_abruf))
                continue
            except Zeitlimit:
                pass
            except schalter.Gestoppt as exc:
                angehalten = {"kanal": exc.sperre["kanal"], "seit": exc.sperre["seit"]}
        grund = "nicht bearbeitet: angehalten" if angehalten else "nicht bearbeitet: Zeitlimit"
        ergebnisse.append({"nr": nr, "arbeitstitel": titel, "ergebnis": "nicht_bearbeitet", "grund": grund})
    out = {"ergebnisse": ergebnisse, **{k: sum(1 for e in ergebnisse if e["ergebnis"] == k) for k in ERGEBNISSE}}
    if angehalten:
        out["angehalten"] = angehalten
    return out
