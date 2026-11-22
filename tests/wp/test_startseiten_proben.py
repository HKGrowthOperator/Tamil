"""Theme tamil 3.16.0: Startseiten-Proben (inc/proben.php, template-parts/home/probe-*.php, stadt.php; TML-W06).

Drei Entwürfe für den ersten Bildschirm (/?probe=cover, news, community) und der Abschnitt „Tamil in meiner Stadt“.
Es gibt sie nur mit dem Schalter im Customizer (theme_mod tamil_startseiten_proben, Standard aus). Ist er aus oder der
Wert unbekannt, steht exakt die normale Startseite da. Probenseiten tragen noindex und den Umschalter; jeder
Beitrags-Anreißer im neuen Bereich ist eine Bildkarte mit Titel im Bild und Punktbogen; die Werbeplätze nach F3 bleiben.
"""

import json
import re

import pytest

PROBEN = {"cover": "titelseite", "news": "nachrichten", "community": "stadt--oben"}
MERKMALE = ("probe-wahl", "oben--probe", "data-stadt-bereich", "stadt--oben", "assets/js/stadt.js", "probe-cover", "probe-news",
            "probe-community")


@pytest.fixture
def proben(wp_cli):
    """Schaltet die Proben für den Test ein oder aus und stellt danach den alten Stand des Schalters wieder her."""
    alt = wp_cli("echo wp_json_encode( get_theme_mod( 'tamil_startseiten_proben', null ) );").strip()

    def schalte(an: bool) -> None:
        wp_cli("set_theme_mod( 'tamil_startseiten_proben', '1' );" if an else "remove_theme_mod( 'tamil_startseiten_proben' );")

    yield schalte
    wp_cli(f"$a = json_decode( '{alt}' ); if ( null === $a ) {{ remove_theme_mod( 'tamil_startseiten_proben' ); }}"
           " else { set_theme_mod( 'tamil_startseiten_proben', $a ); } tamil_flush_auswahl();")


def _seite(wp, pfad: str) -> str:
    r = wp.get(pfad, headers={"Cache-Control": "no-cache"})
    assert r.status_code == 200, pfad
    return r.text


def _main(html: str) -> str:
    m = re.search(r"<main\b.*?</main>", html, re.S)
    assert m, "kein <main>"
    return m.group(0)


def _erster_abschnitt(html: str) -> str:
    """Vom Seitentitel bis zum Werbeplatz 01 (Leaderboard): der erste Abschnitt der Startseite."""
    start = html.index('<h1 class="nur-vorlesen">')
    return html[start:html.index('class="ad ad-leaderboard', start)]


def _stadt(html: str) -> str:
    m = re.search(r'<section class="stadt innen.*?</section>', html, re.S)
    assert m, "Abschnitt „Tamil in meiner Stadt“ fehlt"
    return m.group(0)


def _karten(html: str) -> list[str]:
    """Beitrags-Anreißer: <article> (tamil_anr_imbild) und Kino- bzw. Terminkarten (li.grafik--karte, bis zum Ende ihres Links)."""
    return re.findall(r"<article\b.*?</article>", html, re.S) + re.findall(r'<li[^>]*class="grafik grafik--karte".*?</a>', html, re.S)


def _plaetze(html: str) -> list[str]:
    return re.findall(r'class="ad ad-([a-z-]+)', html)


def _robots(wp_cli, probe: str, production: bool = True) -> dict:
    """Robots-Angaben der Startseite mit ?probe=…; mit production ohne das noindex des Testsystems."""
    code = ("add_filter( 'tamil_site_indexierbar', '__return_true' );" if production else "") + (
        "global $wp_query; $wp_query->is_home = true;"
        f" $_GET['probe'] = '{probe}';"
        " echo wp_json_encode( array( 'probe' => tamil_probe(), 'robots' => (object) apply_filters( 'wp_robots', array() ) ) );")
    return json.loads(wp_cli(code))


def test_schalter_aus_liefert_die_normale_startseite(wp, wp_cli, proben):
    proben(False)
    normal = _seite(wp, "/")
    for probe in PROBEN:
        seite = _seite(wp, f"/?probe={probe}")
        assert _main(seite) == _main(normal), f"Schalter aus: ?probe={probe} zeigt die normale Startseite"
        for merkmal in MERKMALE:
            assert merkmal not in seite, (probe, merkmal)
        stand = _robots(wp_cli, probe)
        assert stand["probe"] == "" and "noindex" not in stand["robots"], "Schalter aus: kein noindex durch die Probe"
    assert wp_cli("echo tamil_opt( 'startseiten_proben' );").strip() == "", "Standard: aus"


