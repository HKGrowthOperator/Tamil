# Nachtschicht 14./15.11.: Kurzbericht Sitzung A (für den Gesamtbericht von B)

Plan: `docs/nachtschicht/2026-11-14.md`. Stand 15.11., 00:55. Alles Live-Gestellte lief vorher durch `pytest`,
`abnahme`, bei WordPress `lint.sh` und `tests/wp/`, und durch eine Prüfung aus frischem Kontext (bei Befunden mit
Gegenprüfung).

## Live auf dem Testsystem (`claude/radar-multiagent`, Auto-Deploy)

| Was | Commit | Stand |
|---|---|---|
| Stand vom 12.11.: Termin-Abgleich (Vereinshinweis, Orte auf -ring, Großbuchstaben), „6:00 – 9:30 p.m.“, SEO (Autor = Redaktion, Logo, Canonical, dünne Schlagwörter, Benutzerliste und Autorenarchive gesperrt) | `d0e088c` | live geprüft: `/author/luis/` 301, `/wp-json/wp/v2/users` 401 |
| Verzeichnis, Radar-Seite (F2, B1.4): Abholen, Prüfen nach festen Regeln, Cockpit alt neben neu, Freigabe; Schalter `RADAR_VERZEICHNIS` aus | `bfba18c` | Szenarien 88, 89; Cockpit-Aufnahmen 0 Fehler |
| Radar-Härtungen: Satzprüfung im Agent-Import, Kostendeckel mit Prüfanteil, Eingang (Datum als Ganzes, Rollback) | `23a7bab` | erste Fassung war überstreng, nach zwei Gegenprüfungen korrigiert (Szenario 95) |
| WordPress-Härtungen: Drossel je /64 in F2/F3, Schalter erst ab Datenversion, Regeln nach Aktivierung | `8606224` | Code-Prüfung nur P3 |
| Protokoll B5 und Testbett (Weiterleitungen wie die Übernahme) | `cccd01a` | B5: 6 von 7 automatisch bestanden, T5 ohne `test_buchung.py` (Ersatz `test_werbung.py` 34/34) |
| Befunde von B: Kostendeckel (Endprüfung muss in den vollen Deckel passen), Verzeichnis-Konflikte | `dbbdf6b` | gezielte Prüfung, P2 behoben |

Zahlen auf `dbbdf6b`: `pytest` 1599 bestanden, `abnahme` 89 von 89; `tests/wp` auf frischem WordPress 185 von 185
(vor `dbbdf6b` gemessen; seitdem kein WordPress-Code geändert).

## Nicht live: Design „Tageskalender“ (Mischung aus A und B, Auftrag Luis 14.11.)

- **Probe** `design/richtungen/hm-tageskalender/`, Runde 3; Kritik r1 (3 P1) → r2 (14/14, 1 P1) → behoben.
- **Theme** `tamil` 2.0.0 nur auf `claude/mache-weiter-i23fs9` (Branch-Stand `c17ffa7`): vier Runden mit Kritik
  (`design/kritik/theme-tageskalender-r1..r3.md`), Runde 4 behebt die P1 aus r3 und ist **nicht mehr frisch geprüft**.
  `tests/wp` 195/195, `lint.sh` sauber, `shots.mjs` 0 Fehler, sloplint 0 FAIL ohne Ausnahme.
- Aufnahmen: `docs/nachtschicht/2026-11-15/theme-*.jpg` auf `claude/mache-weiter-i23fs9`.
- Bewusst: Wortdichte (Gate 58) und Eigenanzeigen auf ungebuchten Plätzen (F3) stehen in `docs/entscheidungen.md`.

## Offen für Luis

1. Theme „Tageskalender“ ansehen: aufs Testsystem (Merge in `claude/radar-multiagent`) oder ändern.
2. Eigenanzeigen auf jedem ungebuchten Platz (F3) behalten oder leere Plätze?
3. Aufmacher der Testseite: Beitrag mit Thileepan-Bezug und Fahnen (Gedenk-Sperrliste) vor dem Kundentermin tauschen.
4. `tamil_werbetage` bei Deinstallation löschen (Spezifikation) oder bezahlte Tage behalten (sonst Doppelbuchung nach
   Neuinstallation möglich)?
5. T5: `test_werbung.py` als Nachweis anerkennen oder `test_buchung.py` nachbauen?
6. Offene P3: Kategorien fest im Code; Drossel F2 nicht atomar; Zähler „unlesbar“ im Cockpit; Punkt 3c der Prüfliste
   („Feldnamen als Präfix“) unklar.
7. Tor B1 (Anthropic-Schlüssel), Tor B2 (Tokens widerrufen).
