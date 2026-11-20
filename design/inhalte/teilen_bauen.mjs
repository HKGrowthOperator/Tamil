#!/usr/bin/env node
// Standard-Teilenbild des Themes (1200 × 630, wordpress/themes/tamil/assets/img/teilen.jpg) mit dem neuen Logo bauen.
//
//   node design/inhalte/teilen_bauen.mjs
//
// Links bleibt das Foto des bisherigen Teilenbilds unverändert (die linken 630 px von teilen.jpg: Sri-Ganesha-
// Hindutempel Berlin, Foto 18quirl08 / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten). Rechts auf Weiß unter dem
// Balken in Titan: das Logo (design/inhalte/logo.png, freigestellt), der Satz zur Seite und der Nachweis des Fotos.
// Schrift: Libre Franklin aus dem Theme. Rendern mit Playwright (Chromium), Ausgabe JPEG.

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const hier = path.dirname(fileURLToPath(import.meta.url));
const wurzel = path.resolve(hier, "..", "..");
const theme = path.join(wurzel, "wordpress", "themes", "tamil");
const ziel = path.join(theme, "assets", "img", "teilen.jpg");
const url = (p) => "file://" + p;

const html = `<!doctype html><html lang="de"><head><meta charset="utf-8"><style>
@font-face { font-family: "LF"; src: url("${url(path.join(theme, "assets/fonts/libre-franklin-latin-wght-normal.woff2"))}") format("woff2"); font-weight: 100 900; }
@font-face { font-family: "LF"; src: url("${url(path.join(theme, "assets/fonts/libre-franklin-latin-ext-wght-normal.woff2"))}") format("woff2"); font-weight: 100 900; unicode-range: U+0100-024F, U+1E00-1EFF; }
* { box-sizing: border-box; margin: 0; }
body { width: 1200px; height: 630px; overflow: hidden; background: #FFFFFF; font-family: "LF", sans-serif; }
.foto { position: absolute; left: 0; top: 0; width: 630px; height: 630px; background: url("${url(ziel)}") 0 0 / 1200px 630px no-repeat; }
.feld { position: absolute; left: 630px; top: 0; width: 570px; height: 630px; padding: 0 56px; }
.balken { position: absolute; left: 0; right: 0; top: 0; height: 12px; background: #660000; }
.logo { position: absolute; left: 56px; top: 132px; width: 360px; height: auto; }
.satz { position: absolute; left: 56px; right: 48px; top: 300px; font-size: 31px; line-height: 1.24; font-weight: 700; color: #000000; letter-spacing: -0.005em; }
.nachweis { position: absolute; left: 56px; right: 48px; bottom: 30px; font-size: 15px; line-height: 1.4; color: #555555; }
</style></head><body>
<div class="foto"></div>
<div class="feld"><div class="balken"></div>
<img class="logo" src="${url(path.join(hier, "logo.png"))}" alt="">
<p class="satz">Nachrichten, Kino und Community für Tamilen in Deutschland, Österreich und der Schweiz</p>
<p class="nachweis">Foto links: 18quirl08 / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten (Sri-Ganesha-Hindutempel, Berlin)</p>
</div></body></html>`;

const tmp = path.join(hier, ".teilen-tmp.html");
fs.writeFileSync(tmp, html);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await page.goto(url(tmp));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(200);
const bild = await page.screenshot({ type: "jpeg", quality: 88 });
await browser.close();
fs.unlinkSync(tmp);
fs.writeFileSync(ziel, bild);
console.log("teilen.jpg geschrieben:", ziel, Math.round(bild.length / 1024), "KB");
