"""Theme tamil 3.16.0/3.16.1: Startseiten-Proben (inc/proben.php, template-parts/home/probe-*.php, stadt.php; TML-W06).

Drei Entwürfe für den ersten Bildschirm (/?probe=cover, news, community) und der Abschnitt „Tamil in meiner Stadt“.
Es gibt sie nur mit dem Schalter im Customizer (theme_mod tamil_startseiten_proben, Standard aus). Ist er aus oder der
Wert unbekannt, steht exakt die normale Startseite da. Probenseiten tragen noindex und den Umschalter; jeder
Beitrags-Anreißer im neuen Bereich ist eine Bildkarte mit Titel im Bild und Punktbogen; die Werbeplätze nach F3 bleiben.

3.16.1 (Korrekturen aus der unabhängigen Kritik vom 22.11.2026, am Ende der Datei): eine erklärte Kinozahl, vergangene
Termine als „war am …“, „Zuletzt erschienen“ nennt die ausgelassene Titelgeschichte, ein für die Stadt leeres Fach
zeigt den Bestand aus allen Städten, Städte mit zwei älteren Beiträgen sind wählbar, unter „Alle Städte“ nur
Geschichten der letzten 60 Tage.
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


# --- 3.16.1: Wahrheits- und Datenfehler aus der Kritik vom 22.11.2026 ---------------------------------------------------

@pytest.fixture
def beitraege(wp_cli):
    """Legt Beiträge für einen Test an (Titel, Alter in Tagen, Meta) und löscht sie danach wieder."""
    ids: list[int] = []

    def lege(titel: str, tage: int = 0, meta: dict | None = None) -> int:
        setzen = "".join(f" update_post_meta( $p, '{k}', {v} );" for k, v in (meta or {}).items())
        pid = int(wp_cli(
            f"$p = wp_insert_post( array( 'post_title' => '{titel}', 'post_status' => 'publish', 'post_content' => '<p>Ein Satz zum Test.</p>',"
            f" 'post_date' => wp_date( 'Y-m-d H:i:s', time() - {tage} * DAY_IN_SECONDS - 60 ) ) );{setzen} echo $p;"))
        ids.append(pid)
        return pid

    yield lege
    if ids:
        wp_cli(f"foreach ( array( {', '.join(map(str, ids))} ) as $id ) {{ wp_delete_post( $id, true ); }} tamil_flush_auswahl();")


def _tag(tage: int) -> str:
    """PHP-Ausdruck für heute plus `tage` als JJJJ-MM-TT (Zeitzone der Website)."""
    return f"wp_date( 'Y-m-d', strtotime( current_time( 'Y-m-d' ) . ' {tage:+d} days' ) )"


def test_kinozahl_im_stadtbereich_sagt_was_sie_zaehlt(wp, wp_cli, proben, beitraege):
    """P0-1: „Diese Woche“ nennt alle Kinos der Kinoliste, der Stadtbereich nur die mit Vorstellung ab heute. Weichen
    die Zahlen ab, steht im Stadtbereich „ab heute noch N von M Kinos“ und M ist die Zahl aus „Diese Woche“."""
    proben(True)
    kino = lambda stadt, tage: f"array( 'kino' => 'Probekino {stadt}', 'stadt' => '{stadt}', 'land' => 'DE', 'termine' => array( {_tag(tage)} ) )"  # noqa: E731
    beitraege("Kinoliste Zahlenfilm Qwertz", 0, {"kino_fakten": "wp_json_encode( array( 'film' => 'Zahlenfilm Qwertz', 'kinos' => array( "
                                                  f"{kino('Altdorf', -1)}, {kino('Altheim', -1)}, {kino('Neustadt', 1)} ) ) )"})
    beitraege("Kinoliste Ganzfilm Asdfgh", 0, {"kino_fakten": "wp_json_encode( array( 'film' => 'Ganzfilm Asdfgh', 'kinos' => array( "
                                                f"{kino('Neustadt', 0)}, {kino('Neuheim', 2)} ) ) )"})
    wp_cli("tamil_flush_auswahl();")
    seite = _seite(wp, "/?probe=cover")

    def zahl(bereich: str, film: str) -> str:
        karte = next(k for k in _karten(bereich) if f">{film}<" in k)
        return re.sub(r"<[^>]+>", "", re.search(r'<p class="meta">.*?</p>', karte, re.S).group(0))

    woche = seite[seite.index('id="diese-woche"'):]
    assert "3 Kinos" in zahl(woche, "Zahlenfilm Qwertz"), "„Diese Woche“ zählt alle Kinos der Liste"
    stadt = zahl(_stadt(seite), "Zahlenfilm Qwertz")
    assert "ab heute noch 1 von 3 Kinos" in stadt, f"Stadtbereich nennt Zählweise und Gesamtzahl: {stadt}"
    assert not re.search(r"\b1 Kino\b", stadt), "nicht „1 Kino“ ohne Erklärung neben „3 Kinos“"
    # laufen noch alle Kinos, stehen überall dieselben Worte
    assert "2 Kinos" in zahl(_stadt(seite), "Ganzfilm Asdfgh") and "ab heute" not in zahl(_stadt(seite), "Ganzfilm Asdfgh")
    assert "2 Kinos" in zahl(woche, "Ganzfilm Asdfgh")
    # die Städte ohne Vorstellung ab heute sind nicht wählbar, die mit Vorstellung schon
    auswahl = re.findall(r"<option[^>]*>([^<]+)</option>", _stadt(seite))
    assert "Neustadt" in auswahl and "Neuheim" in auswahl and "Altdorf" not in auswahl and "Altheim" not in auswahl


def test_vergangener_termin_steht_als_vergangen_im_kontextfeld(wp_cli, beitraege):
    """P0-2: Das Kontextfeld der Titelgeschichte nennt einen Termin vor heute nie wie eine Ankündigung."""
    def feld(tage: int, ende: int | None = None) -> str:
        meta = {"event_datum": _tag(tage), "event_ort": "'Stadtbibliothek, 5000 Aarau'"} | ({"event_ende": _tag(ende)} if ende is not None else {})
        pid = beitraege(f"Terminprobe {tage} {ende}", 3, meta)
        html = wp_cli(f"echo tamil_kontext( {pid}, array( 'form' => 'cover' ) );")
        return re.sub(r"<[^>]+>", "", re.search(r'kontext__angabe--termin"><dt>Termin</dt><dd>(.*?)</dd>', html, re.S).group(1))

    gestern, heute, morgen = feld(-1), feld(0), feld(1)
    assert re.fullmatch(r"war am \S+, \d{1,2}\. \S+ \d{4}", gestern), gestern
    assert "war" not in heute and "war" not in morgen, "heute und kommende Termine bleiben Ankündigung"
    assert re.fullmatch(r"\S+, \d{1,2}\. \S+ \d{4}", morgen), morgen
    assert feld(-3, -1).startswith("war vom "), "Zeitraum, der gestern endete"
    assert "war" not in feld(-3, 0), "Zeitraum, der heute noch läuft"
    assert json.loads(wp_cli(f"echo wp_json_encode( array( tamil_termin_vorbei( {_tag(-1)} ), tamil_termin_vorbei( {_tag(0)} ),"
                             f" tamil_termin_vorbei( {_tag(-2)}, {_tag(0)} ), tamil_termin_vorbei( '' ) ) );")) == [True, False, False, False]


def test_news_first_nennt_die_ausgelassene_titelgeschichte(wp, wp_cli, proben):
    """P0-3: „Zuletzt erschienen“ lässt den neuesten Beitrag nicht stillschweigend aus. Ist er die Titelgeschichte
    (steht daneben), sagt eine Zeile unter der Überschrift das und führt zu ihr."""
    proben(True)
    bild = int(wp_cli(
        "$id = wp_insert_attachment( array( 'post_mime_type' => 'image/jpeg', 'post_title' => 'proben-test', 'post_status' => 'inherit' ), 'proben-test.jpg' );"
        " wp_update_attachment_metadata( $id, array( 'width' => 1600, 'height' => 1200, 'file' => 'proben-test.jpg', 'sizes' => array() ) ); echo $id;"))
    pid = int(wp_cli("$p = wp_insert_post( array( 'post_title' => 'Proben-Test neueste Titelgeschichte', 'post_status' => 'publish',"
                     f" 'post_content' => '<p>Ein Satz zum Test.</p>' ) ); set_post_thumbnail( $p, {bild} ); echo $p;"))
    try:
        v = json.loads(wp_cli("$v = tamil_probe_vorrat(); echo wp_json_encode( array( 'lead' => $v['lead'], 'link' => get_permalink( $v['lead'] ),"
                              " 'zeit' => tamil_zeit_text( (int) get_post_timestamp( $v['lead'] ) ) ) );"))
        assert v["lead"] == pid, "der neueste Beitrag mit Foto ist der Aufmacher"
        seite = _seite(wp, "/?probe=news")
        abschnitt = re.search(r'<section class="nachrichten__folge".*?</section>', seite, re.S).group(0)
        assert v["link"] not in abschnitt, "die Titelgeschichte steht nicht in der Liste"
        hinweis = re.search(r'<p class="zeitfolge__hinweis">(.*?)</p>', abschnitt, re.S)
        assert hinweis, "Liste ohne den neuesten Beitrag braucht den Hinweis"
        assert f"Nicht in dieser Liste: die Titelgeschichte ({v['zeit']})." in hinweis.group(1) and 'href="#titelgeschichte"' in hinweis.group(1)
        assert abschnitt.index("zeitfolge__hinweis") < abschnitt.index('<ol class="zeitfolge">'), "vor der Liste, unter der Überschrift"
        ziel = re.search(r'<div class="nachrichten__seite" id="titelgeschichte">\s*<article[^>]*>.*?</article>', seite, re.S)
        assert ziel and v["link"] in ziel.group(0), "der Link führt zur Titelgeschichte"
    finally:
        wp_cli(f"wp_delete_post( {pid}, true ); wp_delete_attachment( {bild}, true ); tamil_flush_auswahl();")


@pytest.fixture
def staedte_bestand(wp_cli, beitraege):
    """Zwei alte Beiträge aus „Altenhausen“ (200 Tage), davor 26 neuere Beiträge mit Ort ohne Stadt, dazu ein frischer
    aus „Frischdorf“ und einer aus „Altenhausen und Frischdorf“ von vor 70 Tagen."""
    alt = [beitraege(f"Stadtprobe Altenhausen {n}", 200 + n, {"ort": "'Altenhausen, Deutschland'"}) for n in (1, 2)]
    ids = wp_cli("$ids = array(); for ( $i = 0; $i < 26; $i++ ) { $p = wp_insert_post( array( 'post_title' => 'Stadtprobe Füller ' . $i,"
                 " 'post_status' => 'publish', 'post_content' => '<p>x</p>', 'post_date' => wp_date( 'Y-m-d H:i:s', time() - ( 100 + $i ) * DAY_IN_SECONDS ) ) );"
                 " update_post_meta( $p, 'ort', 'Deutschland' ); $ids[] = $p; } echo wp_json_encode( $ids );")
    frisch = beitraege("Stadtprobe Frischdorf", 2, {"ort": "'Frischdorf'"})
    mittel = beitraege("Stadtprobe beide Orte", 70, {"ort": "'Altenhausen und Frischdorf'"})
    wp_cli("tamil_flush_auswahl();")
    yield {"alt": alt, "frisch": frisch, "mittel": mittel}
    wp_cli(f"foreach ( json_decode( '{ids.strip()}' ) as $id ) {{ wp_delete_post( (int) $id, true ); }} tamil_flush_auswahl();")


def test_stadt_mit_zwei_aelteren_beitraegen_ist_waehlbar(wp, wp_cli, proben, staedte_bestand):
    """P1-a: Jede Stadt mit Kino ab heute, kommendem Termin oder zwei Beiträgen ist wählbar, auch wenn ihre Beiträge
    nicht unter den 24 neuesten mit Ort stehen (bis 3.16.0 wurden nur diese gezählt)."""
    proben(True)
    stadt = _stadt(_seite(wp, "/?probe=community"))
    auswahl = re.findall(r'<option value="([^"]*)">', stadt)
    assert "altenhausen" in auswahl, "drei Beiträge, zwei davon 200 Tage alt"
    assert "frischdorf" in auswahl, "zwei Beiträge"
    assert json.loads(wp_cli("echo wp_json_encode( TAMIL_STADT_VORRAT );")) >= 100
    # die Karten der Stadt stehen im HTML (höchstens drei je Stadt), damit die Wahl etwas zeigt
    karten = re.findall(r"<article[^>]*data-stadt-karte[^>]*>", stadt)
    assert 2 <= sum("altenhausen" in re.search(r'data-stadt="([^"]*)"', k).group(1).split() for k in karten) <= 3


def test_alle_staedte_zeigt_nur_geschichten_der_letzten_60_tage(wp, wp_cli, proben, staedte_bestand):
    """P1-b: Unter „Alle Städte“ (so steht der Abschnitt ohne Skript im HTML) stehen nur die neuesten Geschichten mit
    Ortsbezug, höchstens 60 Tage alt; ältere warten verborgen auf die Wahl ihrer Stadt."""
    proben(True)
    assert json.loads(wp_cli("echo wp_json_encode( TAMIL_STADT_TAGE );")) == 60
    d = json.loads(wp_cli("$h = strtotime( current_time( 'Y-m-d' ) . ' 00:00:00 ' . wp_timezone_string() ); echo wp_json_encode( array_map( static fn( $g ) => array("
                          " 'id' => $g['id'], 'alle' => $g['alle'], 'tage' => (int) floor( ( $h - get_post_timestamp( $g['id'] ) ) / DAY_IN_SECONDS ),"
                          " 'link' => get_permalink( $g['id'] ) ), tamil_stadt_daten()['geschichten'] ) );"))
    nach_id = {g["id"]: g for g in d}
    assert nach_id[staedte_bestand["frisch"]]["alle"] is True
    assert all(nach_id[i]["alle"] is False for i in (*staedte_bestand["alt"], staedte_bestand["mittel"])), "über 60 Tage: nicht unter „Alle Städte“"
    assert all(g["tage"] < 60 for g in d if g["alle"]) and 1 <= sum(g["alle"] for g in d) <= 3
    assert [g["tage"] for g in d] == sorted(g["tage"] for g in d), "neueste zuerst"

    fach = re.search(r'<div class="stadt__fach stadt__fach--geschichten".*?</section>', _stadt(_seite(wp, "/?probe=community")), re.S).group(0)
    assert not re.match(r"<div[^>]*\shidden", fach), "es gibt junge Geschichten: das Fach steht da"
    assert ">Aus den Städten<" in fach, "unter „Alle Städte“ heißt das Fach nicht „Aus der Stadt“"
    for karte in re.findall(r"<article[^>]*data-stadt-karte[^>]*>.*?</article>", fach, re.S):
        g = next(x for x in d if x["link"] in karte)
        kopf = re.match(r"<article[^>]*>", karte).group(0)
        assert ("data-alle" in kopf) == g["alle"] and (" hidden" in kopf) == (not g["alle"]), (g, kopf)


def test_duenne_stadt_fuellt_leere_faecher_mit_dem_bestand_aus_allen_staedten(wp, proben, staedte_bestand, beitraege):
    """P0-4: Mit gespeicherter Stadt besteht der Abschnitt nie nur aus Leersätzen. Ein Fach ohne Inhalt für die Stadt
    zeigt den Bestand aus „Alle Städte“ und sagt es darüber; ein Leersatz steht nur, wenn es nirgends etwas gibt."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright für Python fehlt")
    proben(True)
    beitraege("Kinoliste Stadtfilm Yxcvb", 0, {"kino_fakten": "wp_json_encode( array( 'film' => 'Stadtfilm Yxcvb', 'kinos' => array( array("
                                                f" 'kino' => 'Probekino', 'stadt' => 'Kinohausen', 'land' => 'DE', 'termine' => array( {_tag(1)} ) ) ) ) )"})
    messen = """() => { const b = document.querySelector('[data-stadt-bereich]'); const sichtbar = e => !!e && e.getClientRects().length > 0;
        return { titel: b.querySelector('[data-stadt-name]').textContent, status: b.querySelector('[data-stadt-status]').textContent,
          faecher: Object.fromEntries([...b.querySelectorAll('[data-fach]')].map(f => [f.dataset.fach, {
            sichtbar: sichtbar(f), karten: [...f.querySelectorAll('[data-stadt-karte]')].filter(sichtbar).map(k => k.dataset.stadt.split(' ')),
            alle: f.querySelectorAll('[data-stadt-karte][data-alle]').length, max: +f.dataset.max,
            ersatz: sichtbar(f.querySelector('[data-ersatz]')) ? f.querySelector('[data-ersatz]').textContent : '',
            art: f.querySelector('.stadt__art').textContent,
            orte: sichtbar(f.querySelector('.grafik__orte')) }])),
          leer: [...b.querySelectorAll('[data-leer]')].filter(sichtbar).map(p => p.dataset.leer),
          fett: [...b.querySelectorAll('.stadt__leer, .stadt__leer a')].map(e => +getComputedStyle(e).fontWeight) }; }"""
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as fehler:  # noqa: BLE001 – ohne Browser keine Messung
            pytest.skip(f"Chromium nicht startbar: {fehler}")
        for breite in (390, 1440):
            kontext = browser.new_context(viewport={"width": breite, "height": 844})
            kontext.add_init_script("try { localStorage.setItem('tamil_stadt', JSON.stringify({ slug: 'altenhausen', name: 'Altenhausen' })); } catch (e) {}")
            seite = kontext.new_page()
            seite.goto(f"{wp.url}/?probe=community", wait_until="domcontentloaded")
            m = seite.evaluate(messen)
            assert m["titel"] == "Altenhausen", "die gespeicherte Stadt ist gewählt"
            f = m["faecher"]
            # Geschichten: die eigenen der Stadt, ohne Ersatzzeile
            assert f["geschichten"]["sichtbar"] and f["geschichten"]["ersatz"] == "" and f["geschichten"]["art"] == "Aus der Stadt"
            assert f["geschichten"]["karten"] and all("altenhausen" in k for k in f["geschichten"]["karten"])
            # Kino und Termine: Altenhausen hat nichts, also der Bestand aus allen Städten mit Beschriftung
            assert f["kino"]["alle"] >= 1 and f["kino"]["sichtbar"], (breite, f["kino"])
            assert len(f["kino"]["karten"]) == min(f["kino"]["max"], f["kino"]["alle"])
            assert f["kino"]["ersatz"] == "In Altenhausen gerade kein Film. Im Kino anderswo:"
            assert f["kino"]["orte"], "im aufgefüllten Fach steht, in welchen Städten der Film läuft"
            if f["termine"]["alle"]:
                assert f["termine"]["sichtbar"] and f["termine"]["ersatz"] == "Für Altenhausen steht kein Termin im Kalender. Termine anderswo:"
                assert "termine" not in m["leer"]
            else:
                assert m["leer"] == ["termine"], "Leersatz nur, wenn es auch anderswo nichts gibt"
            assert "kino" not in m["leer"] and "geschichten" not in m["leer"]
            assert max(m["fett"]) <= 400, "Leersätze und ihre Links sind nicht fett"
            # eine Stadt mit Kino, aber ohne Geschichte: Geschichten von anderswo, beschriftet
            seite.select_option("#stadt-wahl", "kinohausen")
            seite.wait_for_function("document.querySelector('[data-stadt-status]').textContent.startsWith('Kinohausen')")
            m = seite.evaluate(messen)
            f = m["faecher"]
            assert f["kino"]["ersatz"] == "" and all("kinohausen" in k for k in f["kino"]["karten"]) and not f["kino"]["orte"]
            assert f["geschichten"]["sichtbar"] and f["geschichten"]["art"] == "Aus den Städten"
            assert f["geschichten"]["ersatz"] == "Aus Kinohausen haben wir noch keine Geschichte. Aus anderen Städten:"
            assert m["status"] == "Kinohausen: 1 Film im Kino, kein Termin, keine Geschichte.", "die Ansage zählt nur, was aus der Stadt selbst kommt"
            # zurück zu „Alle Städte“: keine Ersatzzeilen
            seite.select_option("#stadt-wahl", "")
            seite.wait_for_function("document.querySelector('[data-stadt-status]').textContent.startsWith('Alle Städte')")
            assert all(x["ersatz"] == "" for x in seite.evaluate(messen)["faecher"].values())
            kontext.close()
        browser.close()
