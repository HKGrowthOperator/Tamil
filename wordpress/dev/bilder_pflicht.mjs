#!/usr/bin/env node
// Bilderpflicht prüfen (Luis, 17.11.2026): Jeder sichtbare Anreißer, jede Listenzeile, Kachel, jedes Suchergebnis,
// „Weiterlesen“ und jeder Kino- und Termineintrag zeigt ein geladenes Bild. Ausnahmen: Rubrikband, Fußlisten,
// Formulare und reine Textseiten (Impressum, Datenschutz).
//
// Signet an jedem Post (Luis, 19.11.2026, Theme 3.6.0): Jeder Anreißer mit Bild und das Bild des Artikels tragen den
// kleinen Bogen (.signatur-ecke) in ihrem Rahmen. Geprüft wird, dass er da und sichtbar ist (mindestens 18 px breit,
// mit Bilddatei), bündig unten rechts im Bild sitzt, zuoberst liegt (nichts darüber) und weder Text im Bild (Dachzeile,
// Titel) noch das Schild „Symbolbild“ überdeckt (Rechtecke der Textzeilen und des Schilds). Ausgenommen sind
// Rubrikkacheln (Navigation), Leerzustände ohne Beitrag, Verzeichniseinträge und Seiten. Ergebnis: Anteil in Prozent
// je Seite und gesamt; jeder fehlende oder falsche Bogen zählt als Fehler.
//
// Jede Meldung als Karte (Luis, 20.11.2026, Theme 3.7.0): Jeder Beitrags-Anreißer mit Bild trägt seinen Titel im Bild
// (Titel in .imbild im Rahmen). Ausnahmen werden mit Namen gezählt, nicht still weggelassen: Rubrikkachel
// (Navigation), Leerzustand, Verzeichnis, Seite, Tabelle (Spielorte der Kinotabelle) und der Artikel selbst (Titel über
// dem Bild). Ergebnis: Anteil in Prozent; jede Karte ohne Titel im Bild (etwa eine alte Zeile) zählt als Fehler.
//
//   node wordpress/dev/bilder_pflicht.mjs <basis-url> [--out <ordner>] [--widths 390,820,1280] [weitere Pfade …]
//
// Besucht Startseite, einen Artikel (den ersten Link der Startseite), alle Rubriken aus dem Band, /events/, die Suche,
// eine 404-Seite und – falls vorhanden – /kontakt/, /production/, /werben/, /verzeichnis/, /einreichen/; dazu weitere
// Pfade aus der Befehlszeile (etwa ein Artikel mit Titelkarte). Je Breite: Monate aufklappen, ganz nach unten scrollen
// (Bewegung D blendet beim Scrollen ein, „lazy“-Bilder laden erst im Bild), dann jedes Anreißer-Element prüfen: Es
// braucht ein <img> mit naturalWidth > 0. Werbeplätze (.ad, .anzeige) werden getrennt gemeldet und lassen die Prüfung
// nicht scheitern (Baustein Werbung im Plugin). Rückgabewert 1, wenn ein Anreißer ohne Bild, ein Bild ohne richtiges
// Signet oder ein Beitrags-Anreißer ohne Titel im Bild gefunden wurde.

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

