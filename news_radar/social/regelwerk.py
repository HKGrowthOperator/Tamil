"""Regelwerk Social (docs/regeln-social.md): Fassungen laden und ändern, Regeln R1–R9 je Beitrag prüfen.

Fassung 1 steht in `regelwerk.toml`. Jede Änderung (nur Rolle admin, Cockpit) ist eine neue Fassung in der Tabelle
`social_regelwerk` mit Person und Zeit und einer Zeile im Protokoll. Jeder Social-Beitrag speichert die Fassung, nach
der er geprüft wurde.

Ergebnis je Regel: `erfuellt`, `verletzt` oder `unklar`, immer mit Grund. Automatisch geht ein Beitrag nur weiter,
wenn jede Regel erfüllt ist; sonst steht er unter „von Hand entscheiden“. R4 (Bild) entscheidet nur zwischen Foto und
Bildkarte, R5 und R6 (Menge, Ruhezeit) verschieben beim Senden, R7 sichert die Datenbank (eindeutig je Kanal).
"""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .quelle import Beitrag, umfang_menge

TZ = ZoneInfo("Europe/Berlin")
DATEI = Path(__file__).with_name("regelwerk.toml")
REGELN = {"R1": "Rubrik", "R2": "Heikle Themen", "R3": "Alter", "R4": "Bild", "R5": "Menge", "R6": "Ruhezeit",
          "R7": "Dubletten", "R8": "Kennzeichnung", "R9": "Herkunft"}
ZAHLEN = {"max_je_tag": (1, 50), "abstand_min": (0, 24 * 60), "ruhe_von": (0, 23), "ruhe_bis": (0, 23),
          "max_alter_stunden": (1, 24 * 14), "karenz_min": (0, 24 * 60)}


@dataclass(frozen=True)
class Regelwerk:
    fassung: str
    datum: str
    rubriken: tuple[str, ...]
    heikel: tuple[str, ...]
    max_alter_stunden: int
    max_je_tag: int
    abstand_min: int
    ruhe_von: int
    ruhe_bis: int
    karenz_min: int
    ki_hinweis: str
    hashtags: dict
    hashtags_platzhalter: bool
    von: str = ""
    freigegeben_von: str = ""
    freigegeben_at: str = ""

    def inhalt(self) -> dict:
        d = asdict(self)
        for k in ("fassung", "datum", "von", "freigegeben_von", "freigegeben_at"):
            d.pop(k)
        d["rubriken"], d["heikel"] = list(self.rubriken), list(self.heikel)
        return d


def _aus_dict(d: dict, *, fassung: str, datum: str, von: str = "", freigegeben_von: str = "",
              freigegeben_at: str = "") -> Regelwerk:
    return Regelwerk(
        fassung=str(fassung), datum=datum, rubriken=tuple(d["rubriken"]), heikel=tuple(d["heikel"]),
        max_alter_stunden=int(d["max_alter_stunden"]), max_je_tag=int(d["max_je_tag"]),
        abstand_min=int(d["abstand_min"]), ruhe_von=int(d["ruhe_von"]), ruhe_bis=int(d["ruhe_bis"]),
        karenz_min=int(d["karenz_min"]), ki_hinweis=str(d["ki_hinweis"]),
        hashtags={k: list(v) for k, v in dict(d["hashtags"]).items()},
        hashtags_platzhalter=bool(d.get("hashtags_platzhalter")), von=von, freigegeben_von=freigegeben_von or "",
        freigegeben_at=freigegeben_at or "")


def aus_datei(pfad: Path = DATEI) -> Regelwerk:
    d = tomllib.loads(pfad.read_text(encoding="utf-8"))
    return _aus_dict(d, fassung=str(d["fassung"]), datum=str(d.get("datum", "")), von="Datei")


