// Kleine Helfer: Sicherheitsabfragen, Busy-Zustand beim Absenden, Live-Vorschau, Anweisungs-Chips, PWA
document.addEventListener("submit", (e) => {
  const form = e.target;
  const frage = form.getAttribute("data-confirm");
  if (frage && !window.confirm(frage)) { e.preventDefault(); return; }
  const btn = form.querySelector("button[data-busy]");
  if (btn) { btn.textContent = btn.getAttribute("data-busy"); btn.disabled = true; }
});

const inhalt = document.getElementById("inhalt");
if (inhalt) {
  const ziel = document.getElementById("vorschau-text");
  const titel = document.querySelector("input[name=titel]");
  const teaser = document.querySelector("textarea[name=teaser]");
  let t;
  const update = () => {
    clearTimeout(t);
    t = setTimeout(() => {
      if (ziel) {
        // Nur der bearbeitbare Haupttext; Kino-/Event-Block und Quelle hängt der Server beim Speichern an
        const parser = new DOMParser();
        const doc = parser.parseFromString(inhalt.value, "text/html");
        doc.querySelectorAll("script,iframe,object,embed,style").forEach((n) => n.remove());
        doc.querySelectorAll("*").forEach((n) => [...n.attributes].forEach((a) => { if (/^on/i.test(a.name) || /^javascript:/i.test(a.value)) n.removeAttribute(a.name); }));
        ziel.innerHTML = doc.body.innerHTML;
      }
      const vt = document.getElementById("vorschau-titel"); if (vt && titel) vt.textContent = titel.value;
      const vz = document.getElementById("vorschau-teaser"); if (vz && teaser) vz.textContent = teaser.value;
    }, 250);
  };
  inhalt.addEventListener("input", update);
  titel && titel.addEventListener("input", update);
  teaser && teaser.addEventListener("input", update);
}

document.querySelectorAll(".chip[data-anweisung]").forEach((chip) => {
  chip.addEventListener("click", () => {
    const ta = chip.closest("form").querySelector("textarea[name=anweisung]");
    ta.value = chip.getAttribute("data-anweisung");
    ta.focus();
  });
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}
