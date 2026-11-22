"""Theme tamil 3.15.0: Die Bildkacheln von „Diese Woche“ zeigen nur Beiträge, deren Film einen Spieltag ab heute hat
(tamil_woche_bilder() in inc/queries.php, TML-W03). Bis 3.14.0 reichte ein Kino-Beitrag der letzten 30 Tage.
"""

import json

import pytest


@pytest.fixture
def kino(wp_cli):
    """Legt Kinolisten (Meta kino_fakten) und Beiträge der Rubrik Kino an und räumt sie wieder weg."""
    ids: list[int] = []

    class Kino:
        @staticmethod
        def liste(film: str, tage: int) -> int:
            """Kinoliste mit einem einzigen Spieltag: heute plus `tage` (negativ = vorbei)."""
            pid = int(wp_cli(
                f"$p = wp_insert_post( array( 'post_title' => 'Kinoliste {film}', 'post_status' => 'publish', 'post_content' => '<p>x</p>' ) );"
                f" $tag = wp_date( 'Y-m-d', strtotime( current_time( 'Y-m-d' ) . ' {tage:+d} days' ) );"
                f" update_post_meta( $p, 'kino_fakten', wp_json_encode( array( 'film' => '{film}', 'kinos' => array( array("
                " 'kino' => 'Testkino', 'stadt' => 'Hamm', 'land' => 'DE', 'termine' => array( $tag ) ) ) ) ) ); echo $p;"))
            ids.append(pid)
            return pid

        @staticmethod
        def beitrag(titel: str) -> int:
            """Frischer Beitrag der Rubrik Kino ohne eigene Kinoliste."""
            pid = int(wp_cli(
                "$k = get_category_by_slug( 'kino' );"
                f" $p = wp_insert_post( array( 'post_title' => '{titel}', 'post_status' => 'publish', 'post_content' => '<p>x</p>',"
                " 'post_category' => array( (int) $k->term_id ) ) ); echo $p;"))
            ids.append(pid)
            return pid

    if wp_cli("echo get_category_by_slug( 'kino' ) ? 1 : 0;") != "1":
        pytest.skip("Rubrik Kino fehlt im lokalen WordPress")
    yield Kino
    for pid in ids:
        wp_cli(f"wp_delete_post( {pid}, true );")
    wp_cli("tamil_flush_auswahl();")


def _bilder(wp_cli) -> list[int]:
    return json.loads(wp_cli("echo wp_json_encode( tamil_woche_auswahl()['bilder'] );"))


def test_kino_beitrag_ohne_kuenftigen_spieltag_ist_keine_bildkachel(wp_cli, kino):
    kino.liste("Altfilm Qwertz", -1)  # letzter Spieltag gestern
    alt = kino.beitrag("Kritik: „Altfilm Qwertz“ im Rückblick")
    lose = kino.beitrag("Kinonachricht ohne Film und ohne Termin")
    bilder = _bilder(wp_cli)
    assert alt not in bilder, "Film ohne Spieltag ab heute: keine Bildkachel, auch wenn der Beitrag neu ist"
    assert lose not in bilder, "Kino-Beitrag ohne Film mit kommender Vorstellung: keine Bildkachel"


def test_kino_beitrag_mit_kuenftigem_spieltag_ist_bildkachel(wp_cli, kino):
    kino.liste("Neufilm Asdfgh", 0)  # Spieltag heute zählt als kommend
    kino.liste("Altfilm Qwertz", -1)
    neu = kino.beitrag("Kritik: „Neufilm Asdfgh“ startet")
    alt = kino.beitrag("Kritik: „Altfilm Qwertz“ im Rückblick")
    bilder = _bilder(wp_cli)
    assert neu in bilder and alt not in bilder
    laufend = set(json.loads(wp_cli("echo wp_json_encode( array_map( 'intval', wp_list_pluck( tamil_kino_filme( 50 ), 'post' ) ) );")))
    schluessel = set(json.loads(wp_cli(
        "echo wp_json_encode( array_values( array_map( static fn( $f ) => tamil_film_norm( $f['film'] ), tamil_kino_filme( 50 ) ) ) );")))
    for pid in bilder:
        eigene = set(json.loads(wp_cli(f"echo wp_json_encode( tamil_film_schluessel( {pid} ) );")))
        assert pid in laufend or eigene & schluessel, f"Bildkachel {pid} ohne Film mit Spieltag ab heute"


def test_startseite_ohne_laufenden_film_ohne_alte_kachel(wp, wp_cli, kino):
    """Im Abschnitt „Diese Woche“ der Startseite steht der neue Beitrag zum abgelaufenen Film nicht; fehlen die
    Bildkacheln ganz, rückt das Raster zusammen (kein leerer Platz)."""
    kino.liste("Altfilm Qwertz", -1)
    kino.beitrag("Kritik: „Altfilm Qwertz“ im Rückblick")
    wp_cli("tamil_flush_auswahl();")
    seite = wp.get("/").text
    woche = seite[seite.index('id="diese-woche"'):]
    woche = woche[:woche.index("</section>")]
    assert "Altfilm Qwertz" not in woche
    bilder = json.loads(wp_cli("echo wp_json_encode( tamil_start_auswahl()['woche']['bilder'] );"))
    assert ("ohne-gross" in woche) is (len(bilder) < 1) and ("ohne-klein" in woche) is (len(bilder) < 2)
    assert woche.count('class="kachel ') == len(bilder), "so viele Bildkacheln wie ausgewählte Beiträge, kein leerer Rahmen"
