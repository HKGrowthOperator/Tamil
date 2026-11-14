"""Betrieb: Sicherung und Wiederherstellung (Roundtrip), Wochenbericht, Tageszusammenfassung mit Kosten."""

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from news_radar import notify, sicherung
from news_radar.config import load_settings
from news_radar.images import branded_card, save_pair
from news_radar.store import Store
from news_radar.workflow import jobs, repo
from news_radar.workflow.providers import usage_protokollieren

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def settings(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTIFY_WEBHOOK_URL", "")
    s = load_settings()
    s.data_dir = tmp_path / "data"
    return s


def test_backup_restore_roundtrip_keeps_previous_state(settings, tmp_path):
    with Store(settings.db_path) as store:
        store.insert_draft(dict(uid="a", titel="Vor dem Backup"))
        repo.story_anlegen(store, typ="news", titel="Story")
        save_pair(branded_card("Bild", "Kino", "x"), settings.bilder_dir, "x")
    out = sicherung.erstellen(settings.data_dir, tmp_path / "backup", stamp="2026-11-08")
    assert out["datenbank"].exists() and out["bilder"].exists()
    with Store(settings.db_path) as store:  # danach geht etwas schief
        store.insert_draft(dict(uid="b", titel="Nach dem Backup"))
    (settings.bilder_dir / "x.jpg").unlink()
    info = sicherung.wiederherstellen(settings.data_dir, tmp_path / "backup", "2026-11-08")
    assert info["integritaet"] == "ok" and info["drafts"] == 1 and info["stories"] == 1
    with Store(settings.db_path) as store:
        assert [d["titel"] for d in store.list_drafts()] == ["Vor dem Backup"]
    assert (settings.bilder_dir / "x.jpg").exists()
    assert list(settings.data_dir.glob("radar.sqlite.vor-restore-*")) and list(settings.data_dir.glob("bilder.vor-restore-*"))
    kaputt = tmp_path / "backup" / "radar-2026-11-09.sqlite"
    kaputt.write_bytes(b"kein sqlite")
    with pytest.raises(Exception):
        sicherung.pruefen(kaputt)


def test_restore_script_runs_without_systemctl(settings, tmp_path):
    with Store(settings.db_path) as store:
        store.insert_draft(dict(uid="a", titel="Gesichert"))
    sicherung.erstellen(settings.data_dir, tmp_path / "backup", stamp="2026-11-08")
    env = {**os.environ, "APP": str(ROOT), "DEST": str(tmp_path / "backup"), "PY": "python", "OHNE_SYSTEMCTL": "1",
           "RADAR_DATA_DIR_TEST": str(settings.data_dir)}
    pruefen = subprocess.run(["python", "-m", "news_radar", "sicherung", "pruefen", "--ziel", str(tmp_path / "backup"),
                              "--datum", "2026-11-08"], cwd=ROOT, env=env, capture_output=True, text=True)
    assert pruefen.returncode == 0 and "'integritaet': 'ok'" in pruefen.stdout
    assert subprocess.run(["bash", "-n", str(ROOT / "deploy" / "restore.sh")]).returncode == 0
    assert subprocess.run(["bash", "-n", str(ROOT / "deploy" / "backup.sh")]).returncode == 0


def test_weekly_report_and_digest_include_costs_and_problems(settings):
    with Store(settings.db_path) as store:
        sid = repo.story_anlegen(store, typ="news", titel="Story", status="recherche_erforderlich")
        a = store.insert_draft(dict(uid="a", titel="A", story_id=sid))
        b = store.insert_draft(dict(uid="b", titel="B"))
        store.set_status(a, "freigeben")
        store.set_status(b, "ablehnen")
        usage_protokollieren(store, rolle="text", modell="claude-sonnet-5-5", usd=0.12, story_id=sid)
        usage_protokollieren(store, rolle="recherche", modell="claude-sonnet-5-5", status="fehler", fehler="429")
        j = jobs.einreihen(store, sid, "recherche")
        store.db.execute("UPDATE workflow_jobs SET status = 'tot' WHERE id = ?", (j,))
        store.db.commit()
        text = repo.wochenbericht_text(store)
        digest = notify.digest(settings, store)
    assert "Annahmequote 50%" in text and "$0.12" in text and "1 abgebrochene Jobs" in text
    assert "Kosten" in digest and "in Nachrecherche" in digest and "abgebrochene Jobs" in digest


def test_blind_comparison_sheet_hides_models_and_evaluates(settings, tmp_path):
    import csv

    from news_radar import bewertung
    from news_radar.sources import NewsItem
    from news_radar.workflow import orchestrator
    from news_radar.workflow.fake import FakeAnthropic
    from datetime import datetime, timezone

    text = ("Die tamilische Gemeinde in Hamm feiert am Samstag, 14. November, ihr Lichterfest im Tempel. "
            "Erwartet werden rund 3000 Besucherinnen und Besucher aus ganz Deutschland. "
            "Die Feier beginnt um 10 Uhr mit einer Prozession, der Eintritt ist frei. "
            "Veranstalter ist der Tempelverein, der seit 2002 in Hamm aktiv ist und jedes Jahr einlädt.")
    item = NewsItem(title="Tamilisches Lichterfest im Tempel Hamm", url="https://rn.example/l", summary="Fest",
                    source="RN", published=datetime.now(timezone.utc))
    with Store(settings.db_path) as store:
        ctx = orchestrator.kontext(settings, store, client=FakeAnthropic(), fetch_text=lambda u: text, suche=lambda q: [])
        orchestrator.scan(ctx, [item])
        orchestrator.abarbeiten(ctx)
        out = bewertung.vergleich(ctx, tmp_path / "bw", anzahl=5, seed=1)
        modelle = [r["kwargs"]["model"] for r in ctx.claude.client.requests if r["rolle"] == "text"][-2:]
    assert out["fassungen"] == 2 and sorted(modelle) == ["claude-opus-5-5", "claude-sonnet-5-5"]
    zeilen = list(csv.DictReader((tmp_path / "bw" / "bogen.csv").open(encoding="utf-8-sig"), delimiter=";"))
    assert "claude" not in (tmp_path / "bw" / "bogen.csv").read_text(encoding="utf-8-sig")
    for z in zeilen:
        z.update(richtigkeit_1_5="4" if z["fassung"] == "A" else "2", stil_1_5="3", verstaendlichkeit_1_5="5",
                 wuerde_freigeben_ja_nein="ja" if z["fassung"] == "A" else "nein")
    with (tmp_path / "bw" / "bogen.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(zeilen[0]), delimiter=";")
        w.writeheader()
        w.writerows(zeilen)
    werte = bewertung.auswerten(tmp_path / "bw" / "bogen.csv", tmp_path / "bw" / "schluessel.json")
    assert sorted(w["richtigkeit"] for w in werte.values()) == [2.0, 4.0]


# ---- Review 2: WAL-sichere Kopie, nur bilder/ aus dem Archiv, Stand prüfen ---------------------------------------

def test_restore_keeps_wal_data_in_safety_copy_and_only_extracts_images(settings, tmp_path):
    import io
    import sqlite3
    import tarfile

    with Store(settings.db_path) as store:
        store.insert_draft(dict(uid="a", titel="Gesichert"))
    sicherung.erstellen(settings.data_dir, tmp_path / "backup", stamp="2026-11-08")
    offen = sqlite3.connect(settings.db_path)  # Schreiber, dessen Daten noch im WAL stehen
    offen.execute("PRAGMA wal_autocheckpoint = 0")
    offen.execute("INSERT INTO drafts (uid, titel, status, typ, created_at, updated_at) VALUES ('w', 'Nur im WAL', 'neu', "
                  "'artikel', '2026-11-09', '2026-11-09')")
    offen.commit()
    try:
        tgz = tmp_path / "backup" / "bilder-2026-11-08.tgz"  # manipuliertes Archiv: will radar.sqlite überschreiben
        with tarfile.open(tgz, "w:gz") as tar:
            for name, daten in (("bilder/ok.jpg", b"jpg"), ("radar.sqlite", b"boese"), ("../../ausbruch.txt", b"x")):
                info = tarfile.TarInfo(name)
                info.size = len(daten)
                tar.addfile(info, io.BytesIO(daten))
        sicherung.wiederherstellen(settings.data_dir, tmp_path / "backup", "2026-11-08")
    finally:
        offen.close()
    vorher = next(settings.data_dir.glob("radar.sqlite.vor-restore-*"))
    titel = {r[0] for r in sqlite3.connect(vorher).execute("SELECT titel FROM drafts")}
    assert "Nur im WAL" in titel  # früher: nur die Hauptdatei kopiert, WAL-Inhalt verloren
    with Store(settings.db_path) as store:
        assert [d["titel"] for d in store.list_drafts()] == ["Gesichert"]
    assert (settings.bilder_dir / "ok.jpg").read_bytes() == b"jpg"
    assert not (tmp_path / "ausbruch.txt").exists() and not list(settings.data_dir.glob("bilder.restore-*"))


def test_broken_image_archive_changes_nothing(settings, tmp_path):
    with Store(settings.db_path) as store:
        store.insert_draft(dict(uid="a", titel="Gesichert"))
    save_pair(branded_card("Bild", "Kino", "x"), settings.bilder_dir, "x")
    sicherung.erstellen(settings.data_dir, tmp_path / "backup", stamp="2026-11-08")
    with Store(settings.db_path) as store:
        store.insert_draft(dict(uid="b", titel="Danach"))
    (tmp_path / "backup" / "bilder-2026-11-08.tgz").write_bytes(b"kein archiv")
    with pytest.raises(Exception):
        sicherung.wiederherstellen(settings.data_dir, tmp_path / "backup", "2026-11-08")
    with Store(settings.db_path) as store:
        assert len(store.list_drafts()) == 2  # Datenbank unverändert
    assert (settings.bilder_dir / "x.jpg").exists() and not list(settings.data_dir.glob("bilder.restore-*"))


def test_stand_is_validated_and_cleanup_keeps_foreign_files(settings, tmp_path):
    for falsch in ("../2026-11-08", "2026-11-08/../x", "*", "2026-13-01", ""):
        with pytest.raises(ValueError):
            sicherung.stand(falsch)
    ziel = tmp_path / "backup"
    ziel.mkdir()
    fremd = ziel / "notizen.txt"
    fremd.write_text("bleibt")
    alt = ziel / "radar-2026-10-01.sqlite"
    alt.write_bytes(b"x")
    zeit = (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()
    os.utime(fremd, (zeit, zeit))
    os.utime(alt, (zeit, zeit))
    with Store(settings.db_path):
        pass
    sicherung.erstellen(settings.data_dir, ziel, stamp="2026-11-08")
    assert fremd.exists() and not alt.exists()
    bad = subprocess.run(["bash", str(ROOT / "deploy" / "restore.sh"), "../etc"], env={**os.environ, "OHNE_SYSTEMCTL": "1"},
                         capture_output=True, text=True)
    assert bad.returncode == 2 and "YYYY-MM-DD" in bad.stderr


def test_data_dir_and_radar_key_from_environment(tmp_path, monkeypatch):
    import os as _os

    from news_radar.config import load_settings

    monkeypatch.setenv("RADAR_DATA_DIR", str(tmp_path / "pilot"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("RADAR_ANTHROPIC_API_KEY", "sk-ant-test")
    s = load_settings()
    assert s.data_dir == tmp_path / "pilot" and s.db_path == tmp_path / "pilot" / "radar.sqlite"
    assert _os.environ["ANTHROPIC_API_KEY"] == "sk-ant-test"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-vorrang")  # ein gesetzter ANTHROPIC_API_KEY bleibt
    load_settings()
    assert _os.environ["ANTHROPIC_API_KEY"] == "sk-ant-vorrang"
    monkeypatch.delenv("RADAR_DATA_DIR")
    assert load_settings().data_dir.name == "data"
