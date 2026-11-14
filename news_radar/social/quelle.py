"""Erkennen: veröffentlichte Beiträge und Termine der Website, nur lesend über die WordPress-REST-Schnittstelle.

Der Radar holt ab (`GET /wp-json/wp/v2/posts`), WordPress ruft nie den Radar. Erkannt werden auch Beiträge, die jemand
von Hand in WordPress angelegt hat. Zum Beitrag sucht der Radar seine eigenen Daten dazu (Entwurf über `wp_post_id`
oder `radar_uid`, Story für die Markierung `sensibel`, Lizenz-Datensatz des Bildes für den Umfang „social“).
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

ALTBESTAND_PRAEFIXE = ("alt-", "altseite-")  # radar_uid der Übernahme (tools/migration.py)
_TAGS = re.compile(r"<[^>]+>")

Abruf = Callable[[dict], list[dict]]


@dataclass
class Beitrag:
    wp_post_id: int
    link: str
    titel: str
    vorspann: str
    datum: datetime | None          # Veröffentlichung auf der Website (UTC)
    quelle_typ: str                 # beitrag | termin
    rubriken: list[str] = field(default_factory=list)   # Kategorie-Slugs in der Reihenfolge von WordPress
    schlagworte: list[str] = field(default_factory=list)
    radar_uid: str = ""
    story_id: int | None = None
    event_datum: str = ""
    event_ort: str = ""
    sensibel: bool = False          # aus der Story des Radars
    # Bild: nur aus den Daten des Radars (Entwurf + Lizenz-Datensatz), nie aus fremden Adressen
    bild_pfad: object = None        # Path der lokalen Datei oder None
    asset: dict | None = None
    bild_ki: bool = False


def _text(wert) -> str:
    if isinstance(wert, dict):
        wert = wert.get("rendered", "")
    return " ".join(html.unescape(_TAGS.sub(" ", str(wert or ""))).split())


def _zeit(wert: str | None) -> datetime | None:
    if not wert:
        return None
    try:
        dt = datetime.fromisoformat(str(wert).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _int(wert) -> int | None:
    try:
        n = int(wert)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def beitrag_aus_wp(post: dict) -> Beitrag:
    """Eine Antwort von `/wp/v2/posts?_embed=wp:term` in einen Beitrag übersetzen (fehlende Felder bleiben leer)."""
    meta = post.get("meta") if isinstance(post.get("meta"), dict) else {}
    rubriken, schlagworte = [], []
    for gruppe in (post.get("_embedded") or {}).get("wp:term") or []:
        for term in gruppe or []:
            if not isinstance(term, dict):
                continue
            if term.get("taxonomy") == "category" and term.get("slug"):
                rubriken.append(str(term["slug"]))
            elif term.get("taxonomy") == "post_tag" and term.get("name"):
                schlagworte.append(_text(term["name"]))
    event = str(meta.get("event_datum") or "").strip()
    return Beitrag(
        wp_post_id=int(post["id"]),
        link=str(post.get("link") or ""),
        titel=_text(post.get("title")),
        vorspann=_text(meta.get("standfirst")) or _text(post.get("excerpt")),
        datum=_zeit(post.get("date_gmt")),
        quelle_typ="termin" if event else "beitrag",
        rubriken=rubriken,
        schlagworte=schlagworte,
        radar_uid=str(meta.get("radar_uid") or ""),
        story_id=_int(meta.get("radar_story_id")),
        event_datum=event,
        event_ort=_text(meta.get("event_ort")),
    )


def altbestand(b: Beitrag, startmarke: datetime) -> bool:
    """R9: vor dem Start des Moduls veröffentlicht oder aus der Übernahme der alten Seite."""
    if b.radar_uid.startswith(ALTBESTAND_PRAEFIXE):
        return True
    return b.datum is None or b.datum < startmarke


def umfang_menge(wert) -> set[str]:
    """Lizenz-Umfang lesen – die gemeinsame Funktion aus `lizenz.py` (eine Stelle für Gate und Social)."""
    from ..lizenz import umfang_menge as gemeinsam

    return gemeinsam(wert)


def anreichern(store, settings, b: Beitrag) -> Beitrag:
    """Daten des Radars zum Beitrag: Entwurf (Bild), Lizenz-Datensatz, Story (sensibel)."""
    from ..workflow import repo

    draft = store.db.execute(
        "SELECT * FROM drafts WHERE wp_post_id = ? OR (uid = ? AND ? != '') ORDER BY wp_post_id = ? DESC, id DESC "
        "LIMIT 1", (b.wp_post_id, b.radar_uid, b.radar_uid, b.wp_post_id)).fetchone()
    story_id = b.story_id or (draft["story_id"] if draft is not None else None)
    if story_id:
        story = repo.story(store, story_id)
        b.sensibel = bool(story and story.get("sensibel"))
        b.story_id = story_id
    if draft is not None and draft["bild_datei"]:
        pfad = settings.bilder_dir / draft["bild_datei"]
        b.asset = repo.asset_fuer_entwurf(store, draft["id"], draft["bild_datei"])  # nie der eines anderen Entwurfs
        b.bild_pfad = pfad if pfad.is_file() else None
        b.bild_ki = bool((b.asset or {}).get("ki")) or (b.asset or {}).get("herkunft") == "ki" \
            or draft["bild_origin"] == "ki"
    return b


def wp_abruf(settings) -> Abruf:
    """Abruf über `net.safe_get` (SSRF-Schutz, Größenlimit). Öffentliche Beiträge brauchen keine Anmeldung."""
    from .. import net

    basis = f"{settings.wp_url.rstrip('/')}/wp-json/wp/v2/posts"

    def abruf(params: dict) -> list[dict]:
        # HTTP-Fehler wirft safe_get selbst (net.HTTPError); `lauf` fängt sie ab und sendet trotzdem
        daten = net.safe_get(basis, params=params, headers={"Accept": "application/json"}, timeout=20).json()
        return daten if isinstance(daten, list) else []

    return abruf


def abfrage(startmarke: datetime, jetzt: datetime, seite: int = 1) -> dict:
    """Parameter für /wp/v2/posts: nur Veröffentlichtes ab einem Tag vor der Startmarke (WordPress filtert nach
    Ortszeit; genau wird lokal über date_gmt geprüft), höchstens 14 Tage zurück."""
    ab = max(startmarke - timedelta(days=1), jetzt - timedelta(days=14))
    return {"status": "publish", "per_page": 50, "page": seite, "orderby": "date", "order": "desc",
            "after": ab.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds"),
            "_embed": "wp:term"}
