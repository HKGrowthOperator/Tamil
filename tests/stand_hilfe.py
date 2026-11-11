"""Hilfe für Freigabe-Tests: den Stand lesen, den die Seite zeigt."""


def stand_aus(html: str, draft_id: int | None = None) -> str:
    """Stand des Entwurfs, den die Seite zeigt (verstecktes Feld im Freigabe-Formular)."""
    import re

    name = "stand" if draft_id is None else f"stand_{draft_id}"
    m = re.search(rf'name="{name}" value="(\d+)"', html)
    assert m, f"kein {name} auf der Seite"
    return m.group(1)


def stand_von(client, draft_id) -> str:
    """Stand, den die Entwurfsansicht zeigt (Formulare Freigeben/Direkt posten); ohne solches Formular „0“."""
    import re

    m = re.search(r'name="stand" value="(\d+)"', client.get(f"/entwurf/{draft_id}").get_data(as_text=True))
    return m.group(1) if m else "0"
