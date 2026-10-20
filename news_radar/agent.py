"""Agent-Modus: ein Agent (z. B. Claude Code in der Cloud-Sitzung) schreibt die Beiträge statt der API.

Ablauf („Research“ per Zuruf):
  python -m news_radar run --ohne-ki            → Rohfassungen in der Warteschlange
  python -m news_radar agent export --file m.json  → Aufgabenmappe: Entwürfe + Quelltexte + Stilprofil + Bildregeln
  (der Agent schreibt die Beiträge nach prompts/redaktion.md und legt ein Ergebnis-JSON an)
  python -m news_radar agent import --file e.json  → Texte übernehmen, Bild besorgen, Status „bearbeitet“

Das Ergebnis-JSON ist {"ergebnisse": [ … ]}; jeder Eintrag entweder {"id": 12, "verwerfen": "Grund"} oder ein
vollständiger Beitrag mit allen Feldern von `Draft` plus "id". Alles wird validiert; nichts landet halb in der
Warteschlange. Der Mensch gibt im Cockpit frei wie bei jedem anderen Entwurf.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, Field, ValidationError

from . import prompts, sources
from .bilder import BildPool, Transport, beitragsbild
from .config import Settings
from .images import save_pair
from .store import ConflictError, Store
from .wordpress import slugify
from .writer import Draft

log = logging.getLogger(__name__)

EXPORT_FIELDS = (
    "id", "uid", "status", "typ", "titel", "teaser", "inhalt_html", "kategorie", "relevanz", "begruendung",
    "dach_bezug", "ort", "quelle_name", "quelle_url", "quelle_datum", "quelle_sprache", "weitere_quellen",
    "schlagworte", "bild_origin", "bild_credit", "quelle_bild", "bild_thema", "event_datum", "event_ort",
    "ticket_url", "fakten", "hinweise", "created_at",
)

ANLEITUNG = """\
Schreibe aus jedem Entwurf einen fertigen Tamil.de-Beitrag nach dem Stilprofil (Feld "stil") und den
Bildregeln (Feld "bildregeln"). Nutze nur Fakten aus titel, teaser, quelltext, fakten und weitere_quellen.
Lege ein JSON {"ergebnisse": [...]} an. Je Entwurf entweder
  {"id": <id>, "verwerfen": "<Grund>"}  – wenn die Meldung nicht zu Tamil.de passt, doppelt ist oder zu dünn
