"""Bildkette: Gemini-Client (Fake-Transport), Bildpool, Reihenfolge KI → Pool → Stock → Karte."""

import base64
import io
import json

import pytest
from PIL import Image

from news_radar import bilder, prompts
from news_radar.config import load_settings
from news_radar.images import FeaturedImage


def _png(color=(200, 16, 46), size=(1024, 576)) -> str:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _antwort(data_b64: str | None = _png(), status: str = "completed") -> dict:
    content = [{"type": "text", "text": "Here is your image."}]
    if data_b64:
        content.append({"type": "image", "data": data_b64, "mime_type": "image/png"})
    return {"id": "int_1", "status": status, "steps": [{"type": "model_output", "content": content}]}


class FakeTransport:
    def __init__(self, *antworten):
        self.antworten = list(antworten)
        self.calls: list[tuple[dict, dict]] = []

    def __call__(self, headers, body):
        self.calls.append((headers, body))
        return self.antworten.pop(0)


@pytest.fixture
def settings(monkeypatch, tmp_path):
    for var in ("WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "BILD_POOL_DIR"):
        monkeypatch.setenv(var, "")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    s = load_settings()
    s.data_dir = tmp_path
    s.bild_retry_pause = 0
    return s


def test_from_gemini_builds_request_retries_and_returns_fitted_jpeg(settings):
    transport = FakeTransport((429, {"error": "quota"}), (200, _antwort()))
    image = bilder.from_gemini("A quiet cinema foyer", settings, "test-slug", transport)
    assert image is not None and image.origin == "ki" and image.filename == "test-slug.jpg"
    assert image.credit == bilder.KI_CREDIT and image.mime == "image/jpeg"
    with Image.open(io.BytesIO(image.data)) as img:
        assert img.size == (1200, 675)
    headers, body = transport.calls[0]
    assert headers["x-goog-api-key"] == "test-key"
    assert body["model"] == "gemini-nano-banana-2.1" and body["input"] == "A quiet cinema foyer" and body["store"] is False
    assert body["response_format"] == {"type": "image", "mime_type": "image/png", "aspect_ratio": "16:9", "image_size": "1K"}
    assert len(transport.calls) == 2  # 429 → ein Retry


def test_from_gemini_never_raises(settings):
    assert bilder.from_gemini("x", settings, "s", FakeTransport((400, {"error": {"message": "bad"}}))) is None
    assert bilder.from_gemini("x", settings, "s", FakeTransport((200, _antwort(None)))) is None
    assert bilder.from_gemini("x", settings, "s", FakeTransport((200, _antwort(status="failed")))) is None
    assert bilder.from_gemini("x", settings, "s", FakeTransport((500, {}), (503, {}))) is None
    kaputt = _antwort(base64.b64encode(b"kein bild").decode())
    assert bilder.from_gemini("x", settings, "s", FakeTransport((200, kaputt))) is None
    settings.gemini_key = ""
    assert bilder.from_gemini("x", settings, "s", FakeTransport((200, _antwort()))) is None


def test_bildpool_add_pick_least_used_and_status(tmp_path):
    pool = bilder.BildPool(tmp_path / "pool")
    assert pool.pick("kino-saal", "s") is None and pool.status() == {}
    a = FeaturedImage(b"AAA", "a.jpg", "image/jpeg", bilder.KI_CREDIT, "ki")
    b = FeaturedImage(b"BBB", "b.jpg", "image/jpeg", bilder.KI_CREDIT, "ki")
    pool.add("kino-saal", a, "prompt a")
    pool.add("kino-saal", b, "prompt b")
    assert pool.pick("kino-saal", "x").data == b"AAA"  # beide 0× genutzt → das ältere
    assert pool.pick("kino-saal", "x").data == b"BBB"  # jetzt ist a 1× genutzt → b
    third = pool.pick("kino-saal", "x")
    assert third.data == b"AAA" and third.origin == "pool" and third.filename == "x.jpg"
    assert pool.status() == {"kino-saal": {"anzahl": 2, "genutzt": 3}}
    # Index überlebt ein Neuladen
    assert bilder.BildPool(tmp_path / "pool").status()["kino-saal"]["genutzt"] == 3
    assert json.loads((tmp_path / "pool" / "pool.json").read_text())["kino-saal"][0]["prompt"] == "prompt a"


def test_beitragsbild_chain_ki_then_pool_then_card(settings):
    pool = bilder.BildPool(settings.bildpool_dir)
    transport = FakeTransport((200, _antwort()))
    ki = bilder.beitragsbild(settings, titel="Jailer 2 im Kino", kategorie="kino", kategorie_label="Kino", slug="s1",
                             bild_prompt="Empty cinema hall, amber light", bild_thema="kino-saal", transport=transport, pool=pool)
    assert ki.origin == "ki" and pool.anzahl("kino-saal") == 1  # KI-Treffer wandert in den Pool
    assert "Scene: Empty cinema hall, amber light" in transport.calls[0][1]["input"]
    # Rohfassung ohne Prompt: kein KI-Aufruf, Reserve aus dem Pool
    reserve = bilder.beitragsbild(settings, titel="Kinowoche", kategorie="kino", kategorie_label="Kino", slug="s2",
                                  transport=FakeTransport(), pool=pool)
    assert reserve.origin == "pool" and reserve.filename == "s2.jpg" and reserve.credit == bilder.KI_CREDIT
    # Thema ohne Poolbild, keine Stock-Schlüssel → Bildkarte
    karte = bilder.beitragsbild(settings, titel="Pongal in Hamm", kategorie="community", kategorie_label="Community",
                                slug="s3", transport=FakeTransport(), pool=pool)
    assert karte.origin == "karte"
    # KI schlägt fehl → Pool des Themas
    fehl = bilder.beitragsbild(settings, titel="Film", kategorie="kino", kategorie_label="Kino", slug="s4",
                               bild_prompt="x", bild_thema="kino-saal", transport=FakeTransport((400, {})), pool=pool)
    assert fehl.origin == "pool"
    settings.bild_modus = "karte"
    assert bilder.beitragsbild(settings, titel="Film", kategorie="kino", kategorie_label="Kino", slug="s5",
                               bild_prompt="x", transport=FakeTransport((200, _antwort())), pool=pool).origin == "karte"


def test_bildpool_fuellen_uses_theme_prompts(settings):
    pool = bilder.BildPool(settings.bildpool_dir)
    transport = FakeTransport(*[(200, _antwort())] * 2)
    erzeugt = pool.fuellen(settings, thema="kolam", anzahl=2, transport=transport)
    assert erzeugt == {"kolam": 2} and pool.anzahl("kolam") == 2
    assert "rice-flour kolam" in transport.calls[0][1]["input"] and "no text" in transport.calls[0][1]["input"]
    assert pool.fuellen(settings, thema="kolam", anzahl=2, transport=FakeTransport()) == {}  # nichts fehlt
    assert pool.fuellen(settings, thema="gibt-es-nicht", anzahl=1, transport=FakeTransport()) == {}


def test_thema_defaults_follow_bildpool_table():
    assert set(prompts.thema_slugs()) >= {"tempelfest", "kino-saal", "konzert-buehne", "gericht-tisch", "cricket", "kolam"}
    assert prompts.thema_fuer("kueche", "Rezept für Kottu Roti") == "gericht-tisch"
    assert prompts.thema_fuer("news", "Abschiebung nach Sri Lanka gestoppt") == "behoerde-deutschland"
