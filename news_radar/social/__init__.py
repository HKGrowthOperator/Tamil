"""Baustein F4 (Vertrag B2, B3): Instagram, Facebook und WhatsApp-Entwurf.

Ablauf (docs/regeln-social.md, Festlegung F4, Spezifikation datenmodell.md §15):

  quelle.py      neue Beiträge und Termine auf der Website erkennen (nur lesend über /wp/v2/posts); Altbestand nie
  regelwerk.py   Regeln R1–R9 je Beitrag mit Grund; Fassung 1 aus regelwerk.toml, neuere Fassungen in der Datenbank
  bild.py        Bild 1080 × 1350: Beitragsbild mit Logo-Leiste (nur mit Umfang „social“) oder Bildkarte
  ablauf.py      erkennen → vorbereiten → Karenz → senden (zuerst Instagram, dann Facebook), Abgleich nach Abbruch
  transport.py   austauschbarer Weg zu Meta: Trocken (Standard, kein Aufruf) oder Graph API (live); fake.py für Tests
  aktionen.py    was die Redaktion im Cockpit tut (stoppen, Text ändern, freigeben, verwerfen, WhatsApp gepostet)
  konfig.py      Funktionsschalter RADAR_SOCIAL, Live nur mit RADAR_SOCIAL_LIVE und Schlüsseln

Status (Instagram, Facebook): von_hand · karenz · gestoppt · geplant · wird_gesendet · unklar · veroeffentlicht ·
trocken · pausiert · verworfen. WhatsApp: entwurf · gepostet. `trocken` ist der Endstand eines Trockenlaufs: alles
vorbereitet und die Nutzlast gespeichert, aber nichts an Meta geschickt (kein „veröffentlicht“ ohne Meta).
"""

META_KANAELE = ("instagram", "facebook")
KANAELE = ("instagram", "facebook", "whatsapp")
# Zustände, in denen eine Zeile noch hinausgehen kann (Facebook wartet, solange Instagram hier steht)
OFFEN = ("karenz", "geplant", "wird_gesendet", "unklar", "pausiert")
ERLEDIGT = ("veroeffentlicht", "trocken")
SYSTEM = "dienst:social"  # „wer“ im Protokoll für automatische Schritte
