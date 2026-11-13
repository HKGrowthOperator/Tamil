"""Baustein F4 (Vertrag B2, B3): Instagram, Facebook und WhatsApp-Entwurf im Trockenmodus.

Regelwerk Fassung 1 (`docs/regeln-social.md`, R1–R9), Ablauf und Abnahmetests aus `docs/vertrag/festlegung-social.md`,
Felder und Status-Maschine aus `docs/spezifikation/datenmodell.md` §15. Kein Netz: Fake-WordPress (Liste von
REST-Antworten) und FakeMeta bzw. der Trocken-Transport, der beim ersten Aufruf nach außen fehlschlägt.
"""

import io
import json
from datetime import datetime, timedelta, timezone

import pytest
from PIL import Image

from news_radar import dienst, schalter
from news_radar.config import load_settings
from news_radar.social import ablauf, aktionen, konfig, regelwerk
from news_radar.social.fake import FakeMeta
from news_radar.social.quelle import beitrag_aus_wp, umfang_menge
from news_radar.social.transport import TrockenTransport, UnklarFehler, ZugangFehler
from news_radar.store import Store
from news_radar.workflow import repo, schema

UTC = timezone.utc
START = datetime(2026, 11, 16, 8, 0, tzinfo=UTC)  # Montag, 9 Uhr in Berlin


@pytest.fixture
def settings(tmp_path, monkeypatch):
    for var in ("WP_URL", "WP_USER", "WP_APP_PASSWORD", "GEMINI_API_KEY", "NOTIFY_WEBHOOK_URL", "ANTHROPIC_API_KEY",
                "RADAR_SOCIAL", "RADAR_SOCIAL_LIVE", "META_ZUGANG", "META_IG_USER_ID", "META_PAGE_ID"):
        monkeypatch.setenv(var, "")
    s = load_settings()
    s.data_dir = tmp_path
    s.wp_url = "https://www.tamil.de"
    return s


def kbs_freigabe(store, wer="anna"):
    """Die einmalige Freigabe der aktuellen Fassung durch KBS (über Luis) eintragen – Voraussetzung für live."""
    return regelwerk.freigabe_eintragen(store, wer=wer, freigegeben_von="KBS über Luis", datum="2026-11-14",
                                        beleg="Mail von Luis, 14.11.2026")


@pytest.fixture
def store(settings):
    with Store(settings.db_path) as st:
        kbs_freigabe(st)  # die Fälle mit FakeMeta laufen „live“; ohne Freigabe: eigener Test
        yield st


def post(pid, *, titel="Lichterfest im Tempel Hamm", stunden=0.5, jetzt=START, rubrik="community", uid=None,
         event=None, tags=(), standfirst="Tausende feiern Deepavali in Hamm.", story_id=None):
    """Eine Antwort von /wp/v2/posts?_embed=wp:term wie WordPress sie liefert."""
    datum = (jetzt - timedelta(hours=stunden)).replace(tzinfo=None).isoformat(timespec="seconds")
    meta = {"radar_uid": uid if uid is not None else f"radar-{pid}", "standfirst": standfirst, "event_datum": event or "",
            "event_ort": "Festhalle Bern" if event else "", "radar_story_id": story_id or 0}
    terms = [[{"taxonomy": "category", "slug": rubrik, "name": rubrik.title()}],
             [{"taxonomy": "post_tag", "slug": t.lower(), "name": t} for t in tags]]
    return {"id": pid, "date_gmt": datum, "link": f"https://www.tamil.de/beitrag-{pid}/",
            "title": {"rendered": titel}, "excerpt": {"rendered": f"<p>{standfirst}</p>"}, "meta": meta,
            "_embedded": {"wp:term": terms}}


class FakeWP:
    """Lesender Abruf der Website: gibt die gesetzten Beiträge zurück und merkt sich die Parameter."""

    def __init__(self, posts=()):
        self.posts = list(posts)
        self.abrufe = []

    def __call__(self, params):
        self.abrufe.append(dict(params))
        return list(self.posts)


def erkennen(store, settings, wp, jetzt=START):
    return ablauf.erkennen(store, settings, wp, jetzt)


def zeilen(store, **wo):
    sql = "SELECT * FROM social_beitraege" + (" WHERE " + " AND ".join(f"{k} = ?" for k in wo) if wo else "")
    return [dict(r) for r in store.db.execute(sql + " ORDER BY id", tuple(wo.values()))]


def mit_startmarke(store, settings, posts, jetzt=START, vorlauf=timedelta(hours=1)):
    """Erster Lauf setzt die Startmarke `vorlauf` vor `jetzt`; dann sind die Beiträge neu."""
    erkennen(store, settings, FakeWP(), jetzt - vorlauf)
    wp = FakeWP(posts)
    return erkennen(store, settings, wp, jetzt), wp


# ---- Datenmodell ----------------------------------------------------------------------------------

def test_migration_8_legt_social_tabellen_an(store):
    assert schema.LATEST >= 8 and 8 in schema.MIGRATIONS
    assert store.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST
    spalten = {r[1] for r in store.db.execute("PRAGMA table_info(social_beitraege)")}
    for feld in ("wp_post_id", "quelle_typ", "kanal", "status", "regel_fassung", "regelpruefung", "text", "hashtags",
                 "link", "bild_datei", "ki_hinweis", "karenz_bis", "geplant_fuer", "veroeffentlicht_at", "meta_id",
                 "meta_link", "fehler", "gepostet_von", "gepostet_at", "nutzlast", "container_id"):
        assert feld in spalten, feld
    store._write("INSERT INTO social_beitraege (wp_post_id, quelle_typ, kanal, status, regel_fassung, erkannt_at, "
                 "aktualisiert) VALUES (1, 'beitrag', 'instagram', 'karenz', '1', 'x', 'x')")
    with pytest.raises(Exception):  # höchstens einmal je Beitrag und Kanal (R7)
        store._write("INSERT INTO social_beitraege (wp_post_id, quelle_typ, kanal, status, regel_fassung, erkannt_at, "
                     "aktualisiert) VALUES (1, 'beitrag', 'instagram', 'karenz', '1', 'x', 'x')")


# ---- Regelwerk ------------------------------------------------------------------------------------

