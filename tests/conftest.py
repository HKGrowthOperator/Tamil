"""Gemeinsame Test-Einstellungen: kein DNS im Test (net.check_url löst jeden Host auf eine öffentliche Adresse auf)."""

import pytest

from news_radar import net


@pytest.fixture(autouse=True)
def _kein_dns(monkeypatch):
    monkeypatch.setattr(net, "_resolve", lambda host: ["93.184.216.34"])
