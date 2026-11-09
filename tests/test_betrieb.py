"""Betrieb: Sicherung und Wiederherstellung (Roundtrip), Wochenbericht, Tageszusammenfassung mit Kosten."""

import os
import subprocess
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
    assert "Kosten" in digest and "Recherche nötig" in digest and "abgebrochene Jobs" in digest