def test_regelwerk_fassung_1_aus_der_datei(store):
    rw = regelwerk.aktuell(store)
    assert rw.fassung == "1"
    assert set(rw.rubriken) == {"news", "kino", "events", "community", "kueche", "kultur", "sport", "entertainment"}
    assert (rw.max_je_tag, rw.abstand_min, rw.ruhe_von, rw.ruhe_bis, rw.max_alter_stunden, rw.karenz_min) == \
        (6, 60, 22, 7, 48, 10)
    assert rw.hashtags_platzhalter  # KBS liefert die echten Hashtags
    assert all(rw.hashtags.get(r) for r in rw.rubriken)


@pytest.mark.parametrize("kw, regel, ergebnis", [
    ({}, None, None),
    ({"rubrik": "news", "tags": ["Politik"]}, "R2", "verletzt"),
    ({"rubrik": "news", "titel": "Unglück auf der A1: zwei Tote"}, "R2", "verletzt"),
    ({"rubrik": "werbung"}, "R1", "unklar"),
    ({"stunden": 49}, "R3", "verletzt"),
    ({"event": "2026-11-10"}, "R3", "verletzt"),
])
def test_regelpruefung_je_regel_mit_grund(store, kw, regel, ergebnis):
    b = beitrag_aus_wp(post(5, **kw))
    pruefung = regelwerk.pruefen(b, regelwerk.aktuell(store), START)
    assert set(pruefung) == {f"R{i}" for i in range(1, 10)}
    assert all(p["grund"] for p in pruefung.values())
    if regel is None:
        assert regelwerk.automatisch(pruefung)
    else:
        assert pruefung[regel]["ergebnis"] == ergebnis and not regelwerk.automatisch(pruefung)
        assert any(g.startswith(regel) for g in regelwerk.gruende(pruefung))


def test_story_als_sensibel_markiert_geht_nie_automatisch(store, settings):
    sid = repo.story_anlegen(store, typ="news", titel="Prozess in Düsseldorf")
    repo.story_setzen(store, sid, sensibel=1)
    mit_startmarke(store, settings, [post(7, rubrik="news", story_id=sid)])
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "von_hand" and "R2" in ig["fehler"]
    assert json.loads(ig["regelpruefung"])["R2"]["ergebnis"] == "verletzt"


def test_termin_in_der_zukunft_ist_regelkonform(store):
    b = beitrag_aus_wp(post(8, rubrik="events", event="2026-11-28 18:00"))
    assert b.quelle_typ == "termin"
    assert regelwerk.automatisch(regelwerk.pruefen(b, regelwerk.aktuell(store), START))


def test_umfang_wird_tolerant_gelesen():
    assert umfang_menge("website,social") == {"website", "social"}
    assert umfang_menge(" Website; Social ,print") == {"website", "social", "print"}
    assert umfang_menge("Online-Veröffentlichung auf tamil.de") == set()
    assert umfang_menge(None) == set() and umfang_menge("") == set()


def test_regelwerk_aendern_gibt_neue_fassung_und_protokoll(store):
    neu = regelwerk.speichern(store, {"max_je_tag": 4}, wer="anna")
    assert neu.fassung == "2" and neu.max_je_tag == 4 and regelwerk.aktuell(store).fassung == "2"
    zeile = repo.aktionen_liste(store, aktion="social_regelwerk")[0]
    assert zeile["wer"] == "anna" and zeile["regel_fassung"] == "2"
    with pytest.raises(ValueError):
        regelwerk.speichern(store, {"max_je_tag": -1}, wer="anna")


# ---- Erkennen und Vorbereiten ---------------------------------------------------------------------

def test_erster_lauf_setzt_startmarke_und_altbestand_loest_nichts_aus(store, settings):
    alt = [post(1, stunden=3), post(2, stunden=0.1, uid="alt-1234")]
    stats = erkennen(store, settings, FakeWP(alt))
    assert stats["startmarke_gesetzt"] == 1 and zeilen(store) == []
    wp = FakeWP(alt)
    stats = erkennen(store, settings, wp, START + timedelta(minutes=5))
    assert zeilen(store) == [] and stats["altbestand"] == 2  # vor der Startmarke bzw. aus der Übernahme (alt-…)
    assert wp.abrufe and wp.abrufe[0]["status"] == "publish"


def test_neuer_beitrag_ergibt_instagram_facebook_und_whatsapp(store, settings):
    stats, _ = mit_startmarke(store, settings, [post(10, tags=["Deepavali"])])
    assert stats["neu"] == 1
    z = {r["kanal"]: r for r in zeilen(store)}
    assert set(z) == {"instagram", "facebook", "whatsapp"}
    ig = z["instagram"]
    assert ig["status"] == "karenz" and ig["regel_fassung"] == "1" and ig["quelle_typ"] == "beitrag"
    assert ig["karenz_bis"] == (START + timedelta(minutes=10)).isoformat(timespec="seconds")
    assert "Lichterfest im Tempel Hamm" in ig["text"] and "https://www.tamil.de/beitrag-10/" in ig["text"]
    assert json.loads(ig["hashtags"]) and all(h in ig["text"] for h in json.loads(ig["hashtags"]))
    assert ig["bild_art"] == "karte" and "R4" in ig["regelpruefung"]  # ohne Lizenz-Datensatz kein Social-Recht
    bild = Image.open(settings.data_dir / "social" / ig["bild_datei"])
    assert bild.size == (1080, 1350) and bild.format == "JPEG"
    assert z["whatsapp"]["status"] == "entwurf" and "#" not in z["whatsapp"]["text"]
    protokoll = repo.aktionen_liste(store, aktion="social_erkannt")
    assert {p["kanal"] for p in protokoll} == {"instagram", "facebook", "whatsapp"}
    assert all(p["regel_fassung"] == "1" and p["ausloeser"] == "dienst" and p["wp_post_id"] == 10 for p in protokoll)


def test_korrektur_am_artikel_loest_nichts_erneut_aus(store, settings):
    mit_startmarke(store, settings, [post(11)])
    erkennen(store, settings, FakeWP([post(11, titel="Lichterfest im Tempel Hamm (korrigiert)")]),
             START + timedelta(minutes=3))
    assert len(zeilen(store)) == 3 and "korrigiert" not in zeilen(store, kanal="instagram")[0]["text"]


