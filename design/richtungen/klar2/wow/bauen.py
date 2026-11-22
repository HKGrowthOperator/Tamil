#!/usr/bin/env python3
"""Baut die beiden Wow-Vorschauen aus den Punktdaten des Signets und den eingesammelten echten Inhalten.

    python3 design/richtungen/klar2/wow/bauen.py        (vom Repo-Root)

Eingaben:  design/signature/daten/punkte.json   238 Punkte „Tamil Dots 04A“ (Master)
           daten/startseite.json                 Aufmacher und Karten der Testseite (Titel, Datum, Nachweis)
           daten/meldungen-2026.json             alle Meldungen 2026 der Testseite (Titel, Datum, Rubrik, Link)
Ausgaben:  punkt-zum-bild/index.html, jahr-in-punkten/index.html
Nur Standardbibliothek. Nichts wird erfunden: fehlt ein Wert in den Daten, bricht das Skript ab.
"""
import html
import json
import math
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parents[3]
TEST = "https://tamil-web.167.233.76.202.sslip.io"
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
          "November", "Dezember"]
e = html.escape


def punkte():
    """Master-Punkte, auf die Breite 1 normiert: x, y, große und kleine Halbachse, Drehung (Bogenmaß), Lauf 0..1, Ton."""
    roh = json.loads((ROOT / "design/signature/daten/punkte.json").read_text())["master"]
    x0 = min(p[0] - p[2] for p in roh)
    x1 = max(p[0] + p[2] for p in roh)
    y0 = min(p[1] - p[2] for p in roh)
    y1 = max(p[1] + p[2] for p in roh)
    b, h = x1 - x0, y1 - y0
    aus = []
    for x, y, ra, rb, grad, ton in roh:
        # Reihenfolge des Aufbaus wie in design/signature/tamil_dots.py: vom großen Fuß links zum Auslauf rechts
        lauf = 0.88 * (x - x0) / b + 0.12 * (1 - (y - y0) / h)
        aus.append(((x - x0) / b, (y - y0) / b, ra / b, rb / b, math.radians(grad), lauf, ton))
    aus.sort(key=lambda p: p[5])
    return aus, h / b


# Schriften wie im Theme (theme.json): WordPress gibt diese Regeln aus, im Theme-CSS selbst stehen sie nicht.
SCHRIFTEN = """@font-face { font-family: "Libre Franklin"; font-style: normal; font-weight: 100 900; font-display: swap; src: url("../assets/fonts/libre-franklin-latin-wght-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
@font-face { font-family: "Libre Franklin"; font-style: normal; font-weight: 100 900; font-display: swap; src: url("../assets/fonts/libre-franklin-latin-ext-wght-normal.woff2") format("woff2"); unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF; }
@font-face { font-family: Catamaran; font-style: normal; font-weight: 100 900; font-display: swap; src: url("../assets/fonts/catamaran-tamil.woff2") format("woff2"); unicode-range: U+0964-0965, U+0B82-0BFA, U+200C-200D, U+20B9, U+25CC; }
"""

def kopf(titel, beschreibung, extra_css):
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschreibung)}">
<link rel="preload" href="../assets/fonts/libre-franklin-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../assets/css/theme.css">
<style>
{SCHRIFTEN}{extra_css}
</style>
"""


def seitenkopf():
    rubriken = [("Nachrichten", "/category/news/"), ("Entertainment", "/category/entertainment/"),
                ("Events", "/events/"), ("Community", "/category/community/"), ("Küche", "/category/kueche/"),
                ("Kino", "/category/kino/"), ("Sport", "/category/sport/"), ("Kultur", "/category/kultur/"),
                ("Kontakt", "/kontakt/")]
    li = "\n".join(f'\t\t\t<li><a href="{TEST}{u}">{n}</a></li>' for n, u in rubriken)
    return f"""<a class="skip" href="#inhalt">Zum Inhalt</a>
<div class="site">
<header class="kopf">
	<div class="kopfzeile">
		<div class="innen kopfzeile__innen">
			<time class="kopfzeile__datum" datetime="2026-11-21">Samstag, 21. November 2026</time>
			<a class="kopfzeile__suche" href="{TEST}/?s">Suche</a>
		</div>
	</div>
	<div class="innen">
		<a class="kopf__logo" href="{TEST}/" rel="home"><img src="../assets/img/logo.webp" srcset="../assets/img/logo.webp 1x, ../assets/img/logo-2x.webp 2x" width="199" height="72" alt="tamil.de"></a>
	</div>
</header>
<nav class="band" aria-label="Rubriken">
	<div class="band__innen">
		<ul class="band__liste">
{li}
		</ul>
		<span class="band__signet" aria-hidden="true"><span class="signatur signatur--band" aria-hidden="true"></span></span>
	</div>