def aktuell(store) -> Regelwerk:
    """Die neueste Fassung: aus der Datenbank, sonst Fassung 1 aus der Datei."""
    row = store.db.execute("SELECT * FROM social_regelwerk ORDER BY fassung DESC LIMIT 1").fetchone()
    if row is None:
        return aus_datei()
    return _aus_dict(json.loads(row["inhalt"]), fassung=str(row["fassung"]), datum=row["erstellt"][:10],
                     von=row["von"], freigegeben_von=row["freigegeben_von"], freigegeben_at=row["freigegeben_at"])


def speichern(store, aenderung: dict, *, wer: str) -> Regelwerk:
    """Neue Fassung aus der aktuellen plus `aenderung` (Zahlen, `heikel`, `hashtags`). Prüft Grenzen; ohne Person
    oder ohne Änderung entsteht keine Fassung. Die Freigabe durch KBS gilt für die neue Fassung nicht mehr."""
    from ..store import now_iso
    from ..workflow import repo

    wer = (wer or "").strip()
    if not wer:
        raise ValueError("Person fehlt")
    alt = aktuell(store)
    neu = alt.inhalt()
    for k, (lo, hi) in ZAHLEN.items():
        if k in aenderung and aenderung[k] not in (None, ""):
            try:
                n = int(aenderung[k])
            except (TypeError, ValueError):
                raise ValueError(f"{k}: keine ganze Zahl") from None
            if not lo <= n <= hi:
                raise ValueError(f"{k}: {n} liegt nicht zwischen {lo} und {hi}")
            neu[k] = n
    if "heikel" in aenderung:
        liste = [w.strip() for w in aenderung["heikel"] if w.strip()]
        if not liste:
            raise ValueError("Die Liste heikler Themen darf nicht leer sein")
        neu["heikel"] = liste
    if "hashtags" in aenderung:
        tags = dict(neu["hashtags"])
        for rubrik, liste in aenderung["hashtags"].items():
            if rubrik not in alt.rubriken:
                raise ValueError(f"Unbekannte Rubrik {rubrik}")
            tags[rubrik] = [t if t.startswith("#") else f"#{t}" for t in liste if t.strip()][:30]
        neu["hashtags"] = tags
        neu["hashtags_platzhalter"] = False if aenderung.get("hashtags_von_kbs") else neu["hashtags_platzhalter"]
    if neu == alt.inhalt():
        raise ValueError("Keine Änderung – keine neue Fassung")
    fassung = int(alt.fassung) + 1
    store._write("INSERT INTO social_regelwerk (fassung, inhalt, erstellt, von) VALUES (?,?,?,?)",
                 (fassung, json.dumps(neu, ensure_ascii=False), now_iso(), wer))
    geaendert = sorted(k for k in neu if neu[k] != alt.inhalt()[k])
    repo.aktion(store, wer=wer, aktion="social_regelwerk", gegenstand_typ="regelwerk", gegenstand_id=fassung,
                regel_fassung=str(fassung), notiz="geändert: " + ", ".join(geaendert), ausloeser="person")
    return aktuell(store)


def freigegeben(rw: Regelwerk) -> bool:
    """Live nur mit der einmaligen Freigabe dieser Fassung durch KBS (Vertrag §8 Abs. 1); eine neue Fassung hat keine."""
    return bool(rw.freigegeben_von and rw.freigegeben_at)


