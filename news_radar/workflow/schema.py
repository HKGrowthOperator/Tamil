"""Datenbank-Migrationen über PRAGMA user_version.

Version 1 ist das bisherige Schema (store.SCHEMA + ADDED_COLUMNS). Jede weitere Version ist eine Liste von
SQL-Anweisungen; ALTER TABLE … ADD COLUMN wird übersprungen, wenn die Spalte schon existiert.
"""

from __future__ import annotations

import sqlite3

V2 = [
    """CREATE TABLE IF NOT EXISTS http_cache (
        url TEXT PRIMARY KEY, etag TEXT, last_modified TEXT, updated_at TEXT)""",
    "ALTER TABLE source_status ADD COLUMN ok_count INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE source_status ADD COLUMN err_count INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE drafts ADD COLUMN story_id INTEGER",
    """CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        typ TEXT NOT NULL,                      -- news | event | kino | dossier
        status TEXT NOT NULL DEFAULT 'neu',
        titel TEXT, kategorie TEXT, ort TEXT, region TEXT,
        sensibel INTEGER NOT NULL DEFAULT 0,
        schluessel TEXT,                        -- Event-/Kino-Schlüssel fürs Clustering
        prioritaet INTEGER NOT NULL DEFAULT 0,
        laenge TEXT,                            -- kurz | normal | lang
        relevanz INTEGER, begruendung TEXT,
        notiz TEXT,
        erstellt TEXT NOT NULL, aktualisiert TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS stories_status ON stories(status, aktualisiert DESC)",
    "CREATE INDEX IF NOT EXISTS stories_schluessel ON stories(schluessel)",
    """CREATE TABLE IF NOT EXISTS source_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id INTEGER NOT NULL,
        doc_key TEXT NOT NULL,                  -- Q1, Q2 … (stabil je Story, so zitieren die Claims)
        url TEXT, url_norm TEXT, uid TEXT,
        publisher TEXT, quelle TEXT,            -- Verlag / Eintrag im Quellen-Register
        published_at TEXT, retrieved_at TEXT, language TEXT,
        rights TEXT,                            -- frei | zitat | lizenz | unbekannt
        primaer INTEGER NOT NULL DEFAULT 0,
        art TEXT NOT NULL DEFAULT 'zusammenfassung', -- volltext | zusammenfassung | hinweis | daten | redaktion
        titel TEXT, text TEXT, text_sha256 TEXT, auszug TEXT,
        UNIQUE(story_id, doc_key), UNIQUE(story_id, url_norm))""",
    "CREATE INDEX IF NOT EXISTS source_documents_url ON source_documents(url_norm)",
    "CREATE INDEX IF NOT EXISTS source_documents_uid ON source_documents(uid)",
    """CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id INTEGER NOT NULL,
        claim_key TEXT NOT NULL,                -- C1, C2 …
        aussage TEXT NOT NULL, art TEXT, kern INTEGER NOT NULL DEFAULT 0,
        quellen TEXT NOT NULL DEFAULT '[]',     -- JSON-Liste von doc_keys
        support TEXT NOT NULL DEFAULT 'offen',  -- bestaetigt | einzelquelle | unbestaetigt | widerspruch | offen
        confidence REAL, fundstelle TEXT, erstellt TEXT,
        UNIQUE(story_id, claim_key))""",
    """CREATE TABLE IF NOT EXISTS workflow_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id INTEGER,
        schritt TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'offen',   -- offen | laeuft | fertig | tot | wartet_budget
        prio INTEGER NOT NULL DEFAULT 0,
        versuche INTEGER NOT NULL DEFAULT 0,
        naechster_versuch TEXT NOT NULL,
        deadline TEXT,
        idempotenz_key TEXT UNIQUE,
        payload TEXT NOT NULL DEFAULT '{}',
        fehler TEXT, worker TEXT,
        erstellt TEXT NOT NULL, aktualisiert TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS jobs_faellig ON workflow_jobs(status, prio DESC, naechster_versuch)",
    """CREATE TABLE IF NOT EXISTS article_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id INTEGER, draft_id INTEGER,
        rolle TEXT NOT NULL, von TEXT, hash TEXT NOT NULL, inhalt TEXT NOT NULL, erstellt TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS versions_story ON article_versions(story_id, id)",
    """CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datei TEXT NOT NULL, sha256 TEXT,
        herkunft TEXT NOT NULL,                 -- archiv | quelle | stock | pool | ki | karte | upload
        rechteinhaber TEXT, lizenz TEXT, umfang TEXT, attribution TEXT, ablauf TEXT, quelle_url TEXT,
        ki INTEGER NOT NULL DEFAULT 0,
        story_id INTEGER, draft_id INTEGER, erstellt TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS assets_datei ON assets(datei)",
    """CREATE TABLE IF NOT EXISTS agent_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL, story_id INTEGER, job_id INTEGER, rolle TEXT NOT NULL,
        provider TEXT NOT NULL DEFAULT 'anthropic',
        modell_angefragt TEXT, modell TEXT, prompt_version TEXT,
        input_tokens INTEGER NOT NULL DEFAULT 0, output_tokens INTEGER NOT NULL DEFAULT 0,
        cache_write_5m INTEGER NOT NULL DEFAULT 0, cache_write_1h INTEGER NOT NULL DEFAULT 0,
        cache_read INTEGER NOT NULL DEFAULT 0, bilder INTEGER NOT NULL DEFAULT 0,
        iterationen INTEGER NOT NULL DEFAULT 1,
        kosten_usd REAL NOT NULL DEFAULT 0, preis_version TEXT,
        status TEXT NOT NULL,                   -- ok | abgelehnt | abgeschnitten | fehler | budget
        latenz_ms INTEGER, request_id TEXT, fehler TEXT)""",
    "CREATE INDEX IF NOT EXISTS agent_usage_ts ON agent_usage(ts)",
    "CREATE INDEX IF NOT EXISTS agent_usage_story ON agent_usage(story_id)",
    """CREATE TABLE IF NOT EXISTS budget_reservierungen (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, rolle TEXT, betrag REAL NOT NULL, story_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS editorial_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL, wer TEXT, aktion TEXT NOT NULL,
        draft_id INTEGER, story_id INTEGER, fassung_hash TEXT, wp_post_id INTEGER, notiz TEXT)""",
    "CREATE INDEX IF NOT EXISTS actions_draft ON editorial_actions(draft_id, id)",
    """CREATE TABLE IF NOT EXISTS users (
        name TEXT PRIMARY KEY, passwort_hash TEXT NOT NULL,
        rolle TEXT NOT NULL DEFAULT 'redaktion',  -- redaktion | admin
        aktiv INTEGER NOT NULL DEFAULT 1, erstellt TEXT NOT NULL, letzter_login TEXT)""",
]

