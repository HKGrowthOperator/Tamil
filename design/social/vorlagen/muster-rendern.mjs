// Rendert alle Kartenformate als Muster-JPG nach design/social/muster/ (Vorschlag, nicht freigegeben).
// Mit --hilfe zusätzlich Feed, Story und Facebook mit eingezeichneten sicheren Zonen (…-zonen.jpg).
// Aufruf vom Repo-Wurzelverzeichnis: node design/social/vorlagen/muster-rendern.mjs [--hilfe]
// Die Automatik kann dasselbe Muster nutzen: window.KARTE per addInitScript setzen, ohne muster=1 rendern.
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const hier = dirname(fileURLToPath(import.meta.url));
const vorlage = pathToFileURL(resolve(hier, 'karte.html')).href;
const aus = resolve(hier, '..', 'muster');
const hilfe = process.argv.includes('--hilfe');

const JOBS = [
  ['feed', '', 1080, 1350, 'instagram-feed-1080x1350'],
  ['karussell', '1', 1080, 1350, 'instagram-karussell-1-titel-1080x1350'],
  ['karussell', '2', 1080, 1350, 'instagram-karussell-2-1080x1350'],
  ['karussell', '3', 1080, 1350, 'instagram-karussell-3-1080x1350'],
  ['karussell', '4', 1080, 1350, 'instagram-karussell-4-schluss-1080x1350'],
  ['story', '', 1080, 1920, 'story-1080x1920'],
  ['facebook', '', 1200, 630, 'facebook-link-1200x630'],
  ['whatsapp', '', 1080, 1080, 'whatsapp-kanal-1080x1080'],
];

const browser = await chromium.launch();
let fehler = 0;
const auswahl = hilfe ? JOBS.filter(j => ['feed', 'story', 'facebook'].includes(j[0])) : JOBS;
for (const [format, folie, b, h, name] of auswahl) {
  const ctx = await browser.newContext({ viewport: { width: b, height: h }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on('console', m => { if (m.type() === 'error') { fehler++; console.log('Konsole:', name, m.text()); } });
  page.on('requestfailed', r => { fehler++; console.log('Anfrage fehlgeschlagen:', name, r.url()); });
  const url = `${vorlage}?format=${format}${folie ? `&folie=${folie}` : ''}&muster=1${hilfe ? '&hilfe=1' : ''}`;
  await page.goto(url);
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  });
  const k = await page.$('.karte');
  const datei = resolve(aus, `${name}${hilfe ? '-zonen' : ''}.jpg`);
  await k.screenshot({ path: datei, type: 'jpeg', quality: hilfe ? 78 : 88 });
  const ueber = await page.evaluate(() => [...document.querySelectorAll('.text h1, .text h2')].some(e => e.scrollWidth > e.clientWidth + 1));
  if (ueber) { fehler++; console.log('Überlauf in', name); }
  console.log('ok', datei);
  await ctx.close();
}
await browser.close();
process.exit(fehler ? 1 : 0);
