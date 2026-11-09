"""Veröffentlichen freigegebener Entwürfe in WordPress („Direkt posten“ und Timer-Lauf)."""

from __future__ import annotations

import base64
import logging

from .config import Settings
from .images import load_image
from .render import render_content
from .store import Store
from .wordpress import TamilRadarClient, WordPress, make_client, slugify

log = logging.getLogger(__name__)

# Meta-Felder, die der Radar an das Plugin übergibt (Spalte im Store → Meta-Schlüssel)
META_FIELDS = (
    ("relevanz", "radar_relevanz"), ("quelle_name", "quelle_name"), ("quelle_url", "quelle_url"),
    ("quelle_datum", "quelle_datum"), ("quelle_sprache", "quelle_sprache"), ("bild_credit", "bild_credit"),
    ("bild_origin", "bild_origin"), ("ort", "ort"), ("event_datum", "event_datum"), ("event_ort", "event_ort"),
    ("ticket_url", "ticket_url"),
)


def radar_meta(row: dict) -> dict:
    """Meta für das Plugin: Herkunft, Bildnachweis, Ort, Event- und Kinodaten."""
    meta = {"radar_uid": row["uid"]}
    for column, key in META_FIELDS:
        value = row.get(column)
        if value not in (None, "", 0):
            meta[key] = value
    if row.get("typ") == "kino_termine" and row.get("fakten"):
        meta["kino_fakten"] = row["fakten"]
    if row.get("typ") != "event":
        for key in ("event_datum", "event_ort", "ticket_url"):
            meta.pop(key, None)
    return meta


def bild_payload(row: dict, settings: Settings) -> dict:
    path = settings.bilder_dir / (row.get("bild_datei") or "")
    if not row.get("bild_datei") or not path.exists():
        return {}
    return {
        "daten": base64.b64encode(path.read_bytes()).decode("ascii"),
        "dateiname": path.name,
        "alt": row.get("bild_alt") or row["titel"],
        "credit": row.get("bild_credit") or "",
    }


def plugin_payload(row: dict, settings: Settings, status: str) -> dict:
    schlagworte = [s for s in (row.get("schlagworte") or []) if str(s).strip()]
    return {
        "titel": row["titel"],
        "inhalt": render_content(row),
        "teaser": row.get("teaser") or "",
        "status": status,
        "slug": slugify(row["titel"]),
        "kategorie": row.get("kategorie") or "news",
        "schlagworte": schlagworte,
        "meta": radar_meta(row),
        "seo": {
            "title": row.get("seo_titel") or row["titel"],
            "description": row.get("meta_beschreibung") or row.get("teaser") or "",
            "focus": schlagworte[0] if schlagworte else "",
        },
        "bild": bild_payload(row, settings),
    }


def seo_meta(settings: Settings, row: dict) -> dict | None:
    """Meta-Felder des SEO-Plugins – nur wirksam, wenn das Plugin sie per REST freigibt."""
    titel, desc = row.get("seo_titel") or row.get("titel"), row.get("meta_beschreibung") or row.get("teaser")
    if settings.wp_seo_meta == "rankmath":
        return {"rank_math_title": titel, "rank_math_description": desc}
    if settings.wp_seo_meta == "yoast":
        return {"_yoast_wpseo_title": titel, "_yoast_wpseo_metadesc": desc}
    return None


def make_wordpress(settings: Settings) -> WordPress | TamilRadarClient:
    """Plugin-Client, wenn das Tamil.de-Plugin installiert ist, sonst Core-REST."""
    return make_client(settings.wp_url, settings.wp_user, settings.wp_app_password)


def _finish(row: dict, store: Store, post: dict, status: str, edit_link: str) -> dict:
    if status == "publish":
        link = post.get("link") or edit_link
        store.mark_published(row["id"], post.get("id"), link)
        store.event("veroeffentlicht", id=row["id"], titel=row["titel"], wp_post_id=post.get("id"), link=link)
    else:
        store.mark_in_wordpress(row["id"], post.get("id"), edit_link)
        store.event("in_wordpress", id=row["id"], titel=row["titel"], wp_post_id=post.get("id"), link=edit_link)
        link = edit_link
    return {"post_id": post.get("id"), "link": link, "edit_link": edit_link, "status": status}


def publish_via_plugin(row: dict, settings: Settings, wp: TamilRadarClient, store: Store, status: str) -> dict:
    """Ein Aufruf ans Plugin; eine Dublette (409) wird bei Kinoterminen aktualisiert, sonst übernommen."""
    payload = plugin_payload(row, settings, status)
    post = wp.create(payload)
    if post.get("duplikat"):
        if row.get("typ") == "kino_termine":
            update = {k: payload[k] for k in ("titel", "inhalt", "teaser", "meta")}
            post = wp.update(row["uid"], update)
            store.event("aktualisiert", id=row["id"], titel=row["titel"], wp_post_id=post.get("id"), grund="Kinoliste")
        else:
            log.info("Beitrag %s existiert schon in WordPress (Post %s)", row["uid"], post.get("id"))
    edit_link = wp.edit_link(post)
    wp_status = post.get("status") or status
    return _finish(row, store, post, "publish" if wp_status == "publish" else wp_status, edit_link)


def publish_draft(row: dict, settings: Settings, wp: WordPress | TamilRadarClient, store: Store,
                  status: str | None = None) -> dict:
    """Bild hochladen, Beitrag anlegen, Entwurf als veröffentlicht (oder WP-Entwurf) markieren.

    Der Entwurf muss vorher per `store.claim_draft`/`claim_for_publish` reserviert sein.
    Wirft bei WordPress-Fehlern; der Aufrufer markiert dann `fehler`.
    """
    status = status or settings.wp_post_status
    if isinstance(wp, TamilRadarClient):
        return publish_via_plugin(row, settings, wp, store, status)
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
    return _finish(row, store, post, status, wp.edit_link(post))


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
