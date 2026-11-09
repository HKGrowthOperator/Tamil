"""Benachrichtigungen (Vertrag B.2.5): sofort bei neuen Entwürfen, gebündelt als Tageszusammenfassung."""

from __future__ import annotations

import logging

import requests

from .config import Settings
from .store import OPEN_STATES, Store

log = logging.getLogger(__name__)


def _post(settings: Settings, text: str) -> bool:
    if not settings.notify_webhook:
        return False
    try:
        # Slack und Discord/Teams-Webhooks lesen unterschiedliche Felder – beide mitschicken
        requests.post(settings.notify_webhook, json={"text": text, "content": text}, timeout=10)
        return True
    except requests.RequestException as exc:
        log.warning("Benachrichtigung fehlgeschlagen: %s", exc)
        return False


def notify_new(settings: Settings, results: list) -> str:
    fresh = [r for r in results if r.status == "entwurf"]
    if not fresh:
        return ""
    lines = [f"📰 {len(fresh)} neue Tamil.de-Entwürfe warten auf Freigabe:"]
    lines += [f"• [{r.category}] {r.title} – {r.link}" for r in fresh]
    text = "\n".join(lines)
    _post(settings, text)
    return text


def digest(settings: Settings, store: Store) -> str:
    """Tageszusammenfassung: offene Vorgänge und die zehn wichtigsten neuen Entwürfe."""
    counts = store.counts_by_status()
    offen = sum(counts[s] for s in OPEN_STATES)
    lines = [
        f"☀️ Tamil.de Radar – Tageszusammenfassung: {offen} offene Entwürfe "
        f"(neu {counts['neu']}, bearbeitet {counts['bearbeitet']}, zurückgestellt {counts['zurueckgestellt']}), "
        f"{counts['freigegeben']} freigegeben, {counts['fehler']} mit Fehler.",
    ]
    for d in store.list_drafts("neu", limit=10):
        ort = f" · {d['ort']}" if d.get("ort") else ""
        lines.append(f"• [{d['kategorie']}] {d['titel']} (Relevanz {d['relevanz']}{ort}) – {settings.web_url}/entwurf/{d['id']}")
    lines.append(f"Alle Entwürfe: {settings.web_url}/")
    lines += _redaktion_v2(settings, store)
    text = "\n".join(lines)
    _post(settings, text)
    return text


def _redaktion_v2(settings: Settings, store: Store) -> list[str]:
    """Kosten und Probleme der letzten 24 Stunden (Redaktion v2); leer, solange nichts gemessen wurde."""
    from .workflow import jobs, repo
    from .workflow.providers import budget_fuer

    bericht = repo.kosten_bericht(store, 1)
    stand = budget_fuer(settings, store).stand()
    zaehler = jobs.zaehlen(store)
    recherche = store.db.execute("SELECT COUNT(*) FROM stories WHERE status = 'recherche_erforderlich'").fetchone()[0]
    if not bericht["je_rolle"] and not any(zaehler.values()) and not recherche:
        return []
    zeilen = [f"💶 Kosten gestern/heute: ${bericht['gesamt_usd']:.2f} · Monat ${stand['monat_usd']:.2f} von "
              f"${stand['monat_limit']:.2f}" + (" · BUDGET ERREICHT" if stand["stopp"] else "")]
    probleme = []
    if recherche:
        probleme.append(f"{recherche} Storys „Recherche nötig“ ({settings.web_url}/recherche)")
    if zaehler["tot"]:
        probleme.append(f"{zaehler['tot']} abgebrochene Jobs ({settings.web_url}/warteschlange?status=tot)")
    if zaehler["wartet_budget"]:
        probleme.append(f"{zaehler['wartet_budget']} Jobs warten aufs Budget")
    if bericht["fehler"]:
        probleme.append(f"{len(bericht['fehler'])} Fehlversuche bei Modellaufrufen")
    if probleme:
        zeilen.append("⚠️ " + " · ".join(probleme))
    return zeilen
