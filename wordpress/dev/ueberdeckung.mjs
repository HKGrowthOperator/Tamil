#!/usr/bin/env node
// Überdeckung beim Scrollen: Über den Scrollweg der Startseite darf kein Kartenlink einen anderen überdecken (etwa eine
// stehende Spalte, die über die Reihe darunter läuft, N-01). Geprüft bei 1024/1280/1440/1920 und Fensterhöhe 800/1080,
// in Schritten von 40 px bis 3000 px.
//   node wordpress/dev/ueberdeckung.mjs <basis-url> [pfad …]
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const BREITEN = [1024, 1280, 1440, 1920];
const HOEHEN = [800, 1080];

async function main() {
  const [basis, ...pfade] = process.argv.slice(2);
  if (!basis) { console.error("Aufruf: node wordpress/dev/ueberdeckung.mjs <basis-url> [pfad …]"); process.exit(2); }
  const browser = await browser_starten();
  let fehler = 0;
  for (const pfad of pfade.length ? pfade : ["/"]) {
    for (const w of BREITEN) for (const h of HOEHEN) {
      const page = await browser.newPage({ viewport: { width: w, height: h } });
      await page.goto(basis.replace(/\/$/, "") + pfad, { waitUntil: "networkidle" });
      let schlimmst = { flaeche: 0 };
      for (let y = 0; y <= 3000; y += 40) {
        await page.evaluate((y) => window.scrollTo(0, y), y);
        await page.evaluate(() => new Promise((ok) => requestAnimationFrame(() => requestAnimationFrame(ok))));
        const t = await page.evaluate(() => {
          const links = [...document.querySelectorAll("main a.anr")].filter((a) => { const r = a.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; });
          // sichtbare Fläche eines Links: der Kasten seines Bildrahmens (der Link selbst kann den Weg der Bahn umfassen)
          const kasten = (a) => (a.querySelector(".rahmen") || a).getBoundingClientRect();
          let best = { flaeche: 0 };
          for (let i = 0; i < links.length; i++) for (let j = i + 1; j < links.length; j++) {
            const a = links[i], b = links[j];
            if (a.contains(b) || b.contains(a)) continue;
            const p = kasten(a), q = kasten(b);
            const f = Math.max(0, Math.min(p.right, q.right) - Math.max(p.left, q.left)) * Math.max(0, Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top));
            if (f > best.flaeche) best = { flaeche: Math.round(f), hoehe: Math.round(Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top)), a: (a.textContent || "").trim().slice(0, 40), b: (b.textContent || "").trim().slice(0, 40) };
          }
          return best;
        });
        if (t.flaeche > schlimmst.flaeche) schlimmst = { ...t, y };
      }
      const ok = schlimmst.flaeche <= 4;
      if (!ok) fehler++;
      console.log(`${ok ? "ok    " : "FEHLER"} ${w} × ${h}  ${pfad}` + (ok ? "" : `  größte Überdeckung ${schlimmst.hoehe} px hoch bei Scrollstand ${schlimmst.y}: „${schlimmst.a}“ / „${schlimmst.b}“`));
      await page.close();
    }
  }
  await browser.close();
  console.log(fehler ? `\n${fehler} Fenster mit Überdeckung` : "\nkeine Überdeckung");
  process.exit(fehler ? 1 : 0);
}

function browser_starten() { return chromium.launch(); }

main().catch((f) => { console.error(f); process.exit(2); });
