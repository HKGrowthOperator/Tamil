// Sichtbarer erster Bildschirm je Probe und Kennzahlen gegen die harten Kriterien des Briefs.
// Anders als die Kacheln aus tools/shots.mjs (Ausschnitte der ganzen Seite) nimmt dieses Skript nur den sichtbaren
// Bereich auf. Fest stehende Leisten sitzen dadurch dort, wo man sie am Gerät wirklich sieht.
//
//   node design/vergleich/aufnahmen.mjs klar blatt bild
//
// Ergebnis je Probe:
//   design/vergleich/img/<slug>-start-handy.jpg, -start-handy-2.jpg, -start-handy-3.jpg, -start-desktop.jpg,
//     -woche-handy.jpg und -woche-desktop.jpg (Bereich #diese-woche, falls da), -kueche-desktop.jpg (#kueche, falls da),
//     -artikel-handy.jpg (falls da)
//   design/vergleich/kennzahlen/<slug>.json  (Schlagzeilen, Kopfhöhe, größte Schrift, Rotanteil, Radius, Schatten,
//     Anreißer ohne Bild, dunkle Flächen, Bewegung, Kontrast heller Schrift auf Bild oder dunklem Grund …)
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const { chromium } = createRequire(import.meta.url)('playwright');

const hier = dirname(fileURLToPath(import.meta.url));
const wurzel = resolve(hier, '..', '..');
const ziel = resolve(hier, 'img');
const zahlen = resolve(hier, 'kennzahlen');
mkdirSync(ziel, { recursive: true });
mkdirSync(zahlen, { recursive: true });

const ANSICHTEN = [
  { name: 'start-handy', seite: 'index.html', breite: 390, hoehe: 844, messen: 'handy' },
  { name: 'start-handy-2', seite: 'index.html', breite: 390, hoehe: 844, scroll: 844 },
  { name: 'start-handy-3', seite: 'index.html', breite: 390, hoehe: 844, scroll: 1688 },
  { name: 'woche-handy', seite: 'index.html', breite: 390, hoehe: 844, anker: '#diese-woche' },
  { name: 'start-desktop', seite: 'index.html', breite: 1280, hoehe: 800, messen: 'desktop' },
  { name: 'woche-desktop', seite: 'index.html', breite: 1280, hoehe: 800, anker: '#diese-woche' },
  { name: 'kueche-desktop', seite: 'index.html', breite: 1280, hoehe: 800, anker: '#kueche' },
  { name: 'artikel-handy', seite: 'artikel.html', breite: 390, hoehe: 844 },
];