def freigabe_eintragen(store, *, wer: str, freigegeben_von: str, datum: str, beleg: str) -> Regelwerk:
    """Die Freigabe der aktuellen Fassung eintragen (Cockpit: nur admin). Person, Freigebende, Datum (JJJJ-MM-TT) und
    Beleg sind Pflicht; der Beleg steht im Protokoll. Einmalig je Fassung."""
    from ..store import now_iso
    from ..workflow import repo

    wer, von = (wer or "").strip(), " ".join((freigegeben_von or "").split())[:120]
    beleg = " ".join((beleg or "").split())[:250]
    if not (wer and von and beleg):
        raise ValueError("Person, Freigebende und Beleg sind Pflicht")
    try:
        tag = date.fromisoformat((datum or "").strip()).isoformat()
    except ValueError:
        raise ValueError("Datum der Freigabe als JJJJ-MM-TT") from None
    rw = aktuell(store)
    if freigegeben(rw):
        raise ValueError(f"Fassung {rw.fassung} ist schon freigegeben")
    with store.lock:
        store.db.execute("INSERT OR IGNORE INTO social_regelwerk (fassung, inhalt, erstellt, von) VALUES (?,?,?,?)",
                         (int(rw.fassung), json.dumps(rw.inhalt(), ensure_ascii=False), now_iso(), rw.von or "Datei"))
        cur = store.db.execute("UPDATE social_regelwerk SET freigegeben_von = ?, freigegeben_at = ? WHERE fassung = ? "
                               "AND freigegeben_von IS NULL", (von, tag, int(rw.fassung)))
        store.db.commit()
    if cur.rowcount != 1:
        raise ValueError(f"Fassung {rw.fassung} ist schon freigegeben")
    repo.aktion(store, wer=wer, aktion="social_regelwerk_freigabe", gegenstand_typ="regelwerk",
                gegenstand_id=rw.fassung, regel_fassung=rw.fassung, notiz=f"freigegeben von {von} am {tag}; Beleg: {beleg}",
                ausloeser="person")
    return aktuell(store)


# ---- Prüfung ------------------------------------------------------------------------------------

def _muster(eintrag: str) -> str:
    wort = re.escape(eintrag.rstrip("*"))
    return rf"(?<![\w]){wort}" + (r"\w*" if eintrag.endswith("*") else r"(?![\w])")


def heikel_treffer(b: Beitrag, rw: Regelwerk) -> str:
    texte = [b.titel, *b.rubriken, *b.schlagworte]
    for eintrag in rw.heikel:
        rx = re.compile(_muster(eintrag), re.IGNORECASE)
        for t in texte:
            m = rx.search(t or "")
            if m:
                return m.group(0)
    return ""


