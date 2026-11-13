"""Befunde der unabhängigen Prüfung des Eingangs (F1): Erfindungsschutz, Kontaktdaten im Freitext, Bildweg mit
Lizenz-Datensatz, robuste Abholung und feindliche Einsendungen. Alle Personendaten erfunden (example.test)."""

import io
import json

import pytest
from PIL import Image

from news_radar import eingang, lizenz
from news_radar.abnahme.wp_eingang import Antwort, FakeWordPressEingang
from news_radar.store import Store
from news_radar.workflow.fake import FakeAnthropic

from test_eingang import EVENT, JETZT, abholen_und_vorbereiten, claude, client, settings, store, wp  # noqa: F401

GEGENBEISPIELE = ["Eintritt 18 Euro", "Kinder 1 Euro", "Freitag, 16. Juni", "fünfhundert Gäste werden erwartet",
                  "Infos auf testverein-essen.de", "Das Fest findet in der Zeche Zollverein in Gelsenkirchen statt",
                  "Es spricht Dr. Kumar Rajan", "Anmeldung: info [at] testverein punkt de",
                  # Gegenprüfung: Positivliste statt Negativliste
                  "Der Eintritt ist frei.", "Eintritt gratis.", "Für Kinder kostenlos.", "Das Fest ist ausverkauft.",
                  "Das Fest findet heute statt", "Wir treffen uns morgen abend", "am dritten advent",
                  "Das zehnte Fest.", "Wir feiern Pongal in köln.", "Es singt குமார் ராஜன்.",
                  "Infos auf testverein-essen.nl", "Treffpunkt ist gelsenkirchen", "es spricht kumar rajan",
                  "am elf uhr", "erste Ausgabe"]


def _einsendung(**felder):
    return {"art": "event", "felder": {**EVENT, **felder}}


def modell_antwort(**ueber):
    def antwort(user, system, req):
        out = {"zusammenfassung": "Pongal-Fest Testverein in Essen", "titel": "Pongal-Fest Testverein in Essen",
               "teaser": "Tanz, Musik und Essen.", "absaetze": ["Alle Familien sind willkommen."]}
        out.update(ueber)
        return out
    return antwort


# ---- P1: Erfindungsschutz ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("text", GEGENBEISPIELE)
def test_gegenbeispiele_gelten_als_erfunden(text):
    assert eingang.fremde_angaben([text], eingang.erlaubter_text(_einsendung())), text


def test_angaben_aus_der_einsendung_sind_erlaubt():
    erlaubt = eingang.erlaubter_text(_einsendung())
    texte = ["Pongal-Fest Testverein in Essen am Samstag, 16. Januar 2027, 18:30 Uhr.",
             "Testverein e. V.: 10 Euro, Kinder frei.", "TANZ und musik – alle familien sind willkommen.",
             "Tanz, Musik und Essen im Gemeindesaal, Beispielstraße 1."]
    assert eingang.fremde_angaben(texte, erlaubt) == []
    assert eingang.fremde_angaben(["9" * 5000], erlaubt)  # sehr lange Ziffernfolge: als Text, ohne int()


@pytest.mark.parametrize("text", GEGENBEISPIELE)
def test_modelltext_mit_erfundenem_wird_verworfen(settings, store, wp, text):
    wp.einreichen("event", EVENT)
    fake = FakeAnthropic({"eingang": modell_antwort(absaetze=[f"Alle Familien sind willkommen. {text}."])})
    abholen_und_vorbereiten(store, wp, claude(settings, store, fake))
    e = eingang.liste(store)[0]
    assert e["modell_vorschlag"] is None and e["entwurf"]["quelle"] == "regeln"
    assert any(h.startswith("Modell-Entwurf verworfen") for h in e["hinweise"])
    assert text not in json.dumps(e, ensure_ascii=False)


