"""Die einzige Stelle, die Sprachmodelle aufruft: Claude.call() – mit Budget-Reservierung und Messung je Aufruf.

Jeder Aufruf landet in agent_usage: Rolle, angefragtes und tatsächliches Modell, Prompt-Version (Hash des
System-Prompts), Tokens inkl. Cache, Kosten, Status, Latenz und request_id. Auch Ablehnungen, abgeschnittene
Antworten und API-Fehler werden protokolliert (die Tokens, soweit die API sie meldet).
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ValidationError

from .. import schalter
from ..config import Settings
from ..store import now_iso
from . import costs

log = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

FALLBACK_BETA = "server-side-fallback-2026-07-01"
# Effort und Ausgabegrenze je Rolle: billige Rollen knapp, Text und Dossier mit Luft für Thinking
EFFORT = {"signal": "low", "cluster": "low", "lektorat": "low", "seo": "low", "recherche": "medium",
          "faktencheck": "medium", "text": "medium", "dossier": "high", "pruefer": "high"}
MAX_TOKENS = {"signal": 4000, "cluster": 2000, "lektorat": 4000, "seo": 3000, "recherche": 12000,
              "faktencheck": 12000, "text": 16000, "dossier": 32000, "pruefer": 16000}
OHNE_FALLBACK = ("claude-haiku",)  # für Haiku gibt es keinen serverseitigen Fallback


@dataclass
class Antwort:
    status: str  # ok | abgelehnt | abgeschnitten | ungueltig
    daten: Any = None  # validiertes Modell (pydantic) oder dict
    text: str = ""
    modell: str = ""
    kosten_usd: float = 0.0
    usage_id: int | None = None
    hinweis: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"


@dataclass
class Aufruf:
    """Ein Modellaufruf ohne Netz für Agent-Modus und Tests: was die Rolle geschickt hätte."""

    rolle: str
    system: str
    user: str
    schema: dict
    meta: dict = field(default_factory=dict)


def prompt_version(system: str) -> str:
    return hashlib.sha256(system.encode("utf-8")).hexdigest()[:12]


def schema_fuer(modell: type[BaseModel], rolle: str, beschreibung: str = "") -> dict:
    """JSON-Schema für output_config.format: alle Felder Pflicht, keine Zusatzfelder, Rolle in der Beschreibung."""
    schema = modell.model_json_schema()

    def streng(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("title", None)
            node.pop("default", None)
            if node.get("type") == "object" and "properties" in node:
                node["additionalProperties"] = False
                node["required"] = list(node["properties"])
            for value in node.values():
                streng(value)
        elif isinstance(node, list):
            for value in node:
                streng(value)

    streng(schema)
    schema["description"] = f"rolle:{rolle}" + (f" – {beschreibung}" if beschreibung else "")
    return schema


def _usage_zeile(store, **werte) -> int | None:
    cols = ", ".join(werte)
    marks = ", ".join("?" for _ in werte)
    with store.lock:
        cur = store.db.execute(f"INSERT INTO agent_usage ({cols}) VALUES ({marks})", tuple(werte.values()))
        store.db.commit()
        return cur.lastrowid


def usage_protokollieren(store, *, rolle: str, provider: str = "anthropic", modell_angefragt: str = "", modell: str = "",
                         version: str = "", tokens: costs.Tokens | None = None, usd: float = 0.0, status: str = "ok",
                         story_id: int | None = None, job_id: int | None = None, latenz_ms: int | None = None,
                         request_id: str = "", iterationen: int = 1, bilder: int = 0, fehler: str = "") -> int | None:
    t = tokens or costs.Tokens()
    return _usage_zeile(
        store, ts=now_iso(), story_id=story_id, job_id=job_id, rolle=rolle, provider=provider,
        modell_angefragt=modell_angefragt, modell=modell, prompt_version=version, input_tokens=t.input,
        output_tokens=t.output, cache_write_5m=t.cache_write_5m, cache_write_1h=t.cache_write_1h,
        cache_read=t.cache_read, bilder=bilder, iterationen=iterationen, kosten_usd=usd,
        preis_version=costs.PRICE_VERSION, status=status, latenz_ms=latenz_ms, request_id=request_id,
        fehler=fehler[:300] if fehler else None,
    )


class Claude:
    """Rollen rufen Claude ausschließlich hierüber auf."""

    def __init__(self, settings: Settings, store, client=None, budget: costs.Budget | None = None,
                 client_factory: Callable[[], Any] | None = None):
        self.settings = settings
        self.store = store
        self._client = client
        self._factory = client_factory
        self.budget = budget

    @property
    def client(self):
        if self._client is None:
            if self._factory is not None:
                self._client = self._factory()
            else:
                import anthropic

                # 600 s je Versuch: Texte mit Thinking (Sonnet/Opus) brauchen Zeit; die Job-Deadline liegt darüber
                self._client = anthropic.Anthropic(max_retries=1, timeout=600)
        return self._client

    def call(
        self,
        rolle: str,
        system: str,
        user: str,
        ergebnis: type[T],
        *,
        story_id: int | None = None,
        job_id: int | None = None,
        modell: str | None = None,
        max_tokens: int | None = None,
        effort: str | None = None,
        timeout: float | None = None,
        retries: int | None = None,
        cache: bool = True,
        schema: dict | None = None,
    ) -> Antwort:
        """Ruft Claude mit strukturiertem Output auf. BudgetErschoepft, wenn das Budget den Aufruf nicht trägt;
        API-Fehler werden protokolliert und weitergereicht (der Job-Runner entscheidet über Wiederholung)."""
        modell = modell or self.settings.modell_fuer(rolle)
        max_tokens = max_tokens or MAX_TOKENS.get(rolle, 8000)
        version = prompt_version(system)
        if schema is not None:  # z. B. v1-Writer mit Kategorie-Enum
            schema = {**schema, "description": f"rolle:{rolle}"}
        else:
            schema = schema_fuer(ergebnis, rolle)
        reservierung = None
        if self.budget is not None:
            betrag = costs.schaetzung(modell, len(system) + len(user), max_tokens)
            try:
                reservierung = self.budget.reservieren(betrag, rolle, story_id)
            except costs.BudgetErschoepft:
                raise  # kein Aufruf, keine Kosten – protokolliert wird beim Job (wartet_budget), nicht je Versuch
        kwargs: dict[str, Any] = dict(
            model=modell,
            max_tokens=max_tokens,
            system=[{"type": "text", "text": system, **({"cache_control": {"type": "ephemeral"}} if cache else {})}],
            messages=[{"role": "user", "content": user}],
            output_config={"effort": effort or EFFORT.get(rolle, "medium"),
                           "format": {"type": "json_schema", "schema": schema}},
        )
        if not modell.startswith(OHNE_FALLBACK):
            kwargs["betas"] = [FALLBACK_BETA]
            kwargs["fallbacks"] = "default"  # bei einer Ablehnung übernimmt serverseitig ein Ersatzmodell
        client = self.client
        if timeout is not None or retries is not None:
            opts = {}
            if timeout is not None:
                opts["timeout"] = timeout
            if retries is not None:
                opts["max_retries"] = retries
            client = client.with_options(**opts)
        try:
            # Stopp-Schalter unmittelbar vor dem Aufruf nach außen: wirft Gestoppt, kein Aufruf, keine Kosten
            schalter.pruefen(self.store, "redaktion")
            t0 = time.monotonic()
            try:
                response = client.beta.messages.create(**kwargs)
            except Exception as exc:  # noqa: BLE001 – protokollieren und weiterreichen
                usage_protokollieren(self.store, rolle=rolle, modell_angefragt=modell, version=version, status="fehler",
                                     story_id=story_id, job_id=job_id, latenz_ms=int((time.monotonic() - t0) * 1000),
                                     fehler=f"{type(exc).__name__}: {exc}")
                raise
            latenz = int((time.monotonic() - t0) * 1000)
            modell_ist = getattr(response, "model", "") or modell
            abr = costs.abrechnen_usage(getattr(response, "usage", None), modell_ist)
            stop = getattr(response, "stop_reason", "")
            status = {"refusal": "abgelehnt", "max_tokens": "abgeschnitten"}.get(stop, "ok")
            text = "".join(getattr(b, "text", "") for b in getattr(response, "content", []) or []
                           if getattr(b, "type", "") == "text")
            daten, hinweis = None, ""
            if status == "abgelehnt":
                hinweis = f"abgelehnt ({getattr(getattr(response, 'stop_details', None), 'category', None) or 'ohne Kategorie'})"
            elif status == "ok":
                try:
                    daten = ergebnis.model_validate_json(text)
                except (ValidationError, ValueError) as exc:
                    status, hinweis = "ungueltig", f"Antwort passt nicht zum Schema: {str(exc)[:200]}"
            usage_id = usage_protokollieren(
                self.store, rolle=rolle, modell_angefragt=modell, modell=modell_ist, version=version, tokens=abr.tokens,
                usd=abr.usd, status=status, story_id=story_id, job_id=job_id, latenz_ms=latenz,
                request_id=str(getattr(response, "_request_id", "") or getattr(response, "id", "") or ""),
                iterationen=abr.iterationen, fehler=hinweis,
            )
            if status != "ok":
                log.warning("%s: %s %s", rolle, status, hinweis)
            return Antwort(status=status, daten=daten, text=text, modell=modell_ist, kosten_usd=abr.usd,
                           usage_id=usage_id, hinweis=hinweis)
        finally:
            if reservierung is not None and self.budget is not None:
                self.budget.freigeben(reservierung)


def budget_fuer(settings: Settings, store) -> costs.Budget:
    from .. import notify

    def melden(text: str) -> None:
        notify._post(settings, text)

    return costs.Budget(store, settings.budget_tag_usd, settings.budget_monat_usd, settings.budget_warnung, melden=melden)


def json_block(name: str, daten: Any) -> str:
    """Daten als JSON in einem benannten Block. < und > werden als \\u003c/\\u003e geschrieben (gültiges JSON),
    damit Text aus dem Netz den Block nicht mit „</dokumente>“ vorzeitig schließen kann."""
    text = json.dumps(daten, ensure_ascii=False, indent=1).replace("<", "\\u003c").replace(">", "\\u003e")
    return f"<{name}>\n{text}\n</{name}>"
