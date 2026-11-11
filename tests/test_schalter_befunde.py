"""Befunde der Code-Prüfung zum Stopp-Schalter, zu Rollen und /gesund – je Befund ein Test."""

from stand_hilfe import stand_von

import json

import pytest

from news_radar import publisher, schalter, sources
from news_radar.agents import Kontext, cluster, media, relevance, research
from news_radar.config import Source, load_settings
from news_radar.store import Store
from news_radar.workflow import orchestrator, providers, repo
from news_radar.workflow.fake import FakeAnthropic

from test_schalter import FakeWP, entwurf


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    s.web_user, s.web_password, s.web_secret = "luis", "geheim", "s3cret"
    s.agent_token, s.lese_token = "agent-token", "lese-token"
    return s


def _client(settings, user="luis", pw="geheim"):
    from news_radar.web import create_app

    app = create_app(settings, testing=True)
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": user, "password": pw, "_csrf": token}).status_code == 302
    return app, client, token


# ---- 1 (P1): „In WordPress bearbeiten“ im Stopp gibt nicht frei ----------------------------------------

def test_wp_entwurf_im_stopp_bleibt_unveraendert_und_geht_nie_live(settings):
    with Store(settings.db_path) as st:
        did = entwurf(st, freigeben=False)
        schalter.setzen(st, "website", True, wer="anna", grund="Theme-Umbau")
    app, client, token = _client(settings)
    wp = app.extensions["wordpress"] = FakeWP()
    text = client.post(f"/entwurf/{did}/wp-entwurf", data={"_csrf": token, "stand": stand_von(client, did)}, follow_redirects=True).get_data(as_text=True)
    assert "kein WordPress-Entwurf angelegt" in text
    with Store(settings.db_path) as st:
        assert st.get_draft(did)["status"] == "neu" and repo.aktionen(st, did) == []
        schalter.setzen(st, "website", False, wer="anna")
        assert publisher.publish_approved(settings, st, wp=wp) == [] and wp.posts == []


# ---- 2 (P1): Agent-Modus im Stopp ---------------------------------------------------------------------

def test_agent_api_und_cli_im_stopp_abgewiesen(settings, monkeypatch, tmp_path):
    def kein_abruf(*a, **kw):
        raise AssertionError("im Stopp nichts abrufen")

    monkeypatch.setattr(sources, "fetch_article_text", kein_abruf)
    with Store(settings.db_path) as st:
        sid = repo.story_anlegen(st, typ="news", titel="Lichterfest")
        schalter.setzen(st, "redaktion", True, wer="anna", grund="Kosten prüfen")
    from news_radar.web import create_app

    client = create_app(settings, testing=True).test_client()
    kopf = {"Authorization": "Bearer agent-token"}
    resp = client.get("/api/agent/export", headers=kopf)
    assert resp.status_code == 409 and resp.get_json()["kanal"] == "redaktion" and "Kosten prüfen" in resp.get_json()["fehler"]
    resp = client.post("/api/agent/import", headers=kopf, json={"ergebnisse": [{"story_id": sid, "claims": [], "beitrag": {}}]})
    assert resp.status_code == 409
    with Store(settings.db_path) as st:
        assert st.list_drafts() == [] and repo.story(st, sid)["status"] == "neu"
    from news_radar.__main__ import main

    monkeypatch.setenv("RADAR_DATA_DIR", str(settings.data_dir))
    mappe = tmp_path / "mappe.json"
    assert main(["agent", "export", "--v2", "--file", str(mappe)]) == 3 and not mappe.exists()
    (tmp_path / "e.json").write_text(json.dumps({"ergebnisse": []}), encoding="utf-8")
    assert main(["agent", "import", "--v2", "--file", str(tmp_path / "e.json")]) == 3


# ---- 3 (P2): Bild- und Seitenabrufe in laufenden Jobs -----------------------------------------------------