@pytest.mark.parametrize("probe", list(PROBEN))
def test_schalter_an_jede_probe_mit_kennklasse_stadt_noindex_und_umschalter(wp, wp_cli, proben, probe):
    proben(True)
    seite = _seite(wp, f"/?probe={probe}")
    assert f"probe-{probe}" in re.search(r"<body[^>]*>", seite).group(0), "Body-Klasse der Probe"
    assert re.search(rf'class="[^"]*\b{re.escape(PROBEN[probe])}\b', seite), "Kennklasse des ersten Abschnitts"
    stadt = _stadt(seite)
    assert 'id="meine-stadt"' in stadt and "Tamil in" in stadt and 'data-stadt-bereich' in stadt
    assert "Kino nach Stadt" in stadt and "Alle Termine" in stadt, "Links am Ende, auch ohne Skript"
    assert re.search(r'<div class="stadt__wahl"[^>]*\shidden', stadt), "Auswahlfeld erscheint erst mit Skript"
    assert "Musterstadt" not in stadt, "kein Eintrag aus dem Verzeichnis"
    for land in ("Deutschland", "Schweiz", "Österreich"):
        assert not re.search(rf"<option[^>]*>{land}</option>", stadt), "kein Land als Stadt"
    assert "geolocation" not in seite, "keine Standortabfrage"

    # Umschalter mit allen drei Proben und der normalen Startseite; die gezeigte Probe ist markiert
    wahl = re.search(r'<nav class="probe-wahl.*?</nav>', seite, re.S).group(0)
    for p in PROBEN:
        assert re.search(rf'href="[^"]*\?probe={p}"', wahl), p
    assert len(re.findall(r'aria-current="page"', wahl)) == 1 and re.search(rf'probe={probe}"[^>]*aria-current="page"', wahl)

    # noindex: im Kopf der Seite und, unabhängig vom Testsystem, aus dem Filter der Probe
    robots = re.search(r"<meta name=['\"]robots['\"] content=['\"]([^'\"]*)", seite)
    assert robots and "noindex" in robots.group(1)
    stand = _robots(wp_cli, probe)
    assert stand["probe"] == probe and stand["robots"].get("noindex") is True
    assert f'<link rel="canonical" href="{wp.url}/">' in seite, "Canonical bleibt die Startseite"
    assert wp.get(f"/?probe={probe}").headers.get("Cache-Control") == "no-store", "Probenseiten werden nicht zwischengespeichert"
    assert "Warum das wichtig ist" not in seite, "kein Etikett für ein Feld, das es nicht gibt"


def test_unbekannter_wert_und_andere_seiten_bleiben_normal(wp, wp_cli, proben):
    proben(True)
    normal = _seite(wp, "/")
    for wert in ("xyz", "", "Cover%20First", "cover%27"):
        seite = _seite(wp, f"/?probe={wert}")
        assert _main(seite) == _main(normal), wert
        assert "probe-wahl" not in seite and "data-stadt-bereich" not in seite
    assert "probe-wahl" not in normal and "data-stadt-bereich" not in normal, "die normale Startseite hat keinen Umschalter"
    assert _robots(wp_cli, "xyz")["probe"] == ""
    # nur die Startseite kennt Proben
    assert json.loads(wp_cli("$_GET['probe'] = 'cover'; echo wp_json_encode( tamil_probe() );")) == ""


@pytest.mark.parametrize("probe", list(PROBEN))
def test_jede_karte_mit_bild_titel_im_bild_und_punktbogen_ohne_dubletten(wp, proben, probe):
    proben(True)
    seite = _seite(wp, f"/?probe={probe}")
    oben = _erster_abschnitt(seite)
    for name, bereich in (("erster Abschnitt", oben), ("Tamil in meiner Stadt", _stadt(seite))):
        karten = _karten(bereich)
        assert karten, f"{name}: keine Karten"
        for karte in karten:
            kurz = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", karte))[:80]
            rahmen = re.search(r'<div class="rahmen.*', karte, re.S)
            assert rahmen and "<img" in rahmen.group(0), f"{name}: Karte ohne Bild: {kurz}"
            assert re.search(r'<div class="imbild">.*?<h[234] class="titel', rahmen.group(0), re.S), f"{name}: Titel nicht im Bild: {kurz}"
            assert 'class="signatur-ecke' in rahmen.group(0), f"{name}: Punktbogen fehlt: {kurz}"
            assert 'class="anr imbild-anr" href="' in karte, f"{name}: Karte ist kein Link: {kurz}"
    # kein Beitrag doppelt im ersten Abschnitt (Rubrikkacheln sind Navigation und zählen nicht)
    ziele = re.findall(r'class="anr imbild-anr" href="([^"]+)"', oben)
    assert len(ziele) >= 8 and len(ziele) == len(set(ziele)), sorted(z for z in ziele if ziele.count(z) > 1)
    # keine leeren Etiketten
    assert not re.search(r"<dd>\s*</dd>", seite) and not re.search(r"Quelle:\s*</p>", seite)


