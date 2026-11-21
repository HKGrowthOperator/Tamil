# Plan: Baustein 5 – Instagram, Facebook, WhatsApp-Entwurf (F4) im Trockenmodus

## Nachtrag 13.11. (Abgleich mit `docs/spezifikation/integrationen.md` §8–10, `datenmodell.md` §15) – gilt vor
## den Punkten unten
- **Basis/Worktree:** alter Worktree ist weg. Neu: `git -C /home/user/Tamil worktree add
  /home/user/Tamil/.claude/worktrees/social -b feat/social-f4 5ffc4e1` (5ffc4e1 = 40d0560 + Spezifikation).
  Abgabe jetzt: Zwischenstand 22:00, Abgabe 22:30; Priorität 1–5, dann 6, 7; 8 nur, wenn Zeit bleibt.
- **Felder nach Spezifikation** (statt meiner Namen): `wp_post_id`, `quelle_typ`, `kanal` (UNIQUE mit
  `wp_post_id`), `status`, `regel_fassung`, `regelpruefung` (JSON je Regel erfüllt/verletzt + Grund), `text`,
  `hashtags`, `link`, `bild_datei`, `ki_hinweis`, `karenz_bis`, `geplant_fuer`, `veroeffentlicht_at`, `meta_id`,
  `meta_link`, `fehler`, `gepostet_von`, `gepostet_at`; zusätzlich (Auftrag): `quelle_fassung`, `asset_id`,
  `bild_social`, `container_id`, `versuche`, `erkannt_at`, `aktualisiert`, `entschieden_von`, `entscheidung`.
- **Status nach Spezifikation:** `erkannt → von_hand | vorbereitet → karenz → gestoppt | geplant → wird_gesendet →
  veroeffentlicht | unklar (→ veroeffentlicht | von_hand) | pausiert`; `von_hand → vorbereitet | verworfen`;
  WhatsApp `entwurf → gepostet`. Abweichungen: `trocken` als eigener Endstatus des Trockenlaufs (kein
  „veröffentlicht“ ohne Meta, R-02); `dublette` für zweiten WP-Beitrag mit gleicher `radar_uid`. Vergangene
  Termine und > 48 h gehen wie in der Spezifikation nach `von_hand` mit Grund (kein `uebersprungen`).
- **Variablen nach Spezifikation:** `SOCIAL_MODUS` (`trocken` Standard | `live`; ersetzt `RADAR_SOCIAL_LIVE`),
  `META_GRAPH_VERSION`, `META_IG_USER_ID`, `META_PAGE_ID`, `META_ZUGANG` (geheim), `WHATSAPP_KANAL_URL`;
  Funktionsschalter für den Dienst-Takt `RADAR_SOCIAL` bleibt (Echtbetrieb aus).
- **Bildadresse:** wie Spezifikation das Social-JPEG als Medium in WordPress hochladen (vorhandenes
  `upload_media`) und dessen öffentliche Adresse nutzen – **keine** öffentliche Cockpit-Route. Im Trockenmodus kein
  Upload (Platzhalter-Adresse), damit die Mediathek nicht vollläuft.
- **Meta-Ablauf ergänzt:** Container mit `alt_text`; Status-Abfrage höchstens je Lauf, nach 5 Min. ohne
  `FINISHED` bzw. `ERROR`/`EXPIRED` einmal neuer Container, dann `von_hand`; vor `media_publish`
  `content_publishing_limit` und Schalter prüfen. Facebook: `/{page-id}/photos` mit `url`, `caption`,
  `alt_text_custom`, `published=true`, Link über `GET /{post_id}?fields=permalink_url`. Fehlercodes: 190/368 und
  Kontosperre → Kanal pausiert (Schalter mit Grund); 4/17/32/613/80001/80002 → warten, kein Sofort-Wiederholen.
  Facebook scheitert nach Instagram → nur Facebook später erneut.
- **WhatsApp:** Stopp-Schalter `whatsapp` blendet den Entwurf aus; `WHATSAPP_KANAL_URL` im Entwurf, falls gesetzt.

