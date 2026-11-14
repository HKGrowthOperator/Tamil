// tamil.de, Almanac-Probe: die Leiste faehrt beim Abwaertslesen ein, die Quartals-Reiter schalten den Jahresindex.
document.documentElement.classList.add('js');

(() => {
  const bar = document.querySelector('[data-bar]');
  if (!bar) return;
  let last = window.scrollY;
  let ticking = false;
  const update = () => {
    const y = window.scrollY;
    const down = y > last && y > 240;
    bar.classList.toggle('is-tucked', down);
    last = y;
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
})();

(() => {
  for (const box of document.querySelectorAll('[data-switch]')) {
    const list = box.querySelector('[role="tablist"]');
    const tabs = [...box.querySelectorAll('[role="tab"]')];
    const panels = tabs.map((t) => document.getElementById(t.getAttribute('aria-controls')));
    if (!list || !tabs.length) continue;
    list.hidden = false;
    const show = (i, focus) => {
      tabs.forEach((t, j) => {
        const on = i === j;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        panels[j].hidden = !on;
      });
      if (focus) tabs[i].focus({ preventScroll: true });
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => show(i, false));
      t.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') { e.preventDefault(); show((i + 1) % tabs.length, true); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); show((i - 1 + tabs.length) % tabs.length, true); }
      });
    });
    show(0, false);
  }
})();

// Formulare: Pflichtfelder pruefen, Fehler in Worten unter dem Feld; ohne Anschluss wird nichts gesendet.
(() => {
  const meldung = (el) => {
    if (el.validity.valueMissing) return el.type === 'checkbox' ? 'Bitte bestätigen.' : (el.type === 'radio' ? 'Bitte eines auswählen.' : 'Bitte ausfüllen.');
    if (el.validity.typeMismatch && el.type === 'email') return 'Die Adresse sieht unvollständig aus, etwa name@example.org.';
    if (el.validity.typeMismatch && el.type === 'url') return 'Bitte eine Adresse mit https:// angeben.';
    if (el.validity.rangeUnderflow) return 'Das Datum liegt in der Vergangenheit.';
    return 'Bitte prüfen.';
  };
  for (const form of document.querySelectorAll('form[data-form]')) {
    const fehler = form.querySelector('[data-fehler]');
    const stand = form.querySelector('[data-stand]');
    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      let erstes = null;
      let zahl = 0;
      const gesehen = new Set();
      for (const el of form.querySelectorAll('input, select, textarea')) {
        if (el.closest('.falle') || el.disabled) continue;
        if (el.type === 'radio') { if (gesehen.has(el.name)) continue; gesehen.add(el.name); }
        const ok = el.checkValidity();
        const hilfeId = (el.getAttribute('aria-describedby') || el.closest('fieldset')?.getAttribute('aria-describedby') || '').split(' ')[0];
        const hilfe = hilfeId ? document.getElementById(hilfeId) : null;
        if (el.type !== 'radio') el.toggleAttribute('aria-invalid', !ok);
        if (el.type !== 'radio' && !ok) el.setAttribute('aria-invalid', 'true');
        if (hilfe) hilfe.textContent = ok ? '' : meldung(el);
        if (!ok) { zahl += 1; erstes = erstes || el; }
      }
      if (zahl) {
        fehler.hidden = false;
        fehler.textContent = zahl === 1 ? 'Eine Angabe fehlt noch.' : `${zahl} Angaben fehlen noch.`;
        fehler.focus();
        return;
      }
      if (fehler) fehler.hidden = true;
      if (form.dataset.danke) { window.location.href = form.dataset.danke; return; }
      if (stand) stand.textContent = 'Nichts gesendet: Das Formular ist noch nicht angeschlossen.';
    });
  }
  const anliegen = document.querySelector('[data-anliegen]');
  const wert = new URLSearchParams(window.location.search).get('anliegen');
  if (anliegen && wert) anliegen.value = wert;
})();

// Verzeichnis: Filter wirken sofort auf die Liste; die Auswahl steht zugleich in der Adresse.
(() => {
  const form = document.querySelector('[data-filter]');
  if (!form) return;
  const zeilen = [...document.querySelectorAll('tr[data-art]')];
  const anzahl = document.querySelector('[data-anzahl]');
  const leer = document.querySelector('[data-leer]');
  const params = new URLSearchParams(window.location.search);
  for (const [k, v] of params) {
    const el = form.elements[k];
    if (!el) continue;
    if (el instanceof RadioNodeList) { for (const r of el) r.checked = r.value === v; } else { el.value = v; }
  }
  const anwenden = () => {
    const f = new FormData(form);
    const q = (f.get('q') || '').toString().trim().toLowerCase();
    let n = 0;
    for (const z of zeilen) {
      const passt = (!f.get('art') || z.dataset.art === f.get('art'))
        && (!f.get('land') || z.dataset.land === f.get('land'))
        && (!f.get('region') || z.dataset.region === f.get('region'))
        && (!f.get('stadt') || z.dataset.stadt === f.get('stadt'))
        && (!q || z.textContent.toLowerCase().includes(q));
      z.hidden = !passt;
      if (passt) n += 1;
    }
    anzahl.textContent = String(n);
    leer.hidden = n > 0;
  };
  form.addEventListener('input', anwenden);
  form.addEventListener('change', anwenden);
  form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    const f = new URLSearchParams();
    for (const [k, v] of new FormData(form)) if (v) f.set(k, v.toString());
    history.replaceState(null, '', f.toString() ? `?${f}` : window.location.pathname);
    anwenden();
  });
  anwenden();
})();