// Anreißer-Elemente des Themes (inc/anreisser.php, template-parts/*) und des Plugins (Verzeichnis)
const ANREISSER = [
  ".aufmacher", ".karte", ".kachel", ".stueck", ".meldung", ".zeile", "li.grafik", ".kacheln li", ".vz-eintrag",
  ".beistueck", ".zeitkarte", // Startseiten-Proben (/?probe=cover|news|community|ausgabe als weiterer Pfad)
  ".tafel--bilder tbody tr:not(.land)", "article.artikel:not(.seite)",
].join(", ");
const WERBUNG = ".ad, .anzeige, .tz-anzeige, .wb-anzeige";
// ohne Signet: Rubrikkacheln (Navigation), Leerzustände, Verzeichnis (Plugin und Profil), Seiten
const OHNE_SIGNET = ".kacheln li, li.grafik--leer, .vz-eintrag, article.vz-artikel, article.seite";
// Anreißer ohne Titel im Bild, mit Namen (Reihenfolge = Vorrang)
const AUSNAHMEN_KARTE = [
  ["Rubrikkachel (Navigation)", ".kacheln li"],
  ["Leerzustand", "li.grafik--leer"],
  ["Verzeichnis", ".vz-eintrag, article.vz-artikel"],
  ["Seite", "article.seite"],
  ["Tabelle (Spielorte)", ".tafel--bilder tbody tr"],
  ["Artikel (Titel über dem Bild)", "article.artikel"],
];
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
  // Bilder, die noch laden, einzeln ins Bild holen und je Bild auf „load“ oder „error“ warten (höchstens 8 s je Bild).
  // Früher sprang eine Schleife ohne Pause durch alle offenen Bilder: Ein „lazy“-Bild, das nur kurz im Bild war, wurde
  // dann oft gar nicht angefragt und als „ohne Bild“ gemeldet, obwohl Besucher es geladen sehen (Kinokachel „Diese
  // Woche“ bei 390, 21.11.). Ein Bild, das schon fertig ist (auch fehlerhaft: complete, naturalWidth 0), wird nicht
  // abgewartet und bleibt so ein Fehler; ein Bild, das nach 8 s nicht da ist, ebenfalls.
  const anzahl = await page.evaluate(() => {
    const offen = [...document.images].filter((i) => !i.complete);
    offen.forEach((img, n) => img.setAttribute("data-bp-offen", String(n)));
    return offen.length;
  });
  for (let n = 0; n < anzahl; n++) {
    await page.evaluate(async (n) => {
      const img = document.querySelector(`img[data-bp-offen="${n}"]`);
      if (!img) return;
      img.removeAttribute("data-bp-offen");
      img.scrollIntoView({ block: "center" });
      if (img.complete) return;
      await new Promise((ok) => {
        const fertig = () => { clearTimeout(uhr); ok(); };
        const uhr = setTimeout(fertig, 8000);
        img.addEventListener("load", fertig, { once: true });
        img.addEventListener("error", fertig, { once: true });
        if (img.complete) fertig();
      });
    }, n);
  }
}