Zeit: Start ca. 20:25 Berlin. Zwischenstand-Commit spätestens 22:00, Abgabe 22:20. Reihenfolge 1→8; was um 22:00
nicht steht, wird im Bericht als offen benannt.

## 0. Arbeitsbasis richtigstellen
- Der Worktree steht auf `2b09d51` (alter `main`-Merge), **nicht** auf `40d0560`. Da er sauber ist:
  `git -C <worktree> reset --hard 40d0560` auf dem Worktree-Branch `worktree-agent-a6536f6276b2a0a02`
  (kein Push, kein Merge). Danach `python -m pytest -q` als Ausgangsstand (Zahl festhalten).
- Kollisionsrisiko: parallele Aufträge (Einreichungen/Verzeichnis) könnten ebenfalls `V8` bzw. Szenario-Nummern
  belegen. Ich nehme `V8` (nächste freie auf 40d0560) und Szenarien **70–77** (59–66 belegt, Lücke 67–69 für
  Parallelarbeit); im Bericht als Abstimmungspunkt beim Zusammenführen nennen.

## 1. Datenmodell – `news_radar/workflow/schema.py`, neue `V8` (nichts Bestehendes ändern)
```
social_beitraege(id PK, kanal TEXT NOT NULL  -- instagram | facebook | whatsapp
  quelle_typ TEXT NOT NULL  -- beitrag | termin
  quelle_id TEXT NOT NULL   -- WordPress-ID
  quelle_link TEXT, quelle_datum TEXT, radar_uid TEXT, draft_id INTEGER, rubrik TEXT,
  fassung TEXT NOT NULL     -- Hash der Quelle beim Erkennen (Titel, Vorspann, Link, Termin, Bild)
  status TEXT NOT NULL      -- erkannt | regel_ok | von_hand | uebersprungen | karenz | sendet | abgleichen |
                            -- gesendet | trocken | fehler | gestoppt | verworfen | dublette | entwurf | gepostet_markiert
  regel_fassung TEXT, gruende TEXT (JSON-Liste), wartet_grund TEXT,
  text TEXT, bild_datei TEXT, asset_id INTEGER, bild_social INTEGER, bild_art TEXT (foto | karte), ki INTEGER,
  erkannt TEXT, karenz_bis TEXT, gesendet TEXT, aktualisiert TEXT NOT NULL,
  container_id TEXT, externe_id TEXT, link TEXT, fehler TEXT, versuche INTEGER DEFAULT 0,
  entschieden_von TEXT, entscheidung TEXT,
  UNIQUE(kanal, quelle_typ, quelle_id))
INDEX social_status(kanal, status, karenz_bis);  INDEX social_gesendet(kanal, gesendet)
social_stand(schluessel TEXT PK, wert TEXT, gesetzt TEXT)   -- Startmarke (Altbestand), letzter Abruf
```
Dublettenschutz: UNIQUE je Quelle+Kanal (strenger als Quelle+Fassung+Kanal, wie F4 verlangt: „Korrekturen lösen
nichts erneut aus“); die Fassung wird gespeichert. Zweiter WP-Beitrag mit gleicher `radar_uid` im selben Kanal →
Status `dublette`. Test zuerst in `tests/test_social.py` (Migration auf leerer und auf V7-Datenbank, `LATEST == 8`);
`tests/test_migration.py` ggf. auf neue Version anpassen.

## 2. Regelwerk – `news_radar/social/regelwerk.toml` + `social/regelwerk.py`
- TOML (Fassung = erste 12 Zeichen SHA-256 der Datei): `rubriken` (alle acht: news, kino, events, community,
  kueche, kultur, sport, entertainment), `heikel_begriffe` (Politik, Justiz, Gericht, Prozess, Abschiebung, Unglück,
  Unfall, Tod, gestorben, Trauer, Medizin, Krankheit …), `max_alter_stunden = 48`, `max_pro_tag = 6`,
  `abstand_minuten = 60`, `ruhe_von = 22`, `ruhe_bis = 7`, `karenz_minuten = 10`, `hashtags` je Rubrik
  (Platzhalter-Hashtags, als „Vorschlag – KBS liefert“ markiert), `ki_hinweis = "Symbolbild: KI-generiert"`.
