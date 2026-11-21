"""Einstellungen des Bausteins aus der Umgebung (nur Variablennamen in der Doku, Werte in Coolify).

  RADAR_SOCIAL        Funktionsschalter (Standard aus): nur dann plant der Dienst den Lauf und `social lauf` arbeitet
  RADAR_SOCIAL_LIVE   live statt Trockenmodus – wirkt nur zusammen mit allen drei Meta-Angaben
  META_ZUGANG         Token (geheim), META_IG_USER_ID, META_PAGE_ID, META_GRAPH_VERSION (Standard v23.0)
  WHATSAPP_KANAL_URL  Link zum WhatsApp-Kanal (kein Geheimnis), erscheint im Entwurf
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping

AN = ("1", "an", "ja", "true", "on", "yes")


def _an(wert: str | None) -> bool:
    return (wert or "").strip().lower() in AN


@dataclass(frozen=True)
class Konfig:
    aktiv: bool = False
    live_gewuenscht: bool = False
    graph_version: str = "v23.0"
    ig_user_id: str = ""
    page_id: str = ""
    zugang: str = field(default="", repr=False)
    whatsapp_url: str = ""

    @property
    def schluessel_vollstaendig(self) -> bool:
        return bool(self.zugang and self.ig_user_id and self.page_id)

    @property
    def live(self) -> bool:
        return self.live_gewuenscht and self.schluessel_vollstaendig

    @property
    def modus(self) -> str:
        return "live" if self.live else "trocken"


def laden(env: Mapping[str, str] | None = None) -> Konfig:
    env = os.environ if env is None else env
    return Konfig(
        aktiv=_an(env.get("RADAR_SOCIAL")),
        live_gewuenscht=_an(env.get("RADAR_SOCIAL_LIVE")),
        graph_version=(env.get("META_GRAPH_VERSION") or "v23.0").strip(),
        ig_user_id=(env.get("META_IG_USER_ID") or "").strip(),
        page_id=(env.get("META_PAGE_ID") or "").strip(),
        zugang=(env.get("META_ZUGANG") or "").strip(),
        whatsapp_url=(env.get("WHATSAPP_KANAL_URL") or "").strip(),
    )
