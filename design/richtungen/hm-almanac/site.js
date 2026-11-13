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
