#!/usr/bin/env node
// Bildkanten auf gemeinsamen Linien (Luis, 22.11.2026: „Das muss alles auf einer Höhe sein“).
// Regel je mehrspaltigem Block der Startseite: Die Oberkante der Bilder ist in allen Spalten gleich, die Unterkante
// des letzten Bilds jeder Spalte ebenso. Text unter einer Karte zählt nicht (gemessen wird der Bildrahmen .rahmen).
// Dazu teilen alle Blöcke dieselbe linke und rechte Kante (die Inhaltsbreite der Seite).
//   node wordpress/dev/kantenlinie.mjs <basis-url> [--widths 820,1280,1440] [--alles] [weitere Pfade …]
// Ohne Pfade: Startseite und /?probe=ausgabe. --alles zeigt auch die Blöcke, die stimmen (mit ihren Kanten).
// Exit 1 bei einer Abweichung über 1 px.
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

// Block = Wurzel und die Bildrahmen, die zu ihm gehören. „kanten“: Der Block reicht von der linken bis zur rechten
// Inhaltskante (beim Stadtstreifen nur rechts: links steht dort der Kopf mit der Stadtwahl).
const BLOECKE = [
  { name: "Aufmacher und Weitere Meldungen", wurzel: ".oben:not(.oben--probe)", rahmen: ":scope > .aufmacher .rahmen, :scope > .meldungen .rahmen", kanten: "beide" },
  { name: "Nebenstücke", wurzel: ".oben:not(.oben--probe) > .neben", rahmen: ".rahmen", kanten: "beide" },
  { name: "Diese Woche", wurzel: "#diese-woche .woche__raster", rahmen: ".rahmen", kanten: "beide" },
  { name: "Küche", wurzel: ".kueche > .kueche__raster", rahmen: ".rahmen", kanten: "beide" },
  { name: "Rubrik (Bühne)", wurzel: ".rubrikblock__buehne", rahmen: ".rahmen", kanten: "beide" },
  { name: "Rubrik (Reihe)", wurzel: ".rubrikblock > .neben", rahmen: ".rahmen", kanten: "beide" },
  { name: "Ausgabe: Cover", wurzel: ".ausgabe__kopf", rahmen: ".rahmen", kanten: "beide" },
  { name: "Ausgabe: Stadtstreifen", wurzel: ".streifen__bahn", rahmen: "[data-stadt-karte]:not([hidden]) .rahmen", kanten: "rechts" },
  { name: "Ausgabe: Beistücke", wurzel: ".ausgabe__rest > .ausgabe__stuecke", rahmen: ".rahmen", kanten: "beide" },
  { name: "Ausgabe: Weitere Meldungen", wurzel: ".ausgabe__weitere > .ausgabe__stuecke", rahmen: ".rahmen", kanten: "beide" },
  { name: "Rubrikkacheln", wurzel: ".kacheln ul", rahmen: ".rahmen", kanten: "beide" },
];
const PFADE = ["/", "/?probe=ausgabe"];
const GRENZE = 1;

function argumente(argv) {
  const a = { basis: null, widths: [820, 1280, 1440], pfade: [], alles: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--widths") a.widths = argv[++i].split(",").map(Number).filter(Boolean);
    else if (argv[i] === "--alles") a.alles = true;
    else if (!a.basis) a.basis = argv[i].replace(/\/$/, "");
    else a.pfade.push(argv[i]);
  }
  return a;
}

