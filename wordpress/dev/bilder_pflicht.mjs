#!/usr/bin/env node
// Bilderpflicht prüfen (Luis, 17.11.2026): Jeder sichtbare Anreißer, jede Listenzeile, Kachel, jedes Suchergebnis,
// „Weiterlesen“ und jeder Kino- und Termineintrag zeigt ein geladenes Bild. Ausnahmen: Rubrikband, Fußlisten,
// Formulare und reine Textseiten (Impressum, Datenschutz).
//
//   node wordpress/dev/bilder_pflicht.mjs <basis-url> [--out <ordner>] [--widths 390,820,1280] [weitere Pfade …]
//
// Besucht Startseite, einen Artikel (den ersten Link der Startseite), alle Rubriken aus dem Band, /events/, die Suche,
// eine 404-Seite und – falls vorhanden – /kontakt/, /production/, /werben/, /verzeichnis/, /einreichen/; dazu weitere
// Pfade aus der Befehlszeile (etwa ein Artikel mit Titelkarte). Je Breite: Monate aufklappen, ganz nach unten scrollen
// (Bewegung D blendet beim Scrollen ein, „lazy“-Bilder laden erst im Bild), dann jedes Anreißer-Element prüfen: Es
// braucht ein <img> mit naturalWidth > 0. Werbeplätze (.ad, .anzeige) werden getrennt gemeldet und lassen die Prüfung
// nicht scheitern (Baustein Werbung im Plugin). Rückgabewert 1, wenn ein Anreißer ohne Bild gefunden wurde.

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

// Anreißer-Elemente des Themes (inc/anreisser.php, template-parts/*) und des Plugins (Verzeichnis)
const ANREISSER = [
  ".aufmacher", ".kachel", ".stueck", ".meldung", ".zeile", "li.grafik", ".kacheln li", ".vz-eintrag",
  ".tafel--bilder tbody tr:not(.land)", "article.artikel:not(.seite)",
].join(", ");
const WERBUNG = ".ad, .anzeige, .tz-anzeige, .wb-anzeige";
const AUSNAHMEN = ".band, .fuss, .mehr, form, .kopf";
const FEST = ["/kontakt/", "/production/", "/werben/", "/verzeichnis/", "/einreichen/"];

function argumente(argv) {
  const a = { basis: null, out: null, widths: [390, 820, 1280], pfade: [] };
  for (let i = 0; i < argv.length; i++) {
    const x = argv[i];
    if (x === "--out") a.out = argv[++i];
    else if (x === "--widths") a.widths = argv[++i].split(",").map(Number).filter(Boolean);
    else if (!a.basis) a.basis = x.replace(/\/+$/, "");
    else a.pfade.push(x);
  }
  return a;
}

// Ganz nach unten scrollen, damit Auftritte (Bewegung D) und „lazy“-Bilder ausgelöst werden; Monate aufklappen
async function durchscrollen(page) {
  await page.evaluate(() => document.querySelectorAll("details.monat").forEach((d) => { d.open = true; }));
  let y = 0;
  for (let runde = 0; runde < 80; runde++) {
    const hoehe = await page.evaluate(() => document.documentElement.scrollHeight);
    if (y >= hoehe) break;
    y += Math.round((page.viewportSize()?.height || 800) * 0.7);
    await page.evaluate((ziel) => window.scrollTo(0, ziel), y);
    await page.waitForTimeout(120);
  }
  await page.waitForTimeout(400);
  // Bilder, die noch laden, einzeln ins Bild holen und auf sie warten (höchstens 4 s je Seite)
  await page.evaluate(async () => {
    const offen = [...document.images].filter((i) => !i.complete || i.naturalWidth === 0);
    for (const img of offen) img.scrollIntoView({ block: "center" });
    await Promise.race([
      Promise.all(offen.map((i) => (i.decode ? i.decode().catch(() => {}) : Promise.resolve()))),
      new Promise((ok) => setTimeout(ok, 4000)),
    ]);
  });
}

async function pruefen(page, sel) {
  return page.evaluate(({ ANREISSER, WERBUNG, AUSNAHMEN }) => {
    const sichtbar = (el) => {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none" && !el.closest("[hidden]");
    };
    const kurz = (el) => (el.querySelector(".titel, h1, h2, h3, h4, th, a") || el).textContent.trim().replace(/\s+/g, " ").slice(0, 70);
    const geladen = (el) => [...el.querySelectorAll("img")].some((i) => i.complete && i.naturalWidth > 0);
    const kennung = (el) => el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/).join(".") : "");
    const anr = [...document.querySelectorAll(ANREISSER)].filter((el) => !el.closest(AUSNAHMEN) && !el.closest(WERBUNG) && sichtbar(el));
    // verschachtelte Treffer (Zeile in einer Kachel) nur einmal: das innerste Element zählt
    const einzeln = anr.filter((el) => !anr.some((x) => x !== el && el.contains(x)));
    const fehlend = einzeln.filter((el) => !geladen(el)).map((el) => ({ element: kennung(el), text: kurz(el) }));
    const werbung = [...document.querySelectorAll(WERBUNG)].filter((el) => sichtbar(el) && !el.parentElement.closest(WERBUNG));
    const werbungOhne = werbung.filter((el) => !geladen(el) && !el.querySelector("iframe, video, svg")).map((el) => ({ element: kennung(el), text: kurz(el) }));
    return { anreisser: einzeln.length, fehlend, werbung: werbung.length, werbungOhne };
  }, sel);
}