def _event_tag(wert: str) -> date | datetime | None:
    wert = (wert or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(wert[:19], fmt).replace(tzinfo=TZ)
        except ValueError:
            continue
    try:
        return date.fromisoformat(wert[:10])
    except ValueError:
        return None


def _r(ergebnis: str, grund: str) -> dict:
    return {"ergebnis": ergebnis, "grund": grund}


def bild_social(b: Beitrag) -> tuple[bool, str]:
    """R4: Foto nur mit Lizenz-Datensatz, dessen Umfang „social“ enthält, und vorhandener Datei."""
    if b.asset is None:
        return False, "kein Lizenz-Datensatz zum Beitragsbild – Bildkarte „Grafik: Tamil.de“"
    if "social" not in umfang_menge(b.asset.get("umfang")):
        return False, "Lizenz ohne Umfang „social“ – Bildkarte „Grafik: Tamil.de“"
    if b.bild_pfad is None:
        return False, "Bilddatei fehlt im Radar – Bildkarte „Grafik: Tamil.de“"
    return True, "Beitragsbild mit Recht für soziale Netze (Umfang „social“)"


def pruefe_alter(datum: datetime | None, quelle_typ: str, event_datum: str, rw: Regelwerk, jetzt: datetime) -> dict:
    """R3: höchstens `max_alter_stunden` seit der Veröffentlichung; Termine nur, solange sie in der Zukunft liegen.
    Gilt beim Erkennen und noch einmal unmittelbar vor dem Senden."""
    if datum is None:
        return _r("unklar", "Veröffentlichungszeit fehlt")
    alter = (jetzt - datum).total_seconds() / 3600
    if alter > rw.max_alter_stunden:
        return _r("verletzt", f"{alter:.0f} Stunden alt (höchstens {rw.max_alter_stunden})")
    if quelle_typ != "termin":
        return _r("erfuellt", f"{alter:.0f} Stunden alt")
    tag = _event_tag(event_datum)
    if tag is None:
        return _r("unklar", f"Termindatum „{event_datum}“ nicht lesbar")
    if (tag < jetzt) if isinstance(tag, datetime) else (tag < jetzt.astimezone(TZ).date()):
        return _r("verletzt", f"Termin {event_datum} liegt in der Vergangenheit – übersprungen")
    return _r("erfuellt", f"{alter:.0f} Stunden alt, Termin {event_datum} in der Zukunft")


def pruefen(b: Beitrag, rw: Regelwerk, jetzt: datetime) -> dict[str, dict]:
    p: dict[str, dict] = {}
    rubrik = next((r for r in b.rubriken if r in rw.rubriken), "")
    treffer = heikel_treffer(b, rw)
    heikel = b.sensibel or bool(treffer)
    # R1 Rubrik
    if not rubrik:
        p["R1"] = _r("unklar", f"keine der acht Rubriken ({', '.join(b.rubriken) or 'ohne Kategorie'})")
    elif rubrik == "news" and heikel:
        p["R1"] = _r("verletzt", "„Nachrichten“ nur, wenn der Beitrag nicht heikel ist")
    else:
        p["R1"] = _r("erfuellt", f"Rubrik {rubrik}")
    # R2 Heikle Themen
    if b.sensibel:
        p["R2"] = _r("verletzt", "Story ist als sensibel markiert")
    elif treffer:
        p["R2"] = _r("verletzt", f"heikles Thema „{treffer}“ in Titel, Rubrik oder Schlagwort")
    else:
        p["R2"] = _r("erfuellt", "kein heikles Thema erkannt")
    p["R3"] = pruefe_alter(b.datum, b.quelle_typ, b.event_datum, rw, jetzt)
    # R4 Bild: entscheidet nur zwischen Foto und Bildkarte
    p["R4"] = _r("erfuellt", bild_social(b)[1])
    p["R5"] = _r("erfuellt", f"höchstens {rw.max_je_tag} je Kanal und Tag, {rw.abstand_min} Minuten Abstand – "
                             "beim Senden eingehalten")
    p["R6"] = _r("erfuellt", f"Ruhezeit {rw.ruhe_von} bis {rw.ruhe_bis} Uhr – beim Senden eingehalten")
    p["R7"] = _r("erfuellt", "höchstens einmal je Beitrag und Kanal (Korrekturen lösen nichts aus)")
    ki = bild_social(b)[0] and b.bild_ki
    p["R8"] = _r("erfuellt", f"KI-Bild: „{rw.ki_hinweis}“ im Text und im Bild" if ki else "kein KI-Bild")
    p["R9"] = _r("erfuellt", "nach dem Start des Moduls veröffentlicht, nicht aus der Übernahme")
    return p


def automatisch(pruefung: dict[str, dict]) -> bool:
    return all(r["ergebnis"] == "erfuellt" for r in pruefung.values())


def gruende(pruefung: dict[str, dict]) -> list[str]:
    """Verletzte oder unklare Regeln als „R2 Heikle Themen: …“ in der Reihenfolge R1–R9."""
    return [f"{k} {REGELN[k]}: {v['grund']}" for k, v in sorted(pruefung.items(), key=lambda kv: int(kv[0][1:]))
            if v["ergebnis"] != "erfuellt"]


def rubrik(b: Beitrag, rw: Regelwerk) -> str:
    return next((r for r in b.rubriken if r in rw.rubriken), "")


def in_ruhezeit(t: datetime, rw: Regelwerk) -> bool:
    h = t.astimezone(TZ).hour
    if rw.ruhe_von == rw.ruhe_bis:
        return False
    if rw.ruhe_von > rw.ruhe_bis:
        return h >= rw.ruhe_von or h < rw.ruhe_bis
    return rw.ruhe_von <= h < rw.ruhe_bis


def ende_ruhezeit(t: datetime, rw: Regelwerk) -> datetime:
    """Der nächste Zeitpunkt `ruhe_bis` Uhr (Europe/Berlin) nach t."""
    lokal = t.astimezone(TZ)
    ziel = lokal.replace(hour=rw.ruhe_bis, minute=0, second=0, microsecond=0)
    if ziel <= lokal:
        ziel = (lokal + timedelta(days=1)).replace(hour=rw.ruhe_bis, minute=0, second=0, microsecond=0)
    return ziel