- `pruefen(beitrag, jetzt) -> Pruefung(ok, gruende[{regel, text, art}])`; art `hart` → `uebersprungen`
  (nicht freigabefähig: Termin vergangen, älter als 48 h), art `hand` → `von_hand` (Rubrik nicht in Positivliste,
  heikel: Radar-Story `sensibel` oder Begriff in Titel/Kategorien/Schlagworten, „Nachrichten“ ohne
  Heikel-Kennzeichen = von Hand angelegt → unklar → Mensch). Bildrecht ist kein Ablehnungsgrund, sondern schaltet
  auf die Bildkarte. Menge/Abstand/Ruhezeit prüft `senden` (verschiebt nur, verwirft nie).
- Tests zuerst: je Regel ein Fall mit Grundtext; Fassung ändert sich mit dem Inhalt.

## 3. Vorbereiten – `social/vorbereiten.py`, Bild-Helfer in `news_radar/images.py` (nur neue Funktionen)
- Text: Titel, Leerzeile, Vorspann (`meta.standfirst`, sonst Excerpt ohne HTML), „Mehr auf tamil.de: <Link>“,
  feste Hashtags der Rubrik, bei KI-Bild der Hinweis. Kürzen auf 2200 Zeichen (Instagram-Grenze).
- Bild 1080 × 1350: `images.hochformat_foto(data, rubrik)` (ImageOps.fit + schmale Logo-Leiste „tamil.de“, F4
  Punkt 2 Vorschlag) und `images.hochformat_karte(titel, rubrik_label, rubrik)` („Grafik: Tamil.de“; nutzt
  `_font`, `_wrap`, `_kolam`, Farben). Foto nur, wenn lokales Radar-Bild (Entwurf über `drafts.wp_post_id` bzw.
  `radar_uid`) und Asset das Social-Recht trägt (`herkunft` in ki/pool/karte oder `umfang` enthält „Social“);
  sonst Karte. Kein Herunterladen fremder Bilder. Ablage `data/social/social-<sha256[:32]>.jpg` über
  `images._schreiben`.
- Öffentliche Bildadresse für Meta (`image_url`/`url` muss öffentlich sein): neue Route `/social/bild/<name>`
  ohne Anmeldung (nur Dateien `social-[0-9a-f]{32}.jpg` aus `data/social`), Basis `RADAR_SOCIAL_BILD_URL`
  (Standard `RADAR_WEB_URL + /social/bild`).
- Tests: Text (Hashtags, Link, KI-Hinweis), Bildmaße 1080×1350, Karte ohne Social-Recht.

## 4. Meta-Transport – `social/transport.py`, `social/fake.py`
- Schnittstelle `MetaTransport`: `ig_container(image_url, caption)`, `ig_container_status(id)`,
  `ig_veroeffentlichen(container_id)`, `ig_permalink(media_id)`, `ig_letzte()`, `fb_foto(url, caption)`,
  `fb_letzte()`. Fehlerklassen: `ZugangFehler` (Code 190/10/200 → Kanal pausieren über
  `schalter.setzen(kanal, True, wer="dienst:social", grund=…)`), `VoruebergehendFehler` (Netz vor dem
  entscheidenden Aufruf, Rate-Limit 4/17/32/613), `UnklarFehler` (Abbruch/Timeout beim veröffentlichenden Aufruf),
  `MetaFehler` (sonstige 4xx → `fehler`, kein Auto-Wiederholen).
- `GraphTransport`: requests-Session, fester Host `graph.facebook.com/{META_GRAPH_VERSION}` (Standard `v23.0`),
  Token nur im POST-Body/Query, nie geloggt; Timeout 30 s.