def test_formular_immer_aus_den_feldern_modell_nur_auf_klick(settings, store, wp):
    v = wp.einreichen("event", EVENT)
    fake = FakeAnthropic({"eingang": modell_antwort()})
    abholen_und_vorbereiten(store, wp, claude(settings, store, fake))
    e = eingang.holen(store, v)
    assert e["entwurf"] == {"titel": EVENT["titel"], "teaser": "Tanz, Musik und Essen.",
                            "absaetze": [EVENT["beschreibung"]], "quelle": "regeln"}
    assert e["modell_vorschlag"]["titel"] == "Pongal-Fest Testverein in Essen"
    did = eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={})
    assert store.get_draft(did)["titel"] == EVENT["titel"]  # ohne Klick gilt der Entwurf aus den Feldern


def test_vorschlag_des_modells_nur_ausdruecklich(settings, store, wp):
    v = wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp, claude(settings, store, FakeAnthropic({"eingang": modell_antwort()})))
    did = eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={"vorlage": "modell"})
    d = store.get_draft(did)
    assert d["titel"] == "Pongal-Fest Testverein in Essen" and "Alle Familien" in d["inhalt_html"]
    assert eingang.VERMERK in d["hinweise"]


def test_ohne_vorschlag_kein_modell_uebernehmen(settings, store, wp):
    v = wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp)
    with pytest.raises(ValueError):
        eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={"vorlage": "modell"})


# ---- P2: Kontaktdaten im Freitext --------------------------------------------------------------------------------

def test_kontaktdaten_im_freitext_maskiert_und_markiert(settings, store, wp):
    text = "Infos bei erika@example.test oder 0171 2345678. Beginn am 16.01.2027."
    wp.einreichen("event", {**EVENT, "beschreibung": text})
    fake = FakeAnthropic()
    abholen_und_vorbereiten(store, wp, claude(settings, store, fake))
    prompt = fake.requests[0]["user"]
    assert "erika@example.test" not in prompt and "2345678" not in prompt
    assert "[E-Mail]" in prompt and "[Telefon]" in prompt and "16.01.2027" in prompt
    assert "Kontaktdaten im Text" in eingang.liste(store)[0]["hinweise"]


# ---- P2: Bildweg -------------------------------------------------------------------------------------------------

def bild(fmt="PNG", groesse=(300, 200), exif=False) -> bytes:
    img = Image.new("RGB", groesse, (180, 40, 42))
    buf = io.BytesIO()
    if exif:
        ex = Image.Exif()
        ex[0x010F] = "Kamerahersteller"  # Make
        ex[0x8825] = {2: (52.0, 31.0, 0.0)}  # GPS
        img.save(buf, fmt, exif=ex)
    else:
        img.save(buf, fmt)
    return buf.getvalue()


def uebernommen(settings, store, wp, **einreichen):
    v = wp.einreichen("event", EVENT, **einreichen)
    abholen_und_vorbereiten(store, wp)
    return store.get_draft(eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={})), v


def test_bild_mit_recht_wird_neu_gespeichert_mit_lizenz_datensatz(settings, store, wp):
    d, v = uebernommen(settings, store, wp, bild=bild("JPEG", (3000, 1000), exif=True), bild_typ="image/jpeg")
    assert d["bild_datei"] == f"einsendung-{v.lower()}.jpg"
    with Image.open(settings.bilder_dir / d["bild_datei"]) as img:
        assert img.format == "JPEG" and img.size == (2400, 800)
        assert not img.getexif() and "exif" not in img.info
    asset = lizenz.asset_fuer(store, d)
    assert asset["lizenz_kuerzel"] == "nutzungsrecht" and lizenz.umfang_menge(asset["umfang"]) == {"website"}
    assert "Bestätigung im Formular" in asset["beleg"] and "Fassung KBS-Entwurf 1" in asset["beleg"]
    assert asset["geprueft_von"] == "priya" and "Erika" not in json.dumps(asset, ensure_ascii=False)
    assert lizenz.sperre(store, d, settings) == ""  # die Freigabe sperrt das Bild nicht


