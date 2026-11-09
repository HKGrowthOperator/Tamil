# Entscheidungslog

Neueste oben. Format: Datum · Entscheidung · wer · warum. Was hier steht, gilt, bis ein neuerer Eintrag es ändert.
Eine Entscheidung nicht stillschweigend umkehren: neuen Eintrag schreiben.

## 09.11.2026

- **Design-Runde 1, Ergebnis der Kritik:** `zine`, `raster` und `feed` bestehen nach einer Überarbeitung mit je
  28/40 und kommen auf die Vergleichsseite. `plakatwand` erreicht 29/40, hat aber ein offenes P1 und wird nach der
  Regel „nur bestandene“ nicht gezeigt. Stand in `docs/abnahme/2026-11-09-G2.md`. · Ablauf `/design-runde`
- **Radar: keine Ländernamen in der Ausland-Liste.** „Sri Lanka“ oder „Indien“ stehen in fast jedem Bericht der
  Diaspora und würden echte Termine ohne bekannte Stadt verwerfen; in der Liste stehen nur Orte. Altersgrenze für
  Termin-Berichte: 30 Tage (`RADAR_EVENT_MAX_ALTER_TAGE`). · Code-Review, Hauptsitzung
- **Tor G1 bestätigt (vorläufig):** Brief `design/brief.md` mit den Vorbildern des Scouts; die Auswahl des
  Auftraggebers fließt bis G2 ein. Alle vier Richtungen gehen in die Skizzenrunde. · Luis · Die Runde soll nicht auf
  die Rückmeldung warten.
- **Nur Deutsch:** keine tamilische Schrift als Gestaltungsmittel. Die Richtung „Raster + Tamil-Schrift“ wird zu
  „Raster + große Schrift“. · Luis
- **Erster Bildschirm = die eine große Geschichte** (Cover); Kino und Events folgen als zweiter Abschnitt. Laut im
  Kopf, ruhig im Text. · Luis
- **Radar: nur Meldungen mit tamilischem Bezug.** Allgemeine Schweizer Meldungen (Unfall, Polizei, Wahl) erscheinen
  nicht; Quellen, die solche Meldungen liefern, verlangen ein Community-Stichwort. · Luis · Leser finden das auf
  Deutsch überall, und jede Recherche kostet.
- **Coolify-Zugang über DNS-Namen und sicheres Formular:** `coolify.hk-growthoperator.de`, enges Token statt
  Root-Token, Wert nie im Chat (Tor B2). · Luis
- **Projekt-Ordnung (Phase 7):** `CLAUDE.md`, `docs/`, `design/`, Bereichsregeln, 12 Skills, 10 Agents, 7 Commands, vier
  Abnahme-Tore. · Luis · Drei Designrunden sind am Ablauf gescheitert, das Wissen lag nur im Chat.
- **`prototyp/` bleibt Archiv**, Pfade unverändert; `prototyp/content/` bleibt Datenquelle. · Luis · Kein Umbau ohne
  Nutzen.
- **PR #1 wird jetzt gemergt** (Merge-Commit), PR #2 danach gegen `main`; PR #2 wird nach Tor G4 gemergt. · Luis
- **Adressen:** Der Radar bleibt unter `tamil.hk-growthoperator.de`, die Website läuft vorerst unter
  `tamil-web.167.233.76.202.sslip.io`. · Luis · Kein DNS-Aufwand jetzt.
- **Agents mit gemischten Modellen:** Opus für Gestalten, Bauen, Kritik, Code-Prüfung, Redaktion; Sonnet für
  Referenzsuche, Technik-QA, Migration. · Luis · Qualität dort, wo sie zählt, Limit schonen.
- **Kritik-Filter:** Der Auftraggeber sieht nur Richtungen mit mindestens 28/40 und bestandenem Slop-Test. · Luis
- **Abnahmen über Luis**, Referenzen aus Auftraggeber und Scout, Design und Website-Livegang parallel, alle vier
  Richtungen in die Skizzenrunde (Kollywood-Plakatwand, Diaspora-Zine, Raster + Tamil-Schrift, Vertikaler Feed). · Luis
- **Gen-Z-Probeseite abgelehnt** („Trash, komplett generisch“, aber „viel Potenzial, Luft nach oben“). · Auftraggeber
  über Luis · Siehe `.claude/skills/tamil-marke/references/abgelehnt.md`.
- **Redesign für Gen Z:** jung und alt gleich lesbar, Hypebeast/Highsnobiety und Instagram/TikTok als Richtung, Rot trägt
  die Seite, helles Grundbild. · Auftraggeber über Luis · Community-Magazin galt als „altbacken, hingerotzt“.
- **Keine Demo-Inhalte:** Der ganze echte Altbestand von tamil.de wird übernommen (Originaldatum, Slug, Bilder, Seiten,
  301-Weiterleitungen). · Luis
- **„Freigeben“ veröffentlicht sofort** (`WP_POST_STATUS=publish`). · Luis
- **Website als zweite Coolify-App** (WordPress mit SQLite, ein Container). · Luis
- **Agent-Modus übers Netz** (`/api/agent/export|import`, eigenes Token): wartende Storys schreibt eine Claude-Sitzung
  ohne API-Kosten. · Luis · Der Anthropic-Schlüssel fehlt noch.
- **Radar komplett in Coolify** (ein Container: Cockpit, Scan, Worker, Digest, Sicherung), gebaut von
  `claude/radar-multiagent`. · Luis · Statt systemd auf dem HK-Server.
- **Pilot:** 2 $ pro Tag und Monat, 5 Entwürfe pro Tag, keine KI-Bilder, 20 Quellen, Modelle je Rolle wie gesetzt. · Luis
- **Ausland-Filter:** Termine außerhalb von DE/AT/CH werden verworfen (Kanada, UK, Sri Lanka, Indien …). · Ergebnis des
  kostenlosen Pilot-Scans.
- **Root-Token nur für die Einrichtung**, danach widerrufen (Tor B2). · Luis

## 08.11.2026

- **Nachtlauf freigegeben:** Multi-Agenten-Redaktion nach dem Blueprint vom 19.10. ohne Rückfragen bauen. · Luis

## 20.10.2026

- **Blueprint umgesetzt:** Branch `claude/radar-multiagent` mit eigenem PR; Modelle je Rolle (Haiku: Signal, Cluster,
  Lektorat, SEO · Sonnet: Recherche, Faktencheck, Text · Opus: Dossier); keine Embeddings; 20 aktive Quellen;
  Bildreihenfolge Archiv → Quelle → Stock → Pool → KI → Karte. · Luis
- **Newsletter komplett entfernt** (Theme, Plugin, Prototyp, Doku). · Luis
- **Erster Entwurf (Nachtblau, Gold, Ornamente, Tamil-Wörter vor Überschriften) abgelehnt** als „Katastrophe“. ·
  Auftraggeber
