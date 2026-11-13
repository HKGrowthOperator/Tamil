/* tamil.de, Linie Aushang: kleine Helfer. Ohne Skript zeigt jede Seite alles; das Skript filtert nur und sagt ehrlich,
   dass die Formulare in dieser Probe nicht angeschlossen sind. */
(() => {
  const MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
  const TAGE = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
  const lang = (d) => `${TAGE[d.getDay()]}, ${d.getDate()}. ${MONATE[d.getMonth()]} ${d.getFullYear()}`;

  // Kino: Stadt eintippen, die Liste wird kürzer
  document.querySelectorAll('[data-filter]').forEach((input) => {
    const liste = document.querySelector(input.dataset.filter);
    const hilfe = document.getElementById(input.getAttribute('aria-describedby'));
    if (!liste) return;
    const zeilen = [...liste.children];
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      let n = 0;
      zeilen.forEach((z) => { const treffer = !q || (z.dataset.stadt || '').includes(q); z.hidden = !treffer; if (treffer) n += 1; });
      if (hilfe) hilfe.textContent = !q ? '' : n ? `${n} ${n === 1 ? 'Stadt' : 'Städte'} mit tamilischem Film.` : 'Für diese Stadt ist diese Woche kein tamilischer Film gemeldet.';
    });
  });

  // Verzeichnis: Filter stehen in der Adresse und lassen sich teilen
  const liste = document.getElementById('eintraege');
  const filter = document.querySelector('form.filter');
  if (liste && filter) {
    const params = new URLSearchParams(location.search);
    ['q', 'land', 'region', 'stadt'].forEach((k) => { if (params.has(k) && filter.elements[k]) filter.elements[k].value = params.get(k); });
    if (params.has('art')) {
      const r = [...filter.querySelectorAll('input[name="art"]')].find((x) => x.value === params.get('art'));
      if (r) r.checked = true;
    }
    const zaehler = document.querySelector('[data-zaehler]');
    const leer = document.querySelector('[data-leer]');
    const zeilen = [...liste.children];
    const anwenden = (adresse) => {
      const f = new FormData(filter);
      const q = String(f.get('q') || '').trim().toLowerCase();
      const art = String(f.get('art') || '');
      const land = String(f.get('land') || '');
      const region = String(f.get('region') || '');
      const stadt = String(f.get('stadt') || '');
      let n = 0;
      zeilen.forEach((z) => {
        const ok = (!q || z.dataset.such.includes(q)) && (!art || z.dataset.art === art) && (!land || z.dataset.land === land)
          && (!region || z.dataset.region === region) && (!stadt || z.dataset.stadt === stadt);
        z.hidden = !ok;
        if (ok) n += 1;
      });
      zaehler.textContent = `${n} ${n === 1 ? 'Eintrag' : 'Einträge'}`;
      leer.hidden = n > 0;
      if (adresse) {
        const p = new URLSearchParams();
        for (const [k, v] of f) if (v) p.set(k, String(v));
        history.replaceState(null, '', p.toString() ? `?${p}` : location.pathname);
      }
    };
    filter.addEventListener('change', () => anwenden(true));
    filter.addEventListener('input', () => anwenden(true));
    filter.addEventListener('submit', (e) => { e.preventDefault(); anwenden(true); });
    anwenden(false);
  }

  // Buchung: Zusammenfassung folgt der Auswahl
  const buchung = document.querySelector('form.buchung');
  if (buchung) {
    const zf = (k) => buchung.querySelector(`[data-zf="${k}"]`);
    const sync = () => {
      const platz = buchung.querySelector('input[name="platz"]:checked');
      const tage = Number((buchung.querySelector('input[name="laufzeit"]:checked') || {}).value || 14);
      const start = buchung.querySelector('input[name="start"]:checked');
      if (platz) zf('platz').textContent = buchung.querySelector(`label[for="${platz.id}"] .wahl-name`).textContent;
      if (!start) return;
      const s = new Date(`${start.value}T12:00:00`);
      const ende = new Date(s); ende.setDate(s.getDate() + tage - 1);
      zf('zeit').textContent = `${lang(s)} bis ${lang(ende)}`;
      buchung.querySelectorAll('.kalender td').forEach((td) => {
        const i = td.querySelector('input');
        if (!i || i.disabled) return;
        const d = new Date(`${i.value}T12:00:00`);
        td.classList.toggle('gewaehlt', d >= s && d <= ende);
        td.classList.toggle('frei', !(d >= s && d <= ende));
      });
    };
    buchung.addEventListener('change', sync);
    sync();
  }

  // Formulare ohne Anschluss: prüfen, nichts vortäuschen
  document.querySelectorAll('form[data-endpoint]').forEach((form) => {
    const meldung = form.querySelector('[data-meldung]');
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      let erstes = null;
      form.querySelectorAll('input, select, textarea').forEach((el) => {
        if (el.name === 'website' || el.type === 'radio') return;
        const ok = el.checkValidity();
        if (ok) el.removeAttribute('aria-invalid'); else el.setAttribute('aria-invalid', 'true');
        if (!ok && !erstes) erstes = el;
      });
      const pflichtRadio = [...form.querySelectorAll('input[type="radio"][required]')];
      if (!erstes && pflichtRadio.length && !pflichtRadio.some((r) => r.checked)) erstes = pflichtRadio[0];
      if (erstes) {
        if (meldung) meldung.textContent = 'Bitte füllen Sie die markierten Pflichtfelder aus.';
        erstes.focus();
        return;
      }
      if (!form.dataset.endpoint && meldung) meldung.textContent = 'Nichts wurde gesendet: Dieses Formular ist in der Probe noch nicht angeschlossen.';
    });
  });
})();
