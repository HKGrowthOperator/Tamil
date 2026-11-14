"""Vorfilter: Aktualität, Ausschlussliste, Stichwort- und DACH-Relevanz, Dubletten.

Zweistufig: Meldungen mit erkennbarem DACH-Bezug brauchen nur wenige tamilische Stichworte,
Meldungen ohne DACH-Bezug die volle Schwelle. Events und Kinoprogramme umgehen die Stichwortwertung.
Termine brauchen ein junges echtes Datum oder einen Termin in der Zukunft; Quellen mit `bezug_noetig` einen
Begriff mit tamilischem Bezug.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher

from . import dates
from .config import Regions, Settings, Source
from .sources import NewsItem

_TAMIL_SCRIPT = re.compile(r"[஀-௿]")


def _contains(text: str, term: str, exact: bool = False, suffix: int = 0) -> bool:
    """Ganzes Wort (optional mit bis zu `suffix` Flexionsbuchstaben: tamilisch → tamilischer/-en);
    tamilische Schrift per Teilstring ohne abschließendes Pulli (தமிழ் trifft தமிழர்கள்);
    `exact` = Groß-/Kleinschreibung beachten (Essen, Hamm, Bern)."""
    if _TAMIL_SCRIPT.search(term):
        return term.rstrip("\u0bcd") in text
    flags = 0 if exact else re.I
    tail = rf"[a-zäöüß]{{0,{suffix}}}" if suffix else ""
    return re.search(rf"(?<![\w]){re.escape(term)}{tail}(?![\w])", text, flags) is not None


def score_item(item: NewsItem, keywords: dict[str, int]) -> int:
    title = item.title.lower()
    body = item.summary.lower()
    score = 0
    for term, weight in keywords.items():
        if _contains(title, term, suffix=2):
            score += weight * 2
        elif _contains(body, term, suffix=2):
            score += weight
    return score


def dach_score(item: NewsItem, regions: Regions) -> tuple[int, str]:
    """(Punkte, Ort): Stadt im Titel 3, im Text 1, Land 1. Ort = erste Stadt im Titel, sonst im Text, sonst Land."""
    title, body = item.title, item.summary
    score, ort, body_ort, land_ort = 0, "", "", ""
    for stadt, land in regions.staedte.items():
        names = [stadt] + regions.aliases.get(stadt, [])
        exact = stadt in regions.exakt
        if any(_contains(title, n, exact) for n in names):
            score += 3
            ort = ort or stadt
        elif any(_contains(body, n, exact) for n in names):
            score += 1
            body_ort = body_ort or stadt
    for term, land in regions.laender.items():
        if _contains(title, term) or _contains(body, term):
            score += 1
            land_ort = land_ort or {"DE": "Deutschland", "CH": "Schweiz", "AT": "Österreich"}.get(land, land)
    return score, ort or body_ort or land_ort


def guess_category(item: NewsItem, settings: Settings) -> str:
    text = f"{item.title} {item.summary}".lower()
    best, best_hits = settings.categories[0].slug if settings.categories else "news", 0
    for cat in settings.categories:
        hits = sum(1 for h in cat.hints if _contains(text, h))
        if hits > best_hits:
            best, best_hits = cat.slug, hits
    if best_hits == 0 and item.kind == "kino":
        return "kino"
    if best_hits == 0 and item.kind == "event":
        return "events"
    return best


def similar(a: str, b: str, threshold: float = 0.82) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def quelle_nach_name(name: str, quellen: list[Source]) -> Source | None:
    """Quelle zu einem Meldungsnamen: exakt oder „<Quelle> · <Verlag>“, der längste bekannte Name gewinnt.

    Quellennamen enthalten selbst „ · “ („Google News EN · Kollywood“); ein bloßes Präfix („Google News EN“) trifft
    nichts (Review 12.11.: max_items griff für Google-News-Meldungen mit Verlag nicht)."""
    name = name or ""
    treffer = [q for q in quellen if name == q.name or name.startswith(f"{q.name} · ")]
    return max(treffer, key=lambda q: len(q.name), default=None)


def quelle_fuer(item: NewsItem, settings: Settings) -> Source | None:
    return quelle_nach_name(item.source, settings.sources)


def hat_bezug(item: NewsItem, settings: Settings) -> bool:
    """Nennt die Meldung einen Begriff mit Bezug zur tamilischen Community ([bezug] in sources.toml)?"""
    text = f"{item.title} {item.summary}".lower()
    return any(_contains(text, term, suffix=2) for term in settings.bezug)


_DEUTSCH_RE = re.compile(
    r"\b(?:und|oder|das|dem|nach|mit|für|vom|zum|zur|bei|über|gegen|sich|ist|sind|wird|werden|nicht|auch|ein|eine|"
    r"einer|einen|wie|auf|im|tamilisch\w*|tamile|tamilen|tamilin\w*)\b|[äöüß]", re.I)


def deutschsprachig(text: str) -> bool:
    """Deutscher Text? Ein Funktionswort, das es im Englischen nicht gibt („nach“, „mit“, „wie“; bewusst nicht „die“,
    „in“, „an“, „von“, „aus“), ein deutsches Wort für Tamilen/tamilisch oder ein Umlaut. Englische und tamilische
    Meldungen treffen das nicht."""
    return _DEUTSCH_RE.search(text) is not None


def dach_hinweis(text: str, regions: Regions) -> bool:
    """Nennt der Text DACH als Adjektiv oder Variante ([regions] dach_hinweise: German, Austrian, Schweizer, ஜேர்மனி)?
    Nur für die Ausland-Regel; das Ranking zählt weiter nur [regions.laender] und Städte."""
    for t in regions.dach_hinweise:
        if _TAMIL_SCRIPT.search(t):
            if _contains(text, t):
                return True
        elif re.search(rf"(?<![\w]){re.escape(t)}", text, re.I):  # Wortanfang: deutsch → deutsche, Deutschland
            return True
    return any(_contains(text, t) for t in regions.dach_hinweise_wort)  # ganzes Wort: „Sion“, nicht „Sionist“


def _ohne_verlag(item: NewsItem, source: Source | None) -> str:
    """Titel und Text ohne den Verlagsanhang von Google News („… - The Hindu“, „…  The Hindu“): Der Verlag steht im
    Quellennamen nach der Quelle („Google News EN · Kollywood · The Hindu“) und ist kein Inhalt (Prüfung 12.11.: „The
    Hindu“ zählte als tamilischer Bezug „hindu“)."""
    title, summary = item.title, item.summary
    verlag = item.source[len(source.name) + 3:].strip() if source and item.source.startswith(f"{source.name} · ") else ""
    if verlag:
        title = re.sub(rf"\s*[-–—|]?\s*{re.escape(verlag)}\s*$", "", title)
        summary = re.sub(rf"\s*{re.escape(verlag)}\s*$", "", summary)
    return f"{title} {summary}"


def _kino(item: NewsItem, settings: Settings, source: Source | None, text: str) -> bool:
    """Kino/Entertainment für die Ausland-Regel: Kategorie-Hinweise, eine Quelle mit `kollywood = true` oder ein Begriff
    aus [bezug] kollywood (Stars). Entscheidung 12.11.: guess_category allein ergab „news“ für „Rajinikanth meets Tamil
    Nadu Chief Minister“ und „Ilaiyaraaja honoured by India“."""
    if source and source.kollywood:
        return True
    if any(_contains(text, t) for t in settings.kollywood):  # ganzes Wort: „vijay“ trifft nicht „Vijayan“
        return True
    return guess_category(item, settings) in ("kino", "entertainment")


def ohne_dach_grund(item: NewsItem, settings: Settings, source: Source | None) -> str:
    """Warum eine Nachricht ohne DACH-Bezug keine Story wird: „fremdes_kino“, „ausland“ oder „“ (bleibt).

    Gilt nur für Nachrichten (kind = news) mit `dach_score` 0 aus Quellen ohne Land (Google News, Tamil Guardian,
    The Hindu, Lankasri). Ein DACH-Hinweis (German, Schweizer, ஜேர்மனி) oder deutscher Text (deutschsprachige Presse
    ist DACH-Presse) zählt als DACH-Bezug (Prüfung 12.11.). Fremdes Kino: mehr Begriffe aus [bezug] fremdkino als aus
    [bezug] terms (Tollywood-Bilanz, die Kollywood nur nennt). Ausland: ein Ort aus [regions] ausland oder eine Region
    aus [regions] herkunft (Sri Lanka, Tamil Nadu) – außer bei Kino und Entertainment (Kategorie, Kollywood-Quelle oder
    Star, siehe `_kino`), die als Kollywood-Meldungen gewollt sind (Fund und Entscheidung 12.11.)."""
    if item.kind != "news" or item.dach_score > 0 or (source and source.country):
        return ""
    text = _ohne_verlag(item, source)
    if dach_hinweis(text, settings.regions) or deutschsprachig(text):
        return ""
    fremd = sum(1 for t in settings.fremdkino if _contains(text, t, suffix=2))
    if fremd and fremd > sum(1 for t in settings.bezug if _contains(text, t, suffix=2)):
        return "fremdes_kino"
    if _kino(item, settings, source, text):
        return ""
    orte = settings.regions.ausland + settings.regions.herkunft
    return "ausland" if any(_contains(text, t) for t in orte) else ""


_APOSTROPHE = str.maketrans("", "", "'’ʼ‘`´")
_BESITZ_S_RE = re.compile(r"['’ʼ‘`´]s\b", re.I)  # „Maaveerar's Day“ → „Maaveerar Day“


def _ohne_zeichen(text: str) -> str:
    """Kleinbuchstaben ohne Formatzeichen (ZWJ, ZWNJ, ZWSP, weiches Trennzeichen), Apostrophe und Diakritika
    („Māvīrar Nāḷ“ → „mavirar nal“, „Heroes’“ → „heroes“); tamilische Schrift bleibt sonst unverändert (Vokalzeichen
    und Pulli sind dort Teil der Buchstaben)."""
    text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    out = []
    for c in _BESITZ_S_RE.sub("", text).translate(_APOSTROPHE).lower():
        if "\u0b80" <= c <= "\u0bff":
            out.append(c)
        else:
            out.append("".join(x for x in unicodedata.normalize("NFKD", c) if not unicodedata.combining(x)))
    return "".join(out)


def gedenktermin(item: NewsItem, settings: Settings) -> bool:
    """Termin (kein Bericht), der einen Begriff aus [blocklist] termine nennt – z. B. Maaveerar-Gedenken mit
    LTTE-Bezug. Gilt für alle Terminquellen (Entscheidung Luis 13.11.2026): Kalender lassen solche Termine schon beim
    Abruf weg, `select` sortiert sie aus allen übrigen Quellen aus (Abnahme-Szenario 90)."""
    if item.kind != "event":
        return False
    text = _ohne_zeichen(f"{item.title} {item.summary}")
    museum = "museum" in _ohne_zeichen(item.title)
    for begriff in (_ohne_zeichen(t) for t in settings.blocklist_termine):
        if begriff == "national heroes" and museum:
            continue  # „National Heroes Museum“ ist kein Gedenktermin
        if _TAMIL_SCRIPT.search(begriff):
            if begriff.rstrip("\u0bcd") in text:
                return True
        elif re.search(r"(?<![^\W_])" + re.escape(begriff), text):  # Wortanfang: „Maaveerarnaal“, „Maaveerars Day“
            return True
    # Ganzes Wort ([blocklist] termine_wort): „Kittu“, nicht „Kittur“; „கிட்டு“, nicht „கிட்டும்“ (Verb). Tamilische
    # Vokalzeichen sind für `\w` keine Buchstaben, deshalb zählt der ganze Tamil-Block als Wortinneres.
    for begriff in (_ohne_zeichen(t) for t in settings.blocklist_termine_wort):
        if re.search(rf"(?<![\w\u0b80-\u0bff]){re.escape(begriff)}(?![\w\u0b80-\u0bff])", text):
            return True
    return False


def veranstalter_gesperrt(namen: list[str], settings: Settings) -> bool:
    """Ein Name aus [blocklist] veranstalter steht als ganzes Wort in einem der Veranstalternamen (Entscheidung Luis
    13.11.: Termine des Veranstalters STCC kommen nicht automatisch)."""
    for name in (_ohne_zeichen(n) for n in namen if n):
        for begriff in (_ohne_zeichen(t) for t in settings.blocklist_veranstalter):
            if re.search(rf"(?<![\w\u0b80-\u0bff]){re.escape(begriff)}(?![\w\u0b80-\u0bff])", name):
                return True
    return False


def termin_veraltet(item: NewsItem, settings: Settings, now: datetime) -> bool:
    """Alter Bericht statt Termin: laut Quelle älter als `event_max_alter_tage` und kein Datum in der Zukunft.

    Termin-Rubriken mit Archiv (z. B. Swiss Tamil Info · Events) liefern monatealte Berichte; ihr `published` ist der
    Abrufzeitpunkt. Ohne echtes Datum (Kalender, Termin-Seiten) gibt es keine Altersprüfung. Ein Datum ohne Jahr im
    Text wird vom Veröffentlichungstag aus gelesen, nicht von heute."""
    echt = item.source_published
    if item.kind != "event" or echt is None or echt >= now - timedelta(days=settings.event_max_alter_tage):
        return False
    heute = now.astimezone(dates.TZ).date()
    raw = str((item.facts or {}).get("event_datum") or "")[:10]
    try:
        if raw and date.fromisoformat(raw) >= heute:
            return False
    except ValueError:
        pass
    termine = dates.alle_daten(f"{item.title}\n{item.summary}", now=echt.astimezone(dates.TZ))
    return not any(d >= heute for d in termine)


def select(
    items: list[NewsItem],
    settings: Settings,
    seen_uids: set[str],
    recent_titles: list[str],
    now: datetime | None = None,
    zaehler: Counter | None = None,
) -> list[NewsItem]:
    """Die relevantesten neuen Meldungen, DACH zuerst, dann nach Punkten und Datum.

    `zaehler` (optional) zählt, was herausfällt: `termin_veraltet` (alter Bericht aus einer Termin-Quelle),
    `ausland` (Termin an einem Ort außerhalb von DACH, Nachricht aus dem Ausland ohne DACH-Bezug), `fremdes_kino`
    (Telugu, Bollywood … ohne DACH-Bezug) und `ohne_bezug` (Quelle mit bezug_noetig, aber kein Begriff
    aus [bezug])."""
    now = now or datetime.now(timezone.utc)
    zaehler = zaehler if zaehler is not None else Counter()
    cutoff = now - timedelta(hours=settings.max_age_hours)
    per_source: dict[str, int] = {}
    picked: list[NewsItem] = []
    titles = list(recent_titles)
    for item in sorted(items, key=lambda i: i.published, reverse=True):
        text = f"{item.title} {item.summary}".lower()
        if item.uid in seen_uids:
            continue
        if item.kind == "news" and item.published < cutoff:
            continue
        if any(_contains(text, term) for term in settings.blocklist):
            continue
        source = quelle_nach_name(item.source, settings.sources)
        if source and source.kind != "news" and item.kind == "news":
            item.kind = source.kind
        if termin_veraltet(item, settings, now):
            zaehler["termin_veraltet"] += 1
            continue
        if gedenktermin(item, settings):  # gilt seit 13.11. für alle Terminquellen (Entscheidung Luis), nicht nur Kalender
            zaehler["gedenktermin"] += 1
            continue
        item.score = score_item(item, settings.keywords)
        item.dach_score, item.ort = dach_score(item, settings.regions)
        ausland = item.dach_score == 0 and any(_contains(text, t) for t in settings.regions.ausland)
        if ausland and item.kind == "event":
            zaehler["ausland"] += 1
            continue  # Termin im Ausland, auch wenn die Quelle aus DACH berichtet
        if source and source.country and not item.ort and not ausland:
            item.ort = {"DE": "Deutschland", "CH": "Schweiz", "AT": "Österreich"}.get(source.country, source.country)
            item.dach_score = max(item.dach_score, 1)
        if source and source.bezug_noetig and not hat_bezug(item, settings):
            zaehler["ohne_bezug"] += 1  # allgemeine Meldung der Quelle ohne tamilischen Bezug (Entscheidung 09.11.)
            continue
        grund = ohne_dach_grund(item, settings, source)
        if grund:
            zaehler[grund] += 1  # Nachricht aus dem Ausland oder aus fremdem Kino ohne DACH-Bezug (Fund 12.11.)
            continue
        needed = None
        if source and source.min_score is not None:
            needed = source.min_score  # 0 = vertrauenswürdige Quelle, alles durchlassen
        elif item.kind == "news":
            needed = settings.min_score_dach if item.dach_score > 0 else settings.min_score
        if needed and item.score < needed:
            continue
        twin = next((p for p in picked if similar(item.title, p.title)), None)
        if twin is not None:
            twin.related.append(item)
            continue
        if any(similar(item.title, t) for t in titles):
            continue
        key = source.name if source else item.source
        limit = source.max_items if source else settings.max_articles
        if per_source.get(key, 0) >= limit:
            continue
        per_source[key] = per_source.get(key, 0) + 1
        item.category_hint = guess_category(item, settings)
        titles.append(item.title)
        picked.append(item)
    picked.sort(key=lambda i: (i.dach_score > 0, i.score + i.dach_score, i.published), reverse=True)
    return picked
