---
name: tamil-marke
description: Markenwissen für tamil.de – Zielgruppe, Register, Pflichten, echte Inhaltsquellen und die Verbotsliste aus vier abgelehnten Entwürfen. Vorgeladen in alle Gestaltungs- und Bau-Agents; lesen, bevor irgendetwas an Aussehen, Texten oder Inhalten von tamil.de entsteht.
user-invocable: false
---

# tamil.de – Markenwissen

## Wer liest

Tamilinnen und Tamilen in Deutschland, Österreich und der Schweiz: die junge, hier aufgewachsene Generation (Gen Z)
**und** Eltern und Großeltern, beide gleich wichtig. Gelesen wird am Handy, unterwegs oder abends, geteilt über
WhatsApp. Themen: tamilisches Kino in hiesigen Kinos, Feste, Konzerte, Tempel und Vereine, Community, Küche,
Nachrichten aus Sri Lanka und Tamil Nadu mit DACH-Bezug.

## Was gewollt ist (Stand 09.11.2026 abends, Luis)

- **Wie eine große Nachrichtenmarke:** klar, seriös, aufgeräumt, viele Geschichten auf einen Blick. Vorbilder sind
  Zeit Online, Spiegel, Tagesschau/BBC und Guardian/NZZ (`design/referenzen/news-marken.md`), nicht
  Streetwear-Magazine und nicht Social-Media-Apps.
- **Ruhig und hochwertig, überall.** Keine Riesenschrift, keine Effekte. Jung und alt gleich lesbar.
- **Rot nur als Akzent** (Logo, Links, kleine Marken). Heller, kühler Grund. Das Logo bleibt unverändert
  (`prototyp/static/img/logo.png`, Rot #B5282A + Grau).
- **Nur Deutsch** (Luis, 09.11.2026): keine tamilische Schrift als Gestaltungsmittel, auch nicht in Rubriken oder
  Überschriften. Kommt Tamil im Inhalt selbst vor (Namen, Zitate im Altbestand), wird es sauber gesetzt.
- **Erster Bildschirm:** ein klarer Aufmacher und weitere Geschichten. Das Eigene von tamil.de liegt im Inhalt (Kino
  mit Spielorten, Termine der Community, klare Dachzeilen), nicht in einem Effekt.
- **Abgelöst** sind die früheren Festlegungen „Hypebeast/Highsnobiety trifft Instagram/TikTok“, „Rot trägt die
  Seite“, „eine Geschichte als Cover“ und „laut im Kopf“. Der Wunsch des Auftraggebers „schöner, nicht so ein
  hingerotztes News-Magazin“ gilt weiter: Maßstab ist eine **große** Marke, kein Portal aus dem Baukasten.

## Register

- Website: Nachrichtenmagazin. **Vertrautheit vor Eigenwilligkeit.** Maßstab sind der Brief (`design/brief.md`) und
  seine harten Kriterien. Aus `impeccable` gelten nur die „Absolute bans“ und das Handwerk (Kontrast, Abstände,
  Hierarchie), nicht die Aufforderungen des brand-Registers zu Lautstärke und Risiko.
- Cockpit: **product** (Arbeitswerkzeug der Redaktion; Klarheit vor Ausdruck), gleiche Tokens.
- Zwei Tonlagen auf der Website: Nachrichten ruhig und belegt; Kino, Community und Kultur lebendiger durch Bilder
  und Themen, nicht durch lautere Gestaltung.

## Pflichten (nicht verhandelbar)

- WCAG 2.2 AA; Kontrast Text ≥ 4,5:1.
- Fließtext ≥ 18 px am Handy, Zeilenlänge ≤ 70 Zeichen; Tippflächen ≥ 44 × 44 px.
- Tamil-Text mit `lang="ta"` und einer Schrift, die Tamil sauber setzt.
- `prefers-reduced-motion` respektieren; keine Laufbänder, keine automatisch startenden Animationen.
- Kein seitliches Scrollen bei 390, 820, 1280 px (`node tools/shots.mjs`).
- Werbung klar als „Anzeige“ gekennzeichnet und dem Inhalt untergeordnet.
- Drittanbieter-Inhalte (Instagram, YouTube) erst nach Klick laden (DSGVO).

## Verbotsliste

Vier Entwürfe wurden abgelehnt. Bilder, Urteile und Gründe: [references/abgelehnt.md](references/abgelehnt.md).
**Vor jeder Gestaltung lesen.** Kurzfassung – nichts davon wiederholen:

- Nachtblau oder Dunkel als Grund, Gold/Gelb, Ornamente, Bollywood-Glitzer, Neon.
- Tamilische Wörter als Deko vor Überschriften; rotes Laufband/Ticker.
- Creme/Sand + Serifen-Fließtext + braungraue Tinte (wirkt „altbacken“).
- App-Vorlagen-Look: Pillen-Labels überall, runde Karten im Raster, Instagram-Story-Kreise, abgerundete
  Knopf-Reihen, rosa Hinterlegungskästen, „rote Platte über dem Bild“ als Aufmacher.
- Identische Kartenraster, Icons über Überschriften, nummerierte 01/02/03 ohne echte Reihenfolge.
- Laut und Baukasten (Runde 4): riesige rote Titelwörter; Schlagzeilen über 32 px am Handy oder 38 px am Desktop;
  verzerrte, extraschmale oder extrabreite Schriften; Schlagzeilen in Versalien; Stempel, Halbton, Schräglage;
  Rot als Fläche oder andere Vollfarbflächen; ein Cover mit nur einer Geschichte; „Signatur-Elemente“ als Effekt.
- Schriften aus der impeccable-Ausschlussliste (Inter, DM Sans, Space Grotesk, Fraunces, Playfair …) und die schon
  verbrannten Schriften dieses Projekts: Catamaran + Literata (Runde 2), Anek als Einzelfamilie (Runde 3),
  Schibsted Grotesk + Noto Serif Tamil + Fraunces (Runde 1), Sofia Sans Extra Condensed, Bricolage Grotesque,
  Archivo, Anybody und Atkinson Hyperlegible Next (Runde 4).

## Inhalte

Nur echte Inhalte, nichts erfinden. Quellen und bekannte Platzhalter: [references/inhalte.md](references/inhalte.md).
