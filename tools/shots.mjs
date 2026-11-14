#!/usr/bin/env node
// Screenshots und Sichtprüfung für Tamil.de (Richtungsskizzen, Theme, Cockpit, Live-Seiten).
//
//   node tools/shots.mjs <ziel> [<ziel> …] --out <ordner> [--widths 390,820,1280] [--kacheln] [--name <präfix>]
//                        [--login <url>]   (Cockpit: Benutzer/Passwort aus SHOTS_USER / SHOTS_PASSWORD)
//
// <ziel> ist eine URL (http/https) oder eine lokale HTML-Datei. Lokale Dateien liefert ein eingebauter Server aus, dessen
// Wurzel das aktuelle Verzeichnis ist (vom Repo-Root starten, dann funktionieren Pfade wie ../../prototyp/static/img/).
//
// Je Ziel und Breite: Vollseiten-PNG (mit --kacheln zusätzlich Ausschnitte für die Durchsicht) und Prüfungen:
//   ueberlauf    Seite scrollt seitlich (scrollWidth > Breite)                → Fehler
//   konsole      console.error, Seitenfehler, fehlgeschlagene Anfragen        → Fehler
//   bilder       Bilder ohne Inhalt (naturalWidth 0)                           → Fehler
//   schriften    deklarierte @font-face, die nicht geladen wurden              → Warnung
//   tippflaechen sichtbare Links/Knöpfe kleiner als 44 × 44 px (nur ≤ 820 px)   → Warnung
//   tamil        Tamil-Text ohne lang="ta" im Elternpfad                       → Warnung
// Ergebnis: <out>/bericht.json und eine Zusammenfassung auf stdout. Rückgabewert 1 bei mindestens einem Fehler.

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const TYPEN = {
  ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".mjs": "text/javascript",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif", ".woff2": "font/woff2", ".woff": "font/woff",
  ".ttf": "font/ttf", ".ico": "image/x-icon", ".txt": "text/plain",
};

function argumente(argv) {
  const a = { ziele: [], out: null, widths: [390, 820, 1280], kacheln: false, name: null, login: null };
  for (let i = 0; i < argv.length; i++) {
    const x = argv[i];
    if (x === "--out") a.out = argv[++i];
    else if (x === "--widths") a.widths = argv[++i].split(",").map(Number).filter(Boolean);
    else if (x === "--kacheln") a.kacheln = true;
    else if (x === "--name") a.name = argv[++i];
    else if (x === "--login") a.login = argv[++i];
    else if (x === "-h" || x === "--help") a.hilfe = true;
    else a.ziele.push(x);
  }
  return a;
}

function server(wurzel) {
  return new Promise((ok) => {
    const s = http.createServer((req, res) => {
      const roh = decodeURIComponent(new URL(req.url, "http://x").pathname);
      const datei = path.resolve(wurzel, "." + roh);
      if (!datei.startsWith(wurzel)) { res.writeHead(403).end(); return; }
      fs.stat(datei, (err, st) => {
        const ziel = !err && st.isDirectory() ? path.join(datei, "index.html") : datei;
        fs.readFile(ziel, (e, inhalt) => {
          if (e) { res.writeHead(404).end(); return; }
          res.writeHead(200, { "Content-Type": TYPEN[path.extname(ziel).toLowerCase()] || "application/octet-stream" });
          res.end(inhalt);
        });
      });
    });
    s.listen(0, "127.0.0.1", () => ok(s));
  });
}

function kurzname(ziel) {
  const roh = /^https?:/.test(ziel) ? new URL(ziel).pathname.replace(/\/$/, "/index") : ziel;
  return roh.replace(/\.html?$/, "").replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "").slice(-60) || "seite";
}

async function pruefen(page, breite) {
  return page.evaluate(({ breite }) => {
    const sichtbar = (el) => {
      const r = el.getBoundingClientRect();
      const st = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && st.visibility !== "hidden" && st.display !== "none";
    };
    const ergebnis = {
      scrollbreite: document.documentElement.scrollWidth,
      bilder: [...document.images].filter((i) => i.complete && i.naturalWidth === 0 && i.currentSrc).map((i) => i.currentSrc).slice(0, 10),
      schriften: [...document.fonts].filter((f) => f.status === "error").map((f) => `${f.family} ${f.weight}`).slice(0, 10),
      tippflaechen: [],
      tamil: 0,
    };
    if (breite <= 820) {
      for (const el of document.querySelectorAll("a[href], button, input, select, textarea, [role=button]")) {
        if (!sichtbar(el)) continue;
        const r = el.getBoundingClientRect();
        // Links im Fließtext zählen nicht (WCAG 2.5.8 Ausnahme „inline“)
        if (el.tagName === "A" && getComputedStyle(el).display === "inline" && el.closest("p, li")) continue;
        if (r.width < 44 || r.height < 44) {
          ergebnis.tippflaechen.push(`${el.tagName.toLowerCase()} „${(el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 30)}“ ${Math.round(r.width)}×${Math.round(r.height)}`);
        }
      }
      ergebnis.tippflaechen = ergebnis.tippflaechen.slice(0, 15);
    }
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (/[஀-௿]/.test(n.nodeValue) && !n.parentElement.closest('[lang|="ta"]')) ergebnis.tamil++;
    }
    return ergebnis;
  }, { breite });
}

