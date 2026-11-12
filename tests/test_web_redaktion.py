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
    from stand_hilfe import stand_aus

    client.post("/entwurf/1/status", data={"aktion": "freigeben", "_csrf": token, "stand": stand_aus(html)})
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
    assert "33 von 42 Quellen aktiv" in quellen and "verboten" in quellen
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


# ---- Review 2: Login, Sitzungen, Weiterleitung ------------------------------------------------------------------

def _store(app):
    return Store(app.extensions["settings"].db_path)


def test_env_login_needs_a_password_and_app_refuses_to_start_without(app, tmp_path):
    from news_radar.web import check_login

    settings = app.extensions["settings"]
    settings.web_password = ""
    assert check_login(settings, "luis", "") is None
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": "luis", "password": "", "_csrf": token}).status_code == 200
    settings.web_password = "kurz"
    with pytest.raises(RuntimeError, match="WEB_PASSWORD"):
        create_app(settings)
    settings.web_password = "lang-genug-123"
    assert create_app(settings) is not None


def test_locked_or_demoted_user_loses_access_at_once(app):
    with _store(app) as store:
        repo.nutzer_anlegen(store, "anna", "anna-passwort-1", "admin")
    client = app.test_client()
    login(client, "anna", "anna-passwort-1")
    assert client.get("/nutzer").status_code == 200
    with _store(app) as store:  # Rolle direkt in der Tabelle geändert: gilt beim nächsten Klick
        store._write("UPDATE users SET rolle = 'redaktion' WHERE name = 'anna'")
    assert client.get("/nutzer").status_code == 403
    with _store(app) as store:
        repo.nutzer_sperren(store, "anna")
    resp = client.get("/")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]
    with client.session_transaction() as s:
        assert "user" not in s


def test_logout_revokes_a_copied_cookie_and_new_password_ends_sessions(app):
    client = app.test_client()
    token = login(client)
    kopie = app.test_client()
    kopie.set_cookie("session", client.get_cookie("session").value)
    assert kopie.get("/").status_code == 200
    client.post("/logout", data={"_csrf": token})
    assert kopie.get("/").status_code == 302

    with _store(app) as store:
        repo.nutzer_anlegen(store, "priya", "priya-passwort-1")
    c2 = app.test_client()
    login(c2, "priya", "priya-passwort-1")
    with _store(app) as store:
        repo.nutzer_anlegen(store, "priya", "neues-passwort-22")  # Passwort neu gesetzt
    assert c2.get("/").status_code == 302


def test_cookie_without_server_session_is_not_enough(app):
    client = app.test_client()
    with client.session_transaction() as s:  # wie ein Cookie aus der Zeit vor den Sitzungen
        s["user"], s["rolle"] = "luis", "admin"
    assert client.get("/nutzer").status_code == 302


@pytest.mark.parametrize("ziel, erwartet", [("//evil.example/phish", "/"), ("https://evil.example", "/"),
                                            ("/\\evil.example", "/"), ("/entwurf/1", "/entwurf/1")])
def test_login_redirect_stays_on_this_host(app, ziel, erwartet):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    resp = client.post("/login", query_string={"next": ziel}, data={"user": "luis", "password": "geheim", "_csrf": token})
    assert resp.status_code == 302 and resp.headers["Location"] == erwartet


def test_login_rate_limit_csrf_unicode_and_constant_work(app, monkeypatch):
    import werkzeug.security

    client = app.test_client()
    assert client.post("/login", data={"user": "luis", "password": "geheim"}).status_code == 400  # ohne CSRF-Token
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    resp = client.post("/login", data={"user": "läuft", "password": "pässwört", "_csrf": token})
    assert resp.status_code == 200  # Umlaute: Fehlermeldung statt 500
    resp = client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": "tökén"})
    assert resp.status_code == 400

    aufrufe = []
    echt = werkzeug.security.check_password_hash
    monkeypatch.setattr(werkzeug.security, "check_password_hash", lambda h, p: aufrufe.append(1) or echt(h, p))
    client.post("/login", data={"user": "gibtsnicht", "password": "x", "_csrf": token})
    assert aufrufe, "unbekannte Namen brauchen dieselbe Hash-Prüfung wie echte Konten"

    for _ in range(10):
        client.post("/login", data={"user": "luis", "password": "falsch", "_csrf": token},
                    headers={"CF-Connecting-IP": "203.0.113.9"})
    gesperrt = client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token},
                           headers={"CF-Connecting-IP": "203.0.113.9"})
    assert gesperrt.status_code == 429 and "Zu viele Fehlversuche" in gesperrt.get_data(as_text=True)
    andere_ip = client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token},
                            headers={"CF-Connecting-IP": "198.51.100.4"})
    assert andere_ip.status_code == 302