// Läuft im Browser: misst, was im sichtbaren ersten Bildschirm steht, und einige Dinge auf der ganzen Seite.
function messen() {
  const vh = window.innerHeight;
  const sichtbar = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) > 0.05 && r.width > 0 && r.height > 0;
  };
  const ganzImBild = (el) => {
    const r = el.getBoundingClientRect();
    return r.top >= 0 && r.bottom <= vh && r.left >= 0 && r.right <= window.innerWidth + 1;
  };
  const name = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : '');
  // Farben stehen je nach Schreibweise als rgb(), oklch() oder color() im Stil; die Zeichenfläche rechnet sie um.
  const flaeche = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
  const farbwerte = new Map();
  const rgba = (farbe) => {
    if (!farbwerte.has(farbe)) {
      flaeche.clearRect(0, 0, 1, 1);
      flaeche.fillStyle = farbe;
      flaeche.fillRect(0, 0, 1, 1);
      farbwerte.set(farbe, [...flaeche.getImageData(0, 0, 1, 1).data]);
    }
    return farbwerte.get(farbe);
  };
  const istRot = (farbe) => { const [r, g, b] = rgba(farbe); return r > 120 && r > g * 1.6 && r > b * 1.6; };
  const hell = (farbe) => {
    const k = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
    const [r, g, b] = rgba(farbe);
    return 0.2126 * k(r) + 0.7152 * k(g) + 0.0722 * k(b);
  };
  const kopfzeilen = [...document.querySelectorAll('h1, h2, h3')].filter(sichtbar);
  const schlagzeilen = kopfzeilen.filter((h) => h.closest('a') || h.querySelector('a'));
  const erste = schlagzeilen.map((h) => h.getBoundingClientRect().top).sort((a, b) => a - b)[0];
  const zeilen = (el) => Math.round(el.getBoundingClientRect().height / parseFloat(getComputedStyle(el).lineHeight || '0') || 0);

  let groesste = { px: 0, text: '' };
  let groessteRot = { px: 0, text: '' };
  let versalGross = 0;
  const familien = new Set();
  const groessen = new Map();
  const helleTexte = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let k = walker.nextNode(); k; k = walker.nextNode()) {
    const text = k.textContent.trim();
    const el = k.parentElement;
    if (!text || !el || !sichtbar(el)) continue;
    const s = getComputedStyle(el);
    const px = parseFloat(s.fontSize);
    familien.add(s.fontFamily.split(',')[0].replace(/["']/g, '').trim());
    const r = el.getBoundingClientRect();
    const eintrag = groessen.get(px) || { px, anzahl: 0, text: text.slice(0, 40) };
    eintrag.anzahl += 1;
    groessen.set(px, eintrag);
    // Helle Schrift steht auf einem Bild oder einer dunklen Fläche: Lage merken, der Kontrast wird am Foto gemessen.
    const leuchtet = hell(s.color);
    if (leuchtet > 0.4) {
      const bereich = document.createRange();
      bereich.selectNodeContents(k);
      const b = bereich.getBoundingClientRect();
      if (b.width > 0 && b.height > 0) {
        helleTexte.push({ x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, hell: Math.round(leuchtet * 1000) / 1000, px, fett: Number(s.fontWeight) >= 600, text: text.slice(0, 40) });
      }
    }
    if (r.top >= vh || r.bottom <= 0) continue;
    if (px > groesste.px) groesste = { px, text: text.slice(0, 40) };
    if (istRot(s.color) && px > groessteRot.px) groessteRot = { px, text: text.slice(0, 40) };
    if (s.textTransform === 'uppercase' && px > 14) versalGross += 1;
  }

  let radius = { px: 0, element: '' };
  let schatten = 0;
  let gedreht = 0;
  let breiteVerstellt = 0;
  let uebergaenge = 0;
  let laengsterUebergang = 0;
  let animationen = 0;
  let endlos = 0;
  const dunkle = [];
  const fest = [];
  const festOben = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!sichtbar(el)) continue;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const rad = Math.min(parseFloat(s.borderTopLeftRadius) || 0, Math.min(r.width, r.height) / 2);
    if (rad > radius.px) radius = { px: Math.round(rad * 10) / 10, element: name(el) };
    if (s.boxShadow && s.boxShadow !== 'none') {
      // Nur weiche Schatten zählen; Linien, die als Schatten ohne Unschärfe gebaut sind, gelten nicht.
      const px = [...s.boxShadow.matchAll(/(-?[\d.]+)px/g)].map((m) => Number(m[1]));
      if (px.some((wert, i) => i % 4 === 2 && wert > 0)) schatten += 1;
    }
    if (s.transform && s.transform !== 'none') {
      const m = s.transform.match(/matrix\(([^)]+)\)/);
      if (m) { const [, b, c] = m[1].split(',').map(Number); if (Math.abs(b) > 0.001 || Math.abs(c) > 0.001) gedreht += 1; }
    }
    if (s.rotate && s.rotate !== 'none' && parseFloat(s.rotate) !== 0) gedreht += 1;
    if (s.fontStretch && !['100%', 'normal'].includes(s.fontStretch)) breiteVerstellt += 1;
    const dauer = Math.max(0, ...s.transitionDuration.split(',').map((d) => parseFloat(d) * (d.trim().endsWith('ms') ? 0.001 : 1)));
    if (dauer > 0.011) { uebergaenge += 1; laengsterUebergang = Math.max(laengsterUebergang, dauer); }
    if (s.animationName && s.animationName !== 'none') { animationen += 1; if (s.animationIterationCount.includes('infinite')) endlos += 1; }
    // Dunkle Flächen: deckende dunkle Hintergrundfarbe, nicht in einer anderen dunklen Fläche. Verläufe über Bildern
    // sind Hintergrundbilder und zählen hier nicht.
    const [, , , alpha] = rgba(s.backgroundColor);
    if (alpha > 200 && hell(s.backgroundColor) < 0.06 && r.width * r.height > 4000 && !dunkle.some((d) => d.el.contains(el))) {
      dunkle.push({ el, element: name(el), breite: Math.round(r.width), hoehe: Math.round(r.height), oben: Math.round(r.top + scrollY) });
    }
    if (s.position === 'sticky' || s.position === 'fixed') {
      fest.push({ element: name(el), art: s.position, hoehe: Math.round(r.height) });
      // Ein Rubrikband, das stehen bleibt, liegt oft hinter dem <header>; es gehört trotzdem zum Kopf.
      if (r.top + scrollY < 200) festOben.push(r.bottom + scrollY);
    }
  }
  const bilder = [...document.images].filter((b) => sichtbar(b) && b.naturalWidth);
  const zeile = (b) => `${b.getAttribute('src')} (${Math.round(b.getBoundingClientRect().width)} px gezeigt, ${b.naturalWidth} px vorhanden)`;
  // Anreißer: der Behälter (<article> oder <li>) jeder verlinkten Schlagzeile. Ohne Bild heißt: weder <img> noch als gestaltete Grafik
  // gekennzeichnet (data-grafik am Anreißer oder darin; für Einträge aus dem Radar, die kein Foto haben).
  const behaelter = (h) => h.closest('article, li') || (h.closest('a') || h).parentElement;
  const anreisser = [...new Set(schlagzeilen.map(behaelter))];
  const titel = (a) => (a.querySelector('h2, h3')?.textContent || '').trim().slice(0, 50);
  const hatFoto = (a) => [...a.querySelectorAll('img')].some(sichtbar);
  const hatGrafik = (a) => a.matches('[data-grafik]') || !!a.querySelector('[data-grafik]');
  const kopf = document.querySelector('header');
  return {
    kopfleiste_hoehe: kopf ? Math.round(Math.max(kopf.getBoundingClientRect().bottom, ...festOben)) : null,
    erste_schlagzeile_ab: erste === undefined ? null : Math.round(erste),
    schlagzeilen_ganz_sichtbar: schlagzeilen.filter(ganzImBild).length,
    schlagzeilen_seite: schlagzeilen.length,
    max_zeilen_schlagzeile: Math.max(0, ...schlagzeilen.map(zeilen)),
    groesste_schrift: groesste,
    groesste_rote_schrift: groessteRot,
    schriftgroessen_seite: [...groessen.values()].sort((a, b) => b.px - a.px).slice(0, 6),
    versalien_ueber_14px: versalGross,
    schriftfamilien: [...familien],
    groesster_radius: radius,
    schatten,
    gedreht,
    schriftbreite_verstellt: breiteVerstellt,
    bilder_ueber_natuerlicher_breite: bilder.filter((b) => b.getBoundingClientRect().width * 2 > b.naturalWidth + 2).map(zeile),
    bilder_ueber_dateibreite: bilder.filter((b) => b.getBoundingClientRect().width > b.naturalWidth + 1).map(zeile),
    anreisser: anreisser.length,
    anreisser_ohne_bild: anreisser.filter((a) => !hatFoto(a) && !hatGrafik(a)).map(titel),
    anreisser_mit_grafik: anreisser.filter((a) => !hatFoto(a) && hatGrafik(a)).map(titel),
    dunkle_flaechen: dunkle.map(({ el, ...rest }) => rest),
    fest_stehend: fest,
    bewegung: { uebergaenge, laengster_uebergang_s: Math.round(laengsterUebergang * 100) / 100, animationen, endlos },
    helle_texte: helleTexte,
    seitenhoehe: document.documentElement.scrollHeight,
    ueberlauf: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  };
}

