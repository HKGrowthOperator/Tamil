"""Ein Radar-Lauf: einsammeln -> filtern -> schreiben -> Bild -> WordPress-Entwurf.

Ziel: Meldung bis fertiger Entwurf (Text + Bild) in unter 5 Minuten.
"""

from __future__ import annotations

import html
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

import requests

from . import filtering, sources
from .config import Settings
from .images import featured_image
from .store import Store
from .wordpress import WordPress, slugify
from .writer import Draft, Writer

log = logging.getLogger(__name__)


@dataclass
class Result:
    title: str
    status: str  # entwurf | dry-run | verworfen | fehler
    category: str = ""
    link: str = ""
    seconds: float = 0.0
    note: str = ""


def render_content(draft: Draft, item: sources.NewsItem) -> str:
    """Haupttext + verlinkte Quellenangabe."""
    body = draft.inhalt_html.strip()
    link = f'<p class="quelle">Quelle: <a href="{html.escape(item.url)}" rel="nofollow noopener" target="_blank">{html.escape(item.source)}</a></p>'
    if 'class="quelle"' in body:
        head, _, _ = body.rpartition('<p class="quelle">')
        body = head.rstrip()
    return f"{body}\n{link}"


def _dry_run_save(settings: Settings, slug: str, draft: Draft, item, image, content: str) -> str:
    folder = settings.out_dir / slug
    folder.mkdir(parents=True, exist_ok=True)
    (folder / image.filename).write_bytes(image.data)
    (folder / "beitrag.json").write_text(
        json.dumps({"entwurf": draft.model_dump(), "quelle": item.url, "bild": image.credit}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (folder / "vorschau.html").write_text(
        f"<!doctype html><meta charset='utf-8'><title>{html.escape(draft.titel)}</title>"
        "<body style='max-width:760px;margin:40px auto;font-family:Georgia,serif;line-height:1.7;padding:0 16px'>"
        f"<img src='{image.filename}' style='width:100%;border-radius:8px'><small>{html.escape(image.credit)}</small>"
        f"<h1>{html.escape(draft.titel)}</h1><p><strong>{html.escape(draft.teaser)}</strong></p>{content}"
        f"<hr><small>Kategorie: {draft.kategorie} · Schlagworte: {', '.join(map(html.escape, draft.schlagworte))} · "
        f"Relevanz {draft.relevanz}/10 – {html.escape(draft.begruendung)}</small></body>",
        encoding="utf-8",
    )
    return str(folder / "vorschau.html")


def process(item, settings: Settings, writer: Writer, wp: WordPress | None, store: Store) -> Result:
    start = time.monotonic()
    article_text = sources.fetch_article_text(item.url)
    draft = writer.write(item, article_text)
    if draft is None:
        store.mark(item.uid, item.title, item.url, item.source, "abgelehnt")
        return Result(item.title, "verworfen", note="vom Modell abgelehnt", seconds=time.monotonic() - start)
    if draft.relevanz < settings.min_relevance:
        store.mark(item.uid, item.title, item.url, item.source, "irrelevant")
        store.event("verworfen", titel=item.title, relevanz=draft.relevanz, grund=draft.begruendung)
        return Result(item.title, "verworfen", draft.kategorie, note=f"Relevanz {draft.relevanz}: {draft.begruendung}",
                      seconds=time.monotonic() - start)

    slug = slugify(draft.titel)
    label = next((c.label for c in settings.categories if c.slug == draft.kategorie), draft.kategorie)
    image = featured_image(settings, draft.bild_suchbegriff, draft.titel, label, slug)
    content = render_content(draft, item)

    if wp:
        media_id = wp.upload_media(image, draft.bild_alt)
        post = wp.create_post(
            title=draft.titel, content=content, excerpt=draft.teaser, status=settings.wp_post_status,
            category_slug=draft.kategorie, tags=draft.schlagworte, media_id=media_id, slug=slug,
        )
        link, status = wp.edit_link(post), "entwurf"
    else:
        link, status = _dry_run_save(settings, slug, draft, item, image, content), "dry-run"

    store.mark(item.uid, item.title, item.url, item.source, status)
    seconds = time.monotonic() - start
    store.event("entwurf", titel=draft.titel, quelle=item.url, kategorie=draft.kategorie, link=link,
                bild=image.origin, relevanz=draft.relevanz, sekunden=round(seconds, 1))
    return Result(draft.titel, status, draft.kategorie, link, seconds, f"Relevanz {draft.relevanz}, Bild: {image.origin}")


def notify(settings: Settings, results: list[Result]) -> None:
    fresh = [r for r in results if r.status in ("entwurf", "dry-run")]
    if not settings.notify_webhook or not fresh:
        return
    lines = [f"📰 {len(fresh)} neue Tamil.de-Entwürfe warten auf Freigabe:"]
    lines += [f"• [{r.category}] {r.title} – {r.link}" for r in fresh]
    text = "\n".join(lines)
    try:
        requests.post(settings.notify_webhook, json={"text": text, "content": text}, timeout=10)
    except requests.RequestException as exc:
        log.warning("Benachrichtigung fehlgeschlagen: %s", exc)


def run(settings: Settings, writer: Writer | None = None, wp: WordPress | None = None) -> list[Result]:
    t0 = time.monotonic()
    store = Store(settings.data_dir / "radar.sqlite")
    if wp is None and settings.wordpress_enabled:
        wp = WordPress(settings.wp_url, settings.wp_user, settings.wp_app_password)
    writer = writer or Writer(settings)

    items = sources.fetch_all(settings)
    candidates = filtering.select(items, settings, store.seen_uids(), store.recent_titles())
    log.info("%d Meldungen gesammelt, %d relevant, bearbeite max. %d", len(items), len(candidates), settings.max_articles)
    store.event("lauf", gesammelt=len(items), relevant=len(candidates), modus="wordpress" if wp else "dry-run")

    batch = candidates[: settings.max_articles]
    results: list[Result] = []
    deadline = t0 + settings.deadline_seconds
    pool = ThreadPoolExecutor(max_workers=min(5, max(1, len(batch))))
    futures = {pool.submit(process, item, settings, writer, wp, store): item for item in batch}
    try:
        for fut in as_completed(futures, timeout=max(1, deadline - time.monotonic())):
            item = futures[fut]
            try:
                results.append(fut.result())
            except Exception as exc:  # noqa: BLE001 - ein fehlerhafter Beitrag stoppt den Lauf nicht
                log.exception("Fehler bei %s", item.title)
                store.event("fehler", titel=item.title, fehler=str(exc))
                results.append(Result(item.title, "fehler", note=str(exc)[:200]))
    except TimeoutError:
        log.warning("Zeitbudget erreicht – offene Meldungen folgen im nächsten Lauf")
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    notify(settings, results)
    log.info("Lauf beendet nach %.1fs", time.monotonic() - t0)
    return results


def summary(results: list[Result]) -> str:
    if not results:
        return "Keine neuen relevanten Meldungen."
    return "\n".join(
        f"[{r.status:9}] {r.seconds:5.1f}s  {r.category:13} {r.title}" + (f"\n             → {r.link}" if r.link else "")
        + (f"\n             ({r.note})" if r.note else "")
        for r in results
    )