def test_preview_and_links_are_safe(app):
    client = app.test_client()
    token = login(client)
    with _store(app) as store:
        d = store.get_draft(1)
        store.update_draft(1, inhalt_html='<p>Text</p><img src="x"/onerror="alert(1)"><a href="&#106;avascript:alert(2)">a</a>',
                           ticket_url="javascript:alert(3)", weitere_quellen=[{"name": "W", "url": "javascript:alert(4)"}])
        assert d is not None
    html = client.get("/entwurf/1").get_data(as_text=True)
    assert "onerror" not in html and "javascript:" not in html
    client.post("/entwurf/1", data={"_csrf": token, "titel": "T", "teaser": "T", "kategorie": "events",
                                    "inhalt_html": '<p onclick="x()">a</p><svg/onload=alert(1)>', "ticket_url": "javascript:alert(5)"})
    with _store(app) as store:
        row = store.get_draft(1)
    assert "onclick" not in row["inhalt_html"] and "onload" not in row["inhalt_html"] and row["ticket_url"] == ""


def test_add_source_to_finished_story_is_refused(app):
    client = app.test_client()
    token = login(client)
    with _store(app) as store:
        fertig = repo.stories(store, "fertig")[0]["id"]
    resp = client.post(f"/story/{fertig}/quelle", data={"_csrf": token, "url": "https://www1.wdr.de/x"})
    assert resp.status_code == 409 and "Recherche nötig" in resp.get_data(as_text=True)
    with _store(app) as store:
        assert jobs.offen_fuer_story(store, fertig) == []


# ---- Coolify: Lesezugang und Proxy ---------------------------------------------------------------------------

def test_report_api_needs_token_and_returns_pilot_data(app):
    client = app.test_client()
    assert client.get("/api/bericht").status_code == 404  # ohne RADAR_LESE_TOKEN gibt es den Endpunkt nicht
    app.extensions["settings"].lese_token = "lese-token-mit-genug-zeichen"
    assert client.get("/api/bericht").status_code == 401
    assert client.get("/api/bericht", headers={"Authorization": "Bearer falsch"}).status_code == 401
    assert client.get("/api/bericht", headers={"Authorization": "Bearer tökén"}).status_code == 401
    resp = client.get("/api/bericht?tage=3", headers={"Authorization": "Bearer lese-token-mit-genug-zeichen"})
    data = resp.get_json()
    assert resp.status_code == 200 and data["tage"] == 3
    assert data["entwuerfe"] and data["storys"] and {"budget", "warteschlange", "kosten", "aufrufe"} <= set(data)
    story = next(s for s in data["storys"] if s["dokumente"])
    assert story["claims"] and story["fassungen"] and "kosten" in story
    roh = resp.get_data(as_text=True)
    assert "passwort_hash" not in roh and "lese-token" not in roh and "s3cret" not in roh
    assert client.post("/api/bericht", headers={"Authorization": "Bearer lese-token-mit-genug-zeichen"}).status_code != 200


