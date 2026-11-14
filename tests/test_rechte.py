"""Rollen und Rechte im Cockpit (Vertrag B1.1, Festlegung F0 Punkt 8, Test T7): admin, redaktion, leser.

Jede ändernde Route (POST) verlangt ein Recht aus der Karte; `leser` bekommt überall 403 mit verständlicher Seite.
Ein Test schlägt fehl, sobald eine neue POST-Route ohne Recht dazukommt."""

import pytest

from news_radar import schalter
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.web import PUBLIC_ENDPOINTS, create_app, rechte
from news_radar.workflow import jobs, repo

NUTZER = {"anna": ("anna-passwort-1", "admin"), "priya": ("priya-passwort-1", "redaktion"),
          "lena": ("lena-passwort-1", "leser")}


@pytest.fixture
def app(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    settings = load_settings()
    settings.data_dir = tmp_path
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    with Store(settings.db_path) as store:
        for name, (pw, rolle) in NUTZER.items():
            repo.nutzer_anlegen(store, name, pw, rolle)
        for i in (1, 2):
            store.insert_draft(dict(uid=f"u{i}", typ="artikel", titel=f"Beitrag {i}", teaser="T", inhalt_html="<p>x</p>",
                                    kategorie="news", relevanz=8, dach_bezug=True, ort="Hamm", schlagworte=["x"],
                                    original_json={"titel": f"Beitrag {i}", "inhalt_html": "<p>x</p>"}))
        sid = repo.story_anlegen(store, typ="news", titel="Story")
        repo.story_setzen(store, sid, status="recherche_erforderlich")
        jid = jobs.einreihen(store, sid, "recherche")
        store.db.execute("UPDATE workflow_jobs SET status = 'tot' WHERE id = ?", (jid,))
        store.db.commit()
    return create_app(settings, testing=True)


def login(app, user):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    pw = "geheim" if user == "luis" else NUTZER[user][0]
    assert client.post("/login", data={"user": user, "password": pw, "_csrf": token}).status_code == 302
    return client, token


def _post_routen(app):
    out = []
    for rule in app.url_map.iter_rules():
        if "POST" not in rule.methods or rule.endpoint in PUBLIC_ENDPOINTS:
            continue
        werte = {a: (1 if type(rule._converters[a]).__name__ == "IntegerConverter" else "website") for a in rule.arguments}
        out.append((rule, werte))
    return out


def test_karte_ist_vollstaendig_und_nur_mit_bekannten_rollen():
    assert rechte.ROLLEN == ("admin", "redaktion", "leser")
    for recht, rollen in rechte.RECHTE.items():
        assert rollen and set(rollen) <= set(rechte.ROLLEN), recht
        assert "admin" in rollen, f"admin darf alles: {recht}"
    assert {r for r, rollen in rechte.RECHTE.items() if "leser" in rollen} == {"abmelden"}
    assert rechte.RECHTE["alles_einschalten"] == ("admin",)
    assert set(rechte.RECHTE["anhalten"]) == set(rechte.RECHTE["kanal_einschalten"]) == {"admin", "redaktion"}


def test_jede_post_route_verlangt_ein_recht(app):
    """Kommt eine neue POST-Route ohne `@recht_noetig` dazu, schlägt dieser Test fehl."""
    routen = _post_routen(app)
    assert len(routen) >= 15
    ohne = [r.rule for r, _ in routen if getattr(app.view_functions[r.endpoint], "recht", None) not in rechte.RECHTE]
    assert not ohne, f"POST-Routen ohne Recht: {ohne}"


def test_leser_bekommt_bei_jeder_aendernden_route_403(app):
    client, token = login(app, "lena")
    geprueft = 0
    for rule, werte in _post_routen(app):
        recht = app.view_functions[rule.endpoint].recht
        if "leser" in rechte.RECHTE[recht]:
            continue
        with app.test_request_context():
            from flask import url_for
            url = url_for(rule.endpoint, **werte)
        resp = client.post(url, data={"_csrf": token, "aktion": "freigeben", "grund": "x", "name": "neu",
                                      "passwort": "langes-passwort", "url": "https://www.wdr.de/x", "rolle": "admin"})
        assert resp.status_code == 403, f"{rule.rule}: {resp.status_code}"
        assert "Keine Berechtigung" in resp.get_data(as_text=True)
        geprueft += 1
    assert geprueft >= 14  # alle ändernden Routen außer Abmelden
    with Store(app.extensions["settings"].db_path) as store:
        assert store.get_draft(1)["status"] == "neu" and not schalter.gestoppt(store, "website")
        assert repo.aktionen_liste(store) == [] and len(repo.nutzer_liste(store)) == 3


def test_leser_sieht_alles_ohne_knoepfe(app):
    client, _ = login(app, "lena")
    for seite in ("/", "/entwurf/1", "/recherche", "/dashboard", "/kosten", "/quellen", "/warteschlange?status=tot",
                  "/protokoll", "/schalter", "/zeitplan", "/vorschau/1"):
        assert client.get(seite).status_code == 200, seite
    feed = client.get("/").get_data(as_text=True)
    assert "Beitrag 1" in feed and "Freigeben" not in feed and "Ablehnen" not in feed
    entwurf = client.get("/entwurf/1").get_data(as_text=True)
    assert 'id="editor"' not in entwurf and "Neu schreiben" not in entwurf and "Freigeben" not in entwurf
    assert "Quelle ergänzen" not in client.get("/recherche").get_data(as_text=True)
    assert "Erneut" not in client.get("/warteschlange?status=tot").get_data(as_text=True)
    assert "Anhalten" not in client.get("/schalter").get_data(as_text=True)
    assert client.get("/nutzer").status_code == 403
    for export in ("/protokoll.jsonl", "/protokoll/aktionen.jsonl", "/kosten.csv"):
        assert client.get(export).status_code == 403, export
    assert client.post("/logout", data={"_csrf": _token(client)}).status_code == 302


def _token(client):
    with client.session_transaction() as s:
        return s["csrf"]


def test_redaktion_haelt_alles_an_schaltet_aber_nur_einzelne_kanaele_ein(app):
    priya, token = login(app, "priya")
    assert priya.post("/schalter/alles/an", data={"_csrf": token, "grund": "Notfall"}).status_code == 302
    assert priya.post("/schalter/website/an", data={"_csrf": token, "grund": "Theme"}).status_code == 302
    assert priya.post("/schalter/alles/aus", data={"_csrf": token}).status_code == 403
    assert priya.post("/schalter/website/aus", data={"_csrf": token}).status_code == 302
    anna, token_a = login(app, "anna")
    assert anna.post("/schalter/alles/aus", data={"_csrf": token_a}).status_code == 302
    with Store(app.extensions["settings"].db_path) as store:
        assert not schalter.gestoppt(store, "instagram")
        assert [z["wer"] for z in repo.aktionen_liste(store, aktion="schalter_aus")] == ["anna", "priya"]


def test_redaktion_darf_weder_benutzer_noch_erneut_noch_export(app):
    priya, token = login(app, "priya")
    assert priya.get("/nutzer").status_code == 403
    assert priya.post("/nutzer", data={"_csrf": token, "name": "x", "passwort": "langes-passwort"}).status_code == 403
    assert priya.post("/job/1/erneut", data={"_csrf": token}).status_code == 403
    assert priya.get("/protokoll.jsonl").status_code == 403
    from stand_hilfe import stand_aus

    stand = stand_aus(priya.get("/entwurf/1").get_data(as_text=True))
    assert priya.post("/entwurf/1/status", data={"_csrf": token, "aktion": "freigeben", "stand": stand}).status_code == 302
    assert "Benutzer" not in priya.get("/").get_data(as_text=True).split("<main")[0]


def test_admin_und_notzugang_duerfen_alles(app):
    for user in ("anna", "luis"):
        client, token = login(app, user)
        assert client.get("/nutzer").status_code == 200
        assert client.get("/protokoll.jsonl").status_code == 200
        assert client.post("/job/1/erneut", data={"_csrf": token}).status_code == 302


def test_karte_ist_mit_einer_zeile_aenderbar(app, monkeypatch):
    monkeypatch.setitem(rechte.RECHTE, "anhalten", ("admin",))
    priya, token = login(app, "priya")
    assert priya.post("/schalter/website/an", data={"_csrf": token, "grund": "x"}).status_code == 403


def test_leser_anlegen_ueber_seite_und_cli(app, monkeypatch, capsys):
    anna, token = login(app, "anna")
    assert "leser" in anna.get("/nutzer").get_data(as_text=True)
    anna.post("/nutzer", data={"_csrf": token, "aktion": "anlegen", "name": "tom", "passwort": "tom-passwort-1",
                               "rolle": "leser"})
    with Store(app.extensions["settings"].db_path) as store:
        assert {n["name"]: n["rolle"] for n in repo.nutzer_liste(store)}["tom"] == "leser"
        zeile = repo.aktionen_liste(store, aktion="nutzer_anlegen")[0]
        assert zeile["wer"] == "anna" and zeile["gegenstand_typ"] == "nutzer" and zeile["gegenstand_id"] == "tom"
    from news_radar.__main__ import main

    monkeypatch.setenv("RADAR_DATA_DIR", str(app.extensions["settings"].data_dir))
    monkeypatch.setenv("RADAR_NEUES_PASSWORT", "max-passwort-1")
    assert main(["nutzer", "anlegen", "max", "--rolle", "leser"]) == 0
    with Store(app.extensions["settings"].db_path) as store:
        assert repo.nutzer_pruefen(store, "max", "max-passwort-1")["rolle"] == "leser"
    with pytest.raises(ValueError):
        with Store(app.extensions["settings"].db_path) as store:
            repo.nutzer_anlegen(store, "x", "langes-passwort", "gast")