# V3: serverseitige Sitzungen – Sperren, Rollenwechsel und Abmelden wirken sofort, auch auf kopierte Cookies
V3 = [
    """CREATE TABLE IF NOT EXISTS sitzungen (
        id TEXT PRIMARY KEY, nutzer TEXT NOT NULL,
        konto TEXT NOT NULL,  -- db (Tabelle users) | env (WEB_USER aus der .env)
        erstellt TEXT NOT NULL, ablauf TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS sitzungen_nutzer ON sitzungen(nutzer)",
]

# V4: Cockpit-Grundlage (Vertrag B1.1, §8) – Stopp-Schalter je Kanal, Läufe des Dienstes für die Zeitplan-Ansicht,
# Protokoll mit Gegenstand, Kanal, Fassung der Regel und Auslöser. Bestehende Zeilen behalten ihre Werte (NULL = alt).
V4 = [
    """CREATE TABLE IF NOT EXISTS schalter (
        kanal TEXT PRIMARY KEY,                 -- alles | redaktion | website | eingang | verzeichnis | instagram …
        gestoppt INTEGER NOT NULL DEFAULT 0,
        grund TEXT, wer TEXT, seit TEXT)""",
    """CREATE TABLE IF NOT EXISTS dienst_laeufe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aufgabe TEXT NOT NULL, start TEXT NOT NULL, ende TEXT,
        ergebnis TEXT)                          -- ok | fehler (Code n) | timeout | abgebrochen | angehalten (Kanal)""",
    "CREATE INDEX IF NOT EXISTS dienst_laeufe_aufgabe ON dienst_laeufe(aufgabe, id)",
    "ALTER TABLE editorial_actions ADD COLUMN gegenstand_typ TEXT",   # entwurf | story | job | nutzer | schalter
    "ALTER TABLE editorial_actions ADD COLUMN gegenstand_id TEXT",
    "ALTER TABLE editorial_actions ADD COLUMN kanal TEXT",
    "ALTER TABLE editorial_actions ADD COLUMN regel_fassung TEXT",
    "ALTER TABLE editorial_actions ADD COLUMN ausloeser TEXT",        # person | dienst | agent
    "CREATE INDEX IF NOT EXISTS actions_ts ON editorial_actions(ts)",
]

# Nachtrag (Rückblick): Storys aus einem Vorschlag mit Quellen statt aus dem Scan; das Ereignisdatum reist bis zur
# Veröffentlichung mit (Entwurf → Plugin-Feld „datum“). Bestehende Zeilen bekommen Herkunft „radar“.
V5 = [
    "ALTER TABLE stories ADD COLUMN herkunft TEXT NOT NULL DEFAULT 'radar'",   # radar | nachtrag
    "ALTER TABLE stories ADD COLUMN ereignis_datum TEXT",                      # JJJJ-MM-TT (nur Nachtrag)
    "ALTER TABLE stories ADD COLUMN vorschlag TEXT",                           # JSON: Hinweise aus dem Vorschlag
    "ALTER TABLE drafts ADD COLUMN herkunft TEXT NOT NULL DEFAULT 'radar'",
    "ALTER TABLE drafts ADD COLUMN ereignis_datum TEXT",
    "CREATE INDEX IF NOT EXISTS stories_herkunft ON stories(herkunft, ereignis_datum)",
    "CREATE INDEX IF NOT EXISTS drafts_herkunft ON drafts(herkunft, created_at)",
]

# Stand eines Entwurfs: zählt bei jeder Änderung am Inhalt (Text, Bild, Nachweis …) hoch. Die Freigabe im Cockpit
# greift nur, wenn der Stand noch der ist, den die Seite gezeigt hat (Bedingung im selben UPDATE).
DRAFT_INHALT = ('typ', 'quelle_name', 'quelle_url', 'quelle_datum', 'quelle_sprache', 'weitere_quellen', 'quelle_bild', 'relevanz', 'begruendung', 'dach_bezug', 'ort', 'kategorie', 'titel', 'teaser', 'inhalt_html', 'schlagworte', 'seo_titel', 'meta_beschreibung', 'bild_datei', 'bild_credit', 'bild_alt', 'bild_suchbegriff', 'bild_origin', 'bild_thema', 'bild_prompt', 'event_datum', 'event_ort', 'ticket_url', 'fakten_json', 'hinweise', 'story_id', 'herkunft', 'ereignis_datum')
V6 = [
    "ALTER TABLE drafts ADD COLUMN stand INTEGER NOT NULL DEFAULT 0",
    "CREATE TRIGGER IF NOT EXISTS drafts_stand AFTER UPDATE OF " + ", ".join(DRAFT_INHALT) + " ON drafts "
    "BEGIN UPDATE drafts SET stand = stand + 1 WHERE id = NEW.id; END",
]
# Letzter Abruf mit Teilausfall: zählt für den Takt (interval_minutes) wie last_ok, ohne als Erfolg zu gelten
V7 = ["ALTER TABLE source_status ADD COLUMN last_try TEXT"]
# V9: Lizenz-Datensatz je Bild (docs/spezifikation/bilder-und-lizenzen.md, Abschnitt 3.1). `umfang` bleibt die Spalte
# aus V2, gilt ab jetzt als kommagetrennte Menge aus website, social, print (`lizenz.umfang_text`); Altbestand mit
# Freitext gilt als unvollständig, bis die Nachführung oder die Redaktion den Datensatz ergänzt. Nummer 8 hält eine
# parallele Spur frei.
V9 = [
    "ALTER TABLE assets ADD COLUMN urheber TEXT",
    "ALTER TABLE assets ADD COLUMN lizenz_kuerzel TEXT",      # Positivliste lizenz.KUERZEL (eigen, cc-by-4.0 …)
    "ALTER TABLE assets ADD COLUMN lizenz_url TEXT",
    "ALTER TABLE assets ADD COLUMN bild_url TEXT",            # Adresse der abgerufenen Bilddatei
    "ALTER TABLE assets ADD COLUMN bearbeitung TEXT",         # keine | zugeschnitten | eingepasst | Logo-Leiste | KI-Hinweis
    "ALTER TABLE assets ADD COLUMN beleg TEXT",               # wie die Lizenz geprüft wurde (Abruf, Register, Datei)
    "ALTER TABLE assets ADD COLUMN geprueft_von TEXT",        # dienst | agent:<name> | Benutzername
    "ALTER TABLE assets ADD COLUMN geprueft_am TEXT",
    "ALTER TABLE assets ADD COLUMN ki_modell TEXT",
    "ALTER TABLE assets ADD COLUMN prompt_hash TEXT",
    "ALTER TABLE assets ADD COLUMN alt TEXT",
    "ALTER TABLE assets ADD COLUMN fokus TEXT",               # x,y in Prozent
    "CREATE INDEX IF NOT EXISTS assets_draft ON assets(draft_id, datei)",
]
MIGRATIONS: dict[int, list[str]] = {2: V2, 3: V3, 4: V4, 5: V5, 6: V6, 7: V7, 9: V9}
LATEST = max(MIGRATIONS)


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in db.execute(f"PRAGMA table_info({table})")}


def _version(db: sqlite3.Connection) -> int:
    return db.execute("PRAGMA user_version").fetchone()[0] or 1


def apply(db: sqlite3.Connection) -> int:
    """Wendet alle ausstehenden Migrationen an und gibt die neue Version zurück.

    Jede Version läuft in einer Schreibtransaktion (BEGIN IMMEDIATE) und liest die Version darin neu: Starten Cockpit,
    Worker und Scan gleichzeitig, migriert genau einer, die anderen warten (busy_timeout) und finden nichts mehr zu tun.
    """
    version = _version(db)
    for target in sorted(v for v in MIGRATIONS if v > version):
        if db.in_transaction:
            db.commit()
        db.execute("BEGIN IMMEDIATE")
        try:
            if _version(db) >= target:  # ein anderer Prozess war schneller
                db.commit()
                version = _version(db)
                continue
            for sql in MIGRATIONS[target]:
                stripped = " ".join(sql.split())
                if stripped.upper().startswith("ALTER TABLE") and " ADD COLUMN " in stripped.upper():
                    parts = stripped.split()
                    table, column = parts[2], parts[5]
                    if column in _columns(db, table):
                        continue
                db.execute(sql)
            db.execute(f"PRAGMA user_version = {int(target)}")
            db.commit()
        except BaseException:
            db.rollback()
            raise
        version = target
    return version
