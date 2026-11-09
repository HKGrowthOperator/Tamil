import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from news_radar.store import OPEN_STATES, ConflictError, Store


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "radar.sqlite")
    yield s
    s.close()


def draft(uid="u1", **kw):
    base = dict(
        uid=uid, typ="artikel", quelle_name="Test", quelle_url=f"https://example.com/{uid}", relevanz=8,
        dach_bezug=True, ort="Paderborn", kategorie="kino", titel=f"Titel {uid}", teaser="Teaser",
        inhalt_html="<p>Text</p>", schlagworte=["Kino", "Paderborn"], original_json={"titel": f"Titel {uid}"},
        fakten={"kinos": []},
    )
    base.update(kw)
    return base


def test_wal_and_row_factory(store):
    assert store.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    store.insert_draft(draft())
    row = store.db.execute("SELECT * FROM drafts").fetchone()
    assert isinstance(row, sqlite3.Row)


def test_insert_draft_ignores_duplicate_uid(store):
    assert store.insert_draft(draft()) == 1
    assert store.insert_draft(draft(titel="anders")) is None
    assert store.counts_by_status()["neu"] == 1
    d = store.get_draft(1)
    assert d["schlagworte"] == ["Kino", "Paderborn"] and d["fakten"] == {"kinos": []} and d["dach_bezug"] is True


def test_set_status_follows_transitions(store):
    store.insert_draft(draft())
    assert store.set_status(1, "bearbeiten", von="luis") == "bearbeitet"
    assert store.set_status(1, "freigeben", von="luis") == "freigegeben"
    assert store.get_draft(1)["freigegeben_at"]
    store.set_status(1, "ablehnen")
    with pytest.raises(ConflictError):
        store.set_status(1, "freigeben")
    assert store.set_status(1, "wiederherstellen") == "neu"
    with pytest.raises(ValueError):
        store.set_status(1, "explodieren")


def test_set_status_conflict_between_two_stores(tmp_path):
    path = tmp_path / "radar.sqlite"
    a, b = Store(path), Store(path)
    a.insert_draft(draft())
    b.set_status(1, "ablehnen")
    with pytest.raises(ConflictError):
        a.set_status(1, "freigeben")
    a.close(), b.close()


def test_claim_for_publish_is_atomic(tmp_path):
    path = tmp_path / "radar.sqlite"
    a, b = Store(path), Store(path)
    for i in range(3):
        a.insert_draft(draft(f"u{i}"))
        a.set_status(i + 1, "freigeben")
    first = a.claim_for_publish(limit=2)
    second = b.claim_for_publish(limit=5)
    assert {d["id"] for d in first} == {1, 2} and {d["id"] for d in second} == {3}
    assert a.get_draft(1)["status"] == "wird_veroeffentlicht"
    a.mark_published(1, 77, "https://www.tamil.de/x/")
    a.mark_publish_failed(2, "WP 500")
    a.release_claim(3)
    assert a.get_draft(1)["status"] == "veroeffentlicht" and a.get_draft(1)["wp_post_id"] == 77
    assert a.get_draft(2)["status"] == "fehler" and a.get_draft(2)["fehler"] == "WP 500"
    assert a.get_draft(3)["status"] == "freigegeben"
    assert a.set_status(2, "erneut") == "freigegeben"
    a.close(), b.close()


def test_claim_draft_direct_post_from_open_state(store):
    store.insert_draft(draft())
    claimed = store.claim_draft(1, von="luis")
    assert claimed["status"] == "wird_veroeffentlicht" and claimed["freigegeben_at"]
    assert store.claim_draft(1) is None  # schon vergeben
    store.mark_published(1, 5, "https://www.tamil.de/a/")
    assert store.claim_draft(1) is None  # veröffentlicht ist endgültig


def test_update_kino_facts_only_when_open(store):
    store.insert_draft(draft(typ="kino_termine", fingerprint="f1"))
    assert store.update_kino_facts("u1", {"kinos": [1]}, "f1", "nix") is False  # gleicher Fingerprint
    assert store.update_kino_facts("u1", {"kinos": [1, 2]}, "f2", "Aktualisiert: +Mainz") is True
    d = store.get_draft(1)
    assert d["fakten"] == {"kinos": [1, 2]} and d["hinweise"] == ["Aktualisiert: +Mainz"]
    store.set_status(1, "freigeben")
    assert store.update_kino_facts("u1", {"kinos": [1, 2, 3]}, "f3", "x") is False


