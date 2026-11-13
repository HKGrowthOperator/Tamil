# Auftrag von Luis, 13.11.2026, 20:00 (Schicht bis 23:00)

Wortlaut (gekürzt, mündlich diktiert):

> „Das Design passt mir überhaupt gar nicht. Es sieht komplett generisch aus … generischer AI-Swap [Slop], geht gar
> nicht … egal ob es Dashboard ist oder die Webseite … der Kunde zahlt 28.000 € netto.“
>
> „Machst schon mal alle Sachen, die im Vertrag drinstehen, die Instagram-Anbindung, die Facebook-Anbindung, für
> WhatsApp die Anbindung, alle Anbindungen fertig. Definierst einmal die Bildgenerierung und woher du dir die Bilder
> ziehst. Wir brauchen auch immer Lizenzen … Wenn wir keine haben, müssen wir die anderen eingeben.“
>
> „Komplett einmal schon mal die Felder definieren, schon mal die ganze Software definieren. Es ist ja komplett
> wirklich ein Agent-Software-Projekt hinter der Webseite … viel mehr Struktur, viel mehr Definierung … nur bei
> tamil.de.“
>
> „Du sollst alles selber entscheiden, selbst definieren, selbst strukturieren, selbst ändern, ohne mich zu fragen …
> teile dir schon mal auch Aufgaben für die Nachtschicht.“

## Was daraus gilt

| Punkt | Festhaltung |
|---|---|
| Design | Urteil über `mix-ordnung` und `mix-feed` (und alle Runden davor): generisch, abgelehnt. Neuer Brief `design/brief-v3.md`; gestaltet wird mit Hallmark (von Luis bereitgestelltes Repo `HKGrowthOperator/hallmark`). Website **und** Cockpit werden neu gestaltet. |
| Tor G3 / Theme-Umbau | Luis ordnet die Neugestaltung von Website und Cockpit selbst an. Die Probeseiten entstehen jetzt; Umsetzung ins WordPress-Theme und ins Cockpit in der Nachtschicht. Abnahme durch den Auftraggeber bleibt Tor G4. |
| F4 Social | Gilt als **Ja zu F4** (Instagram, Facebook, WhatsApp-Entwurf) mit den Vorschlägen der Festlegung für offene Punkte. Gebaut wird im Trockenmodus; live erst mit Konten von KBS und der einmaligen Freigabe des Regelwerks durch KBS (Vertrag B2). |
| F0–F3 | „Alle Sachen, die im Vertrag drinstehen“: Bau auf dem Testsystem freigegeben, mit den Vorschlägen der Festlegungen; im Echtbetrieb bleiben neue Funktionen per Schalter aus, bis Auftragsverarbeitung und Rechtstexte vorliegen (`.claude/rules/vertrag.md`). |
| Bilder und Lizenzen | Jedes Bild braucht einen vollständigen Lizenz-Datensatz; fehlt er, trägt die Redaktion ihn im Cockpit ein, sonst keine Freigabe. Festgelegt in `docs/spezifikation/bilder-und-lizenzen.md`. |
| Spezifikation | `docs/spezifikation/` (System, Datenmodell mit allen Feldern, Agenten, Automationen, Bilder und Lizenzen, Integrationen). |
| Rückfragen | Keine. Entscheidungen trifft die Hauptsitzung und hält sie in `docs/entscheidungen.md` fest. |