def test_report_api_accepts_agent_token_too(app):
    """Die tägliche Redaktionsroutine kommt mit RADAR_AGENT_TOKEN allein aus: /api/bericht nimmt Lese- oder Agent-Token."""
    client = app.test_client()
    s = app.extensions["settings"]
    lese, agent = "lese-token-mit-genug-zeichen", "agent-token-mit-genug-zeichen"
    s.lese_token, s.agent_token = "", ""
    assert client.get("/api/bericht", headers={"Authorization": f"Bearer {agent}"}).status_code == 404
    s.agent_token = agent  # nur das Agent-Token gesetzt
    assert client.get("/api/bericht", headers={"Authorization": f"Bearer {agent}"}).status_code == 200
    assert client.get("/api/bericht", headers={"Authorization": f"Bearer {lese}"}).status_code == 401
    assert client.get("/api/bericht", headers={"Authorization": "Bearer "}).status_code == 401
    s.lese_token = lese  # beide gesetzt
    assert client.get("/api/bericht", headers={"Authorization": f"Bearer {agent}"}).status_code == 200
    assert client.get("/api/bericht", headers={"Authorization": f"Bearer {lese}"}).status_code == 200
    assert client.get("/api/bericht", headers={"Authorization": "Bearer falsch"}).status_code == 401
    assert client.get("/api/bericht").status_code == 401
    s.agent_token = ""  # nur das Lese-Token gesetzt
    assert client.get("/api/bericht", headers={"Authorization": f"Bearer {lese}"}).status_code == 200
    assert client.get("/api/bericht", headers={"Authorization": f"Bearer {agent}"}).status_code == 401
    roh = client.get("/api/bericht", headers={"Authorization": f"Bearer {lese}"}).get_data(as_text=True)
    assert agent not in roh and lese not in roh
    # Das Lese-Token öffnet den Agent-Modus nicht
    s.agent_token = agent
    assert client.get("/api/agent/export", headers={"Authorization": f"Bearer {lese}"}).status_code == 401


def test_behind_proxy_rate_limit_uses_real_client_ip(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "NOTIFY_WEBHOOK_URL"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    settings.proxy_hops = 1
    client = create_app(settings, testing=True).test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    for _ in range(10):
        client.post("/login", data={"user": "luis", "password": "falsch", "_csrf": token},
                    headers={"X-Forwarded-For": "203.0.113.7"})
    angreifer = client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token},
                            headers={"X-Forwarded-For": "203.0.113.7"})
    redaktion = client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token},
                            headers={"X-Forwarded-For": "198.51.100.20", "X-Forwarded-Proto": "https"})
    assert angreifer.status_code == 429 and redaktion.status_code == 302


def test_agent_api_export_and_import_need_their_own_token(app, monkeypatch):
    from news_radar.agents import research

    monkeypatch.setattr(research, "belege_sammeln", lambda ctx, story: [])  # kein Netz im Test
    client = app.test_client()
    assert client.get("/api/agent/export").status_code == 404  # ohne RADAR_AGENT_TOKEN aus
    settings = app.extensions["settings"]
    settings.agent_token, settings.lese_token = "agent-token-mit-genug-zeichen", "lese-token-mit-genug-zeichen"
    agent = {"Authorization": "Bearer agent-token-mit-genug-zeichen"}
    assert client.get("/api/agent/export", headers={"Authorization": "Bearer lese-token-mit-genug-zeichen"}).status_code == 401
    resp = client.get("/api/agent/export?limit=3", headers=agent)
    data = resp.get_json()
    assert resp.status_code == 200 and data["version"] == 2 and "regeln_recherche" in data
    sid = next(p["story_id"] for p in data["storys"] if p["titel"] == "Kaputte Story")
    with _store(app) as store:
        fertig = repo.stories(store, "fertig")[0]["id"]
    abgelehnt = client.post("/api/agent/import", json={"ergebnisse": [{"story_id": fertig, "verwerfen": "alt"}]},
                            headers=agent).get_json()
    ok = client.post("/api/agent/import?von=test", json={"ergebnisse": [{"story_id": sid, "verwerfen": "Test"}]},
                     headers=agent).get_json()
    assert abgelehnt["verworfen"] == 0 and "nicht aus dem Export" in abgelehnt["fehler"][0]
    assert ok["verworfen"] == 1
    with _store(app) as store:
        assert repo.story(store, fertig)["status"] == "fertig" and repo.story(store, sid)["status"] == "verworfen"
    assert client.post("/api/agent/import", data="kein json", headers=agent, content_type="text/plain").status_code == 400
    assert client.post("/api/agent/import", json={"ergebnisse": None}, headers=agent).status_code == 400
    assert client.post("/api/agent/import", json={"ergebnisse": []}).status_code == 401


