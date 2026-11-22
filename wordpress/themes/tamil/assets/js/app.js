/* Tamil.de Theme – Menü „Mehr“, mobiler Werbeplatz, Filter im Kalender, Videos, Link kopieren, TV-Player, Zutaten
   abhaken und die Bewegung beim Scrollen (Variante D). Kein Framework. */
(function () {
  "use strict";
  var $ = function (s, root) { return (root || document).querySelector(s); };
  var $$ = function (s, root) { return Array.prototype.slice.call((root || document).querySelectorAll(s)); };
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Menü „Mehr“ (details): mit Escape, Klick daneben und wenn der Fokus das Menü verlässt schließen (am Handy
  // verdeckt das offene Menü sonst den Aufmacher, WCAG 2.4.11); ohne Skript öffnet und schließt es trotzdem
  var menue = $(".band .mehr");
  if (menue) {
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menue.open) { menue.open = false; var s = $("summary", menue); s && s.focus(); }
    });
    document.addEventListener("click", function (e) { if (menue.open && !menue.contains(e.target)) menue.open = false; });
    menue.addEventListener("focusout", function (e) {
      if (menue.open && e.relatedTarget && !menue.contains(e.relatedTarget)) menue.open = false;
    });
  }

  // Rubrikband am Handy und Tablet: die aktive Rubrik beim Laden in die Mitte holen (nur der Streifen scrollt, nie die
  // Seite) und einen Verlauf am rechten Rand zeigen, solange rechts noch Rubriken folgen
  var streifen = $(".band__liste");
  if (streifen) {
    var aktiv = $("a[aria-current]", streifen);
    if (aktiv && streifen.scrollWidth > streifen.clientWidth) {
      var abstand = aktiv.getBoundingClientRect().left - streifen.getBoundingClientRect().left;
      streifen.scrollLeft += abstand - (streifen.clientWidth - aktiv.offsetWidth) / 2;
    }
    var rand = function () {
      streifen.classList.toggle("mehr-rechts", streifen.scrollLeft + streifen.clientWidth < streifen.scrollWidth - 2);
      streifen.classList.toggle("mehr-links", streifen.scrollLeft > 2);
    };
    rand();
    streifen.addEventListener("scroll", rand, { passive: true });
    window.addEventListener("resize", rand);
  }

  // Logo im stehenden Band: sobald der Kopf mit dem großen Logo aus dem Bild ist, zeigt das Band links das Logo
  var band = $(".band"), kopf = $(".kopf");
  if (band && kopf && "IntersectionObserver" in window) {
    new IntersectionObserver(function (eintraege) {
      var e = eintraege[0];
      band.classList.toggle("band--steht", !e.isIntersecting && e.boundingClientRect.top < 0);
    }).observe(kopf);
  }

  // Rubrikkacheln und wischbare Kartenreihen laden „lazy“; am Handy laufen sie seitlich, dort lädt der Browser Bilder
  // außerhalb des Streifens sonst erst beim Wischen: kommt der Streifen in die Nähe, laden alle auf einmal (Kartenreihen
  // erst kurz vor dem Bild, damit sie dem ersten Bildschirm nichts wegnehmen)
  if ("IntersectionObserver" in window) {
    [[".kacheln", "800px 0px"], [".karten--reihe", "200px 0px"]].forEach(function (art) {
      $$(art[0]).forEach(function (k) {
        new IntersectionObserver(function (e, beob) {
          if (!e[0].isIntersecting) return;
          $$("img[loading=lazy]", k).forEach(function (i) {
            // „sizes=auto“ gilt nur für lazy-Bilder. Fiele es beim Umschalten weg, wählte der Browser ein größeres
            // Bild und bräche das schon laufende kleine ab. Darum die gerenderte Breite fest eintragen.
            var breite = Math.ceil(i.getBoundingClientRect().width);
            if (breite > 0 && /^\s*auto\b/i.test(i.getAttribute("sizes") || "")) { i.sizes = breite + "px"; }
            i.loading = "eager";
          });
          beob.disconnect();
        }, { rootMargin: art[1] }).observe(k);
      });
    });
  }

  // Handy-Leiste (Werbeplatz „mobile“ des Plugins, aside#ad-mobile; genau eine je Seite): erst einblenden, wenn der
  // erste Abschnitt aus dem Bild unter dem Rubrikband verschwunden ist – der Aufmacher, sonst der erste Block in main –,
  // spätestens nach einem Bildschirm. Früher hing das am ersten main > section/header/article: Im Artikel ist das der
  // ganze Beitrag (am Handy über 4000 px), auf der Startseite „Diese Woche“ weit unten; die Leiste kam dort erst am Ende.
  // Gemessen beim Scrollen (ein Mal je Bild), nach dem Einblenden hört das auf. Schließen blendet sie für die Seite aus.
  var sticky = $("#ad-mobile");
  if (sticky) {
    var hauptteil = $("main");
    var erster = $("main .aufmacher") || (hauptteil && Array.prototype.filter.call(hauptteil.children, function (el) { return el.offsetHeight > 40; })[0]);
    var leiste = $(".band");
    var geplant = false;
    var pruefe = function () {
      geplant = false;
      var kante = leiste ? leiste.getBoundingClientRect().bottom : 0;
      var weg = erster ? erster.getBoundingClientRect().bottom <= kante : false;
      if (!weg && window.scrollY < window.innerHeight) return;
      sticky.classList.add("ist-sichtbar");
      window.removeEventListener("scroll", plane);
      window.removeEventListener("resize", plane);
    };
    var plane = function () { if (!geplant) { geplant = true; requestAnimationFrame(pruefe); } };
    window.addEventListener("scroll", plane, { passive: true });
    window.addEventListener("resize", plane, { passive: true });
    pruefe();
    var zu = $(".schliessen", sticky);
    zu && zu.addEventListener("click", function () { sticky.hidden = true; var site = $(".site"); site && site.classList.remove("has-sticky-ad"); });
  }

  // Filter im Kalender (Land, Stadt): Knöpfe mit aria-pressed, erst mit Skript sichtbar; ohne Skript steht die ganze
  // Liste da. Monate ohne passende Termine verschwinden, die Zahl oben wird mitgezählt (aria-live).
  $$("[data-filter]").forEach(function (block) {
    var leiste = $(".filter", block); if (!leiste) return;
    var wahl = { land: "", stadt: "" };
    var zeilen = $$("li[data-land]", block);
    var zahl = $("[data-filter-zahl]", block), leer = $("[data-filter-leer]", block);
    leiste.hidden = false;
    leiste.addEventListener("click", function (e) {
      var knopf = e.target.closest(".chip"); if (!knopf) return;
      var gruppe = knopf.closest("[data-filter-art]"); if (!gruppe) return;
      wahl[gruppe.getAttribute("data-filter-art")] = knopf.getAttribute("data-wert") || "";
      $$(".chip", gruppe).forEach(function (c) { c.setAttribute("aria-pressed", c === knopf ? "true" : "false"); });
      var n = 0;
      zeilen.forEach(function (z) {
        var ok = (!wahl.land || z.getAttribute("data-land") === wahl.land) && (!wahl.stadt || z.getAttribute("data-stadt") === wahl.stadt);
        z.hidden = !ok; if (ok) n++;
      });
      // Mit Filter zeigt die Liste auch die Termine aus „Ab heute“ (ohne Filter blendet das CSS sie hier aus)
      block.classList.toggle("gefiltert", !!(wahl.land || wahl.stadt));
      $$(".kalender__monat", block).forEach(function (m) { m.hidden = !$("li[data-land]:not([hidden])", m); });
      if (zahl) zahl.textContent = n === 1 ? "1 Termin" : n + " Termine";
      if (leer) leer.hidden = n > 0;
      // Der Filter gilt auch für „Ab heute“ darüber (Q2-12): eine Karte dort bleibt, wenn ihr Termin in der Liste passt
      var aktiv = !!(wahl.land || wahl.stadt);
      $$(".woche--seite .termine-raster > li").forEach(function (karte) {
        var link = $("a[href]", karte), zeile = null;
        if (link) zeilen.forEach(function (z) { var a = $("a[href]", z); if (a && a.href === link.href) zeile = z; });
        karte.hidden = aktiv && !!zeile && zeile.hidden;
      });
    });
  });

  // YouTube erst nach Klick laden – oder sofort, wenn die Zustimmung „externe_medien“ vorliegt (Plugin tamil-site)
  function ladeVideo(box, perKlick) {
    if (box.classList.contains("is-geladen")) return;
    var id = box.getAttribute("data-video");
    var frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + (perKlick ? "?autoplay=1" : "");
    frame.title = "YouTube-Video";
    frame.allow = "autoplay; encrypted-media; picture-in-picture";
    frame.allowFullscreen = true;
    if (!perKlick) frame.loading = "lazy";
    box.classList.add("is-geladen");
    box.textContent = "";
    box.appendChild(frame);
    if (perKlick) frame.focus(); // der Knopf ist weg; der Fokus bleibt beim Video statt an den Seitenanfang zu springen
  }
  $$(".video-embed").forEach(function (box) {
    var btn = $(".video-load", box); if (!btn) return;
    btn.addEventListener("click", function () { ladeVideo(box, true); });
  });

  // Wischbare Kartenreihen: eine Karte, die per Tastatur den Fokus bekommt, ganz ins Bild holen (sonst bleibt beim
  // Einrasten jede zweite fast außerhalb, Q2-02); nur der Streifen rollt, die Seite höchstens so weit wie nötig
  $$(".karten--reihe").forEach(function (reihe) {
    reihe.addEventListener("focusin", function (e) {
      var karte = e.target.closest(".karten--reihe > *");
      if (!karte || karte.parentNode !== reihe) return;
      var r = karte.getBoundingClientRect(), s = reihe.getBoundingClientRect();
      if (r.left < s.left || r.right > s.right) karte.scrollIntoView({ inline: "start", block: "nearest", behavior: "auto" });
    });
  });

  // Bilder im Text, die nicht laden (Altbestand mit Bildern fremder Server per http://, Q2-05): ausblenden statt eines
  // leeren Rahmens mit Alternativtext als Link; der Inhalt selbst bleibt unverändert
  var bildWeg = function (img) {
    var huelle = img.closest(".blocks-gallery-item, .gallery-item, figure, .bild-ecke") || img;
    var link = img.parentNode && img.parentNode.tagName === "A" && img.parentNode.textContent.trim() === "" ? img.parentNode : null;
    (huelle !== img ? huelle : (link || img)).hidden = true;
  };
  $$(".inhalt img").forEach(function (img) {
    if (!img.getAttribute("src") || (img.complete && img.naturalWidth === 0 && !/\.svg(\?|$)/i.test(img.src))) bildWeg(img);
    else img.addEventListener("error", function () { bildWeg(img); }, { once: true });
  });

  // Link kopieren
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var txt = btn.getAttribute("data-copy") || location.href;
      var done = function () { var alt = btn.innerHTML; btn.innerHTML = "Kopiert"; setTimeout(function () { btn.innerHTML = alt; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, done); else done();
    });
  });


  // Tamil TV: Stream erst nach Klick laden (Safari/iOS spielen HLS direkt, sonst Link zum Stream) – oder sofort bei Zustimmung
  function ladeStream(box, perKlick) {
    if (box.classList.contains("is-geladen")) return;
    var src = box.getAttribute("data-stream"), v = document.createElement("video");
    box.classList.add("is-geladen");
    if (v.canPlayType("application/vnd.apple.mpegurl")) {
      v.src = src; v.controls = true; v.autoplay = perKlick; v.playsInline = true; v.preload = perKlick ? "auto" : "metadata";
      v.style.width = "100%"; v.style.height = "100%";
      box.innerHTML = ""; box.appendChild(v);
    } else {
      box.innerHTML = '<a class="knopf" href="' + src.replace(/"/g, "") + '" target="_blank" rel="noopener">Stream öffnen</a>';
    }
  }
  $$(".player[data-stream]").forEach(function (box) {
    var btn = $(".play", box); if (!btn) return;
    btn.addEventListener("click", function () { ladeStream(box, true); });
  });

  // Zustimmung „externe_medien“: Videos und Streams ohne Klick laden (nur wenn das Plugin die Zustimmung anbietet)
  function externeMedien() {
    var z = window.tamilZustimmung;
    if (!z || !z.hat("externe_medien")) return;
    $$(".video-embed").forEach(function (box) { if ($(".video-load", box)) ladeVideo(box, false); });
    $$(".player[data-stream]").forEach(function (box) { if ($(".play", box)) ladeStream(box, false); });
  }
  document.addEventListener("tamil:zustimmung", externeMedien);
  externeMedien();

  // Zutaten abhaken
  $$(".rezept-zutaten li").forEach(function (li) { li.addEventListener("click", function () { li.classList.toggle("ist-ab"); }); });
})();

