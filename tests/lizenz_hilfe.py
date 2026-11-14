"""Hilfe für Tests, die Freigabe oder Veröffentlichen prüfen, aber nicht die Lizenz: ein vollständiger Lizenz-Datensatz
(Bildkarte, Spezifikation Bilder 3.2) zum aktuellen Bild eines Entwurfs und ein gültiger Alt-Text.

Das Gate selbst wird nie gelockert; die Tests liefern nur die Angaben, die ein echter Entwurf auch hätte."""

from news_radar import lizenz
from news_radar.images import FeaturedImage


def lizenz_setzen(store, draft_id: int, settings=None, *, alt: str = "Grafik mit der Überschrift des Beitrags") -> None:
    row = store.get_draft(draft_id)
    if not row.get("bild_datei"):
        return
    daten = b""
    if settings is not None and (settings.bilder_dir / row["bild_datei"]).is_file():
        daten = (settings.bilder_dir / row["bild_datei"]).read_bytes()
    karte = FeaturedImage(daten, row["bild_datei"], "image/jpeg", lizenz.KARTE_CREDIT, "karte")
    felder = lizenz.datensatz(karte)
    if not daten:
        felder["sha256"] = "0" * 64  # Testentwurf ohne Datei: Prüfsumme als Platzhalter
    lizenz.anlegen(store, datei=row["bild_datei"], daten=daten, draft_id=draft_id, story_id=row.get("story_id"),
                   felder=felder)
    if lizenz.alt_fehler(row.get("bild_alt"), row.get("titel") or ""):
        store.update_draft(draft_id, bild_alt=alt)
