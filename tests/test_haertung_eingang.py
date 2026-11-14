"""F1-Radar (Eingang), Prüfliste vom 13.11.2026, Punkt 3.

a) Ein Datum im Modelltext muss als Ganzes (Tag, Monat, Jahr) in der Einsendung stehen – nicht nur Tag und Monat an
   einer Stelle und das Jahr an einer anderen („gegründet im Januar 2019“ + „16. Januar 2027“ ≠ „16. Januar 2019“).
b) Store.transaktion: schlägt der Commit fehl, wird zurückgerollt; der nächste Schreibschritt nimmt die halbe
   Transaktion nicht mit.
"""

import sqlite3

import pytest

from news_radar import eingang

from test_eingang import EVENT, settings, store  # noqa: F401


def _erlaubt(**felder):
    return eingang.erlaubter_text({"art": "event", "felder": {**EVENT, **felder}})


def test_a_datum_aus_zwei_stellen_zusammengesetzt_ist_erfunden():
    erlaubt = _erlaubt(beschreibung="Der Testverein, gegründet im Januar 2019, lädt zum Fest.")
    assert eingang.fremde_angaben(["Samstag, 16. Januar 2019"], erlaubt)


def test_a_datum_der_einsendung_bleibt_erlaubt():
    erlaubt = _erlaubt(beschreibung="Der Testverein, gegründet im Januar 2019, lädt zum Fest.")
    assert eingang.fremde_angaben(["Samstag, 16. Januar 2027, 18:30 Uhr."], erlaubt) == []
    assert eingang.fremde_angaben(["Samstag, 16. Januar"], erlaubt) == []


class _CommitFehler:
    """Verbindung, deren nächster Commit scheitert (wie SQLITE_BUSY oder ein voller Datenträger)."""

    def __init__(self, db):
        self._db, self.scheitern = db, True

    def __getattr__(self, name):
        return getattr(self._db, name)

    def commit(self):
        if self.scheitern:
            self.scheitern = False
            raise sqlite3.OperationalError("disk I/O error")
        return self._db.commit()


def test_b_transaktion_rollt_zurueck_wenn_der_commit_scheitert(store):
    echt = store.db
    store.db = _CommitFehler(echt)
    try:
        with pytest.raises(sqlite3.OperationalError):
            with store.transaktion():
                store._write("INSERT INTO log (ts, event, data) VALUES ('x', 'halb', '{}')")
        store._write("INSERT INTO log (ts, event, data) VALUES ('x', 'danach', '{}')")
    finally:
        store.db = echt
    assert not echt.in_transaction
    assert echt.execute("SELECT COUNT(*) FROM log WHERE event = 'halb'").fetchone()[0] == 0
    assert echt.execute("SELECT COUNT(*) FROM log WHERE event = 'danach'").fetchone()[0] == 1


def test_p3_uhrzeit_mit_punkt_ist_kein_datum():
    # „18.30.“ (Satzende nach der Uhrzeit) ist kein Datum mit Monat 30
    erlaubt = _erlaubt(beschreibung="Einlass 18.30 Uhr. Tanz, Musik und Essen.")
    assert eingang.fremde_angaben(["Einlass 18.30."], erlaubt) == []
