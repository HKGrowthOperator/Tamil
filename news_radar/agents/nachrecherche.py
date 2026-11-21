"""Nachrecherche: scheitert das Gate, sucht der Radar selbst nach Belegen für die Fehlstellen – ohne Sprachmodell.

Auftrag Luis vom 13.11.2026: keine Story bleibt auf „Recherche nötig“ stehen, niemand fügt Links von Hand ein.
Aus Titel, Ort, Personen und den Fehlstellen (Gründe des Gates, `fehlende_angaben` der Recherche) entstehen
Suchanfragen; Kandidaten kommen über diese Wege (in dieser Reihenfolge):

  dokumente    Adressen, die in den Dokumenten der Story genannt sind (z. B. die Seite des Veranstalters)
  hinweis      Hinweis-Dokumente mit direkter Adresse (nicht Google News), die noch keinen Text haben
  register     Meldungen registrierter Quellen, die der Radar in den letzten 30 Tagen gesehen hat (Tabelle seen),
               und die Suche der registrierten WordPress-Quellen
  bildquellen  Startseiten aus dem Bildquellen-Register, deren Betreiber zur Story passt (Tempel, Vereine)
  suche        Google-News-RSS-Suche: Treffer mit Google-Adresse bleiben Hinweise (nie Beleg), direkte Adressen werden
               gelesen

Gelesen wird nur über ctx.text_von bzw. ctx.json_abruf (net.safe_get, Stopp-Schalter vor jedem Abruf). Nie soziale
Netzwerke, nie Quellen mit Paywall (Register oder Paywall-Text auf der Seite). Angehängt wird nur, was genug Text hat
und zur Story passt (Ort und ein Stichwort oder zwei Stichwörter aus dem Titel) – als Volltext; ob eine Aussage damit
bestätigt ist, entscheidet danach wie immer das Gate (wörtliche Fundstelle). Höchstens MAX_RUNDEN Runden je Story.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus, urlsplit

from .. import filtering, schalter
from ..quellencheck import _PAYWALL_RE
from ..sources import clean_text
from ..workflow import repo
from ..workflow.models import Claim, SourceDocument
from . import Kontext
from .research import VOLLTEXT_MIN, _suchbegriffe, google_news_suche, ist_google

log = logging.getLogger(__name__)

MAX_RUNDEN = 2
MAX_ANFRAGEN = 4
MAX_NEU = 4  # neue Belege je Runde
MAX_ABRUFE = 8  # gelesene Seiten je Runde
MAX_HINWEISE = 3
SEEN_TAGE = 30
TEXT_MAX = 20000

SOZIAL = ("facebook.com", "fb.com", "fb.me", "instagram.com", "x.com", "twitter.com", "t.co", "tiktok.com",
          "youtube.com", "youtu.be", "linkedin.com", "whatsapp.com", "wa.me", "telegram.org", "telegram.me", "t.me",
          "threads.net", "pinterest.com", "reddit.com", "snapchat.com", "vk.com", "discord.gg", "discord.com")
_STOP = {"der", "die", "das", "und", "mit", "für", "von", "vom", "zum", "zur", "den", "dem", "des", "ein", "eine",
         "einen", "einem", "nach", "auf", "aus", "bei", "über", "unter", "wird", "werden", "hat", "haben", "ist", "sind",
         "neue", "neuer", "neues", "heute", "jetzt", "mehr", "the", "and", "for", "with", "news"}
# Großgeschriebene Wörter, die keine Namen sind (Nomen am Satzanfang, Monate, Tage, Rollen)
_KEIN_NAME = {"der", "die", "das", "den", "dem", "des", "ein", "eine", "am", "im", "in", "an", "auf", "zum", "zur",
              "vorsitzende", "vorsitzender", "präsident", "präsidentin", "bürgermeister", "bürgermeisterin",
              "oberbürgermeister", "oberbürgermeisterin", "stadt", "verein", "tempel", "gemeinde", "rathaus", "herr",
              "frau", "januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september", "oktober",
              "november", "dezember", "montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag",
              "tamilische", "tamilischer", "tamilisches", "tamilischen", "deutschland", "schweiz", "österreich",
              "sri", "lanka", "wdr", "ndr", "swr", "srf", "orf", "dpa"}
_GENERISCH = {"tempel", "hindu", "verein", "kultur", "gemeinschaft", "restaurant", "internationales", "institut",
              "festival", "sangam", "arulmigu", "alayam", "kovil", "swamy", "tamilische", "tamil", "tamilischen"}
_NAME_RE = re.compile(r"\b[A-ZÄÖÜ][a-zäöüß]+(?:[- ][A-ZÄÖÜ][a-zäöüß]+){1,3}\b")
_URL_RE = re.compile(r"(?:https?://|\bwww\.)[^\s<>\"'()\[\]{}|]+", re.I)

FEHL_MUSTER = (
    (r"ohne bestätigtes Datum", "Datum"),
    (r"ohne bestätigten Ort", "Ort"),
    (r"Keine Kernaussage", "Bericht mit Volltext"),
    (r"Widerspruch bei Kernaussage \w+: (.+)", "Klärung: {0}"),
    (r"Kernaussage \w+ nur (?:aus einer Quelle|als Hinweis) belegt: (.+)", "zweite Quelle: {0}"),
    (r"Faktencheck: (.+)", "Beleg für: {0}"),
)


@dataclass
class Kandidat:
    url: str
    weg: str
    titel: str = ""
    publisher: str = ""
    doc_key: str = ""  # gesetzt bei „hinweis“: vorhandenes Dokument, das Text bekommt
    primaer: bool = False  # Veranstalter oder vertrauenswürdige Registerquelle


@dataclass
class Ergebnis:
    runde: int
    fehlend: list[str]
    anfragen: list[str]
    neu: list[str] = field(default_factory=list)  # doc_keys der neuen bzw. aufgewerteten Belege
    hinweise: int = 0  # neue Google-Hinweise (kein Beleg)
    gelesen: int = 0
    wege: Counter = field(default_factory=Counter)
    abgelehnt: Counter = field(default_factory=Counter)

    def zusammenfassung(self) -> str:
        if self.neu:
            wege = ", ".join(f"{w} {n}" for w, n in self.wege.items())
            return f"{len(self.neu)} neue {'Quelle' if len(self.neu) == 1 else 'Quellen'} ({wege})"
        return f"nichts Neues gefunden ({self.gelesen} Seiten gelesen, {self.hinweise} Hinweise)"


def host(url: str) -> str:
    try:
        h = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def sozial(url: str) -> bool:
    h = host(url)
    return any(h == s or h.endswith("." + s) for s in SOZIAL)


# Verworfen, weil Belege fehlten (zweite KI nach der Nachrecherche, Agent-Import nach zwei Runden) oder als Dublette
# eines Entwurfs: eine neue Quelle startet die Story noch einmal – höchstens MAX_NEUSTARTS-mal. Nie nach der
# Endprüfung („Zweite KI (Endprüfung): …“), dem Faktencheck, einem vergangenen Termin oder einer Entscheidung der
# Redaktion bzw. des Agenten.
NEU_STARTBAR_VERWORFEN = ("Zweite KI: verworfen", "Nach zwei Runden Nachrecherche",
                          "Entwurf zu dieser Meldung existiert schon")
MAX_NEUSTARTS = 2


def neu_startbar(story: dict) -> bool:
    return story.get("status") == "verworfen" and (story.get("notiz") or "").startswith(NEU_STARTBAR_VERWORFEN)


mangels_beleg = neu_startbar  # alter Name (Cluster)


def neustarts(store, story_id: int) -> int:
    return store.db.execute("SELECT COUNT(*) FROM log WHERE event = 'neu_gestartet' AND json_extract(data, '$.story') = ?"
                            " AND json_extract(data, '$.vorher') IN ('verworfen', 'fehler')", (story_id,)).fetchone()[0]


def runden(store, story_id: int) -> int:
    """Wie viele Runden Nachrecherche die Story schon hat (jeder Job zählt, auch der laufende)."""
    return store.db.execute("SELECT COUNT(*) FROM workflow_jobs WHERE story_id = ? AND schritt = 'nachrecherche'",
                            (story_id,)).fetchone()[0]


def fehlstellen(gruende: list[str], fehlend: list[str]) -> list[str]:
    """Was gesucht wird: aus den Gründen des Gates (Datum, Ort, zweite Quelle …) und den fehlenden Angaben."""
    out: list[str] = []
    for g in gruende:
        for muster, text in FEHL_MUSTER:
            m = re.search(muster, g or "")
            if m:
                out.append(text.format(*(s.strip()[:80] for s in m.groups())))
                break
    out += [f.strip()[:120] for f in fehlend if isinstance(f, str) and f.strip()]
    return list(dict.fromkeys(out))[:6]


def personen(texte: list[str]) -> list[str]:
    """Namen (zwei bis vier großgeschriebene Wörter) aus Aussagen und Titeln; Rollen und Nomen davor fallen weg."""
    out = []
    for text in texte:
        for m in _NAME_RE.finditer(text or ""):
            teile = re.split(r"[- ]", m.group(0))
            while teile and teile[0].lower() in _KEIN_NAME:
                teile = teile[1:]
            if len(teile) >= 2 and not any(t.lower() in _KEIN_NAME for t in teile):
                out.append(" ".join(teile))
    return list(dict.fromkeys(out))[:2]


def _titel(story: dict) -> str:
    from ..writer import split_source_suffix

    return split_source_suffix(story.get("titel") or "")[0]


def suchanfragen(story: dict, texte: list[str], fehl: list[str]) -> list[str]:
    """Höchstens MAX_ANFRAGEN Anfragen: Titel, Titel + Ort, Personen + Ort, Titel + Fehlstelle."""
    basis = _suchbegriffe(_titel(story))
    kurz = " ".join(basis.split()[:4])
    ort = (story.get("ort") or "").strip()
    anfragen = [basis] if basis else []
    if ort and ort.lower() not in basis.lower():
        anfragen.append(f"{kurz} {ort}".strip())
    for name in personen(texte):
        anfragen.append(f"{name} {ort or kurz}".strip())
    for f in fehl:
        wort = f.split(":", 1)[-1].strip() if ":" in f else f
        if wort in ("Bericht mit Volltext",):
            continue
        anfragen.append(f"{kurz} {_suchbegriffe(wort)[:60]}".strip())
    return [a for a in dict.fromkeys(a.strip() for a in anfragen) if a][:MAX_ANFRAGEN]


def stichworte(story: dict) -> list[str]:
    """Wortanfänge (bis 6 Zeichen) der tragenden Titelwörter – „tamil…“ zählt nicht, das steht überall."""
    worte = re.findall(r"[\wäöüß]{4,}", _titel(story).lower())
    return list(dict.fromkeys(w[:6] for w in worte if w not in _STOP and not w.startswith("tamil")))


def passt(text: str, worte: list[str], ort: str, jahr: int | None = None, datum=None) -> bool:
    """Passt die Seite zur Story? Ort und ein Titelwort oder zwei Titelwörter – und, wo bekannt, das Jahr (nennt die
    Seite Jahre, muss das der Story dabei sein) und bei Terminen das Datum (nennt sie Daten, muss es dabei sein)."""
    low = (text or "").lower()
    n = sum(1 for w in worte if w in low)
    if not (n >= 2 or (bool(ort) and ort.lower() in low and n >= 1)):
        return False
    if jahr:
        jahre = set(re.findall(r"\b(20\d\d)\b", text or ""))
        if jahre and str(jahr) not in jahre:
            return False
    if datum is not None:
        from .. import dates

        daten = dates.alle_daten(text or "")
        if daten and datum not in daten:
            return False
    return True


def story_zeit(story: dict, docs: list[SourceDocument]) -> tuple[int | None, object]:
    """(Jahr, Termindatum) der Story: Ereignisdatum (Nachtrag), Termin aus den strukturierten Angaben, sonst das Jahr
    der Anlage."""
    import json as _json
    from datetime import date

    datum = None
    for wert in [story.get("ereignis_datum") or ""] + [
            str((_json.loads(d.text or "{}") if d.art == "daten" and (d.text or "").startswith("{") else {})
                .get("event_datum") or "") for d in docs]:
        try:
            datum = date.fromisoformat(wert[:10])
            break
        except ValueError:
            continue
    jahr = datum.year if datum else int((story.get("erstellt") or "0")[:4] or 0) or None
    return jahr, (datum if story.get("typ") == "event" else None)


def _primaer_hosts(ctx: Kontext) -> set[str]:
    """Veranstalter (Bildquellen-Register) und vertrauenswürdige Quellen des Registers: nur ihre Seiten sind allein ein
    Beleg (primär); alles andere braucht wie immer einen zweiten Verlag."""
    from .research import quelle_vertrauenswuerdig

    hosts = {b.host for b in ctx.settings.bildquellen}
    hosts |= {host(s.url) for s in ctx.settings.alle_quellen if s.url and quelle_vertrauenswuerdig(s)}
    return {h for h in hosts if h}


def _ist_primaer(url: str, hosts: set[str]) -> bool:
    h = host(url)
    return any(h == x or h.endswith("." + x) for x in hosts)


def _paywall_hosts(ctx: Kontext) -> set[str]:
    return {host(s.url) for s in ctx.settings.alle_quellen if s.paywall and s.url}


def _aus_dokumenten(docs: list[SourceDocument]) -> list[Kandidat]:
    out = []
    for d in docs:
        for m in _URL_RE.finditer(f"{d.titel} {d.text}"):
            url = m.group(0).rstrip(".,;:!?")
            if url.lower().startswith("www."):
                url = "https://" + url
            if not ist_google(url):
                out.append(Kandidat(url=url, weg="dokumente"))
        if d.art == "hinweis" and d.url and not ist_google(d.url) and not d.text.strip():
            out.append(Kandidat(url=d.url, weg="hinweis", titel=d.titel, publisher=d.publisher, doc_key=d.doc_key))
    return out


def _aus_register(ctx: Kontext, story: dict, worte: list[str], ort: str) -> list[Kandidat]:
    seit = (datetime.now(timezone.utc) - timedelta(days=SEEN_TAGE)).isoformat(timespec="seconds")
    treffer = []
    for titel, url, quelle in ctx.store.db.execute(
            "SELECT title, url, source FROM seen WHERE created_at >= ? ORDER BY created_at DESC LIMIT 3000", (seit,)):
        if not url or ist_google(url):
            continue
        src = filtering.quelle_nach_name(quelle or "", ctx.settings.alle_quellen)
        if src is None or src.paywall or src.type == "gnews_region":
            continue
        low = (titel or "").lower()
        n = sum(1 for w in worte if w in low) + (1 if ort and ort.lower() in low else 0)
        if n >= 2:
            treffer.append((n, Kandidat(url=url, weg="register", titel=clean_text(titel or ""), publisher=src.name,
                                        primaer=research_vertrauen(src))))
    treffer.sort(key=lambda t: -t[0])
    out = [k for _, k in treffer[:4]]
    # WordPress-Quellen des Registers durchsuchen (eigene Suche der Seite, nur Titel und Adresse)
    for src in ctx.settings.alle_quellen:
        if not (src.enabled and src.type in ("wp_json", "tribe_events") and not src.paywall and src.url):
            continue
        q = quote_plus(" ".join(_suchbegriffe(_titel(story)).split()[:4]))
        if src.type == "tribe_events":
            url = f"{src.url.rstrip('/')}/wp-json/tribe/events/v1/events?search={q}&per_page=3"
        else:
            url = f"{src.url.rstrip('/')}/wp-json/wp/v2/posts?search={q}&per_page=3&_fields=link,title"
        try:
            daten = ctx.json_abruf(url)
        except schalter.Gestoppt:
            raise
        except Exception as exc:  # noqa: BLE001 – eine Suche, die nicht antwortet, stoppt die Nachrecherche nicht
            log.info("WordPress-Suche %s: %s", src.name, exc)
            continue
        eintraege = daten.get("events", []) if isinstance(daten, dict) else daten if isinstance(daten, list) else []
        for e in eintraege[:3]:
            if not isinstance(e, dict):
                continue
            link = e.get("link") or e.get("url") or ""
            titel = e.get("title")
            titel = titel.get("rendered", "") if isinstance(titel, dict) else str(titel or "")
            if isinstance(link, str) and link.startswith("https://"):
                out.append(Kandidat(url=link, weg="register", titel=clean_text(titel), publisher=src.name))
    return out


def research_vertrauen(src) -> bool:
    from .research import quelle_vertrauenswuerdig

    return quelle_vertrauenswuerdig(src)


def _aus_bildquellen(ctx: Kontext, story_text: str) -> list[Kandidat]:
    staedte = {s.lower() for s in ctx.settings.regions.staedte}
    low = story_text.lower()
    out = []
    for b in ctx.settings.bildquellen:
        stamm = b.host.split(".")[0]
        worte = [w for w in re.findall(r"[\wäöüß]{5,}", b.betreiber.lower())
                 if w not in _GENERISCH and w not in staedte and not w.startswith("tamil")]
        if (len(stamm) >= 6 and stamm in low.replace(" ", "")) or sum(1 for w in set(worte) if w in low) >= 2:
            out.append(Kandidat(url=f"https://{b.host}/", weg="bildquellen", publisher=b.betreiber, primaer=True))
    return out


def _suche(ctx: Kontext, story: dict, anfragen: list[str], bekannt_titel: set[str]) -> tuple[list[Kandidat], list[dict]]:
    suche = ctx.suche or google_news_suche
    kandidaten, hinweise = [], []
    for q in anfragen:
        schalter.pruefen(ctx.store, "redaktion")  # unmittelbar vor jeder Suche
        for t in suche(q) or []:
            url, titel = t.get("url", ""), t.get("titel", "")
            if not url or sozial(url):
                continue
            if ist_google(url):
                if titel.lower() not in bekannt_titel:
                    bekannt_titel.add(titel.lower())
                    hinweise.append(t)
            else:
                kandidaten.append(Kandidat(url=url, weg="suche", titel=titel, publisher=t.get("publisher", "")))
    return kandidaten, hinweise


def nachrecherchieren(ctx: Kontext, story: dict, fehlend: list[str], gruende: list[str], runde: int) -> Ergebnis:
    """Eine Runde: Kandidaten sammeln, lesen, passende Seiten als Volltext-Belege anhängen."""
    sid = story["id"]
    docs = repo.dokumente(ctx.store, sid)
    claims: list[Claim] = repo.claims(ctx.store, sid)
    fehl = fehlstellen(gruende, fehlend) or ["Bericht mit Volltext"]
    texte = [c.aussage for c in claims if c.art == "wer"] + [d.titel for d in docs]
    anfragen = suchanfragen(story, texte, fehl)
    erg = Ergebnis(runde=runde, fehlend=fehl, anfragen=anfragen)
    worte, ort = stichworte(story), (story.get("ort") or "").strip()
    jahr, datum = story_zeit(story, docs)
    primaer_hosts = _primaer_hosts(ctx)
    story_text = " ".join([story.get("titel") or ""] + [f"{d.titel} {d.text[:3000]}" for d in docs])

    kandidaten = _aus_dokumenten(docs) + _aus_register(ctx, story, worte, ort) + _aus_bildquellen(ctx, story_text)
    gefunden, hinweise = _suche(ctx, story, anfragen, {d.titel.lower() for d in docs})
    kandidaten += gefunden
    for t in hinweise[:MAX_HINWEISE]:
        key = repo.dokument_hinzufuegen(ctx.store, sid, url=t["url"], publisher=t.get("publisher", ""),
                                        quelle="Nachrecherche (suche)", rights="zitat", art="hinweis",
                                        titel=t.get("titel", ""), text="")
        erg.hinweise += 1 if key else 0

    bekannt = {repo.normalize_url(d.url) for d in docs if d.url}
    paywall = _paywall_hosts(ctx)
    gesehen: set[str] = set()
    for k in kandidaten:
        if len(erg.neu) >= MAX_NEU or erg.gelesen >= MAX_ABRUFE:
            break
        norm = repo.normalize_url(k.url)
        if norm in gesehen or (norm in bekannt and k.weg != "hinweis"):
            continue
        gesehen.add(norm)
        if sozial(k.url):
            erg.abgelehnt["sozial"] += 1
            continue
        if host(k.url) in paywall:
            erg.abgelehnt["paywall"] += 1
            continue
        erg.gelesen += 1
        try:
            text = ctx.text_von(k.url)
        except schalter.Gestoppt:
            raise
        except Exception as exc:  # noqa: BLE001 – eine kaputte Seite stoppt die Nachrecherche nicht
            log.info("Nachrecherche: %s nicht gelesen (%s)", k.url[:80], exc)
            text = ""
        if len(text or "") < VOLLTEXT_MIN:
            erg.abgelehnt["zu_wenig_text"] += 1
            continue
        if _PAYWALL_RE.search(text[:4000]):
            erg.abgelehnt["paywall"] += 1
            continue
        if not passt(text, worte, ort, jahr, datum):
            erg.abgelehnt["passt_nicht"] += 1
            continue
        if k.doc_key:
            primaer = k.primaer or _ist_primaer(k.url, primaer_hosts)
            repo.dokument_setzen(ctx.store, sid, k.doc_key, text=text[:TEXT_MAX], art="volltext", primaer=primaer)
            key = k.doc_key
        else:
            key = repo.dokument_hinzufuegen(ctx.store, sid, url=k.url, publisher=k.publisher or host(k.url),
                                            quelle=f"Nachrecherche ({k.weg})", rights="zitat",
                                            primaer=k.primaer or _ist_primaer(k.url, primaer_hosts),
                                            art="volltext", titel=k.titel, text=text[:TEXT_MAX])
        if key:
            erg.neu.append(key)
            erg.wege[k.weg] += 1
    return erg


def stand(store, story_id: int) -> dict | None:
    """Letzte Runde der Nachrecherche einer Story (aus dem Protokoll) – für Cockpit und Agent-Export."""
    import json

    row = store.db.execute(
        "SELECT ts, data FROM log WHERE event = 'nachrecherche' AND json_extract(data, '$.story') = ? "
        "ORDER BY id DESC LIMIT 1", (story_id,)).fetchone()
    if row is None:
        return None
    try:
        daten = json.loads(row[1])
    except ValueError:
        return None
    return {**daten, "ts": row[0]}
