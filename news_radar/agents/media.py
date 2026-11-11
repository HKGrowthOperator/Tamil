"""Bild mit Lizenz: Archiv → Quelle → Stock → Pool → KI → Bildkarte (Reihenfolge per BILD_REIHENFOLGE).

- archiv: lizenzierte eigene Bilder unter data/archiv/ mit archiv.json (Rechteinhaber, Lizenz, Umfang, Ablauf, Themen)
- quelle: Pressebild der Quelle nur, wenn im Register `bild_nutzen = true` steht (dokumentierte Erlaubnis)
- stock: Unsplash/Pexels mit Schlüssel, Lizenz der Plattform
- pool: Reserve-Symbolbilder (KI) je Thema
- ki: neues KI-Symbolbild – höchstens RADAR_KI_BILDER_JE_ARTIKEL je Story, nur mit Budget
- karte: Tamil.de-Bildkarte (immer möglich)
Jedes Bild bekommt einen Datensatz in `assets`. KI-Bilder bleiben als Symbolbild gekennzeichnet.
"""

from __future__ import annotations

import io
import json
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import requests
from PIL import Image, ImageOps

from .. import bilder, images, net, prompts, schalter
from ..config import Source
from ..images import SIZE, FeaturedImage
from ..workflow import costs, repo
from ..workflow.providers import usage_protokollieren
from . import Kontext

log = logging.getLogger(__name__)


@dataclass
class Bild:
    image: FeaturedImage
    rechteinhaber: str
    lizenz: str
    umfang: str = "Online-Veröffentlichung auf tamil.de"
    attribution: str = ""
    ablauf: str = ""
    quelle_url: str = ""
    ki: bool = False


def _archiv(ctx: Kontext, thema: str, kategorie: str, slug: str) -> Bild | None:
    ordner = ctx.settings.data_dir / "archiv"
    index = ordner / "archiv.json"
    if not index.exists():
        return None
    try:
        eintraege = json.loads(index.read_text(encoding="utf-8"))
    except ValueError:
        log.warning("archiv.json unlesbar")
        return None
    heute = date.today().isoformat()
    for e in eintraege:
        themen = set(e.get("themen") or []) | set(e.get("rubriken") or [])
        if thema not in themen and kategorie not in themen:
            continue
        if e.get("ablauf") and e["ablauf"] < heute:
            continue
        pfad = ordner / e.get("datei", "")
        if not e.get("lizenz") or not e.get("rechteinhaber") or not pfad.is_file():
            continue  # ohne dokumentierte Lizenz kein Bild
        data = images.from_upload(pfad.read_bytes(), slug, credit=e.get("attribution") or f"Foto: {e['rechteinhaber']}")
        return Bild(FeaturedImage(data.data, data.filename, data.mime, data.credit, "archiv"), e["rechteinhaber"],
                    e["lizenz"], e.get("umfang") or "Online-Veröffentlichung auf tamil.de", data.credit, e.get("ablauf", ""))
    return None


def _quelle(source: Source | None, bild_url: str, slug: str) -> Bild | None:
    if not source or not source.bild_nutzen or not bild_url:
        return None
    try:
        got = net.safe_get(bild_url, accept=net.IMAGE_TYPES, max_bytes=8_000_000, timeout=10)
        with Image.open(io.BytesIO(got.content)) as img:
            fitted = ImageOps.fit(ImageOps.exif_transpose(img).convert("RGB"), SIZE, Image.Resampling.LANCZOS)
    except (requests.RequestException, ValueError, OSError) as exc:
        log.info("Pressebild nicht übernommen: %s", exc)
        return None
    credit = f"Foto: {source.betreiber or source.name}"
    return Bild(FeaturedImage(images._encode(fitted), f"{slug}.jpg", "image/jpeg", credit, "quelle"),
                source.betreiber or source.name, f"Erlaubnis laut Quellen-Register ({source.vertrag or 'bild_nutzen'})",
                attribution=credit, quelle_url=bild_url)


def _stock(ctx: Kontext, suchbegriff: str, slug: str) -> Bild | None:
    s = ctx.settings
    for fn, key, plattform in ((images.from_unsplash, s.unsplash_key, "Unsplash"), (images.from_pexels, s.pexels_key, "Pexels")):
        if not key:
            continue
        try:
            img = fn(suchbegriff, key, slug)
        except requests.RequestException as exc:
            log.info("Stockfoto (%s) fehlgeschlagen: %s", plattform, exc)
            continue
        if img:
            return Bild(img, img.credit.removeprefix("Foto: ").split(" / ")[0], f"{plattform} License", attribution=img.credit)
    return None


def _ki_bilder(ctx: Kontext, story_id: int) -> int:
    return ctx.store.db.execute("SELECT COUNT(*) FROM assets WHERE story_id = ? AND herkunft = 'ki'", (story_id,)).fetchone()[0]


