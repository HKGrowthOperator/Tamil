"""Cockpit v2: Belege im Entwurf, Recherche nötig, Kosten, Quellen, Warteschlange, Benutzer und Rollen, Audit-Spur."""

from datetime import datetime, timedelta, timezone

import pytest

from news_radar import sources
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.web import create_app
from news_radar.workflow import jobs, orchestrator, repo
from news_radar.workflow.fake import FakeAnthropic

ARTIKEL = ("Die tamilische Gemeinde in Hamm feiert am Samstag, 14. November, ihr Lichterfest im Tempel. "
           "Erwartet werden rund 3000 Besucherinnen und Besucher aus ganz Deutschland. "
           "Die Feier beginnt um 10 Uhr mit einer Prozession, der Eintritt ist frei. "
           "Veranstalter ist der Tempelverein, der seit 2002 in Hamm aktiv ist und jedes Jahr zum Fest einlädt.")


@pytest.fixture
def app(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    now = datetime.now(timezone.utc)
    gut = sources.NewsItem(title="Tamilisches Lichterfest im Tempel Hamm", url="https://www.ruhrnachrichten.de/l",
                           summary="Fest", source="Ruhr Nachrichten", published=now - timedelta(hours=1))
    nur_titel = sources.NewsItem(title="Tamilischer Verein in Köln gewinnt Preis - WDR", summary="Preis",
                                 url="https://news.google.com/rss/articles/x", source="Google News DACH · WDR",
                                 published=now - timedelta(hours=2))
    with Store(settings.db_path) as store:
        ctx = orchestrator.kontext(settings, store, client=FakeAnthropic(), fetch_text=lambda u: ARTIKEL, suche=lambda q: [])
        orchestrator.scan(ctx, [gut, nur_titel])
        orchestrator.abarbeiten(ctx)
        sid = repo.story_anlegen(store, typ="news", titel="Kaputte Story")
        jid = jobs.einreihen(store, sid, "recherche")
        store.db.execute("UPDATE workflow_jobs SET status = 'tot', fehler = 'Timeout' WHERE id = ?", (jid,))
        store.db.commit()
    return create_app(settings, testing=True)


def login(client, user="luis", password="geheim"):
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    resp = client.post("/login", data={"user": user, "password": password, "_csrf": token})
    assert resp.status_code == 302, resp.get_data(as_text=True)[:300]
    return token


def test_draft_shows_evidence_costs_license_and_approval_is_audited(app):
    client = app.test_client()
    token = login(client)
    html = client.get("/entwurf/1").get_data(as_text=True)
    assert "Belege" in html and "Faktenmatrix" in html and "Primärquelle" in html and "Faktencheck" in html
    assert "Kosten und Rechte" in html and "Lizenz: eigene Grafik" in html and "Als Dossier recherchieren" in html
    client.post("/entwurf/1/status", data={"aktion": "freigeben", "_csrf": token})
    with Store(app.extensions["settings"].db_path) as store:
        aktion = repo.aktionen(store, 1)[-1]
        row = store.get_draft(1)
    assert aktion["wer"] == "luis" and aktion["aktion"] == "freigeben" and aktion["fassung_hash"] == repo.fassung_hash(row)


def test_research_needed_page_add_source_blocks_internal_urls(app):
    client = app.test_client()
    token = login(client)
    html = client.get("/recherche").get_data(as_text=True)
    assert "Tamilischer Verein in Köln" in html and "Quelle ergänzen" in html
    with Store(app.extensions["settings"].db_path) as store:
        sid = repo.stories(store, "recherche_erforderlich")[0]["id"]
    resp = client.post(f"/story/{sid}/quelle", data={"url": "http://127.0.0.1:8787/", "_csrf": token}, follow_redirects=True)
    assert "geht nicht" in resp.get_data(as_text=True)
    client.post(f"/story/{sid}/quelle", data={"url": "https://www1.wdr.de/preis", "_csrf": token})
    with Store(app.extensions["settings"].db_path) as store:
        assert repo.story(store, sid)["status"] == "neu" and jobs.offen_fuer_story(store, sid)


def test_costs_sources_queue_pages_and_csv(app):
    client = app.test_client()
    token = login(client)
    kosten = client.get("/kosten").get_data(as_text=True)
    assert "Nach Rolle" in kosten and "recherche" in kosten and "je Entwurf" in kosten
    csv = client.get("/kosten.csv")
    assert csv.mimetype == "text/csv" and "kosten_usd" in csv.get_data(as_text=True)
    quellen = client.get("/quellen").get_data(as_text=True)
    assert "20 von 28 Quellen aktiv" in quellen and "verboten" in quellen
    schlange = client.get("/warteschlange?status=tot").get_data(as_text=True)
    assert "Kaputte Story" in schlange and "Erneut" in schlange
    resp = client.post("/job/9999/erneut", data={"_csrf": token}, follow_redirects=True)
    assert "kann nicht" in resp.get_data(as_text=True)
    gesund = client.get("/gesund").json
    assert gesund["warteschlange"]["tot"] == 1 and "budget" in gesund


def test_users_roles_and_admin_only_pages(app):
    client = app.test_client()
    token = login(client)
    resp = client.post("/nutzer", data={"name": "priya", "passwort": "sehr-geheim-1", "rolle": "redaktion", "_csrf": token},
                       follow_redirects=True)
    assert "priya angelegt" in resp.get_data(as_text=True)
    zu_kurz = client.post("/nutzer", data={"name": "x1", "passwort": "kurz", "_csrf": token}, follow_redirects=True)
    assert "mindestens 10" in zu_kurz.get_data(as_text=True)
    andere = app.test_client()
    login(andere, "priya", "sehr-geheim-1")
    assert andere.get("/nutzer").status_code == 403
    assert andere.get("/kosten").status_code == 200
    assert "Benutzer" not in andere.get("/").get_data(as_text=True).split("<main")[0]


def test_budget_banner_when_stopped(app):
    settings = app.extensions["settings"]
    settings.budget_tag_usd = 0.0001
    client = app.test_client()
    login(client)
    assert "Budget erreicht" in client.get("/").get_data(as_text=True)


def test_approved_version_hash_matches_queued_draft(app):
    with Store(app.extensions["settings"].db_path) as store:
        row = store.get_draft(1)
        entwurf = [v for v in repo.fassungen(store, draft_id=1) if v["rolle"] == "entwurf"][-1]
    assert entwurf["hash"] == repo.fassung_hash(row)
