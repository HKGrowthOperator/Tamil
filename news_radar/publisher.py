"""Veröffentlichen freigegebener Entwürfe in WordPress („Direkt posten“ und Timer-Lauf)."""

from __future__ import annotations

import logging

from .config import Settings
from .images import load_image
from .render import render_content
from .store import Store
from .wordpress import WordPress, slugify

log = logging.getLogger(__name__)


def seo_meta(settings: Settings, row: dict) -> dict | None:
    """Meta-Felder des SEO-Plugins – nur wirksam, wenn das Plugin sie per REST freigibt."""
    titel, desc = row.get("seo_titel") or row.get("titel"), row.get("meta_beschreibung") or row.get("teaser")
    if settings.wp_seo_meta == "rankmath":
        return {"rank_math_title": titel, "rank_math_description": desc}
    if settings.wp_seo_meta == "yoast":
        return {"_yoast_wpseo_title": titel, "_yoast_wpseo_metadesc": desc}
    return None


def make_wordpress(settings: Settings) -> WordPress:
    return WordPress(settings.wp_url, settings.wp_user, settings.wp_app_password)


def publish_draft(row: dict, settings: Settings, wp: WordPress, store: Store, status: str | None = None) -> dict:
    """Bild hochladen, Beitrag anlegen, Entwurf als veröffentlicht (oder WP-Entwurf) markieren.

    Der Entwurf muss vorher per `store.claim_draft`/`claim_for_publish` reserviert sein.
    Wirft bei WordPress-Fehlern; der Aufrufer markiert dann `fehler`.
    """
    status = status or settings.wp_post_status
    media_id = None
    if row.get("bild_datei"):
        path = settings.bilder_dir / row["bild_datei"]
        if path.exists():
            media_id = wp.upload_media(load_image(path, row.get("bild_credit") or ""), row.get("bild_alt") or row["titel"])
    post = wp.create_post(
        title=row["titel"],
        content=render_content(row),
        excerpt=row.get("teaser") or "",
        status=status,
        category_slug=row.get("kategorie") or "news",
        tags=row.get("schlagworte") or [],
        media_id=media_id,
        slug=slugify(row["titel"]),
        meta=seo_meta(settings, row),
    )
    edit_link = wp.edit_link(post)
    if status == "publish":
        link = post.get("link") or edit_link
        store.mark_published(row["id"], post.get("id"), link)
        store.event("veroeffentlicht", id=row["id"], titel=row["titel"], wp_post_id=post.get("id"), link=link)
    else:
        store.mark_in_wordpress(row["id"], post.get("id"), edit_link)
        store.event("in_wordpress", id=row["id"], titel=row["titel"], wp_post_id=post.get("id"), link=edit_link)
        link = edit_link
    return {"post_id": post.get("id"), "link": link, "edit_link": edit_link, "status": status}


def publish_approved(settings: Settings, store: Store, wp: WordPress | None = None, limit: int = 10) -> list:
    """Timer-Lauf: alles Freigegebene veröffentlichen, das noch nicht gepostet ist."""
    from .pipeline import Result  # zirkulärer Import vermeiden

    results: list[Result] = []
    claimed = store.claim_for_publish(limit)
    if not claimed:
        return results
    wp = wp or make_wordpress(settings)
    for row in claimed:
        try:
            info = publish_draft(row, settings, wp, store)
            results.append(Result(row["titel"], "veroeffentlicht", row.get("kategorie") or "", info["link"], draft_id=row["id"]))
        except Exception as exc:  # noqa: BLE001 - ein fehlerhafter Beitrag stoppt den Lauf nicht
            log.exception("Veröffentlichen fehlgeschlagen: %s", row["titel"])
            store.mark_publish_failed(row["id"], str(exc))
            store.event("fehler", id=row["id"], titel=row["titel"], fehler=str(exc)[:300], schritt="veroeffentlichen")
            results.append(Result(row["titel"], "fehler", row.get("kategorie") or "", note=str(exc)[:200], draft_id=row["id"]))
    return results
