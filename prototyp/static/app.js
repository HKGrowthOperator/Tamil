/* Tamil.de Prototyp – nur Zustandswechsel, keine Datenabfragen. Alle Formulare sind Attrappen. */
(function () {
  "use strict";
  var $ = function (s, root) { return (root || document).querySelector(s); };
  var $$ = function (s, root) { return Array.prototype.slice.call((root || document).querySelectorAll(s)); };

  // Drawer (mobile Navigation)
  var drawer = $("#drawer"), burger = $("#burger");
  function openDrawer() { if (!drawer) return; drawer.hidden = false; burger && burger.setAttribute("aria-expanded", "true"); var first = $("a, button", drawer); first && first.focus(); }
  function closeDrawer() { if (!drawer || drawer.hidden) return; drawer.hidden = true; burger && burger.setAttribute("aria-expanded", "false"); burger && burger.focus(); }
  burger && burger.addEventListener("click", function () { drawer.hidden ? openDrawer() : closeDrawer(); });
  drawer && drawer.addEventListener("click", function (e) { if (e.target === drawer || e.target.closest("[data-close]")) closeDrawer(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  // Suche (mobil: Feld einblenden)
  var sucheBtn = $("#suche-btn"), suche = $("#suche");
  sucheBtn && sucheBtn.addEventListener("click", function () { suche.style.display = suche.style.display === "flex" ? "" : "flex"; var i = $("input", suche); i && i.focus(); });

  // Mobile Sticky-Werbeplatz schließen
  var sticky = $("#ad-mobile");
  if (sticky) $(".schliessen", sticky).addEventListener("click", function () { sticky.hidden = true; document.body.classList.remove("has-sticky-ad"); $(".site") && $(".site").classList.remove("has-sticky-ad"); });

  // Filter-Chips (Kategorieseite, Events)
  $$("[data-filter-group]").forEach(function (group) {
    var key = group.getAttribute("data-filter-group");
    var items = $$("[data-" + key + "]");
    group.addEventListener("click", function (e) {
      var chip = e.target.closest("[data-filter]"); if (!chip) return;
      $$("[data-filter]", group).forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      var wert = chip.getAttribute("data-filter");
      var sichtbar = 0;
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

  // YouTube erst nach Klick laden (youtube-nocookie)
  $$(".video-embed").forEach(function (box) {
    var btn = $(".video-load", box); if (!btn) return;
    btn.addEventListener("click", function () {
      var id = box.getAttribute("data-video");
      box.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1" title="YouTube-Video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
    });
  });

  // Formulare: nur Erfolgsmeldung (Prototyp)
  $$("form[data-demo]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      form.classList.add("ist-gesendet");
      var ok = $(".erfolg", form); ok && ok.scrollIntoView({ block: "nearest" });
    });
  });
  $$("[data-betreff]").forEach(function (a) {
    a.addEventListener("click", function () { var sel = $("#betreff"); if (sel) { sel.value = a.getAttribute("data-betreff"); } });
  });

  // Link kopieren
  $$("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var txt = btn.getAttribute("data-copy") || location.href;
      var done = function () { var alt = btn.innerHTML; btn.innerHTML = "Kopiert"; setTimeout(function () { btn.innerHTML = alt; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, done); else done();
    });
  });

  // Zutaten abhaken
  $$(".zutaten li").forEach(function (li) { li.addEventListener("click", function () { li.style.opacity = li.style.opacity === "0.45" ? "" : "0.45"; li.style.textDecoration = li.style.opacity ? "line-through" : ""; }); });
})();
