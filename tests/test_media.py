"""Bildkette mit Lizenz: Archiv → Quelle (nur mit Erlaubnis) → Stock → Pool → KI (max. 1, Budget) → Bildkarte."""

import base64
import io
import json

import pytest
from PIL import Image

from news_radar.agents import Kontext, media
from news_radar.config import Source, load_settings
from news_radar.store import Store
from news_radar.workflow import costs, repo


def _png(farbe=(200, 30, 30)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (1600, 900), farbe).save(buf, "PNG")
    return buf.getvalue()


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    for var in ("UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY", "BILD_POOL_DIR"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    store = Store(s.db_path)
    yield Kontext(settings=s, store=store, budget=costs.Budget(store, 5, 150))
    store.close()


STORY = {"id": 1, "typ": "news"}
FELDER = {"titel": "Tempelfest in Hamm", "kategorie": "community", "bild_thema": "tempelfest",
          "bild_prompt": "Temple courtyard at dusk with oil lamps, no people in focus"}


def test_archive_image_with_license_comes_first_and_expired_is_skipped(ctx):
    ordner = ctx.settings.data_dir / "archiv"
    ordner.mkdir()
    (ordner / "alt.jpg").write_bytes(_png())
    (ordner / "neu.jpg").write_bytes(_png((10, 10, 200)))
    (ordner / "archiv.json").write_text(json.dumps([
        {"datei": "alt.jpg", "themen": ["tempelfest"], "rechteinhaber": "A", "lizenz": "L", "ablauf": "2020-01-01"},
        {"datei": "ohne-lizenz.jpg", "themen": ["tempelfest"], "rechteinhaber": "B"},
        {"datei": "neu.jpg", "themen": ["tempelfest"], "rechteinhaber": "Foto Kumar", "lizenz": "Nutzungsrecht tamil.de",
         "attribution": "Foto: Kumar"},
    ]))
    bild, versucht = media.besorgen(ctx, STORY, FELDER, "s1", kategorie_label="Community")
    assert bild.image.origin == "archiv" and bild.rechteinhaber == "Foto Kumar" and versucht == []
    name, asset_id = media.speichern(ctx, bild, "s1-tempel", 1)
    asset = repo.asset_fuer_datei(ctx.store, name)
    assert asset["lizenz"] == "Nutzungsrecht tamil.de" and asset["sha256"] and not asset["ki"]


def test_press_image_only_with_documented_permission(ctx, monkeypatch):
    from news_radar import net

    class Got:
        content = _png()

    monkeypatch.setattr(net, "safe_get", lambda url, **kw: Got())
    ohne = Source(name="Verlag", type="rss")
    bild, versucht = media.besorgen(ctx, STORY, FELDER, "s1", kategorie_label="Community", quelle=ohne,
                                    quelle_bild="https://verlag.de/bild.jpg")
    assert bild.image.origin == "karte" and "quelle" in versucht
    mit = Source(name="Swiss Tamil Media", type="rss", bild_nutzen=True, betreiber="Swiss Tamil Media",
                 vertrag="Mail 10/2026")
    bild, _ = media.besorgen(ctx, STORY, FELDER, "s1", kategorie_label="Community", quelle=mit,
                             quelle_bild="https://swisstamilmedia.com/bild.jpg")
    assert bild.image.origin == "quelle" and "Mail 10/2026" in bild.lizenz and bild.image.credit == "Foto: Swiss Tamil Media"


def test_ki_image_at_most_once_per_story_with_budget_and_cost(ctx):
    ctx.settings.gemini_key = "test"
    ctx.settings.bild_retry_pause = 0
    data = base64.b64encode(_png()).decode()
    ctx.bild_transport = lambda headers, body: (200, {"status": "completed", "outputs": [{"type": "image", "data": data}]})
    bild, _ = media.besorgen(ctx, STORY, FELDER, "s1", kategorie_label="Community")
    assert bild.image.origin == "ki" and bild.ki
    media.speichern(ctx, bild, "s1-ki", 1)
    usage = dict(ctx.store.db.execute("SELECT * FROM agent_usage WHERE rolle = 'bild'").fetchone())
    assert usage["provider"] == "gemini" and usage["bilder"] == 1 and usage["kosten_usd"] == pytest.approx(0.0336)
    zweites, versucht = media.besorgen(ctx, STORY, {**FELDER, "bild_thema": "kino-saal"}, "s1b", kategorie_label="Community")
    assert zweites.image.origin == "karte" and "ki" in versucht  # höchstens ein KI-Bild je Story
    ctx.budget = costs.Budget(ctx.store, 0.0, 150)
    leer, _ = media.besorgen(ctx, {"id": 2, "typ": "news"}, {**FELDER, "bild_thema": "kino-saal"}, "s2", kategorie_label="x")
    assert leer.image.origin == "karte"
