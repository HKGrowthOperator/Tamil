"""Stopp-Schalter (Vertrag B1.1, §8, Test T7): global und je Kanal, Prüfung unmittelbar vor dem Aufruf nach außen,
Grund Pflicht, Protokollzeile, CLI und Cockpit. Kein Netz: FakeAnthropic und Fake-WordPress."""

import sqlite3

import pytest

from news_radar import publisher, schalter
from news_radar.config import load_settings
from news_radar.store import Store
from news_radar.workflow import jobs, orchestrator, providers, repo, schema
from news_radar.workflow.fake import FakeAnthropic
from news_radar.workflow.models import RechercheErgebnis


class FakeWP:
    """Core-REST-Ersatz: zählt jeden Aufruf; `beim_post` läuft beim Anlegen (z. B. Schalter setzen)."""

    def __init__(self, beim_post=None):
        self.posts = []
        self.beim_post = beim_post

    def upload_media(self, image, alt):
        return 9

    def create_post(self, **kw):
        self.posts.append(kw)
        if self.beim_post:
            self.beim_post()
        return {"id": 500 + len(self.posts), "link": f"https://www.tamil.de/{kw['slug']}/"}

    def edit_link(self, post):
        return f"https://www.tamil.de/wp-admin/post.php?post={post['id']}&action=edit"


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY", "GEMINI_API_KEY",
                "BILD_POOL_DIR", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    return s


@pytest.fixture
def store(settings):
    with Store(settings.db_path) as st:
        yield st


def entwurf(store, uid="u1", titel="Lichterfest in Hamm", freigeben=True) -> int:
    did = store.insert_draft(dict(uid=uid, typ="artikel", titel=titel, teaser="T", inhalt_html="<p>Text</p>",
                                  kategorie="news", relevanz=8, dach_bezug=True, ort="Hamm", schlagworte=["Fest"],
                                  quelle_url="https://q.de/1", quelle_name="Q", original_json={"titel": titel}))
    if freigeben:
        store.set_status(did, "freigeben", von="priya")
    return did


# ---- Migration --------------------------------------------------------------------------------

def test_migration_legt_tabellen_und_spalten_an(store):
    assert store.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST >= 4
    tabellen = {r[0] for r in store.db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"schalter", "dienst_laeufe"} <= tabellen
    spalten = {r[1] for r in store.db.execute("PRAGMA table_info(editorial_actions)")}
    assert {"gegenstand_typ", "gegenstand_id", "kanal", "regel_fassung", "ausloeser"} <= spalten
    # keine Tabellen für spätere Bausteine
    assert not tabellen & {"einsendungen", "verzeichnis", "werbung", "regeln"}


def _schema_dump(path) -> list:
    db = sqlite3.connect(path)
    try:
        return sorted(db.execute("SELECT type, name, sql FROM sqlite_master").fetchall()) + \
            [db.execute("PRAGMA user_version").fetchone()[0]]
    finally:
        db.close()


def test_migration_auf_altem_bestand_behaelt_daten_und_ist_wiederholbar(settings, monkeypatch):
    """Stand vor der Migration anlegen (v3), Daten hinein, migrieren, Daten noch da, zweiter Start ändert nichts."""
    alt = {v: sql for v, sql in schema.MIGRATIONS.items() if v <= 3}
    monkeypatch.setattr(schema, "MIGRATIONS", alt)
    with Store(settings.db_path) as st:
        assert st.db.execute("PRAGMA user_version").fetchone()[0] == 3
        repo.nutzer_anlegen(st, "anna", "anna-passwort-1", "admin")
        repo.nutzer_anlegen(st, "priya", "priya-passwort-1", "redaktion")
        did = entwurf(st)
        st.db.execute("INSERT INTO editorial_actions (ts, wer, aktion, draft_id) VALUES ('2026-11-01T10:00:00+00:00', "
                      "'priya', 'freigeben', ?)", (did,))
        st.db.commit()
    monkeypatch.undo()
    with Store(settings.db_path) as st:
        assert st.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST
        assert {(n["name"], n["rolle"], n["aktiv"]) for n in repo.nutzer_liste(st)} == {("anna", "admin", 1),
                                                                                       ("priya", "redaktion", 1)}
        assert repo.nutzer_pruefen(st, "priya", "priya-passwort-1")["rolle"] == "redaktion"
        alt_zeile = repo.aktionen(st, did)[0]
        assert alt_zeile["wer"] == "priya" and alt_zeile["aktion"] == "freigeben" and alt_zeile["kanal"] is None
        assert st.get_draft(did)["status"] == "freigegeben"
        assert not schalter.gestoppt(st, "redaktion")
    vorher = _schema_dump(settings.db_path)
    with Store(settings.db_path):
        pass
    assert _schema_dump(settings.db_path) == vorher


