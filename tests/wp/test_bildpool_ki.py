"""KI-Symbolbilder im Rubrik-Pool (Theme 3.13.0, Entscheidung 21.11.2026 in docs/entscheidungen.md):

- Nachweis überall genau „Symbolbild: KI-generiert · Tamil.de“ (Spezifikation 4.8), auch im Fuß „Bildnachweise dieser
  Seite“; nie „Symbolbild, Symbolbild“, nie „zugeschnitten“, kein Commons-Nachweis ohne Urheber.
- Beiträge der Rubrik Nachrichten bekommen nie ein KI-Bild (Spezifikation 4.2), auch nicht, wenn der Pool erschöpft
  ist und der allgemeine einspringt, und auch nicht, wenn die Hauptrubrik eine andere ist.
- Ist der Pool einer Rubrik auf einer Seite erschöpft, kommt erst ein freies Bild des allgemeinen Pools, bevor sich
  eines wiederholt.
- Nicht im Pool: news-4 bis news-7 und community-4 (Entscheidung 21.11.).

Gegen ein lokales WordPress (wordpress/dev/setup.sh + serve.sh).
"""

import html
import json
import re

import pytest
import requests
from wp_umgebung import URL

KI = "Symbolbild: KI-generiert · Tamil.de"


def _json(wp_cli, code: str):
    return json.loads(wp_cli(code))


def test_pool_umfang_und_ausschluesse(wp_cli):
    pool = _json(wp_cli, "echo wp_json_encode( tamil_bildpool() );")
    ki = {r: [b["datei"] for b in l if b.get("ki")] for r, l in pool.items()}
    assert {r: len(l) for r, l in ki.items() if l} == {
        "entertainment": 4, "events": 4, "community": 3, "kueche": 4, "kino": 4, "sport": 4, "kultur": 4}
    alle = {b["datei"] for l in pool.values() for b in l}
    for aus in ("news-4.webp", "news-5.webp", "news-6.webp", "news-7.webp", "community-4.webp"):
        assert aus not in alle, aus
    for l in pool.values():
        for b in l:
            if b.get("ki"):
                assert (b["urheber"], b["lizenz"], b["lizenz_url"], b["seite"]) == ("", "", "", ""), b["datei"]


def test_ki_nachweis_wortlaut(wp_cli):
    r = _json(wp_cli, "$p = tamil_pool_liste( 'kultur' ); $ki = array_values( array_filter( $p, fn( $x ) => ! empty( $x['ki'] ) ) );"
                      " $alt = array_values( array_filter( $p, fn( $x ) => empty( $x['ki'] ) ) );"
                      " echo wp_json_encode( array( tamil_pool_nachweis( $ki[0] ), tamil_pool_nachweis( $alt[0] ) ) );")
    assert html.unescape(r[0]) == KI
    assert "Wikimedia Commons" in r[1] and "zugeschnitten" in r[1]  # Commons-Fotos wie bisher


@pytest.fixture
def ohne_bild(wp_cli):
    """Beiträge ohne eigenes Bild: zwei in Kultur, einer in Nachrichten, einer in Kultur und Nachrichten."""
    code = ("$k = get_category_by_slug( 'kultur' )->term_id; $n = get_category_by_slug( 'news' )->term_id; $ids = array();"
            " foreach ( array( array( 'ki-kultur-1', array( $k ) ), array( 'ki-kultur-2', array( $k ) ), array( 'ki-news-1', array( $n ) ),"
            " array( 'ki-beides-1', array( $k, $n ) ) ) as $e ) { $ids[ $e[0] ] = wp_insert_post( array( 'post_status' => 'publish',"
            " 'post_title' => 'KI-Probe ' . $e[0], 'post_name' => $e[0], 'post_content' => '<p>Text ohne Bild.</p>', 'post_category' => $e[1] ) ); }"
            " echo wp_json_encode( $ids );")
    ids = _json(wp_cli, code)
    yield ids
    for pid in ids.values():
        wp_cli(f"wp_delete_post( {int(pid)}, true );")


