/* Tamil.de Theme – Menü, Suche, Lesebalken, Filter, Monatsansicht, Videos, Link kopieren, TV-Player. Kein Framework. */
(function () {
  "use strict";
  var $ = function (s, root) { return (root || document).querySelector(s); };
  var $$ = function (s, root) { return Array.prototype.slice.call((root || document).querySelectorAll(s)); };
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Menü (Seitenpaneel)
  var menue = $("#menue"), burger = $("#burger");
  function openMenue() { if (!menue) return; menue.hidden = false; document.body.style.overflow = "hidden"; burger && burger.setAttribute("aria-expanded", "true"); var first = $("a, button", menue); first && first.focus(); }
  function closeMenue() { if (!menue || menue.hidden) return; menue.hidden = true; document.body.style.overflow = ""; burger && burger.setAttribute("aria-expanded", "false"); burger && burger.focus(); }
  burger && burger.addEventListener("click", function () { menue.hidden ? openMenue() : closeMenue(); });
  menue && menue.addEventListener("click", function (e) { if (e.target === menue || e.target.closest("[data-close]")) closeMenue(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeMenue(); } });

  // Suche im Kopf
  var sucheBtn = $("#suche-btn"), suche = $("#suche");
  sucheBtn && suche && sucheBtn.addEventListener("click", function () {
    suche.hidden = !suche.hidden;
    sucheBtn.setAttribute("aria-expanded", suche.hidden ? "false" : "true");
    if (!suche.hidden) { var i = $("input", suche); i && i.focus(); }
  });

  // Mobiler Werbeplatz: schließen
  var sticky = $("#ad-mobile");
  if (sticky && $(".schliessen", sticky)) $(".schliessen", sticky).addEventListener("click", function () { sticky.hidden = true; var site = $(".site"); site && site.classList.remove("has-sticky-ad"); });

  // Lesebalken (Artikel)
  var balken = $(".lesebalken");
  if (balken) {
    var tick = function () { var h = document.documentElement; var max = h.scrollHeight - h.clientHeight; balken.style.width = (max > 0 ? Math.min(100, h.scrollTop / max * 100) : 0) + "%"; };
    window.addEventListener("scroll", tick, { passive: true }); tick();
  }

  // Filter-Chips (Kategorieseite, Events)
  $$("[data-filter-group]").forEach(function (group) {
    var key = group.getAttribute("data-filter-group");
    var items = $$("[data-" + key + "]");
    group.addEventListener("click", function (e) {
      var chip = e.target.closest("[data-filter]"); if (!chip) return;
      $$("[data-filter]", group).forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      var wert = chip.getAttribute("data-filter"), sichtbar = 0;
      items.forEach(function (el) { var ok = wert === "alle" || (" " + el.getAttribute("data-" + key) + " ").indexOf(" " + wert + " ") >= 0; el.hidden = !ok; if (ok) sichtbar++; });
      var leer = $("[data-filter-leer='" + key + "']"); if (leer) leer.hidden = sichtbar > 0;
      $$("[data-filter-count='" + key + "']").forEach(function (el) { el.textContent = sichtbar; });
    });
  });

  // Events: Liste / Monat
  $$("[data-view]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var ziel = btn.getAttribute("data-view");
      $$("[data-view]").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      $$("[data-view-panel]").forEach(function (p) { p.hidden = p.getAttribute("data-view-panel") !== ziel; });
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
      box.innerHTML = '<a class="knopf knopf-rot" href="' + src.replace(/"/g, "") + '" target="_blank" rel="noopener">Stream öffnen</a>';
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
  $$(".rezept-zutaten li").forEach(function (li) { li.addEventListener("click", function () { var an = li.style.opacity === "0.45"; li.style.opacity = an ? "" : "0.45"; li.style.textDecoration = an ? "" : "line-through"; }); });
})();
