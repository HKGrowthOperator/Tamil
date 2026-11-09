// Sichtbarer erster Bildschirm je Probe und Kennzahlen gegen die harten Kriterien des Briefs.
// Anders als die Kacheln aus tools/shots.mjs (Ausschnitte der ganzen Seite) nimmt dieses Skript nur den sichtbaren
// Bereich auf. Fest stehende Leisten sitzen dadurch dort, wo man sie am Gerät wirklich sieht.
//
//   node design/vergleich/aufnahmen.mjs klar blatt bild
//
// Ergebnis je Probe:
//   design/vergleich/img/<slug>-start-handy.jpg, -start-handy-2.jpg, -start-desktop.jpg, -artikel-handy.jpg (falls da)
//   design/vergleich/kennzahlen/<slug>.json  (Schlagzeilen, Kopfhöhe, größte Schrift, Rotanteil, Radius, Schatten …)
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const { chromium } = createRequire(import.meta.url)('playwright');

const hier = dirname(fileURLToPath(import.meta.url));
const wurzel = resolve(hier, '..', '..');
const ziel = resolve(hier, 'img');
const zahlen = resolve(hier, 'kennzahlen');
mkdirSync(ziel, { recursive: true });
mkdirSync(zahlen, { recursive: true });

const ANSICHTEN = [
  { name: 'start-handy', seite: 'index.html', breite: 390, hoehe: 844, messen: 'handy' },
  { name: 'start-handy-2', seite: 'index.html', breite: 390, hoehe: 844, scroll: 844 },
  { name: 'start-desktop', seite: 'index.html', breite: 1280, hoehe: 800, messen: 'desktop' },
  { name: 'artikel-handy', seite: 'artikel.html', breite: 390, hoehe: 844 },
];

// Läuft im Browser: misst, was im sichtbaren ersten Bildschirm steht.
function messen() {
  const vh = window.innerHeight;
  const sichtbar = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) > 0.05 && r.width > 0 && r.height > 0;
  };
  const ganzImBild = (el) => {
    const r = el.getBoundingClientRect();
    return r.top >= 0 && r.bottom <= vh && r.left >= 0 && r.right <= window.innerWidth + 1;
  };
  // Farben stehen je nach Schreibweise als rgb(), oklch() oder color() im Stil; die Zeichenfläche rechnet sie um.
  const flaeche = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
  const farbwerte = new Map();
  const istRot = (farbe) => {
    if (!farbwerte.has(farbe)) {
      flaeche.clearRect(0, 0, 1, 1);
      flaeche.fillStyle = farbe;
      flaeche.fillRect(0, 0, 1, 1);
      const [r, g, b] = flaeche.getImageData(0, 0, 1, 1).data;
      farbwerte.set(farbe, r > 120 && r > g * 1.6 && r > b * 1.6);
    }
    return farbwerte.get(farbe);
  };
  const kopfzeilen = [...document.querySelectorAll('h1, h2, h3')].filter(sichtbar);
  const schlagzeilen = kopfzeilen.filter((h) => h.closest('a') || h.querySelector('a'));
  const erste = schlagzeilen.map((h) => h.getBoundingClientRect().top).sort((a, b) => a - b)[0];
  const zeilen = (el) => Math.round(el.getBoundingClientRect().height / parseFloat(getComputedStyle(el).lineHeight || '0') || 0);

  let groesste = { px: 0, text: '' };
  let groessteRot = { px: 0, text: '' };
  let versalGross = 0;
  const familien = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let k = walker.nextNode(); k; k = walker.nextNode()) {
    const text = k.textContent.trim();
    const el = k.parentElement;
    if (!text || !el || !sichtbar(el)) continue;
    const s = getComputedStyle(el);
    const px = parseFloat(s.fontSize);
    familien.add(s.fontFamily.split(',')[0].replace(/["']/g, '').trim());
    const r = el.getBoundingClientRect();
    if (r.top >= vh || r.bottom <= 0) continue;
    if (px > groesste.px) groesste = { px, text: text.slice(0, 40) };
    if (istRot(s.color) && px > groessteRot.px) groessteRot = { px, text: text.slice(0, 40) };
    if (s.textTransform === 'uppercase' && px > 14) versalGross += 1;
  }

  let radius = { px: 0, element: '' };
  let schatten = 0;
  let gedreht = 0;
  let breiteVerstellt = 0;
  for (const el of document.querySelectorAll('body *')) {
    if (!sichtbar(el)) continue;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const rad = Math.min(parseFloat(s.borderTopLeftRadius) || 0, Math.min(r.width, r.height) / 2);
    if (rad > radius.px) radius = { px: Math.round(rad * 10) / 10, element: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : '') };
    if (s.boxShadow && s.boxShadow !== 'none') {
      // Nur weiche Schatten zählen; Linien, die als Schatten ohne Unschärfe gebaut sind, gelten nicht.
      const px = [...s.boxShadow.matchAll(/(-?[\d.]+)px/g)].map((m) => Number(m[1]));
      if (px.some((wert, i) => i % 4 === 2 && wert > 0)) schatten += 1;
    }
    if (s.transform && s.transform !== 'none') {
      const m = s.transform.match(/matrix\(([^)]+)\)/);
      if (m) { const [, b, c] = m[1].split(',').map(Number); if (Math.abs(b) > 0.001 || Math.abs(c) > 0.001) gedreht += 1; }
    }
    if (s.rotate && s.rotate !== 'none' && parseFloat(s.rotate) !== 0) gedreht += 1;
    if (s.fontStretch && !['100%', 'normal'].includes(s.fontStretch)) breiteVerstellt += 1;
  }
  const gestreckt = [...document.images].filter((b) => sichtbar(b) && b.naturalWidth && b.getBoundingClientRect().width * 2 > b.naturalWidth + 2)
    .map((b) => `${b.getAttribute('src')} (${Math.round(b.getBoundingClientRect().width)} px gezeigt, ${b.naturalWidth} px vorhanden)`);
  const kopf = document.querySelector('header');
  return {
    kopfleiste_hoehe: kopf ? Math.round(kopf.getBoundingClientRect().bottom) : null,
    erste_schlagzeile_ab: erste === undefined ? null : Math.round(erste),
    schlagzeilen_ganz_sichtbar: schlagzeilen.filter(ganzImBild).length,
    schlagzeilen_seite: schlagzeilen.length,
    max_zeilen_schlagzeile: Math.max(0, ...schlagzeilen.map(zeilen)),
    groesste_schrift: groesste,
    groesste_rote_schrift: groessteRot,
    versalien_ueber_14px: versalGross,
    schriftfamilien: [...familien],
    groesster_radius: radius,
    schatten,
    gedreht,
    schriftbreite_verstellt: breiteVerstellt,
    bilder_ueber_natuerlicher_breite: gestreckt,
    ueberlauf: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  };
}

