/* „Tamil in meiner Stadt“ (Startseiten-Proben), Teil 2: Auswahlfeld bedienen. Die Wahl filtert die Karten (Funktion aus
   stadt-start.js am Abschnitt), wird nur im localStorage dieses Browsers gemerkt (Schlüssel tamil_stadt, „Alle Städte“
   löscht den Eintrag) und steht danach in der Statuszeile für Vorleseprogramme. Kein Cookie, keine Anfrage an den
   Server, keine Standortabfrage. */
(function () {
  "use strict";
  var b = document.querySelector("[data-stadt-bereich]");
  if (!b || typeof b.tamilStadt !== "function") return;
  var feld = b.querySelector("[data-stadt-wahl] select");
  if (!feld) return;
  var inhalt = b.querySelector("[data-stadt-inhalt]");
  var status = b.querySelector("[data-stadt-status]");
  var fort = b.querySelector("[data-stadt-fort]");
  var ruhig = !window.matchMedia || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var uhr = 0;

  function wort(n, eins, viele, keins) { return n === 0 ? keins : n === 1 ? "1 " + eins : n + " " + viele; }

  function melde(name, zahl) {
    if (!status) return;
    // angesagt wird nur, was der Abschnitt führt (der Streifen der Probe „Ausgabe“ hat kein Fach für Geschichten)
    var teile = [];
    if ("kino" in zahl) teile.push(wort(zahl.kino || 0, "Film im Kino", "Filme im Kino", "keine Vorstellung"));
    if ("termine" in zahl) teile.push(wort(zahl.termine || 0, "Termin", "Termine", "kein Termin"));
    if ("geschichten" in zahl) teile.push(wort(zahl.geschichten || 0, "Geschichte", "Geschichten", "keine Geschichte"));
    status.textContent = name + ": " + teile.join(", ") + ".";
  }

  function wechsle() {
    var slug = feld.value;
    var name = slug ? feld.options[feld.selectedIndex].textContent : "";
    try {
      if (slug) window.localStorage.setItem("tamil_stadt", JSON.stringify({ slug: slug, name: name }));
      else window.localStorage.removeItem("tamil_stadt");
    } catch (e) { /* privater Modus: die Wahl gilt dann nur für diese Ansicht */ }
    if (fort) fort.hidden = true;
    var fertig = function () {
      melde(slug ? name : feld.options[0].textContent, b.tamilStadt(slug, name));
      if (inhalt) inhalt.classList.remove("ist-wechsel");
    };
    window.clearTimeout(uhr);
    // Antwort auf die Handlung: kurz ausblenden, umstellen, einblenden (160 ms); mit „Bewegung reduzieren“ sofort
    if (ruhig || !inhalt) { fertig(); return; }
    inhalt.classList.add("ist-wechsel");
    uhr = window.setTimeout(fertig, 160);
  }

  feld.addEventListener("change", wechsle);
})();
