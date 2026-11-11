/* Tamil.de – Cookie-Zustimmung. Eigene Lösung, kein fremdes Skript, nichts geht an Dritte.
 * Die Wahl liegt sechs Monate im Browser (localStorage, sonst ein eigenes Cookie).
 * Schnittstelle: window.tamilZustimmung.hat("externe_medien"), .oeffnen(); Ereignis "tamil:zustimmung" am document
 * (detail: { externe_medien: bool, statistik: bool }), auch einmal beim Laden, wenn schon eine Wahl vorliegt. */
(function () {
  "use strict";
  var SCHLUESSEL = "tamil_zustimmung";
  var DAUER_MS = 182 * 24 * 60 * 60 * 1000; // sechs Monate
  var KATEGORIEN = ["externe_medien", "statistik"];
  var hinweis = document.querySelector("[data-tz-hinweis]");
  var dialog = document.querySelector(".tz-dialog");
  var fassung = hinweis ? hinweis.getAttribute("data-fassung") || "" : "";
  var ausloeser = null;

  function lesen() {
    var roh = null;
    try { roh = window.localStorage.getItem(SCHLUESSEL); } catch (e) { roh = null; }
    if (!roh) {
      var m = document.cookie.match(/(?:^|;\s*)tamil_zustimmung=([^;]*)/);
      roh = m ? decodeURIComponent(m[1]) : null;
    }
    if (!roh) return null;
    var d;
    try { d = JSON.parse(roh); } catch (e) { return null; }
    if (!d || d.v !== 1 || d.fassung !== fassung || typeof d.zeit !== "number" || Date.now() - d.zeit > DAUER_MS) return null;
    return d;
  }

  function schreiben(d) {
    var roh = JSON.stringify(d);
    try { window.localStorage.setItem(SCHLUESSEL, roh); return; } catch (e) { /* weiter mit Cookie */ }
    document.cookie = SCHLUESSEL + "=" + encodeURIComponent(roh) + "; Max-Age=" + Math.floor(DAUER_MS / 1000) +
      "; Path=/; SameSite=Lax" + (location.protocol === "https:" ? "; Secure" : "");
  }

  var stand = lesen();

  function hat(kategorie) {
    if (kategorie === "notwendig") return true;
    return !!(stand && stand[kategorie] === true);
  }

  // Inhalte, die erst nach Zustimmung laden dürfen (z. B. fremdes Werbe-HTML), stehen inaktiv in
  // <template data-zustimmung="kategorie"> und werden hier eingesetzt. Skripte aus einer Vorlage laufen nicht von selbst,
  // darum werden sie neu angelegt. (Werbeskripte mit document.write funktionieren nachträglich nicht.)
  function vorlagenEinsetzen() {
    Array.prototype.forEach.call(document.querySelectorAll("template[data-zustimmung]"), function (tpl) {
      if (!hat(tpl.getAttribute("data-zustimmung"))) return;
      var platz = tpl.closest("[data-tz-platz]") || tpl.parentNode;
      var inhalt = tpl.content.cloneNode(true);
      Array.prototype.forEach.call(inhalt.querySelectorAll("script"), function (alt) {
        var neu = document.createElement("script");
        Array.prototype.forEach.call(alt.attributes, function (a) { neu.setAttribute(a.name, a.value); });
        neu.text = alt.text;
        alt.parentNode.replaceChild(neu, alt);
      });
      platz.textContent = "";
      platz.appendChild(inhalt);
    });
  }

  function melden() {
    vorlagenEinsetzen();
    var detail = {};
    KATEGORIEN.forEach(function (k) { detail[k] = hat(k); });
    var ev;
    try { ev = new CustomEvent("tamil:zustimmung", { detail: detail }); }
    catch (e) { ev = document.createEvent("CustomEvent"); ev.initCustomEvent("tamil:zustimmung", false, false, detail); }
    document.dispatchEvent(ev);
  }

  function schliessen() {
    if (dialog && dialog.open) dialog.close();
  }

  function setzen(werte) {
    stand = { v: 1, fassung: fassung, zeit: Date.now() };
    KATEGORIEN.forEach(function (k) { stand[k] = !!werte[k]; });
    schreiben(stand);
    if (hinweis) hinweis.hidden = true;
    schliessen();
    melden();
  }

  function oeffnen(von) {
    if (!dialog) return;
    ausloeser = von || document.activeElement;
    KATEGORIEN.forEach(function (k) {
      var feld = dialog.querySelector('[name="tz-' + k + '"]');
      if (feld) feld.checked = hat(k);
    });
    if (typeof dialog.showModal === "function") {
      if (!dialog.open) dialog.showModal(); // modal: der Rest der Seite ist inaktiv, der Fokus bleibt im Dialog
    } else {
      dialog.setAttribute("open", "");
    }
    var erstes = dialog.querySelector('input:not([disabled]), button');
    if (erstes) erstes.focus();
  }

  if (dialog) {
    dialog.addEventListener("close", function () {
      if (ausloeser && typeof ausloeser.focus === "function" && document.contains(ausloeser) && ausloeser.offsetParent !== null) ausloeser.focus();
      else if (hinweis && !hinweis.hidden) { var k = hinweis.querySelector("button"); if (k) k.focus(); }
      ausloeser = null;
    });
    // Klick auf den abgedunkelten Hintergrund schließt den Dialog ohne Änderung
    dialog.addEventListener("click", function (e) { if (e.target === dialog) schliessen(); });
  }

  document.addEventListener("click", function (e) {
    var ziel = e.target && e.target.closest ? e.target.closest("[data-tz-alle], [data-tz-notwendig], [data-tz-speichern], [data-tz-oeffnen]") : null;
    if (!ziel) return;
    e.preventDefault();
    if (ziel.hasAttribute("data-tz-oeffnen")) { oeffnen(ziel); return; }
    if (ziel.hasAttribute("data-tz-alle")) { setzen({ externe_medien: true, statistik: true }); return; }
    if (ziel.hasAttribute("data-tz-notwendig")) { setzen({}); return; }
    var werte = {};
    KATEGORIEN.forEach(function (k) {
      var feld = dialog && dialog.querySelector('[name="tz-' + k + '"]');
      werte[k] = !!(feld && feld.checked);
    });
    setzen(werte);
  });

  window.tamilZustimmung = {
    hat: hat,
    oeffnen: function () { oeffnen(null); },
    stand: function () { var d = {}; KATEGORIEN.forEach(function (k) { d[k] = hat(k); }); return d; }
  };

  if (location.hash === "#cookie-einstellungen") oeffnen(null);
  if (!stand && hinweis) hinweis.hidden = false;
  if (stand) melden();
})();