const slugs = process.argv.slice(2);
if (!slugs.length) {
  console.error('Aufruf: node design/vergleich/aufnahmen.mjs <slug> [<slug> …]');
  process.exit(2);
}

const browser = await chromium.launch();
let fehler = 0;
for (const slug of slugs) {
  const ergebnis = { slug, stand: new Date().toISOString().slice(0, 16) };
  for (const a of ANSICHTEN) {
    const datei = resolve(wurzel, 'design', 'richtungen', slug, a.seite);
    if (!existsSync(datei)) continue;
    const kontext = await browser.newContext({ viewport: { width: a.breite, height: a.hoehe }, deviceScaleFactor: 2, reducedMotion: 'reduce' });
    const seite = await kontext.newPage();
    const meldungen = [];
    seite.on('pageerror', (e) => meldungen.push(String(e)));
    await seite.goto(pathToFileURL(datei).href, { waitUntil: 'load' });
    await seite.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map((b) => (b.complete ? null : b.decode().catch(() => null))));
    });
    if (a.scroll) await seite.evaluate((y) => window.scrollTo(0, y), a.scroll);
    await seite.screenshot({ path: resolve(ziel, `${slug}-${a.name}.jpg`), type: 'jpeg', quality: 88 });
    if (a.messen) {
      const m = await seite.evaluate(messen);
      await seite.addStyleTag({ content: 'img, picture, video, svg { visibility: hidden !important } * { background-image: none !important }' });
      const ohne = resolve(zahlen, `.${slug}-${a.messen}.png`);
      await seite.screenshot({ path: ohne, type: 'png' });
      m.farbanteil_ohne_bilder = JSON.parse(execFileSync('python3', [resolve(hier, 'farbanteil.py'), ohne], { encoding: 'utf-8' }));
      rmSync(ohne);
      m.seitenfehler = meldungen;
      ergebnis[a.messen] = m;
      if (m.ueberlauf > 0 || meldungen.length) fehler += 1;
      console.log(`${slug} ${a.messen}: Schlagzeilen ganz sichtbar ${m.schlagzeilen_ganz_sichtbar}, Kopf ${m.kopfleiste_hoehe} px, erste Schlagzeile ab ${m.erste_schlagzeile_ab} px, größte Schrift ${m.groesste_schrift.px} px, ` +
        `größte rote ${m.groesste_rote_schrift.px} px, Rot ${(m.farbanteil_ohne_bilder.rot * 100).toFixed(1)} %, Radius ${m.groesster_radius.px} px, Schatten ${m.schatten}, ` +
        `gedreht ${m.gedreht}, Überlauf ${m.ueberlauf} px`);
    }
    await kontext.close();
  }
  writeFileSync(resolve(zahlen, `${slug}.json`), JSON.stringify(ergebnis, null, 2) + '\n');
}
await browser.close();
process.exit(fehler ? 1 : 0);