/* Bewegung beim Scrollen, Variante D (Quelle: design/richtungen/klar2/bewegung/, Wahl von Luis am 16.11.2026).
   1. Jede Einheit (Kachel, Nebenstück, Meldung, Listenzeile, Blocktitel, Signet …) bekommt data-art (steigen,
      aufdecken, zeilen, vorhang, aufbau). Erst damit greifen die versteckenden Regeln in theme.css.
   2. Was beim Laden schon im Bild (oder darüber) ist, steht sofort da: nichts startet von selbst.
   3. Der Rest erscheint einmal, wenn er ins Bild kommt (IntersectionObserver, Klasse .da); was gemeinsam kommt,
      gestaffelt in Lesereihenfolge.
   Kopf, Leselinie und Aufmacher-Tiefe hängen am Scrollweg: per CSS-Scroll-Timeline, sonst über einen einzigen
   passiven Scroll-Handler mit requestAnimationFrame. Mit „Bewegung reduzieren“ passiert nichts davon. */
(() => {
  "use strict";

  const html = document.documentElement;
  const reduziert = window.matchMedia ? matchMedia("(prefers-reduced-motion: reduce)") : { matches: true };
  const kannIo = "IntersectionObserver" in window;
  const kannSda = !!(window.CSS && CSS.supports && CSS.supports("animation-timeline: scroll()"));
  if (reduziert.matches || !kannIo) return;

  const TAKT = 60;            // Staffel zwischen Stücken einer Reihe, die gemeinsam ins Bild kommen
  const STAFFEL_MAX = 6;      // höchstens 6 × 60 ms
  const REIHE = 100;          // jede weitere Reihe im selben Moment 100 ms später
  const REIHEN_MAX = 3;       // höchstens 300 ms
  const REIHE_TOLERANZ = 24;  // gleiche Reihe: Oberkanten weniger als 24 px auseinander
  const NACH_VORHANG = 0.55;  // Inhalt der dunklen Fläche beginnt nach 55 % des Vorhangs
  // Rubrikkacheln und wischbare Kartenreihen erscheinen gemeinsam, auch die rechts angeschnittenen
  // (dazu die wischbaren Reihen der Probe „Ausgabe“)
  const GRUPPE = ".kacheln, .karten--reihe, .streifen__bahn, .ausgabe__stapel--reihe";
  const TIEFE = 40;           // Aufmacherbild höchstens 40 px langsamer
  const REGELN = [
    [".kacheln li, .karte, .woche .kachel--klein, .woche__art, .grafik, .kueche .kachel--klein", "steigen"],
    [".block-titel, .woche__titel", "zeilen"],
    [".woche", "vorhang"],
    [".kachel--gross", "aufdecken zeilen"],
    [".signatur--flaeche", "aufbau"],   // Signet auf den Titan-Flächen: Punkte bauen die Form auf
  ];

  let io = null;
  let vorhangAb = 0;
  let aktiv = true;
  let T = {};
  let breite = innerWidth;
  const einheiten = new Set();
  const gruppen = new Map();
  const original = new Map();
  const uhren = new Set();
  const kopf = document.querySelector(".kopf");
  const band = document.querySelector(".band");
  const aufRahmen = document.querySelector(".aufmacher:not(.wow) .rahmen"); // der Wow-Aufmacher hat seine eigene Bewegung
  const aufBild = aufRahmen && aufRahmen.querySelector("img");

  const warte = (ms) => new Promise((ok) => setTimeout(ok, ms));
  const klemme = (x) => Math.min(1, Math.max(0, x));
  const ueberschrift = (el) => (el.matches("h2, h3") ? el : el.querySelector(".titel"));

  function zeiten() {
    const s = getComputedStyle(html);
    const ms = (name, sonst) => { const v = parseFloat(s.getPropertyValue(name)); return Number.isFinite(v) ? v : sonst; };
    return {
      steigen: ms("--t-steigen", 560), bild: ms("--t-bild", 750), zoom: ms("--t-zoom", 1100), blenden: ms("--t-blenden", 500),
      zeile: ms("--t-zeile", 700), takt: ms("--zeilen-takt", 90), zeilenStart: ms("--zeilen-start", 160), vorhang: ms("--t-vorhang", 800),
      aufbau: ms("--t-aufbau", 1500),
    };
  }

  // Zeilenumbrüche hängen an der Webschrift: erst messen, wenn sie geladen ist (höchstens 1,2 s warten)
  function schriften() {
    if (!document.fonts) return Promise.resolve();
    return Promise.race([
      Promise.all([document.fonts.load('650 20px "Libre Franklin"'), document.fonts.ready]).catch(() => {}),
      warte(1200),
    ]);
  }

  // Überschrift in ihre gemessenen Zeilen legen; der Text bleibt Text, nach dem Auftritt kommt das Original zurück
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
      aussen.className = "zeilenteil";
      innen.className = "zeilenteil__in";
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
    if (art.includes("aufdecken")) t = Math.max(t, T.bild, T.zoom, 100 + T.blenden);
    if (art.includes("vorhang")) t = Math.max(t, T.vorhang);
    if (art.includes("aufbau")) t = Math.max(t, T.aufbau);
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

  function zeige(el, verz, unterVorhang = false) {
    const art = el.dataset.art || "";
    const jetzt = performance.now();
    if (art.includes("vorhang")) vorhangAb = jetzt + verz;
    else if (unterVorhang && vorhangAb) verz += Math.max(0, vorhangAb + T.vorhang * NACH_VORHANG - jetzt);
    el.style.setProperty("--verz", Math.round(verz) + "ms");
    const los = () => {
      if (!aktiv) return;
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
    const neu = [];
    for (const e of eintraege) {
      if (!e.isIntersecting) continue;
      io.unobserve(e.target);
      neu.push(...(gruppen.get(e.target) || [e.target]));
    }
    // Schon über dem Bild (schnell vorbeigescrollt): ohne Staffel. Im Bild: oben vor unten, links vor rechts.
    const lage = new Map(neu.map((el) => [el, el.getBoundingClientRect()]));
    neu.filter((el) => lage.get(el).bottom <= 0).forEach((el) => zeige(el, 0));
    const imBild = neu.filter((el) => lage.get(el).bottom > 0).sort((x, y) => {
      const a = lage.get(x), b = lage.get(y);
      return Math.abs(a.top - b.top) > REIHE_TOLERANZ ? a.top - b.top : a.left - b.left;
    });
    const unter = (el) => !el.matches('[data-art~="vorhang"]') && !!el.closest('[data-art~="vorhang"]');
    for (const teil of [imBild.filter((el) => !unter(el)), imBild.filter(unter)]) {
      let reihe = -1, spalte = 0, oberkante = null;
      for (const el of teil) {
        const top = lage.get(el).top;
        if (oberkante === null || Math.abs(top - oberkante) > REIHE_TOLERANZ) { reihe++; spalte = 0; oberkante = top; }
        zeige(el, Math.min(reihe, REIHEN_MAX) * REIHE + Math.min(spalte++, STAFFEL_MAX) * TAKT, unter(el));
      }
    }
  }

  function beobachte() {
    // Auslöselinie 10 % über der Unterkante; nach oben reicht der Rahmen weit über die Seite hinaus, damit auch
    // schnell Übersprungenes erscheint
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
    await schriften();
    if (!aktiv) return;
    T = zeiten();
    for (const [sel, art] of REGELN) {
      for (const el of document.querySelectorAll(sel)) {
        if (el.closest(".mehr, .fuss, .ad")) continue;
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
    requestAnimationFrame(() => { if (aktiv) beobachte(); });
  }

  // Abschalten (Fehler oder „Bewegung reduzieren“ bei offener Seite): alles sichtbar, nichts geteilt
  function aus(fehler) {
    aktiv = false;
    html.classList.remove("bewegt", "sda");
    if (io) io.disconnect();
    uhren.forEach(clearTimeout);
    for (const h of [...original.keys()]) wiederher(h);
    for (const el of einheiten) { el.classList.remove("laeuft"); el.classList.add("da"); }
    if (fehler) console.warn("Bewegung abgeschaltet:", fehler);
  }

  // Ersatzweg ohne Scroll-Timelines: ein passiver Handler, gedrosselt auf ein Bild (rAF)
  let geplant = false;
  function aufScroll() { if (!geplant) { geplant = true; requestAnimationFrame(rechne); } }
  function rechne() {
    geplant = false;
    if (kannSda || !aktiv || !kopf) return;
    const y = scrollY;
    kopf.style.setProperty("--kopf", klemme(y / kopf.offsetHeight).toFixed(4));
    const weg = html.scrollHeight - innerHeight;
    if (band) band.style.setProperty("--fortschritt", (weg > 0 ? klemme(y / weg) : 0).toFixed(4));
    if (aufRahmen && aufBild) {
      const r = aufRahmen.getBoundingClientRect();
      const kante = band ? band.offsetHeight : 48;
      aufBild.style.setProperty("--tiefe", (klemme((kante - r.top) / r.height) * TIEFE).toFixed(1) + "px");
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

  try {
    html.classList.add("bewegt");
    if (kannSda) html.classList.add("sda");
    if (reduziert.addEventListener) reduziert.addEventListener("change", () => { if (reduziert.matches) aus(); });
    addEventListener("resize", neueBreite, { passive: true });
    if (!kannSda) {
      addEventListener("scroll", aufScroll, { passive: true });
      addEventListener("resize", aufScroll, { passive: true });
    }
    rechne();
    scharf().catch(aus);
  } catch (f) {
    aus(f);
  }
})();
