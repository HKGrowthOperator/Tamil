"""Ein Radar-Lauf: einsammeln -> filtern -> schreiben -> Bild -> Entwurf in die Warteschlange.

Ziel: Meldung bis fertiger Entwurf (Text + Bild) in unter 5 Minuten. Veröffentlicht wird nur, was in
der Freigabe-App freigegeben wurde (publisher.py).
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone

from . import filtering, notify, sources
from .config import Settings
from .images import featured_image, save_pair
from .store import Store
from .wordpress import slugify
from .writer import Draft, Writer, split_source_suffix

log = logging.getLogger(__name__)


@dataclass
class Result:
    title: str
    status: str  # entwurf | aktualisiert | verworfen | fehler | veroeffentlicht | in_wordpress
    category: str = ""
    link: str = ""
    seconds: float = 0.0
    note: str = ""
    draft_id: int | None = None


def category_label(settings: Settings, slug: str) -> str:
    return next((c.label for c in settings.categories if c.slug == slug), slug)


def quelle_name(item: sources.NewsItem) -> str:
    """Bei Google-News-Treffern steht der Verlag nur im Titel-Suffix – den zeigen wir statt „Google News“."""
    if item.source.lower().startswith("google news"):
        _, verlag = split_source_suffix(sources.clean_text(item.title))
        if verlag:
            return f"{verlag} (via Google News)"
    return item.source


def draft_row(item: sources.NewsItem, draft: Draft, bild_datei: str, image, hinweise: tuple | list = ()) -> dict:
    """Ein Entwurf für die Warteschlange, zusammengesetzt aus Meldung, Schreib-Ergebnis und Bild."""
    typ = "kino_termine" if item.kind == "kino" else draft.typ
    return {
        "uid": item.uid,
        "typ": typ,
        "quelle_name": quelle_name(item),
        "quelle_url": item.url,
        "quelle_bild": item.image_url or "",
        "hinweise": list(hinweise),
        "quelle_datum": item.published.isoformat(timespec="minutes"),
        "quelle_sprache": item.language,
        "weitere_quellen": [{"name": r.source, "url": r.url} for r in item.related],
        "relevanz": draft.relevanz,
        "begruendung": draft.begruendung,
        "dach_bezug": draft.dach_bezug or item.dach_score > 0,
        "ort": draft.ort or item.ort,
        "kategorie": draft.kategorie,
        "titel": draft.titel,
        "teaser": draft.teaser,
        "inhalt_html": draft.inhalt_html,
        "schlagworte": draft.schlagworte,
        "seo_titel": draft.seo_titel,
        "meta_beschreibung": draft.meta_beschreibung,
        "bild_datei": bild_datei,
        "bild_credit": image.credit,
        "bild_alt": draft.bild_alt,
        "bild_suchbegriff": draft.bild_suchbegriff,
        "bild_origin": image.origin,
        "event_datum": draft.event_datum,
        "event_ort": draft.event_ort,
        "ticket_url": draft.ticket_url,
        "fakten": item.facts or {},
        "fingerprint": item.fingerprint,
        "original_json": draft.model_dump(),
    }


def process(item: sources.NewsItem, settings: Settings, writer: Writer, store: Store) -> Result:
    start = time.monotonic()
    hinweise = [writer.hinweis] if getattr(writer, "hinweis", "") else []  # RawWriter: Rohfassung ohne KI
    article_text = sources.fetch_article_text(item.url) if item.kind == "news" else ""
    draft = writer.write(item, article_text)
    if draft is None:
        store.mark(item.uid, item.title, item.url, item.source, "abgelehnt_modell")
        return Result(item.title, "verworfen", note="vom Modell abgelehnt", seconds=time.monotonic() - start)
    if draft.relevanz < settings.min_relevance:
        store.mark(item.uid, item.title, item.url, item.source, "irrelevant")
        store.event("verworfen", titel=item.title, quelle=item.url, relevanz=draft.relevanz, grund=draft.begruendung)
        return Result(item.title, "verworfen", draft.kategorie, note=f"Relevanz {draft.relevanz}: {draft.begruendung}",
                      seconds=time.monotonic() - start)

    stem = f"{item.uid[:12]}-{slugify(draft.titel, 50)}"
    image = featured_image(settings, draft.bild_suchbegriff, draft.titel, category_label(settings, draft.kategorie), stem)
    bild_datei, _thumb = save_pair(image, settings.bilder_dir, stem)
    draft_id = store.insert_draft(draft_row(item, draft, bild_datei, image, hinweise))
    store.mark(item.uid, item.title, item.url, item.source, "entwurf")
    if draft_id is None:
        return Result(draft.titel, "verworfen", draft.kategorie, note="Entwurf existiert schon", seconds=time.monotonic() - start)

    seconds = time.monotonic() - start
    link = f"{settings.web_url}/entwurf/{draft_id}"
    store.event("entwurf", id=draft_id, titel=draft.titel, quelle=item.url, kategorie=draft.kategorie, typ=draft.typ,
                bild=image.origin, relevanz=draft.relevanz, dach=draft.ort, sekunden=round(seconds, 1),
                modus="roh" if hinweise else "ki")
    note = f"Relevanz {draft.relevanz}, Bild: {image.origin}"
    if hinweise:
        note = "Rohfassung · " + note
    return Result(draft.titel, "entwurf", draft.kategorie, link, seconds, note, draft_id)


def refresh_kino(items: list[sources.NewsItem], store: Store, seen: set[str]) -> list[Result]:
    """Neue Spielorte in offene Kino-Entwürfe übernehmen statt einen zweiten Entwurf anzulegen."""
    results = []
    for item in items:
        if item.kind != "kino" or item.uid not in seen:
            continue
        existing = store.draft_by_uid(item.uid)
        if not existing:
            continue
        old = {k.get("kino") for k in existing["fakten"].get("kinos", [])}
        new = {k.get("kino") for k in (item.facts or {}).get("kinos", [])}
        added, removed = sorted(new - old), sorted(old - new)
        parts = [f"+{k}" for k in added] + [f"−{k}" for k in removed]
        note = f"Aktualisiert {datetime.now(timezone.utc):%d.%m.}: " + (", ".join(parts) if parts else "Termine aktualisiert")
        if store.update_kino_facts(item.uid, item.facts or {}, item.fingerprint, note):
            store.event("kino_aktualisiert", id=existing["id"], titel=existing["titel"], hinweis=note)
            results.append(Result(existing["titel"], "aktualisiert", existing["kategorie"], note=note, draft_id=existing["id"]))
        elif existing["status"] not in ("neu", "bearbeitet", "zurueckgestellt") and existing.get("fingerprint") != item.fingerprint:
            store.event("kino_update_ignoriert", id=existing["id"], titel=existing["titel"], status=existing["status"])
    return results


def run(settings: Settings, writer: Writer | None = None, store: Store | None = None) -> list[Result]:
    t0 = time.monotonic()
    own_store = store is None
    store = store or Store(settings.db_path)
    modus = "wordpress" if settings.wordpress_enabled else "warteschlange"
    if getattr(writer, "hinweis", ""):
        modus += " · ohne KI"
    run_id = store.start_run(modus)
    results: list[Result] = []
    try:
        items = sources.fetch_all(settings, store)
        seen = store.seen_uids()
        results += refresh_kino(items, store, seen)
        candidates = filtering.select(items, settings, seen, store.recent_titles())

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        budget = max(0, settings.max_drafts_per_day - store.drafts_created_since(today))
        if candidates and budget == 0:
            log.warning("Tagesbudget von %d Entwürfen erreicht – Rest morgen", settings.max_drafts_per_day)
            store.event("tagesbudget", offen=len(candidates))
        batch = candidates[: min(settings.max_articles, budget)]
        log.info("%d Meldungen gesammelt, %d relevant, bearbeite %d", len(items), len(candidates), len(batch))

        if batch:
            writer = writer or Writer(settings)
            deadline = t0 + settings.deadline_seconds
            pool = ThreadPoolExecutor(max_workers=min(5, len(batch)))
            futures = {pool.submit(process, item, settings, writer, store): item for item in batch}
            try:
                for fut in as_completed(futures, timeout=max(1, deadline - time.monotonic())):
                    item = futures[fut]
                    try:
                        results.append(fut.result())
                    except Exception as exc:  # noqa: BLE001 - ein fehlerhafter Beitrag stoppt den Lauf nicht
                        log.exception("Fehler bei %s", item.title)
                        store.event("fehler", titel=item.title, quelle=item.url, fehler=str(exc)[:300])
                        results.append(Result(item.title, "fehler", note=str(exc)[:200]))
            except TimeoutError:
                log.warning("Zeitbudget erreicht – offene Meldungen folgen im nächsten Lauf")
            finally:
                pool.shutdown(wait=False, cancel_futures=True)

        if settings.wordpress_enabled:
            from .publisher import publish_approved

            results += publish_approved(settings, store)

        notify.notify_new(settings, results)
        counts = {s: sum(1 for r in results if r.status == s) for s in ("entwurf", "verworfen", "fehler", "veroeffentlicht")}
        store.finish_run(run_id, gesammelt=len(items), relevant=len(candidates), entwuerfe=counts["entwurf"],
                         verworfen=counts["verworfen"], veroeffentlicht=counts["veroeffentlicht"], fehler=counts["fehler"])
        log.info("Lauf beendet nach %.1fs", time.monotonic() - t0)
    finally:
        if own_store:
            store.close()
    return results


def summary(results: list[Result]) -> str:
    if not results:
        return "Keine neuen relevanten Meldungen."
    return "\n".join(
        f"[{r.status:14}] {r.seconds:5.1f}s  {r.category:13} {r.title}" + (f"\n                  → {r.link}" if r.link else "")
        + (f"\n                  ({r.note})" if r.note else "")
        for r in results
    )
