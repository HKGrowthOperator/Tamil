# Bildpool Tamil.de

Der Bildpool ist die Reserve für Beiträge ohne eigenes KI-Bild (Rohfassungen, Ausfall der Bild-KI, Beiträge ohne
brauchbares Motiv). Je Thema liegen mehrere Symbolbilder unter `data/bildpool/<thema>/`, der Radar nimmt das am
wenigsten genutzte. `python -m news_radar bildpool fuellen` erzeugt fehlende Bilder nach den Motiv-Prompts dieser Tabelle
(Regeln aus `bild.md` werden automatisch angehängt). Der Writer wählt je Beitrag ein `bild_thema` aus der Spalte Thema.

| Thema | Rubrik | Motiv (Englisch, wird als {motiv} eingesetzt) |
| --- | --- | --- |
| tempelfest | community | Exterior of a colorful South Indian style Hindu temple in a German town on a festival day, garlands of marigold and jasmine, oil lamps, visitors in saris seen from behind, soft overcast daylight |
| tempel-innen | community | Inside a Tamil Hindu temple hall in Europe: brass oil lamps, flower offerings, patterned floor, warm light, worshippers out of focus in the background |
| gemeindefest | community | A Tamil community hall in Germany decorated for a celebration, long tables with food, children's drawings on the wall, families seen from behind, friendly daylight |
| tamilschule | community | Weekend Tamil language school classroom in a European community center, exercise books with Tamil script blurred, backpacks, chalkboard without readable text, morning light |
| kolam | kultur | Close-up of hands drawing a white rice-flour kolam pattern on a doorstep at dawn, flower petals, warm low sunlight |
| pongal | kultur | Pongal celebration table with a clay pot boiling over, sugarcane, bananas, turmeric plants, decorated with kolam, bright festive morning |
| bharatanatyam | kultur | Bharatanatyam dancer silhouetted on a small stage, ankle bells, dramatic warm stage light, face not visible, dark background |
| parai-musik | kultur | Parai drums and hands of drummers during a cultural evening in Europe, motion blur, warm stage light, no faces |
| kino-saal | kino | Empty cinema auditorium with red seats and a glowing blank screen, cinematic blue and amber light, slight haze |
| kino-abend | kino | Friends arriving at a multiplex cinema entrance at night in a German city, seen from behind, neon reflections on wet pavement, no readable signs |
| filmplakat-wand | kino | Wall of blank movie posters in a cinema foyer, warm spotlights, people walking by in motion blur |
| konzert-buehne | entertainment | Large concert arena from the back of the crowd, hands raised, colorful stage lights and confetti, stage far away without readable screens |
| musik-studio | entertainment | Recording studio with a microphone, headphones and a keyboard, moody warm light, no people |
| sri-lanka-kueste | news | Coastline of northern Sri Lanka near Jaffna with palmyra palms, fishing boats and a lagoon at golden hour |
| sri-lanka-stadt | news | Street scene in Colombo with buses, tuk-tuks and colonial facades at dusk, people as silhouettes, no readable signs |
| tamil-nadu-tempel | news | Towering gopuram of a Tamil Nadu temple against a monsoon sky, pilgrims small in the frame, no faces |
| chennai-stadt | news | Marina Beach in Chennai at sunrise with fishing boats and joggers in the distance |
| politik-sri-lanka | news | Parliament-style white building with flagpoles without flags under a dramatic sky in Sri Lanka, empty forecourt |
| behoerde-deutschland | news | Facade of a German administrative building with glass doors and a bicycle rack, grey morning light, no signage |
| diaspora-stadt | news | Residential street in a German city with Tamil shop window with saris and spices, no readable text, autumn light |
| bahnhof-ankunft | news | Travelers with suitcases on a German railway platform seen from behind, soft evening light |
| rezept-kueche | kueche | Home kitchen counter with Sri Lankan Tamil ingredients: curry leaves, chilies, coconut, mustard seeds, a cast iron pan, warm daylight |
| gericht-tisch | kueche | Plate of Tamil food (dosa, sambar, chutneys) on a banana leaf on a wooden table, steam rising, overhead view |
| strassenkueche | kueche | Street food stall cooking kottu roti at night, sparks and steam, hands and spatulas in motion, no faces |
| cricket | sport | Cricket match on a village green in Europe, batsman from behind, overcast sky, green grass |
| fussball | sport | Amateur football pitch in Germany at dusk, players blurred in motion, floodlights, no club logos |
| event-halle | events | Event hall before the doors open: rows of chairs, stage with purple and gold lighting, balloons, no text |
| hochzeit | events | Tamil wedding hall decorated with flowers and brass lamps, bride and groom out of focus in the distance |
| buch-literatur | kultur | Stack of old books with Tamil script blurred, reading glasses and a cup of tea on a windowsill, soft daylight |
| tamil-sprache | kultur | Close-up of a child's hand writing Tamil letters in an exercise book, pencil, soft classroom light, letters not readable |