def test_migration_haelt_gleichzeitigen_start_aus(settings):
    """Zwei Prozesse starten gleichzeitig (Web und Worker): die Spalte existiert schon, die Migration läuft trotzdem."""
    with Store(settings.db_path) as st:
        st.db.execute("PRAGMA user_version = 3")
        st.db.commit()
    with Store(settings.db_path) as st:
        assert st.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST


# ---- Schalter setzen --------------------------------------------------------------------------

def test_kanaele_und_standard_aus(store):
    assert schalter.KANAELE == ("alles", "redaktion", "website", "eingang", "verzeichnis", "instagram", "facebook",
                                "whatsapp")
    assert not any(schalter.gestoppt(store, k) for k in schalter.KANAELE)
    assert [z["kanal"] for z in schalter.stand(store)] == list(schalter.KANAELE)


def test_grund_und_person_sind_pflicht(store):
    with pytest.raises(ValueError, match="Grund"):
        schalter.setzen(store, "website", True, wer="priya", grund="   ")
    with pytest.raises(ValueError, match="Person"):
        schalter.setzen(store, "website", True, wer="", grund="Wartung")
    with pytest.raises(ValueError, match="Kanal"):
        schalter.setzen(store, "telegram", True, wer="priya", grund="x")
    assert not schalter.gestoppt(store, "website")


def test_kanal_und_alles(store):
    schalter.setzen(store, "website", True, wer="priya", grund="Theme-Umbau")
    assert schalter.gestoppt(store, "website") and not schalter.gestoppt(store, "redaktion")
    sperre = schalter.sperre(store, "website")
    assert sperre["kanal"] == "website" and sperre["grund"] == "Theme-Umbau" and sperre["wer"] == "priya" and sperre["seit"]
    schalter.setzen(store, "alles", True, wer="anna", grund="Notfall")
    assert all(schalter.gestoppt(store, k) for k in schalter.KANAELE)
    assert schalter.sperre(store, "instagram")["kanal"] == "alles"
    schalter.setzen(store, "alles", False, wer="anna")
    assert schalter.gestoppt(store, "website") and not schalter.gestoppt(store, "instagram")
    with pytest.raises(schalter.Gestoppt) as exc:
        schalter.pruefen(store, "website")
    assert "website" in str(exc.value) and "Theme-Umbau" in str(exc.value)
    schalter.pruefen(store, "redaktion")  # wirft nicht


def test_jede_aenderung_schreibt_protokoll_ohne_inhalt(store):
    schalter.setzen(store, "instagram", True, wer="priya", grund="Regel unklar")
    schalter.setzen(store, "instagram", False, wer="anna")
    zeilen = repo.aktionen_liste(store, kanal="instagram")
    assert [z["aktion"] for z in zeilen] == ["schalter_aus", "schalter_an"]
    an = zeilen[1]
    assert an["wer"] == "priya" and an["ausloeser"] == "person" and an["gegenstand_typ"] == "schalter"
    assert an["gegenstand_id"] == "instagram" and an["notiz"] == "Regel unklar"


