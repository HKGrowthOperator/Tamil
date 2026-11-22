/* „Tamil in meiner Stadt“ als Streifen (Probe „Ausgabe“): Die Reihe der Karten ist seitlich wischbar, sobald sie breiter
   ist als ihr Platz. Dann zeigt dieses Skript darunter einen Balken (wo man steht und wie viel es gibt) und zwei Pfeile
   für Tastatur und Maus. Passt alles in den Platz, bleibt beides verborgen. Bewegung nur als Antwort auf Wischen oder
   Tippen; mit „Bewegung reduzieren“ springt die Reihe ohne Gleiten. Keine Anfrage, nichts wird gespeichert. */
(function () {
  "use strict";
  var s = document.querySelector("[data-streifen]");
  if (!s) return;
  var bahn = s.querySelector("[data-bahn]"), lage = s.querySelector("[data-lage]");
  if (!bahn || !lage) return;
  var zurueck = lage.querySelector("[data-zurueck]"), weiter = lage.querySelector("[data-weiter]"), balken = lage.querySelector("[data-balken]");
  var ruhig = !window.matchMedia || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var wartet = false;

  function stand() {
    wartet = false;
    var weg = bahn.scrollWidth - bahn.clientWidth, zuviel = weg > 4;
    lage.hidden = !zuviel;
    if (!zuviel) return;
    var anteil = bahn.clientWidth / bahn.scrollWidth, ort = Math.min(1, Math.max(0, bahn.scrollLeft / weg));
    if (balken) {
      balken.style.width = (anteil * 100).toFixed(2) + "%";
      balken.style.left = ((1 - anteil) * ort * 100).toFixed(2) + "%";
    }
    if (zurueck) zurueck.disabled = bahn.scrollLeft <= 2;
    if (weiter) weiter.disabled = bahn.scrollLeft >= weg - 2;
  }
  function gleich() {
    if (wartet) return;
    wartet = true;
    (window.requestAnimationFrame || window.setTimeout)(stand);
  }
  // ein Schritt = eine Karte samt Abstand
  function schritt(richtung) {
    var karte = bahn.querySelector("[data-stadt-karte]:not([hidden])");
    var breite = karte ? karte.getBoundingClientRect().width + 20 : bahn.clientWidth * 0.8;
    bahn.scrollBy({ left: richtung * breite, behavior: ruhig ? "auto" : "smooth" });
  }

  if (zurueck) zurueck.addEventListener("click", function () { schritt(-1); });
  if (weiter) weiter.addEventListener("click", function () { schritt(1); });
  bahn.addEventListener("scroll", gleich, { passive: true });
  window.addEventListener("resize", gleich);
  // Stadtwechsel blendet Karten ein und aus: Reihe an den Anfang, Balken neu rechnen
  if ("MutationObserver" in window) {
    new MutationObserver(function () { bahn.scrollLeft = 0; gleich(); }).observe(bahn, { subtree: true, attributes: true, attributeFilter: ["hidden"] });
  }
  stand();
})();
