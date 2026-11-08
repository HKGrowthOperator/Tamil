"""Kosten je Modellaufruf und das Budget (Tag/Monat) mit Reservierung vor dem Aufruf.

Preise in US-Dollar je 1 Mio. Tokens, geprüft am 08.11.2026 (Claude: Anthropic-Modellübersicht; Gemini: Preisliste
der Gemini-API). Thinking-Tokens zählen als Output. Bei serverseitigem Fallback ist `usage.iterations` die Quelle der
Wahrheit: jeder Versuch wird zum Preis des Modells abgerechnet, das ihn ausgeführt hat.

Budget: Vor jedem bezahlten Aufruf wird der ungünstigste Fall (Prompt + max_tokens) reserviert. Reservierungen und
schon angefallene Kosten zusammen dürfen das Tages- und Monatslimit nicht überschreiten; so können zwei parallele
Jobs das Budget nicht gemeinsam reißen. Nach dem Aufruf wird die Reservierung durch die echten Kosten ersetzt.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from zoneinfo import ZoneInfo

log = logging.getLogger(__name__)

PRICE_VERSION = "2026-11-08"
ZONE = ZoneInfo("Europe/Berlin")  # Budget-Tag und -Monat nach deutscher Zeit
RESERVIERUNG_VERFALL_MIN = 60  # Reservierungen abgestürzter Jobs zählen nach einer Stunde nicht mehr


@dataclass(frozen=True)
class Preis:
    input: float
    output: float
    cache_read: float
    schwelle: int | None = None  # Prompt-Tokens, ab denen der höhere Satz gilt (Haiku 5.5: 100K)
    input_hoch: float = 0.0
    output_hoch: float = 0.0


PREISE: dict[str, Preis] = {
    "claude-haiku-5-5": Preis(0.10, 0.50, 0.01, schwelle=100_000, input_hoch=0.50, output_hoch=2.50),
    "claude-sonnet-5-5": Preis(2.00, 10.00, 0.20),
    "claude-opus-5-5": Preis(4.00, 20.00, 0.20),
    "claude-fable-5-1": Preis(10.00, 50.00, 0.25),
    "claude-sonnet-5": Preis(2.00, 10.00, 0.20),
    "claude-opus-5": Preis(5.00, 25.00, 0.50),
}
CACHE_5M, CACHE_1H = 1.25, 2.0  # Aufschlag auf den Input-Preis beim Schreiben in den Cache

# Bild-KI: Preis je erzeugtem Bild nach Auflösung
BILD_PREISE: dict[str, dict[str, float]] = {
    "gemini-nano-banana-2.1": {"1K": 0.0336, "2K": 0.0504, "4K": 0.113},
    "gemini-3.1-flash-lite-image": {"1K": 0.0336},
    "gemini-3.1-flash-image": {"1K": 0.067, "2K": 0.101, "4K": 0.151},
    "gemini-3-pro-image": {"1K": 0.134, "2K": 0.134, "4K": 0.24},
}


class UnbekanntesModell(KeyError):
    pass


def preis(modell: str) -> Preis:
    """Preis zu einer Modell-ID; Suffixe wie „[1m]“ oder ein Datum werden ignoriert."""
    base = modell.split("[", 1)[0].strip()
    if base in PREISE:
        return PREISE[base]
    for key in sorted(PREISE, key=len, reverse=True):
        if base.startswith(key):
            return PREISE[key]
    raise UnbekanntesModell(modell)


@dataclass
class Tokens:
    input: int = 0
    output: int = 0
    cache_write_5m: int = 0
    cache_write_1h: int = 0
    cache_read: int = 0

    def __iadd__(self, other: "Tokens") -> "Tokens":
        for f in ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read"):
            setattr(self, f, getattr(self, f) + getattr(other, f))
        return self

    @property
    def prompt(self) -> int:
        return self.input + self.cache_write_5m + self.cache_write_1h + self.cache_read


def _get(obj: Any, name: str, default: Any = 0) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def tokens_aus(usage: Any) -> Tokens:
    """Tokens aus einem usage-Objekt (SDK-Objekt oder dict); Cache-Schreiben nach TTL aufgeteilt, wenn vorhanden."""
    creation = _get(usage, "cache_creation", None)
    cw_total = int(_get(usage, "cache_creation_input_tokens", 0) or 0)
    cw_5m = int(_get(creation, "ephemeral_5m_input_tokens", 0) or 0) if creation is not None else cw_total
    cw_1h = int(_get(creation, "ephemeral_1h_input_tokens", 0) or 0) if creation is not None else 0
    if creation is not None and cw_5m + cw_1h == 0:
        cw_5m = cw_total
    return Tokens(
        input=int(_get(usage, "input_tokens", 0) or 0),
        output=int(_get(usage, "output_tokens", 0) or 0),
        cache_write_5m=cw_5m,
        cache_write_1h=cw_1h,
        cache_read=int(_get(usage, "cache_read_input_tokens", 0) or 0),
    )


def kosten_tokens(modell: str, t: Tokens) -> float:
    p = preis(modell)
    inp, out = p.input, p.output
    cache_read = p.cache_read
    if p.schwelle and t.prompt > p.schwelle:
        inp, out = p.input_hoch, p.output_hoch
        cache_read = p.cache_read * (p.input_hoch / p.input)
    usd = (
        t.input * inp
        + t.output * out
        + t.cache_write_5m * inp * CACHE_5M
        + t.cache_write_1h * inp * CACHE_1H
        + t.cache_read * cache_read
    ) / 1_000_000
    return round(usd, 6)


@dataclass
class Abrechnung:
    modell: str  # Modell, das die Antwort geliefert hat
    tokens: Tokens
    usd: float
    iterationen: int


def abrechnen_usage(usage: Any, modell_antwort: str) -> Abrechnung:
    """Kosten einer Antwort. Mit `usage.iterations` (serverseitiger Fallback) zählt jeder Versuch einzeln."""
    iterations = _get(usage, "iterations", None) or []
    if not iterations:
        t = tokens_aus(usage)
        return Abrechnung(modell_antwort, t, kosten_tokens(modell_antwort, t), 1)
    gesamt, usd = Tokens(), 0.0
    for it in iterations:
        modell = _get(it, "model", "") or modell_antwort
        t = tokens_aus(it)
        gesamt += t
        usd += kosten_tokens(modell, t)
    return Abrechnung(modell_antwort, gesamt, round(usd, 6), len(iterations))


def bild_kosten(modell: str, groesse: str = "1K", anzahl: int = 1) -> float:
    tabelle = BILD_PREISE.get(modell) or BILD_PREISE["gemini-nano-banana-2.1"]
    return round(tabelle.get(groesse.upper(), max(tabelle.values())) * anzahl, 6)


def schaetzung(modell: str, prompt_zeichen: int, max_tokens: int) -> float:
    """Obergrenze für die Reservierung: Prompt (≈ 3 Zeichen je Token, eher zu viel) plus volle max_tokens als Output."""
    t = Tokens(input=prompt_zeichen // 3 + 50, output=max_tokens)
    return kosten_tokens(modell, t)


# ---- Budget -------------------------------------------------------------------------------------

class BudgetErschoepft(Exception):
    """Tages- oder Monatsbudget reicht für diesen Aufruf nicht – neue bezahlte Jobs warten."""


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def tag_start(now: datetime | None = None) -> datetime:
    local = (now or datetime.now(timezone.utc)).astimezone(ZONE)
    return local.replace(hour=0, minute=0, second=0, microsecond=0)


def monat_start(now: datetime | None = None) -> datetime:
    return tag_start(now).replace(day=1)


class Budget:
    """Tages- und Monatsbudget über agent_usage + budget_reservierungen (beide in der Radar-Datenbank)."""

    def __init__(self, store, tag_usd: float, monat_usd: float, warnung: float = 0.8,
                 melden: Callable[[str], None] | None = None, uhr: Callable[[], datetime] | None = None):
        self.store = store
        self.tag_usd = tag_usd
        self.monat_usd = monat_usd
        self.warnung = warnung
        self.melden = melden
        self.uhr = uhr or (lambda: datetime.now(timezone.utc))

    def _summen(self, now: datetime) -> tuple[float, float, float]:
        db = self.store.db
        tag = db.execute("SELECT COALESCE(SUM(kosten_usd), 0) FROM agent_usage WHERE ts >= ?",
                         (_iso(tag_start(now)),)).fetchone()[0]
        monat = db.execute("SELECT COALESCE(SUM(kosten_usd), 0) FROM agent_usage WHERE ts >= ?",
                           (_iso(monat_start(now)),)).fetchone()[0]
        frisch = _iso(now - timedelta(minutes=RESERVIERUNG_VERFALL_MIN))
        reserviert = db.execute("SELECT COALESCE(SUM(betrag), 0) FROM budget_reservierungen WHERE ts >= ?",
                                (frisch,)).fetchone()[0]
        return float(tag), float(monat), float(reserviert)

    def stand(self) -> dict:
        now = self.uhr()
        tag, monat, reserviert = self._summen(now)
        anteil = max(tag / self.tag_usd if self.tag_usd else 0, monat / self.monat_usd if self.monat_usd else 0)
        return {
            "tag_usd": round(tag, 4), "monat_usd": round(monat, 4), "reserviert_usd": round(reserviert, 4),
            "tag_limit": self.tag_usd, "monat_limit": self.monat_usd, "anteil": round(anteil, 3),
            "warnung": anteil >= self.warnung, "stopp": tag >= self.tag_usd or monat >= self.monat_usd,
        }

    def reservieren(self, betrag: float, rolle: str = "", story_id: int | None = None) -> int:
        """Reserviert `betrag` atomar; BudgetErschoepft, wenn Tag oder Monat dadurch überschritten würden."""
        now = self.uhr()
        with self.store.lock:
            tag, monat, reserviert = self._summen(now)
            if tag + reserviert + betrag > self.tag_usd or monat + reserviert + betrag > self.monat_usd:
                raise BudgetErschoepft(
                    f"Budget erreicht: heute ${tag:.2f} von ${self.tag_usd:.2f}, Monat ${monat:.2f} von ${self.monat_usd:.2f}"
                    f" (reserviert ${reserviert:.2f}, benötigt ${betrag:.2f})"
                )
            cur = self.store.db.execute(
                "INSERT INTO budget_reservierungen (ts, rolle, betrag, story_id) VALUES (?,?,?,?)",
                (_iso(now), rolle, betrag, story_id),
            )
            self.store.db.commit()
            return cur.lastrowid

    def freigeben(self, reservierung_id: int) -> None:
        with self.store.lock:
            self.store.db.execute("DELETE FROM budget_reservierungen WHERE id = ?", (reservierung_id,))
            self.store.db.commit()
        self.pruefe_warnung()

    def pruefe_warnung(self) -> None:
        """Einmal je Tag eine Warnung ab 80 % und einmal eine Meldung beim Stopp (Protokoll + Webhook)."""
        s = self.stand()
        heute = tag_start(self.uhr()).date().isoformat()
        for art, aktiv in (("budget_stopp", s["stopp"]), ("budget_warnung", s["warnung"])):
            if not aktiv:
                continue
            schon = any(e.get("tag") == heute for e in self.store.iter_log(event=art, limit=5))
            if schon:
                return
            self.store.event(art, tag=heute, **{k: s[k] for k in ("tag_usd", "monat_usd", "tag_limit", "monat_limit")})
            text = (f"News-Radar: Budget {'erreicht – neue bezahlte Jobs pausieren' if art == 'budget_stopp' else 'zu 80 % verbraucht'}"
                    f" (heute ${s['tag_usd']:.2f} von ${s['tag_limit']:.2f}, Monat ${s['monat_usd']:.2f} von ${s['monat_limit']:.2f})")
            log.warning(text)
            if self.melden:
                try:
                    self.melden(text)
                except Exception:  # noqa: BLE001 – eine Meldung darf den Lauf nie stoppen
                    log.debug("Budget-Meldung nicht zugestellt", exc_info=True)
            return
