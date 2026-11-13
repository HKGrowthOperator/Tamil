"""Stopp-Schalter (Vertrag B1.1 und §8, Festlegung F0 Punkt 7): einer für alles und je einer pro Kanal.

Anhalten heißt: Es beginnt nichts Neues, und unmittelbar vor jedem Aufruf nach außen wird der Schalter noch einmal
geprüft (`pruefen`). Bearbeiten und Freigeben von Hand bleiben möglich; Freigegebenes wartet, bis der Schalter wieder
aus ist. Jede Änderung braucht eine Person, ein Stopp zusätzlich einen Grund, und steht im Protokoll
(editorial_actions). Ein Kanal ohne Zeile in der Tabelle läuft.

Heute fragen ab: `redaktion` (Scan, Job-Übernahme, Modellaufruf), `website` (Übertragung nach WordPress),
`instagram`, `facebook`, `whatsapp` (Baustein F4, `social/ablauf.py`). Die übrigen Kanäle sind schaltbar und sichtbar;
spätere Bausteine fragen `gestoppt()` ab. Der Budget-Stopp ist davon unabhängig.
"""

from __future__ import annotations

from .store import now_iso

KANAELE = ("alles", "redaktion", "website", "eingang", "verzeichnis", "instagram", "facebook", "whatsapp")
LABEL = {"alles": "Alles", "redaktion": "Redaktion", "website": "Website", "eingang": "Eingang",
         "verzeichnis": "Verzeichnis", "instagram": "Instagram", "facebook": "Facebook", "whatsapp": "WhatsApp"}
HAELT_AN = {
    "alles": "jede automatische Ausführung und jeden Aufruf nach außen",
    "redaktion": "Scan der Quellen und die Agenten-Redaktion (keine Job-Übernahme, kein Modellaufruf)",
    "website": "das Übertragen freigegebener Beiträge nach WordPress",
    "eingang": "Abholen und Vorbereiten von Einsendungen (noch ohne Abnehmer)",
    "verzeichnis": "die Prüfung von Verzeichniseinträgen (noch ohne Abnehmer)",
    "instagram": "Senden an Instagram, auch während der Karenz (Facebook wartet mit, weil Instagram zuerst geht)",
    "facebook": "Senden an die Facebook-Seite, auch während der Karenz",
    "whatsapp": "die WhatsApp-Entwürfe im Cockpit (ausgeblendet)",
}
GRUND_MAX = 300


class Gestoppt(Exception):
    """Ein Schalter hält diesen Kanal an; der Aufruf nach außen unterbleibt."""

    def __init__(self, kanal: str, sperre: dict):
        self.kanal = kanal
        self.sperre = sperre
        durch = "" if sperre["kanal"] == kanal else f" (über „{LABEL[sperre['kanal']]}“)"
        super().__init__(f"Kanal „{kanal}“ angehalten{durch}: {sperre.get('grund') or 'ohne Grund'}")


def _kanal(kanal: str) -> str:
    if kanal not in KANAELE:
        raise ValueError(f"Unbekannter Kanal „{kanal}“ – erlaubt: {', '.join(KANAELE)}")
    return kanal


def _zeilen(store) -> dict[str, dict]:
    return {r["kanal"]: dict(r) for r in store.db.execute("SELECT * FROM schalter")}


def stand(store) -> list[dict]:
    """Alle Kanäle in fester Reihenfolge: gestoppt, Grund, wer, seit (leer, solange nie geschaltet)."""
    zeilen = _zeilen(store)
    out = []
    for k in KANAELE:
        z = zeilen.get(k) or {}
        out.append({"kanal": k, "label": LABEL[k], "haelt_an": HAELT_AN[k], "gestoppt": bool(z.get("gestoppt")),
                    "grund": z.get("grund") or "", "wer": z.get("wer") or "", "seit": z.get("seit") or ""})
    return out


def aktive(store) -> list[dict]:
    """Nur die gestoppten Kanäle (für Banner und /gesund)."""
    return [z for z in stand(store) if z["gestoppt"]]


def sperre(store, kanal: str) -> dict | None:
    """Der Eintrag, der `kanal` anhält – der Kanal selbst oder „alles“ – sonst None."""
    _kanal(kanal)
    for k in ("alles", kanal) if kanal != "alles" else ("alles",):
        row = store.db.execute("SELECT * FROM schalter WHERE kanal = ? AND gestoppt = 1", (k,)).fetchone()
        if row is not None:
            return dict(row)
    return None


def gestoppt(store, kanal: str) -> bool:
    return sperre(store, kanal) is not None


def pruefen(store, kanal: str) -> None:
    """Unmittelbar vor einem Aufruf nach außen: wirft Gestoppt, wenn der Kanal (oder alles) angehalten ist."""
    s = sperre(store, kanal)
    if s is not None:
        raise Gestoppt(kanal, s)


def setzen(store, kanal: str, an: bool, *, wer: str, grund: str = "") -> dict:
    """Stopp setzen (`an=True`, Grund Pflicht) oder aufheben. Person ist immer Pflicht; jede Änderung wird
    protokolliert. Wer was darf, prüft das Cockpit (rechte.py); die Konsole gilt als Betrieb."""
    from .workflow import repo

    _kanal(kanal)
    wer = (wer or "").strip()
    grund = " ".join((grund or "").split())[:GRUND_MAX]
    if not wer:
        raise ValueError("Person fehlt: wer schaltet?")
    if an and not grund:
        raise ValueError("Grund fehlt: ein Stopp braucht einen Grund")
    jetzt = now_iso()
    store._write(
        "INSERT INTO schalter (kanal, gestoppt, grund, wer, seit) VALUES (?,?,?,?,?) ON CONFLICT(kanal) DO UPDATE SET "
        "gestoppt = excluded.gestoppt, grund = excluded.grund, wer = excluded.wer, seit = excluded.seit",
        (kanal, 1 if an else 0, grund, wer, jetzt),
    )
    repo.aktion(store, wer=wer, aktion="schalter_an" if an else "schalter_aus", gegenstand_typ="schalter",
                gegenstand_id=kanal, kanal=kanal, notiz=grund, ausloeser="person")
    store.event("schalter", kanal=kanal, gestoppt=an, grund=grund, von=wer)
    return {"kanal": kanal, "gestoppt": an, "grund": grund, "wer": wer, "seit": jetzt}


def haelt_an(store, kanaele: tuple[str, ...]) -> dict | None:
    """Für den Dienst: eine Aufgabe mit diesen Kanälen ruht, wenn alle davon angehalten sind (oder „alles“).
    Ohne Kanäle (z. B. Sicherung) ruht sie nie."""
    if not kanaele:
        return None
    sperren = [sperre(store, k) for k in kanaele]
    return sperren[0] if all(sperren) else None