def test_update_draft_sets_fields_and_editor(store):
    store.insert_draft(draft())
    store.update_draft(1, von="luis", titel="Neu", schlagworte=["a"], status="veroeffentlicht", uid="hack")
    d = store.get_draft(1)
    assert d["titel"] == "Neu" and d["schlagworte"] == ["a"] and d["bearbeitet_von"] == "luis"
    assert d["status"] == "neu" and d["uid"] == "u1"  # status/uid nicht über update_draft änderbar


def test_daily_count_runs_and_sources(store):
    store.insert_draft(draft("a"))
    store.insert_draft(draft("b"))
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    assert store.drafts_created_since(today) == 2
    run = store.start_run("timer")
    store.finish_run(run, gesammelt=10, relevant=3, entwuerfe=2, fehler=0, unbekannt=1)
    assert store.recent_runs()[0]["entwuerfe"] == 2
    store.source_ok("Google", 12)
    store.source_failed("Kino", "429", pause_minutes=30)
    assert store.sources_paused() == {"Kino"}
    assert store.source_last_ok("Google") > datetime.now(timezone.utc) - timedelta(minutes=1)
    store.source_ok("Kino", 1)
    assert store.sources_paused() == set()
    store.event("fehler", titel="x", fehler="boom")
    dash = store.dashboard(7)
    assert dash["offen"] == 2 and dash["status"]["neu"] == 2 and dash["fehler"][0]["fehler"] == "boom"
    assert {q["name"] for q in dash["quellen"]} == {"Google", "Kino"}


def test_list_drafts_orders_new_by_dach_and_relevance(store):
    store.insert_draft(draft("x", dach_bezug=False, relevanz=9))
    store.insert_draft(draft("y", dach_bezug=True, relevanz=6))
    store.insert_draft(draft("z", dach_bezug=True, relevanz=8))
    assert [d["uid"] for d in store.list_drafts("neu")] == ["z", "y", "x"]
    assert OPEN_STATES == {"neu", "bearbeitet", "zurueckgestellt"}


def test_export_log_roundtrip(store, tmp_path):
    store.event("lauf", gesammelt=5)
    store.event("entwurf", titel="A")
    out = tmp_path / "log.jsonl"
    assert store.export_log(out) == 2
    lines = out.read_text(encoding="utf-8").splitlines()
    assert '"event": "lauf"' in lines[0] and '"titel": "A"' in lines[1]


def test_export_drafts_shape_and_column_migration(tmp_path):
    path = tmp_path / "alt.sqlite"
    with Store(path) as s:
        s.db.execute("ALTER TABLE drafts DROP COLUMN quelle_bild")  # Datenbank aus der Zeit vor der Spalte
        s.db.commit()
    with Store(path) as s:  # migrate() legt die Spalte wieder an
        s.insert_draft(draft("a", quelle_datum="2026-10-17T10:00", quelle_bild="https://img/a.jpg", hinweise=["Rohfassung ohne KI: …"]))
        s.insert_draft(draft("b", quelle_datum="2026-10-18T10:00"))
        s.insert_draft(draft("c", quelle_datum="2026-10-19T10:00"))
        s.set_status(3, "ablehnen")
        run_id = s.start_run("warteschlange · ohne KI")
        s.finish_run(run_id, gesammelt=5, relevant=2, entwuerfe=2)
        s.source_ok("Test", 5)
        data = s.export_drafts()
    assert [d["uid"] for d in data["entwuerfe"]] == ["b", "a"]
    a = data["entwuerfe"][1]
    assert a["quelle_bild"] == "https://img/a.jpg" and a["hinweise"] == ["Rohfassung ohne KI: …"] and a["fakten"] == {"kinos": []}
    assert "original_json" not in a and "fingerprint" not in a
    assert data["lauf"]["modus"] == "warteschlange · ohne KI" and data["quellen"][0]["name"] == "Test"