async function main() {
  const a = argumente(process.argv.slice(2));
  if (!a.basis) {
    console.error("Aufruf: node wordpress/dev/bilder_pflicht.mjs <basis-url> [--out <ordner>] [--widths 390,820,1280] [pfade …]");
    process.exit(2);
  }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  // Seiten finden: Rubriken aus dem Band, ein Artikel von der Startseite
  await page.goto(a.basis + "/", { waitUntil: "domcontentloaded" });
  const gefunden = await page.evaluate((basis) => {
    const intern = (h) => h && h.startsWith(basis) ? h.slice(basis.length) || "/" : null;
    const rubriken = [...document.querySelectorAll(".band__liste a")].map((x) => intern(x.href)).filter(Boolean);
    const artikel = [...document.querySelectorAll(".aufmacher a.anr, .stueck a.anr")].map((x) => intern(x.href)).filter(Boolean);
    return { rubriken, artikel: artikel[0] || null };
  }, a.basis);
  const seiten = ["/", ...(gefunden.artikel ? [gefunden.artikel] : []), ...gefunden.rubriken, "/events/", "/?s=tamil",
    "/diese-seite-gibt-es-nicht-bilderpflicht/", ...FEST, ...a.pfade];
  const pfade = [...new Set(seiten.map((p) => (p.startsWith("/") ? p : "/" + p)))];

  const bericht = [];
  const werbungOhne = new Map();
  let fehler = 0;
  for (const pfad of pfade) {
    for (const w of a.widths) {
      await page.setViewportSize({ width: w, height: 900 });
      const antwort = await page.goto(a.basis + pfad, { waitUntil: "networkidle" }).catch(() => null);
      const status = antwort ? antwort.status() : 0;
      const absichtlich404 = pfad.includes("gibt-es-nicht");
      if (status === 404 && !absichtlich404) {
        if (w === a.widths[0]) console.log(`fehlt   ${pfad} (404, übersprungen)`);
        break;
      }
      if (status >= 500 || status === 0) {
        fehler += 1;
        bericht.push({ pfad, breite: w, status, anreisser: 0, fehlend: [], werbung: 0, werbungOhne: [] });
        console.log(`FEHLER ${String(w).padStart(4)}  ${pfad}  HTTP ${status || "ohne Antwort"}`);
        continue;
      }
      await durchscrollen(page);
      const e = await pruefen(page, { ANREISSER, WERBUNG, AUSNAHMEN });
      fehler += e.fehlend.length;
      bericht.push({ pfad, breite: w, status, ...e });
      const zeichen = e.fehlend.length ? "FEHLER" : "ok    ";
      console.log(`${zeichen} ${String(w).padStart(4)}  ${pfad}  ${e.anreisser} Anreißer, ${e.fehlend.length} ohne Bild` +
        (e.werbung ? `, Werbung ${e.werbung} (${e.werbungOhne.length} ohne Bild)` : ""));
      for (const f of e.fehlend) console.log(`          ohne Bild: ${f.element}  „${f.text}“`);
      for (const f of e.werbungOhne) werbungOhne.set(f.element, f.text);
    }
  }
  await browser.close();
  if (a.out) {
    fs.mkdirSync(a.out, { recursive: true });
    fs.writeFileSync(path.join(a.out, "bilder-pflicht.json"), JSON.stringify(bericht, null, 1));
  }
  if (werbungOhne.size) {
    console.log("\nWerbeplätze ohne Bild (Plugin tamil-site, zählen nicht als Fehler):");
    for (const [el, text] of werbungOhne) console.log(`  ${el}  „${text}“`);
  }
  const n = bericht.reduce((s, b) => s + b.anreisser, 0);
  console.log(`\n${bericht.length} Aufnahmen, ${n} Anreißer geprüft, ${fehler} ohne Bild` + (a.out ? ` → ${path.join(a.out, "bilder-pflicht.json")}` : ""));
  process.exit(fehler ? 1 : 0);
}

main().catch((f) => { console.error(f); process.exit(2); });
