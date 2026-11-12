"""Kino-HTML-Weg (Anbieter "html"), Funde der Prüfung 11.11.2026: Tamil-Erkennung nur über Titel und Sprachangabe,
Seiten ohne Uhrzeit ergeben eine Laufzeit „ab Datum“ statt 00:00. Ohne Netz, gegen gespeicherte Seiten."""

from datetime import datetime
from pathlib import Path

import pytest

from news_radar import kino_providers as kp
from news_radar import sources
from news_radar.config import load_settings

FIX = Path(__file__).parent / "fixtures"
STAND = datetime(2026, 11, 11, 12, tzinfo=kp.TZ)
BABYLON = "Babylon Berlin · IndoGerman Film"


class Antwort:
    def __init__(self, inhalt: bytes):
        self.status_code = 200
        self.content = inhalt
        self.headers = {"Content-Type": "text/html; charset=utf-8"}

    def iter_content(self, size):
        yield self.content

    def raise_for_status(self):
        pass

    def close(self):
        pass


@pytest.fixture
def settings(monkeypatch):
    for var in ("WP_USER", "WP_APP_PASSWORD", "NEWSAPI_KEY", "GNEWS_TOKEN"):
        monkeypatch.setenv(var, "")
    return load_settings()


def _quelle(settings, name):
    return next(q for q in settings.alle_quellen if q.name == name)


def _seite(monkeypatch, inhalt: bytes):
    monkeypatch.setattr(sources.requests, "get", lambda url, **kw: Antwort(inhalt))


@pytest.mark.parametrize("titel,sprache", [
    ("Scene (Tamil)", ""), ("Jailer 2 [Tamil]", ""), ("(tamil) Jailer 2", ""), ("Jailer 2 (Tamil OmeU)", ""),
    ("OM", "Tamil version with English subs"), ("OM", "tamil Original mit engl. Untertitel"), ("Coolie", "Tamil OmU"),
    ("Coolie", "OV Tamil"), ("Scene", "Tamil"), ("Leo", "Sprache: Tamil"),
    ("IndoGerman Film: OM", "IndoGerman Film: OM (OmeU) \\[Tamil\\], IN 2026, R: Rajkumar Periasamy"),
])
def test_tamil_fassung_ueber_titel_oder_sprache(titel, sprache):
    assert kp.ist_tamil_fassung(titel, sprache)


@pytest.mark.parametrize("titel,sprache", [
    ("Yeh Prem Mol Liya", "hindi Original mit engl. Untertitel"),
    ("IndoGerman Film: OM", "(OmeU) \\[Telugu\\], gedreht in Andhra Pradesh und Tamil Nadu"),
    ("Kaantha", "Telugu version, Remake eines Tamil-Klassikers"),
    ("Tamil Nadu – Land der Tempel", ""),  # Dokumentarfilm über die Region, keine tamilische Fassung
    ("Reise durch Tamil Nadu (Doku)", ""),
    ("Scene", "Tamil Nadu"),
])
def test_tamil_nadu_oder_beilaeufige_nennung_ist_keine_tamil_fassung(titel, sprache):
    assert not kp.ist_tamil_fassung(titel, sprache)


def test_beschreibung_mit_tamil_nadu_macht_telugu_film_nicht_tamilisch(monkeypatch, settings):
    """Gegenprobe zur Prüfung 11.11.: Die Beschreibung nennt „Tamil Nadu“ und „Tamil-Fassung“, die Vorstellung ist
    Telugu → kein Treffer (früher reichte „Tamil“ irgendwo im Eintragstext)."""
    _seite(monkeypatch, (FIX / "babylon_telugu_tamil_nadu.html").read_bytes())
    assert kp.fetch_html_kino(_quelle(settings, BABYLON), settings, now=STAND) == []


def test_babylon_tamilische_fassung_kommt_ueber_die_sprachangabe(monkeypatch, settings):
    seite = (FIX / "babylon_indogerman.html").read_bytes().replace(b"\\[Telugu\\]", b"\\[Tamil\\]")
    _seite(monkeypatch, seite)
    shows = kp.fetch_html_kino(_quelle(settings, BABYLON), settings, now=STAND)
    assert [(s.kino, s.stadt) for s in shows] == [("Babylon", "Berlin")]
    assert shows[0].start == datetime(2026, 11, 21, 13, 0, tzinfo=kp.TZ)