def test_bild_und_seitenabrufe_pruefen_den_schalter(settings, monkeypatch):
    abrufe = []
    monkeypatch.setattr("news_radar.net.safe_get", lambda *a, **kw: abrufe.append(a) or (_ for _ in ()).throw(AssertionError))
    with Store(settings.db_path) as st:
        ctx = Kontext(settings=settings, store=st, fetch_text=lambda u: abrufe.append(u) or "",
                      suche=lambda q: abrufe.append(q) or [])
        sid = repo.story_anlegen(st, typ="news", titel="Lichterfest")
        repo.dokument_hinzufuegen(st, sid, url="https://www.wdr.de/x", publisher="WDR", art="zusammenfassung", titel="x",
                                  text="kurz")
        schalter.setzen(st, "redaktion", True, wer="anna", grund="Test")
        settings.bild_reihenfolge = ("quelle", "karte")
        with pytest.raises(schalter.Gestoppt):  # kein stilles Ausweichen auf die Bildkarte
            media.besorgen(ctx, repo.story(st, sid), {"titel": "Lichterfest", "kategorie": "news"}, "slug",
                           kategorie_label="News", quelle=Source(name="Q", type="rss", bild_nutzen=True),
                           quelle_bild="https://q.example/bild.jpg")
        with pytest.raises(schalter.Gestoppt):
            research.belege_sammeln(ctx, repo.story(st, sid))
        with pytest.raises(schalter.Gestoppt):
            ctx.text_von("https://www.wdr.de/x")
    assert abrufe == []


# ---- 4 (P2): laufender Scan bricht ohne doppelte oder halbe Storys ab -------------------------------------

def _item(titel="Tamilisches Lichterfest im Tempel Hamm"):
    from datetime import datetime, timedelta, timezone

    return sources.NewsItem(title=titel, url="https://www.ruhrnachrichten.de/l", summary="Tamilen in Hamm",
                            source="Ruhr Nachrichten", published=datetime.now(timezone.utc) - timedelta(hours=1))


def test_cluster_und_signal_reichen_gestoppt_durch(settings):
    with Store(settings.db_path) as st:
        claude = providers.Claude(settings, st, client=FakeAnthropic())
        ctx = Kontext(settings=settings, store=st, claude=claude)
        schalter.setzen(st, "redaktion", True, wer="anna", grund="Test")
        with pytest.raises(schalter.Gestoppt):
            cluster._grenzfaelle_entscheiden(ctx, [(0, _item(), {"id": 1, "titel": "Lichterfest Hamm"})], [None])
        with pytest.raises(schalter.Gestoppt):
            relevance.pruefen(ctx, [_item()])


@pytest.mark.parametrize("wann", ["im_cluster", "nach_cluster"])
def test_scan_bricht_sauber_ab(settings, monkeypatch, wann):
    echt = cluster.zuordnen

    def zuordnen(ctx, picked):
        schalter.setzen(ctx.store, "redaktion", True, wer="anna", grund="mitten im Scan")
        if wann == "im_cluster":
            raise schalter.Gestoppt("redaktion", schalter.sperre(ctx.store, "redaktion"))
        return echt(ctx, picked)

    monkeypatch.setattr(cluster, "zuordnen", zuordnen)
    with Store(settings.db_path) as st:
        ctx = orchestrator.kontext(settings, st, client=FakeAnthropic(), fetch_text=lambda u: "", suche=lambda q: [])
        item = _item()
        assert orchestrator.scan(ctx, [item])["angehalten"] == 1
        assert repo.stories(st) == [] and item.uid not in st.seen_uids()


# ---- 5 (P2): „fehler“ im Website-Stopp wartet wirklich; Abgelehntes wird nicht behauptet ----------------

def test_fehler_wartet_wirklich_und_abgelehnt_ehrlich(settings):
    with Store(settings.db_path) as st:
        fehler = entwurf(st, "u1", "Erster")
        st.claim_draft(fehler, von="dienst")
        st.mark_publish_failed(fehler, "Timeout")
        abgelehnt = entwurf(st, "u2", "Zweiter", freigeben=False)
        st.set_status(abgelehnt, "ablehnen", von="anna")
        schalter.setzen(st, "website", True, wer="anna", grund="Theme-Umbau")
    app, client, token = _client(settings)
    app.extensions["wordpress"] = FakeWP()
    text = client.post(f"/entwurf/{fehler}/veroeffentlichen", data={"_csrf": token, "stand": stand_von(client, fehler)}, follow_redirects=True).get_data(as_text=True)
    assert "freigegeben und wartet" in text
    text = client.post(f"/entwurf/{abgelehnt}/veroeffentlichen", data={"_csrf": token, "stand": stand_von(client, abgelehnt)}, follow_redirects=True).get_data(as_text=True)
    assert "wartet nicht" in text
    with Store(settings.db_path) as st:
        assert st.get_draft(fehler)["status"] == "freigegeben" and st.get_draft(abgelehnt)["status"] == "abgelehnt"
        assert [a["aktion"] for a in repo.aktionen(st, fehler)][-2:] == ["erneut", "zurueckgehalten"]
        assert repo.aktionen(st, abgelehnt) == []


