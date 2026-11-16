/* tamil.de – klar2, Bewegung beim Scrollen: Vorschau mit Umschalter (A, B, C, D, Aus). Ohne Bibliothek.
   Ablauf je Variante:
   1. Jede Einheit (Aufmacher, Kachel, Nebenstück, Meldung, Blocktitel …) bekommt data-art (steigen, aufdecken,
      zeilen, blenden, vorhang). Erst damit greifen die versteckenden Regeln in bewegung.css.
   2. Was beim Laden schon im Bild ist, steht sofort da: nichts startet von selbst, Bewegung nur als Antwort aufs Scrollen.
   3. Der Rest erscheint einmal, wenn er ins Bild kommt (IntersectionObserver, Klasse .da); was gemeinsam kommt, gestaffelt.
   Kopf, Leselinie und Aufmacher-Tiefe hängen am Scrollweg: per CSS-Scroll-Timeline, sonst über einen einzigen passiven
   Scroll-Handler mit requestAnimationFrame. Mit „Bewegung reduzieren“ passiert nichts davon. */
(() => {
  "use strict";

  const html = document.documentElement;
  const reduziert = matchMedia("(prefers-reduced-motion: reduce)");
  const kannIo = "IntersectionObserver" in window;
  const kannSda = !!(window.CSS && CSS.supports && CSS.supports("animation-timeline: scroll()"));

  const TAKT = 60;            // Staffel zwischen Stücken einer Reihe, die gemeinsam ins Bild kommen
  const STAFFEL_MAX = 6;      // höchstens 6 × 60 ms (sieben Rubrikkacheln: 0 bis 360 ms)
  const REIHE = 100;          // jede weitere Reihe im selben Moment 100 ms später
  const REIHEN_MAX = 3;       // höchstens 300 ms
  const REIHE_TOLERANZ = 24;  // gleiche Reihe: Oberkanten weniger als 24 px auseinander (versteckt sind manche 16 px tiefer)
  const NACH_VORHANG = 0.55;  // Inhalt der dunklen Fläche beginnt nach 55 % des Vorhangs
  const GRUPPE = ".kacheln";  // Rubrikkacheln erscheinen gemeinsam, auch die rechts angeschnittenen
  const TIEFE = 40;           // Aufmacherbild höchstens 40 px langsamer
  const BAND = 48;            // Höhe des stehenden Rubrikbands (Desktop), Beginn des Tiefenwegs

  const ALLE = ".aufmacher, .kacheln li, .neben .stueck, .block-titel, .meldung, .woche__titel, .woche .kachel, "
    + ".woche__art, .grafik, .kueche .kachel";

  const VARIANTEN = {
    a: {
      name: "A Einblenden",
      text: "Blöcke und Karten steigen beim Erscheinen 16 px auf, was nebeneinander steht, gestaffelt.",
      regeln: [[ALLE, "steigen"]],
    },
    b: {
      name: "B Aufdecken",
      text: "Bilder decken sich von unten auf, Überschriften steigen Zeile für Zeile.",
      regeln: [
        [".aufmacher, .neben .stueck, .meldung, .woche .kachel, .kueche .kachel, .grafik", "aufdecken zeilen"],
        [".kacheln li", "aufdecken"],
        [".block-titel, .woche__titel", "zeilen"],
        [".woche__art", "blenden"],
      ],
    },
    c: {
      name: "C Kopf & Bänder",
      text: "Der Kopf faltet sich ins Band, rote Leselinie, die dunkle Fläche zieht auf.",
      kopf: true,
      regeln: [
        [".woche", "vorhang"],
        [".woche__titel, .woche .kachel, .woche__art, .grafik", "steigen"],
      ],
    },
    d: {
      name: "D Kombination",
      text: "Empfehlung: Kopf und Fläche aus C, große Bilder und Blocktitel aus B, Listen aus A.",
      kopf: true,
      regeln: [
        [".kacheln li, .neben .stueck, .meldung, .woche .kachel--klein, .woche__art, .grafik, .kueche .kachel--klein", "steigen"],
        [".block-titel, .woche__titel", "zeilen"],
        [".woche", "vorhang"],
        [".kachel--gross", "aufdecken zeilen"],
      ],
    },
    aus: { name: "Aus", text: "Keine Bewegung beim Scrollen, so wie klar2.", regeln: [] },
  };

  let variante = ausHash() || "d";
  let lauf = 0;          // zählt Umschaltungen; ältere, noch wartende Schritte brechen ab
  let io = null;
  let vorhangAb = 0;     // Zeitpunkt, an dem der Vorhang beginnt
  let T = {};
  let breite = innerWidth;
  let kopf, band, aufRahmen, aufBild, text, knoepfe;
  const einheiten = new Set();
  const gruppen = new Map();   // .kacheln → ihre Kacheln
  const original = new Map();  // geteilte Überschrift → ursprüngliches HTML
  const uhren = new Set();

  function ausHash() {
    const h = decodeURIComponent(location.hash.slice(1)).toLowerCase();
    return Object.prototype.hasOwnProperty.call(VARIANTEN, h) ? h : null;
  }
  const aktiv = () => kannIo && !reduziert.matches && variante !== "aus";
  const warte = (ms) => new Promise((ok) => setTimeout(ok, ms));
  const klemme = (x) => Math.min(1, Math.max(0, x));
  const ueberschrift = (el) => (el.matches("h2, h3") ? el : el.querySelector(".titel"));

  function zeiten() {
    const s = getComputedStyle(html);
    const ms = (name, sonst) => {
      const v = parseFloat(s.getPropertyValue(name));
      return Number.isFinite(v) ? v : sonst;
    };
    return {
      steigen: ms("--t-steigen", 500), bild: ms("--t-bild", 650), zoom: ms("--t-zoom", 650),
      blenden: ms("--t-blenden", 450), zeile: ms("--t-zeile", 650), takt: ms("--zeilen-takt", 80),
      zeilenStart: ms("--zeilen-start", 140), vorhang: ms("--t-vorhang", 800),
    };
  }

  // Zeilenumbrüche hängen an der Webschrift: erst messen, wenn sie geladen ist (höchstens 1,2 s warten)
  function schriften() {
    if (!document.fonts) return Promise.resolve();
    return Promise.race([
      Promise.all([document.fonts.load('600 20px "Libre Franklin"'), document.fonts.ready]).catch(() => {}),
      warte(1200),
    ]);
  }

  /* Überschrift in ihre gemessenen Zeilen legen: <span class="zeile"><span class="zeile__in">…</span></span>.
     Der Text bleibt Text (gleiche Wörter, gleiche Leerzeichen, .zusammen bleibt ganz); nach dem Auftritt wird das
     ursprüngliche HTML zurückgesetzt. */
  function teile(h) {
    if (original.has(h)) return;
    const vorher = h.innerHTML;
    const stuecke = [];
    let raum = false;
    for (const n of [...h.childNodes]) {
      if (n.nodeType === Node.TEXT_NODE) {
        for (const t of n.nodeValue.split(/([ \t\n\r]+)/)) {
          if (!t) continue;
          if (/^[ \t\n\r]+$/.test(t)) { raum = true; continue; }
          const s = document.createElement("span");
          s.textContent = t;
          stuecke.push({ knoten: s, raum });
          raum = false;
        }
      } else if (n.nodeType === Node.ELEMENT_NODE) {
        stuecke.push({ knoten: n.cloneNode(true), raum });
        raum = false;
      }
    }
    if (!stuecke.length) return;
    h.replaceChildren(...stuecke.flatMap((s, i) => (i && s.raum ? [" ", s.knoten] : [s.knoten])));
    const zeilen = [];
    let oben = null;
    for (const s of stuecke) {
      const y = Math.round(s.knoten.getBoundingClientRect().top);
      if (oben === null || Math.abs(y - oben) > 4) { zeilen.push([]); oben = y; }
      zeilen[zeilen.length - 1].push(s);
    }
    h.replaceChildren(...zeilen.map((zeile, i) => {
      const aussen = document.createElement("span");
      const innen = document.createElement("span");
      aussen.className = "zeile";
      innen.className = "zeile__in";
      innen.style.setProperty("--zi", String(i));
      zeile.forEach((s, j) => { if (j && s.raum) innen.append(" "); innen.append(s.knoten); });
      aussen.append(innen);
      if (i < zeilen.length - 1) aussen.append(" ");
      return aussen;
    }));
    h.dataset.zeilen = String(zeilen.length);
    original.set(h, vorher);
  }

  function wiederher(h) {
    if (!original.has(h)) return;
    h.innerHTML = original.get(h);
    original.delete(h);
    delete h.dataset.zeilen;
  }

  function dauer(el) {
    const art = el.dataset.art || "";
    let t = 0;
    if (art.includes("steigen")) t = Math.max(t, T.steigen);
    if (art.includes("aufdecken")) t = Math.max(t, T.bild, T.zoom, 320 + T.blenden);
    if (art.includes("blenden")) t = Math.max(t, T.blenden);
    if (art.includes("vorhang")) t = Math.max(t, T.vorhang);
    if (art.includes("zeilen")) {
      const h = ueberschrift(el);
      const n = h ? Number(h.dataset.zeilen || 1) : 1;
      t = Math.max(t, (art === "zeilen" ? 0 : T.zeilenStart) + (n - 1) * T.takt + T.zeile);
    }
    return t;
  }

  // Bilder erst aufdecken, wenn sie da sind (höchstens 0,7 s warten)
  function bilderBereit(el) {
    const offen = [...el.querySelectorAll("img")].filter((i) => !i.complete);
    if (!offen.length) return Promise.resolve();
    return Promise.race([Promise.all(offen.map((i) => i.decode().catch(() => {}))), warte(700)]);
  }

  function zeige(el, verz, l, unterVorhang = false) {
    const art = el.dataset.art || "";
    const jetzt = performance.now();
    if (art.includes("vorhang")) vorhangAb = jetzt + verz;
    else if (unterVorhang && vorhangAb) verz += Math.max(0, vorhangAb + T.vorhang * NACH_VORHANG - jetzt);
    el.style.setProperty("--verz", Math.round(verz) + "ms");
    const los = () => {
      if (l !== lauf) return;
      el.classList.add("da", "laeuft");
      const uhr = setTimeout(() => {
        uhren.delete(uhr);
        el.classList.remove("laeuft");
        const h = art.includes("zeilen") && ueberschrift(el);
        if (h) wiederher(h);
      }, verz + dauer(el) + 80);
      uhren.add(uhr);
    };
    if (art.includes("aufdecken")) bilderBereit(el).then(los); else los();
  }

  function beobachtet(eintraege) {
    const l = lauf;
    const neu = [];
    for (const e of eintraege) {
      if (!e.isIntersecting) continue;
      io.unobserve(e.target);
      neu.push(...(gruppen.get(e.target) || [e.target]));
    }
    // Schon über dem Bild (schnell vorbeigescrollt): ohne Staffel. Im Bild: Lesereihenfolge, oben vor unten, links vor rechts.
    const lage = new Map(neu.map((el) => [el, el.getBoundingClientRect()]));
    const oben = neu.filter((el) => lage.get(el).bottom <= 0);
    const imBild = neu.filter((el) => lage.get(el).bottom > 0).sort((x, y) => {
      const a = lage.get(x), b = lage.get(y);
      return Math.abs(a.top - b.top) > REIHE_TOLERANZ ? a.top - b.top : a.left - b.left;
    });
    oben.forEach((el) => zeige(el, 0, l));
    // Staffel je Reihe: 60 ms von links nach rechts, jede weitere Reihe 100 ms später.
    // Inhalt unter einem Vorhang zählt eigene Reihen, gerechnet ab dem Vorhang.
    const unter = (el) => !el.matches('[data-art~="vorhang"]') && !!el.closest('[data-art~="vorhang"]');
    for (const teil of [imBild.filter((el) => !unter(el)), imBild.filter(unter)]) {
      let reihe = -1, spalte = 0, oberkante = null;
      for (const el of teil) {
        const top = lage.get(el).top;
        if (oberkante === null || Math.abs(top - oberkante) > REIHE_TOLERANZ) { reihe++; spalte = 0; oberkante = top; }
        const verz = Math.min(reihe, REIHEN_MAX) * REIHE + Math.min(spalte++, STAFFEL_MAX) * TAKT;
        zeige(el, verz, l, unter(el));
      }
    }
  }

  function beobachte() {
    // Auslöselinie 10 % über der Unterkante. Nach oben reicht der Rahmen weit über die Seite hinaus: Was oberhalb der Linie
    // liegt, gilt als erreicht, auch wenn es beim schnellen Scrollen nie im Bild war.
    io = new IntersectionObserver(beobachtet, { rootMargin: "100000px 0px -10% 0px", threshold: 0 });
    for (const el of einheiten) {
      if (el.classList.contains("da")) continue;
      const g = el.closest(GRUPPE);
      if (g) {
        if (!gruppen.has(g)) { gruppen.set(g, []); io.observe(g); }
        gruppen.get(g).push(el);
      } else {
        io.observe(el);
      }
    }
  }

  async function scharf() {
    const l = lauf;
    if (!aktiv()) { html.classList.remove("zuruecksetzen"); return; }
    await schriften();
    if (l !== lauf) return;
    html.classList.add("zuruecksetzen");
    T = zeiten();
    for (const [sel, art] of VARIANTEN[variante].regeln) {
      for (const el of document.querySelectorAll(sel)) {
        el.dataset.art = ((el.dataset.art || "") + " " + art).trim();
        einheiten.add(el);
      }
    }
    // Was schon im Bild (oder darüber) ist, steht sofort da
    const hoch = innerHeight;
    for (const el of einheiten) if (el.getBoundingClientRect().top < hoch) el.classList.add("da");
    for (const el of einheiten) {
      if (el.classList.contains("da") || !el.dataset.art.includes("zeilen")) continue;
      const h = ueberschrift(el);
      if (h) teile(h);
    }
    void html.offsetHeight;
    requestAnimationFrame(() => {
      if (l !== lauf) return;
      html.classList.remove("zuruecksetzen");
      beobachte();
    });
  }

  function entschaerfe() {
    html.classList.add("zuruecksetzen");
    if (io) io.disconnect();
    io = null;
    gruppen.clear();
    uhren.forEach(clearTimeout);
    uhren.clear();
    for (const h of [...original.keys()]) wiederher(h);
    for (const el of einheiten) {
      el.classList.remove("da", "laeuft");
      el.removeAttribute("data-art");
      el.style.removeProperty("--verz");
      if (!el.getAttribute("style")) el.removeAttribute("style");
    }
    einheiten.clear();
    vorhangAb = 0;
    if (kopf) kopf.style.removeProperty("--kopf");
    if (band) band.style.removeProperty("--fortschritt");
    if (aufBild) aufBild.style.removeProperty("--tiefe");
  }

  function wechsle(v) {
    lauf++;
    variante = v;
    entschaerfe();
    html.dataset.bewegung = v;
    html.classList.toggle("bewegt", aktiv());
    zeigeWahl();
    scrollTo({ top: 0, left: 0, behavior: "instant" });
    rechne();
    scharf().catch(notfall);
  }

  // Ersatzweg ohne Scroll-Timelines: ein passiver Handler, gedrosselt auf ein Bild (rAF)
  let geplant = false;
  function aufScroll() {
    if (!geplant) { geplant = true; requestAnimationFrame(rechne); }
  }
  function rechne() {
    geplant = false;
    if (kannSda || !aktiv() || !VARIANTEN[variante].kopf || !kopf) return;
    const y = scrollY;
    kopf.style.setProperty("--kopf", klemme(y / kopf.offsetHeight).toFixed(4));
    const weg = html.scrollHeight - innerHeight;
    band.style.setProperty("--fortschritt", (weg > 0 ? klemme(y / weg) : 0).toFixed(4));
    if (aufRahmen && aufBild) {
      const r = aufRahmen.getBoundingClientRect();
      aufBild.style.setProperty("--tiefe", (klemme((BAND - r.top) / r.height) * TIEFE).toFixed(1) + "px");
    }
  }

  // Neue Breite: noch nicht gezeigte Überschriften neu in Zeilen legen
  let breitenUhr = 0;
  function neueBreite() {
    clearTimeout(breitenUhr);
    breitenUhr = setTimeout(() => {
      if (innerWidth === breite) return;
      breite = innerWidth;
      for (const h of [...original.keys()]) {
        const einheit = h.closest("[data-art]");
        if (einheit && !einheit.classList.contains("da")) { wiederher(h); teile(h); }
      }
    }, 200);
  }

  // Sprünge auf der Seite (#diese-woche, #kueche) ohne Hash, damit die Adresse die Variante behält
  function sprung(e) {
    const a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const id = a.getAttribute("href").slice(1);
    if (Object.prototype.hasOwnProperty.call(VARIANTEN, id)) return;
    e.preventDefault();
    const ziel = id && document.getElementById(id);
    if (!ziel) return;
    ziel.scrollIntoView({ behavior: aktiv() ? "smooth" : "auto", block: "start" });
    if (!ziel.hasAttribute("tabindex")) ziel.setAttribute("tabindex", "-1");
    ziel.focus({ preventScroll: true });
  }

  function zeigeWahl() {
    for (const b of knoepfe) b.setAttribute("aria-pressed", String(b.dataset.variante === variante));
    const v = VARIANTEN[variante];
    const name = document.createElement("strong");
    name.textContent = v.name + ". ";
    text.replaceChildren(name, reduziert.matches ? "Bewegung reduziert (Systemeinstellung)." : v.text);
  }

  function notfall(f) {
    lauf++;
    html.classList.remove("bewegt", "zuruecksetzen");
    console.error("Bewegung abgeschaltet:", f);
  }

  function start() {
    try {
      if ("scrollRestoration" in history) history.scrollRestoration = "manual";
      kopf = document.querySelector(".kopf");
      band = document.querySelector(".band");
      aufRahmen = document.querySelector(".aufmacher .rahmen");
      aufBild = aufRahmen && aufRahmen.querySelector("img");
      const wahl = document.getElementById("wahl");
      text = document.getElementById("wahl-text");
      knoepfe = [...wahl.querySelectorAll("button[data-variante]")];

      if (!ausHash()) history.replaceState(null, "", "#" + variante);
      if (kannSda) html.classList.add("sda");
      html.dataset.bewegung = variante;
      html.classList.toggle("bewegt", aktiv());

      wahl.hidden = false;
      html.classList.add("mit-wahl");
      const miss = () => html.style.setProperty("--wahl-hoehe", wahl.offsetHeight + "px");
      miss();
      if ("ResizeObserver" in window) new ResizeObserver(miss).observe(wahl);
      zeigeWahl();

      wahl.addEventListener("click", (e) => {
        const b = e.target.closest("button[data-variante]");
        if (!b) return;
        const v = b.dataset.variante;
        if (ausHash() === v) wechsle(v); // noch einmal tippen spielt die Variante von vorn
        else location.hash = v;
      });
      addEventListener("hashchange", () => { const v = ausHash(); if (v) wechsle(v); });
      reduziert.addEventListener("change", () => wechsle(variante));
      document.addEventListener("click", sprung);
      addEventListener("resize", neueBreite, { passive: true });
      if (!kannSda) {
        addEventListener("scroll", aufScroll, { passive: true });
        addEventListener("resize", aufScroll, { passive: true });
      }
      rechne();
      scharf().catch(notfall);
    } catch (f) {
      notfall(f);
    }
  }

  start();
})();