</nav>
"""


def seitenfuss(nachweise, hinweis):
    nw = ""
    if nachweise:
        nw = ('<div class="innen vorschau-nachweise"><h2>Bildnachweise dieser Seite</h2><ul class="nachweise">'
              + "".join(f"<li>{e(n)}</li>" for n in nachweise) + "</ul></div>")
    return f"""<footer class="fuss">
	<div class="innen fuss__innen">
		<div class="fuss__marke">
			<a class="fuss__logo" href="{TEST}/" rel="home"><img src="../assets/img/logo.webp" srcset="../assets/img/logo.webp 1x, ../assets/img/logo-2x.webp 2x" width="199" height="72" alt="tamil.de" loading="lazy"></a>
			<p class="fuss__satz">Nachrichten, Kino und Community für Tamilen in DE, AT und CH</p>
		</div>
	</div>
	{nw}
	<div class="innen"><p class="fuss__recht"><span>{e(hinweis)}</span></p></div>
</footer>
</div>
"""


# ---------------------------------------------------------------------------------------------------------------------
# Vorschau 1: Punkt für Punkt zum Bild
# ---------------------------------------------------------------------------------------------------------------------

CSS_1 = """
/* --- Nur Vorschau: Umschaltleiste, nicht Teil des Entwurfs --- */
.vorschau-leiste { background: #F2F2F2; border-bottom: 1px solid #D9D9D9; font-size: 13px; color: #000; }
.vorschau-leiste__innen { display: flex; flex-wrap: wrap; align-items: center; gap: 0 4px; max-width: var(--breite); margin: 0 auto; padding: 0 var(--rand); }
.vorschau-leiste__name { margin-right: 8px; color: #555; }
.vorschau-leiste button {
  font: inherit; color: inherit; background: none; border: 0; border-bottom: 3px solid transparent; min-height: 44px;
  padding: 0 10px; cursor: pointer;
}
.vorschau-leiste button[aria-pressed="true"] { border-bottom-color: #660000; font-weight: 650; }
.vorschau-leiste button:focus-visible { outline: 3px solid #660000; outline-offset: -3px; }
.vorschau-nachweise { padding-block: 8px 20px; font-size: 13px; color: #555; }
.vorschau-nachweise h2 { font-size: 13px; font-weight: 600; margin: 0 0 4px; color: #000; }
.vorschau-nachweise ul { margin: 0; padding: 0; list-style: none; }
.kopfzeile__suche { margin-left: auto; }

/* --- Entwurf: Aufmacher „Punkt für Punkt zum Bild“ --- */
.wow-oben { padding-top: 0; }
.wow { --bandh: 46px; --hoch: 148vw; --weg: max(70vh, 420px); }
.wow .anr { display: block; }
/* Bahn: so lang wie das Bild plus der Scrollweg, auf dem die Punkte wachsen. Das Bild bleibt solange stehen. */
.wow-bahn { position: relative; }
.wow .rahmen.wow-rahmen {
  aspect-ratio: auto; height: min(var(--hoch), calc(100vh - var(--bandh) - 20px)); overflow: hidden;
}
@supports (height: 100svh) {
  .wow .rahmen.wow-rahmen { height: min(var(--hoch), calc(100svh - var(--bandh) - 20px)); }
}
.wow .rahmen.wow-rahmen img { object-position: 50% 42%; }
.wow-decke { display: none; position: absolute; inset: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }
.wow .imbild { z-index: 3; }
.wow .signatur-ecke { z-index: 3; }
@media (min-width: 600px) { .wow { --bandh: 48px; --hoch: 60vw; } }
@media (min-width: 1024px) { .wow { --hoch: clamp(420px, calc(100vh - 250px), 620px); } .wow .vorspann { font-size: 19px; } }

/* Nur mit Skript und ohne „weniger Bewegung“: Bild steht fest, die Decke mit den Punktfenstern liegt darüber. */
/* Der Scrollweg ist ein leerer Block in der Bahn (Innenabstand zählt für „sticky“ nicht). */
.wow-an .wow-bahn::after { content: ""; display: block; height: var(--weg); }
.wow-an .wow .wow-halter { position: sticky; top: var(--bandh); }
.wow-an .wow-decke { display: block; background: var(--decke, #660000); }
.wow-an .wow-decke.gezeichnet { background: none; }
/* Dachzeile und Titel stehen von Anfang an unten auf der Decke, außerhalb der Form, an derselben Stelle wie später
   im Bild. Ihr Verlauf gehört zum Foto und liegt als eigene Ebene unter der Decke (vom Skript angelegt). */
.wow-an .wow .imbild { background-image: none; }
.wow-an .wow .wow-verlauf { position: absolute; left: 0; right: 0; bottom: 0; z-index: 1; background-image: var(--verlauf); }
.wow-an .wow .wow-verlauf > * { visibility: hidden; }
.wow-an .wow .signatur-ecke { opacity: var(--titel, 0); }
/* Variante B: schwarz auf der weißen Decke, weiß erst, wenn der Verlauf des Fotos darunter trägt. */
.wow-an.wow-weiss .wow-rahmen:not(.wow-foto) .imbild,
.wow-an.wow-weiss .wow-rahmen:not(.wow-foto) .imbild .meta,
.wow-an.wow-weiss .wow-rahmen:not(.wow-foto) .imbild .meta__rubrik { color: #000000; }
.wow-weiss { --decke: #FFFFFF; }
.wow-an.wow-weiss .wow .rahmen.wow-rahmen { outline: 1px solid rgb(0 0 0 / calc(0.14 * (1 - var(--titel, 0)))); outline-offset: -1px; }

.wow-oben .neben.karten { margin-top: 28px; }
.wow-oben .meldungen { margin-top: 36px; padding-bottom: 48px; }
@media (min-width: 1024px) {
  .wow-oben .neben.karten { grid-template-columns: repeat(4, minmax(0, 1fr)); grid-auto-flow: row; margin-top: 36px; }
  .wow-oben .meldungen .karten--reihe { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
"""

JS_KOPF_1 = """<script>
/* Vor dem ersten Bild: Variante bestimmen. Ohne Skript oder mit „weniger Bewegung“ bleibt das fertige Foto. */
(function () {
  var v = (new URLSearchParams(location.search).get('v') || 'a').toLowerCase();
  if (!/^[abc]$/.test(v)) v = 'a';
  var ruhe = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var h = document.documentElement;
  h.dataset.variante = v;
  if (v !== 'c' && !ruhe && window.CanvasRenderingContext2D) h.classList.add('wow-an');
  if (v === 'b') h.classList.add('wow-weiss');
})();
</script>
"""

JS_1 = """<script>
(function () {
  'use strict';
  /* 238 Punkte des Masters „Tamil Dots 04A“ aus design/signature/daten/punkte.json, auf Breite 1 normiert:
     x, y, große Halbachse, kleine Halbachse, Drehung (Bogenmaß), Lauf (0 = Fuß links … 1 = Auslauf rechts). */
  var P = __PUNKTE__;
  var SEITE = __SEITE__;            // Höhe der Form bei Breite 1
  var html = document.documentElement;
  var bahn = document.querySelector('.wow-bahn');
  var halter = document.querySelector('.wow-halter');
  var rahmen = document.querySelector('.wow-rahmen');
  var decke = document.querySelector('.wow-decke');
  var ctx = decke.getContext('2d');
  var ZOOM = 3.2, mx = 0, my = 0;
  var HO = 0;                       // Höhe der Bildzone über dem Titelfeld
  var B = 0, H = 0, dpr = 0, scharf = 1, grob = 1, f = 1, ox = 0, oy = 0, rmax = 0, ende = 1, letzter = -1, wartet = false;

  function messen() {
    var r = rahmen.getBoundingClientRect();
    B = r.width; H = r.height;
    // Ruhend (Anfang) zeichnet die Decke scharf, höchstens 2-fach. In Bewegung reichen rund 250 000 Bildpunkte,
    // das hält jedes Bild auch auf schwachen Handys kurz.
    scharf = Math.min(window.devicePixelRatio || 1, 2);
    grob = Math.max(1, Math.min(scharf, Math.sqrt(250000 / (B * H))));
    dpr = 0;
    // Unten steht das Titelfeld (Dachzeile und Titel auf der Decke). Die Form steht mittig in der Zone darüber,
    // mit Luft zum Rand; ihre Proportion bleibt unverändert, sie berührt den Titel nie.
    HO = Math.max(H * 0.4, rahmen.querySelector('.imbild .meta').getBoundingClientRect().top - r.top - 20);
    f = Math.min(B * (B < 600 ? 0.86 : 0.74), HO * 0.78 / SEITE);
    ox = (B - f) / 2; oy = (HO - f * SEITE) / 2;
    // Beim Wachsen fährt der Blick in die Form hinein (Faktor ZOOM, um ihren Schwerpunkt), damit die Punkte bis
    // zuletzt einzelne Fenster bleiben. Am Anfang steht die Form unverändert.
    mx = 0; my = 0;
    for (var k = 0; k < P.length; k++) { mx += P[k][0]; my += P[k][1]; }
    mx /= P.length; my /= P.length;
    // Größter Abstand eines Bildpunkts zum nächsten Punktmittelpunkt im Endzustand: so weit müssen die Punkte wachsen.
    rmax = 0;
    for (var gy = 0; gy <= 12; gy++) for (var gx = 0; gx <= 16; gx++) {
      var px = B * gx / 16, py = HO * gy / 12, m = 1e9;
      for (var i = 0; i < P.length; i++) {
        var dx = B / 2 + (P[i][0] - mx) * f * ZOOM - px, dy = HO / 2 + (P[i][1] - my) * f * ZOOM - py, d = dx * dx + dy * dy;
        if (d < m) m = d;
      }
      if (m > rmax) rmax = m;
    }
    rmax = Math.sqrt(rmax) * 1.04 + 2;
    // Scrollweg bis zum fertigen Bild: Lage der Bahn im Dokument plus der Weg, auf dem das Bild feststeht.
    var top = bahn.getBoundingClientRect().top + window.scrollY;
    var klebt = parseFloat(getComputedStyle(halter).top) || 0;
    ende = Math.max(1, top - klebt + bahn.offsetHeight - halter.offsetHeight);
    letzter = -1;
  }

  var weiss = html.classList.contains('wow-weiss'), farbe = weiss ? '#FFFFFF' : '#660000';

  function zeichnen(p) {
    // p 0..1 über den Scrollweg. Bis 0,8 wachsen die Punkte, danach löst sich das Titelfeld in das Foto auf.
    // In Variante A bleibt die Schrift weiß (auf Titan 13,4 : 1, auf dem Verlauf wie im Theme). In Variante B
    // wechselt sie von Schwarz zu Weiß; dort ist die Auflösung kurz gehalten, der Wechsel liegt in ihrer Mitte.
    var t = Math.min(1, p / 0.8), titel = Math.max(0, Math.min(1, (p - 0.8) / (weiss ? 0.05 : 0.17)));
    rahmen.style.setProperty('--titel', titel.toFixed(3));
    rahmen.classList.toggle('wow-foto', titel >= 0.5);
    var soll = p === 0 ? scharf : grob;
    if (soll !== dpr) { dpr = soll; decke.width = Math.round(B * dpr); decke.height = Math.round(H * dpr); }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.globalCompositeOperation = 'source-over';
    ctx.clearRect(0, 0, B, H);
    if (t < 1) {
      ctx.fillStyle = farbe;
      ctx.fillRect(0, 0, B, HO);
      ctx.globalCompositeOperation = 'destination-out';
      ctx.beginPath();
      var g = t * t * (3 - 2 * t), zoom = 1 + (ZOOM - 1) * g, fz = f * zoom;
      var cx = ox + mx * f + (B / 2 - ox - mx * f) * g, cy = oy + my * f + (HO / 2 - oy - my * f) * g;
      for (var i = 0; i < P.length; i++) {
        var q = P[i];
        // Der Fuß links beginnt, der Auslauf rechts folgt; jeder Punkt wächst erst sanft, dann schneller.
        var z = (t - q[5] * 0.5) / 0.5;
        z = z <= 0 ? 0 : z >= 1 ? 1 : z;
        var plus = z * z * z * z * rmax, mal = 1 + 0.9 * z;
        var x = cx + (q[0] - mx) * fz, y = cy + (q[1] - my) * fz, a = q[2] * fz * mal + plus, b = q[3] * fz * mal + plus;
        if (x + a < 0 || x - a > B || y + a < 0 || y - a > HO) continue;
        ctx.moveTo(x + a * Math.cos(q[4]), y + a * Math.sin(q[4]));
        ctx.ellipse(x, y, a, b, q[4], 0, 6.2832);
      }
      ctx.fill();
    }
    if (titel < 1) {
      // Titelfeld: bleibt geschlossen, bis das Foto steht, und wird dann durchsichtig.
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0, HO, B, H - HO);
      ctx.globalAlpha = 1 - titel; ctx.fillStyle = farbe; ctx.fillRect(0, HO, B, H - HO); ctx.globalAlpha = 1;
    }
    decke.classList.add('gezeichnet');
  }

  function bild() {
    wartet = false;
    var p = Math.max(0, Math.min(1, window.scrollY / ende));
    if (p === letzter) return;
    letzter = p;
    zeichnen(p);
  }
  function anfordern() { if (!wartet) { wartet = true; requestAnimationFrame(bild); } }

  if (html.classList.contains('wow-an')) {
    // Der Verlauf unter der Schrift als eigene Ebene unter der Decke: gleiche Maße wie der Titelblock.
    var verlauf = rahmen.querySelector('.imbild').cloneNode(true);
    verlauf.classList.add('wow-verlauf'); verlauf.setAttribute('aria-hidden', 'true');
    rahmen.insertBefore(verlauf, decke);
    messen(); bild();
    window.addEventListener('scroll', anfordern, { passive: true });
    window.addEventListener('resize', function () { messen(); anfordern(); });
    window.addEventListener('load', function () { messen(); anfordern(); });
    // Nachgeladene Schrift kann die Höhe des Titels ändern: dann neu messen.
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { messen(); anfordern(); });
  }

  // Umschaltleiste (nur Vorschau): lädt die Seite mit der gewählten Variante neu, oben beginnend.
  var v = html.dataset.variante;
  document.querySelectorAll('.vorschau-leiste button').forEach(function (k) {
    k.setAttribute('aria-pressed', String(k.dataset.v === v));
    k.addEventListener('click', function () {
      var u = new URL(location.href); u.searchParams.set('v', k.dataset.v);
      if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
      location.href = u.toString();
    });
  });
})();
</script>
"""


def karte(k, stufe="h3", klasse="karte", eager=False):
    sym = ('<span class="symbolbild" aria-hidden="true"><span class="symbolbild__lang">Symbolbild</span>'
           '<span class="symbolbild__kurz" title="Symbolbild">S</span></span>') if k["symbolbild"] else ""
    return (f'<article class="{klasse}"><a class="anr imbild-anr" href="{e(k["href"])}"><div class="rahmen r169">'
            f'<img width="640" height="360" src="../bilder/{e(k["bild"])}" alt="{e(k["alt"])}" decoding="async" '
            f'loading="{"eager" if eager else "lazy"}">{sym}<span class="signatur-ecke" aria-hidden="true"></span>'
            f'<div class="imbild"><p class="meta"><span class="meta__rubrik">{e(k["rubrik"])}</span>'
            f'<time datetime="{e(k["dt"])}">{e(k["datum"])}</time></p><{stufe} class="titel">{e(k["titel"])}</{stufe}>'
            f'</div></div><p class="vorspann">{e(k["vorspann"])}</p></a></article>')


def seite_1(P, seite):
    d = json.loads((HIER / "daten/startseite.json").read_text())["karten"]
    auf = next(k for k in d if k["rolle"] == "aufmacher")
    neben = [k for k in d if k["rolle"] == "neben"]
    meld = [k for k in d if k["rolle"] == "meldung"]
    pj = "[" + ",".join("[" + ",".join(f"{v:.4f}".rstrip("0").rstrip(".") for v in p[:6]) + "]" for p in P) + "]"
    js = JS_1.replace("__PUNKTE__", pj).replace("__SEITE__", f"{seite:.4f}")
    klein = auf["bild"].replace("-1200.", "-768.")
    nachweise = []
    for k in d:
        n = ("Symbolbild, " if k["symbolbild"] else "") + k["nachweis"]
        if n not in nachweise:
            nachweise.append(n)
    return (kopf("Vorschau: Punkt für Punkt zum Bild – tamil.de",
                 "Vorschau eines Aufmachers für tamil.de: Das Foto entsteht beim Scrollen aus den 238 Punkten des Signets.",
                 CSS_1)
            + JS_KOPF_1 + "</head>\n<body class=\"home page-start\">\n"
            + """<div class="vorschau-leiste" role="group" aria-label="Vorschau, nicht Teil des Entwurfs: Variante wählen">
	<div class="vorschau-leiste__innen">
		<span class="vorschau-leiste__name">Vorschau</span>
		<button type="button" data-v="a" aria-pressed="true">A: Punkte auf Titan</button>
		<button type="button" data-v="b" aria-pressed="false">B: Punkte auf Weiß</button>
		<button type="button" data-v="c" aria-pressed="false">C: aus (wie heute)</button>
	</div>
</div>
"""
            + seitenkopf()
            + f"""<main id="inhalt" tabindex="-1">
<h1 class="nur-vorlesen">Tamil.de, Startseite</h1>
<div class="innen wow-oben">
	<article class="aufmacher wow"><a class="anr imbild-anr" href="{e(auf["href"])}">
		<div class="wow-bahn"><div class="wow-halter"><div class="rahmen wow-rahmen">
			<img width="1200" height="675" src="../bilder/{e(auf["bild"])}" srcset="../bilder/{e(klein)} 768w, ../bilder/{e(auf["bild"])} 1200w" sizes="(min-width: 1280px) 1232px, 100vw" alt="{e(auf["alt"])}" decoding="async" loading="eager" fetchpriority="high">
			<canvas class="wow-decke" aria-hidden="true"></canvas>
			<span class="signatur-ecke" aria-hidden="true"></span>
			<div class="imbild"><p class="meta"><span class="meta__rubrik">{e(auf["rubrik"])}</span><time datetime="{e(auf["dt"])}">{e(auf["datum"])}</time></p><h2 class="titel">{e(auf["titel"])}</h2></div>
		</div>
		<p class="vorspann">{e(auf["vorspann"])}</p>
		</div></div>
	</a></article>
	<section class="neben karten" aria-label="Weitere Geschichten">
		{"".join(karte(k) for k in neben)}
	</section>
	<section class="meldungen" aria-labelledby="t-meldungen">
		<h2 class="block-titel" id="t-meldungen">Weitere Meldungen</h2>
		<ul class="karten karten--reihe">
			{"".join("<li>" + karte(k, klasse="karte karte--meldung") + "</li>" for k in meld)}
		</ul>
	</section>
</div>
</main>
"""
            + seitenfuss(nachweise, "Vorschau für Luis, 21.11.2026. Titel, Fotos und Nachweise vom Testsystem.")
            + js + "</body>\n</html>\n")


# ---------------------------------------------------------------------------------------------------------------------
# Vorschau 2: 2026 in 238 Punkten
# ---------------------------------------------------------------------------------------------------------------------

CSS_2 = """
.kopfzeile__suche { margin-left: auto; }
.vorschau-hinweis { background: #F2F2F2; border-bottom: 1px solid #D9D9D9; font-size: 13px; color: #555; }
.vorschau-hinweis p { max-width: var(--breite); margin: 0 auto; padding: 10px var(--rand); }

.jahr { padding-block: 28px 56px; }
.jahr h1 { margin: 0; font-size: 28px; line-height: 1.15; font-weight: 700; letter-spacing: -0.012em; }
.jahr__vorspann { margin: 10px 0 0; max-width: 40em; font-size: 18px; line-height: 1.5; }
.jahr__zurliste { display: inline-flex; align-items: center; min-height: 44px; margin-top: 4px; color: #B30000; font-weight: 600; }
.jahr__filter { display: flex; flex-wrap: wrap; gap: 8px; margin: 0; padding: 0; list-style: none; }
.jahr__filter button {
  font: inherit; font-size: 15px; font-weight: 600; min-height: 44px; padding: 0 14px; cursor: pointer;
  color: #660000; background: #FFFFFF; border: 1px solid #660000; border-radius: 0;
}
.jahr__filter button span { font-weight: 400; }
.jahr__filter button:hover { color: #B30000; border-color: #B30000; }
.jahr__filter button[aria-pressed="true"] { color: #FFFFFF; background: #660000; border-color: #660000; }
.jahr__filter button:focus-visible { outline: 3px solid #660000; outline-offset: 2px; }
.jahr__stand { margin: 12px 0 0; font-size: 15px; color: #555; min-height: 1.5em; }

.jahr__kuppel { position: relative; margin: 16px 0 0; }
.jahr__kuppel svg { display: block; width: 100%; height: auto; overflow: visible; }
.jahr__kuppel .leer { fill: #660000; opacity: 0.13; }
.jahr__kuppel a { outline: none; cursor: pointer; }
.jahr__kuppel .p { fill: var(--f); transform-box: fill-box; transform-origin: center; }
.jahr__kuppel .griff { fill: transparent; }
.jahr[data-filter] .jahr__kuppel a .p { fill: #660000; opacity: 0.13; }
.jahr[data-filter] .jahr__kuppel a.an .p { fill: #B30000; opacity: 1; }
.jahr[data-filter] .jahr__kuppel a:not(.an) { pointer-events: none; }
.jahr__kuppel a:hover .p, .jahr__kuppel a:focus-visible .p, .jahr__kuppel a.zeigt .p {
  fill: #B30000; opacity: 1; scale: 1.45; stroke: #000000; stroke-width: 2.5; vector-effect: non-scaling-stroke;
}
@media (prefers-reduced-motion: no-preference) {
  .jahr__kuppel .p { transition: scale 0.16s ease-out, fill 0.2s ease-out, opacity 0.2s ease-out; }
}
.jahr__achse { display: flex; justify-content: space-between; margin: 6px 0 0; font-size: 13px; color: #555; }
.jahr__wahl { margin-top: 20px; }
.jahr__tipp {
  position: absolute; z-index: 5; left: 0; top: 0; width: max-content; max-width: min(300px, 80vw); padding: 9px 12px 10px;
  background: #000000; color: #FFFFFF; font-size: 15px; line-height: 1.3; font-weight: 600; pointer-events: none;
}
.jahr__tipp span { display: block; margin-top: 4px; font-size: 13px; font-weight: 400; color: #CCCCCC; }
.jahr__tipp[hidden] { display: none; }

.jahr__listen { margin-top: 44px; max-width: 46em; }
.jahr__listen > h2 { margin: 0; padding-top: 10px; border-top: 2px solid #660000; font-size: 19px; font-weight: 700; }
.jahr__listen h3 { margin: 26px 0 0; font-size: 15px; font-weight: 600; color: #555; }
.jahr__liste { margin: 4px 0 0; padding: 0; list-style: none; }
.jahr__liste li { border-top: 1px solid #D9D9D9; }
.jahr__liste a { display: block; padding: 11px 0 12px; color: #000000; text-decoration: none; }
.jahr__liste a strong { display: block; font-size: 18px; line-height: 1.3; font-weight: 600; }
.jahr__liste a span { display: block; margin-top: 3px; font-size: 13px; color: #555; }
.jahr__liste a b { font-weight: 600; color: #B30000; }
.jahr__liste a:hover strong { text-decoration: underline; text-underline-offset: 3px; }
.jahr__liste a:focus-visible { outline: 3px solid #660000; outline-offset: 2px; }
@media (min-width: 1024px) {
  .jahr { padding-top: 36px; display: grid; grid-template-columns: 330px minmax(0, 1fr); column-gap: 48px; align-items: start; }
  .jahr__kopf { grid-column: 1; grid-row: 1; }
  .jahr__wahl { grid-column: 1; grid-row: 2; }
  .jahr__kuppel { grid-column: 2; grid-row: 1 / span 2; margin-top: 0; }
  .jahr__listen { grid-column: 1 / -1; }
  .jahr h1 { font-size: 34px; }
  .jahr__vorspann { font-size: 19px; }
  .jahr__liste a strong { font-size: 19px; }
}
"""

JS_2 = """<script>
(function () {
  'use strict';
  var jahr = document.querySelector('.jahr'), kuppel = document.querySelector('.jahr__kuppel');
  var tipp = document.querySelector('.jahr__tipp'), stand = document.querySelector('.jahr__stand');
  var punkte = Array.prototype.slice.call(kuppel.querySelectorAll('a'));
  var zeilen = Array.prototype.slice.call(document.querySelectorAll('.jahr__liste li'));
  var GESAMT = punkte.length;

  // Schild am Punkt: Titel, Rubrik und Datum; steht über dem Punkt, bei wenig Platz darunter.
  function zeigen(a) {
    var k = kuppel.getBoundingClientRect(), r = a.querySelector('.p').getBoundingClientRect();
    tipp.textContent = a.dataset.titel;
    var s = document.createElement('span'); s.textContent = a.dataset.rubrik + ' | ' + a.dataset.datum; tipp.appendChild(s);
    tipp.hidden = false;
    var b = tipp.offsetWidth, h = tipp.offsetHeight;
    var x = r.left + r.width / 2 - k.left - b / 2, y = r.top - k.top - h - 12;
    if (r.top - h - 12 < 60) y = r.bottom - k.top + 12;
    tipp.style.left = Math.max(0, Math.min(k.width - b, x)) + 'px'; tipp.style.top = y + 'px';
  }
  function weg() { tipp.hidden = true; }
  punkte.forEach(function (a) {
    a.addEventListener('pointerenter', function () { zeigen(a); });
    a.addEventListener('pointerleave', weg);
    a.addEventListener('focus', function () { zeigen(a); });
    a.addEventListener('blur', weg);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') weg(); });

  // Zeile der Liste hebt ihren Punkt hervor.
  zeilen.forEach(function (li) {
    var a = document.getElementById('p' + li.dataset.id);
    function an() { a.classList.add('zeigt'); } function aus() { a.classList.remove('zeigt'); }
    li.addEventListener('pointerenter', an); li.addEventListener('pointerleave', aus);
    li.addEventListener('focusin', an); li.addEventListener('focusout', aus);
  });

  // Filter nach Rubrik: zugehörige Punkte in Impact, die übrigen blass; die Liste zeigt dieselbe Auswahl.
  var knoepfe = Array.prototype.slice.call(document.querySelectorAll('.jahr__filter button'));
  knoepfe.forEach(function (k) {
    k.addEventListener('click', function () {
      var r = k.dataset.rubrik, n = 0;
      knoepfe.forEach(function (o) { o.setAttribute('aria-pressed', String(o === k)); });
      if (r) jahr.dataset.filter = r; else delete jahr.dataset.filter;
      punkte.forEach(function (a) {
        var ja = !r || a.dataset.rubrik === r;
        a.classList.toggle('an', !!r && ja);
        if (ja) { a.removeAttribute('tabindex'); a.removeAttribute('aria-hidden'); n++; }
        else { a.setAttribute('tabindex', '-1'); a.setAttribute('aria-hidden', 'true'); }
      });
      zeilen.forEach(function (li) { li.hidden = !!r && li.dataset.rubrik !== r; });
      document.querySelectorAll('.jahr__monat').forEach(function (m) {
        m.hidden = !m.querySelector('li:not([hidden])');
      });
      stand.textContent = r ? n + (n === 1 ? ' Meldung' : ' Meldungen') + ' in ' + r + ', in der Kuppel rot.'
                            : GESAMT + ' von 238 Punkten sind Meldungen. Die blassen Punkte sind noch frei.';
    });
  });
})();
</script>
"""


def datum_lang(iso):
    j, m, t = iso.split("-")
    return f"{int(t)}. {MONATE[int(m) - 1]} {j}"


def mischen(ton):
    """Farbe eines Punkts wie im Master: Titan #660000 bis Impact #B30000 in 7 Stufen."""
    stufe = min(int(ton * 7), 6) / 6
    return "#{:02X}0000".format(round(0x66 + (0xB3 - 0x66) * stufe))


def seite_2(P, seite):
    M = json.loads((HIER / "daten/meldungen-2026.json").read_text())["meldungen"]
    n = len(M)
    assert 0 < n <= 238
    # Die Meldungen laufen zeitlich vom Fuß (Januar) zum Auslauf (neueste). Je Abschnitt des Bogens bekommt die
    # Meldung den größten Punkt, damit er sich gut treffen lässt. Die Punktgröße sagt nichts über die Bedeutung.
    belegt = {}
    for i, m in enumerate(M):
        a, b = i * 238 // n, (i + 1) * 238 // n
        belegt[max(range(a, b), key=lambda k: P[k][2] * P[k][3])] = m
    H = 1000 * seite
    leer, voll = [], []
    for k, (x, y, ra, rb, rot, lauf, ton) in enumerate(P):
        lage = f'cx="{x * 1000:.1f}" cy="{y * 1000:.1f}" rx="{ra * 1000:.1f}" ry="{rb * 1000:.1f}"'
        dreh = f'transform="rotate({math.degrees(rot):.1f} {x * 1000:.1f} {y * 1000:.1f})"'
        geo = f"{lage} {dreh}"
        if k not in belegt:
            leer.append(f'<ellipse class="leer" {geo}/>')
            continue
        m = belegt[k]
        griff = max(ra * 1000 + 5, 11)
        voll.append(
            f'<a id="p{m["id"]}" href="{e(m["link"])}" aria-label="{e(m["titel"])}, {e(m["rubrik"])}, '
            f'{datum_lang(m["datum"])}" data-titel="{e(m["titel"])}" data-rubrik="{e(m["rubrik"])}" '
            f'data-datum="{datum_lang(m["datum"])}"><circle class="griff" cx="{x * 1000:.1f}" cy="{y * 1000:.1f}" '
            f'r="{griff:.1f}"/><g {dreh}><ellipse class="p" style="--f:{mischen(ton)}" {lage}/></g></a>')
    rubriken = {}
    for m in M:
        rubriken[m["rubrik"]] = rubriken.get(m["rubrik"], 0) + 1
    filter_html = ('<li><button type="button" data-rubrik="" aria-pressed="true">Alle <span>' + str(n)
                   + "</span></button></li>"
                   + "".join(f'<li><button type="button" data-rubrik="{e(r)}" aria-pressed="false">{e(r)} '
                             f"<span>{z}</span></button></li>"
                             for r, z in sorted(rubriken.items(), key=lambda t: (-t[1], t[0]))))
    monate = {}
    for m in reversed(M):
        monate.setdefault(m["datum"][:7], []).append(m)
    liste = ""
    for ym, ms in monate.items():
        liste += (f'<div class="jahr__monat"><h3>{MONATE[int(ym[5:]) - 1]} {ym[:4]}</h3><ul class="jahr__liste">'
                  + "".join(f'<li data-id="{m["id"]}" data-rubrik="{e(m["rubrik"])}"><a href="{e(m["link"])}">'
                            f'<strong>{e(m["titel"])}</strong><span><b>{e(m["rubrik"])}</b> | '
                            f'<time datetime="{m["datum"]}">{datum_lang(m["datum"])}</time></span></a></li>'
                            for m in ms) + "</ul></div>")
    erster, letzter = M[0]["datum"], M[-1]["datum"]
    return (kopf("Vorschau: 2026 in 238 Punkten – tamil.de",
                 "Vorschau einer Sonderseite für tamil.de: Die Punkte des Signets sind die Meldungen des Jahres 2026.",
                 CSS_2)
            + "</head>\n<body>\n"
            + '<div class="vorschau-hinweis"><p>Vorschau für Luis, 21.11.2026, nicht Teil des Entwurfs: '
              f"Auf dem Testsystem stehen {n} Meldungen mit Datum 2026. Darum sind {n} von 238 Punkten belegt, "
              "die übrigen bleiben frei.</p></div>\n"
            + seitenkopf()
            + f"""<main id="inhalt" tabindex="-1">
<div class="innen jahr">
	<div class="jahr__kopf">
	<h1>2026 in 238 Punkten</h1>
	<p class="jahr__vorspann">Jeder rote Punkt ist eine Meldung aus diesem Jahr, von {MONATE[int(erster[5:7]) - 1]} am großen Fuß links bis {MONATE[int(letzter[5:7]) - 1]} im feinen Auslauf rechts. Ein Klick öffnet die Meldung.</p>
	<a class="jahr__zurliste" href="#liste">Alle {n} Meldungen als Liste lesen</a>
	</div>
	<div class="jahr__kuppel">
		<svg viewBox="0 0 1000 {H:.1f}" role="group" aria-label="Die Meldungen des Jahres 2026 als Punkte des Signets Tamil Dots, {n} Punkte führen zu einer Meldung">
			<g aria-hidden="true">{"".join(leer)}</g>
			{"".join(voll)}
		</svg>
		<div class="jahr__tipp" aria-hidden="true" hidden></div>
		<p class="jahr__achse" aria-hidden="true"><span>{MONATE[int(erster[5:7]) - 1]} 2026</span><span>{MONATE[int(letzter[5:7]) - 1]} 2026</span></p>
	</div>
	<div class="jahr__wahl">
		<ul class="jahr__filter" aria-label="Nach Rubrik zeigen">{filter_html}</ul>
		<p class="jahr__stand" role="status">{n} von 238 Punkten sind Meldungen. Die blassen Punkte sind noch frei.</p>
	</div>
	<section class="jahr__listen" id="liste" aria-labelledby="t-liste" tabindex="-1">
		<h2 id="t-liste">Alle {n} Meldungen des Jahres</h2>
		{liste}
	</section>
</div>
</main>
"""
            + seitenfuss([], "Vorschau für Luis, 21.11.2026. Titel, Daten und Rubriken vom Testsystem.")
            + JS_2 + "</body>\n</html>\n")


if __name__ == "__main__":
    P, SEITE = punkte()
    assert len(P) == 238, len(P)
    (HIER / "punkt-zum-bild/index.html").write_text(seite_1(P, SEITE))
    print("punkt-zum-bild/index.html", (HIER / "punkt-zum-bild/index.html").stat().st_size, "Bytes")
    (HIER / "jahr-in-punkten/index.html").write_text(seite_2(P, SEITE))
    print("jahr-in-punkten/index.html", (HIER / "jahr-in-punkten/index.html").stat().st_size, "Bytes")
