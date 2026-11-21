"""Gemeinsame Test-Einstellungen: kein DNS im Test (net.check_url löst jeden Host auf eine öffentliche Adresse auf);
Abrufe ohne Proxy gehen über `requests` statt über die Session mit Verbindungsprüfung, damit Fakes für requests.get greifen."""

import pytest
import requests

from news_radar import net


@pytest.fixture(autouse=True)
def _kein_dns(monkeypatch):
    monkeypatch.setattr(net, "_resolve", lambda host: ["93.184.216.34"])
    monkeypatch.setattr(net, "_safe_session", lambda: requests)