# ---- Redaktion: kein Scan, kein Claim, kein Modellaufruf ----------------------------------------

def test_kein_job_wird_uebernommen(store):
    jobs.einreihen(store, None, "recherche")
    schalter.setzen(store, "redaktion", True, wer="priya", grund="Test")
    assert jobs.naechster(store, "w") is None
    schalter.setzen(store, "redaktion", False, wer="priya")
    schalter.setzen(store, "alles", True, wer="priya", grund="Test")
    assert jobs.naechster(store, "w") is None
    schalter.setzen(store, "alles", False, wer="anna")
    schalter.setzen(store, "website", True, wer="priya", grund="nur Website")
    assert jobs.naechster(store, "w")["schritt"] == "recherche"


@pytest.mark.parametrize("kanal", ["redaktion", "alles"])
def test_modellaufruf_wird_unmittelbar_vorher_geprueft(settings, store, kanal):
    client = FakeAnthropic()
    budget = providers.budget_fuer(settings, store)
    claude = providers.Claude(settings, store, client=client, budget=budget)
    schalter.setzen(store, kanal, True, wer="priya", grund="Test")
    with pytest.raises(schalter.Gestoppt):
        claude.call("recherche", "System", "<dokumente>\n[]\n</dokumente>", RechercheErgebnis)
    assert client.requests == []
    assert store.db.execute("SELECT COUNT(*) FROM agent_usage").fetchone()[0] == 0
    assert store.db.execute("SELECT COUNT(*) FROM budget_reservierungen").fetchone()[0] == 0


def test_gestoppter_schritt_kostet_keinen_versuch(settings, store):
    ctx = orchestrator.kontext(settings, store, client=FakeAnthropic(), fetch_text=lambda u: "", suche=lambda q: [])
    sid = repo.story_anlegen(store, typ="news", titel="Lichterfest")
    jobs.einreihen(store, sid, "recherche")
    job = jobs.naechster(store, "w")
    schalter.setzen(store, "redaktion", True, wer="priya", grund="mitten im Schritt")
    assert orchestrator.job_ausfuehren(ctx, job) == "angehalten"
    zeile = store.db.execute("SELECT status, versuche FROM workflow_jobs WHERE id = ?", (job["id"],)).fetchone()
    assert tuple(zeile) == ("offen", 0)
    assert repo.story(store, sid)["status"] != "fehler"


def test_scan_beginnt_nicht(settings, store, monkeypatch):
    def kein_abruf(*a, **kw):
        raise AssertionError("Quellen dürfen bei Stopp nicht abgerufen werden")

    monkeypatch.setattr("news_radar.sources.fetch_all", kein_abruf)
    ctx = orchestrator.kontext(settings, store, client=FakeAnthropic())
    schalter.setzen(store, "redaktion", True, wer="priya", grund="Test")
    assert orchestrator.scan(ctx)["angehalten"] == 1
    assert repo.stories(store) == []


def test_v1_lauf_beginnt_nicht(settings, store, monkeypatch):
    from news_radar import pipeline

    def kein_abruf(*a, **kw):
        raise AssertionError("Quellen dürfen bei Stopp nicht abgerufen werden")

    monkeypatch.setattr("news_radar.sources.fetch_all", kein_abruf)
    schalter.setzen(store, "redaktion", True, wer="priya", grund="Test")
    assert pipeline.run(settings, writer=object(), store=store) == []


def test_lauf_mit_gestoppter_redaktion_veroeffentlicht_trotzdem(settings, monkeypatch):
    wp = FakeWP()
    monkeypatch.setattr(publisher, "make_wordpress", lambda s: wp)
    settings.wp_url, settings.wp_user, settings.wp_app_password = "https://www.tamil.de", "u", "p"
    with Store(settings.db_path) as st:
        entwurf(st)
        schalter.setzen(st, "redaktion", True, wer="priya", grund="Test")
    stats = orchestrator.lauf(settings, items=[])
    assert stats["angehalten"] == 1 and len(wp.posts) == 1