@pytest.mark.parametrize("probe", list(PROBEN))
def test_werbeplaetze_nach_f3_bleiben_an_ihrem_ort(wp, proben, probe):
    proben(True)
    normal = _seite(wp, "/")
    seite = _seite(wp, f"/?probe={probe}")
    assert _plaetze(seite) == _plaetze(normal) and {"leaderboard", "billboard", "footer"} <= set(_plaetze(seite))
    haupt = _main(seite)
    # nichts über dem ersten Beitrag; das Leaderboard direkt nach den Rubrikkacheln, vor „Diese Woche“
    assert haupt.index('class="ad ') > haupt.index("<article"), "keine Anzeige über dem ersten Beitrag"
    kacheln = haupt.index('<nav class="kacheln"')
    board = haupt.index('class="ad ad-leaderboard')
    assert kacheln < board < haupt.index('id="diese-woche"')
    assert "<article" not in haupt[haupt.index("</nav>", kacheln):board], "zwischen Rubrikkacheln und Leaderboard steht kein Beitrag"
    assert 'class="ad ' not in _stadt(seite), "keine Anzeige in „Tamil in meiner Stadt“"
    if "kueche" in haupt:
        assert haupt.index('id="kueche"') < haupt.index('class="ad ad-billboard'), "Billboard nach „Küche“"


def test_community_first_laesst_den_ersten_abschnitt_wie_er_ist(wp, proben):
    proben(True)
    ziele = r'class="anr imbild-anr" href="([^"]+)"'
    normal = re.search(r'<div class="innen oben">.*?</nav>\s*</div>', _seite(wp, "/"), re.S).group(0)
    seite = _seite(wp, "/?probe=community")
    probe = re.search(r'<div class="innen oben">.*?</nav>\s*</div>', seite, re.S).group(0)
    assert re.findall(ziele, probe) == re.findall(ziele, normal), "Aufmacher, Nebenstücke und Meldungen wie auf der Startseite"
    assert seite.index('id="meine-stadt"') < seite.index('<div class="innen oben">'), "der Abschnitt steht ganz oben"
    # die Beiträge des Abschnitts kommen nicht noch einmal im ersten Abschnitt darunter
    assert not set(re.findall(ziele, _stadt(seite))) & set(re.findall(ziele, probe))
    for p in ("cover", "news"):
        s = _seite(wp, f"/?probe={p}")
        assert s.index('class="ad ad-leaderboard') < s.index('id="meine-stadt"') < s.index('id="diese-woche"'), p


def test_news_first_keine_erfundene_aktualitaet(wp, wp_cli, proben):
    proben(True)
    # Zeittext: heute und gestern mit Uhrzeit, älter nur das Datum
    heute, gestern, alt = json.loads(wp_cli(
        "$j = time(); echo wp_json_encode( array( tamil_zeit_text( $j ), tamil_zeit_text( strtotime( current_time( 'Y-m-d' ) . ' 12:00:00 ' . wp_timezone_string() ) - DAY_IN_SECONDS ),"
        " tamil_zeit_text( $j - 9 * DAY_IN_SECONDS ) ) );"))
    assert re.fullmatch(r"Heute, \d\d:\d\d Uhr", heute) and re.fullmatch(r"Gestern, \d\d:\d\d Uhr", gestern)
    assert re.fullmatch(r"\d{1,2}\. \S+ \d{4}", alt), "älter: Datum ohne Uhrzeit"

    seite = _seite(wp, "/?probe=news")
    folge = re.search(r'<ol class="zeitfolge">.*?</ol>', seite, re.S).group(0)
    zeiten = re.findall(r'<time datetime="([^"]+)">([^<]+)</time>', folge)
    assert 1 <= len(zeiten) <= 5 and [z[0] for z in zeiten] == sorted((z[0] for z in zeiten), reverse=True), "streng nach Zeit, neueste zuerst"
    tag = wp_cli("echo current_time( 'Y-m-d' );").strip()
    von_heute = any(z[0].startswith(tag) for z in zeiten)
    titel = re.search(r'id="t-zeitfolge">([^<]+)<', seite).group(1)
    assert titel == ("Heute wichtig" if von_heute else "Zuletzt erschienen")
    for iso, text in zeiten:
        assert ("Uhr" in text) == bool(re.match(r"(Heute|Gestern),", text)), "Uhrzeit nur bei heute und gestern"
    assert len(re.findall(r'<li class="zeitfolge__eintrag', folge)) == len(zeiten), "jede Zeile hat ihre Zeit"