def _ki(ctx: Kontext, story_id: int, bild_prompt: str, thema: str, slug: str, pool: bilder.BildPool) -> Bild | None:
    s = ctx.settings
    if not s.gemini_key or not bild_prompt.strip() or _ki_bilder(ctx, story_id) >= s.ki_bilder_je_artikel:
        return None
    betrag = costs.bild_kosten(s.bild_modell, s.bild_groesse)
    reservierung = None
    if ctx.budget is not None:
        try:
            reservierung = ctx.budget.reservieren(betrag, "bild", story_id)
        except costs.BudgetErschoepft:
            log.info("KI-Bild übersprungen: Budget erreicht")
            return None
    try:
        prompt = prompts.bild_prompt_bauen(bild_prompt, thema)
        img = bilder.from_gemini(prompt, s, slug, ctx.bild_transport)
        usage_protokollieren(ctx.store, rolle="bild", provider="gemini", modell_angefragt=s.bild_modell,
                             modell=s.bild_modell, usd=betrag if img else 0.0, bilder=1 if img else 0,
                             status="ok" if img else "fehler", story_id=story_id)
    finally:
        if reservierung is not None:
            ctx.budget.freigeben(reservierung)
    if img is None:
        return None
    if thema:
        try:
            pool.add(thema, img, prompt)
        except (OSError, ValueError) as exc:
            log.warning("Pool nicht beschreibbar: %s", exc)
    return Bild(img, "Tamil.de (KI-generiert)", "KI-generiert – Symbolbild, keine Abbildung des Ereignisses",
                attribution=bilder.KI_CREDIT, ki=True)


def besorgen(ctx: Kontext, story: dict, felder: dict, slug: str, *, kategorie_label: str,
             quelle: Source | None = None, quelle_bild: str = "") -> tuple[Bild, list[str]]:
    """Das erste verfügbare Bild in der eingestellten Reihenfolge; die Bildkarte fällt nie aus."""
    s = ctx.settings
    thema = bilder.gueltiges_thema(felder.get("bild_thema") or "", felder.get("kategorie") or "", felder.get("titel") or "")
    pool = bilder.BildPool(s.bildpool_dir)
    versucht = []
    for stufe in s.bild_reihenfolge:
        bild = None
        if stufe in ("quelle", "stock", "ki"):  # Aufruf nach außen: Gestoppt geht nach oben, kein Ausweichen
            schalter.pruefen(ctx.store, "redaktion")
        if stufe == "archiv":
            bild = _archiv(ctx, thema, felder.get("kategorie") or "", slug)
        elif stufe == "quelle":
            bild = _quelle(quelle, quelle_bild, slug)
        elif stufe == "stock":
            bild = _stock(ctx, felder.get("bild_suchbegriff") or felder.get("titel") or "", slug)
        elif stufe == "pool" and thema:
            img = pool.pick(thema, slug)
            if img:
                bild = Bild(img, "Tamil.de (KI-generiert)", "KI-generiert – Symbolbild aus der Bildreserve",
                            attribution=img.credit, ki=True)
        elif stufe == "ki":
            bild = _ki(ctx, story["id"], felder.get("bild_prompt") or "", thema, slug, pool)
        elif stufe == "karte":
            img = images.branded_card(felder.get("titel") or "", kategorie_label, slug, felder.get("kategorie") or "")
            bild = Bild(img, "Tamil.de", "eigene Grafik", attribution=img.credit)
        if bild is not None:
            return bild, versucht
        versucht.append(stufe)
    img = images.branded_card(felder.get("titel") or "", kategorie_label, slug, felder.get("kategorie") or "")
    return Bild(img, "Tamil.de", "eigene Grafik", attribution=img.credit), versucht


def speichern(ctx: Kontext, bild: Bild, stem: str, story_id: int | None) -> tuple[str, int]:
    """Bild + Vorschaubild ablegen und den Lizenz-Datensatz anlegen. (Dateiname, asset_id)"""
    ordner = ctx.settings.bilder_dir
    vorher = {n: (ordner / n).exists() for n in (f"{stem}.jpg", f"{stem}-thumb.jpg")} if ordner.exists() else {}
    name, thumb = images.save_pair(bild.image, ordner, stem)
    try:
        asset_id = repo.asset_anlegen(
            ctx.store, datei=name, herkunft=bild.image.origin, rechteinhaber=bild.rechteinhaber, lizenz=bild.lizenz,
            umfang=bild.umfang, attribution=bild.attribution, ablauf=bild.ablauf, quelle_url=bild.quelle_url,
            ki=bild.ki, story_id=story_id, daten=bild.image.data,
        )
    except BaseException:
        # ohne Lizenz-Datensatz kein Bild: neu angelegte Dateien wieder weg (vorhandene gleiche Dateien bleiben)
        for n in (name, thumb):
            if not vorher.get(n) and not ctx.store.db.execute(
                    "SELECT 1 FROM drafts WHERE bild_datei = ? LIMIT 1", (name,)).fetchone():
                (ordner / n).unlink(missing_ok=True)
        raise
    return name, asset_id


def archiv_vorlage(ordner: Path) -> Path:
    """Legt eine leere archiv.json mit Beispiel an, damit die Redaktion weiß, welche Angaben Pflicht sind."""
    ordner.mkdir(parents=True, exist_ok=True)
    index = ordner / "archiv.json"
    if not index.exists():
        index.write_text(json.dumps([{
            "datei": "beispiel.jpg", "themen": ["tempelfest"], "rubriken": ["community"],
            "rechteinhaber": "Name der Fotografin", "lizenz": "Nutzungsrecht für tamil.de, unbefristet",
            "umfang": "Online-Veröffentlichung auf tamil.de und Social Media", "attribution": "Foto: Name",
            "ablauf": "",
        }], ensure_ascii=False, indent=1), encoding="utf-8")
    return index
