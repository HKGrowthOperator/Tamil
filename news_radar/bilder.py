"""Beitragsbild-Kette: KI-Symbolbild → Bildpool → Stockfoto → Bildkarte. Es gibt keinen Beitrag ohne Bild.

- KI: Gemini-Bildmodell („Nano Banana“) über die Interactions-API, Prompt aus prompts/bild.md + Motiv des Writers.
  Nur mit `bild_prompt` – Rohfassungen bekommen ein Reserve-Bild, das KI-Bild entsteht mit dem fertigen Text.
- Bildpool: je Thema (prompts/bildpool.md) mehrere Symbolbilder unter data/bildpool/<thema>/, das am wenigsten
  genutzte zuerst. KI-Treffer wandern zusätzlich in den Pool ihres Themas.
- Stock/Karte: wie bisher in images.py (Unsplash/Pexels nur mit Schlüssel, sonst Tamil.de-Bildkarte).

KI-Bilder sind Symbolbilder und werden so gekennzeichnet (Bildnachweis), siehe prompts/bild.md.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator

import requests
from PIL import Image, ImageOps

from . import images, prompts
from .config import Settings
from .images import SIZE, FeaturedImage

log = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
KI_CREDIT = "Symbolbild: KI-generiert · Tamil.de"
MODI = ("ki", "pool", "stock", "karte")
# (headers, body) -> (status, json) – austauschbar für Tests
Transport = Callable[[dict, dict], tuple[int, dict]]


def _http_transport(timeout: float) -> Transport:
    def send(headers: dict, body: dict) -> tuple[int, dict]:
        resp = requests.post(GEMINI_URL, headers=headers, json=body, timeout=timeout)
        try:
            data = resp.json()
        except ValueError:
            data = {"text": resp.text[:300]}
        return resp.status_code, data if isinstance(data, dict) else {"data": data}

    return send


def _image_blocks(obj) -> Iterator[dict]:
    """Alle Bildblöcke {"type": "image", "data": …} in der Antwort, egal wie tief sie liegen."""
    if isinstance(obj, dict):
        if obj.get("type") == "image" and obj.get("data"):
            yield obj
        for value in obj.values():
            yield from _image_blocks(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _image_blocks(value)


def gemini_request(prompt: str, settings: Settings) -> dict:
    return {
        "model": settings.bild_modell,
        "input": prompt,
        "store": False,
        "response_format": {
            "type": "image",
            "mime_type": "image/png",
            "aspect_ratio": "16:9",
            "image_size": settings.bild_groesse,
        },
    }


def from_gemini(prompt: str, settings: Settings, slug: str, transport: Transport | None = None) -> FeaturedImage | None:
    """Ein Symbolbild von der Bild-KI; None bei fehlendem Schlüssel, Fehler oder unbrauchbarer Antwort (nie Exception)."""
    if not settings.gemini_key or not prompt.strip():
        return None
    headers = {"x-goog-api-key": settings.gemini_key, "Content-Type": "application/json"}
    body = gemini_request(prompt, settings)
    send = transport or _http_transport(90)
    status, data = 0, {}
    for attempt in (1, 2):
        try:
            status, data = send(headers, body)
        except requests.RequestException as exc:
            log.warning("Bild-KI nicht erreichbar: %s", exc)
            status, data = 0, {}
        if status == 200:
            break
        if (status == 0 or status == 429 or status >= 500) and attempt == 1:
            time.sleep(settings.bild_retry_pause)
            continue
        log.warning("Bild-KI antwortet %s: %s", status, json.dumps(data, ensure_ascii=False)[:300])
        return None
    if status != 200:
        return None
    if data.get("errors") or data.get("status") not in (None, "completed"):
        log.warning("Bild-KI ohne Ergebnis (%s): %s", data.get("status"), json.dumps(data.get("errors"), ensure_ascii=False)[:300])
        return None
    block = next(_image_blocks(data), None)
    if block is None:
        log.warning("Bild-KI-Antwort ohne Bildblock")
        return None
    try:
        raw = base64.b64decode(block["data"])
        with Image.open(io.BytesIO(raw)) as img:
            fitted = ImageOps.fit(img.convert("RGB"), SIZE, Image.Resampling.LANCZOS)
    except (OSError, ValueError, TypeError) as exc:
        log.warning("Bild-KI-Bild unbrauchbar: %s", exc)
        return None
    return FeaturedImage(images._encode(fitted), f"{slug}.jpg", "image/jpeg", KI_CREDIT, "ki")


class BildPool:
    """Reserve-Bilder je Thema mit Nutzungszähler (pool.json)."""

    def __init__(self, folder: Path):
        self.folder = folder
        self.index = folder / "pool.json"
        self._data: dict[str, list[dict]] = {}
        if self.index.exists():
            try:
                self._data = json.loads(self.index.read_text(encoding="utf-8"))
            except ValueError:
                log.warning("pool.json unlesbar – Pool wird neu aufgebaut")
                self._data = {}

    def _save(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        self.index.write_text(json.dumps(self._data, ensure_ascii=False, indent=1), encoding="utf-8")

    def themen(self) -> list[str]:
        return sorted(self._data)

    def status(self) -> dict[str, dict]:
        return {t: {"anzahl": len(e), "genutzt": sum(x.get("genutzt", 0) for x in e)} for t, e in sorted(self._data.items())}

    def anzahl(self, thema: str) -> int:
        return len(self._data.get(thema, []))

    def add(self, thema: str, image: FeaturedImage, prompt: str = "") -> Path:
        entries = self._data.setdefault(thema, [])
        name = f"{thema}-{len(entries) + 1:03d}.jpg"
        (self.folder / thema).mkdir(parents=True, exist_ok=True)
        (self.folder / thema / name).write_bytes(image.data)
        entries.append({
            "datei": name, "prompt": prompt, "credit": image.credit, "origin": image.origin,
            "erstellt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "genutzt": 0,
        })
        self._save()
        return self.folder / thema / name

    def pick(self, thema: str, slug: str) -> FeaturedImage | None:
        """Das am wenigsten genutzte Bild des Themas (bei Gleichstand das älteste); zählt die Nutzung hoch."""
        entries = [e for e in self._data.get(thema, []) if (self.folder / thema / e["datei"]).exists()]
        if not entries:
            return None
        entry = min(entries, key=lambda e: (e.get("genutzt", 0), e.get("erstellt", "")))
        entry["genutzt"] = entry.get("genutzt", 0) + 1
        self._save()
        data = (self.folder / thema / entry["datei"]).read_bytes()
        return FeaturedImage(data, f"{slug}.jpg", "image/jpeg", entry.get("credit") or KI_CREDIT, "pool")

    def fuellen(self, settings: Settings, thema: str | None = None, anzahl: int = 3,
                transport: Transport | None = None) -> dict[str, int]:
        """Erzeugt fehlende Bilder je Thema aus den Motiv-Prompts in prompts/bildpool.md."""
        themen = [thema] if thema else prompts.thema_slugs()
        erzeugt: dict[str, int] = {}
        for t in themen:
            motiv = prompts.motiv_fuer_thema(t)
            if not motiv:
                log.warning("Thema %s steht nicht in bildpool.md", t)
                continue
            for n in range(self.anzahl(t), anzahl):
                prompt = prompts.bild_prompt_bauen(motiv, t)
                image = from_gemini(prompt, settings, f"{t}-{n + 1}", transport)
                if image is None:
                    break
                self.add(t, image, prompt)
                erzeugt[t] = erzeugt.get(t, 0) + 1
        return erzeugt


def beitragsbild(
    settings: Settings,
    *,
    titel: str,
    kategorie: str,
    kategorie_label: str,
    slug: str,
    bild_prompt: str = "",
    bild_thema: str = "",
    bild_suchbegriff: str = "",
    transport: Transport | None = None,
    pool: BildPool | None = None,
) -> FeaturedImage:
    """Immer ein Bild: KI (nur mit Prompt und Schlüssel) → Pool → Stock (nur mit Schlüssel) → Karte."""
    modus = settings.bild_modus if settings.bild_modus in MODI else "ki"
    thema = bild_thema or prompts.thema_fuer(kategorie, titel)
    if modus == "karte":
        return images.branded_card(titel, kategorie_label, slug, kategorie)
    pool = pool or BildPool(settings.bildpool_dir)
    if modus == "ki" and bild_prompt.strip() and settings.gemini_key:
        prompt = prompts.bild_prompt_bauen(bild_prompt, thema)
        image = from_gemini(prompt, settings, slug, transport)
        if image is not None:
            if thema:
                try:
                    pool.add(thema, image, prompt)
                except OSError as exc:
                    log.warning("Pool nicht beschreibbar: %s", exc)
            return image
    if modus in ("ki", "pool") and thema:
        image = pool.pick(thema, slug)
        if image is not None:
            return image
    return images.featured_image(settings, bild_suchbegriff or titel, titel, kategorie_label, slug)
