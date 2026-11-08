"""Datenmodelle der Redaktion v2: Belege (Dokumente, Claims), Evidenzpaket und die Ergebnisse der Rollen.

Die Ergebnis-Modelle sind bewusst ohne Zahlengrenzen (ge/le) definiert: strukturierte Ausgaben der API unterstützen
nicht jede JSON-Schema-Einschränkung. Grenzen und Querverweise prüft der Code danach (validate_refs, Gate).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..writer import Draft

ClaimArt = Literal["was", "wer", "wann", "wo", "zahl", "preis", "ticket", "zitat", "hintergrund", "sonstiges"]
Support = Literal["bestaetigt", "einzelquelle", "unbestaetigt", "widerspruch", "offen"]
KERN_ARTEN = ("was", "wer", "wann", "wo")
EVENT_KERN_ARTEN = ("wann", "wo", "preis", "ticket")


class SourceDocument(BaseModel):
    doc_key: str
    url: str = ""
    publisher: str = ""
    quelle: str = ""  # Name im Quellen-Register
    published_at: str = ""
    retrieved_at: str = ""
    language: str = "de"
    rights: str = "unbekannt"  # frei | zitat | lizenz | unbekannt
    primaer: bool = False
    art: str = "zusammenfassung"  # volltext | zusammenfassung | hinweis | daten | redaktion
    titel: str = ""
    text: str = ""


class Claim(BaseModel):
    id: str = Field(description="C1, C2 …")
    aussage: str = Field(description="Eine überprüfbare Aussage auf Deutsch, ohne Wertung")
    art: ClaimArt
    kern: bool = Field(description="true für die Kernaussagen (was/wer/wann/wo; bei Events Datum/Ort/Preis/Ticket)")
    quellen: list[str] = Field(description="doc_keys der Dokumente, in denen die Aussage steht (Q1, Q2 …)")
    fundstelle: str = Field(description="kurzes wörtliches Stück aus dem Dokument, max. 160 Zeichen")
    sicherheit: float = Field(description="0 bis 1: wie eindeutig steht das so in den Quellen")
    support: Support = "offen"


class Widerspruch(BaseModel):
    claim_ids: list[str]
    beschreibung: str


class EvidencePackage(BaseModel):
    story_id: int
    typ: str
    titel: str
    dokumente: list[SourceDocument]
    claims: list[Claim] = []


# ---- Ergebnisse der Rollen (Schema für output_config.format) -----------------------------------

class SignalBewertung(BaseModel):
    nr: int
    relevanz: int = Field(description="1-10 für die tamilische Community im DACH-Raum")
    land: str = Field(description="DE, AT, CH oder leer")
    grund: str = Field(description="ein Satz")
    risiko: Literal["keins", "sensibel", "fragwuerdig"]


class SignalErgebnis(BaseModel):
    bewertungen: list[SignalBewertung]


class ClusterEntscheidung(BaseModel):
    nr: int
    gleiche_story: bool
    grund: str


class ClusterErgebnis(BaseModel):
    entscheidungen: list[ClusterEntscheidung]


class RechercheErgebnis(BaseModel):
    claims: list[Claim]
    widersprueche: list[Widerspruch]
    fehlende_angaben: list[str] = Field(description="Was für einen vollständigen Beitrag fehlt (z. B. Uhrzeit, Ort)")


class Beleg(BaseModel):
    absatz: int = Field(description="Nummer des <p>-Absatzes im inhalt_html, ab 1")
    claim_ids: list[str]


class TextErgebnis(Draft):
    belege: list[Beleg] = Field(description="Zu jedem Absatz die Claims, auf denen er beruht")


class SatzUrteil(BaseModel):
    nr: int
    satz: str
    urteil: Literal["gedeckt", "ungedeckt", "widerspruch", "kein_fakt"]
    claim_ids: list[str]
    fundstelle: str = Field(description="Beleg aus dem Dokument oder leer")
    kern: bool = Field(description="true, wenn der Satz eine Kernaussage trägt (was/wer/wann/wo, Datum, Ort, Preis)")


class FaktencheckErgebnis(BaseModel):
    saetze: list[SatzUrteil]


class LektoratHinweis(BaseModel):
    art: Literal["sprache", "stil", "verstaendlichkeit", "ton", "fakten"]
    stelle: str
    vorschlag: str


class LektoratErgebnis(BaseModel):
    hinweise: list[LektoratHinweis]


class SeoErgebnis(BaseModel):
    fokus_keyword: str
    seo_titel: str = Field(description="max. 60 Zeichen")
    meta_beschreibung: str = Field(description="120-155 Zeichen")
    bild_alt: str = Field(description="Alt-Text auf Deutsch, beschreibt das Bild, max. 125 Zeichen")


def validate_refs(claims: list[Claim], doc_keys: set[str]) -> tuple[list[Claim], list[str]]:
    """Claims ohne gültige Quelle fliegen raus; unbekannte doc_keys werden entfernt. (behalten, verworfen-Gründe)"""
    behalten, verworfen = [], []
    seen: set[str] = set()
    for c in claims:
        quellen = [q for q in c.quellen if q in doc_keys]
        if not quellen:
            verworfen.append(f"{c.id}: keine gültige Quelle ({', '.join(c.quellen) or '–'})")
            continue
        if c.id in seen:
            verworfen.append(f"{c.id}: doppelte ID")
            continue
        seen.add(c.id)
        behalten.append(c.model_copy(update={"quellen": quellen, "fundstelle": c.fundstelle[:200],
                                             "sicherheit": min(1.0, max(0.0, c.sicherheit))}))
    return behalten, verworfen