async function main() {
  const a = argumente(process.argv.slice(2));
  if (a.hilfe || !a.ziele.length || !a.out) {
    console.log("node tools/shots.mjs <url|datei.html> […] --out <ordner> [--widths 390,820,1280] [--kacheln] [--login <url>]");
    process.exit(a.hilfe ? 0 : 2);
  }
  fs.mkdirSync(a.out, { recursive: true });
  const wurzel = process.cwd();
  const srv = a.ziele.some((z) => !/^https?:/.test(z)) ? await server(wurzel) : null;
  const basis = srv ? `http://127.0.0.1:${srv.address().port}` : null;
  const browser = await chromium.launch();
  const bericht = { stand: new Date().toISOString(), ergebnisse: [] };
  let fehler = 0;

  for (const breite of a.widths) {
    const ctx = await browser.newContext({ viewport: { width: breite, height: breite < 600 ? 844 : 900 }, deviceScaleFactor: 1, locale: "de-DE" });
    if (a.login) {
      const p = await ctx.newPage();
      await p.goto(a.login, { waitUntil: "domcontentloaded" });
      await p.fill('input[name="user"]', process.env.SHOTS_USER || "");
      await p.fill('input[name="password"]', process.env.SHOTS_PASSWORD || "");
      await Promise.all([p.waitForLoadState("networkidle"), p.click('button[type="submit"], form button')]);
      await p.close();
    }
    for (const ziel of a.ziele) {
      const url = /^https?:/.test(ziel) ? ziel : `${basis}/${path.relative(wurzel, path.resolve(ziel)).split(path.sep).join("/")}`;
      const page = await ctx.newPage();
      const konsole = [];
      page.on("console", (m) => m.type() === "error" && konsole.push(m.text().slice(0, 200)));
      page.on("pageerror", (e) => konsole.push(`Seitenfehler: ${String(e).slice(0, 200)}`));
      page.on("requestfailed", (r) => konsole.push(`Anfrage fehlgeschlagen: ${r.url().slice(0, 160)}`));
      page.on("response", (r) => r.status() >= 400 && konsole.push(`HTTP ${r.status()}: ${r.url().slice(0, 160)}`));
      let status = 0;
      try {
        const resp = await page.goto(url, { waitUntil: "networkidle", timeout: 45000 });
        status = resp ? resp.status() : 0;
      } catch (e) {
        konsole.push(`Laden fehlgeschlagen: ${String(e).slice(0, 200)}`);
      }
      // Lazy-Bilder laden: einmal durchscrollen
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 50)); }
        window.scrollTo(0, 0);
        await document.fonts.ready;
      }).catch(() => {});
      await page.waitForLoadState("networkidle").catch(() => {});
      const p = await pruefen(page, breite).catch((e) => ({ fehler: String(e) }));
      const name = `${a.name ? a.name + "-" : ""}${kurzname(ziel)}-${breite}`;
      const datei = path.join(a.out, `${name}.png`);
      await page.screenshot({ path: datei, fullPage: true });
      const kacheln = [];
      if (a.kacheln) {
        const hoehe = await page.evaluate(() => document.documentElement.scrollHeight);
        const schritt = Math.round((breite < 600 ? 844 : 900) * 1.5);
        for (let y = 0, i = 0; y < hoehe && i < 12; y += schritt, i++) {
          const k = path.join(a.out, `${name}-k${i}.png`);
          await page.screenshot({ path: k, fullPage: true, clip: { x: 0, y, width: breite, height: Math.min(schritt, hoehe - y) } });
          kacheln.push(k);
        }
      }
      const e = {
        ziel, url, breite, status, datei, kacheln,
        ueberlauf: p.scrollbreite > breite ? p.scrollbreite - breite : 0,
        konsole, bilder: p.bilder || [], schriften: p.schriften || [], tippflaechen: p.tippflaechen || [], tamil_ohne_lang: p.tamil || 0,
      };
      e.fehler = (e.ueberlauf > 0) + (konsole.length > 0) + (e.bilder.length > 0) + (status >= 400 ? 1 : 0);
      fehler += e.fehler;
      bericht.ergebnisse.push(e);
      const warn = [e.schriften.length && `${e.schriften.length} Schriften fehlen`, e.tippflaechen.length && `${e.tippflaechen.length} kleine Tippflächen`, e.tamil_ohne_lang && `${e.tamil_ohne_lang}× Tamil ohne lang`].filter(Boolean);
      const fehl = [e.ueberlauf && `seitlich ${e.ueberlauf}px`, konsole.length && `${konsole.length} Konsolenfehler`, e.bilder.length && `${e.bilder.length} Bilder leer`, status >= 400 && `HTTP ${status}`].filter(Boolean);
      console.log(`${fehl.length ? "FEHLER" : "ok    "} ${String(breite).padStart(4)}  ${ziel}${fehl.length ? "  · " + fehl.join(", ") : ""}${warn.length ? "  · Hinweis: " + warn.join(", ") : ""}`);
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  if (srv) srv.close();
  bericht.fehler = fehler;
  fs.writeFileSync(path.join(a.out, "bericht.json"), JSON.stringify(bericht, null, 2));
  console.log(`\n${bericht.ergebnisse.length} Aufnahmen, ${fehler} Fehler → ${path.join(a.out, "bericht.json")}`);
  process.exit(fehler ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(2); });
