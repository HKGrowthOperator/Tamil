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