@pytest.mark.parametrize("fall", ["recht", "pruefsumme", "typ", "gif", "gross", "bombe"])
def test_bild_wird_abgewiesen(settings, store, wp, monkeypatch, fall):
    kw = {"bild": bild()}
    if fall == "recht":
        kw["bild_recht"] = False
    elif fall == "typ":
        kw["bild_typ"] = "image/gif"
    elif fall == "gif":
        kw["bild"] = bild("GIF")  # behauptet PNG, ist GIF
    elif fall == "gross":
        monkeypatch.setattr(eingang, "BILD_MAX", 100)
    elif fall == "bombe":
        monkeypatch.setattr(eingang, "BILD_MAX_PIXEL", 10_000)  # 300×200 liegt darüber
    if fall == "pruefsumme":
        v = wp.einreichen("event", EVENT, **kw)
        wp.zeile(v)["bild"]["sha256"] = "0" * 64
        abholen_und_vorbereiten(store, wp)
        d = store.get_draft(eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={}))
    else:
        d, v = uebernommen(settings, store, wp, **kw)
    assert not d["bild_datei"]
    assert any(h.startswith("Bild der Einsendung nicht übernommen") for h in d["hinweise"])
    assert not list(settings.bilder_dir.glob("einsendung-*")) if settings.bilder_dir.exists() else True


def test_bilddatei_wird_entfernt_wenn_der_entwurf_scheitert(settings, store, wp, monkeypatch):
    v = wp.einreichen("event", EVENT, bild=bild())
    abholen_und_vorbereiten(store, wp)

    def kaputt(row):
        raise RuntimeError("Datenbank voll")
    monkeypatch.setattr(store, "insert_draft", kaputt)
    with pytest.raises(RuntimeError):
        eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={})
    assert not list(settings.bilder_dir.glob("einsendung-*"))
    assert eingang.holen(store, v)["status"] == "vorbereitet"


# ---- P3 ----------------------------------------------------------------------------------------------------------

def test_fehlertext_des_clients_ohne_personendaten():
    class Session:
        auth, headers = None, {}

        def request(self, method, url, **kw):
            return Antwort(500, {"code": "kaputt", "name": "Erika Beispiel", "email": "erika@example.test"})

    from news_radar.wordpress import TamilRadarClient

    c = TamilRadarClient("https://www.tamil.test", "u", "p", session=Session())
    for aufruf in (lambda: c.einsendungen(0), lambda: c.einsendung("T261113-K7M3Q"),
                   lambda: c.einsendung_status("T261113-K7M3Q", "erledigt"), lambda: c.einsendung_bild("T261113-K7M3Q")):
        with pytest.raises(RuntimeError) as fehler:
            aufruf()
        assert "Erika" not in str(fehler.value) and "example.test" not in str(fehler.value)
        assert "500" in str(fehler.value)


def test_kaputte_zeile_blockiert_den_cursor_nicht(store, wp):
    wp.einreichen("kontakt", {"nachricht": "Erste"})
    wp.zeilen.append({**wp.zeilen[0], "id": 2, "vorgangsnummer": "T261113-ZZZZZ", "felder": "kaputt", "eingang_at": 7,
                      "einwilligung_fassung": {"x": 1}})
    wp.zeilen.append({**wp.zeilen[0], "id": 3, "vorgangsnummer": "T261113-YYYYY",
                      "bild": {"typ": "image/png", "groesse": "viel"}})
    wp.einreichen("kontakt", {"nachricht": "Vierte"})
    out = eingang.abholen(store, client(wp))
    assert out["neu"] == 2 and out["kaputt"] == 2
    assert eingang._cursor(store) == 4
    assert eingang.abholen(store, client(wp))["neu"] == 0


def test_dauerhafte_ablehnung_wird_vermerkt_und_nicht_wiederholt(settings, store, wp):
    v = wp.einreichen("kontakt", {"nachricht": "Hallo"})
    abholen_und_vorbereiten(store, wp)
    wp.status_antwort[v] = (400, {"code": "tamil_einsendung_status", "message": "x", "data": {"status": 400}})
    eingang.abschliessen(store, v, "erledigt", von="priya", client=client(wp))
    e = eingang.holen(store, v)
    assert e["wp_status"] == "abgewiesen" and any("HTTP 400" in h for h in e["hinweise"])
    vorher = len(wp.aufrufe)
    eingang.melden(store, client(wp))
    assert len(wp.aufrufe) == vorher


def test_event_datum_muss_ortszeit_im_format_sein(settings, store, wp):
    v = wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp)
    with pytest.raises(ValueError):
        eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={"event_datum": "morgen"})
    assert eingang.holen(store, v)["status"] == "vorbereitet"