def _offene_ids(app):
    from news_radar.agent_v2 import fuer_agent_offen

    with _store(app) as store:
        alle = [s["id"] for s in repo.stories(store)]
        return [i for i in alle if fuer_agent_offen(store, i)], [i for i in alle if not fuer_agent_offen(store, i)]


def _agent_client(app):
    app.extensions["settings"].agent_token = "agent-token-mit-genug-zeichen"
    return app.test_client(), {"Authorization": "Bearer agent-token-mit-genug-zeichen"}


def test_agent_export_mit_ids_liefert_genau_die_offenen_in_dieser_reihenfolge(app, monkeypatch):
    from news_radar.agents import research

    monkeypatch.setattr(research, "belege_sammeln", lambda ctx, story: [])  # kein Netz im Test
    client, agent = _agent_client(app)
    with _store(app) as store:  # eine zweite offene Story, damit die Reihenfolge prüfbar ist
        jobs.einreihen(store, repo.story_anlegen(store, typ="news", titel="Zweite offene Story"), "recherche")
    offen, zu = _offene_ids(app)
    assert len(offen) >= 2 and zu, (offen, zu)
    auswahl = [offen[-1], zu[0], 99999, offen[0], offen[-1]]  # fertige und fremde fallen heraus, doppelte einmal
    resp = client.get("/api/agent/export?ids=" + ",".join(map(str, auswahl)), headers=agent)
    assert resp.status_code == 200
    assert [p["story_id"] for p in resp.get_json()["storys"]] == [offen[-1], offen[0]]
    ohne = client.get("/api/agent/export?limit=1", headers=agent).get_json()  # ohne Parameter wie bisher
    assert len(ohne["storys"]) == 1 and "regeln_recherche" in ohne


@pytest.mark.parametrize("wert", ["abc", "", "1,,2", "1;2", "-3", "١٢", "1 ,2", "1234567890",
                                  ",".join(str(i) for i in range(1, 22))])
def test_agent_export_ungueltige_ids_400(app, monkeypatch, wert):
    from news_radar.agents import research

    monkeypatch.setattr(research, "belege_sammeln", lambda ctx, story: pytest.fail("kein Abruf bei 400"))
    client, agent = _agent_client(app)
    resp = client.get("/api/agent/export", query_string={"ids": wert}, headers=agent)
    assert resp.status_code == 400 and resp.get_json()["fehler"]


def test_agent_export_uebersicht_ohne_dokumente_und_ohne_abruf(app, monkeypatch):
    from news_radar import schalter
    from news_radar.agents import research

    monkeypatch.setattr(research, "belege_sammeln", lambda ctx, story: pytest.fail("Übersicht ruft nichts ab"))
    client, agent = _agent_client(app)
    offen, _ = _offene_ids(app)
    data = client.get("/api/agent/export?nur=uebersicht", headers=agent).get_json()
    assert sorted(s["story_id"] for s in data["storys"]) == sorted(offen)
    assert set(data["storys"][0]) == {"story_id", "typ", "herkunft", "titel", "kategorie", "ereignis_datum", "erstellt"}
    assert "dokumente" not in data["storys"][0] and "regeln_recherche" not in data
    assert client.get("/api/agent/export?nur=alles", headers=agent).status_code == 400
    with _store(app) as store:
        schalter.setzen(store, "redaktion", True, wer="test", grund="Test")
    assert client.get("/api/agent/export?nur=uebersicht", headers=agent).status_code == 409


def test_cli_agent_export_mit_ids(app, monkeypatch, tmp_path):
    import json

    from news_radar.__main__ import main
    from news_radar.agents import research

    monkeypatch.setattr(research, "belege_sammeln", lambda ctx, story: [])
    monkeypatch.setenv("RADAR_DATA_DIR", str(app.extensions["settings"].data_dir))
    offen, zu = _offene_ids(app)
    mappe = tmp_path / "mappe.json"
    assert main(["agent", "export", "--v2", "--file", str(mappe), "--ids", f"{zu[0]},{offen[0]}"]) == 0
    assert [p["story_id"] for p in json.loads(mappe.read_text(encoding="utf-8"))["storys"]] == [offen[0]]
    assert main(["agent", "export", "--v2", "--file", str(mappe), "--ids", "abc"]) == 2
