// Erster Bildschirm je Richtung für die Vergleichsseite (Tor G2).
// Anders als die Kacheln aus tools/shots.mjs (Ausschnitte der ganzen Seite) nimmt dieses Skript nur den sichtbaren
// Bereich auf. Fest stehende Leisten sitzen dadurch dort, wo man sie am Gerät wirklich sieht.
//
//   node design/vergleich/aufnahmen.mjs plakatwand zine raster feed
//
// Ergebnis: design/vergleich/img/<slug>-start-handy.jpg, -start-desktop.jpg, -artikel-handy.jpg
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const { chromium } = createRequire(import.meta.url)('playwright');

const hier = dirname(fileURLToPath(import.meta.url));
const wurzel = resolve(hier, '..', '..');
const ziel = resolve(hier, 'img');
mkdirSync(ziel, { recursive: true });

const ANSICHTEN = [
  { name: 'start-handy', seite: 'index.html', breite: 390, hoehe: 844 },
  { name: 'start-desktop', seite: 'index.html', breite: 1280, hoehe: 800 },
  { name: 'artikel-handy', seite: 'artikel.html', breite: 390, hoehe: 844 },
];

const slugs = process.argv.slice(2);
if (!slugs.length) {
  console.error('Aufruf: node design/vergleich/aufnahmen.mjs <slug> [<slug> …]');
  process.exit(2);
}

const browser = await chromium.launch();
let fehler = 0;
for (const slug of slugs) {
  for (const a of ANSICHTEN) {
    const kontext = await browser.newContext({
      viewport: { width: a.breite, height: a.hoehe },
      deviceScaleFactor: 2,
      reducedMotion: 'reduce',
    });
    const seite = await kontext.newPage();
    const meldungen = [];
    seite.on('pageerror', (e) => meldungen.push(String(e)));
    await seite.goto(pathToFileURL(resolve(wurzel, 'design', 'richtungen', slug, a.seite)).href, {
      waitUntil: 'load',
    });
    await seite.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map((b) => (b.complete ? null : b.decode().catch(() => null))));
    });
    const ueberlauf = await seite.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    const datei = resolve(ziel, `${slug}-${a.name}.jpg`);
    await seite.screenshot({ path: datei, type: 'jpeg', quality: 88 });
    if (ueberlauf > 0 || meldungen.length) fehler += 1;
    console.log(`${slug} ${a.name}: ${a.breite}×${a.hoehe}, Überlauf ${ueberlauf} px, Fehler ${meldungen.length}`);
    await kontext.close();
  }
}
await browser.close();
process.exit(fehler ? 1 : 0);
