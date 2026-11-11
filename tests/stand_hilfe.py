"""Hilfe für Freigabe-Tests: den Stand lesen, den die Seite zeigt."""


def stand_aus(html: str, draft_id: int | None = None) -> str:
    """Stand des Entwurfs, den die Seite zeigt (verstecktes Feld im Freigabe-Formular)."""
    import re

    name = "stand" if draft_id is None else f"stand_{draft_id}"
    m = re.search(rf'name="{name}" value="(\d+)"', html)
    assert m, f"kein {name} auf der Seite"
    return m.group(1)
