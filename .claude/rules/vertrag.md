---
paths:
  - "docs/vertrag/**"
  - "wordpress/plugins/**"
  - "wordpress/docker/**"
  - "news_radar/**"
  - "tests/**"
---

# Regeln: Vertrag (Anlage 1, tamil.de)

Maßstab: `docs/vertrag/leistungen.md`. Einzelheiten je Baustein: `docs/vertrag/festlegung-<baustein>.md`.

- **Erst festlegen, dann bauen.** Ein Baustein wird gebaut, wenn Luis seine Festlegung bestätigt hat
  (`docs/abnahme/*-F*-<baustein>.md`; für F0–F4 gilt das Gesamt-Ja `docs/abnahme/2026-11-13-auftrag-luis.md`). Was nicht in der Festlegung steht, wird nicht gebaut.
- **Kein Mailversand.** Kein `wp_mail`, kein `smtplib`, kein Maildienst. Rückmeldungen stehen auf der Website oder im
  Cockpit. `tests/test_kein_mailversand.py` sichert das ab.
- **Automatisch läuft nur, was in einer freigegebenen Regel steht.** Unklares geht an einen Menschen. Jede
  automatische Ausführung prüft unmittelbar vor dem Aufruf nach außen den Stopp-Schalter und schreibt eine Zeile ins
  Protokoll (wer oder welcher Agent, was, Kanal, Fassung der Regel).
- **Nur offizielle Schnittstellen**, immer über einen austauschbaren Transport; in Tests der Fake, nie das Netz.
- **Website und Cockpit bleiben getrennt abnehmbar.** WordPress hält Öffentliches, Kunden und Geld; das Cockpit hält
  Agenten, Prüfung, Freigabe, Zeitplan, Stopp und Protokoll. Der Radar holt bei WordPress ab, nie umgekehrt.
- **Nichts Erfundenes.** Agenten verwenden nur, was in der Einsendung oder in den Belegen steht.
- **Personendaten:** nur nötige Felder, Einwilligung mit Fassung, Löschfrist. Keine Namen oder Kontaktdaten in
  Protokollen, Logs oder Testdaten aus dem Echtbetrieb.
- **Neue Funktionen im Echtbetrieb aus**, bis Auftragsverarbeitung und Rechtstexte vorliegen (Funktionsschalter).
- **Werbung:** „aktiv“ entscheidet genau eine Funktion (bezahlt und geprüft und nicht pausiert und im Zeitraum).
  Zahlungsdaten bleiben beim Anbieter; ein Webhook gilt nur mit gültiger Signatur.
- **Vertragsdaten** (Preise, Zahlungsplan, Steuer- und Bankdaten, die Vertragsdatei) gehören nicht ins Repo.