async function messen(page) {
  return page.evaluate(({ BLOECKE }) => {
    const sichtbar = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== "hidden"; };
    const y0 = window.scrollY;
    const kasten = (el) => { const r = el.getBoundingClientRect(); return { l: r.left, r: r.right, o: r.top + y0, u: r.bottom + y0 }; };
    // Inhaltskanten der Seite: der erste .innen-Bereich im Hauptteil, ohne seinen Innenabstand
    const innen = document.querySelector("main .innen") || document.querySelector(".innen");
    const st = getComputedStyle(innen), ir = innen.getBoundingClientRect();
    const seite = { l: ir.left + parseFloat(st.paddingLeft), r: ir.right - parseFloat(st.paddingRight) };
    const bloecke = [];
    for (const b of BLOECKE) {
      for (const wurzel of document.querySelectorAll(b.wurzel)) {
        if (!sichtbar(wurzel)) continue;
        const rahmen = [...wurzel.querySelectorAll(b.rahmen)].filter(sichtbar).map(kasten);
        if (!rahmen.length) continue;
        // wischbare Reihe (breiter als ihr Platz): Die rechte Kante liegt mit Absicht außerhalb, Spalten gibt es nicht
        const rollt = [wurzel, ...wurzel.querySelectorAll("*")].some((e) => e.scrollWidth > e.clientWidth + 4 && /auto|scroll/.test(getComputedStyle(e).overflowX));
        // Reihen: Rahmen, deren senkrechte Spannen sich überlappen (eine große Karte neben einem Stapel = eine Reihe)
        const reihen = [];
        for (const x of [...rahmen].sort((p, q) => p.o - q.o)) {
          const treffer = reihen.filter((g) => g.some((y) => x.o < y.u - 1 && y.o < x.u - 1));
          if (!treffer.length) { reihen.push([x]); continue; }
          treffer[0].push(x);
          for (const g of treffer.slice(1)) { treffer[0].push(...g); reihen.splice(reihen.indexOf(g), 1); }
        }
        const zeilen = [];
        for (const reihe of reihen) {
          const spalten = new Map();
          for (const x of reihe) { const s = Math.round(x.l / 4); (spalten.get(s) || spalten.set(s, []).get(s)).push(x); }
          if (spalten.size < 2 || rollt) continue;
          const sp = [...spalten.values()].map((c) => ({ l: Math.min(...c.map((x) => x.l)), r: Math.max(...c.map((x) => x.r)), o: Math.min(...c.map((x) => x.o)), u: Math.max(...c.map((x) => x.u)), n: c.length })).sort((p, q) => p.l - q.l);
          zeilen.push({ spalten: sp, oben: Math.max(...sp.map((c) => c.o)) - Math.min(...sp.map((c) => c.o)), unten: Math.max(...sp.map((c) => c.u)) - Math.min(...sp.map((c) => c.u)) });
        }
        const l = Math.min(...rahmen.map((x) => x.l)), r = Math.max(...rahmen.map((x) => x.r));
        bloecke.push({
          name: b.name, zeilen, rollt, l, r,
          links: b.kanten === "beide" && !rollt ? l - seite.l : 0,
          rechts: !rollt ? r - seite.r : 0,
        });
      }
    }
    return { seite, bloecke };
  }, { BLOECKE });
}

const z = (n) => String(Math.round(n));
const spalte = (c) => `[${z(c.l)},${z(c.r)},${z(c.o)},${z(c.u)}]${c.n > 1 ? "×" + c.n : ""}`;

async function main() {
  const a = argumente(process.argv.slice(2));
  if (!a.basis) { console.error("Aufruf: node wordpress/dev/kantenlinie.mjs <basis-url> [--widths …] [--alles] [pfade …]"); process.exit(2); }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce", ignoreHTTPSErrors: true });
  const pfade = a.pfade.length ? a.pfade : PFADE;
  let geprueft = 0, fehler = 0;
  for (const pfad of pfade) {
    for (const w of a.widths) {
      await page.setViewportSize({ width: w, height: 900 });
      const antwort = await page.goto(a.basis + pfad, { waitUntil: "networkidle" }).catch(() => null);
      if (!antwort || antwort.status() >= 400) { console.log(`fehlt   ${w}  ${pfad}`); fehler++; continue; }
      await page.evaluate(async () => { document.querySelectorAll("[style*=content-visibility], li").forEach((e) => (e.style.contentVisibility = "visible")); await Promise.all([...document.images].map((i) => { i.loading = "eager"; return i.decode().catch(() => {}); })); window.scrollTo(0, 0); });
      const m = await messen(page);
      for (const b of m.bloecke) {
        geprueft++;
        const maengel = [];
        for (const zeile of b.zeilen) {
          if (zeile.oben > GRENZE) maengel.push(`Oberkanten ${z(zeile.oben)} px auseinander`);
          if (zeile.unten > GRENZE) maengel.push(`Unterkanten ${z(zeile.unten)} px auseinander`);
        }
        if (Math.abs(b.links) > GRENZE) maengel.push(`linke Kante ${z(b.l)} statt ${z(m.seite.l)}`);
        if (Math.abs(b.rechts) > GRENZE) maengel.push(`rechte Kante ${z(b.r)} statt ${z(m.seite.r)}`);
        if (maengel.length) fehler++;
        if (maengel.length || a.alles) {
          const kanten = b.zeilen.map((zeile) => zeile.spalten.map(spalte).join(" | ")).join("  //  ") || `[${z(b.l)},${z(b.r)}]${b.rollt ? " wischbar" : ""}`;
          console.log(`${maengel.length ? "SCHIEF" : "ok    "}  ${w}  ${pfad}  ${b.name}: ${maengel.join("; ") || "auf Linie"}  ${kanten}`);
        }
      }
    }
  }
  await browser.close();
  console.log(`${geprueft} Blöcke geprüft, ${fehler} mit Abweichung (Spalten als [links,rechts,oben,unten], Seitenkoordinaten)`);
  process.exit(fehler ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(2); });
