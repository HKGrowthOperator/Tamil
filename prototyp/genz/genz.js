/* Tamil.de Probeseite: Teilen, Link kopieren, Reels erst nach Einwilligung, Stories als gesehen markieren. */
(() => {
  const toast = document.querySelector(".hinweis-toast");
  let toastZeit;
  const melden = (text) => {
    if (!toast) return;
    toast.textContent = text;
    toast.classList.add("da");
    clearTimeout(toastZeit);
    toastZeit = setTimeout(() => toast.classList.remove("da"), 2600);
  };

  const kopieren = async () => {
    try {
      await navigator.clipboard.writeText(location.href);
      melden("Link kopiert");
    } catch {
      melden("Kopieren ging nicht. Bitte die Adresse oben nehmen.");
    }
  };

  document.querySelectorAll("[data-kopieren]").forEach((b) => b.addEventListener("click", kopieren));
  document.querySelectorAll("[data-teilen]").forEach((b) =>
    b.addEventListener("click", async () => {
      if (navigator.share) {
        try {
          await navigator.share({ title: document.title, url: location.href });
          return;
        } catch (e) {
          if (e && e.name === "AbortError") return; // selbst abgebrochen
        }
      }
      kopieren(); // kein Teilen-Dialog verfügbar: Link kopieren
    })
  );
  const text = encodeURIComponent(`${document.title} ${location.href}`);
  document.querySelectorAll("[data-whatsapp]").forEach((a) => (a.href = `https://wa.me/?text=${text}`));

  // Reels: kein Drittanbieter-Code, bevor jemand zustimmt
  const box = document.querySelector(".einwilligung");
  let gewaehlt = null;
  const schliessen = () => {
    box.hidden = true;
    gewaehlt?.focus();
  };
  document.querySelectorAll(".reel").forEach((r) =>
    r.addEventListener("click", () => {
      if (!box) return;
      gewaehlt = r;
      box.querySelector("[data-reel-titel]").textContent = r.dataset.titel || "";
      box.hidden = false;
      box.querySelector("[data-laden]").focus();
    })
  );
  box?.querySelector("[data-laden]").addEventListener("click", () => {
    schliessen();
    melden("Probeseite: Hier startet später das Video.");
  });
  box?.querySelector("[data-abbrechen]").addEventListener("click", schliessen);
  box?.addEventListener("keydown", (e) => e.key === "Escape" && schliessen());

  // Probeseite: Ziele, die es erst auf der fertigen Website gibt
  document.querySelectorAll("[data-probe]").forEach((a) =>
    a.addEventListener("click", (e) => {
      e.preventDefault();
      melden(a.dataset.probe);
    })
  );

  document.querySelectorAll(".stories a").forEach((a) =>
    a.addEventListener("click", () => a.closest("li").classList.add("gesehen"))
  );
})();