# ---- 6 (P2): der letzte Admin sperrt sich nicht aus ---------------------------------------------------------

def test_letzter_admin_bleibt(settings, monkeypatch):
    with Store(settings.db_path) as st:
        repo.nutzer_anlegen(st, "anna", "anna-passwort-1", "admin")
        repo.nutzer_anlegen(st, "priya", "priya-passwort-1", "redaktion")
        with pytest.raises(ValueError, match="letzte aktive Admin"):
            repo.nutzer_sperren(st, "anna")
        with pytest.raises(ValueError, match="letzte aktive Admin"):
            repo.nutzer_anlegen(st, "anna", "anna-passwort-2", "redaktion")
        repo.nutzer_anlegen(st, "ben", "ben-passwort-1", "admin")
    app, client, token = _client(settings, "anna", "anna-passwort-1")
    text = client.post("/nutzer", data={"_csrf": token, "aktion": "sperren", "name": "anna"},
                       follow_redirects=True).get_data(as_text=True)
    assert "Sich selbst" in text
    client.post("/nutzer", data={"_csrf": token, "aktion": "anlegen", "name": "anna", "passwort": "anna-passwort-1",
                                 "rolle": "leser"})
    with Store(settings.db_path) as st:
        assert {n["name"]: (n["rolle"], n["aktiv"]) for n in repo.nutzer_liste(st)}["anna"] == ("admin", 1)
        repo.nutzer_sperren(st, "ben")  # es gibt noch anna
    from news_radar.__main__ import main

    monkeypatch.setenv("RADAR_DATA_DIR", str(settings.data_dir))
    with pytest.raises(SystemExit, match="letzte aktive Admin"):
        main(["nutzer", "sperren", "anna"])


# ---- 8 (P3): /gesund verrät keine Kanäle, /api/bericht nennt sie --------------------------------------------

def test_kanaele_nur_im_geschuetzten_bericht(settings):
    from news_radar.web import create_app

    with Store(settings.db_path) as st:
        schalter.setzen(st, "instagram", True, wer="anna", grund="Regel unklar")
    client = create_app(settings, testing=True).test_client()
    gesund = client.get("/gesund").get_json()
    assert gesund["gestoppt"] is True and gesund["gestoppt_kanaele"] == 1 and "instagram" not in json.dumps(gesund)
    bericht = client.get("/api/bericht", headers={"Authorization": "Bearer lese-token"}).get_json()
    assert [g["kanal"] for g in bericht["gestoppt"]] == ["instagram"] and bericht["gestoppt"][0]["seit"]


# ---- Oberfläche B, C, D, G, H ------------------------------------------------------------------------------

def test_oberflaeche_sammelbanner_status_protokoll_403_fehlermeldung(settings):
    with Store(settings.db_path) as st:
        repo.nutzer_anlegen(st, "lena", "lena-passwort-1", "leser")
    app, client, token = _client(settings)
    text = client.post("/schalter/website/an", data={"_csrf": token, "grund": " "}, follow_redirects=True).get_data(as_text=True)
    assert 'role="alert"' in text and "Nicht angehalten" in text and 'class="banner stopp"' not in text  # H
    assert "Radar läuft" in text
    for kanal, grund in (("website", "Theme-Umbau"), ("instagram", "Regel"), ("facebook", "Regel"), ("redaktion", "Kosten")):
        client.post(f"/schalter/{kanal}/an", data={"_csrf": token, "grund": grund})
    client.post("/schalter/website/aus", data={"_csrf": token})
    client.post("/schalter/website/an", data={"_csrf": token, "grund": "Theme-Umbau"})
    text = client.get("/protokoll").get_data(as_text=True)
    assert text.count('class="banner stopp"') == 1 and 'role="status"' in text  # B
    assert text.count("Bearbeiten und Freigeben von Hand gehen weiter") == 1
    assert "Radar angehalten" in text and "Radar läuft" not in text  # C
    assert "Website angehalten: Theme-Umbau" in text and "Website wieder eingeschaltet" in text  # D
    assert "False" not in text and "True" not in text
    _, lena, _ = _client(settings, "lena", "lena-passwort-1")
    text = lena.get("/nutzer").get_data(as_text=True)
    assert "Benutzer verwalten" in text and "(benutzer)" not in text  # G
