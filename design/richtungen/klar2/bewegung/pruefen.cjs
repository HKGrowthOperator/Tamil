// Prüfung der Bewegungsvorschau (vom Repo-Root): node design/richtungen/klar2/bewegung/pruefen.cjs [--bilder]
// 1. Endzustand: je Variante und Breite einmal ganz durchscrollen, warten, nach oben; dann Lage jedes Elements
//    gegen ../index.html (klar2 ohne Bewegung) vergleichen und prüfen, dass nichts versetzt, verblasst oder beschnitten bleibt.
// 2. Zeilen: geteilte Überschriften sind so hoch wie die ungeteilten.
// 3. Ersatzweg ohne CSS-Scroll-Timelines und „Bewegung reduzieren“.
// 4. Mit --bilder: Einzelbilder bei 390 px nach shots/frames/ (JPEG 70).
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const WURZEL = process.cwd();
const ORDNER = "design/richtungen/klar2/bewegung";
const TYPEN = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2" };
const warte = (ms) => new Promise((ok) => setTimeout(ok, ms));

function server() {
  return new Promise((ok) => {
    const s = http.createServer((req, res) => {
      const datei = path.resolve(WURZEL, "." + decodeURIComponent(new URL(req.url, "http://x").pathname));
      fs.readFile(datei, (e, inhalt) => {
        if (e) return res.writeHead(404).end();
        res.writeHead(200, { "Content-Type": TYPEN[path.extname(datei)] || "application/octet-stream" }).end(inhalt);
      });
    });
    s.listen(0, "127.0.0.1", () => ok(s));
  });
}

// Lage aller Elemente in Kopf, Band und Hauptteil (ohne die Leiste der Vorschau)
const LAGE = () => [...document.querySelectorAll("header *, nav.band *, main *")].map((el) => {
  const r = el.getBoundingClientRect();
  const klasse = [...el.classList].filter((k) => k !== "da" && k !== "laeuft").join(" ");
  return [el.tagName + "." + klasse, Math.round(r.left * 2) / 2, Math.round((r.top + scrollY) * 2) / 2, Math.round(r.width * 2) / 2, Math.round(r.height * 2) / 2];
});

const REST = () => {
  const auffaellig = [];
  for (const el of document.querySelectorAll("header, header *, nav.band, nav.band *, main, main *")) {
    const s = getComputedStyle(el);
    const fehler = [];
    if (s.opacity !== "1") fehler.push("opacity " + s.opacity);
    if (s.translate !== "none" && s.translate !== "0px") fehler.push("translate " + s.translate);
    if (s.scale !== "none" && s.scale !== "1") fehler.push("scale " + s.scale);
    if (s.clipPath !== "none" && !/^inset\(0(px)?\)$/.test(s.clipPath) && !el.matches(".nur-vorlesen")) fehler.push("clip " + s.clipPath);
    if (fehler.length) auffaellig.push(el.tagName + "." + el.className + ": " + fehler.join(", "));
  }
  // Deckfläche des Vorhangs muss weg sein (Breite 0)
  const decke = getComputedStyle(document.querySelector(".woche"), "::after");
  if (decke.content !== "none" && decke.scale !== "0 1") auffaellig.push("woche::after: scale " + decke.scale);
  return {
    auffaellig: auffaellig.slice(0, 10),
    zeilenReste: document.querySelectorAll(".zeile, [data-zeilen]").length,
    laeuft: document.querySelectorAll(".laeuft").length,
    nichtDa: document.querySelectorAll("[data-art]:not(.da)").length,
  };
};

async function durchscrollen(page) {
  await page.evaluate(async () => {
    const w = (ms) => new Promise((ok) => setTimeout(ok, ms));
    for (let y = 0; y < document.documentElement.scrollHeight; y += 200) { scrollTo(0, y); await w(40); }
    await w(2500);
    scrollTo(0, 0);
    await w(200);
  });
}