def test_news_first_heute_wichtig_nur_mit_beitrag_von_heute(wp, wp_cli, proben):
    proben(True)
    ids, bilder = [], []
    try:
        for n in (1, 2):  # zwei von heute: einer wird Aufmacher, der andere steht in der Zeitfolge
            bild = int(wp_cli(
                "$id = wp_insert_attachment( array( 'post_mime_type' => 'image/jpeg', 'post_title' => 'proben-test', 'post_status' => 'inherit' ), 'proben-test.jpg' );"
                " wp_update_attachment_metadata( $id, array( 'width' => 1600, 'height' => 1200, 'file' => 'proben-test.jpg', 'sizes' => array() ) ); echo $id;"))
            bilder.append(bild)
            ids.append(int(wp_cli(
                f"$p = wp_insert_post( array( 'post_title' => 'Proben-Test heute {n}', 'post_status' => 'publish', 'post_content' => '<p>Ein Satz zum Test.</p>',"
                f" 'post_date' => wp_date( 'Y-m-d H:i:s', time() - {n * 60} ) ) ); set_post_thumbnail( $p, {bild} ); echo $p;")))
        seite = _seite(wp, "/?probe=news")
        assert re.search(r'id="t-zeitfolge">Heute wichtig<', seite)
        folge = re.search(r'<ol class="zeitfolge">.*?</ol>', seite, re.S).group(0)
        assert re.search(r">Heute, \d\d:\d\d Uhr</time>", folge) and "Proben-Test heute" in folge
    finally:
        for pid in ids:
            wp_cli(f"wp_delete_post( {pid}, true );")
        for aid in bilder:
            wp_cli(f"wp_delete_attachment( {aid}, true );")
        wp_cli("tamil_flush_auswahl();")
    assert re.search(r'id="t-zeitfolge">(Heute wichtig|Zuletzt erschienen)<', _seite(wp, "/?probe=news"))


def test_staedte_aus_freitext_ohne_laender_und_einrichtungen(wp_cli):
    def namen(ort: str) -> list[str]:
        return list(json.loads(wp_cli(f"echo wp_json_encode( array_values( tamil_stadt_namen( '{ort}' ) ) );")))

    assert namen("Viersen, Arnsberg, Hannover, Stuttgart und Landau, Deutschland") == ["Viersen", "Arnsberg", "Hannover", "Stuttgart", "Landau"]
    assert namen("Deutschland") == [] and namen("Kanton Solothurn") == [] and namen("Sri Lanka") == []
    assert namen("CH-4056 Basel, Schweiz") == ["Basel"] and namen("Lysbüchelplatz 1, 4056 Basel") == ["Basel"]
    assert namen("Bern (Bundesplatz) / Zürich; Tamilalayams") == ["Bern", "Zürich"]


def test_kino_nur_mit_vorstellung_ab_heute(wp_cli):
    code = ("$h = '2026-11-21'; echo wp_json_encode( array("
            " (bool) tamil_stadt_kino_laeuft( array( 'termine' => array( '2026-10-16T19:30', '2026-11-20T19:30' ) ), $h ),"
            " tamil_stadt_kino_laeuft( array( 'termine' => array( '2026-11-20T19:30', '2026-11-21T19:30', '2026-11-23T16:00' ) ), $h )['termine'] ?? null,"
            " (bool) tamil_stadt_kino_laeuft( array( 'von' => '2026-11-19', 'bis' => '2026-11-20' ), $h ),"
            " (bool) tamil_stadt_kino_laeuft( array( 'von' => '2026-11-19', 'bis' => '2026-11-25' ), $h ),"
            " (bool) tamil_stadt_kino_laeuft( array( 'von' => '2026-11-19' ), $h ) ) );")
    assert json.loads(wp_cli(code)) == [False, ["2026-11-21T19:30", "2026-11-23T16:00"], False, True, True]
    # keine vergangenen Vorstellungen oder Termine im Abschnitt, jede Stadt der Auswahl hat mindestens ein gefülltes Fach
    d = json.loads(wp_cli(
        "$d = tamil_stadt_daten(); $h = current_time( 'Y-m-d' ); $alt = 0;"
        " foreach ( $d['termine'] as $t ) { if ( substr( (string) get_post_meta( $t['id'], 'event_datum', true ), 0, 10 ) < $h ) { ++$alt; } }"
        " $voll = array(); foreach ( $d['staedte'] as $s => $n ) { $z = 0;"
        "   foreach ( $d['filme'] as $f ) { $z += isset( $f['orte'][ $s ] ) ? 1 : 0; }"
        "   foreach ( $d['termine'] as $t ) { $z += $t['stadt'] === $s ? 1 : 0; }"
        "   foreach ( $d['geschichten'] as $g ) { $z += in_array( $s, $g['staedte'], true ) ? 1 : 0; } $voll[ $s ] = $z; }"
        " echo wp_json_encode( array( 'alt' => $alt, 'voll' => (object) $voll ) );"))
    assert d["alt"] == 0 and all(z >= 1 for z in d["voll"].values()), d
