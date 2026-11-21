#!/usr/bin/env node
// Karten auf einer Höhe: je Reihe von Karten (Raster, wischbare Reihe, „Neben“, „Diese Woche“) Ober- und Unterkante
// vergleichen. Eine Reihe besteht, wenn alle Karten oben und unten höchstens 1 px auseinanderliegen.
//   node wordpress/dev/kartenhoehe.mjs <basis-url> [--widths 390,820,1280] [weitere Pfade …]
// Unterkante: bei Karten mit eigener Fläche (Hintergrund) die Karte selbst, sonst die Kästen ihres Inhalts
// (Bild, Titel, Vorspann samt freigehaltener Zeilen), nicht die gestreckte Listenzelle.
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const LISTEN = ".karten, .neben, .woche__raster, .woche__gruppe ul";
const KARTE = ":scope > li, :scope > article, :scope > .woche__gruppe";
const PFADE = ["/", "/category/kultur/", "/category/kino/", "/events/", "/?s=tamil", "/production/", "/2026/10/"];

function argumente(argv) {
  const a = { basis: null, widths: [390, 820, 1280], pfade: [] };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--widths") a.widths = argv[++i].split(",").map(Number).filter(Boolean);
    else if (!a.basis) a.basis = argv[i].replace(/\/$/, "");
    else a.pfade.push(argv[i]);
  }
  return a;
}

async function messen(page) {
  return page.evaluate(({ LISTEN, KARTE }) => {
    const sichtbar = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== "hidden"; };
    const flaeche = (el) => {
      for (const x of [el, el.querySelector(":scope > a, :scope > .anr")].filter(Boolean)) {
        const bg = getComputedStyle(x).backgroundColor;
        if (bg && bg !== "transparent" && !/rgba\(0, 0, 0, 0\)/.test(bg)) return x.getBoundingClientRect();
      }
      // ohne eigene Fläche: die Kästen des Inhalts (Bild, Titel, Vorspann mit seiner Zeilenzahl), nicht die Karte selbst
      const rs = [...el.querySelectorAll("*")].filter((x) => x.children.length === 0 || x.matches("p, .rahmen") || !/^(transparent|rgba\(0, 0, 0, 0\))$/.test(getComputedStyle(x).backgroundColor)).map((x) => x.getBoundingClientRect()).filter((q) => q.width > 0 && q.height > 0);
      return { top: Math.min(...rs.map((q) => q.top)), bottom: Math.max(...rs.map((q) => q.bottom)) };
    };
    const reihen = [];
    for (const liste of document.querySelectorAll(LISTEN)) {
      if (liste.closest(".kacheln, .band, .fuss, .mehr, .tafel")) continue;
      const karten = [...liste.querySelectorAll(KARTE)].filter(sichtbar);
      if (karten.length < 2) continue;
      const boxen = karten.map((k) => ({ k, b: flaeche(k), r: k.getBoundingClientRect() })).sort((x, y) => x.r.top - y.r.top);
      let reihe = [];
      const fertig = () => { if (reihe.length > 1) reihen.push({ liste: liste.className, n: reihe.length, oben: Math.max(...reihe.map((x) => x.b.top)) - Math.min(...reihe.map((x) => x.b.top)), unten: Math.max(...reihe.map((x) => x.b.bottom)) - Math.min(...reihe.map((x) => x.b.bottom)), text: (reihe[0].k.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40) }); };
      for (const x of boxen) {
        if (reihe.length && x.r.top >= Math.min(...reihe.map((y) => y.r.bottom)) - 1) { fertig(); reihe = []; }
        reihe.push(x);
      }
      fertig();
    }
    return reihen;
  }, { LISTEN, KARTE });
}

async function main() {
  const a = argumente(process.argv.slice(2));
  if (!a.basis) { console.error("Aufruf: node wordpress/dev/kartenhoehe.mjs <basis-url> [--widths …] [pfade …]"); process.exit(2); }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
  await page.goto(a.basis + "/", { waitUntil: "domcontentloaded" });
  const artikel = await page.evaluate((b) => { const x = document.querySelector(".aufmacher a.anr"); return x && x.href.startsWith(b) ? x.href.slice(b.length) : null; }, a.basis);
  const pfade = [...new Set([...PFADE, ...(artikel ? [artikel] : []), ...a.pfade])];
  let reihenAlle = 0, fehler = 0;
  for (const pfad of pfade) {
    for (const w of a.widths) {
      await page.setViewportSize({ width: w, height: 900 });
      const antwort = await page.goto(a.basis + pfad, { waitUntil: "networkidle" }).catch(() => null);
      if (!antwort || antwort.status() >= 400) { console.log(`fehlt   ${w}  ${pfad}`); continue; }
      await page.evaluate(async () => { document.querySelectorAll("[style*=content-visibility], li").forEach((e) => (e.style.contentVisibility = "visible")); await Promise.all([...document.images].map((i) => { i.loading = "eager"; return i.decode().catch(() => {}); })); });
      const reihen = await messen(page);
      const schief = reihen.filter((r) => r.oben > 1 || r.unten > 1);
      reihenAlle += reihen.length; fehler += schief.length;
      console.log(`${schief.length ? "FEHLER" : "ok    "} ${String(w).padStart(4)}  ${pfad}  ${reihen.length} Reihen, ${schief.length} uneben`);
      for (const r of schief) console.log(`          ${r.liste}: ${r.n} Karten, oben Δ${r.oben.toFixed(1)} px, unten Δ${r.unten.toFixed(1)} px  „${r.text}“`);
    }
  }
  await browser.close();
  console.log(`\n${reihenAlle} Reihen geprüft, ${fehler} uneben (Abweichung > 1 px)`);
  process.exit(fehler ? 1 : 0);
}

main().catch((f) => { console.error(f); process.exit(2); });
