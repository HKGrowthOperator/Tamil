# Echte Inhalte und bekannte Platzhalter

| Quelle | Inhalt | Hinweise |
|---|---|---|
| `prototyp/content/posts.json` → `posts[]` | 63 echte Beiträge der alten tamil.de: `titel`, `slug`, `datum_original` (echtes Datum), `kategorien`, `standfirst`, `inhalt_html`, `bild.src` (`img/pNNNN.jpg`), `lesezeit` | Bilder in `prototyp/static/img/` (meist 900–1024 px breit, Querformat ~1,9:1 – starke Hochformat-Zuschnitte werden unscharf). Datum immer mit Jahr zeigen, viele Beiträge sind von 2019–2024 |
| `prototyp/content/events.json` | Kinoliste „Jailer 2“ (Oktober 2026), 6 Termine (Okt./Nov. 2026, inzwischen vorbei) | als Beispiel für Aufbau, nicht als „demnächst“ zeigen |
| `prototyp/content/site.json` | Navigation, Rubriken, Werbeplätze, Seiten-Texte | **Telefon, E-Mail und WhatsApp-Nummer sind Beispielwerte** – nie als echt zeigen. Echt: WhatsApp-Kanal `https://whatsapp.com/channel/0029VaFIN43KWEKo3BGoE13t` |
| Live-Radar `/api/bericht` (`python tools/radar_bericht.py`) | aktuelle Entwürfe: Diwali Basel (21.11.2026, Aula Lysbüchel, Basel Tamil Sangam), „Scene“ in 11 Kinos in DE, „Ramayana: Rise of a Legend“ in Gütersloh und Ravensburg | Stand ändert sich; vor Gebrauch abrufen |
| `prototyp/static/img/logo.png` | Logo 300×121, Rot + Dunkelgrau auf transparent | weiß einfärben per CSS-Filter möglich |

Regeln:
- Keine erfundenen Titel, Zahlen, Termine, Zitate, Bildnachweise oder Personen. Bildbeschreibungen (`alt`) nur, wenn
  das Bild angesehen wurde.
- Titel dürfen für die Anzeige gekürzt werden, Fakten bleiben.
- Reels/Videos: Es gibt noch keine festgelegten Kanäle; Platzhalter klar als solche kennzeichnen.