def _bild_und_fuss(slug: str) -> tuple[str, list[str], str]:
    seite = requests.get(f"{URL}/{slug}/", timeout=30).text
    bild = re.search(r'<img[^>]*class="artikel__bild[^"]*"[^>]*>|<figure class="artikel__figur">.*?<img[^>]*>', seite, re.S)
    src = re.search(r'src="([^"]+)"', bild.group(0)).group(1) if bild else ""
    i = seite.find("Bildnachweise")
    fuss = [html.unescape(re.sub("<[^>]+>", "", x)).strip() for x in re.findall(r"<li[^>]*>(.*?)</li>", seite[i:i + 8000], re.S)]
    return src, fuss, seite


def test_ki_bild_mit_nachweis_unter_dem_bild_und_im_fuss(wp, ohne_bild):
    funde = 0
    for slug in ("ki-kultur-1", "ki-kultur-2"):
        src, fuss, seite = _bild_und_fuss(slug)
        assert "/img/rubrik/kultur-" in src, (slug, src)
        datei = src.split("/")[-1]
        if datei in ("kultur-1.webp",):  # Commons-Foto der Rubrik
            continue
        funde += 1
        assert html.unescape(re.search(r"<figcaption[^>]*>(.*?)</figcaption>", seite, re.S).group(1)).strip() == KI
        assert fuss.count(KI) == 1, fuss
        assert not any("Symbolbild, Symbolbild" in z or ("KI-generiert" in z and "zugeschnitten" in z) for z in fuss), fuss
        assert not any("Wikimedia Commons" in z and z.startswith(("Foto:  /", "Symbolbild, Foto:  /")) for z in fuss), fuss
        assert 'symbolbild__lang' in seite  # Schild am Bild
    assert funde, "mindestens einer der beiden Beiträge zeigt ein KI-Bild"


@pytest.mark.parametrize("slug", ["ki-news-1", "ki-beides-1"])
def test_nachrichten_nie_ki(wp, wp_cli, ohne_bild, slug):
    """Auch „ki-beides-1“ (Hauptrubrik Kultur, zusätzlich in Nachrichten) bekommt kein KI-Bild."""
    ki = set(_json(wp_cli, "$k = array(); foreach ( tamil_bildpool() as $l ) { foreach ( $l as $p ) { if ( ! empty( $p['ki'] ) )"
                           " { $k[] = $p['datei']; } } } echo wp_json_encode( $k );"))
    src, fuss, seite = _bild_und_fuss(slug)
    assert "/img/rubrik/" in src, src
    datei = src.split("/")[-1].replace("-480", "").replace("-320", "")
    assert datei not in ki, datei
    # Nachweis unter dem eigenen Bild (der Fuß sammelt auch Bilder anderer Karten der Seite, z. B. „Weiterlesen“)
    unter = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", seite, re.S)
    assert unter and "KI-generiert" not in unter.group(1), unter and unter.group(1)


def test_nachrichten_nie_ki_auch_wenn_der_pool_erschoepft_ist(wp_cli):
    """Mehr Rahmen als Bilder in Nachrichten und im allgemeinen Pool: keiner bekommt ein KI-Bild."""
    r = _json(wp_cli, "$aus = array(); for ( $i = 0; $i < 20; $i++ ) { $aus[] = tamil_pool_seite( 'news', $i ); }"
                      " for ( $i = 0; $i < 10; $i++ ) { $aus[] = tamil_pool_seite( 'kultur', $i, true ); }"
                      " $aus[] = tamil_pool_bild( 'news', 3 ); $aus = array_merge( $aus, tamil_pool_liste( 'news' ) );"
                      " echo wp_json_encode( array_map( fn( $p ) => array( $p['datei'], ! empty( $p['ki'] ) ), $aus ) );")
    assert r and not [d for d, ki in r if ki], r


def test_erschoepfter_rubrik_pool_nimmt_erst_den_allgemeinen(wp_cli):
    r = _json(wp_cli, "$n = count( tamil_pool_liste( 'kultur' ) ); $a = count( tamil_pool_liste( 'allgemein' ) ); $aus = array();"
                      " for ( $i = 0; $i < $n + $a + 1; $i++ ) { $aus[] = tamil_pool_seite( 'kultur', $i )['datei']; }"
                      " echo wp_json_encode( array( $n, $a, $aus ) );")
    n, a, aus = r
    assert len(set(aus[:n])) == n and all(d.startswith("kultur-") for d in aus[:n]), aus
    assert len(set(aus[:n + a])) == n + a and all(d.startswith("allgemein-") for d in aus[n:n + a]), aus
    assert aus[n + a] in aus[:n + a]  # erst danach wiederholt sich eines
