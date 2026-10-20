"""Lokales WordPress mit den Inhalten des Prototyps füllen (Testbett für Theme und Plugins).

Liest prototyp/content/*.json und legt an: Altbestand-Beiträge, die fertigen Radar-Beiträge, die Kinoliste,
Termine (Kategorie „events“ mit Termin-Feldern) und die Seiten (Events, Kontakt, Production, TV, Impressum,
Datenschutz, Über uns). Beiträge laufen über tamil-radar/v1/beitrag (ein Aufruf mit Bild, Meta, Schlagworten),
Seiten über die Core-REST. Idempotent: vorhandene Beiträge (gleiche radar_uid) und Seiten (gleicher Slug) bleiben.

    set -a; . "$WP_DIR/.env.local"; set +a
    python wordpress/dev/import_prototype.py [--wp-cli "php $WP_DIR/wp-cli.phar --path=$WP_DIR --allow-root"]

Mit --wp-cli setzt das Skript zusätzlich Customizer-Werte (Aufmacher, Rezept, Beispiel-Kontaktdaten), die REST nicht
erreicht. Nur für das lokale Testbett gedacht – nie gegen die echte tamil.de laufen lassen.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from news_radar.render import render_content, render_kino_liste  # noqa: E402

CONTENT = REPO / "prototyp" / "content"
STATIC = REPO / "prototyp" / "static"
EVENT_TAGS = {"kino": "Kino", "kultur": "Kultur", "tanz": "Tanz", "konzert": "Konzert"}


class WP:
    def __init__(self, url: str, user: str, password: str):
        self.url = url.rstrip("/")
        self.http = requests.Session()
        self.http.auth = (user, password)
        self.http.headers["User-Agent"] = "TamilDE-Import/1.0"

    def req(self, method: str, path: str, **kw) -> tuple[int, dict | list]:
        r = self.http.request(method, f"{self.url}/wp-json/{path}", timeout=120, **kw)
        try:
            data = r.json()
        except ValueError:
            data = {"text": r.text[:300]}
        return r.status_code, data

    def beitrag(self, payload: dict) -> tuple[str, int]:
        code, data = self.req("POST", "tamil-radar/v1/beitrag", json=payload)
        if code == 409:
            return "vorhanden", int((data.get("data") or {}).get("id") or 0)
        if code >= 400:
            raise RuntimeError(f"{payload['titel'][:60]}: {code} {str(data)[:300]}")
        return "neu", int(data["id"])

    def seite(self, slug: str, titel: str, inhalt: str) -> tuple[str, int]:
        code, data = self.req("GET", "wp/v2/pages", params={"slug": slug, "status": "publish,draft", "context": "edit"})
        if code == 200 and data:
            return "vorhanden", int(data[0]["id"])
        code, data = self.req("POST", "wp/v2/pages", json={"slug": slug, "title": titel, "content": inhalt, "status": "publish"})
        if code >= 400:
            raise RuntimeError(f"Seite {slug}: {code} {str(data)[:300]}")
        return "neu", int(data["id"])


def bild(pfad: Path, alt: str, credit: str) -> dict:
    if not pfad.exists():
        return {}
    return {"daten": base64.b64encode(pfad.read_bytes()).decode("ascii"), "dateiname": pfad.name, "alt": alt, "credit": credit}


def altbestand(wp: WP, posts: list[dict], site: dict, stats: dict) -> dict[int, int]:
    production = {int(i) for i in site["production"]["konzerte"]}
    ids: dict[int, int] = {}
    for p in posts:
        if p.get("radar"):
            continue
        tags = [t for t in p.get("tags") or [] if t]
        if int(p["id"]) in production:
            tags.append("production")
        payload = {
            "titel": p["titel"],
            "inhalt": p["inhalt_html"],
            "teaser": p.get("excerpt") or "",
            "status": "publish",
            "slug": p["slug"],
            "datum": p["datum"] + " 09:00",
            "kategorie": (p.get("kategorien") or ["news"])[0],
            "kategorien": (p.get("kategorien") or [])[1:],
            "schlagworte": tags,
            "meta": {"radar_uid": f"alt-{p['id']}", "standfirst": p.get("standfirst") or ""},
            "bild": bild(STATIC / p["bild"]["src"], p["titel"], "Foto: Tamil.de"),
        }
        status, wp_id = wp.beitrag(payload)
        stats[status] += 1
        ids[int(p["id"])] = wp_id
    return ids


def radar_beitraege(wp: WP, radar: dict, stats: dict) -> dict[int, int]:
    ids: dict[int, int] = {}
    for d in radar["entwuerfe"]:
        if d.get("status") not in ("bearbeitet", "freigegeben", "veroeffentlicht"):
            continue
        b = d.get("bild") or {}
        datei = STATIC / "img" / "radar" / (b.get("datei") or "")
        meta = {k: d.get(k) for k in ("quelle_name", "quelle_url", "quelle_sprache", "ort", "bild_origin") if d.get(k)}
        meta.update({"radar_uid": d["uid"], "radar_relevanz": int(d.get("relevanz") or 0), "standfirst": d.get("teaser") or ""})
        if d.get("quelle_datum"):
            meta["quelle_datum"] = d["quelle_datum"][:16]
        payload = {
            "titel": d["titel"],
            "inhalt": render_content(d),
            "teaser": d.get("teaser") or "",
            "status": "publish",
            "datum": (d.get("updated_at") or d.get("created_at") or "")[:16].replace("T", " "),
            "kategorie": d.get("kategorie") or "news",
            "schlagworte": d.get("schlagworte") or [],
            "meta": meta,
            "seo": {"title": d.get("seo_titel") or d["titel"], "description": d.get("meta_beschreibung") or ""},
            "bild": bild(datei, d.get("bild_alt") or d["titel"], b.get("credit") or d.get("bild_credit") or ""),
        }
        status, wp_id = wp.beitrag(payload)
        stats[status] += 1
        ids[int(d["id"])] = wp_id
    return ids


def kino_und_termine(wp: WP, events: dict, stats: dict) -> None:
    k = events["kino_termine"]
    payload = {
        "titel": k["titel"],
        "inhalt": k["inhalt_html"] + "\n" + render_kino_liste(k["fakten"]) + f'\n<p class="quelle">Quelle: {k["hinweis"]}</p>',
        "teaser": k["teaser"],
        "status": "publish",
        "slug": k["slug"],
        "datum": k["stand"] + " 08:00",
        "kategorie": "kino",
        "schlagworte": [k["film"], "Kinotermine"],
        "meta": {"radar_uid": f"kino-{k['slug']}", "kino_fakten": k["fakten"], "standfirst": k["teaser"]},
        "bild": bild(STATIC / "img" / f"ev-{k['slug']}.jpg", k["titel"], "Grafik: Tamil.de"),
    }
    stats[wp.beitrag(payload)[0]] += 1
    for e in events["events"]:
        if e["slug"] == "jailer-2-kinowoche":  # steht schon als Kinoliste da
            continue
        start = e["von"] + (" " + e["zeit"] if e.get("zeit", "")[:2].isdigit() else "")
        land = e.get("land") if e.get("land") in ("DE", "AT", "CH", "DACH") else ""
        quelle = e.get("quelle") or {}
        inhalt = f"<p>{e['beschreibung']}</p>"
        if str(quelle.get("url", "")).startswith("http"):
            inhalt += f'\n<p class="quelle">Quelle: <a href="{quelle["url"]}" rel="nofollow noopener" target="_blank">{quelle["name"]}</a></p>'
        payload = {
            "titel": e["titel"],
            "inhalt": inhalt,
            "teaser": e["beschreibung"][:200],
            "status": "publish",
            "slug": e["slug"],
            "datum": "2026-10-16 10:00",
            "kategorie": "events",
            "schlagworte": [EVENT_TAGS.get(e["kategorie"], e.get("kategorie_label") or "Event")],
            "meta": {
                "radar_uid": f"event-{e['slug']}",
                "event_datum": start,
                "event_ende": e["bis"] if e.get("bis") and e["bis"] != e["von"] else "",
                "event_ort": e.get("ort") or "",
                "event_land": land,
                "event_veranstalter": e.get("veranstalter") or "",
                "event_preis": e.get("preis") or "",
                "ticket_url": e["ticket_url"] if str(e.get("ticket_url", "")).startswith("http") else "",
                "ticket_label": e.get("ticket_label") or "",
                "ort": e.get("stadt") or "",
            },
            "bild": bild(STATIC / "img" / f"ev-{e['slug']}.jpg", e["titel"], "Grafik: Tamil.de"),
        }
        stats[wp.beitrag(payload)[0]] += 1


def seiten(wp: WP, posts: dict, site: dict, stats: dict) -> None:
    alt = {s["slug"]: s for s in posts["seiten"]}
    faq = "".join(
        f'<!-- wp:details -->\n<details class="wp-block-details"><summary>{f["frage"]}</summary><!-- wp:paragraph -->\n<p>{f["antwort"]}</p>\n<!-- /wp:paragraph --></details>\n<!-- /wp:details -->\n'
        for f in site["faq"]
    )
    reporter = alt.get("reporter", {}).get("inhalt_html", "")
    plan = [
        ("events", "Events", ""),
        ("kontakt", "Kontakt", (f"<h2>Mitmachen: Leser-Reporter</h2>\n{reporter}\n" if reporter else "") + "<h2>Häufige Fragen</h2>\n" + faq),
        ("production", "Production", ""),
        ("tv", "Tamil TV", ""),
        ("impressum", "Impressum", alt.get("impressum", {}).get("inhalt_html") or "<p>Angaben gemäß § 5 DDG – vom Auftraggeber zu liefern.</p>"),
        ("datenschutz", "Datenschutzerklärung", alt.get("datenschutzerklaerung", {}).get("inhalt_html", "")),
        ("ueber-uns", "Über Tamil.de", alt.get("ueberuns", {}).get("inhalt_html") or f"<p>{site['ueber_uns']}</p>"),
        ("fsk", "Alterseinstufungen und FSK-Kennzeichen", alt.get("fsk", {}).get("inhalt_html", "")),
    ]
    for slug, titel, inhalt in plan:
        stats[wp.seite(slug, titel, inhalt)[0]] += 1


def sticky(wp: WP, ids: list[int]) -> None:
    for wp_id in ids:
        if wp_id:
            wp.req("POST", f"wp/v2/posts/{wp_id}", json={"sticky": True})


def theme_mods(wp_cli: str, werte: dict[str, str]) -> None:
    cmd = shlex.split(wp_cli)
    for key, value in werte.items():
        subprocess.run([*cmd, "theme", "mod", "set", f"tamil_{key}", str(value)], check=True, capture_output=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wp-cli", default="", help="Aufruf von wp-cli für Customizer-Werte (optional)")
    args = ap.parse_args()
    url = os.environ.get("WP_URL", "")
    user = os.environ.get("WP_ADMIN_USER", "")
    pw = os.environ.get("WP_ADMIN_APP_PASSWORD", "")
    if not (url and user and pw):
        print("WP_URL, WP_ADMIN_USER und WP_ADMIN_APP_PASSWORD fehlen (stehen in $WP_DIR/.env.local).")
        return 2
    if "tamil.de" in url and "127.0.0.1" not in url:
        print("Abbruch: Der Importer ist nur für das lokale Testbett gedacht.")
        return 2
    wp = WP(url, user, pw)
    posts = json.loads((CONTENT / "posts.json").read_text(encoding="utf-8"))
    site = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
    radar = json.loads((CONTENT / "radar.json").read_text(encoding="utf-8"))
    events = json.loads((CONTENT / "events.json").read_text(encoding="utf-8"))
    stats = {"neu": 0, "vorhanden": 0}

    alt_ids = altbestand(wp, posts["posts"], site, stats)
    radar_ids = radar_beitraege(wp, radar, stats)
    kino_und_termine(wp, events, stats)
    seiten(wp, posts, site, stats)
    sticky(wp, [alt_ids.get(int(i), 0) for i in site["top_themen"]] + [radar_ids.get(int(site.get("radar_lead") or 0), 0)])
    if args.wp_cli:
        theme_mods(args.wp_cli, {
            "aufmacher_id": radar_ids.get(int(site.get("radar_lead") or 0), 0) or "",
            "rezept_id": alt_ids.get(int(site["rezept"]["id"]), 0) or "",
            "telefon": "+49 69 123 456 (Beispiel)",
            "email": "info@tamil.de",
            "whatsapp": "+49 170 123 4567",
            "adresse": "\n".join(site["kontakt"]["adresse"]),
            "production_ticket_url": site["production"]["ticket"]["url"],
            "production_ticket_label": site["production"]["ticket"]["label"],
            "tv_sender": "\n".join(f"{s['name']} | {s['stream']}" for s in site["tv"]["sender"]),
        })
    print(f"Import fertig: {stats['neu']} neu, {stats['vorhanden']} schon vorhanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