def test_feindliche_einsendung(settings, store, wp):
    from news_radar.web import create_app
    from news_radar.workflow import repo

    v = wp.einreichen("event", {**EVENT, "titel": "<script>alert(1)</script>Fest",
                                "beschreibung": "<img src=x onerror=alert(1)> Tanz", "ticket_link": "javascript:alert(1)"},
                      email="a@b.c?bcc=x")
    abholen_und_vorbereiten(store, wp)
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim-geheim", "s3cret"
    repo.nutzer_anlegen(store, "priya", "priya-passwort-1", "redaktion")
    app = create_app(settings, testing=True)
    c = app.test_client()
    c.get("/login")
    with c.session_transaction() as s:
        token = s["csrf"]
    c.post("/login", data={"user": "priya", "password": "priya-passwort-1", "_csrf": token})
    seite = c.get(f"/eingang/{v}").get_data(as_text=True)
    assert "<script>alert" not in seite and "<img src=x" not in seite
    assert 'href="javascript:' not in seite and "mailto:" not in seite
    r = c.post(f"/eingang/{v}/uebernehmen", data={"_csrf": token, "event_datum": "nicht-ein-datum"})
    assert r.status_code == 400
    d = store.get_draft(eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={}))
    assert "<script" not in d["inhalt_html"] and "<img" not in d["inhalt_html"] and d["ticket_url"] == ""


def test_loeschfrist_fuer_eintraege_die_auf_der_website_fehlen(store, wp):
    from datetime import datetime, timedelta, timezone

    v = wp.einreichen("kontakt", {"nachricht": "Hallo"})
    abholen_und_vorbereiten(store, wp)
    alt = (datetime.now(timezone.utc) - timedelta(days=eingang.FEHLT_TAGE + 1)).isoformat(timespec="seconds")
    store._write("UPDATE einsendungen SET wp_status = 'fehlt', aktualisiert = ? WHERE vorgangsnummer = ?", (alt, v))
    assert eingang.loeschen(store)["fehlt"] == 1 and eingang.holen(store, v) is None


def test_cockpit_formular_aus_feldern_vorschlag_nur_per_knopf(settings, store, wp):
    from news_radar.web import create_app
    from news_radar.workflow import repo

    v = wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp, claude(settings, store, FakeAnthropic({"eingang": modell_antwort()})))
    settings.web_user, settings.web_password, settings.web_secret = "luis", "geheim-geheim", "s3cret"
    repo.nutzer_anlegen(store, "priya", "priya-passwort-1", "redaktion")
    app = create_app(settings, testing=True)
    app.extensions["eingang_client"] = client(wp)
    c = app.test_client()
    c.get("/login")
    with c.session_transaction() as s:
        token = s["csrf"]
    c.post("/login", data={"user": "priya", "password": "priya-passwort-1", "_csrf": token})
    seite = c.get(f"/eingang/{v}").get_data(as_text=True)
    formular = seite.split("Als Entwurf übernehmen</button>")[0]
    assert f'name="titel" value="{EVENT["titel"]}"' in formular  # vorbelegt aus den Feldern
    assert "Vorschlag des Agenten" in seite and 'name="vorlage" value="modell"' in seite
    r = c.post(f"/eingang/{v}/uebernehmen", data={"_csrf": token, "vorlage": "modell"})
    assert r.status_code == 302
    assert store.list_drafts("neu")[0]["titel"] == "Pongal-Fest Testverein in Essen"


# ---- Gegenprüfung ------------------------------------------------------------------------------------------------

def test_vorschlag_wird_markiert_statt_behauptet(settings, store, wp):
    erlaubt = eingang.erlaubter_text(_einsendung())
    html = str(eingang.markieren("Tanz in köln <b>", erlaubt))
    assert '<mark title="nicht in der Einsendung">köln</mark>' in html and "&lt;b&gt;" in html
    assert "<mark" not in str(eingang.markieren("Tanz, Musik und Essen.", erlaubt))
    from pathlib import Path

    vorlage = (Path(eingang.__file__).parent / "web/templates/einsendung.html").read_text(encoding="utf-8")
    assert "steht in der Einsendung; sonst" not in vorlage


