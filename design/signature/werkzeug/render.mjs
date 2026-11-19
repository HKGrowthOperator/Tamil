// Rendert SVG- oder HTML-Dateien mit Playwright (Chromium) zu PNG.
// Aufruf: node design/signature/werkzeug/render.mjs <datei> <ausgabe.png> <breite> <hoehe> [--transparent] [--skala 2]
// Mehrere Aufträge: node render.mjs --liste auftraege.json   ([{"datei","aus","b","h","transparent","skala"}])
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const args = process.argv.slice(2);
let jobs = [];
if (args[0] === '--liste') {
  jobs = JSON.parse(readFileSync(args[1], 'utf8'));
} else {
  const [datei, aus, b, h] = args;
  jobs = [{ datei, aus, b: +b, h: +h, transparent: args.includes('--transparent'),
            skala: args.includes('--skala') ? +args[args.indexOf('--skala') + 1] : 1 }];
}
const browser = await chromium.launch();
for (const j of jobs) {
  const ctx = await browser.newContext({ viewport: { width: j.b, height: j.h }, deviceScaleFactor: j.skala || 1,
                                         reducedMotion: j.bewegung ? 'no-preference' : 'reduce' });
  const page = await ctx.newPage();
  const fehler = [];
  page.on('console', m => { if (m.type() === 'error') fehler.push(m.text()); });
  page.on('pageerror', e => fehler.push(String(e)));
  await page.goto(pathToFileURL(resolve(j.datei)).href);
  await page.evaluate(() => document.fonts && document.fonts.ready);
  if (j.warten) await page.waitForTimeout(j.warten);
  await page.screenshot({ path: j.aus, omitBackground: !!j.transparent, fullPage: !!j.ganz });
  if (fehler.length) console.log('FEHLER', j.datei, fehler.join(' | '));
  console.log('ok', j.aus);
  await ctx.close();
}
await browser.close();
