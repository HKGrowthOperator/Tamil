"""Rollen und Rechte im Cockpit (Vertrag B1.1, Festlegung F0 Punkt 8).

Die Karte ist Daten: je Recht eine Zeile mit den Rollen, die es haben. Jede ändernde Route trägt
`@recht_noetig("…")`; die Prüfung sitzt serverseitig (403 mit verständlicher Seite), die Oberfläche blendet Knöpfe
nur zusätzlich aus (`darf()` in den Templates). Lesen dürfen alle Angemeldeten. Der Notzugang aus WEB_USER ist admin.
Die Bearer-Zugänge (/api/bericht, /api/agent/*) prüfen ihr eigenes Token und gehören nicht hierher.

Stand der Karte: Vorschlag aus F0, noch nicht bestätigt – Änderungen hier, eine Zeile je Recht.
"""

from __future__ import annotations

from functools import wraps

from flask import abort, session

from ..workflow.repo import ROLLEN

ADMIN = ("admin",)
REDAKTION = ("admin", "redaktion")
ALLE = ROLLEN

RECHTE: dict[str, tuple[str, ...]] = {
    "bearbeiten": REDAKTION,          # Speichern, Neu schreiben, Bild, Zurücksetzen, Zurückstellen, Ablehnen
    "freigeben": REDAKTION,           # Freigeben (auch „erneut“ nach einem WordPress-Fehler)
    "veroeffentlichen": REDAKTION,    # Direkt posten, WordPress-Entwurf
    "story_verwerfen": REDAKTION,
    "quelle_ergaenzen": REDAKTION,
    "dossier": REDAKTION,
    "eingang_entscheiden": REDAKTION,  # Einsendungen übernehmen, erledigt/abgelehnt/Spam, Notiz (F1); sieht Kontaktdaten
    "anhalten": REDAKTION,            # jeden Kanal anhalten, auch „alles“
    "kanal_einschalten": REDAKTION,   # einen einzelnen Kanal wieder einschalten
    "alles_einschalten": ADMIN,       # den Schalter „alles“ wieder einschalten
    "job_erneut": ADMIN,              # „Erneut“ bei toten Jobs
    "benutzer": ADMIN,                # Benutzer ansehen, anlegen, sperren
    "export": ADMIN,                  # Protokoll und Kosten als Datei
    "social": REDAKTION,              # Social (F4): stoppen, Text ändern, von Hand entscheiden, WhatsApp gepostet
    "social_regelwerk": ADMIN,        # Regelwerk Social ändern (neue Fassung, Festlegung F4 Frage 4)
    "abmelden": ALLE,
}

NAMEN = {"bearbeiten": "Entwürfe bearbeiten", "freigeben": "Entwürfe freigeben", "veroeffentlichen": "veröffentlichen",
         "story_verwerfen": "Storys verwerfen", "quelle_ergaenzen": "Quellen ergänzen", "dossier": "Dossiers anstoßen",
         "eingang_entscheiden": "über Einsendungen entscheiden",
         "anhalten": "Kanäle anhalten", "kanal_einschalten": "Kanäle wieder einschalten",
         "alles_einschalten": "„Alles“ wieder einschalten", "job_erneut": "abgebrochene Jobs neu starten",
         "benutzer": "Benutzer verwalten", "export": "Daten exportieren",
         "social": "Social-Beiträge stoppen und entscheiden", "social_regelwerk": "das Social-Regelwerk ändern", "abmelden": "abmelden"}
TEXT_403 = ("Ihre Rolle „{rolle}“ darf nicht: {recht}. Ansehen geht weiter; wer Änderungen braucht, fragt "
            "jemanden mit Rolle admin.")


def rolle() -> str:
    return session.get("rolle") or ""


def darf(recht: str, rolle_: str | None = None) -> bool:
    """Hat die Rolle (Standard: die angemeldete) dieses Recht? Unbekannte Rechte sind ein Programmierfehler."""
    return (rolle_ if rolle_ is not None else rolle()) in RECHTE[recht]


def pruefe(recht: str) -> None:
    if not darf(recht):
        abort(403, description=TEXT_403.format(rolle=rolle() or "unbekannt", recht=NAMEN.get(recht, recht)))


def recht_noetig(recht: str):
    """Dekorator für Routen: ohne das Recht 403. Das Recht steht als `.recht` an der Funktion (Test der Karte)."""
    if recht not in RECHTE:
        raise KeyError(f"Recht „{recht}“ fehlt in der Karte")

    def deko(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            pruefe(recht)
            return fn(*args, **kwargs)

        wrapper.recht = recht
        return wrapper

    return deko
