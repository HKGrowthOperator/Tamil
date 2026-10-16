"""HTML eines Entwurfs so, wie er auf tamil.de erscheint – für Vorschau und Veröffentlichung."""

from __future__ import annotations

import html
import re
from datetime import datetime

_QUELLE_RE = re.compile(r'<p class="quelle">.*?</p>\s*', re.S)
_UNSAFE_RE = re.compile(r"<\s*(script|iframe|object|embed|style)[^>]*>.*?<\s*/\s*\1\s*>|<\s*(script|iframe|object|embed|style)[^>]*/?>", re.I | re.S)
_ON_ATTR_RE = re.compile(r"\s+on\w+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
_JS_HREF_RE = re.compile(r"(href|src)\s*=\s*([\"']?)\s*javascript:[^\"'>\s]*", re.I)
_ALLOWED_TAGS = re.compile(r"</?(p|h2|h3|strong|em|b|i|ul|ol|li|a|br|blockquote|figure|figcaption|img|div|span|table|thead|tbody|tr|th|td)\b[^>]*>", re.I)


def sanitize_html(text: str) -> str:
    """Entfernt Script/Iframe/Event-Handler – WordPress filtert für Autoren noch einmal (wp_kses)."""
    text = _UNSAFE_RE.sub("", text or "")
    text = _ON_ATTR_RE.sub("", text)
    text = _JS_HREF_RE.sub(r'\1=\2#', text)
    return re.sub(r"<[^>]+>", lambda m: m.group(0) if _ALLOWED_TAGS.fullmatch(m.group(0)) else "", text)


def format_date_de(value: str | None, with_time: bool = False) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return dt.strftime("%d.%m.%Y %H:%M" if with_time else "%d.%m.%Y")


def _link(url: str, label: str) -> str:
    return f'<a href="{html.escape(url, quote=True)}" rel="nofollow noopener" target="_blank">{html.escape(label)}</a>'


def render_kino_liste(fakten: dict) -> str:
    kinos = (fakten or {}).get("kinos") or []
    if not kinos:
        return ""
    by_city: dict[str, list[dict]] = {}
    for k in kinos:
        by_city.setdefault(k.get("stadt") or "Weitere Orte", []).append(k)
    parts = ["<h2>Spielorte und Termine</h2>", '<ul class="kino-liste">']
    for stadt in sorted(by_city):
        for k in sorted(by_city[stadt], key=lambda x: x.get("kino", "")):
            termine = [format_date_de(t, with_time=True) for t in k.get("termine") or []]
            termin_txt = ", ".join(t for t in termine if t)
            if not termin_txt and k.get("von"):
                termin_txt = f"ab {format_date_de(k['von'])}"
            land = f" ({k['land']})" if k.get("land") and k["land"] != "DE" else ""
            line = f"<strong>{html.escape(stadt)}{land}</strong> – {html.escape(k.get('kino', ''))}"
            if termin_txt:
                line += f": {html.escape(termin_txt)}"
            if k.get("url"):
                line += " · " + _link(k["url"], "Tickets & Infos")
            parts.append(f"<li>{line}</li>")
    parts.append("</ul>")
    woche = (fakten or {}).get("woche")
    if woche:
        parts.append(f'<p class="hinweis">Stand: Kinowoche {html.escape(str(woche))}. Angaben ohne Gewähr, bitte beim Kino prüfen.</p>')
    return "\n".join(parts)


def render_event_box(row: dict) -> str:
    rows = []
    if row.get("event_datum"):
        rows.append(f"<p><strong>Wann:</strong> {html.escape(format_date_de(row['event_datum']))}</p>")
    if row.get("event_ort"):
        rows.append(f"<p><strong>Wo:</strong> {html.escape(row['event_ort'])}</p>")
    if row.get("ticket_url"):
        rows.append(f"<p>{_link(row['ticket_url'], 'Tickets')}</p>")
    if not rows:
        return ""
    return '<div class="event-box">\n' + "\n".join(rows) + "\n</div>"


def render_content(row: dict) -> str:
    """Haupttext + Kino-/Event-Block + verlinkte Quellen. `row` ist ein Entwurf aus dem Store."""
    body = _QUELLE_RE.sub("", sanitize_html(row.get("inhalt_html") or "")).rstrip()
    blocks = [body]
    if row.get("typ") == "kino_termine":
        blocks.append(render_kino_liste(row.get("fakten") or {}))
    elif row.get("typ") == "event":
        blocks.append(render_event_box(row))
    quelle = row.get("quelle_url") or ""
    name = row.get("quelle_name") or "Quelle"
    if quelle:
        links = [_link(quelle, name)]
        for extra in row.get("weitere_quellen") or []:
            if extra.get("url"):
                links.append(_link(extra["url"], extra.get("name") or extra["url"]))
        blocks.append('<p class="quelle">Quelle: ' + ", ".join(links) + "</p>")
    return "\n".join(b for b in blocks if b)
