"""Orchestrator der Redaktion v2: deterministisch, Sprachmodelle nur in den Rollen.

  scan (Timer, alle 3 Minuten)   Quellen → Vorfilter → Signal (Grauzone) → Cluster → Story + Job
  worker (Dienst)                recherche → gate → schreiben → faktencheck → lektorat → seo → endpruefung → bild
                                 → Entwurf „neu“
  Gate scheitert                 nachrecherche (ohne Modell, höchstens zwei Runden) → recherche → gate …; danach
                                 pruefung (zweite KI): schreiben (notfalls Kurzmeldung) oder verwerfen mit Grund
  kino                           Kinoprogramm → Textvorlage → Entwurf (ohne Modell)
  Mensch (Cockpit)               freigeben → Publisher → WordPress

Ohne neue Treffer gibt es keinen Modellaufruf. Am Budget scheiternde Jobs warten (wartet_budget), Freigabe und
Veröffentlichung laufen weiter.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import hashlib
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable

from .. import filtering, images, notify, schalter, sources
from ..agents import (Kontext, cluster, copydesk, factcheck, media, nachrecherche, pruefer, relevance, research,
                      schreiben, seo)
from ..config import Settings
from ..pipeline import Result, category_label, quelle_name, refresh_kino, stale_event_date
from ..store import OPEN_STATES, Store, now_iso
from ..wordpress import slugify
from ..writer import split_source_suffix
from . import costs, jobs, repo
from .providers import Claude, budget_fuer, usage_protokollieren

log = logging.getLogger(__name__)

Handler = Callable[[Kontext, dict], list[tuple[str, dict]]]


OHNE_MODELL = ("gate", "bild", "kino", "nachrecherche")  # Schritte, die auch ohne API-Schlüssel laufen


def kontext(settings: Settings, store: Store, client=None, **kw) -> Kontext:
    """Kontext für Rollen und Jobs. Ohne Client und ohne ANTHROPIC_API_KEY gibt es kein Modell (claude = None):
    Scan und Kino laufen, Recherche-Jobs warten auf den Worker mit Schlüssel oder den Agent-Modus."""
    import os

    budget = budget_fuer(settings, store)
    claude = None
    if client is not None or os.environ.get("ANTHROPIC_API_KEY"):
        claude = Claude(settings, store, client=client, budget=budget)
    return Kontext(settings=settings, store=store, claude=claude, budget=budget, **kw)


# ---- Scan -------------------------------------------------------------------------------------

def _event_bald(item: sources.NewsItem, now: datetime, tage: int = 7) -> bool:
    raw = str((item.facts or {}).get("event_datum") or "")[:10]
    try:
        d = date.fromisoformat(raw)
    except ValueError:
        return False
    return now.date() <= d <= (now + timedelta(days=tage)).date()


def _titel(item: sources.NewsItem) -> str:
    titel = sources.clean_text(item.title)
    if item.source.lower().startswith("google news"):
        titel, _ = split_source_suffix(titel)
    return titel


def _offener_entwurf(store: Store, story_id: int) -> dict | None:
    row = store.db.execute(
        "SELECT id FROM drafts WHERE story_id = ? AND status IN ('neu', 'bearbeitet', 'zurueckgestellt') "
        "ORDER BY id DESC LIMIT 1", (story_id,)).fetchone()
    return store.get_draft(row[0]) if row else None


def scan(ctx: Kontext, items: list[sources.NewsItem] | None = None) -> dict:
    """Ein Scan: neue Treffer werden Storys (mit Job) oder reichern bestehende Storys an. Gibt Zählwerte zurück.
    Hält der Schalter „redaktion“ an – vorher oder mittendrin –, endet der Scan sauber: keine halbe Story, und was
    nicht verarbeitet ist, bleibt ungesehen für den nächsten Scan."""
    if schalter.gestoppt(ctx.store, "redaktion"):  # Stopp-Schalter: kein Abruf der Quellen, keine Story, kein Job
        return {"angehalten": 1}
    try:
        return _scan(ctx, items)
    except schalter.Gestoppt:
        log.info("Scan angehalten (Schalter)")
        return {"angehalten": 1}


def _scan(ctx: Kontext, items: list[sources.NewsItem] | None = None) -> dict:
    s, store = ctx.settings, ctx.store
    now = ctx.uhr()
    items = items if items is not None else sources.fetch_all(s, store)
    seen = store.seen_uids()
    stats: Counter = Counter(gesammelt=len(items))
    stats["kino_aktualisiert"] = len(refresh_kino(items, store, seen))
    # Ähnliche Titel nicht verwerfen (wie v1), sondern dem Clustering geben: sie reichern bestehende Storys an
    aussortiert: Counter = Counter()
    picked = filtering.select(items, s, seen, [], now=now, zaehler=aussortiert)
    bezahlt = repo.bezahlte_storys_heute(store, costs.tag_start(now).astimezone(timezone.utc).isoformat(timespec="seconds"))
    grau = relevance.grauzone(items, s, seen, {i.uid for i in picked}, now) if bezahlt < s.entwuerfe_tag else []
    stats["grauzone"] = len(grau)
    if grau:
        aus_grauzone, beurteilt = relevance.pruefen(ctx, grau)
        stats["grauzone_angenommen"] = len(aus_grauzone)
        picked += aus_grauzone
        angenommen = {i.uid for i in aus_grauzone}
        for item in grau:  # nur, was Haiku wirklich beurteilt und abgelehnt hat, gilt als gesehen
            if item.uid in beurteilt and item.uid not in angenommen:
                store.mark(item.uid, item.title, item.url, item.source, "irrelevant")
    stats["relevant"] = len(picked)
    stats.update(aussortiert)  # termin_veraltet, ausland, ohne_bezug – in der Laufnotiz nur, wenn größer 0
    limit_gemeldet = False
    neue_storys: dict[int, int] = {}  # Index der Zuordnung → angelegte Story (für Meldungen desselben Scans)
    schalter.pruefen(store, "redaktion")
    zuordnungen = cluster.zuordnen(ctx, picked)
    for idx, z in enumerate(zuordnungen):
        schalter.pruefen(store, "redaktion")  # vor jeder Meldung: entweder ganz oder gar nicht
        item = z.item
        publisher = quelle_name(item)
        if z.bezug is not None:
            # dieselbe Story wie eine frühere Meldung des Scans: deren neue Story – oder die bestehende, der das Modell
            # den Grenzfall zugeordnet hat
            ziel = neue_storys.get(z.bezug) or zuordnungen[z.bezug].story_id
            if not ziel:
                continue  # die erste Meldung wurde nicht angelegt (Tageslimit/veraltet): diese auch nicht
            z.story_id = ziel
        if item.kind == "event":
            vergangen = stale_event_date(item, "", s, now=now)
            if vergangen:
                store.mark(item.uid, item.title, item.url, item.source, "veraltet")
                stats["veraltet"] += 1
                continue
        if z.story_id:
            neu = research.dokumente_aus_meldung(ctx, z.story_id, item, publisher)
            store.mark(item.uid, item.title, item.url, item.source, "angereichert")
            if neu:
                stats["angereichert"] += 1
                store.event("story_angereichert", story=z.story_id, titel=item.title, quelle=item.url, grund=z.grund)
                if neu_starten(store, z.story_id, f"Neue Quelle: {publisher}"):
                    stats["neu_gestartet"] += 1
                offen = _offener_entwurf(store, z.story_id)
                if offen:
                    store.update_draft(offen["id"], hinweise=offen["hinweise"] + [f"Neue Quelle: {publisher} – {item.url}"],
                                       weitere_quellen=offen["weitere_quellen"] + [{"name": publisher, "url": item.url}],
                                       nur_status=OPEN_STATES)
            continue
        typ = {"kino": "kino", "event": "event"}.get(item.kind, "news")
        if typ != "kino" and bezahlt >= s.entwuerfe_tag:
            stats["tageslimit"] += 1
            if not limit_gemeldet:
                store.event("tageslimit", limit=s.entwuerfe_tag, offen=len(picked))
                limit_gemeldet = True
            continue  # nicht als gesehen markieren: kommt morgen wieder dran, wenn es dann noch frisch ist
        signal = getattr(item, "signal", None) or {}
        relevanz = signal.get("relevanz") or relevance.heuristik(item, s)
        prio = (jobs.PRIO_EVENT_BALD if typ == "event" and _event_bald(item, now)
                else jobs.PRIO_NEWS if typ == "news" else jobs.PRIO_NORMAL)
        sid = repo.story_anlegen(
            store, typ=typ, titel=_titel(item), kategorie=item.category_hint or ("kino" if typ == "kino" else "news"),
            ort=item.ort, region=signal.get("land", ""), schluessel=cluster.schluessel(item), prioritaet=prio,
            relevanz=relevanz, begruendung=signal.get("grund") or f"Vorfilter: {item.score} Punkte, DACH {item.dach_score}",
            sensibel=signal.get("risiko") == "sensibel",
        )
        neue_storys[idx] = sid
        research.dokumente_aus_meldung(ctx, sid, item, publisher)
        if typ == "kino":
            jobs.einreihen(store, sid, "kino", prio=prio, payload={
                "fakten": item.facts or {}, "fingerprint": item.fingerprint, "uid": item.uid, "quelle": item.source,
                "url": item.url})
        else:
            jobs.einreihen(store, sid, "recherche", prio=prio, payload={
                "uid": item.uid, "quelle": item.source, "quelle_bild": item.image_url, "url": item.url,
                "fakten": item.facts or {}})
            bezahlt += 1
        store.mark(item.uid, item.title, item.url, item.source, "story")
        stats["storys"] += 1
    return dict(stats)


# ---- Schritte -----------------------------------------------------------------------------------

def _story(ctx: Kontext, job: dict) -> dict:
    story = repo.story(ctx.store, job["story_id"])
    if story is None:
        raise RuntimeError(f"Story {job['story_id']} fehlt")
    return story


def _letzte_fassung(ctx: Kontext, story_id: int) -> dict:
    for v in reversed(repo.fassungen(ctx.store, story_id=story_id)):
        if v["rolle"] in ("text", "ueberarbeitung", "lektorat", "seo", "pruefung"):
            return {k: w for k, w in v["inhalt"].items() if k not in ("faktencheck", "pruefung")}
    raise RuntimeError("Keine Textfassung vorhanden")


# Nutzdaten, die von Schritt zu Schritt weiterreisen (gruende/fehlend: Fehlstellen für die Nachrecherche;
# kurzmeldung/nur_claims: Entscheidung der zweiten KI; endpruefung/fc_ungedeckt: Prüfung des Entwurfs)
WEITER = ("hinweise", "uid", "quelle", "quelle_bild", "url", "fakten", "runde", "gruende", "fehlend", "kurzmeldung",
          "nur_claims", "endpruefung", "fc_ungedeckt")


def _weiter(payload: dict, **neu) -> dict:
    out = {k: payload[k] for k in WEITER if k in payload}
    out.update(neu)
    return out


def termin_vorbei(ctx: Kontext, story: dict, docs) -> str:
    """Datum eines Termins, wenn er schon vorbei ist („“ sonst). Erst die strukturierten Daten der Quelle; ohne sie
    das **späteste** Datum im Text – Veranstaltungsseiten nennen den Termin oft nur im Text, und davor stehen gern das
    Veröffentlichungsdatum oder frühere Termine. Ein Termin in der Zukunft hält die Story also immer offen."""
    if story["typ"] != "event":
        return ""
    from .. import dates

    now = ctx.uhr()
    when = None
    for d in docs:
        if d.art == "daten":
            try:
                raw = str(json.loads(d.text or "{}").get("event_datum") or "")[:10]
                when = date.fromisoformat(raw) if raw else None
            except (ValueError, AttributeError):
                when = None
            if when:
                break
    if when is None:
        kandidaten = [t for d in docs if d.art in ("volltext", "zusammenfassung")
                      for t in dates.alle_daten(f"{d.titel}\n{d.text[:4000]}", now=now)]
        when = max(kandidaten) if kandidaten else None
    if when is None:
        return ""
    cutoff = (now - timedelta(hours=ctx.settings.max_age_hours)).date()
    return when.isoformat() if when < cutoff else ""


def schritt_recherche(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    if story["status"] != "recherche_erforderlich":  # in der Nachrecherche bleibt die Story im Reiter sichtbar
        if not repo.story_setzen(ctx.store, story["id"], nur_offen=True, status="recherche"):
            return []  # inzwischen fertig oder verworfen
    docs = research.belege_sammeln(ctx, story)
    vorbei = termin_vorbei(ctx, story, docs)
    if vorbei:  # vor jedem bezahlten Aufruf: ein vergangener Termin wird kein Beitrag
        repo.story_setzen(ctx.store, story["id"], status="verworfen", notiz=f"Termin vom {vorbei} liegt zurück")
        ctx.store.event("verworfen", story=story["id"], titel=story["titel"], grund=f"Termin vom {vorbei} liegt zurück")
        return []
    claims, widersprueche, fehlend, verworfen = research.claims_ziehen(ctx, story, docs, job["id"])
    repo.claims_setzen(ctx.store, story["id"], claims)
    hinweise = [f"Recherche: Claim verworfen – {v}" for v in verworfen]
    return [("gate", _weiter(job["payload"], widersprueche=widersprueche, fehlend=fehlend,
                             hinweise=job["payload"].get("hinweise", []) + hinweise))]


def schritt_gate(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    docs = repo.dokumente(ctx.store, story["id"])
    g = factcheck.gate(story, docs, repo.claims(ctx.store, story["id"]), job["payload"].get("widersprueche", []))
    repo.claims_setzen(ctx.store, story["id"], g.claims)
    repo.story_setzen(ctx.store, story["id"], laenge=g.laenge, sensibel=g.sensibel or story["sensibel"])
    hinweise = job["payload"].get("hinweise", []) + g.hinweise + [f"Fehlt: {f}" for f in job["payload"].get("fehlend", [])]
    if not g.ok:
        return _nicht_belegt(ctx, story, job["payload"], g.gruende, job["payload"].get("fehlend", []))
    repo.story_setzen(ctx.store, story["id"], status="geprueft")
    return [("schreiben", _weiter(job["payload"], hinweise=hinweise, runde=1))]


def schritt_schreiben(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    p = job["payload"]
    docs = repo.dokumente(ctx.store, story["id"])
    claims = repo.claims(ctx.store, story["id"])
    if p.get("nur_claims"):  # Kurzmeldung: genau die Claims, die die zweite KI als tragend genannt hat
        claims = [c for c in claims if c.id in set(p["nur_claims"])]
    text = schreiben.schreiben(ctx, story, claims, docs, story.get("laenge") or "normal",
                               anmerkung=p.get("anmerkung", ""), vorige=p.get("vorige"), job_id=job["id"])
    runde = int(p.get("runde", 1))
    repo.fassung_speichern(ctx.store, story["id"], "text" if runde == 1 else "ueberarbeitung", text.model_dump(),
                           von=ctx.settings.modell_fuer("dossier" if story["typ"] == "dossier" else "text"))
    repo.story_setzen(ctx.store, story["id"], status="geschrieben")
    return [("faktencheck", _weiter(p, runde=runde))]


def schritt_faktencheck(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    p = job["payload"]
    runde = int(p.get("runde", 1))
    felder = _letzte_fassung(ctx, story["id"])
    claims = repo.claims(ctx.store, story["id"])
    urteile = factcheck.text_pruefen(ctx, story, felder, [c for c in claims if c.support == "bestaetigt"],
                                     repo.dokumente(ctx.store, story["id"]), job["id"])
    a = factcheck.auswerten(urteile)
    repo.fassung_speichern(ctx.store, story["id"], "faktencheck",
                           {**felder, "faktencheck": [u.model_dump() for u in urteile]})
    if a.kern_probleme:
        if runde == 1:
            return [("schreiben", _weiter(p, runde=2, anmerkung=factcheck.anmerkung(a), vorige=felder))]
        grund = ("Faktencheck: Kernaussage auch nach Überarbeitung nicht gedeckt – " +
                 "; ".join(u.satz[:120] for u in a.kern_probleme))
        if p.get("kurzmeldung") or p.get("endpruefung"):  # schon nach Nachrecherche bzw. zweiter KI: Ende
            return _verwerfen(ctx, story, f"{grund} (nach Nachrecherche und zweiter KI)")
        return _nicht_belegt(ctx, story, p, [grund], p.get("fehlend", []))
    hinweise = list(p.get("hinweise", []))
    hinweise += [f"Faktencheck: nicht belegt (bitte prüfen) – „{u.satz[:160]}“" for u in a.markiert]
    if runde == 2:
        hinweise.append("Faktencheck: Text nach Beanstandung einmal überarbeitet")
    repo.story_setzen(ctx.store, story["id"], status="geprueft_text")
    # Nebensätze, die der Faktencheck nicht gedeckt fand, streicht die zweite KI am Ende in jedem Fall
    return [("lektorat", _weiter(p, hinweise=hinweise, fc_ungedeckt=[u.satz for u in a.markiert]))]


def schritt_lektorat(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    felder = _letzte_fassung(ctx, story["id"])
    felder = {k: v for k, v in felder.items() if k != "faktencheck"}
    claims = [c for c in repo.claims(ctx.store, story["id"]) if c.support == "bestaetigt"]
    h = copydesk.pruefen(felder, claims, repo.dokumente(ctx.store, story["id"]), story.get("laenge") or "normal",
                         ctx.settings.category_slugs())
    h += copydesk.lektorat(ctx, story["id"], felder, job["id"])
    repo.fassung_speichern(ctx.store, story["id"], "lektorat", felder)
    return [("seo", _weiter(job["payload"], hinweise=job["payload"].get("hinweise", []) + h))]


def schritt_seo(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    felder, h = seo.optimieren(ctx, story["id"], _letzte_fassung(ctx, story["id"]), job["id"])
    repo.fassung_speichern(ctx.store, story["id"], "seo", felder)
    return [("endpruefung", _weiter(job["payload"], hinweise=job["payload"].get("hinweise", []) + h))]


# ---- Nachrecherche und zweite KI (Auftrag Luis, 13.11.2026) ---------------------------------------------

def _verwerfen(ctx: Kontext, story: dict, grund: str) -> list[tuple[str, dict]]:
    if repo.story_setzen(ctx.store, story["id"], nur_offen=True, status="verworfen", notiz=grund[:900]):
        ctx.store.event("verworfen", story=story["id"], titel=story["titel"], grund=grund[:300])
    return []


def _nicht_belegt(ctx: Kontext, story: dict, p: dict, gruende: list[str], fehlend: list[str]) -> list[tuple[str, dict]]:
    """Gate oder Faktencheck gescheitert: kein Endzustand, sondern Nachrecherche (höchstens zwei Runden), danach
    entscheidet die zweite KI. „recherche_erforderlich“ heißt im Cockpit „In Nachrecherche“."""
    sid = story["id"]
    n = nachrecherche.runden(ctx.store, sid)
    hinweise = [h for h in p.get("hinweise", []) if h.startswith(("Nachrecherche", "Neue Quelle"))]
    weiter = _weiter(p, gruende=list(gruende), fehlend=list(fehlend), hinweise=hinweise)
    for k in ("kurzmeldung", "nur_claims", "endpruefung", "fc_ungedeckt"):
        weiter.pop(k, None)
    grund = "; ".join(gruende)
    weiter_mit = "nachrecherche" if n < nachrecherche.MAX_RUNDEN else "pruefung"
    ctx.store.event("recherche_erforderlich", story=sid, titel=story["titel"], gruende=gruende, weiter=weiter_mit)
    if weiter_mit == "nachrecherche":
        notiz = f"In Nachrecherche (Runde {n + 1} von {nachrecherche.MAX_RUNDEN}); {grund}"
    else:
        notiz = f"Zweite KI prüft nach {n} Runden Nachrecherche; {grund}"
    if not repo.story_setzen(ctx.store, sid, nur_offen=True, status="recherche_erforderlich", notiz=notiz[:900]):
        return []
    return [(weiter_mit, weiter)]


def schritt_nachrecherche(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    """Belege für die Fehlstellen suchen (ohne Modell). Neues gefunden → Recherche und Gate erneut; nichts gefunden →
    zweite KI. Ohne Modell (Agent-Modus) geht die Story mit Fehlstellen und Suchanfragen in den Export."""
    story = _story(ctx, job)
    sid, p = story["id"], job["payload"]
    runde = nachrecherche.runden(ctx.store, sid)
    erg = nachrecherche.nachrecherchieren(ctx, story, p.get("fehlend", []), p.get("gruende", []), runde)
    usage_protokollieren(ctx.store, rolle="nachrecherche", provider="suche", modell="ohne-ki", story_id=sid,
                         job_id=job["id"])
    ctx.store.event("nachrecherche", story=sid, runde=runde, fehlend=erg.fehlend, anfragen=erg.anfragen,
                    neu=len(erg.neu), hinweise=erg.hinweise, gelesen=erg.gelesen, wege=dict(erg.wege),
                    abgelehnt=dict(erg.abgelehnt), ergebnis=erg.zusammenfassung())
    ergebnis = f"Nachrecherche Runde {runde} von {nachrecherche.MAX_RUNDEN}: {erg.zusammenfassung()}"
    gruende = "; ".join(p.get("gruende", []))
    repo.story_setzen(ctx.store, sid, status="recherche_erforderlich",
                      notiz=(f"{ergebnis}; {gruende}" if gruende else ergebnis)[:900])
    if jobs.ist_nachtrag(ctx.store, sid):
        return []  # Nachträge schreibt nur der Agent-Modus: die Story steht mit den neuen Belegen im Export
    weiter = _weiter(p, hinweise=p.get("hinweise", []) + [ergebnis])
    if erg.neu or ctx.claude is None:
        return [("recherche", weiter)]
    return [("pruefung", weiter)]


MAX_PRUEFUNGEN = 10  # Recherche-, Prüf- und Endprüf-Jobs je Story zusammen (alle Runden und Neustarts)


def modell_schritte(store, story_id: int) -> int:
    return store.db.execute("SELECT COUNT(*) FROM workflow_jobs WHERE story_id = ? AND schritt IN "
                            "('recherche', 'pruefung', 'endpruefung')", (story_id,)).fetchone()[0]


def schritt_pruefung(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    """Zweite KI nach der Nachrecherche: schreibbar mit nur belegten Aussagen (notfalls Kurzmeldung) oder verwerfen."""
    story = _story(ctx, job)
    sid, p = story["id"], job["payload"]
    gruende = list(p.get("gruende", []))
    gate_text = f" · Gate: {'; '.join(gruende)}" if gruende else ""
    runden_text = [h for h in p.get("hinweise", []) if h.startswith("Nachrecherche Runde")]
    gate_text += f" · {'; '.join(runden_text)}" if runden_text else ""
    schon = ctx.store.db.execute("SELECT COUNT(*) FROM workflow_jobs WHERE story_id = ? AND schritt = 'pruefung'",
                                 (sid,)).fetchone()[0]
    if modell_schritte(ctx.store, sid) > MAX_PRUEFUNGEN:  # Sicherung gegen einen Kreisel (Neustarts, Runden)
        return _verwerfen(ctx, story, f"Zweite KI: verworfen – {schon - 1}× geprüft, Belege tragen nicht{gate_text}")
    claims = repo.claims(ctx.store, sid)
    urteil = pruefer.story_pruefen(ctx, story, claims, repo.dokumente(ctx.store, sid), gruende, job["id"])
    regel = pruefer.kurzmeldung_regel(story, claims)
    if urteil.entscheidung != "schreiben" or regel:
        grund = urteil.grund if urteil.entscheidung != "schreiben" else f"{regel} (Regel des Radars)"
        return _verwerfen(ctx, story, f"Zweite KI: verworfen – {grund}{gate_text}")
    neu, raus = pruefer.kurzmeldung_claims(claims)
    repo.claims_setzen(ctx.store, sid, neu)
    bestaetigt = [c.id for c in neu if c.support == "bestaetigt"]
    nur = [i for i in urteil.claim_ids if i in set(bestaetigt)] or bestaetigt
    repo.story_setzen(ctx.store, sid, status="geprueft", laenge="event" if story["typ"] == "event" else "kurz",
                      notiz=f"Zweite KI: als Kurzmeldung schreibbar – {urteil.grund}"[:900])
    hinweise = p.get("hinweise", []) + [f"Kurzmeldung nur aus belegten Aussagen (zweite KI: {urteil.grund})"]
    hinweise += [f"Nicht im Text, weil nicht belegt: {c.aussage[:120]}" for c in raus]
    return [("schreiben", _weiter(p, hinweise=hinweise, runde=1, kurzmeldung=1, nur_claims=nur))]


def schritt_endpruefung(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    """Zweite KI vor „neu im Cockpit“: jeder Satz gegen die Dokumente. Ungedeckte Nebensätze (auch die, die der
    Faktencheck nicht gedeckt fand) werden gestrichen; eine ungedeckte Kernaussage heißt einmal Überarbeitung, danach
    verwerfen."""
    from .models import SatzUrteil

    story = _story(ctx, job)
    sid, p = story["id"], job["payload"]
    felder = _letzte_fassung(ctx, sid)
    claims = [c for c in repo.claims(ctx.store, sid) if c.support == "bestaetigt"]
    urteile = pruefer.entwurf_pruefen(ctx, story, felder, claims, repo.dokumente(ctx.store, sid), job["id"])
    beanstandet = {u.satz.strip() for u in urteile if u.urteil != "gedeckt"}
    zusatz = [SatzUrteil(nr=0, satz=s, urteil="ungedeckt", claim_ids=[], fundstelle="", kern=False)
              for s in p.get("fc_ungedeckt", []) if s.strip() not in beanstandet]
    neu, gestrichen, probleme = pruefer.pruefung_anwenden(felder, urteile + zusatz)
    fehlt, _ = pruefer.abdeckung(felder, urteile)  # jeder Satz muss geprüft sein, sonst Überarbeitung
    probleme += [SatzUrteil(nr=0, satz=s, urteil="ungedeckt", claim_ids=[], fundstelle="nicht geprüft", kern=True)
                 for s in fehlt]
    if modell_schritte(ctx.store, sid) > MAX_PRUEFUNGEN:
        return _verwerfen(ctx, story, "Zweite KI (Endprüfung): verworfen – zu viele Prüfrunden")
    modell = ctx.settings.modell_fuer("pruefer")
    repo.fassung_speichern(ctx.store, sid, "pruefung", {**neu, "pruefung": [u.model_dump() for u in urteile]},
                           von=modell)
    if probleme:
        if not p.get("endpruefung"):
            hinweise = p.get("hinweise", []) + ["Zweite KI: Text nach Beanstandung einmal überarbeitet"]
            return [("schreiben", _weiter(p, runde=2, anmerkung=pruefer.anmerkung(probleme), vorige=felder,
                                          endpruefung=1, fc_ungedeckt=[], hinweise=hinweise))]
        return _verwerfen(ctx, story, "Zweite KI (Endprüfung): verworfen – auch nach Überarbeitung nicht durch die "
                                      "Dokumente gedeckt: " + "; ".join(u.satz[:120] for u in probleme))
    hinweise = [h for h in p.get("hinweise", []) if not h.startswith("Faktencheck: nicht belegt")]
    kopf = (f"Geprüft von zweiter KI ({modell}): {len(urteile)} Sätze gegen die Dokumente geprüft, "
            + (f"{len(gestrichen)} gestrichen" if gestrichen else "alle gedeckt"))
    hinweise = [kopf] + hinweise + [f"Zweite KI hat gestrichen: „{s[:160]}“" for s in gestrichen]
    return [("bild", _weiter(p, hinweise=hinweise))]


def _quelle(ctx: Kontext, name: str):
    return filtering.quelle_nach_name(name, ctx.settings.alle_quellen)


def _neues_bild_verwerfen(ctx: Kontext, name: str, asset_id: int) -> None:
    """Nicht übernommenes Bild: den ungebundenen Lizenz-Datensatz entfernen, Datei und Vorschaubild nur, wenn kein
    Entwurf darauf zeigt (bei gleichen Bytes ist es dieselbe Datei wie die des bestehenden Entwurfs)."""
    # Zeigt schon ein Entwurf auf die Datei (festgeschrieben, nur das Binden fehlte), bleibt der Datensatz: sonst
    # hätte der Entwurf ein Bild ohne Lizenz und ohne KI-Kennzeichnung.
    ctx.store._write("DELETE FROM assets WHERE id = ? AND draft_id IS NULL AND NOT EXISTS "
                     "(SELECT 1 FROM drafts WHERE drafts.bild_datei = assets.datei)", (asset_id,))
    _alte_datei_aufraeumen(ctx, name, "")


def _alte_datei_aufraeumen(ctx: Kontext, datei: str | None, neu: str) -> None:
    if not datei or datei == neu or ctx.store.db.execute(
            "SELECT 1 FROM drafts WHERE bild_datei = ? LIMIT 1", (datei,)).fetchone():
        return
    for pfad in (datei, datei.replace(".jpg", "-thumb.jpg")):
        (ctx.settings.bilder_dir / pfad).unlink(missing_ok=True)


def entwurf_anlegen(ctx: Kontext, story: dict, felder: dict, payload: dict, *, typ: str, hinweise: list[str],
                    fakten: dict | None = None, fingerprint: str = "") -> int | None:
    """Bild besorgen, Entwurf in die Warteschlange (Status „neu“), Lizenz und Fassung verknüpfen."""
    s = ctx.settings
    docs = repo.dokumente(ctx.store, story["id"])
    primaer = docs[0] if docs else None
    uid = payload.get("uid") or (primaer.url if primaer else "") or f"story:{story['id']}"
    if story["typ"] == "dossier":
        uid = f"dossier:{story['id']}"
    andere = ctx.store.draft_by_uid(uid)
    if andere and andere.get("story_id") not in (None, story["id"]):
        # Fund 13.11. (Story 117 gegen Entwurf 68): ein eigener Beitrag mit derselben Primärquelle bekommt eine eigene
        # uid – sonst würde er als Dublette verworfen und der Publisher könnte den anderen Post überschreiben
        uid = f"{uid}#story-{story['id']}"
    stem = f"s{story['id']}-{slugify(felder.get('titel') or 'beitrag', 50)}"
    label = category_label(s, felder.get("kategorie") or "news")
    bild, versucht = media.besorgen(ctx, story, felder, stem, kategorie_label=label,
                                    quelle=_quelle(ctx, payload.get("quelle", "")), quelle_bild=payload.get("quelle_bild", ""))
    # Eindeutiger Name (Entwurf, falls schon da, und Inhalts-Hash): nie die Datei eines anderen Entwurfs überschreiben
    vorhanden = ctx.store.draft_by_uid(uid)
    eindeutig = f"{stem}-e{vorhanden['id']}" if vorhanden else f"{stem}-u{hashlib.sha256(uid.encode()).hexdigest()[:6]}"
    eindeutig += "-" + hashlib.sha256(bild.image.data).hexdigest()[:8]
    # Alt-Text: die Bildkarte beschreibt sich selbst („Grafik mit der Überschrift: …“), sonst der des Writers
    if not bild.felder.get("alt"):
        bild.felder["alt"] = felder.get("bild_alt", "")
    name, asset_id = media.speichern(ctx, bild, eindeutig, story["id"])
    try:
        return _entwurf_eintragen(ctx, story, felder, payload, typ=typ, hinweise=hinweise, fakten=fakten,
                                  fingerprint=fingerprint, uid=uid, docs=docs, bild=bild, versucht=versucht, name=name,
                                  asset_id=asset_id)
    except BaseException:  # Abbruch nach dem Speichern: keine Datei und kein Lizenz-Datensatz ohne Entwurf
        try:
            _neues_bild_verwerfen(ctx, name, asset_id)
        except Exception:  # noqa: BLE001 – das Aufräumen darf die ursprüngliche Ausnahme nicht ersetzen
            log.exception("Aufräumen des Bildes %s fehlgeschlagen", name)
        raise


def _entwurf_eintragen(ctx: Kontext, story: dict, felder: dict, payload: dict, *, typ: str, hinweise: list[str],
                       fakten: dict | None, fingerprint: str, uid: str, docs: list, bild: media.Bild, versucht: list,
                       name: str, asset_id: int) -> int | None:
    """Entwurf anlegen oder einen wartenden aktualisieren; Lizenz und Fassung verknüpfen (Bild liegt schon)."""
    s = ctx.settings
    primaer = docs[0] if docs else None
    weitere = [{"name": d.publisher or d.quelle, "url": d.url} for d in docs[1:] if d.url and not d.url.endswith("#daten")]
    if story.get("sensibel"):
        hinweise = ["Sensibles Thema: vor der Freigabe eine zweite Person lesen lassen"] + \
            [h for h in hinweise if not h.startswith("Sensibles Thema")]
    row = {
        "uid": uid, "typ": typ, "story_id": story["id"],
        "herkunft": story.get("herkunft") or "radar", "ereignis_datum": story.get("ereignis_datum") or "",
        "quelle_name": primaer.publisher if primaer else "", "quelle_url": primaer.url if primaer else "",
        "quelle_datum": primaer.published_at if primaer else "", "quelle_sprache": primaer.language if primaer else "de",
        "quelle_bild": payload.get("quelle_bild", ""), "weitere_quellen": weitere,
        "relevanz": story.get("relevanz") or felder.get("relevanz") or 6,
        "begruendung": story.get("begruendung") or felder.get("begruendung", ""),
        "dach_bezug": bool(felder.get("dach_bezug") or story.get("ort")), "ort": felder.get("ort") or story.get("ort") or "",
        "kategorie": felder.get("kategorie") or story.get("kategorie") or "news",
        "titel": felder.get("titel", ""), "teaser": felder.get("teaser", ""), "inhalt_html": felder.get("inhalt_html", ""),
        "schlagworte": felder.get("schlagworte") or [], "seo_titel": felder.get("seo_titel", ""),
        "meta_beschreibung": felder.get("meta_beschreibung", ""), "bild_datei": name, "bild_credit": bild.image.credit,
        "bild_alt": bild.felder.get("alt") or felder.get("bild_alt", ""), "bild_suchbegriff": felder.get("bild_suchbegriff", ""),
        "bild_origin": bild.image.origin, "bild_thema": felder.get("bild_thema", ""), "bild_prompt": felder.get("bild_prompt", ""),
        "event_datum": felder.get("event_datum", ""), "event_ort": felder.get("event_ort", ""),
        "ticket_url": felder.get("ticket_url", ""), "fakten": fakten if fakten is not None else payload.get("fakten") or {},
        "fingerprint": fingerprint, "hinweise": hinweise, "original_json": felder,
    }
    draft_id = ctx.store.insert_draft(row)
    if draft_id is None:
        existing = ctx.store.draft_by_uid(uid)
        if existing and existing["status"] in ("neu", "bearbeitet", "zurueckgestellt"):
            draft_id = existing["id"]
            if von_mensch_bearbeitet(existing):
                # Die Arbeit der Redaktion nie überschreiben: die neue Fassung liegt in den Fassungen, der Entwurf
                # bekommt nur einen Hinweis.
                hinweis = f"Neue Radar-Fassung vom {now_iso()[:16].replace('T', ' ')} (Story {story['id']}) – Text nicht überschrieben, siehe Fassungen"
                ctx.store.update_draft(draft_id, nur_status=OPEN_STATES, hinweise=[hinweis] + [h for h in existing.get("hinweise") or []
                                                                       if not h.startswith("Neue Radar-Fassung")])
                repo.fassung_speichern(ctx.store, story["id"], "entwurf_neu", {**felder, **{k: row[k] for k in repo.FASSUNG_FELDER if k in row},
                                                                     "bild_datei": ""},  # Bild wird verworfen
                                       von="radar", draft_id=draft_id)
                repo.story_setzen(ctx.store, story["id"], status="fertig")
                ctx.store.event("entwurf_nicht_ueberschrieben", id=draft_id, story=story["id"], status=existing["status"])
                _neues_bild_verwerfen(ctx, name, asset_id)
                return draft_id
            if not ctx.store.update_draft(draft_id, von="radar", nur_status=OPEN_STATES,
                                          bild_vorher=existing.get("bild_datei"),
                                          **{k: v for k, v in row.items() if k not in ("uid", "fakten")}):
                existing = None  # inzwischen freigegeben oder anderes Bild: nicht überschreiben
            else:
                _alte_datei_aufraeumen(ctx, existing.get("bild_datei"), name)
        if existing is None or existing["status"] not in OPEN_STATES:
            _neues_bild_verwerfen(ctx, name, asset_id)
            ctx.store.event("entwurf_existiert", story=story["id"], uid=uid)
            repo.story_setzen(ctx.store, story["id"], status="verworfen", notiz="Entwurf zu dieser Meldung existiert schon")
            return None
    images.datei_sicherstellen(bild.image, s.bilder_dir, name)  # Datei gehört jetzt sicher zum Entwurf
    repo.asset_draft_setzen(ctx.store, asset_id, draft_id)
    # Fassung „entwurf“ = genau das, was in der Warteschlange liegt (inkl. Bild) – derselbe Hash wie bei der Freigabe
    endfassung = {**felder, **{k: row[k] for k in repo.FASSUNG_FELDER if k in row}}
    repo.fassung_speichern(ctx.store, story["id"], "entwurf", endfassung, von="radar", draft_id=draft_id)
    repo.story_setzen(ctx.store, story["id"], status="fertig")
    kosten = repo.kosten_story(ctx.store, story["id"])
    ctx.store.event("entwurf", id=draft_id, story=story["id"], titel=row["titel"], kategorie=row["kategorie"], typ=typ,
                    bild=bild.image.origin, relevanz=row["relevanz"], dach=row["ort"], modus="v2",
                    kosten_usd=kosten["usd"], bild_versucht=versucht)
    notify.notify_new(s, [Result(row["titel"], "entwurf", row["kategorie"], f"{s.web_url}/entwurf/{draft_id}",
                                 note=f"Story {story['id']}, ${kosten['usd']:.3f}", draft_id=draft_id)])
    return draft_id


def schritt_bild(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    felder = _letzte_fassung(ctx, story["id"])
    typ = {"event": "event", "kino": "kino_termine"}.get(story["typ"], felder.get("typ") or "artikel")
    entwurf_anlegen(ctx, story, felder, job["payload"], typ=typ, hinweise=job["payload"].get("hinweise", []))
    return []


def kino_text(fakten: dict) -> dict:
    """Textvorlage für ein Kinoprogramm – ohne Sprachmodell. Die Kinoliste hängt render.py automatisch an."""
    film = fakten.get("film") or "Der Film"
    kinos = fakten.get("kinos") or []
    staedte = sorted({k.get("stadt") for k in kinos if k.get("stadt")})
    laender = sorted({k.get("land") for k in kinos if k.get("land")})
    n = len(kinos)
    orte = ", ".join(staedte[:5]) + (f" und {len(staedte) - 5} weiteren Städten" if len(staedte) > 5 else "")
    land_text = {"DE": "Deutschland", "AT": "Österreich", "CH": "der Schweiz"}
    laender_text = " und ".join(land_text.get(x, x) for x in laender) or "im DACH-Raum"
    titel = f"„{film}“ im Kino: {n} {'Spielort' if n == 1 else 'Spielorte'} in {laender_text}"[:90]
    teaser = f"Tamilisches Kino auf der großen Leinwand: „{film}“ läuft diese Woche in {orte or laender_text}."[:220]
    absaetze = [
        f"Gute Nachricht für alle, die tamilisches Kino lieber im Saal als auf dem Handy sehen: „{film}“ läuft in dieser "
        f"Kinowoche in {n} {'Kino' if n == 1 else 'Kinos'} in {laender_text}.",
        f"Gezeigt wird der Film unter anderem in {orte}. Die Spielorte und Termine stehen unten; Vorstellungen sind oft "
        "schnell ausverkauft, eine Reservierung beim Kino lohnt sich.",
        "Die Termine stammen aus den Programmen der Kinos und werden aktualisiert, sobald neue Vorstellungen dazukommen.",
    ]
    html_text = "\n".join(f"<p>{a}</p>" for a in absaetze) + '\n<p class="quelle">Quelle: Kinoprogramme der Kinos</p>'
    return {
        "titel": titel, "teaser": teaser, "inhalt_html": html_text, "kategorie": "kino", "typ": "kino_termine",
        "schlagworte": ["Kino", film, *staedte[:3]][:6], "seo_titel": f"„{film}“ im Kino – Termine"[:60],
        "meta_beschreibung": (f"„{film}“ läuft in {n} Kinos in {laender_text}: alle Spielorte und Termine der Woche auf "
                              "Tamil.de, mit Links zu den Kinos.")[:155],
        "bild_alt": "Kinosaal mit roten Sitzen", "bild_thema": "kino-saal", "bild_prompt": "", "bild_suchbegriff": "cinema hall",
        "event_datum": "", "event_ort": "", "ticket_url": "", "relevanz": 9, "dach_bezug": True,
        "ort": staedte[0] if len(staedte) == 1 else ("Deutschland" if laender == ["DE"] else ""),
        "begruendung": "Kinotermine im DACH-Raum",
    }


def schritt_kino(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    p = job["payload"]
    felder = kino_text(p.get("fakten") or {})
    repo.fassung_speichern(ctx.store, story["id"], "vorlage", felder, von="kino-vorlage")
    usage_protokollieren(ctx.store, rolle="kino", provider="vorlage", modell="ohne-ki", story_id=story["id"],
                         job_id=job["id"])
    entwurf_anlegen(ctx, story, felder, p, typ="kino_termine", fakten=p.get("fakten") or {},
                    fingerprint=p.get("fingerprint", ""),
                    hinweise=["Kino-Vorlage ohne KI: Besetzung und Handlung bei Bedarf ergänzen"])
    return []


SCHRITTE: dict[str, Handler] = {
    "recherche": schritt_recherche, "gate": schritt_gate, "schreiben": schritt_schreiben,
    "faktencheck": schritt_faktencheck, "lektorat": schritt_lektorat, "seo": schritt_seo, "bild": schritt_bild,
    "kino": schritt_kino, "nachrecherche": schritt_nachrecherche, "pruefung": schritt_pruefung,
    "endpruefung": schritt_endpruefung,
}


# ---- Job-Runner ---------------------------------------------------------------------------------

def job_ausfuehren(ctx: Kontext, job: dict) -> str:
    store = ctx.store
    story_jetzt = repo.story(store, job["story_id"]) if job.get("story_id") else None
    if story_jetzt and story_jetzt["status"] in repo.ENDZUSTAND and job["schritt"] != "kino":
        # inzwischen fertig oder verworfen (Redaktion, Import, anderer Weg): der Schritt entfällt, kein Abruf, kein Modell
        store._write("UPDATE workflow_jobs SET status = 'fertig', fehler = ?, aktualisiert = ? WHERE id = ?",
                     (f"Story ist {story_jetzt['status']} – Schritt entfällt", now_iso(), job["id"]))
        return "entfallen"
    if jobs.ist_nachtrag(store, job["story_id"]) and job["schritt"] not in jobs.NACHTRAG_ERLAUBT:
        # Altbestand oder Umweg: ein Nachtrag läuft nie über Worker und Modell, er wartet im Agent-Export
        store._write("UPDATE workflow_jobs SET status = 'fertig', fehler = 'Nachtrag: nur Agent-Modus', aktualisiert = ? "
                     "WHERE id = ?", (now_iso(), job["id"]))
        story = repo.story(store, job["story_id"])
        if story and story["status"] not in ("fertig", "verworfen"):
            repo.story_setzen(store, job["story_id"], status="neu")
        return "nachtrag"
    handler = SCHRITTE.get(job["schritt"])
    if handler is None:
        jobs.fehlgeschlagen(store, job["id"], f"Unbekannter Schritt {job['schritt']}")
        return "fehler"
    try:
        naechste = handler(ctx, job)
    except schalter.Gestoppt as exc:
        # Schalter mitten im Schritt: der Schritt endet ohne Aufruf nach außen, der Job wartet ohne Versuch
        jobs.angehalten(store, job["id"], str(exc), worker=job.get("worker"))
        store.event("angehalten", story=job["story_id"], schritt=job["schritt"], kanal=exc.sperre["kanal"])
        return "angehalten"
    except costs.BudgetErschoepft as exc:
        jobs.wartet_budget(store, job["id"], str(exc))
        store.event("budget", story=job["story_id"], schritt=job["schritt"], grund=str(exc))
        return "wartet_budget"
    except Exception as exc:  # noqa: BLE001 – ein Fehler betrifft nur diesen Job
        log.exception("Job %s (%s) fehlgeschlagen", job["id"], job["schritt"])
        status = jobs.fehlgeschlagen(store, job["id"], f"{type(exc).__name__}: {exc}", worker=job.get("worker"))
        if status == "tot" and job["story_id"]:
            repo.story_setzen(store, job["story_id"], status="fehler", notiz=f"{job['schritt']}: {exc}"[:500])
            store.event("fehler", story=job["story_id"], schritt=job["schritt"], fehler=str(exc)[:300])
        return status
    if not jobs.erledigt(store, job["id"], worker=job.get("worker")):
        # Deadline überschritten und neu vergeben: der andere Worker übernimmt, hier keine Folgeschritte
        log.warning("Job %s gehört nicht mehr %s – Ergebnis verworfen", job["id"], job.get("worker"))
        return "verloren"
    for schritt, payload in naechste:
        runde = payload.get("runde", 1)
        jobs.einreihen(store, job["story_id"], schritt, prio=job["prio"],
                       key=f"{job['story_id']}:{schritt}:{runde}:{job['id']}", payload=payload)
    return "fertig"


def abarbeiten(ctx: Kontext, *, bis: float | None = None, max_jobs: int | None = None, worker: str = "worker") -> Counter:
    """Jobs nacheinander abarbeiten, bis die Schlange leer ist, die Zeit (monotonic) abläuft oder max_jobs erreicht ist."""
    stats: Counter = Counter()
    jobs.aufraeumen(ctx.store)
    jobs.budget_wieder_frei(ctx.store)  # nur Jobs, deren Pause (15 Minuten) abgelaufen ist
    nachrecherche_anstossen(ctx)
    nur = None if ctx.claude is not None else OHNE_MODELL
    while (bis is None or time.monotonic() < bis) and (max_jobs is None or sum(stats.values()) < max_jobs):
        job = jobs.naechster(ctx.store, worker, schritte=nur)
        if job is None:
            break
        stats[job_ausfuehren(ctx, job)] += 1
    return stats


def nachrecherche_anstossen(ctx: Kontext) -> int:
    """Storys auf „recherche_erforderlich“ ohne offenen Job und ohne Entwurf (Bestand von vor der Nachrecherche oder
    ein abgebrochener Schritt) bekommen wieder einen: Nachrecherche, nach zwei Runden die zweite KI (mit Modell) bzw.
    die Recherche für den Agent-Export (ohne Modell). Nachträge stehen nach zwei Runden ohnehin im Export."""
    store = ctx.store
    if schalter.gestoppt(store, "redaktion"):
        return 0
    rows = store.db.execute(
        "SELECT s.id, s.notiz, s.herkunft FROM stories s WHERE s.status = 'recherche_erforderlich' AND s.typ != 'kino' "
        "AND NOT EXISTS (SELECT 1 FROM workflow_jobs j WHERE j.story_id = s.id AND j.status IN ('offen', 'laeuft', "
        "'wartet_budget')) AND NOT EXISTS (SELECT 1 FROM drafts d WHERE d.story_id = s.id) LIMIT 50").fetchall()
    n = 0
    for sid, notiz, herkunft in rows:
        runden = nachrecherche.runden(store, sid)
        gruende = [g.strip() for g in (notiz or "").split("; ") if g.strip() and not g.startswith(
            ("In Nachrecherche", "Nachrecherche Runde", "Zweite KI prüft", "Ergänzt am"))]
        if runden < nachrecherche.MAX_RUNDEN:
            schritt = "nachrecherche"
        elif herkunft == "nachtrag":
            continue
        else:
            schritt = "pruefung" if ctx.claude is not None else "recherche"
        if jobs.einreihen(store, sid, schritt, prio=jobs.PRIO_NEWS, key=f"{sid}:{schritt}:anstoss{runden}",
                          payload={"gruende": gruende, "fehlend": [], "hinweise": []}):
            n += 1
    return n


def worker(settings: Settings, *, parallel: int | None = None, einmal: bool = False, pause: float = 5.0,
           stop: threading.Event | None = None, client_factory: Callable[[], Any] | None = None,
           kontext_kw: dict | None = None) -> Counter:
    """Dauerdienst: N Threads, jeder mit eigener Datenbankverbindung. `einmal` = Schlange leeren und beenden."""
    parallel = parallel or settings.parallel_jobs
    stop = stop or threading.Event()
    gesamt: Counter = Counter()
    lock = threading.Lock()

    def lauf(nr: int) -> None:
        with Store(settings.db_path) as store:
            ctx = kontext(settings, store, client=client_factory() if client_factory else None, **(kontext_kw or {}))
            while not stop.is_set():
                stats = abarbeiten(ctx, max_jobs=20, worker=f"worker-{nr}")
                with lock:
                    gesamt.update(stats)
                if not stats or set(stats) <= {"wartet_budget", "verloren"}:  # nichts geschafft: kurz ruhen
                    if einmal:
                        return
                    stop.wait(pause)

    threads = [threading.Thread(target=lauf, args=(n,), name=f"radar-worker-{n}", daemon=True) for n in range(parallel)]
    for t in threads:
        t.start()
    try:
        for t in threads:
            while t.is_alive():
                t.join(timeout=1.0)
    except KeyboardInterrupt:
        stop.set()
    return gesamt


def lauf(settings: Settings, *, mit_jobs: bool = False, client=None, items=None, **kontext_kw) -> dict:
    """`run` mit RADAR_WORKFLOW=v2: Scan (+ Jobs bis zur Deadline) + Veröffentlichung freigegebener Entwürfe."""
    t0 = time.monotonic()
    with Store(settings.db_path) as store:
        run_id = store.start_run("v2" + (" · mit Jobs" if mit_jobs else ""))
        ctx = kontext(settings, store, client=client, **kontext_kw)
        stats = scan(ctx, items)
        if mit_jobs:
            stats["jobs"] = dict(abarbeiten(ctx, bis=t0 + settings.deadline_seconds))
        veroeffentlicht = 0
        if settings.wordpress_enabled:
            from ..publisher import publish_approved

            veroeffentlicht = sum(1 for r in publish_approved(settings, store) if r.status == "veroeffentlicht")
        store.finish_run(run_id, gesammelt=stats.get("gesammelt", 0), relevant=stats.get("relevant", 0),
                         entwuerfe=stats.get("storys", 0), verworfen=stats.get("veraltet", 0),
                         veroeffentlicht=veroeffentlicht, fehler=0,
                         notiz=", ".join(f"{k} {v}" for k, v in stats.items() if k != "jobs" and v))
    stats["sekunden"] = round(time.monotonic() - t0, 1)
    return stats


# ---- Eingriffe der Redaktion -------------------------------------------------------------------

def _recherche_neu(store: Store, story_id: int, notiz: str) -> None:
    """Recherche erneut einreihen; die Nutzdaten (uid, Quelle, Pressebild, Fakten) des ersten Laufs bleiben erhalten.
    Ein Nachtrag bekommt keinen Job: er geht zurück in den Agent-Export (Status „neu“)."""
    if jobs.ist_nachtrag(store, story_id):
        repo.story_setzen(store, story_id, status="neu", notiz=notiz[:500])
        return
    erste = store.db.execute("SELECT payload, prio FROM workflow_jobs WHERE story_id = ? AND schritt = 'recherche' "
                             "ORDER BY id LIMIT 1", (story_id,)).fetchone()
    payload = json.loads(erste["payload"]) if erste else {}
    n = store.db.execute("SELECT COUNT(*) FROM workflow_jobs WHERE story_id = ? AND schritt = 'recherche'",
                         (story_id,)).fetchone()[0]
    repo.story_setzen(store, story_id, status="neu", notiz=notiz[:500])
    jobs.einreihen(store, story_id, "recherche", prio=erste["prio"] if erste else jobs.PRIO_NEWS,
                   key=f"{story_id}:recherche:neu{n + 1}", payload=payload)


def von_mensch_bearbeitet(draft: dict) -> bool:
    return draft["status"] == "bearbeitet" or (draft.get("bearbeitet_von") or "radar") not in ("radar", "agent")


NEU_STARTBAR = ("recherche_erforderlich", "fehler")


class StoryNichtOffen(Exception):
    """Die Story ist fertig, verworfen, läuft gerade oder ist ein Kino-Datensatz – „Quelle ergänzen“ geht dort nicht."""


def neu_starten(store: Store, story_id: int, notiz: str) -> bool:
    """Eine Story, die wegen fehlender Belege oder eines Fehlers hängt, mit der neuen Quelle noch einmal prüfen."""
    story = repo.story(store, story_id)
    if story is None or story["typ"] == "kino":
        return False
    verworfen = nachrecherche.neu_startbar(story)
    if story["status"] not in NEU_STARTBAR and not verworfen:
        return False
    if verworfen and (nachrecherche.neustarts(store, story_id) >= nachrecherche.MAX_NEUSTARTS
                      or modell_schritte(store, story_id) >= MAX_PRUEFUNGEN
                      or store.db.execute("SELECT 1 FROM drafts WHERE story_id = ?", (story_id,)).fetchone()):
        return False
    if jobs.offen_fuer_story(store, story_id):
        return False  # die laufende Nachrecherche bzw. Recherche liest das neue Dokument ohnehin
    _recherche_neu(store, story_id, notiz)
    # protokolliert; die Runden der Nachrecherche zählen über alle Neustarts (höchstens zwei je Story)
    store.event("neu_gestartet", story=story_id, vorher=story["status"], grund=notiz[:200],
                runden_nachrecherche=nachrecherche.runden(store, story_id))
    return True


def quelle_ergaenzen(store: Store, story_id: int, url: str, von: str = "") -> str | None:
    """Quelle von Hand (nur admin, im Cockpit versteckt): die Story läuft erneut durch Recherche und Gate. Im
    Normalfall sucht die Nachrecherche selbst; niemand muss Links einfügen."""
    from .. import net

    story = repo.story(store, story_id)
    if story is None or story["status"] not in NEU_STARTBAR or story["typ"] == "kino" or jobs.offen_fuer_story(store, story_id):
        status = story["status"] if story else "fehlt"
        raise StoryNichtOffen(f"Story {story_id} ist {status} – eine Quelle lässt sich nur „In Nachrecherche“ oder "
                              "„Fehler“ ergänzen (nicht bei Kino und nicht, solange sie läuft)")
    net.check_url(url)
    key = repo.dokument_hinzufuegen(store, story_id, url=url, publisher="Redaktion", quelle="Redaktion", rights="zitat",
                                    art="zusammenfassung", titel=f"Quelle ergänzt von {von or 'Redaktion'}")
    _recherche_neu(store, story_id, f"Quelle ergänzt: {url}")
    store.event("quelle_ergaenzt", story=story_id, url=url, von=von)
    return key


def dossier_anlegen(store: Store, draft_id: int, von: str = "") -> int:
    """„Als Dossier recherchieren“: neue Story vom Typ dossier mit allen Quellen des Entwurfs (Opus schreibt)."""
    row = store.get_draft(draft_id)
    if row is None:
        raise ValueError(f"Entwurf {draft_id} fehlt")
    sid = repo.story_anlegen(store, typ="dossier", titel=row["titel"], kategorie=row["kategorie"], ort=row.get("ort") or "",
                             prioritaet=jobs.PRIO_DOSSIER, relevanz=row.get("relevanz"),
                             begruendung=f"Dossier zu Entwurf {draft_id}", laenge="dossier")
    alte = repo.dokumente(store, row["story_id"]) if row.get("story_id") else []
    if alte:
        for d in alte:
            repo.dokument_hinzufuegen(store, sid, url=d.url, publisher=d.publisher, quelle=d.quelle,
                                      published_at=d.published_at, language=d.language, rights=d.rights,
                                      primaer=d.primaer, art=d.art, titel=d.titel, text=d.text)
    else:
        repo.dokument_hinzufuegen(store, sid, url=row.get("quelle_url") or "", publisher=row.get("quelle_name") or "",
                                  rights="zitat", art="zusammenfassung", titel=row["titel"], text=row.get("teaser") or "")
        for q in row.get("weitere_quellen") or []:
            repo.dokument_hinzufuegen(store, sid, url=q.get("url", ""), publisher=q.get("name", ""), rights="zitat",
                                      art="zusammenfassung", titel=q.get("name", ""))
    jobs.einreihen(store, sid, "recherche", prio=jobs.PRIO_DOSSIER, payload={"uid": f"dossier:{sid}"})
    store.event("dossier", story=sid, entwurf=draft_id, von=von)
    return sid
