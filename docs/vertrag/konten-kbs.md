# Konten von KBS anlegen (laufende Kosten beim Kunden)

Stand 13.11.2026. Anlass: Luis am 13.11. „Wir dürfen jetzt selbst nicht die API-Kosten zahlen.“ Alle Dienste, die
laufend Geld kosten oder Zahlungen annehmen, laufen auf Konten von KBS (Vertrag §3 Abs. 2: Kosten bei Dritten nur mit
Freigabe). Wir legen nichts in unserem Namen an. Die Schlüssel trägt Luis in Coolify ein, nie in den Chat, nie ins
Repo. In dieser Datei stehen nur Variablen*namen*.

## Reihenfolge und was jedes Konto freischaltet

| Nr. | Dienst | Wer legt an | Was KBS tut | Variable in Coolify (App) | Schaltet frei | Ohne Konto |
|---|---|---|---|---|---|---|
| 1 | **Anthropic** (Claude) | KBS, Luis als Mitglied | Konto in der Konsole, Zahlungsmittel, **Ausgabenlimit** (Vorschlag: 50 $ im Monat zum Start), API-Schlüssel für „tamil-radar“ | `ANTHROPIC_API_KEY` (Radar „tamil.de“) | Agenten-Redaktion im Radar selbst: Recherche, Text, Faktencheck, zweite Prüfung, Eingang, Verzeichnis-Prüfung | Recherche nur im Agent-Modus aus einer Claude-Sitzung (läuft heute so) |
| 2 | **Stripe** | KBS | Konto als Unternehmen, Identitätsprüfung (einige Tage), Testmodus zuerst; Webhook auf `https://<website>/wp-json/tamil-site/v1/werbung/stripe` | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (Website „tamil-web“) | Werbebuchung mit Online-Zahlung | Buchung nur im Testsystem gegen den Fake |
| 3 | **Meta** (Instagram, Facebook) | KBS | Instagram-Professional-Konto, verknüpfte Facebook-Seite, Business-Portfolio, App bei Meta (Rolle Admin bei KBS), Systembenutzer mit Seiten-Token; falls verlangt Unternehmensverifizierung und App-Prüfung (Wochen) | `META_ZUGANG`, `META_IG_USER_ID`, `META_PAGE_ID` (Radar); danach `RADAR_SOCIAL=an`, `RADAR_SOCIAL_LIVE=an` | Instagram und Facebook automatisch nach Regelwerk | Trockenmodus: alles vorbereitet, nichts geht hinaus |
| 4 | **WhatsApp-Kanal** | KBS | Kanal anlegen, Adresse nennen | `WHATSAPP_KANAL_URL` (Radar, kein Geheimnis) | Link im Entwurf zum Kopieren | Entwurf ohne Kanal-Link |
| 5 | **Google AI Studio** (Gemini) | KBS, nur wenn KI-Symbolbilder gewollt sind | Projekt mit Abrechnung, Schlüssel, Budgetwarnung | `GEMINI_API_KEY` und `BILD_KI_FREIGABE=an` (Radar) | KI-Symbolbilder mit Kennzeichnung | Bildkarte „Grafik: Tamil.de“ oder lizenzierte Fotos |
| 6 | **Pexels** (optional) | KBS | kostenloses Konto, Schlüssel | `PEXELS_API_KEY` (Radar) | Stockfotos mit Lizenzdatensatz | Commons und Quellen-Register |

Dazu ohne Konto, aber Pflicht vor dem Echtbetrieb: `TAMIL_PROXY_ANZAHL=1` in der Website-App (sonst begrenzt die
Formular-Drossel die ganze Website gemeinsam).

## Was Luis danach tut

1. Schlüssel in Coolify eintragen (Variablen der jeweiligen App, als „secret“), App neu starten.
2. `python tools/coolify.py status` und `/gesund` prüfen; im Cockpit unter „Kosten“ das Limit sehen.
3. Tor B1 in `docs/abnahme/` festhalten (Datum, welche Konten, Limit).
4. Tor B2: die beiden Coolify-Tokens aus dem Chat widerrufen.

## Was bis dahin gilt

- Der Radar läuft ohne Modell (Kosten 0 $). Neue Storys warten auf Recherche; geschrieben wird im Agent-Modus aus
  einer Claude-Sitzung. Mit Schlüssel übernimmt der Radar das selbst, das Tages- und Monatsbudget im Radar
  (`RADAR_BUDGET_TAG_USD`, `RADAR_BUDGET_MONAT_USD`) begrenzt zusätzlich zum Limit bei Anthropic.
- Alle neuen Funktionen (Eingang, Verzeichnis, Werbung, Social) bleiben im Echtbetrieb aus, bis
  Auftragsverarbeitung und Rechtstexte da sind (`docs/vertrag/zuarbeit-kbs.md`).
