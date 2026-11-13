"""Social-Bild im Hochformat 1080 × 1350 (Instagram 4:5, JPEG): Beitragsbild mit schmaler Logo-Leiste (F4 Frage 2,
Vorschlag zum Start) oder die Bildkarte „Grafik: Tamil.de“, wenn das Recht für soziale Netze fehlt (R4).

Ein Bild aus der KI trägt den Hinweis wie auf der Website in der Leiste (R8). Fremde Bilder lädt dieses Modul nie: das
Foto kommt aus der lokalen Datei des Radars. Gestaltung wie die vorhandene Bildkarte; das neue Design folgt später.
"""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from .. import images

GROESSE = (1080, 1350)
LEISTE = 96


def _jpeg(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=88, optimize=True, progressive=True)
    return buf.getvalue()


def _wortmarke(draw: ImageDraw.ImageDraw, x: int, y: int, groesse: int, farbe=images.TINTE) -> None:
    font = images._font(groesse)
    draw.text((x, y), "tamil", font=font, fill=farbe)
    draw.text((x + draw.textlength("tamil", font=font), y), ".de", font=font, fill=images.ROT)


def foto(daten: bytes, *, nachweis: str = "", ki_hinweis: str = "") -> bytes:
    """Beitragsbild auf 1080 × 1350 zuschneiden, unten eine schmale Leiste mit Wortmarke und Hinweis."""
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(daten))).convert("RGB")
    flaeche = ImageOps.fit(img, (GROESSE[0], GROESSE[1] - LEISTE), Image.Resampling.LANCZOS)
    bild = Image.new("RGB", GROESSE, images.SAND)
    bild.paste(flaeche, (0, 0))
    draw = ImageDraw.Draw(bild)
    y = GROESSE[1] - LEISTE
    _wortmarke(draw, 48, y + 22, 44)
    hinweis = " · ".join(t for t in (ki_hinweis, nachweis) if t)
    if hinweis:
        font = images._font(26, "Bold")
        breite = draw.textlength(hinweis, font=font)
        draw.text((GROESSE[0] - 48 - breite, y + 34), hinweis[:80], font=font, fill=images.TINTE_2)
    return _jpeg(bild)


def karte(titel: str, rubrik_label: str, rubrik: str = "") -> bytes:
    """Bildkarte ohne Foto: Sand, Rubrikpunkt, Schlagzeile, Kolam in der Rubrikfarbe, Wortmarke, „Grafik: Tamil.de“."""
    farbe = images.RUBRIK_FARBEN.get(rubrik, images.ROT)
    bild = Image.new("RGB", GROESSE, images.SAND)
    draw = ImageDraw.Draw(bild)
    hell = tuple(int(c + (s - c) * 0.72) for c, s in zip(farbe, images.SAND))
    images._kolam(draw, GROESSE[0] - 150, GROESSE[1] - 330, 380, hell, 16)
    draw.ellipse([80, 112, 80 + 26, 112 + 26], fill=farbe)
    draw.text((124, 98), rubrik_label or "Tamil.de", font=images._font(42, "Bold"), fill=images.TINTE)
    font = images._font(78)
    y = 220
    for zeile in images._wrap(draw, titel or "", font, GROESSE[0] - 160)[:6]:
        draw.text((80, y), zeile, font=font, fill=images.TINTE)
        y += 92
    _wortmarke(draw, 80, GROESSE[1] - 150, 52)
    draw.text((80, GROESSE[1] - 84), "Grafik: Tamil.de", font=images._font(26, "Bold"), fill=images.TINTE_2)
    return _jpeg(bild)


def ablegen(daten: bytes, ordner: Path) -> str:
    """Unter data/social/social-<sha256[:32]>.jpg speichern (nie in place überschreiben); gibt den Dateinamen."""
    ordner.mkdir(parents=True, exist_ok=True)
    name = f"social-{hashlib.sha256(daten).hexdigest()[:32]}.jpg"
    images._schreiben(ordner / name, daten)
    return name