// Größter Maßstab in den Stilen der Probe (Zoom beim Überfahren). Aus der Datei gelesen, weil der Browser Stilregeln
// lokaler Dateien nicht herausgibt.
function groessterMassstab(ordner) {
  let max = 1;
  for (const datei of ['index.html', 'artikel.html']) {
    const pfad = resolve(ordner, datei);
    if (!existsSync(pfad)) continue;
    const text = readFileSync(pfad, 'utf-8');
    const stile = [text, ...[...text.matchAll(/<link[^>]+href="([^"]+\.css)"/g)].map((m) => resolve(ordner, m[1])).filter(existsSync).map((p) => readFileSync(p, 'utf-8'))];
    for (const stil of stile) {
      for (const m of stil.matchAll(/scale(?:3d)?\(\s*([\d.]+)|(?:^|[;{\s])scale\s*:\s*([\d.]+)/g)) max = Math.max(max, Number(m[1] || m[2]));
    }
  }
  return max;
}

const slugs = process.argv.slice(2);
if (!slugs.length) {
  console.error('Aufruf: node design/vergleich/aufnahmen.mjs <slug> [<slug> …]');
  process.exit(2);
}

const browser = await chromium.launch();
let fehler = 0;
for (const slug of slugs) {
  const ordner = resolve(wurzel, 'design', 'richtungen', slug);
  const ergebnis = { slug, stand: new Date().toISOString().slice(0, 16), groesster_massstab: groessterMassstab(ordner) };
  for (const a of ANSICHTEN) {
    const datei = resolve(ordner, a.seite);
    if (!existsSync(datei)) continue;
    const oeffnen = async (bewegung) => {
      const kontext = await browser.newContext({ viewport: { width: a.breite, height: a.hoehe }, deviceScaleFactor: 2, reducedMotion: bewegung });
      const seite = await kontext.newPage();
      const meldungen = [];
      seite.on('pageerror', (e) => meldungen.push(String(e)));
      await seite.goto(pathToFileURL(datei).href, { waitUntil: 'load' });
      await seite.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all([...document.images].map((b) => (b.complete ? null : b.decode().catch(() => null))));
      });
      return { kontext, seite, meldungen };
    };
    const { kontext, seite, meldungen } = await oeffnen('reduce');
    if (a.anker) {
      const da = await seite.evaluate((sel) => {
        const el = document.querySelector(sel);
        if (!el) return false;
        const festHoch = Math.max(0, ...[...document.querySelectorAll('body *')].filter((e) => ['sticky', 'fixed'].includes(getComputedStyle(e).position)).map((e) => e.getBoundingClientRect().height));
        window.scrollTo(0, el.getBoundingClientRect().top + scrollY - festHoch - 12);
        return true;
      }, a.anker);
      if (!da) { await kontext.close(); continue; }
    }
    if (a.scroll) {
      const hoch = await seite.evaluate(() => document.documentElement.scrollHeight);
      if (a.scroll >= hoch - 100) { await kontext.close(); continue; }
      await seite.evaluate((y) => window.scrollTo(0, y), a.scroll);
    }
    await seite.waitForTimeout(150);
    await seite.screenshot({ path: resolve(ziel, `${slug}-${a.name}.jpg`), type: 'jpeg', quality: 88 });
    if (a.messen) {
      const m = await seite.evaluate(messen);
      // Bei „Bewegung reduzieren“ darf nichts mehr übergehen oder laufen.
      m.bewegung_bei_reduziert = m.bewegung;
      const frei = await oeffnen('no-preference');
      m.bewegung = (await frei.seite.evaluate(messen)).bewegung;
      await frei.kontext.close();
      // Kontrast heller Schrift: ganze Seite ohne Schrift aufnehmen und unter jeder hellen Zeile die hellste Stelle messen.
      const texte = m.helle_texte;
      delete m.helle_texte;
      if (texte.length) {
        const ohneSchrift = await seite.addStyleTag({ content: '* { color: transparent !important; -webkit-text-fill-color: transparent !important; text-shadow: none !important; text-decoration-color: transparent !important }' });
        const foto = resolve(zahlen, `.${slug}-${a.messen}-ohne-schrift.png`);
        const liste = resolve(zahlen, `.${slug}-${a.messen}-texte.json`);
        await seite.evaluate(() => window.scrollTo(0, 0));
        await seite.screenshot({ path: foto, type: 'png', fullPage: true });
        writeFileSync(liste, JSON.stringify(texte));
        const kontraste = JSON.parse(execFileSync('python3', [resolve(hier, 'kontrast.py'), foto, liste, '2'], { encoding: 'utf-8' }));
        rmSync(foto);
        rmSync(liste);
        await ohneSchrift.evaluate((n) => n.remove());
        m.helle_schrift = { anzahl: kontraste.length, kleinster_kontrast: kontraste.length ? kontraste[0].verhaeltnis : null, unter_4_5: kontraste.filter((k) => k.verhaeltnis < 4.5) };
      } else {
        m.helle_schrift = { anzahl: 0, kleinster_kontrast: null, unter_4_5: [] };
      }
      await seite.addStyleTag({ content: 'img, picture, video, svg { visibility: hidden !important } * { background-image: none !important }' });
      const ohne = resolve(zahlen, `.${slug}-${a.messen}.png`);
      await seite.screenshot({ path: ohne, type: 'png' });
      m.farbanteil_ohne_bilder = JSON.parse(execFileSync('python3', [resolve(hier, 'farbanteil.py'), ohne], { encoding: 'utf-8' }));
      rmSync(ohne);
      m.seitenfehler = meldungen;
      ergebnis[a.messen] = m;
      if (m.ueberlauf > 0 || meldungen.length) fehler += 1;
      console.log(`${slug} ${a.messen}: Schlagzeilen ganz sichtbar ${m.schlagzeilen_ganz_sichtbar}, Kopf ${m.kopfleiste_hoehe} px, erste Schlagzeile ab ${m.erste_schlagzeile_ab} px, größte Schrift ${m.groesste_schrift.px} px, ` +
        `größte rote ${m.groesste_rote_schrift.px} px, Rot ${(m.farbanteil_ohne_bilder.rot * 100).toFixed(1)} %, dunkel ${(m.farbanteil_ohne_bilder.dunkel * 100).toFixed(1)} %, Radius ${m.groesster_radius.px} px, Schatten ${m.schatten}, ` +
        `gedreht ${m.gedreht}, Überlauf ${m.ueberlauf} px, Anreißer ${m.anreisser} (ohne Bild ${m.anreisser_ohne_bild.length}, Grafik ${m.anreisser_mit_grafik.length}), ` +
        `dunkle Flächen ${m.dunkle_flaechen.length}, helle Schrift kleinster Kontrast ${m.helle_schrift.kleinster_kontrast ?? '–'}, ` +
        `Übergänge ${m.bewegung.uebergaenge} (längster ${m.bewegung.laengster_uebergang_s} s, bei „reduziert“ ${m.bewegung_bei_reduziert.uebergaenge}), Animationen ${m.bewegung.animationen}`);
    }
    await kontext.close();
  }
  console.log(`${slug}: größter Maßstab in den Stilen ${ergebnis.groesster_massstab}`);
  writeFileSync(resolve(zahlen, `${slug}.json`), JSON.stringify(ergebnis, null, 2) + '\n');
}
await browser.close();
process.exit(fehler ? 1 : 0);