- `TrockenTransport`: kein Netz, liefert `trocken-…`-Kennungen; Status `trocken` (nicht `gesendet`, R-02).
  Live nur, wenn `RADAR_SOCIAL_LIVE` in (1, an, ja, true) **und** `META_ACCESS_TOKEN` + `META_IG_USER_ID` bzw.
  `META_FB_PAGE_ID` gesetzt; `--trocken` erzwingt trocken. In Tests nur `FakeMeta` (zählt Aufrufe, kann
  Zugang-abgelaufen, Timeout beim Veröffentlichen, IN_PROGRESS simulieren).
- Senden je Zeile (R-07): `UPDATE … SET status='sendet' WHERE id=? AND status='karenz' AND karenz_bis<=?`
  (rowcount=1 sonst nichts), dann Menge/Abstand/Ruhezeit, dann `schalter.pruefen(kanal)` unmittelbar vor dem
  Aufruf (bei Stopp zurück auf `karenz`, `wartet_grund`, Protokoll nur beim Wechsel des Grundes), dann
  Protokollzeile `social_senden` (notiz `live`/`trocken`, regel_fassung) und Aufruf. Instagram: Container
  anlegen (container_id sofort speichern) → Status abfragen (nicht FINISHED: bleibt, nächster Lauf fragt erneut,
  kein neuer Container) → `media_publish` → Permalink. Facebook danach: `/{page-id}/photos` mit `url` und
  `caption` → Link `https://www.facebook.com/<post_id>`.
- Unklarer Ausgang → `abgleichen`; nächster Lauf: letzte Beiträge des Kontos holen, Abgleich über den
  tamil.de-Link im Text → gefunden: `gesendet` mit Kennung/Link; nicht gefunden: `von_hand` „Ausgang unklar“. Nie
  blind wiederholen.
- Tests: Trocken ohne Netz; Live mit FakeMeta (beide Links + Kennung); Stopp „instagram“ → 0 IG-Aufrufe, Grund im
  Protokoll, Zeile wartet; Stopp in der Karenz; Timeout beim Publish → abgleichen → gefunden/nicht gefunden;
  Zugang abgelaufen → Schalter „instagram“ angehalten mit Grund; 6/Tag, 60 min, Ruhezeit 22–7 (Uhr injiziert).

## 5. Ablauf – `social/ablauf.py`, CLI, Dienst
- `erkennen(store, wp, jetzt)`: Startmarke beim ersten Lauf = jetzt (`social_stand`); Abfrage
  `GET /wp/v2/posts?status=publish&after=max(startmarke, jetzt-49h)&_embed=wp:term&_fields=…` über eine neue
  Lesemethode `WordPress.beitraege_seit(...)` im vorhandenen Core-Client (`news_radar/wordpress.py`). Nie
  auslösen: vor der Startmarke, `radar_uid` beginnt mit `alt-` (Importer-Kennung des Altbestands). Vorher
  `schalter.pruefen("alles")`. Termin = Beitrag mit `meta.event_datum`.
- Je neuem Beitrag Zeilen für instagram, facebook, whatsapp; IG/FB: prüfen → `karenz` (karenz_bis = jetzt+10 min)
  oder `von_hand`/`uebersprungen` mit Gründen; WhatsApp: `entwurf` (heikel/Regelbruch → trotzdem Entwurf, aber mit
  Hinweis, weil ein Mensch postet). Protokoll `social_erkannt`/`social_von_hand`.
- CLI in `__main__.py`: `python -m news_radar social status|pruefen|senden [--trocken]`
  (status: Zählung je Kanal/Status, Modus live/trocken, Regelwerk-Fassung, Startmarke).
- Dienst: `dienst.plan()` bekommt `social` (`social senden`, alle 180 s, Timeout 300, Kanäle
  instagram/facebook/whatsapp) nur mit Funktionsschalter `RADAR_SOCIAL=an` (Echtbetrieb aus, Grundlage Punkt 6).
  `schalter.HAELT_AN` Texte „(noch ohne Abnehmer)“ für die drei Kanäle anpassen; `test_zeitplan`/`test_dienst`
  ergänzen.

