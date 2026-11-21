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
{extra_css}
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
@media (min-width: 1024px) { .wow { --hoch: 620px; } .wow .vorspann { font-size: 19px; } }

/* Nur mit Skript und ohne „weniger Bewegung“: Bild steht fest, die Decke mit den Punktfenstern liegt darüber. */
/* Der Scrollweg ist ein leerer Block in der Bahn (Innenabstand zählt für „sticky“ nicht). */
.wow-an .wow-bahn::after { content: ""; display: block; height: var(--weg); }
.wow-an .wow .wow-halter { position: sticky; top: var(--bandh); }
.wow-an .wow-decke { display: block; background: var(--decke, #660000); }
.wow-an .wow-decke.gezeichnet { background: none; }
.wow-an .wow .imbild, .wow-an .wow .signatur-ecke { opacity: var(--titel, 0); }
.wow-an .wow .imbild { translate: 0 calc((1 - var(--titel, 0)) * 14px); }
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
  var B = 0, H = 0, dpr = 1, f = 1, ox = 0, oy = 0, rmax = 0, ende = 1, letzter = -1, wartet = false;

  function messen() {
    var r = rahmen.getBoundingClientRect();
    B = r.width; H = r.height;
    // Die Decke braucht nicht die volle Pixeldichte: höchstens 2-fach und höchstens rund 500 000 Bildpunkte.
    dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 2, Math.sqrt(500000 / (B * H))));
    decke.width = Math.round(B * dpr); decke.height = Math.round(H * dpr);
    // Die Form steht mittig im Bild, mit Luft zum Rand; ihre Proportion bleibt unverändert.
    f = Math.min(B * (B < 600 ? 0.86 : 0.74), H * 0.74 / SEITE);
    ox = (B - f) / 2; oy = (H - f * SEITE) / 2;
    // Beim Wachsen fährt der Blick in die Form hinein (Faktor ZOOM, um ihren Schwerpunkt), damit die Punkte bis
    // zuletzt einzelne Fenster bleiben. Am Anfang steht die Form unverändert.
    mx = 0; my = 0;
    for (var k = 0; k < P.length; k++) { mx += P[k][0]; my += P[k][1]; }
    mx /= P.length; my /= P.length;
    // Größter Abstand eines Bildpunkts zum nächsten Punktmittelpunkt im Endzustand: so weit müssen die Punkte wachsen.
    rmax = 0;
    for (var gy = 0; gy <= 12; gy++) for (var gx = 0; gx <= 16; gx++) {
      var px = B * gx / 16, py = H * gy / 12, m = 1e9;
      for (var i = 0; i < P.length; i++) {
        var dx = B / 2 + (P[i][0] - mx) * f * ZOOM - px, dy = H / 2 + (P[i][1] - my) * f * ZOOM - py, d = dx * dx + dy * dy;
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

  function zeichnen(p) {
    // p 0..1 über den Scrollweg. Bis 0,84 wachsen die Punkte, danach kommt der Titel.
    var t = Math.min(1, p / 0.84), titel = Math.max(0, Math.min(1, (p - 0.84) / 0.13));
    rahmen.style.setProperty('--titel', titel.toFixed(3));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.globalCompositeOperation = 'source-over';
    ctx.clearRect(0, 0, B, H);
    if (t < 1) {
      ctx.fillStyle = html.classList.contains('wow-weiss') ? '#FFFFFF' : '#660000';
      ctx.fillRect(0, 0, B, H);
      ctx.globalCompositeOperation = 'destination-out';
      ctx.beginPath();
      var g = t * t * (3 - 2 * t), zoom = 1 + (ZOOM - 1) * g, fz = f * zoom;
      var cx = ox + mx * f + (B / 2 - ox - mx * f) * g, cy = oy + my * f + (H / 2 - oy - my * f) * g;
      for (var i = 0; i < P.length; i++) {
        var q = P[i];
        // Der Fuß links beginnt, der Auslauf rechts folgt; jeder Punkt wächst erst sanft, dann schneller.
        var z = (t - q[5] * 0.5) / 0.5;
        z = z <= 0 ? 0 : z >= 1 ? 1 : z;
        var plus = z * z * z * z * rmax, mal = 1 + 0.9 * z;
        var x = cx + (q[0] - mx) * fz, y = cy + (q[1] - my) * fz, a = q[2] * fz * mal + plus, b = q[3] * fz * mal + plus;
        if (x + a < 0 || x - a > B || y + a < 0 || y - a > H) continue;
        ctx.moveTo(x + a * Math.cos(q[4]), y + a * Math.sin(q[4]));
        ctx.ellipse(x, y, a, b, q[4], 0, 6.2832);
      }
      ctx.fill();
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
    messen(); bild();
    window.addEventListener('scroll', anfordern, { passive: true });
    window.addEventListener('resize', function () { messen(); anfordern(); });
    window.addEventListener('load', function () { messen(); anfordern(); });
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


if __name__ == "__main__":
    P, SEITE = punkte()
    assert len(P) == 238, len(P)
    (HIER / "punkt-zum-bild/index.html").write_text(seite_1(P, SEITE))
    print("punkt-zum-bild/index.html", (HIER / "punkt-zum-bild/index.html").stat().st_size, "Bytes")