# ---- Website: Freigegebenes wartet ---------------------------------------------------------------

def test_website_stopp_haelt_zurueck_und_protokolliert_einmal(settings, store):
    did = entwurf(store)
    wp = FakeWP()
    schalter.setzen(store, "website", True, wer="priya", grund="Theme-Umbau")
    assert publisher.publish_approved(settings, store, wp=wp) == []
    assert publisher.publish_approved(settings, store, wp=wp) == []
    assert wp.posts == [] and store.get_draft(did)["status"] == "freigegeben"
    zurueck = repo.aktionen_liste(store, aktion="zurueckgehalten")
    assert len(zurueck) == 1 and zurueck[0]["kanal"] == "website" and zurueck[0]["ausloeser"] == "dienst"
    assert zurueck[0]["draft_id"] == did and "website" in zurueck[0]["notiz"]
    schalter.setzen(store, "website", False, wer="priya")
    ergebnis = publisher.publish_approved(settings, store, wp=wp)
    assert [r.status for r in ergebnis] == ["veroeffentlicht"] and len(wp.posts) == 1
    raus = repo.aktionen_liste(store, aktion="veroeffentlicht")[0]
    assert raus["wer"] == "dienst" and raus["ausloeser"] == "dienst" and raus["kanal"] == "website"
    assert raus["gegenstand_typ"] == "entwurf" and raus["gegenstand_id"] == str(did) and raus["wp_post_id"] == 501
    assert raus["fassung_hash"] == repo.fassung_hash(store.get_draft(did))


def test_publish_draft_prueft_direkt_vor_wordpress(settings, store):
    did = entwurf(store)
    row = store.claim_draft(did, von="priya")
    wp = FakeWP()
    schalter.setzen(store, "alles", True, wer="priya", grund="Notfall")
    with pytest.raises(schalter.Gestoppt):
        publisher.publish_draft(row, settings, wp, store, status="publish")
    assert wp.posts == []


def test_stopp_mitten_im_lauf_gibt_den_rest_frei(settings, store):
    a, b = entwurf(store, "u1", "Erster"), entwurf(store, "u2", "Zweiter")
    wp = FakeWP(beim_post=lambda: schalter.setzen(store, "website", True, wer="priya", grund="sofort"))
    ergebnis = publisher.publish_approved(settings, store, wp=wp)
    assert len(wp.posts) == 1 and [r.status for r in ergebnis] == ["veroeffentlicht"]
    assert {store.get_draft(a)["status"], store.get_draft(b)["status"]} == {"veroeffentlicht", "freigegeben"}


# ---- CLI -------------------------------------------------------------------------------------------

def test_cli_stopp(settings, monkeypatch, capsys):
    from news_radar.__main__ import main

    monkeypatch.setenv("RADAR_DATA_DIR", str(settings.data_dir))
    assert main(["stopp", "an", "website", "--grund", "Wartung"]) == 0
    assert main(["stopp", "status"]) == 0
    out = capsys.readouterr().out
    assert "website" in out and "angehalten" in out and "Wartung" in out
    with pytest.raises(SystemExit):
        main(["stopp", "an", "redaktion"])  # ohne Grund
    assert main(["stopp", "an", "--grund", "Notfall"]) == 0  # ohne Kanal: alles
    with Store(settings.db_path) as st:
        assert schalter.gestoppt(st, "instagram") and schalter.sperre(st, "instagram")["wer"] == "konsole"
    assert main(["stopp", "aus", "alles"]) == 0 and main(["stopp", "aus", "website"]) == 0
    with Store(settings.db_path) as st:
        assert not any(schalter.gestoppt(st, k) for k in schalter.KANAELE)
        assert len(repo.aktionen_liste(st, aktion="schalter_an")) == 2


# ---- Cockpit: Seite, Banner, /gesund, Direkt posten im Stopp ------------------------------------

