# Regelwerk Social (Instagram, Facebook, WhatsApp-Entwurf)

**Fassung 1 vom 13.11.2026.** Grundlage: Festlegung F4 (`docs/vertrag/festlegung-social.md`), bestätigt von Luis am
13.11.2026 mit allen Vorschlägen (`docs/abnahme/2026-11-13-auftrag-luis.md`). **Live erst nach der einmaligen Freigabe
dieser Fassung durch KBS** (Vertrag B2, §8 Abs. 1) und mit den Konten von KBS; bis dahin Trockenmodus.

Jeder Social-Beitrag speichert die Fassung, nach der er geprüft wurde (`regel_fassung`). Eine Änderung an diesem
Regelwerk ist eine neue Fassung mit Datum; ändern darf es nur die Rolle `admin`, die Änderung steht im Protokoll.

## Regeln

Ein Beitrag geht nur automatisch hinaus, wenn **jede** Regel erfüllt ist. Ist eine Regel verletzt oder unklar, steht
er im Cockpit unter „von Hand entscheiden“ mit der verletzten Regel als Grund.

| Nr. | Regel | Prüfung |
|---|---|---|
| R1 | Rubrik | alle acht Rubriken; „Nachrichten“ nur, wenn der Beitrag nicht als heikel markiert ist |
| R2 | Heikle Themen | Politik, Justiz, Unglück, Tod, Medizin gehen nie automatisch (Markierung `sensibel` der Story oder Rubrik/Schlagwort aus der Liste) |
| R3 | Alter | Beitrag höchstens 48 Stunden seit Veröffentlichung auf tamil.de; Termine nur, wenn sie in der Zukunft liegen |
| R4 | Bild | nur mit Recht zur Nutzung in sozialen Netzen (Umfang `social` im Lizenz-Datensatz, `docs/spezifikation/bilder-und-lizenzen.md`); sonst die Bildkarte „Grafik: Tamil.de“ |
| R5 | Menge | höchstens sechs Beiträge je Kanal und Tag, mindestens 60 Minuten Abstand |
| R6 | Ruhezeit | zwischen 22 und 7 Uhr (Europe/Berlin) wird nichts veröffentlicht; Wartendes geht ab 7 Uhr in der Reihenfolge hinaus |
| R7 | Dubletten | jeder Beitrag höchstens einmal je Kanal (eindeutig `wp_post_id` + `kanal`); Korrekturen am Artikel lösen nichts erneut aus |
| R8 | Kennzeichnung | Bilder aus der KI tragen den Hinweis wie auf der Website, im Bild und im Text |
| R9 | Herkunft | der übernommene Altbestand (vor dem Start des Moduls veröffentlicht) löst nie etwas aus |

## Ablauf

1. Erkennen neuer Beiträge und Termine auf tamil.de (auch von Hand angelegte).
2. Regelprüfung R1–R9, Ergebnis je Regel mit Grund gespeichert (`regelpruefung`).
3. Vorbereiten: Text aus Titel und Vorspann, Hashtags je Rubrik (liefert KBS), Verweis auf tamil.de; Bild 1080 × 1350
   (Foto mit schmaler Logo-Leiste, sonst Bildkarte).
4. Karenz zehn Minuten: im Cockpit ändern oder stoppen.
5. Veröffentlichen: zuerst Instagram, danach derselbe Inhalt auf der Facebook-Seite als Foto mit Text.
6. WhatsApp: Entwurf (Text, Link, Bild) im Cockpit mit „Kopieren“, „Bild herunterladen“, „als gepostet markieren“;
   gepostet wird von Hand.

## Was nie automatisch geschieht

Antworten auf Kommentare oder Nachrichten; Storys, Reels, Karussells, Video; bezahlte Reichweite; andere Netzwerke;
Posten in WhatsApp über inoffizielle Dienste; Wiederholen nach einem Abbruch ohne Abgleich mit den letzten Beiträgen
des Kontos. Der Stopp-Schalter je Kanal (`instagram`, `facebook`, `whatsapp`) und der globale Stopp wirken sofort,
auch während der Karenz.

## Freigabe durch KBS

| Fassung | Freigegeben von | Datum | Beleg |
|---|---|---|---|
| 1 | (steht aus) | | |