def entwurf_mit_bild(store, settings, umfang, *, ki=False, wp_post_id=12, **lizenz_felder):
    from news_radar import images, lizenz

    settings.bilder_dir.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1600, 900), (20, 120, 60))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    (settings.bilder_dir / "foto.jpg").write_bytes(buf.getvalue())
    did = store.insert_draft(dict(uid=f"radar-{wp_post_id}", typ="artikel", titel="T", teaser="T", inhalt_html="<p>x</p>",
                                  kategorie="community", relevanz=8, dach_bezug=True, ort="Hamm", schlagworte=["x"],
                                  bild_datei="foto.jpg", bild_origin="ki" if ki else "commons",
                                  original_json={"titel": "T"}))
    store._write("UPDATE drafts SET wp_post_id = ? WHERE id = ?", (wp_post_id, did))
    # vollständiger Lizenz-Datensatz (Spezifikation Bilder 3.1), Umfang nach Testfall
    if ki:
        felder = lizenz.datensatz(images.FeaturedImage(buf.getvalue(), "foto.jpg", "image/jpeg", lizenz.KI_CREDIT, "ki",
                                                       prompt="Empty hall", modell="gemini-nano-banana-2.1"))
    else:
        felder = {"herkunft": "commons", "rechteinhaber": "Max Muster", "urheber": "Max Muster",
                  "lizenz_kuerzel": "cc-by-4.0", "lizenz": "CC BY 4.0", "lizenz_url": lizenz.lizenz_url("cc-by-4.0"),
                  "attribution": "Foto: Max Muster / Wikimedia Commons, CC BY 4.0", "bearbeitung": "zugeschnitten",
                  "quelle_url": "https://commons.wikimedia.org/wiki/File:A.jpg", "bild_url": "https://upload.wikimedia.org/a.jpg",
                  "beleg": "commons-api", "geprueft_von": "agent:test", "geprueft_am": "2026-11-13T10:00:00+00:00"}
    lizenz.anlegen(store, datei="foto.jpg", daten=buf.getvalue(), draft_id=did,
                   felder={**felder, "umfang": umfang, **lizenz_felder})
    assert images  # Modul vorhanden (Schriften und Farben der Bildkarte)
    return did


def test_beitragsbild_nur_mit_umfang_social(store, settings):
    entwurf_mit_bild(store, settings, "website,social")
    mit_startmarke(store, settings, [post(12)])
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["bild_art"] == "foto" and ig["asset_id"] and not ig["ki_hinweis"]
    assert Image.open(settings.data_dir / "social" / ig["bild_datei"]).size == (1080, 1350)


def test_ohne_umfang_social_die_bildkarte(store, settings):
    entwurf_mit_bild(store, settings, "website")
    mit_startmarke(store, settings, [post(12)])
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["bild_art"] == "karte" and "Bildkarte" in json.loads(ig["regelpruefung"])["R4"]["grund"]


def test_abgelaufene_oder_unvollstaendige_lizenz_ergibt_die_bildkarte(store, settings):
    """Umfang „social“ reicht nicht: der Datensatz muss vollständig sein (Ablauf, Kürzel, Urheber)."""
    entwurf_mit_bild(store, settings, "website,social", ablauf="2020-01-01")
    mit_startmarke(store, settings, [post(12)])
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["bild_art"] == "karte" and "Ablauf" in json.loads(ig["regelpruefung"])["R4"]["grund"]


def test_datensatz_eines_anderen_entwurfs_zaehlt_nicht(store, settings):
    did = entwurf_mit_bild(store, settings, "website,social")
    store._write("UPDATE assets SET draft_id = ? WHERE draft_id = ?", (did + 100, did))  # gehört einem anderen Entwurf
    mit_startmarke(store, settings, [post(12)])
    assert zeilen(store, kanal="instagram")[0]["bild_art"] == "karte"


def test_ki_bild_traegt_hinweis_in_text_und_bild(store, settings):
    entwurf_mit_bild(store, settings, "website,social", ki=True)
    mit_startmarke(store, settings, [post(12)])
    ig = zeilen(store, kanal="instagram")[0]
    rw = regelwerk.aktuell(store)
    assert ig["ki_hinweis"] == 1 and rw.ki_hinweis in ig["text"]
    assert json.loads(ig["regelpruefung"])["R8"]["ergebnis"] == "erfuellt"


# ---- Senden im Trockenmodus -----------------------------------------------------------------------

def test_trockenmodus_nichts_vor_der_karenz_dann_volle_nutzlast_ohne_aufruf(store, settings):
    mit_startmarke(store, settings, [post(20)])
    t = TrockenTransport()
    assert ablauf.senden(store, settings, t, START + timedelta(minutes=9))["gesendet"] == 0
    stats = ablauf.senden(store, settings, t, START + timedelta(minutes=11))
    assert stats["trocken"] == 2
    ig, fb = zeilen(store, kanal="instagram")[0], zeilen(store, kanal="facebook")[0]
    assert ig["status"] == fb["status"] == "trocken" and not ig["meta_id"] and ig["modus"] == "trocken"
    nutzlast = json.loads(ig["nutzlast"])
    assert [s["pfad"] for s in nutzlast["schritte"]] == ["/{ig-user-id}/media", "/{container-id}?fields=status_code",
                                                         "/{ig-user-id}/content_publishing_limit",
                                                         "/{ig-user-id}/media_publish", "/{media-id}?fields=permalink"]
    assert nutzlast["schritte"][0]["daten"]["caption"] == ig["text"]
    assert json.loads(fb["nutzlast"])["schritte"][0]["pfad"] == "/{page-id}/photos"
    assert ig["sende_at"] <= fb["sende_at"]  # zuerst Instagram
    for kanal in ("instagram", "facebook"):
        z = repo.aktionen_liste(store, aktion="social_senden", kanal=kanal)[0]
        assert z["regel_fassung"] == "1" and "trocken" in z["notiz"] and z["ausloeser"] == "dienst"
    assert ablauf.senden(store, settings, t, START + timedelta(hours=3))["gesendet"] == 0  # nie doppelt


def test_trocken_transport_ruft_nie_nach_aussen():
    with pytest.raises(AssertionError):
        TrockenTransport().ig_container("https://x", "c", "a")


def test_live_nur_mit_schalter_und_schluesseln(monkeypatch):
    env = {"RADAR_SOCIAL_LIVE": "an", "META_ZUGANG": "t", "META_IG_USER_ID": "1", "META_PAGE_ID": "2"}
    assert konfig.laden(env).live
    assert not konfig.laden({**env, "RADAR_SOCIAL_LIVE": ""}).live
    assert not konfig.laden({**env, "META_ZUGANG": ""}).live
    k = konfig.laden({})
    assert not k.live and not k.aktiv and k.modus == "trocken"
    assert konfig.laden({"RADAR_SOCIAL": "an"}).aktiv
    assert isinstance(ablauf.transport_fuer(konfig.laden({})), TrockenTransport)