## 6. WhatsApp
- Zeile `entwurf` je Beitrag mit Text, Link, Bild; Aktion „als gepostet markieren“ (`gepostet_markiert`,
  `entschieden_von`, Zeit, Protokoll `whatsapp_gepostet` mit Person). Kein Sendeweg. Test zuerst.

## 7. Cockpit – `news_radar/web/social.py` (Blueprint), `templates/social.html`, `static/app.js`, `base.html`-Nav
- GET `/social`: Warteschlange (Karenz-Restzeit in Minuten, Wartegrund), „von Hand entscheiden“ mit Gründen,
  Fehler/abgleichen, Historie (Zeit, Kanal, Status, Link, Kennung, Regelwerk-Fassung), WhatsApp-Entwürfe.
- POST (CSRF wie bestehende Formulare, Recht `social` = REDAKTION in `rechte.py`): `/social/<id>/stoppen`
  (nur aus `karenz`, bedingtes UPDATE), `/aendern` (Text in der Karenz), `/freigeben` (von_hand → karenz, Grund
  Pflicht), `/verwerfen` (Grund Pflicht), `/gepostet` (WhatsApp). Jede Aktion ins Protokoll.
- „Kopieren“ über `data-kopieren` + Handler in `static/app.js` (Clipboard API), „Bild herunterladen“ als Link
  mit `download`. Nur vorhandenes `app.css`, keine Gestaltung, kein Inline-Script.
- Tests (Flask-Testclient): leser sieht, darf nicht stoppen (403); redaktion stoppt in der Karenz; gepostet
  markieren schreibt Person+Zeit; öffentliche Bildroute liefert nur gültige Namen.

## 8. Abnahme T1–T3 und Doku
- Szenarien 70–77 in `abnahme/szenarien.py` mit `nachher`-Hooks in `abnahme/__init__.py` (Fake-WP + FakeMeta,
  `_ohne_modell`, aufrufe 0): 70 Artikel → nach Karenz IG+FB mit Links/Kennung; 71 Termin Zukunft gesendet,
  Vergangenheit übersprungen; 72 heikel → von Hand; 73 Stopp Instagram → kein IG-Aufruf, Grund im Protokoll;
  74 WhatsApp gepostet markiert mit Person/Zeit; 75 Altbestand löst nichts aus; 76 Abbruch beim Veröffentlichen →
  Abgleich, kein Doppelpost; 77 Trockenmodus ohne Zugangsdaten → kein Transportaufruf, Status trocken.
- `docs/betrieb.md`: Variablennamen `RADAR_SOCIAL`, `RADAR_SOCIAL_LIVE`, `META_ACCESS_TOKEN`, `META_IG_USER_ID`,
  `META_FB_PAGE_ID`, `META_GRAPH_VERSION`, `RADAR_SOCIAL_BILD_URL` (keine Werte).
  `docs/vertrag/festlegung-social.md`: Stand „in Bau, Trockenmodus“ + angewandte Vorschläge.

## Prüfen und Abgabe
- `python -m pytest -q`, `python -m news_radar abnahme` (alle Szenarien), `tests/test_kein_mailversand.py`.
  Oberfläche: `tools/shots.mjs` nur, wenn Zeit bleibt (sonst im Bericht als nicht gelaufen).
- Commits `feat(news-radar): …` mit Trailern (Co-Authored-By / Claude-Session), etwa: Datenmodell+Regelwerk,
  Vorbereiten+Transport+Ablauf+CLI+Dienst (Zwischenstand ≤ 22:00), WhatsApp+Cockpit, Abnahme+Doku. Nicht pushen.
- Bericht: Commits, Stand je Punkt, Testzahlen, Abnahme, offene Punkte, Variablennamen, Auslegungen
  (Stopp Instagram hält nur Instagram; vergangene Termine = „übersprungen“; Status `trocken`; öffentliche Bildroute).