oder ein Beitrag mit allen Feldern: id, relevanz (1-10), begruendung, kategorie (Slug aus "kategorien"), typ
(artikel|event|kino_termine – den vorhandenen typ beibehalten), dach_bezug, ort, titel (max. 90 Zeichen), teaser
(max. 220), inhalt_html (<p>-Absätze, optional <h2>, letzter Absatz <p class="quelle">Quelle: NAME</p>),
schlagworte (3-6), seo_titel (max. 60), meta_beschreibung (max. 155), bild_suchbegriff (englisch, 2-4 Begriffe),
bild_alt (deutsch), bild_thema (Slug aus "bildthemen"), bild_prompt (englisches Motiv, 30-60 Wörter, keine realen
Personen, kein Text, kein Logo), event_datum (YYYY-MM-DD oder leer), event_ort, ticket_url.
Zwei Entwürfe zum selben Thema: einen schreiben, den anderen mit Verweis verwerfen. Immer auf Deutsch.
"""

Fetcher = Callable[[str], str]


class AgentDraft(Draft):
    """Ein fertiger Beitrag aus der Agent-Antwort: alle Draft-Felder plus die Entwurfs-ID, mit harten Grenzen."""

    id: int = Field(ge=1)
    relevanz: int = Field(ge=1, le=10)
    titel: str = Field(min_length=8, max_length=120)
    teaser: str = Field(min_length=20, max_length=260)
    inhalt_html: str = Field(min_length=120)
    schlagworte: list[str] = Field(min_length=1, max_length=8)
    seo_titel: str = Field(min_length=5, max_length=80)
    meta_beschreibung: str = Field(min_length=20, max_length=180)
    bild_alt: str = Field(min_length=3, max_length=200)


class Verwerfen(BaseModel):
    id: int = Field(ge=1)
    verwerfen: str = Field(min_length=3, max_length=300)


def _roh(row: dict) -> bool:
    return any(str(h).startswith("Rohfassung") for h in (row.get("hinweise") or []))


def export_tasks(
    store: Store,
    settings: Settings,
    file: Path,
    *,
    statuses: tuple[str, ...] = ("neu",),
    nur_roh: bool = True,
    limit: int = 20,
    mit_text: bool = True,
    fetch_text: Fetcher = sources.fetch_article_text,
) -> dict:
    """Schreibt die Aufgabenmappe für den Agenten und gibt sie zurück."""
    rows: list[dict] = []
    for status in statuses:
        rows += store.list_drafts(status=status, limit=500)
    if nur_roh:
        rows = [r for r in rows if _roh(r)]
    rows.sort(key=lambda r: (int(r.get("relevanz") or 0), r.get("quelle_datum") or ""), reverse=True)
    rows = rows[:limit]

    entwuerfe = []
    for r in rows:
        e = {k: r.get(k) for k in EXPORT_FIELDS}
        e["quelltext"] = ""
        url = r.get("quelle_url") or ""
        if mit_text and r.get("typ") != "kino_termine" and url and "news.google.com" not in url:
            try:
                e["quelltext"] = fetch_text(url)
            except Exception as exc:  # noqa: BLE001 – ein kaputter Link darf den Export nicht stoppen
                log.info("Quelltext nicht geladen (%s): %s", url[:80], exc)
        entwuerfe.append(e)

    data = {
        "stand": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "anleitung": ANLEITUNG,
        "stil": prompts.redaktion(),
        "bildregeln": prompts.load_prompt("bild"),
        "bildthemen": prompts.thema_slugs(),
        "bildpool": BildPool(settings.bildpool_dir).status(),
        "kategorien": [{"slug": c.slug, "label": c.label} for c in settings.categories],
        "felder": [f for f in Draft.model_fields],
        "entwuerfe": entwuerfe,
    }
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def _kurz(exc: ValidationError) -> str:
    first = exc.errors()[0]
    return f"{'.'.join(str(p) for p in first.get('loc', ()))}: {first.get('msg')}"


def import_results(
    store: Store,
    settings: Settings,
    file: Path,
    *,
    von: str = "agent",
    transport: Transport | None = None,
) -> dict:
    """Übernimmt die Agent-Antwort: validieren, Bild besorgen, Entwurf aktualisieren, Status „bearbeitet“."""
    raw = json.loads(file.read_text(encoding="utf-8"))
    items = raw.get("ergebnisse", []) if isinstance(raw, dict) else raw
    stats = {"uebernommen": 0, "verworfen": 0, "fehler": [], "bilder": {}}
    pool = BildPool(settings.bildpool_dir)
    slugs = set(settings.category_slugs())

    for item in items:
        draft_id = item.get("id") if isinstance(item, dict) else None
        row = store.get_draft(int(draft_id)) if isinstance(draft_id, int) else None
        if row is None:
            stats["fehler"].append(f"{draft_id}: Entwurf nicht gefunden")
            continue
        if item.get("verwerfen"):
            try:
                v = Verwerfen.model_validate(item)
                store.set_status(v.id, "ablehnen", von=von)
                store.event("agent", id=v.id, aktion="verworfen", titel=row.get("titel"), grund=v.verwerfen)
                stats["verworfen"] += 1
            except (ValidationError, ConflictError) as exc:
                stats["fehler"].append(f"{draft_id}: {_kurz(exc) if isinstance(exc, ValidationError) else exc}")
            continue
        try:
            d = AgentDraft.model_validate(item)
        except ValidationError as exc:
            stats["fehler"].append(f"{draft_id}: {_kurz(exc)}")
            continue
        if d.kategorie not in slugs:
            stats["fehler"].append(f"{draft_id}: unbekannte Kategorie „{d.kategorie}“")
            continue
        if row["status"] not in ("neu", "bearbeitet", "zurueckgestellt"):
            stats["fehler"].append(f"{draft_id}: Status „{row['status']}“ lässt keine Bearbeitung zu")
            continue
        typ = "kino_termine" if row.get("typ") == "kino_termine" else d.typ

        stem = f"{row['uid'][:12]}-{slugify(d.titel, 50)}-a{int(row.get('rewrite_count') or 0) + 1}"
        image = beitragsbild(
            settings, titel=d.titel, kategorie=d.kategorie,
            kategorie_label=next((c.label for c in settings.categories if c.slug == d.kategorie), d.kategorie),
            slug=stem, bild_prompt=d.bild_prompt, bild_thema=d.bild_thema, bild_suchbegriff=d.bild_suchbegriff,
            transport=transport, pool=pool,
        )
        name, _thumb = save_pair(image, settings.bilder_dir, stem)
        for old in (row.get("bild_datei"), (row.get("bild_datei") or "").replace(".jpg", "-thumb.jpg")):
            if old and old != name:
                (settings.bilder_dir / old).unlink(missing_ok=True)

        fields = d.model_dump(exclude={"id"})
        fields.update(
            typ=typ,
            hinweise=[h for h in (row.get("hinweise") or []) if not str(h).startswith("Rohfassung")],
            bild_datei=name, bild_credit=image.credit, bild_origin=image.origin,
            rewrite_count=int(row.get("rewrite_count") or 0) + 1,
        )
        store.update_draft(d.id, von=von, **fields)
        if row["status"] != "bearbeitet":
            store.set_status(d.id, "bearbeiten", von=von)
        store.event("agent", id=d.id, aktion="geschrieben", titel=d.titel, kategorie=d.kategorie, typ=typ,
                    relevanz=d.relevanz, bild=image.origin, von=von)
        stats["uebernommen"] += 1
        stats["bilder"][image.origin] = stats["bilder"].get(image.origin, 0) + 1
    return stats