# ---- Senden mit nachgestellter Schnittstelle --------------------------------------------------------

def test_t1_nach_der_karenz_instagram_dann_facebook_mit_links_und_kennung(store, settings):
    mit_startmarke(store, settings, [post(30)])
    meta = FakeMeta()
    stats = ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "https://cdn/x.jpg")
    assert stats["veroeffentlicht"] == 2
    ig, fb = zeilen(store, kanal="instagram")[0], zeilen(store, kanal="facebook")[0]
    assert ig["status"] == fb["status"] == "veroeffentlicht" and ig["modus"] == "live"
    assert ig["meta_id"] and ig["meta_link"].startswith("https://www.instagram.com/")
    assert fb["meta_id"] and fb["meta_link"].startswith("https://www.facebook.com/")
    namen = [a[0] for a in meta.aufrufe]
    assert namen.index("ig_veroeffentlichen") < namen.index("fb_foto")
    assert meta.aufrufe[0][1]["image_url"] == "https://cdn/x.jpg"


def test_stopp_instagram_nichts_geht_hinaus_protokoll_nennt_grund(store, settings):
    schalter.setzen(store, "instagram", True, wer="priya", grund="Konto wird geprüft")
    mit_startmarke(store, settings, [post(31)])
    meta = FakeMeta()
    for minuten in (11, 14, 17):
        ablauf.senden(store, settings, meta, START + timedelta(minutes=minuten), bild_url=lambda z: "https://cdn/x.jpg")
    assert meta.aufrufe == []
    ig, fb = zeilen(store, kanal="instagram")[0], zeilen(store, kanal="facebook")[0]
    assert ig["status"] in ("karenz", "geplant") and "Konto wird geprüft" in ig["wartet_grund"]
    assert "Instagram" in fb["wartet_grund"]
    angehalten = repo.aktionen_liste(store, aktion="social_angehalten")
    assert len(angehalten) == 1 and angehalten[0]["kanal"] == "instagram" and "Konto wird geprüft" in angehalten[0]["notiz"]
    schalter.setzen(store, "instagram", False, wer="priya")
    ablauf.senden(store, settings, meta, START + timedelta(minutes=20), bild_url=lambda z: "https://cdn/x.jpg")
    assert {z["status"] for z in zeilen(store) if z["kanal"] != "whatsapp"} == {"veroeffentlicht"}


def test_stopp_alles_haelt_auch_social_an(store, settings):
    schalter.setzen(store, "alles", True, wer="priya", grund="Notfall")
    mit_startmarke(store, settings, [post(32)])
    meta = FakeMeta()
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    assert meta.aufrufe == []


def test_redaktion_stoppt_in_der_karenz(store, settings):
    mit_startmarke(store, settings, [post(33)])
    ig = zeilen(store, kanal="instagram")[0]
    aktionen.stoppen(store, ig["id"], wer="priya", grund="Foto falsch")
    meta = FakeMeta()
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    assert meta.aufrufe == [] and {z["status"] for z in zeilen(store) if z["kanal"] != "whatsapp"} == {"gestoppt"}
    assert repo.aktionen_liste(store, aktion="social_gestoppt")[0]["wer"] == "priya"
    with pytest.raises(ValueError):  # nach der Karenz nicht mehr stoppbar
        aktionen.stoppen(store, ig["id"], wer="priya", grund="zu spät")


def test_text_aendern_nur_in_der_karenz_fuer_beide_kanaele(store, settings):
    mit_startmarke(store, settings, [post(34)])
    ig = zeilen(store, kanal="instagram")[0]
    aktionen.text_aendern(store, ig["id"], "Neuer Text #TamilDE", wer="priya")
    assert {z["text"] for z in zeilen(store) if z["kanal"] != "whatsapp"} == {"Neuer Text #TamilDE"}
    assert repo.aktionen_liste(store, aktion="social_text")[0]["wer"] == "priya"


def test_heikel_von_hand_freigeben_und_verwerfen(store, settings):
    mit_startmarke(store, settings, [post(35, rubrik="news", tags=["Justiz"]), post(36, rubrik="news", tags=["Tod"])])
    meta = FakeMeta()
    ablauf.senden(store, settings, meta, START + timedelta(minutes=30), bild_url=lambda z: "x")
    assert meta.aufrufe == []
    a = zeilen(store, wp_post_id=35, kanal="instagram")[0]
    b = zeilen(store, wp_post_id=36, kanal="facebook")[0]
    with pytest.raises(ValueError):
        aktionen.freigeben(store, a["id"], wer="priya", grund="", jetzt=START)
    aktionen.freigeben(store, a["id"], wer="priya", grund="Urteil ist öffentlich", jetzt=START + timedelta(minutes=30))
    aktionen.verwerfen(store, b["id"], wer="priya", grund="zu heikel")
    assert {z["status"] for z in zeilen(store, wp_post_id=35) if z["kanal"] != "whatsapp"} == {"karenz"}
    assert {z["status"] for z in zeilen(store, wp_post_id=36) if z["kanal"] != "whatsapp"} == {"verworfen"}
    ablauf.senden(store, settings, meta, START + timedelta(minutes=41), bild_url=lambda z: "x")
    assert {z["status"] for z in zeilen(store, wp_post_id=35) if z["kanal"] != "whatsapp"} == {"veroeffentlicht"}
    z = repo.aktionen_liste(store, aktion="social_freigegeben")[0]
    assert z["wer"] == "priya" and z["notiz"] == "Urteil ist öffentlich"


