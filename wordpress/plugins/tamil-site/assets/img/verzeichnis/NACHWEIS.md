# Symbolbilder des Verzeichnisses (Plugin tamil-site)

Ersatzbilder für Einträge ohne eigenes Bild (`includes/verzeichnis-ansicht.php`, `tamil_site_vz_ersatzbilder()`), je
Art eins (Business und Dienstleister teilen eins). Sie zeigen nie den Eintrag selbst: In der Liste steht „Symbolbild“
auf dem Bild, im Profil „Symbolbild, Foto: …“ mit Nachweis unter dem Bild, der Alternativtext beginnt mit „Symbolbild“, der
Nachweis steht im Fuß der Seite. Je Bild eine Datei in höchstens 1200 px Breite und eine in 600 px (WebP, ohne
Metadaten).

Nur Wikimedia Commons mit CC0, CC BY oder CC BY-SA; geladen am 17.11.2026 über die Commons-API (Vorschaubild 1280 px).

| Datei | Art | Motiv | Urheber | Lizenz | Dateiseite | Bearbeitung |
|---|---|---|---|---|---|---|
| `firma.webp`, `firma-600.webp` | Business, Dienstleister | Gewürze in Schalen an einem Marktstand (Carmel-Markt) | Markusurlaub | CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0 | https://commons.wikimedia.org/wiki/File:Carmel_Markt_Sep_2018.jpg | zugeschnitten: rechts unten (16 : 9, 820 × 461 von 1280 × 853), ohne die Personen am Stand |
| `verein.webp`, `verein-600.webp` | Verein | Gruppe tanzt Bharatanatyam auf einer Bühne | Mohd Zishan | CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0 | https://commons.wikimedia.org/wiki/File:A_Vibrant_Bharatanatyam_Group_Interpretation.jpg | verkleinert |
| `tempel.webp`, `tempel-600.webp` | Tempel | Sri-Mayurapathy-Murugan-Tempel, Blaschkoallee, Berlin-Britz | Fridolin freudenfett | CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0 | https://commons.wikimedia.org/wiki/File:Britz_Blaschkoallee_Sri-Mayurapathy-Murugan-Tempel.JPG | verkleinert |

Angezeigter Nachweis (wie in `verzeichnis-ansicht.php`, mit „Symbolbild,“ davor):

- Business, Dienstleister: „Foto: Markusurlaub / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten“
- Verein: „Foto: Mohd Zishan / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten“
- Tempel: „Foto: Fridolin freudenfett / Wikimedia Commons, CC BY-SA 4.0, zugeschnitten“

„zugeschnitten“ steht bei allen drei: Liste und Profil zeigen sie im Format 16 : 9 (`object-fit: cover`). Dateiseite
und Lizenz-URL stehen zusätzlich im Code (`quelle`, `lizenz`) und gehen mit der Aktion `tamil_site_bildnachweis` an
das Theme (verlinkte Nachweise).

Weitergabe unter gleichen Bedingungen (BY-SA): zugeschnittene und verkleinerte Dateien stehen unter derselben Lizenz wie
das Original.
