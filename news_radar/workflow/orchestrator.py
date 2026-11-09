"""Orchestrator der Redaktion v2: deterministisch, Sprachmodelle nur in den Rollen.

  scan (Timer, alle 3 Minuten)   Quellen → Vorfilter → Signal (Grauzone) → Cluster → Story + Job
  worker (Dienst)                recherche → gate → schreiben → faktencheck → lektorat → seo → bild → Entwurf „neu“
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
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable

from .. import filtering, notify, sources
from ..agents import Kontext, cluster, copydesk, factcheck, media, relevance, research, schreiben, seo
from ..config import Settings
from ..pipeline import Result, category_label, quelle_name, refresh_kino, stale_event_date
from ..store import Store, now_iso
from ..wordpress import slugify
from ..writer import split_source_suffix
from . import costs, jobs, repo
from .providers import Claude, budget_fuer, usage_protokollieren

log = logging.getLogger(__name__)

Handler = Callable[[Kontext, dict], list[tuple[str, dict]]]


OHNE_MODELL = ("gate", "bild", "kino")  # Schritte, die auch ohne API-Schlüssel laufen


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
    """Ein Scan: neue Treffer werden Storys (mit Job) oder reichern bestehende Storys an. Gibt Zählwerte zurück."""
    s, store = ctx.settings, ctx.store
    now = ctx.uhr()
    items = items if items is not None else sources.fetch_all(s, store)
    seen = store.seen_uids()
    stats: Counter = Counter(gesammelt=len(items))
    stats["kino_aktualisiert"] = len(refresh_kino(items, store, seen))
    # Ähnliche Titel nicht verwerfen (wie v1), sondern dem Clustering geben: sie reichern bestehende Storys an
    picked = filtering.select(items, s, seen, [], now=now)
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
    limit_gemeldet = False
    neue_storys: dict[int, int] = {}  # Index der Zuordnung → angelegte Story (für Meldungen desselben Scans)
    zuordnungen = cluster.zuordnen(ctx, picked)
    for idx, z in enumerate(zuordnungen):
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
                                       weitere_quellen=offen["weitere_quellen"] + [{"name": publisher, "url": item.url}])
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
        if v["rolle"] in ("text", "ueberarbeitung", "lektorat", "seo"):
            return v["inhalt"]
    raise RuntimeError("Keine Textfassung vorhanden")


def _weiter(payload: dict, **neu) -> dict:
    out = {k: payload[k] for k in ("hinweise", "uid", "quelle", "quelle_bild", "url", "fakten", "runde") if k in payload}
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
    repo.story_setzen(ctx.store, story["id"], status="recherche")
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
        repo.story_setzen(ctx.store, story["id"], status="recherche_erforderlich", notiz="; ".join(g.gruende)[:900])
        ctx.store.event("recherche_erforderlich", story=story["id"], titel=story["titel"], gruende=g.gruende)
        return []
    repo.story_setzen(ctx.store, story["id"], status="geprueft")
    return [("schreiben", _weiter(job["payload"], hinweise=hinweise, runde=1))]


def schritt_schreiben(ctx: Kontext, job: dict) -> list[tuple[str, dict]]:
    story = _story(ctx, job)
    p = job["payload"]
    docs = repo.dokumente(ctx.store, story["id"])
    text = schreiben.schreiben(ctx, story, repo.claims(ctx.store, story["id"]), docs, story.get("laenge") or "normal",
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
        repo.story_setzen(ctx.store, story["id"], status="recherche_erforderlich",
                          notiz="Faktencheck: Kernaussage auch nach Überarbeitung nicht gedeckt – " +
                          "; ".join(u.satz[:120] for u in a.kern_probleme))
        ctx.store.event("recherche_erforderlich", story=story["id"], titel=story["titel"], gruende=["Faktencheck"])
        return []
    hinweise = list(p.get("hinweise", []))
    hinweise += [f"Faktencheck: nicht belegt (bitte prüfen) – „{u.satz[:160]}“" for u in a.markiert]
    if runde == 2:
        hinweise.append("Faktencheck: Text nach Beanstandung einmal überarbeitet")
    repo.story_setzen(ctx.store, story["id"], status="geprueft_text")
    return [("lektorat", _weiter(p, hinweise=hinweise))]


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
    return [("bild", _weiter(job["payload"], hinweise=job["payload"].get("hinweise", []) + h))]


def _quelle(ctx: Kontext, name: str):
    by_name = {q.name: q for q in ctx.settings.alle_quellen}
    return by_name.get(name) or by_name.get((name or "").split(" · ")[0])


def entwurf_anlegen(ctx: Kontext, story: dict, felder: dict, payload: dict, *, typ: str, hinweise: list[str],
                    fakten: dict | None = None, fingerprint: str = "") -> int | None:
    """Bild besorgen, Entwurf in die Warteschlange (Status „neu“), Lizenz und Fassung verknüpfen."""
    s = ctx.settings
    docs = repo.dokumente(ctx.store, story["id"])
    primaer = docs[0] if docs else None
    uid = payload.get("uid") or (primaer.url if primaer else "") or f"story:{story['id']}"
    if story["typ"] == "dossier":
        uid = f"dossier:{story['id']}"
    stem = f"s{story['id']}-{slugify(felder.get('titel') or 'beitrag', 50)}"
    label = category_label(s, felder.get("kategorie") or "news")
    bild, versucht = media.besorgen(ctx, story, felder, stem, kategorie_label=label,
                                    quelle=_quelle(ctx, payload.get("quelle", "")), quelle_bild=payload.get("quelle_bild", ""))
    name, asset_id = media.speichern(ctx, bild, stem, story["id"])
    weitere = [{"name": d.publisher or d.quelle, "url": d.url} for d in docs[1:] if d.url and not d.url.endswith("#daten")]
    if story.get("sensibel"):
        hinweise = ["Sensibles Thema: vor der Freigabe eine zweite Person lesen lassen"] + \
            [h for h in hinweise if not h.startswith("Sensibles Thema")]
    row = {
        "uid": uid, "typ": typ, "story_id": story["id"],
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
        "bild_alt": felder.get("bild_alt", ""), "bild_suchbegriff": felder.get("bild_suchbegriff", ""),
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
                ctx.store.update_draft(draft_id, hinweise=[hinweis] + [h for h in existing.get("hinweise") or []
                                                                       if not h.startswith("Neue Radar-Fassung")])
                repo.fassung_speichern(ctx.store, story["id"], "entwurf_neu", {**felder, **{k: row[k] for k in repo.FASSUNG_FELDER if k in row}},
                                       von="radar", draft_id=draft_id)
                repo.story_setzen(ctx.store, story["id"], status="fertig")
                ctx.store.event("entwurf_nicht_ueberschrieben", id=draft_id, story=story["id"], status=existing["status"])
                return draft_id
            ctx.store.update_draft(draft_id, von="radar", **{k: v for k, v in row.items() if k not in ("uid", "fakten")})
        else:
            ctx.store.event("entwurf_existiert", story=story["id"], uid=uid)
            repo.story_setzen(ctx.store, story["id"], status="verworfen", notiz="Entwurf zu dieser Meldung existiert schon")
            return None
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
    "kino": schritt_kino,
}


# ---- Job-Runner ---------------------------------------------------------------------------------

def job_ausfuehren(ctx: Kontext, job: dict) -> str:
    store = ctx.store
    handler = SCHRITTE.get(job["schritt"])
    if handler is None:
        jobs.fehlgeschlagen(store, job["id"], f"Unbekannter Schritt {job['schritt']}")
        return "fehler"
    try:
        naechste = handler(ctx, job)
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
    nur = None if ctx.claude is not None else OHNE_MODELL
    while (bis is None or time.monotonic() < bis) and (max_jobs is None or sum(stats.values()) < max_jobs):
        job = jobs.naechster(ctx.store, worker, schritte=nur)
        if job is None:
            break
        stats[job_ausfuehren(ctx, job)] += 1
    return stats


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
    """Recherche erneut einreihen; die Nutzdaten (uid, Quelle, Pressebild, Fakten) des ersten Laufs bleiben erhalten."""
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
    if story is None or story["status"] not in NEU_STARTBAR or story["typ"] == "kino":
        return False
    _recherche_neu(store, story_id, notiz)
    return True


def quelle_ergaenzen(store: Store, story_id: int, url: str, von: str = "") -> str | None:
    """„Recherche nötig“: die Redaktion gibt eine Quelle dazu, die Story läuft erneut durch Recherche und Gate."""
    from .. import net

    story = repo.story(store, story_id)
    if story is None or story["status"] not in NEU_STARTBAR or story["typ"] == "kino" or jobs.offen_fuer_story(store, story_id):
        status = story["status"] if story else "fehlt"
        raise StoryNichtOffen(f"Story {story_id} ist {status} – eine Quelle lässt sich nur bei „Recherche nötig“ oder "
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