def test_ruhezeit_menge_und_abstand(store, settings):
    nacht = datetime(2026, 11, 16, 22, 30, tzinfo=UTC)  # 23:30 in Berlin
    erkennen(store, settings, FakeWP(), nacht - timedelta(hours=1))
    erkennen(store, settings, FakeWP([post(40, jetzt=nacht), post(41, jetzt=nacht)]), nacht)
    meta = FakeMeta()
    ablauf.senden(store, settings, meta, nacht + timedelta(minutes=11), bild_url=lambda z: "x")
    assert meta.aufrufe == []
    ig = zeilen(store, kanal="instagram")
    assert {z["status"] for z in ig} == {"geplant"} and all("R6" in z["wartet_grund"] for z in ig)
    assert ig[0]["geplant_fuer"] == "2026-11-17T06:00:00+00:00"  # 7 Uhr in Berlin
    morgen = datetime(2026, 11, 17, 6, 0, tzinfo=UTC)
    ablauf.senden(store, settings, meta, morgen, bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")
    assert [z["status"] for z in ig] == ["veroeffentlicht", "geplant"]  # 60 Minuten Abstand je Kanal
    assert "R5" in ig[1]["wartet_grund"] and ig[1]["geplant_fuer"] == "2026-11-17T07:00:00+00:00"
    ablauf.senden(store, settings, meta, morgen + timedelta(minutes=60), bild_url=lambda z: "x")
    assert [z["status"] for z in zeilen(store, kanal="instagram")] == ["veroeffentlicht", "veroeffentlicht"]


def test_hoechstens_sechs_je_tag_und_kanal(store, settings):
    tag = datetime(2026, 11, 16, 6, 0, tzinfo=UTC)
    erkennen(store, settings, FakeWP(), tag - timedelta(hours=1))
    erkennen(store, settings, FakeWP([post(50 + i, jetzt=tag) for i in range(7)]), tag)
    meta = FakeMeta()
    for stunde in range(8):
        ablauf.senden(store, settings, meta, tag + timedelta(minutes=11, hours=stunde), bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")
    assert sum(z["status"] == "veroeffentlicht" for z in ig) == 6
    rest = [z for z in ig if z["status"] == "geplant"][0]
    assert "R5" in rest["wartet_grund"] and rest["geplant_fuer"] == "2026-11-17T06:00:00+00:00"


# ---- Fehler: kein blindes Wiederholen ---------------------------------------------------------------

def test_abbruch_beim_veroeffentlichen_abgleich_findet_den_beitrag(store, settings):
    mit_startmarke(store, settings, [post(60)])
    meta = FakeMeta(abbruch_bei=("ig_veroeffentlichen",), kommt_an=True)
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "unklar"
    ablauf.senden(store, settings, meta, START + timedelta(minutes=14), bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "veroeffentlicht" and ig["meta_link"]
    assert [a[0] for a in meta.aufrufe].count("ig_veroeffentlichen") == 1  # kein zweiter Post
    assert repo.aktionen_liste(store, aktion="social_abgleich")[0]["notiz"].startswith("gefunden")


def test_abbruch_ohne_treffer_geht_an_einen_menschen(store, settings):
    mit_startmarke(store, settings, [post(61)])
    meta = FakeMeta(abbruch_bei=("ig_veroeffentlichen",), kommt_an=False)
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    ablauf.senden(store, settings, meta, START + timedelta(minutes=14), bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "von_hand" and "unklar" in ig["fehler"]
    assert [a[0] for a in meta.aufrufe].count("ig_veroeffentlichen") == 1


def test_zugang_abgelaufen_pausiert_den_kanal_mit_grund(store, settings):
    mit_startmarke(store, settings, [post(62)])
    meta = FakeMeta(fehler={"ig_container": ZugangFehler(190, "Token abgelaufen")})
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "pausiert" and "190" in ig["fehler"]
    sperre = schalter.sperre(store, "instagram")
    assert sperre and "190" in sperre["grund"] and sperre["wer"] == "dienst:social"


def test_container_noch_nicht_fertig_wartet_und_nutzt_ihn_wieder(store, settings):
    mit_startmarke(store, settings, [post(63)])
    meta = FakeMeta(container_status=["IN_PROGRESS", "FINISHED"])
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "geplant" and ig["container_id"]
    ablauf.senden(store, settings, meta, START + timedelta(minutes=13), bild_url=lambda z: "x")
    assert zeilen(store, kanal="instagram")[0]["status"] == "veroeffentlicht"
    assert [a[0] for a in meta.aufrufe].count("ig_container") == 1


def test_facebook_scheitert_nach_instagram_nur_facebook_spaeter(store, settings):
    mit_startmarke(store, settings, [post(64)])
    meta = FakeMeta(abbruch_bei=("fb_foto",), kommt_an=False)
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    ablauf.senden(store, settings, meta, START + timedelta(minutes=14), bild_url=lambda z: "x")
    assert zeilen(store, kanal="instagram")[0]["status"] == "veroeffentlicht"
    assert zeilen(store, kanal="facebook")[0]["status"] == "von_hand"
    assert [a[0] for a in meta.aufrufe].count("ig_veroeffentlichen") == 1


def test_unklar_fehler_ist_eine_ausnahme():
    assert issubclass(UnklarFehler, Exception)


# ---- WhatsApp ------------------------------------------------------------------------------------

def test_whatsapp_als_gepostet_markieren_mit_person_und_zeit(store, settings):
    mit_startmarke(store, settings, [post(70)])
    wa = zeilen(store, kanal="whatsapp")[0]
    aktionen.gepostet(store, wa["id"], wer="priya")
    wa = zeilen(store, kanal="whatsapp")[0]
    assert wa["status"] == "gepostet" and wa["gepostet_von"] == "priya" and wa["gepostet_at"]
    z = repo.aktionen_liste(store, aktion="whatsapp_gepostet")[0]
    assert z["wer"] == "priya" and z["kanal"] == "whatsapp" and z["ts"] and z["ausloeser"] == "person"
    with pytest.raises(ValueError):
        aktionen.gepostet(store, wa["id"], wer="priya")


def test_stopp_whatsapp_blendet_entwuerfe_aus(store, settings):
    mit_startmarke(store, settings, [post(71)])
    assert len(aktionen.ansicht(store)["whatsapp"]) == 1
    schalter.setzen(store, "whatsapp", True, wer="priya", grund="Kanal pausiert")
    assert aktionen.ansicht(store)["whatsapp"] == []


# ---- Dienst ---------------------------------------------------------------------------------------

def test_dienst_plant_social_nur_mit_funktionsschalter(settings):
    assert "social" not in [e.name for e in dienst.plan(settings, env={})]
    e = [e for e in dienst.plan(settings, env={"RADAR_SOCIAL": "an"}) if e.name == "social"][0]
    assert e.args == ("social", "lauf") and e.regel.alle == 180
    assert set(e.kanaele) == {"instagram", "facebook", "whatsapp"}


def test_cli_lauf_ohne_funktionsschalter_tut_nichts(settings, monkeypatch, capsys):
    from news_radar.__main__ import main

    monkeypatch.setenv("RADAR_DATA_DIR", str(settings.data_dir))
    assert main(["social", "lauf"]) == 0
    assert "aus" in capsys.readouterr().out
    assert main(["social", "status"]) == 0
    assert "trocken" in capsys.readouterr().out


# ---- Cockpit --------------------------------------------------------------------------------------

NUTZER = {"anna": ("anna-passwort-1", "admin"), "priya": ("priya-passwort-1", "redaktion"),
          "lena": ("lena-passwort-1", "leser")}


@pytest.fixture
def app(settings, store):
    from news_radar.web import create_app

    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim-geheim", "s3cret"
    for name, (pw, rolle) in NUTZER.items():
        repo.nutzer_anlegen(store, name, pw, rolle)
    jetzt = datetime.now(UTC)
    erkennen(store, settings, FakeWP(), jetzt - timedelta(hours=1))
    erkennen(store, settings, FakeWP([post(80, jetzt=jetzt), post(81, jetzt=jetzt, rubrik="news", tags=["Politik"])]),
             jetzt)
    return create_app(settings, testing=True)


def login(app, user):
    client = app.test_client()
    client.get("/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    assert client.post("/login", data={"user": user, "password": NUTZER[user][0], "_csrf": token}).status_code == 302
    return client, token


def test_cockpit_leser_sieht_nur(app, store):
    client, token = login(app, "lena")
    seite = client.get("/social").get_data(as_text=True)
    assert "Lichterfest im Tempel Hamm" in seite and "Von Hand entscheiden" in seite and "Trockenmodus" in seite
    assert "R2" in seite and "Stoppen" not in seite and "als gepostet markieren" not in seite.lower()
    ig = zeilen(store, wp_post_id=80, kanal="instagram")[0]
    for pfad in (f"/social/{ig['id']}/stoppen", f"/social/{ig['id']}/text", "/social/regelwerk"):
        assert client.post(pfad, data={"_csrf": token, "grund": "x", "text": "x"}).status_code == 403
    assert client.get(f"/social/{ig['id']}/bild").status_code == 200


def test_cockpit_redaktion_stoppt_und_markiert_aber_aendert_kein_regelwerk(app, store):
    client, token = login(app, "priya")
    seite = client.get("/social").get_data(as_text=True)
    assert "Stoppen" in seite and "data-kopieren" in seite and "download" in seite
    ig = zeilen(store, wp_post_id=80, kanal="instagram")[0]
    wa = zeilen(store, wp_post_id=80, kanal="whatsapp")[0]
    assert client.post(f"/social/{ig['id']}/stoppen", data={"_csrf": token, "grund": "Bild prüfen"}).status_code == 302
    assert client.post(f"/social/{wa['id']}/gepostet", data={"_csrf": token}).status_code == 302
    assert zeilen(store, wp_post_id=80, kanal="instagram")[0]["status"] == "gestoppt"
    assert zeilen(store, wp_post_id=80, kanal="whatsapp")[0]["gepostet_von"] == "priya"
    assert client.post("/social/regelwerk", data={"_csrf": token, "max_je_tag": "3"}).status_code == 403


def test_cockpit_admin_aendert_regelwerk(app, store):
    client, token = login(app, "anna")
    assert "Regelwerk ändern" in client.get("/social").get_data(as_text=True)
    resp = client.post("/social/regelwerk", data={"_csrf": token, "max_je_tag": "5", "abstand_min": "60",
                                                   "ruhe_von": "22", "ruhe_bis": "7", "max_alter_stunden": "48",
                                                   "karenz_min": "10", "heikel": "Politik, Justiz",
                                                   "hashtags_news": "#TamilDE #News"})
    assert resp.status_code == 302
    rw = regelwerk.aktuell(store)
    assert rw.fassung == "2" and rw.max_je_tag == 5 and rw.hashtags["news"] == ["#TamilDE", "#News"]
    assert "nicht freigegeben" in client.get("/social").get_data(as_text=True)  # neue Fassung: Freigabe erlischt
    resp = client.post("/social/regelwerk/freigabe", data={"_csrf": token, "freigegeben_von": "KBS über Luis",
                                                           "datum": "2026-11-15", "beleg": "Mail vom 15.11."})
    assert resp.status_code == 302 and regelwerk.freigegeben(regelwerk.aktuell(store))


def test_cockpit_freigabe_des_regelwerks_nur_admin(app, store):
    regelwerk.speichern(store, {"max_je_tag": 5}, wer="anna")
    client, token = login(app, "priya")
    assert "Freigabe eintragen" not in client.get("/social").get_data(as_text=True)
    assert client.post("/social/regelwerk/freigabe", data={"_csrf": token, "freigegeben_von": "KBS",
                                                            "datum": "2026-11-15", "beleg": "x"}).status_code == 403


# ---- Befunde der Code-Prüfung (Regressionen) --------------------------------------------------------

def test_p1_unbekannter_fehler_vor_dem_veroeffentlichen_laesst_nichts_haengen(store, settings):
    mit_startmarke(store, settings, [post(90)])

    def kaputt(zeile):
        raise RuntimeError("WordPress POST media -> 502")

    meta = FakeMeta()
    for minuten in (11, 30, 50):
        ablauf.senden(store, settings, meta, START + timedelta(minutes=minuten), bild_url=kaputt)
        ig = zeilen(store, kanal="instagram")[0]
        assert ig["status"] != "wird_gesendet" and "502" in ig["fehler"]
    assert ig["status"] == "von_hand"  # nach drei Versuchen an einen Menschen, nie endlos
    assert meta.aufrufe == [] and zeilen(store, kanal="facebook")[0]["status"] in ("karenz", "geplant")


def test_p1_fehler_im_veroeffentlichenden_aufruf_wird_unklar(store, settings):
    mit_startmarke(store, settings, [post(91)])
    meta = FakeMeta(fehler={"ig_veroeffentlichen": KeyError("id")})
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    assert zeilen(store, kanal="instagram")[0]["status"] == "unklar"


def test_p1_antwort_ohne_kennung_beim_veroeffentlichen_ist_unklar():
    t, _ = graph((200, {}))
    with pytest.raises(UnklarFehler):
        t.ig_veroeffentlichen("c1")


def test_p1_verwaiste_zeile_wird_abgeglichen(store, settings):
    mit_startmarke(store, settings, [post(92)])
    ig = zeilen(store, kanal="instagram")[0]
    store._write("UPDATE social_beitraege SET status = 'wird_gesendet', modus = 'live', sende_at = ? WHERE id = ?",
                 ((START + timedelta(minutes=11)).isoformat(timespec="seconds"), ig["id"]))
    meta = FakeMeta()
    ablauf.senden(store, settings, meta, START + timedelta(minutes=12), bild_url=lambda z: "x")
    assert zeilen(store, kanal="instagram")[0]["status"] == "wird_gesendet"  # läuft vielleicht noch
    ablauf.senden(store, settings, meta, START + timedelta(minutes=40), bild_url=lambda z: "x")
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "von_hand" and "unklar" in ig["fehler"].lower()
    assert "ig_veroeffentlichen" not in [a[0] for a in meta.aufrufe]  # nie blind wiederholt


def test_p1_verwaiste_zeile_im_trockenmodus_geht_zurueck(store, settings):
    mit_startmarke(store, settings, [post(93)])
    ig = zeilen(store, kanal="instagram")[0]
    store._write("UPDATE social_beitraege SET status = 'wird_gesendet', modus = 'trocken', sende_at = ? WHERE id = ?",
                 ((START + timedelta(minutes=11)).isoformat(timespec="seconds"), ig["id"]))
    ablauf.senden(store, settings, TrockenTransport(), START + timedelta(minutes=40))
    assert zeilen(store, kanal="instagram")[0]["status"] == "trocken"


def test_p2_r3_wird_beim_senden_neu_geprueft(store, settings):
    termin = (START + timedelta(minutes=30)).astimezone(regelwerk.TZ).strftime("%Y-%m-%d %H:%M")
    mit_startmarke(store, settings, [post(94, stunden=47.5), post(95, rubrik="events", event=termin)],
                   vorlauf=timedelta(days=3))
    nacht = START + timedelta(hours=14)  # 23 Uhr: Ruhezeit hält beide bis zum Morgen
    ablauf.senden(store, settings, FakeMeta(), nacht, bild_url=lambda z: "x")
    meta = FakeMeta()
    ablauf.senden(store, settings, meta, datetime(2026, 11, 17, 6, 0, tzinfo=UTC), bild_url=lambda z: "x")
    assert meta.aufrufe == []
    for pid in (94, 95):
        z = zeilen(store, wp_post_id=pid, kanal="instagram")[0]
        assert z["status"] == "von_hand" and "R3" in z["fehler"], pid
        assert json.loads(z["regelpruefung"])["R3"]["ergebnis"] == "verletzt"


def test_p2_von_hand_freigegeben_wird_nicht_erneut_nach_r3_zurueckgeholt(store, settings):
    mit_startmarke(store, settings, [post(96, stunden=50)], vorlauf=timedelta(days=3))
    ig = zeilen(store, kanal="instagram")[0]
    assert ig["status"] == "von_hand"
    aktionen.freigeben(store, ig["id"], wer="priya", grund="trotzdem zeigen", jetzt=START)
    ablauf.senden(store, settings, FakeMeta(), START + timedelta(minutes=11), bild_url=lambda z: "x")
    assert zeilen(store, kanal="instagram")[0]["status"] == "veroeffentlicht"


def test_p2_live_nur_mit_freigabe_des_regelwerks(store, settings):
    regelwerk.speichern(store, {"max_je_tag": 5}, wer="anna")  # neue Fassung: Freigabe erlischt
    assert not regelwerk.freigegeben(regelwerk.aktuell(store))
    mit_startmarke(store, settings, [post(97)])
    meta = FakeMeta()
    stats = ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    assert meta.aufrufe == [] and stats["ohne_freigabe"] == 1
    assert {z["status"] for z in zeilen(store) if z["kanal"] != "whatsapp"} == {"trocken"}
    assert isinstance(ablauf.transport_fuer(konfig.laden(GRAPH_ENV), regelwerk.aktuell(store)), TrockenTransport)
    with pytest.raises(ValueError):
        regelwerk.freigabe_eintragen(store, wer="anna", freigegeben_von="KBS", datum="2026-11-14", beleg="")
    rw = kbs_freigabe(store)
    assert rw.fassung == "2" and regelwerk.freigegeben(rw)
    z = repo.aktionen_liste(store, aktion="social_regelwerk_freigabe")[0]
    assert z["wer"] == "anna" and z["regel_fassung"] == "2" and "Mail von Luis" in z["notiz"]
    with pytest.raises(ValueError):  # einmalig je Fassung
        kbs_freigabe(store)


def test_p3_schalter_website_haelt_den_bild_upload_an(store, settings):
    schalter.setzen(store, "website", True, wer="priya", grund="Theme-Umbau")
    mit_startmarke(store, settings, [post(98)])
    hochgeladen = []
    ablauf.senden(store, settings, FakeMeta(), START + timedelta(minutes=11), bild_url=hochgeladen.append)
    ig = zeilen(store, kanal="instagram")[0]
    assert hochgeladen == [] and ig["status"] in ("karenz", "geplant") and "Theme-Umbau" in ig["wartet_grund"]


def test_p3_bedingter_wechsel_nur_mit_dem_gelesenen_stand(store, settings):
    mit_startmarke(store, settings, [post(99)])
    alt = zeilen(store, kanal="instagram")[0]
    store._write("UPDATE social_beitraege SET text = 'Neuer Text', aktualisiert = '2099-01-01T00:00:00+00:00' "
                 "WHERE wp_post_id = 99 AND kanal != 'whatsapp'")  # Redaktion ändert zwischen Lesen und Senden
    meta = FakeMeta()
    ablauf._eine(store, settings, meta, regelwerk.aktuell(store), alt, START + timedelta(minutes=11), lambda z: "x")
    assert meta.aufrufe == [] and zeilen(store, kanal="instagram")[0]["status"] == "karenz"
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    assert meta.aufrufe[0][1]["caption"] == "Neuer Text"


def test_p3_abgleich_vergleicht_den_link_exakt(store, settings):
    mit_startmarke(store, settings, [post(65)])
    meta = FakeMeta(abbruch_bei=("ig_veroeffentlichen",), kommt_an=False)
    meta.ig_beitraege.append({"id": "m1", "caption": "Mehr auf tamil.de: https://www.tamil.de/beitrag-65/teil-2",
                              "permalink": "https://www.instagram.com/p/m1/"})
    ablauf.senden(store, settings, meta, START + timedelta(minutes=11), bild_url=lambda z: "x")
    ablauf.senden(store, settings, meta, START + timedelta(minutes=14), bild_url=lambda z: "x")
    assert zeilen(store, kanal="instagram")[0]["status"] == "von_hand"


def _jpeg():
    buf = io.BytesIO()
    Image.new("RGB", (800, 600), (10, 80, 140)).save(buf, "JPEG")
    return buf.getvalue()


def test_p3_langer_bildnachweis_wird_gekuerzt_und_haelt_abstand():
    from news_radar.social import bild

    lang = "Foto: " + "Sehr langer Name einer Rechteinhaberin " * 6 + "/ CC BY-SA 4.0"
    text, breite = bild.hinweis_passend(lang)
    assert text.endswith("…") and breite <= bild.HINWEIS_MAX
    assert bild.hinweis_passend("Foto: Tempelverein")[0] == "Foto: Tempelverein"
    daten = bild.foto(_jpeg(), nachweis=lang, ki_hinweis="Symbolbild: KI-generiert")
    assert Image.open(io.BytesIO(daten)).size == (1080, 1350)


def test_p3_angewandte_fassung_beim_senden_im_protokoll(store, settings):
    mit_startmarke(store, settings, [post(100)])
    regelwerk.speichern(store, {"max_je_tag": 5}, wer="anna")
    kbs_freigabe(store)
    ablauf.senden(store, settings, FakeMeta(), START + timedelta(minutes=11), bild_url=lambda z: "x")
    z = repo.aktionen_liste(store, aktion="social_senden", kanal="instagram")[0]
    assert z["regel_fassung"] == "2" and "Fassung 1" in z["notiz"]


def test_p3_fehler_beim_erkennen_haelt_das_senden_nicht_auf(store, settings):
    mit_startmarke(store, settings, [post(101)])

    def kaputt(params):
        raise RuntimeError("WordPress nicht erreichbar")

    stats = ablauf.lauf(store, settings, konfig.laden({}), START + timedelta(minutes=11), abruf=kaputt,
                        transport=TrockenTransport())
    assert stats["erkennen_fehler"] == 1 and stats["trocken"] == 2


# ---- GraphTransport mit nachgestellter Session (kein Netz) ---------------------------------------

GRAPH_ENV = {"RADAR_SOCIAL_LIVE": "an", "META_ZUGANG": "GEHEIMES-TOKEN-123", "META_IG_USER_ID": "1784",
             "META_PAGE_ID": "4242"}


class FakeAntwort:
    def __init__(self, code, daten):
        self.status_code, self._daten = code, daten

    def json(self):
        return self._daten


class FakeSession:
    """requests.Session-Ersatz: liefert der Reihe nach Antworten oder wirft Ausnahmen; merkt sich jeden Aufruf."""

    def __init__(self, antworten):
        self.antworten = list(antworten)
        self.aufrufe = []
        self.headers = {}

    def _naechste(self, methode, url, **kw):
        self.aufrufe.append((methode, url, kw))
        a = self.antworten.pop(0)
        if isinstance(a, Exception):
            raise a
        return FakeAntwort(*a)

    def get(self, url, **kw):
        return self._naechste("GET", url, **kw)

    def post(self, url, **kw):
        return self._naechste("POST", url, **kw)


def graph(*antworten):
    from news_radar.social.transport import GraphTransport

    s = FakeSession(antworten)
    return GraphTransport(konfig.laden(GRAPH_ENV), session=s), s


def meta_fehler(code):
    return (400, {"error": {"code": code, "message": "Fehler von Meta", "type": "OAuthException"}})


@pytest.mark.parametrize("code, klasse", [(190, "ZugangFehler"), (368, "ZugangFehler"), (4, "WarteFehler"),
                                          (17, "WarteFehler"), (100, "MetaFehler")])
def test_graph_fehlercodes(code, klasse):
    from news_radar.social import transport

    t, _ = graph(meta_fehler(code))
    with pytest.raises(getattr(transport, klasse)) as exc:
        t.ig_container("https://x/b.jpg", "Text", "Alt")
    assert type(exc.value).__name__ == klasse and "GEHEIMES-TOKEN-123" not in str(exc.value)


def test_graph_429_heisst_warten():
    from news_radar.social.transport import WarteFehler

    t, _ = graph((429, {}))
    with pytest.raises(WarteFehler):
        t.fb_letzte()


def _abbrueche():
    import requests

    return [requests.Timeout("zu lange"), (502, {}), requests.exceptions.ChunkedEncodingError("abgebrochen")]


@pytest.mark.parametrize("nr", range(3))
@pytest.mark.parametrize("aufruf", ["ig", "fb"])
def test_graph_abbruch_beim_veroeffentlichen_ist_unklar(nr, aufruf):
    t, _ = graph(_abbrueche()[nr])
    with pytest.raises(UnklarFehler) as exc:
        if aufruf == "ig":
            t.ig_veroeffentlichen("c1")
        else:
            t.fb_foto("https://x/b.jpg", "Text", "Alt")
    assert "GEHEIMES-TOKEN-123" not in str(exc.value)


def test_graph_netzfehler_vor_dem_veroeffentlichen_heisst_warten():
    import requests

    from news_radar.social.transport import WarteFehler

    t, _ = graph(requests.ConnectionError("weg"))
    with pytest.raises(WarteFehler):
        t.ig_container("https://x/b.jpg", "Text", "Alt")


def test_graph_ablauf_und_token_nur_im_aufruf(store, settings):
    t, s = graph((200, {"id": "c1"}), (200, {"status_code": "FINISHED"}),
                 (200, {"data": [{"quota_usage": 1, "config": {"quota_total": 100}}]}), (200, {"id": "m1"}),
                 (200, {"permalink": "https://www.instagram.com/p/m1/"}),
                 (200, {"id": "f1", "post_id": "4242_9"}), (200, {"permalink_url": "https://www.facebook.com/4242_9"}))
    mit_startmarke(store, settings, [post(102)])
    ablauf.senden(store, settings, t, START + timedelta(minutes=11), bild_url=lambda z: "https://cdn/x.jpg")
    ig, fb = zeilen(store, kanal="instagram")[0], zeilen(store, kanal="facebook")[0]
    assert (ig["meta_id"], ig["meta_link"]) == ("m1", "https://www.instagram.com/p/m1/")
    assert (fb["meta_id"], fb["meta_link"]) == ("4242_9", "https://www.facebook.com/4242_9")
    pfade = [(m, u.split("/v23.0/")[1]) for m, u, _ in s.aufrufe]
    assert pfade == [("POST", "1784/media"), ("GET", "c1"), ("GET", "1784/content_publishing_limit"),
                     ("POST", "1784/media_publish"), ("GET", "m1"), ("POST", "4242/photos"), ("GET", "4242_9")]
    gespeichert = " ".join(str(v) for z in zeilen(store) for v in z.values())
    protokoll = " ".join(str(v) for z in repo.aktionen_liste(store) for v in z.values())
    assert "GEHEIMES-TOKEN-123" not in gespeichert + protokoll
