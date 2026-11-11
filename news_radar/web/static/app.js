// Cockpit-Helfer: Sicherheitsabfragen, Busy-Zustand, Live-Vorschau, Anweisungs-Chips, Tastaturkürzel im Feed, Countdown, PWA
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
        const parser = new DOMParser();
        const doc = parser.parseFromString(inhalt.value, "text/html");
        // Live-Vorschau: dieselbe Allowlist wie auf dem Server (render.sanitize_html), dazu blockt die CSP Inline-Skripte
        const TAGS = /^(P|H2|H3|STRONG|EM|B|I|UL|OL|LI|A|BR|BLOCKQUOTE|FIGURE|FIGCAPTION|IMG|DIV|SPAN|TABLE|THEAD|TBODY|TR|TH|TD)$/;
        const ATTR = /^(class|href|src|alt|title|rel|target|width|height|colspan|rowspan)$/;
        doc.querySelectorAll("script,style,iframe,object,embed,template,noscript").forEach((n) => n.remove());
        [...doc.body.querySelectorAll("*")].reverse().forEach((n) => {
          [...n.attributes].forEach((a) => {
            const wert = a.value.replace(/[\u0000-\u0020\u007f]/g, "");
            if (!ATTR.test(a.name) || ((a.name === "href" || a.name === "src") && !/^(https?:|mailto:|\/(?!\/)|#)/i.test(wert))) n.removeAttribute(a.name);
          });
          if (!TAGS.test(n.tagName)) n.replaceWith(...n.childNodes);
        });
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

// Sammelfreigabe: Auswahl je Karte, „alle sichtbaren“, Rückfrage mit Anzahl (Server prüft jeden Entwurf einzeln)
const sammel = document.querySelector("form[data-sammel]");
if (sammel) {
  const boxen = [...document.querySelectorAll('input[name="ids"][form="sammel"]')];
  const alle = sammel.querySelector("[data-alle]");
  const anzahl = sammel.querySelector("[data-anzahl]");
  const knopf = sammel.querySelector("button");
  const zaehle = () => {
    const n = boxen.filter((b) => b.checked).length;
    anzahl.textContent = n ? `${n} ausgewählt` : "Keiner ausgewählt";
    knopf.disabled = n === 0;
    alle.checked = n > 0 && n === boxen.length;
    alle.indeterminate = n > 0 && n < boxen.length;
    sammel.setAttribute("data-confirm", `${n} ${n === 1 ? "Entwurf" : "Entwürfe"} freigeben?`);
  };
  boxen.forEach((b) => b.addEventListener("change", zaehle));
  alle.addEventListener("change", () => { boxen.forEach((b) => { b.checked = alle.checked; }); zaehle(); });
  zaehle();
}

// Tastatur im Feed: J/K wechseln, F freigeben, A ablehnen, Enter öffnet
const board = document.querySelector("[data-board]");
if (board) {
  const karten = [...board.querySelectorAll(".entwurf-karte")];
  let idx = -1;
  const setze = (i) => {
    if (!karten.length) return;
    idx = Math.max(0, Math.min(karten.length - 1, i));
    karten.forEach((k, n) => k.classList.toggle("ist-fokus", n === idx));
    karten[idx].scrollIntoView({ block: "nearest", behavior: "smooth" });
  };
  karten.forEach((k, n) => k.addEventListener("focus", () => setze(n)));
  document.addEventListener("keydown", (e) => {
    if (e.target.matches("input, textarea, select") || e.metaKey || e.ctrlKey || e.altKey) return;
    const key = e.key.toLowerCase();
    if (key === "j" || key === "arrowdown") { e.preventDefault(); setze(idx + 1); }
    else if (key === "k" || key === "arrowup") { e.preventDefault(); setze(idx - 1); }
    else if (idx >= 0 && (key === "f" || key === "a")) { const f = karten[idx].querySelector(`form[data-key="${key}"]`); if (f) { e.preventDefault(); f.requestSubmit ? f.requestSubmit() : f.submit(); } }
    else if (idx >= 0 && key === "enter") { const a = karten[idx].querySelector("[data-open]"); if (a) { e.preventDefault(); a.click(); } }
  });
}

// Countdown bis zum nächsten Lauf (Takt: 3 Minuten ab dem letzten Start)
const status = document.querySelector(".rail .status[data-lauf]");
if (status) {
  const ziel = status.querySelector("[data-countdown] b");
  const start = Date.parse(status.getAttribute("data-lauf").replace(" ", "T"));
  if (ziel && !Number.isNaN(start)) {
    const tick = () => {
      const takt = 180000;
      let rest = takt - ((Date.now() - start) % takt);
      const s = Math.floor(rest / 1000);
      ziel.textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
    };
    tick(); setInterval(tick, 1000);
  }
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}

document.querySelectorAll("select[data-auto-submit]").forEach((sel) => sel.addEventListener("change", () => sel.form.submit()));
