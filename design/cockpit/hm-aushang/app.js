// Cockpit-Probe hm-aushang: einziges Verhalten ist „Text kopieren“ beim WhatsApp-Entwurf.
// Ohne Skript bleibt der Text sichtbar und lässt sich von Hand markieren.
document.addEventListener("click", async (ereignis) => {
  const knopf = ereignis.target.closest("[data-kopieren]");
  if (!knopf) return;
  const quelle = document.getElementById(knopf.dataset.kopieren);
  const meldung = document.getElementById("wa-meldung");
  if (!quelle || !meldung) return;
  try {
    await navigator.clipboard.writeText(quelle.textContent);
    meldung.textContent = "Text in der Zwischenablage. Jetzt in WhatsApp einfügen.";
  } catch {
    const bereich = document.createRange();
    bereich.selectNodeContents(quelle);
    const auswahl = window.getSelection();
    auswahl.removeAllRanges();
    auswahl.addRange(bereich);
    meldung.textContent = "Text markiert. Mit Strg+C oder Teilen kopieren.";
  }
});