async function main() {
  const bilder = process.argv.includes("--bilder");
  const srv = await server();
  const basis = `http://127.0.0.1:${srv.address().port}/${ORDNER}`;
  const browser = await chromium.launch();
  const konsole = [];
  let fehler = 0;
  const neueSeite = async (opts, url, init) => {
    const ctx = await browser.newContext({ deviceScaleFactor: 1, locale: "de-DE", ...opts });
    const page = await ctx.newPage();
    if (init) await page.addInitScript(init);
    page.on("console", (m) => m.type() === "error" && konsole.push(url + " " + m.text()));
    page.on("pageerror", (e) => konsole.push(url + " Seitenfehler " + e));
    page.on("requestfailed", (r) => konsole.push(url + " Anfrage " + r.url()));
    await page.goto(url, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await warte(300);
    return { ctx, page };
  };
  const melde = (ok, text) => { if (!ok) fehler++; console.log((ok ? "ok    " : "FEHLER") + " " + text); };

  // 1. Endzustand gleich klar2
  for (const breite of [390, 820, 1280]) {
    const vp = { viewport: { width: breite, height: breite < 600 ? 844 : 900 } };
    const ref = await neueSeite(vp, `${basis}/../index.html`);
    const soll = await ref.page.evaluate(LAGE);
    await ref.ctx.close();
    for (const v of ["a", "b", "c", "d", "aus"]) {
      const { ctx, page } = await neueSeite(vp, `${basis}/index.html#${v}`);
      await durchscrollen(page);
      const ist = await page.evaluate(LAGE);
      const rest = await page.evaluate(REST);
      const abw = [];
      if (ist.length !== soll.length) abw.push(`Elementzahl ${ist.length} statt ${soll.length}`);
      for (let i = 0; i < Math.min(ist.length, soll.length) && abw.length < 5; i++) {
        const a = ist[i], b = soll[i];
        if (a[0] !== b[0] || [1, 2, 3, 4].some((k) => Math.abs(a[k] - b[k]) > 0.5)) abw.push(`${a.join(" ")} ≠ ${b.join(" ")}`);
      }
      const gut = !abw.length && !rest.auffaellig.length && !rest.zeilenReste && !rest.laeuft && !rest.nichtDa;
      melde(gut, `${breite} #${v}: Endlage wie klar2 (${ist.length} Elemente)` + (gut ? "" : " " + JSON.stringify({ abw, ...rest })));
      await ctx.close();
    }
  }

  // 2. Geteilte Überschriften gleich hoch wie ungeteilte (B teilt alle Titel unterhalb des ersten Bildschirms)
  for (const breite of [390, 1280]) {
    const vp = { viewport: { width: breite, height: breite < 600 ? 844 : 900 } };
    const hoehen = () => [...document.querySelectorAll(".titel, .block-titel, .woche__titel")].map((h) => [h.textContent.replace(/\s+/g, " ").trim(), Math.round(h.getBoundingClientRect().height * 2) / 2, !!h.querySelector(".zeile")]);
    const ref = await neueSeite(vp, `${basis}/../index.html`);
    const soll = await ref.page.evaluate(hoehen);
    await ref.ctx.close();
    for (const v of ["b", "d"]) {
      const { ctx, page } = await neueSeite(vp, `${basis}/index.html#${v}`);
      const ist = await page.evaluate(hoehen);
      const geteilt = ist.filter((x) => x[2]).length;
      const abw = ist.filter((x, i) => x[0] !== soll[i][0] || Math.abs(x[1] - soll[i][1]) > 0.5);
      melde(!abw.length && geteilt > 0, `${breite} #${v}: ${geteilt} Überschriften geteilt, Text und Höhe gleich` + (abw.length ? " " + JSON.stringify(abw.slice(0, 3)) : ""));
      await ctx.close();
    }
  }

  // 2b. Schneller Sprung ans Ende: nichts darf versteckt zurückbleiben
  for (const v of ["a", "b", "c", "d"]) {
    const { ctx, page } = await neueSeite({ viewport: { width: 390, height: 844 } }, `${basis}/index.html#${v}`);
    await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
    await warte(2500);
    await page.evaluate(() => scrollTo(0, 0)); // Kopf und Tiefe hängen am Scrollweg: oben wieder neutral
    await warte(200);
    const r = await page.evaluate(REST);
    melde(!r.nichtDa && !r.auffaellig.length && !r.zeilenReste, `390 #${v}: Sprung ans Ende, danach alles sichtbar` + (r.nichtDa || r.auffaellig.length ? " " + JSON.stringify(r) : ""));
    await ctx.close();
  }

  // 2c. Umschalten über die Leiste: Adresse, Anfang der Seite, Zustände neu
  {
    const { ctx, page } = await neueSeite({ viewport: { width: 390, height: 844 } }, `${basis}/index.html`);
    const start = await page.evaluate(() => location.hash);
    await page.evaluate(() => scrollTo(0, 1500));
    await warte(1500);
    await page.click('.wahl button[data-variante="b"]');
    await warte(400);
    const nachB = await page.evaluate(() => ({ hash: location.hash, y: scrollY, v: document.documentElement.dataset.bewegung, versteckt: document.querySelectorAll("[data-art]:not(.da)").length, geteilt: document.querySelectorAll("[data-zeilen]").length, gedrueckt: document.querySelector('.wahl [aria-pressed="true"]').dataset.variante }));
    await page.click('.wahl button[data-variante="aus"]');
    await warte(300);
    const nachAus = await page.evaluate(() => ({ hash: location.hash, bewegt: document.documentElement.classList.contains("bewegt"), art: document.querySelectorAll("[data-art]").length, geteilt: document.querySelectorAll("[data-zeilen]").length }));
    melde(start === "#d" && nachB.hash === "#b" && nachB.y === 0 && nachB.v === "b" && nachB.versteckt > 0 && nachB.geteilt > 0 && nachB.gedrueckt === "b"
      && nachAus.hash === "#aus" && !nachAus.bewegt && !nachAus.art && !nachAus.geteilt,
      "Umschalten: " + JSON.stringify({ start, nachB, nachAus }));
    await ctx.close();
  }

  // 3a. Ersatzweg: Browser ohne Scroll-Timelines (CSS.supports meldet nein)
  {
    const init = () => { const s = CSS.supports.bind(CSS); CSS.supports = (...a) => (/animation-timeline/.test(a.join(" ")) ? false : s(...a)); };
    const { ctx, page } = await neueSeite({ viewport: { width: 390, height: 844 } }, `${basis}/index.html#d`, init);
    const werte = await page.evaluate(async () => {
      const w = (ms) => new Promise((ok) => setTimeout(ok, ms));
      scrollTo(0, 60); await w(150);
      const logo = getComputedStyle(document.querySelector(".kopf__logo"));
      const mitte = { sda: document.documentElement.classList.contains("sda"), scale: logo.scale, opacity: logo.opacity };
      scrollTo(0, 1200); await w(150);
      const linie = getComputedStyle(document.querySelector(".band"), "::after").scale;
      const tiefe = getComputedStyle(document.querySelector(".aufmacher .rahmen img")).translate;
      return { ...mitte, linie, tiefe };
    });
    melde(!werte.sda && werte.scale !== "1" && werte.scale !== "none" && werte.linie !== "0 1" && /40px/.test(werte.tiefe),
      "Ersatzweg ohne Scroll-Timelines: " + JSON.stringify(werte));
    await ctx.close();
  }

  // 3b. Bewegung reduzieren: nichts versteckt, nichts geteilt, Leiste erklärt es
  for (const v of ["a", "b", "c", "d"]) {
    const { ctx, page } = await neueSeite({ viewport: { width: 390, height: 844 }, reducedMotion: "reduce" }, `${basis}/index.html#${v}`);
    await page.evaluate(() => scrollTo(0, 2100));
    await warte(150);
    const r = await page.evaluate(REST);
    const info = await page.evaluate(() => ({ bewegt: document.documentElement.classList.contains("bewegt"), text: document.getElementById("wahl-text").textContent, art: document.querySelectorAll("[data-art]").length }));
    melde(!info.bewegt && !info.art && !r.auffaellig.length && !r.zeilenReste && /Bewegung reduziert \(Systemeinstellung\)/.test(info.text),
      `reduziert #${v}: alles sichtbar und still, Leiste: „${info.text}“`);
    if (bilder && v === "d") {
      await page.screenshot({ path: `${ORDNER}/shots/frames/reduziert-1-woche.jpg`, type: "jpeg", quality: 70 });
      await page.evaluate(() => scrollTo(0, 0)); await warte(100);
      await page.screenshot({ path: `${ORDNER}/shots/frames/reduziert-0-oben.jpg`, type: "jpeg", quality: 70 });
    }
    await ctx.close();
  }

  // 4. Einzelbilder mitten in der Bewegung, 390 × 844
  if (bilder) {
    fs.mkdirSync(`${ORDNER}/shots/frames`, { recursive: true });
    // [Name, Ziel-Scroll in px oder Selektor (Oberkante 70 % hoch im Bild), Wartezeit nach Ankunft in ms]
    const PLAN = {
      a: [["1-liste-steigt", 560, 60], ["2-liste-ende", 560, 900], ["3-woche-steigt", ".woche", 120], ["4-kueche-steigt", ".kueche", 120]],
      b: [["1-bilder-decken-auf", 560, 120], ["2-liste-ende", 560, 1100], ["3-kanguva-deckt-auf", ".woche .kachel--gross", 150], ["4-kueche-deckt-auf", ".kueche", 200]],
      c: [["1-kopf-faltet", 55, 0], ["2-band-steht", 330, 0], ["3-flaeche-zieht-auf", ".woche", 150], ["4-flaeche-inhalt", ".woche", 650]],
      d: [["1-kopf-faltet", 55, 0], ["2-liste-steigt", 560, 60], ["3-flaeche-zieht-auf", ".woche", 150], ["4-kanguva-deckt-auf", ".woche .kachel--gross", 560]],
    };
    for (const [v, plan] of Object.entries(PLAN)) {
      const { ctx, page } = await neueSeite({ viewport: { width: 390, height: 844 } }, `${basis}/index.html#${v}`);
      for (const [name, ziel, ms] of plan) {
        // wie ein Daumen: in 120-px-Schritten pro Bild hinscrollen
        await page.evaluate(async (ziel) => {
          const y = typeof ziel === "number" ? ziel : document.querySelector(ziel).getBoundingClientRect().top + scrollY - innerHeight * 0.7;
          const frame = () => new Promise((ok) => requestAnimationFrame(ok));
          let jetzt = scrollY;
          while (Math.abs(jetzt - y) > 1) { jetzt += Math.max(-120, Math.min(120, y - jetzt)); scrollTo(0, jetzt); await frame(); }
          await frame(); await frame();
        }, ziel);
        await warte(ms);
        await page.screenshot({ path: `${ORDNER}/shots/frames/${v}-${name}.jpg`, type: "jpeg", quality: 70 });
      }
      await ctx.close();
    }
  }

  await browser.close();
  srv.close();
  melde(!konsole.length, "Konsole ohne Fehler" + (konsole.length ? ": " + konsole.slice(0, 5).join(" | ") : ""));
  process.exit(fehler ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(2); });