def test_alte_zeile_mit_modell_entwurf_nimmt_den_entwurf_aus_den_feldern(store, wp):
    v = wp.einreichen("event", EVENT)
    abholen_und_vorbereiten(store, wp)
    alt = {"titel": "Erfundener Titel", "teaser": "x", "absaetze": ["Rund 500 Gäste"], "quelle": "modell"}
    store._write("UPDATE einsendungen SET entwurf = ? WHERE vorgangsnummer = ?", (json.dumps(alt), v))
    e = eingang.holen(store, v)
    assert e["entwurf"]["quelle"] == "regeln" and e["entwurf"]["titel"] == EVENT["titel"]
    assert e["modell_vorschlag"] is None


def test_migration_12_holt_social_und_lizenz_nach(tmp_path, monkeypatch):
    from news_radar.workflow import schema

    pfad = tmp_path / "alt.sqlite"
    monkeypatch.setattr(schema, "MIGRATIONS", {k: v for k, v in schema.MIGRATIONS.items() if k not in (8, 9, 12)})
    Store(pfad).close()  # Stand 5aab944: V11 ohne V8 und V9
    monkeypatch.undo()
    with Store(pfad) as st:
        assert st.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST >= 12
        tabellen = {r[0] for r in st.db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        assert {"social_beitraege", "social_stand", "social_regelwerk", "einsendungen"} <= tabellen
        assert {"lizenz_kuerzel", "beleg", "geprueft_von"} <= {r[1] for r in st.db.execute("PRAGMA table_info(assets)")}
    assert 10 not in schema.MIGRATIONS
    with Store(tmp_path / "neu.sqlite") as st:  # frisch: V8, V9, V11 und V12 laufen durch, ohne Fehler
        assert st.db.execute("PRAGMA user_version").fetchone()[0] == schema.LATEST


def test_entwurf_wird_entfernt_wenn_der_lizenzdatensatz_scheitert(settings, store, wp, monkeypatch):
    v = wp.einreichen("event", EVENT, bild=bild())
    abholen_und_vorbereiten(store, wp)

    def kaputt(*a, **kw):
        raise RuntimeError("Lizenz nicht gespeichert")
    monkeypatch.setattr(lizenz, "anlegen", kaputt)
    with pytest.raises(RuntimeError):
        eingang.uebernehmen(store, settings, v, von="priya", client=client(wp), felder={})
    assert store.list_drafts() == [] and not list(settings.bilder_dir.glob("einsendung-*"))
    assert store.db.execute("SELECT COUNT(*) FROM assets").fetchone()[0] == 0
    assert eingang.holen(store, v)["status"] == "vorbereitet"


def test_bild_wird_nach_exif_ausrichtung_gedreht():
    img = Image.new("RGB", (300, 200), (180, 40, 42))
    ex = Image.Exif()
    ex[0x0112] = 6  # Orientation: um 90° drehen
    buf = io.BytesIO()
    img.save(buf, "JPEG", exif=ex)
    neu = eingang.bild_neu_speichern(buf.getvalue())
    with Image.open(io.BytesIO(neu)) as jetzt:
        assert jetzt.size == (200, 300) and not jetzt.getexif()
    assert eingang.BILD_MAX_PIXEL == 25_000_000


def test_maskierung_ort_bleibt_handles_und_at_punkt_werden_maskiert():
    e = {"art": "event", "felder": {**EVENT, "ort": "Gemeindesaal, Beispielstraße 1, 45127 Essen",
                                    "beschreibung": "Ruf an: 0201 12345. Code 1234567. Folgt @testverein_essen "
                                                    "oder schreibt info at testverein punkt de."}}
    felder, gefunden = eingang.felder_maskiert(e)
    assert gefunden and felder["ort"] == "Gemeindesaal, Beispielstraße 1, 45127 Essen"
    b = felder["beschreibung"]
    assert "[Telefon]" in b and "0201" not in b and "1234567" in b  # 7 Ziffern ohne Vorwahl bleiben
    assert "@testverein_essen" not in b and "testverein punkt de" not in b
