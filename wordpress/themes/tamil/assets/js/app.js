/* Tamil.de Theme – Menü, Suche, Laufband, Lesebalken, Zähler, Filter, Monatsansicht, Mininav, TV-Player. Kein Framework. */
(function () {
  "use strict";
  var $ = function (s, root) { return (root || document).querySelector(s); };
  var $$ = function (s, root) { return Array.prototype.slice.call((root || document).querySelectorAll(s)); };
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Drawer (mobile Navigation)
  var drawer = $("#drawer"), burger = $("#burger");
  function openDrawer() { if (!drawer) return; drawer.hidden = false; burger && burger.setAttribute("aria-expanded", "true"); var first = $("a, button", drawer); first && first.focus(); }
  function closeDrawer() { if (!drawer || drawer.hidden) return; drawer.hidden = true; burger && burger.setAttribute("aria-expanded", "false"); burger && burger.focus(); }
  burger && burger.addEventListener("click", function () { drawer.hidden ? openDrawer() : closeDrawer(); });
  drawer && drawer.addEventListener("click", function (e) { if (e.target === drawer || e.target.closest("[data-close]")) closeDrawer(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  // Suche (mobil)
  var sucheBtn = $("#suche-btn"), suche = $("#suche");
  sucheBtn && sucheBtn.addEventListener("click", function () { suche.style.display = suche.style.display === "flex" ? "" : "flex"; var i = $("input", suche); i && i.focus(); });

  // Mobile Sticky-Werbeplatz schließen
  var sticky = $("#ad-mobile");
  if (sticky) $(".schliessen", sticky).addEventListener("click", function () { sticky.hidden = true; var site = $(".site"); site && site.classList.remove("has-sticky-ad"); });

  // Ticker und Filmstreifen: Inhalt verdoppeln, damit die Schleife nahtlos läuft
  $$(".ticker .track, .strip .track").forEach(function (track) {
    if (reduced) return;
    track.innerHTML += track.innerHTML;
    track.querySelectorAll("[id]").forEach(function (n, i) { if (i >= track.children.length / 2) n.removeAttribute("id"); });
  });

  // Lesebalken (Artikel)
  var balken = $(".lesebalken");
  if (balken) {
    var tick = function () { var h = document.documentElement; var max = h.scrollHeight - h.clientHeight; balken.style.width = (max > 0 ? Math.min(100, h.scrollTop / max * 100) : 0) + "%"; };
    window.addEventListener("scroll", tick, { passive: true }); tick();
  }

  // Zähler (Kino-Radar): zählt hoch, sobald sichtbar – einmal
  var zaehler = $$("[data-count]");
  if (zaehler.length && "IntersectionObserver" in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, ziel = parseInt(el.getAttribute("data-count"), 10), start = performance.now(), dauer = 900;
        var step = function (t) { var p = Math.min(1, (t - start) / dauer); p = 1 - Math.pow(1 - p, 3); el.textContent = Math.round(ziel * p); if (p < 1) requestAnimationFrame(step); };
        requestAnimationFrame(step); io.unobserve(el);
      });
    }, { threshold: .6 });
    zaehler.forEach(function (el) { el.textContent = "0"; io.observe(el); });
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

  // YouTube erst nach Klick laden
  $$(".video-embed").forEach(function (box) {
    var btn = $(".video-load", box); if (!btn) return;
    btn.addEventListener("click", function () {
      var id = box.getAttribute("data-video");
      box.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1" title="YouTube-Video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
    });
  });

  // Link kopieren
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var txt = btn.getAttribute("data-copy") || location.href;
      var done = function () { var alt = btn.innerHTML; btn.innerHTML = "Kopiert"; setTimeout(function () { btn.innerHTML = alt; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, done); else done();
    });
  });


  // Mininav (Startseite): aktiver Abschnitt beim Scrollen, sanftes Springen
  var mini = $(".mininav");
  if (mini && "IntersectionObserver" in window) {
    var links = $$("a[href^='#']", mini), ziele = links.map(function (a) { return $(a.getAttribute("href")); }).filter(Boolean);
    var setActive = function (id) { links.forEach(function (a) { a.classList.toggle("is-active", a.getAttribute("href") === "#" + id); }); };
    var mio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) setActive(en.target.id); });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    ziele.forEach(function (z) { mio.observe(z); });
    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var z = $(a.getAttribute("href")); if (!z) return;
        e.preventDefault(); setActive(z.id);
        z.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
        history.replaceState(null, "", a.getAttribute("href"));
      });
    });
  }


  // Tamil TV: Stream erst nach Klick laden (Safari/iOS spielen HLS direkt, sonst Link zum Stream)
  $$(".player[data-stream]").forEach(function (box) {
    var btn = $(".play", box); if (!btn) return;
    btn.addEventListener("click", function () {
      var src = box.getAttribute("data-stream"), v = document.createElement("video");
      if (v.canPlayType("application/vnd.apple.mpegurl")) {
        v.src = src; v.controls = true; v.autoplay = true; v.playsInline = true; v.style.width = "100%"; v.style.height = "100%";
        box.innerHTML = ""; box.appendChild(v);
      } else {
        box.innerHTML = '<a class="btn btn-gold" href="' + src.replace(/"/g, "") + '" target="_blank" rel="noopener">Stream öffnen</a>';
      }
    });
  });

  // Zutaten abhaken
  $$(".zutaten li, .rezept-zutaten li").forEach(function (li) { li.addEventListener("click", function () { var an = li.style.opacity === "0.45"; li.style.opacity = an ? "" : "0.45"; li.style.textDecoration = an ? "" : "line-through"; }); });
})();
