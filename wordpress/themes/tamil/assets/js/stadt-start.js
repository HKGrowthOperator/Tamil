/* „Tamil in meiner Stadt“ (Startseiten-Proben), Teil 1: steht direkt hinter dem Abschnitt im HTML und läuft vor dem
   ersten Malen. Zeigt das Auswahlfeld, liest die gespeicherte Stadt (nur localStorage, Schlüssel tamil_stadt) und
   filtert die Karten über data-stadt. Teil 2 (stadt.js, defer) bedient das Auswahlfeld. Kein Cookie, keine Anfrage,
   keine Standortabfrage. */
(function () {
  "use strict";
  var b = document.querySelector("[data-stadt-bereich]");
  if (!b || b.tamilStadt) return;
  var alle = function (s, r) { return Array.prototype.slice.call((r || b).querySelectorAll(s)); };
  var eins = function (s, r) { return (r || b).querySelector(s); };
  var hat = function (el, slug) { return (" " + (el.getAttribute("data-stadt") || "") + " ").indexOf(" " + slug + " ") > -1; };
  var GROSS = "(min-width: 1024px) 800px, (min-width: 600px) calc(66vw - 32px), calc(100vw - 32px)";

  // Zustand herstellen: slug leer = „Alle Städte“ (nur Karten mit data-alle). Hat die gewählte Stadt in einem Fach
  // nichts, zeigt das Fach den Bestand aus „Alle Städte“ und sagt es in der Zeile darüber ([data-ersatz]).
  // Gibt die Zahl der Karten der Stadt selbst je Fach zurück (für die Ansage), bei „Alle Städte“ die gezeigten.
  function zeige(slug, name) {
    var zahl = {}, sicht = {};
    alle("[data-fach]").forEach(function (fach) {
      var max = parseInt(fach.getAttribute("data-max"), 10) || 2, n = 0, eigen = 0;
      var karten = alle("[data-stadt-karte]", fach), art = fach.getAttribute("data-fach");
      if (slug) karten.forEach(function (k) {
        var ok = hat(k, slug) && eigen < max;
        k.hidden = !ok;
        if (ok) eigen++;
      });
      n = eigen;
      if (!eigen) karten.forEach(function (k) {
        var ok = k.hasAttribute("data-alle") && n < max;
        k.hidden = !ok;
        if (ok) n++;
      });
      var ersatz = !!slug && !eigen && n > 0, zeile = eins("[data-ersatz]", fach), kopf = eins("[data-fach-kopf]", fach);
      if (zeile) {
        zeile.textContent = ersatz ? (zeile.getAttribute("data-text") || "").replace("{stadt}", name || "") : "";
        zeile.hidden = !ersatz;
      }
      // Der Kopf hat ein eigenes Kennzeichen: data-art gehört dem Einblenden (app.js setzt es auch an Karten); danach
      // zu suchen traf in Fächern ohne umschaltbaren Kopf die erste Karte und leerte sie
      if (kopf) kopf.textContent = kopf.getAttribute(slug && eigen ? "data-text-stadt" : "data-text-alle");
      fach.classList.toggle("ist-ersatz", ersatz);
      zahl[art] = slug ? eigen : n;
      sicht[art] = n;
      fach.hidden = n === 0;
      fach.style.setProperty("--n", String(Math.max(1, n)));
    });
    // Kino: mit Stadt je Kino dieser Stadt eine Zeile mit „Tickets und Zeiten“
    alle(".stadt__spielorte").forEach(function (liste) {
      var n = 0;
      alle("li", liste).forEach(function (z) { z.hidden = !slug || z.getAttribute("data-stadt") !== slug; if (!z.hidden) n++; });
      liste.hidden = n === 0;
    });
    // Bühne „Aus der Stadt“: die erste sichtbare Karte groß (16:9), die übrigen klein (8:3)
    var buehne = eins("[data-buehne]");
    if (buehne) {
      var i = 0;
      alle("[data-stadt-karte]", buehne).forEach(function (k) {
        if (k.hidden) return;
        var gross = i++ === 0, rahmen = eins(".rahmen", k), bild = eins("img", k);
        k.classList.toggle("kachel--gross", gross); k.classList.toggle("kachel--klein", !gross);
        if (rahmen) { rahmen.classList.toggle("r169", gross); rahmen.classList.toggle("r83", !gross); }
        if (gross && bild && bild.getAttribute("sizes") !== GROSS) bild.setAttribute("sizes", GROSS);
      });
      buehne.className = buehne.className.replace(/kueche__raster--\d/, "kueche__raster--" + Math.max(1, i));
    }
    // Leerzustände als Satz, nur wenn das Fach auch mit dem Bestand aus allen Städten leer bleibt
    alle("[data-leer]").forEach(function (p) {
      var leer = !sicht[p.getAttribute("data-leer")], art = slug ? "data-text-stadt" : "data-text-alle", da = false;
      alle("[data-leer-satz], [data-leer-link]", p).forEach(function (t) {
        var text = (t.getAttribute(art) || "").replace("{stadt}", name || "");
        t.textContent = text; if (text) da = true;
      });
      p.hidden = !leer || !da;
    });
    var reihe = eins(".stadt__reihe");
    if (reihe) reihe.setAttribute("data-karten", String((sicht.kino || 0) + (sicht.termine || 0)));
    var titel = eins("[data-stadt-name]");
    if (titel) titel.textContent = slug ? name : titel.getAttribute("data-ohne");
    b.classList.toggle("stadt--gewaehlt", !!slug);
    return zahl;
  }
  b.tamilStadt = zeige;

  var wahl = eins("[data-stadt-wahl]"), feld = eins("select", wahl || b);
  if (!wahl || !feld) return;
  wahl.hidden = false;
  var gemerkt = null;
  try { gemerkt = JSON.parse(window.localStorage.getItem("tamil_stadt") || "null"); } catch (e) { gemerkt = null; }
  if (!gemerkt || typeof gemerkt.slug !== "string" || !gemerkt.slug) return;
  var option = alle("option", feld).filter(function (o) { return o.value === gemerkt.slug; })[0];
  if (option) {
    feld.value = gemerkt.slug;
    zeige(gemerkt.slug, option.textContent);
  } else {
    // Die gespeicherte Stadt steht nicht mehr in der Liste: „Alle Städte“ und ein Satz dazu
    var fort = eins("[data-stadt-fort]");
    if (fort && typeof gemerkt.name === "string" && gemerkt.name) {
      fort.textContent = (fort.getAttribute("data-text") || "").replace("{stadt}", gemerkt.name.slice(0, 60));
      fort.hidden = false;
    }
  }
})();