async function pruefen(page, sel) {
  return page.evaluate(({ ANREISSER, WERBUNG, AUSNAHMEN, OHNE_SIGNET, AUSNAHMEN_KARTE }) => {
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

    // Signet: der Rahmen mit dem geladenen Bild, darin direkt die Spanne .signatur-ecke
    const schnitt = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
    const textZeilen = (wurzel) => {
      const out = [];
      const w = document.createTreeWalker(wurzel, NodeFilter.SHOW_TEXT);
      for (let n = w.nextNode(); n; n = w.nextNode()) {
        if (!n.textContent.trim()) continue;
        const r = document.createRange();
        r.selectNodeContents(n);
        out.push(...[...r.getClientRects()].filter((q) => q.width > 0 && q.height > 0));
      }
      return out;
    };
    // Lage des Bilds ohne Verschiebungen am Bild selbst (Tiefe des Aufmachers beim Scrollen)
    const bildBox = (img) => {
      const p = img.offsetParent ? img.offsetParent.getBoundingClientRect() : { left: 0, top: 0 };
      const left = p.left + img.offsetLeft, top = p.top + img.offsetTop;
      return { left, top, right: left + img.offsetWidth, bottom: top + img.offsetHeight };
    };
    const mitBild = einzeln.filter((el) => geladen(el) && !el.matches(OHNE_SIGNET) && !el.closest(OHNE_SIGNET));
    const signetFehler = [];
    let signetOk = 0;
    for (const el of mitBild) {
      const rahmen = [...el.querySelectorAll(".rahmen, .artikel__figur, .bild-ecke")].find((r) => [...r.querySelectorAll(":scope > img")].some((i) => i.complete && i.naturalWidth > 0));
      const fehler = (grund) => signetFehler.push({ element: kennung(el), text: kurz(el), grund });
      if (!rahmen) { fehler("kein Rahmen mit Bild"); continue; }
      const sig = rahmen.querySelector(":scope > .signatur-ecke");
      if (!sig) { fehler("kein Signet im Rahmen"); continue; }
      const st = getComputedStyle(sig), nach = getComputedStyle(sig, "::after");
      const r = sig.getBoundingClientRect();
      if (st.display === "none" || st.visibility === "hidden" || Number(st.opacity) < 1 || r.width < 18 || !/ecke(-rot)?\.svg/.test(nach.backgroundImage)) { fehler(`nicht sichtbar (${Math.round(r.width)} px)`); continue; }
      if (sig.getAttribute("aria-hidden") !== "true") { fehler("nicht aria-hidden"); continue; }
      const b = bildBox(rahmen.querySelector(":scope > img"));
      if (Math.abs(r.right - b.right) > 1.5 || Math.abs(r.bottom - b.bottom) > 1.5) { fehler(`nicht bündig unten rechts (Δx ${Math.round(r.right - b.right)}, Δy ${Math.round(r.bottom - b.bottom)})`); continue; }
      const schild = rahmen.querySelector(":scope > .symbolbild");
      if (schild && schnitt(r, schild.getBoundingClientRect()) > 0) { fehler("überdeckt das Schild „Symbolbild“"); continue; }
      const text = rahmen.querySelector(":scope > .imbild");
      const unter = text ? textZeilen(text).find((z) => schnitt(r, z) > 0) : null;
      if (unter) { fehler("überdeckt Text im Bild"); continue; }
      // zuoberst: in der Mitte des Bogens liegt nichts darüber (wischbare Reihen dafür ohne Einrasten zum Bogen schieben)
      const reihe = sig.closest(".karten--reihe, .kacheln ul");
      if (reihe) reihe.style.scrollSnapType = "none";
      sig.scrollIntoView({ block: "center", inline: "center" });
      const q = sig.getBoundingClientRect();
      sig.style.pointerEvents = "auto";
      const oben = document.elementFromPoint(q.left + q.width * 0.5, q.top + q.height * 0.5);
      sig.style.pointerEvents = "";
      if (reihe) { reihe.style.scrollSnapType = ""; reihe.scrollLeft = 0; }
      if (oben !== sig) { fehler(`verdeckt von ${oben ? kennung(oben) : "nichts"}`); continue; }
      signetOk++;
    }
    // Titel im Bild: jeder Beitrags-Anreißer mit Bild, Ausnahmen mit Namen
    const ausnahmen = {};
    const kartenFehler = [];
    let kartenSoll = 0, kartenOk = 0;
    for (const el of einzeln.filter((x) => geladen(x))) {
      const art = AUSNAHMEN_KARTE.find(([, s]) => el.matches(s) || el.closest(s));
      if (art) { ausnahmen[art[0]] = (ausnahmen[art[0]] || 0) + 1; continue; }
      kartenSoll++;
      const titel = el.querySelector(".rahmen > .imbild .titel");
      const r = titel && titel.getBoundingClientRect();
      const rahmen = titel && titel.closest(".rahmen").getBoundingClientRect();
      if (titel && r.height > 0 && r.top >= rahmen.top - 1 && r.bottom <= rahmen.bottom + 1) kartenOk++;
      else kartenFehler.push({ element: kennung(el), text: kurz(el), grund: titel ? "Titel ragt aus dem Bild" : "Titel nicht im Bild (Zeile statt Karte)" });
    }
    // doppelte Kartenbilder: dasselbe Bild (ohne Größenzusatz) an mehr als einer Beitragskarte; Ausnahmen (Rubrikkacheln,
    // Kinotabelle, Verzeichnis, Leerzustände, Artikelbild) zählen nicht
    const bildname = (img) => (img.currentSrc || img.src).split("?")[0].split("/").pop().replace(/-(\d+x\d+|320|480)(?=\.\w+$)/, "");
    const zaehler = {};
    for (const el of einzeln.filter((x) => geladen(x) && !AUSNAHMEN_KARTE.some(([, s]) => x.matches(s) || x.closest(s)))) {
      const img = [...el.querySelectorAll("img")].find((i) => i.complete && i.naturalWidth > 0);
      if (img) (zaehler[bildname(img)] = zaehler[bildname(img)] || []).push(kurz(el));
    }
    const doppelt = Object.entries(zaehler).filter(([, v]) => v.length > 1).map(([bild, karten]) => ({ bild, karten }));
    return { doppelt, anreisser: einzeln.length, fehlend, werbung: werbung.length, werbungOhne, signetSoll: mitBild.length, signetOk, signetFehler, kartenSoll, kartenOk, kartenFehler, ausnahmen };
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
      const e = await pruefen(page, { ANREISSER, WERBUNG, AUSNAHMEN, OHNE_SIGNET, AUSNAHMEN_KARTE });
      fehler += e.fehlend.length + e.signetFehler.length + e.kartenFehler.length;
      bericht.push({ pfad, breite: w, status, ...e });
      const zeichen = e.fehlend.length || e.signetFehler.length || e.kartenFehler.length ? "FEHLER" : "ok    ";
      const aus = Object.entries(e.ausnahmen).map(([k, n]) => `${k} ${n}`).join(", ");
      console.log(`${zeichen} ${String(w).padStart(4)}  ${pfad}  ${e.anreisser} Anreißer, ${e.fehlend.length} ohne Bild` +
        `, Signet ${e.signetOk}/${e.signetSoll}, Titel im Bild ${e.kartenOk}/${e.kartenSoll}` + (aus ? ` (Ausnahmen: ${aus})` : "") +
        (e.werbung ? `, Werbung ${e.werbung} (${e.werbungOhne.length} ohne Bild)` : "") +
        (e.doppelt.length ? `, Hinweis: ${e.doppelt.length} Bild(er) doppelt` : ""));
      for (const d of e.doppelt) console.log(`          doppelt (Hinweis): ${d.bild}  ${d.karten.map((t) => "„" + t + "“").join(", ")}`);
      for (const f of e.fehlend) console.log(`          ohne Bild: ${f.element}  „${f.text}“`);
      for (const f of e.signetFehler) console.log(`          Signet: ${f.grund}  ${f.element}  „${f.text}“`);
      for (const f of e.kartenFehler) console.log(`          Karte: ${f.grund}  ${f.element}  „${f.text}“`);
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
  const ohne = bericht.reduce((s, b) => s + b.fehlend.length, 0);
  const soll = bericht.reduce((s, b) => s + (b.signetSoll || 0), 0);
  const ok = bericht.reduce((s, b) => s + (b.signetOk || 0), 0);
  const anteil = soll ? ((100 * ok) / soll).toFixed(1).replace(".", ",") : "–";
  const kSoll = bericht.reduce((s, b) => s + (b.kartenSoll || 0), 0);
  const kOk = bericht.reduce((s, b) => s + (b.kartenOk || 0), 0);
  const kAnteil = kSoll ? ((100 * kOk) / kSoll).toFixed(1).replace(".", ",") : "–";
  const aus = {};
  for (const b of bericht) for (const [k, v] of Object.entries(b.ausnahmen || {})) aus[k] = (aus[k] || 0) + v;
  console.log(`\n${bericht.length} Aufnahmen, ${n} Anreißer geprüft, ${ohne} ohne Bild; Signet an ${ok} von ${soll} Bildern (${anteil} %); ` +
    `Titel im Bild bei ${kOk} von ${kSoll} Beitrags-Anreißern (${kAnteil} %)` + (a.out ? ` → ${path.join(a.out, "bilder-pflicht.json")}` : ""));
  const dop = bericht.reduce((s, b) => s + ((b.doppelt || []).length), 0);
  const dopSeiten = bericht.filter((b) => (b.doppelt || []).length).length;
  console.log(`Hinweis (kein Fehler): doppelte Kartenbilder ${dop} in ${dopSeiten} von ${bericht.length} Aufnahmen`);
  if (Object.keys(aus).length) console.log("Ausnahmen (ohne Titel im Bild, gewollt): " + Object.entries(aus).map(([k, v]) => `${k} ${v}`).join(", "));
  process.exit(fehler ? 1 : 0);
}

main().catch((f) => { console.error(f); process.exit(2); });
