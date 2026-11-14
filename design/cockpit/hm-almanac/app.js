// Kopieren des WhatsApp-Entwurfs. Ohne Skript bleibt der Text markierbar; der Knopf meldet nur, was wirklich geschah.
document.querySelectorAll('[data-kopiere]').forEach((knopf) => {
  const ziel = document.getElementById(knopf.dataset.kopiere);
  const hilfe = document.getElementById(knopf.getAttribute('aria-describedby'));
  knopf.addEventListener('click', () => {
    if (!navigator.clipboard || !ziel) { if (hilfe) hilfe.textContent = 'Kopieren geht hier nicht. Bitte den Text markieren und kopieren.'; return; }
    navigator.clipboard.writeText(ziel.innerText.trim())
      .then(() => { if (hilfe) hilfe.textContent = 'Text in der Zwischenablage. Jetzt im WhatsApp-Kanal einfügen.'; })
      .catch(() => { if (hilfe) hilfe.textContent = 'Kopieren wurde nicht erlaubt. Bitte den Text markieren und kopieren.'; });
  });
});