@pytest.fixture
def web(settings):
    from news_radar.web import create_app

    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim", "s3cret"
    with Store(settings.db_path) as st:
        entwurf(st, freigeben=False)
    app = create_app(settings, testing=True)
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": "luis", "password": "geheim", "_csrf": token}).status_code == 302
    return app, client, token


def test_schalterseite_grund_pflicht_banner_und_gesund(web):
    app, client, token = web
    html = client.get("/schalter").get_data(as_text=True)
    for k in schalter.KANAELE:
        assert f"/schalter/{k}/an" in html
    assert 'name="grund"' in html and "required" in html
    resp = client.post("/schalter/website/an", data={"_csrf": token, "grund": "  "}, follow_redirects=True)
    assert "Grund fehlt" in resp.get_data(as_text=True)
    assert client.get("/gesund").get_json()["gestoppt"] == []
    client.post("/schalter/website/an", data={"_csrf": token, "grund": "Theme-Umbau"})
    for seite in ("/", "/kosten", "/protokoll", "/entwurf/1", "/schalter", "/zeitplan"):
        text = client.get(seite).get_data(as_text=True)
        assert 'class="banner stopp"' in text and "Website" in text and "Theme-Umbau" in text, seite
    gesund = client.get("/gesund").get_json()
    assert gesund["ok"] is True and [g["kanal"] for g in gesund["gestoppt"]] == ["website"]
    assert gesund["gestoppt"][0]["seit"] and set(gesund["gestoppt"][0]) == {"kanal", "seit"}  # öffentlich: ohne Grund, ohne Person
    client.post("/schalter/website/aus", data={"_csrf": token})
    assert 'class="banner stopp"' not in client.get("/").get_data(as_text=True)


@pytest.mark.parametrize("weg", ["veroeffentlichen", "wp-entwurf"])
def test_direkt_posten_im_stopp_gibt_frei_und_sagt_warum(web, settings, weg):
    app, client, token = web
    wp = app.extensions["wordpress"] = FakeWP()
    client.post("/schalter/website/an", data={"_csrf": token, "grund": "Theme-Umbau"})
    resp = client.post(f"/entwurf/1/{weg}", data={"_csrf": token}, follow_redirects=True)
    text = resp.get_data(as_text=True)
    assert resp.status_code == 200 and "angehalten" in text and "wartet" in text
    assert wp.posts == []
    with Store(settings.db_path) as st:
        assert st.get_draft(1)["status"] == "freigegeben"
        assert [a["aktion"] for a in repo.aktionen(st, 1)] == ["freigeben", "zurueckgehalten"]
        assert repo.aktionen(st, 1)[-1]["kanal"] == "website"
    client.post("/schalter/website/aus", data={"_csrf": token})
    with Store(settings.db_path) as st:
        assert [r.status for r in publisher.publish_approved(settings, st, wp=wp)] == ["veroeffentlicht"]


def test_neu_schreiben_im_stopp_ohne_modellaufruf(web, settings):
    app, client, token = web

    class Writer:
        aufrufe = 0

        def rewrite(self, row, anweisung):
            Writer.aufrufe += 1

    app.extensions["writer"] = Writer()
    client.post("/schalter/redaktion/an", data={"_csrf": token, "grund": "Kosten prüfen"})
    text = client.post("/entwurf/1/neu-schreiben", data={"_csrf": token}, follow_redirects=True).get_data(as_text=True)
    assert "angehalten" in text and Writer.aufrufe == 0
    # Bearbeiten und Freigeben von Hand bleiben möglich
    client.post("/entwurf/1", data={"_csrf": token, "titel": "Neu", "kategorie": "news", "inhalt_html": "<p>a</p>"})
    client.post("/entwurf/1/status", data={"_csrf": token, "aktion": "freigeben"})
    with Store(settings.db_path) as st:
        assert st.get_draft(1)["titel"] == "Neu" and st.get_draft(1)["status"] == "freigegeben"
