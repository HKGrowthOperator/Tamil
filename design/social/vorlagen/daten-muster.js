// MUSTER-Daten für die Kartenvorlagen (Vorschlag, nicht freigegeben).
// Echter Beitrag vom Testsystem (REST: /wp-json/wp/v2/posts/2716, Bild /wp-json/wp/v2/media/2717), Stand 19.11.2026.
// Die Automatik ersetzt dieses Objekt (z. B. per Playwright addInitScript: window.KARTE = {...}).
window.KARTE = window.KARTE || {
  rubrik: "Events",
  titel: "Deepavali 2026: Lichterfest in Berlin, Bayern und Düsseldorf",
  // Kurzfassung für Story und Facebook (≤ 60 Zeichen); sonst wird der Titel genommen
  kurztitel: "Deepavali 2026: Lichterfest in Berlin, Bayern und Düsseldorf",
  bild: "../bilder/deepavali-2026-ganesha-tempel-berlin.jpg",
  bild_alt: "Der Sri-Ganesha-Hindutempel in der Berliner Hasenheide, aufgenommen im Juni 2026",
  nachweis: "Foto: 18quirl08 / Wikimedia Commons, CC BY-SA 4.0",
  fokus: "57% 40%",           // Bildausschnitt (object-position), je Beitrag einstellbar
  link_text: "tamil.de",
  // Karussell: Folien zwischen Titel und Schluss (aus dem Beitragstext, nicht erfunden)
  folien: [
    {
      titel: "Das Lichterfest",
      text: [
        "Am Sonntag, 8. November 2026, war Deepavali. Der Name heißt ungefähr „Reihe von Lichtern“.",
        "In vielen Häusern stehen Diyas, kleine Öllampen aus Ton, auf Fensterbänken und vor den Eingängen."
      ]
    },
    {
      titel: "Hier wurde gefeiert",
      liste: [
        ["Berlin", "Sri Ganesha Hindu Temple: Lichterfest mit Lakshmi Pooja"],
        ["München", "Sivaalayam-Tempel und Sri-Pillaiyar-Tempel"],
        ["Düsseldorf", "Tamil Sangam e.V., Sonntag, 15. November, 13.30 bis 22 Uhr"]
      ]
    }
  ]
};
