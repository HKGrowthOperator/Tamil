"""PDF-Text lesen – läuft als eigener Kindprozess (nachtrag.pdf_lesen), nie im Web-Worker.

  python -I news_radar/pdf_kind.py <startseite>   (PDF-Bytes auf stdin)  →  {"text": …, "titel": …} | {"fehler": …}

Das Kind bekommt nur die Bytes und die Startseite: kein Netz, keine Datenbank, keine Importe aus dem Paket. Der
Elternprozess setzt ein hartes Zeitlimit; hier gilt zusätzlich eine Speichergrenze (RLIMIT_AS), je Seite höchstens
INHALT_MAX entpackte Bytes Inhaltsstrom, zusammen höchstens GESAMT_MAX, und jeder Inhaltsstrom wird nur einmal gelesen
(eine Datei, deren 40 Seiten alle denselben riesigen Strom referenzieren, kostet so nur eine Seite).
"""

from __future__ import annotations

import json
import logging
import re
import sys
import zlib

SPEICHER_MAX = 300 * 1024 * 1024  # je Kind; höchstens nachtrag.PDF_PARALLEL Kinder zugleich
SEITEN_MAX = 40
INHALT_MAX = 2_000_000  # entpackte Bytes Inhaltsstrom je Seite
GESAMT_MAX = 8_000_000  # entpackte Bytes Inhaltsstrom je Datei
TEXT_MAX = 20000


class Unlesbar(ValueError):
    """Die Datei ist nicht lesbar; der Text ist der Grund für den Bericht."""


def begrenzen(speicher: int = SPEICHER_MAX) -> None:
    try:
        import resource
    except ImportError:  # nicht überall vorhanden (Windows): dann nur das Zeitlimit des Elternprozesses
        return
    try:
        resource.setrlimit(resource.RLIMIT_AS, (speicher, speicher))
    except (ValueError, OSError):
        pass


def _trennung(m: re.Match) -> str:
    # „Bundes-\namt“ → „Bundesamt“; vor einem Großbuchstaben bleibt der Bindestrich („Sri-\nLanka“ → „Sri-Lanka“)
    return m.group(1) + ("" if m.group(2).islower() else "-") + m.group(2)


def seite_text(roh: str) -> str:
    t = (roh or "").replace("­", "").replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"(\w)-[ \t]*\n[ \t]*(\w)", _trennung, t)
    absaetze = (re.sub(r"\s+", " ", a).strip() for a in re.split(r"\n[ \t]*\n", t))
    return "\n\n".join(a for a in absaetze if a)


def _entpackt(strom) -> int:
    """Entpackte Größe eines Inhaltsstroms, höchstens bis INHALT_MAX + 1 entpackt (nie den ganzen Strom)."""
    roh = getattr(strom, "_data", b"") or b""
    filt = strom.get("/Filter")
    filt = list(filt) if isinstance(filt, list) else ([filt] if filt else [])
    if not filt:
        return len(roh)
    if [str(f) for f in filt] == ["/FlateDecode"] and not strom.get("/DecodeParms"):
        try:
            return len(zlib.decompressobj().decompress(roh, INHALT_MAX + 1))
        except zlib.error:
            return 0  # kaputter Strom: pypdf liest ihn leer
    return len(roh) * 4  # andere Filter: grob geschätzt, das harte Limit greift ohnehin


def _stroeme(seite) -> list[tuple[tuple | None, object]]:
    """[(Kennung des Objekts oder None, Strom)] der Inhaltsströme einer Seite, ohne sie zu entpacken."""
    roh = dict.get(seite, "/Contents")  # unaufgelöst: die Objekt-Kennung zeigt geteilte Ströme
    if roh is None:
        return []
    obj = roh.get_object()
    eintraege = list(obj) if isinstance(obj, list) else [roh]  # ArrayObject ist eine Liste unaufgelöster Einträge
    out = []
    for e in eintraege:
        kennung = (e.idnum, e.generation) if hasattr(e, "idnum") else None
        out.append((kennung, e.get_object()))
    return out


def lesen(daten: bytes, ab_seite: int = 1) -> tuple[str, str]:
    from io import BytesIO

    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(daten))
        if reader.is_encrypted:
            try:  # nur Rechte-Schutz ohne Kennwort lässt sich öffnen
                offen = reader.decrypt("")
            except Exception:  # noqa: BLE001
                offen = 0
            if not offen:
                raise Unlesbar("PDF nicht lesbar (verschlüsselt)")
        anzahl = len(reader.pages)
        if ab_seite > anzahl:
            raise Unlesbar(f"PDF nicht lesbar: keine Seite {ab_seite} (hat {anzahl})")
        teile, laenge, gesamt, gelesen = [], 0, 0, set()
        for i in range(ab_seite - 1, min(anzahl, ab_seite - 1 + SEITEN_MAX)):
            seite = reader.pages[i]
            stroeme = _stroeme(seite)
            schluessel = {k for k, _ in stroeme if k is not None}
            if schluessel and schluessel <= gelesen:
                continue  # derselbe Inhaltsstrom wie eine schon gelesene Seite
            gelesen |= schluessel
            groesse = sum(_entpackt(s) for _, s in stroeme)
            if groesse > INHALT_MAX:
                continue  # zu großer Inhaltsstrom: Seite überspringen
            gesamt += groesse
            if gesamt > GESAMT_MAX:
                break
            t = seite_text(seite.extract_text() or "")
            if t:
                teile.append(t)
                laenge += len(t) + 2
            if laenge >= TEXT_MAX:
                break
        try:
            titel = re.sub(r"\s+", " ", str((reader.metadata or {}).get("/Title") or "")).strip()[:300]
        except Exception:  # noqa: BLE001 – kaputte Metadaten: ohne Titel
            titel = ""
    except Unlesbar:
        raise
    except MemoryError:
        raise Unlesbar("PDF zu aufwendig") from None
    except Exception:  # noqa: BLE001 – kaputte Datei (auch Schleifen im Seitenbaum)
        raise Unlesbar("PDF nicht lesbar") from None
    return "\n\n".join(teile)[:TEXT_MAX], titel


def main(argv: list[str]) -> int:
    begrenzen()
    logging.disable(logging.WARNING)  # pypdf-Warnungen (je Objekt eine Zeile) gar nicht erst schreiben
    try:
        ab_seite = max(1, int(argv[1])) if len(argv) > 1 else 1
        text, titel = lesen(sys.stdin.buffer.read(), ab_seite)
        out = {"text": text, "titel": titel}
    except Unlesbar as exc:
        out = {"fehler": str(exc)}
    except MemoryError:
        out = {"fehler": "PDF zu aufwendig"}
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
