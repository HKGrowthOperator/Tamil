#!/usr/bin/env python3
"""Tamil.de – HTML-Prototypen der fünf Vertrags-Vorlagen (Designkonzept, Pos. A.1.1–A.1.4).

    python prototyp/build.py snapshot [--export export] [--no-shift]  # Beiträge + Bilder aus dem Export aufbereiten
    python prototyp/build.py build                                     # dist/ erzeugen (statisches HTML)
    python prototyp/build.py shots                                     # Screenshots 390 / 820 / 1280 px nach shots/
    python prototyp/build.py artifact                                  # dist-artifact/ (Startseite ohne Dokumentgerüst)
    python prototyp/build.py all                                       # build + shots + artifact

`snapshot` braucht den Export aus `tools/export_site.py` (posts/media/categories/tags.json, inventory.csv)
und lädt die verwendeten Bilder einmalig herunter. `build` arbeitet danach ohne Netz nur mit `content/`.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import html as html_mod
import io
import json
import math
import re
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO))

from news_radar.render import format_date_de, render_kino_liste, sanitize_html  # noqa: E402
from news_radar.wordpress import slugify  # noqa: E402

import radar_map  # noqa: E402

CONTENT, TEMPLATES, STATIC = ROOT / "content", ROOT / "templates", ROOT / "static"
IMG, DIST, DIST_ARTIFACT, SHOTS = STATIC / "img", ROOT / "dist", ROOT / "dist-artifact", ROOT / "shots"
CHROMIUM = Path("/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

SIZE_PRIORITY = ("large", "medium_large", "slider-img", "full")
TAG_IGNORE = {"tamil", "tt", "ticker", "sticker", "dfgfsd", "test", "slider-sidebar", "tamil.de"}
MIN_WORDS = 120
HERO_MIN_WIDTH, HERO_MIN_WORDS = 1024, 150
PER_CATEGORY_PAGE, PER_RUBRIK, NEUESTE, RELATED = 12, 4, 6, 3
INLINE_IMAGES_MAX = 2
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
WOCHENTAGE_KURZ = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

_SHARE_RE = re.compile(r"<div class=['\"]share-to-whatsapp-wrapper['\"].*$", re.S)
_YT_IFRAME_RE = re.compile(r"<iframe[^>]+src=[\"']https?://(?:www\.)?(?:youtube(?:-nocookie)?\.com/embed/|youtu\.be/)([A-Za-z0-9_-]{6,})[^\"']*[\"'][^>]*>(?:\s*</iframe>)?", re.I | re.S)
_DEAD_LINKED_IMG_RE = re.compile(r"<a[^>]*>\s*(?:<br\s*/?>\s*)*<img[^>]+src=[\"']http://[^>]*>\s*</a>", re.I | re.S)
_DEAD_IMG_RE = re.compile(r"<img[^>]+src=[\"']http://[^>]*>", re.I)
_TAG_RE = re.compile(r"<(/?)([a-zA-Z0-9]+)([^>]*)>")
_ATTR_RE = re.compile(r"([a-zA-Z-]+)\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)")
_LINKED_IMG_RE = re.compile(r"<a href=\"[^\"]+\.(?:jpe?g|png|gif|webp)\"[^>]*>\s*(<img[^>]+>)\s*</a>", re.I)
_EMPTY_RE = re.compile(r"<(p|div|figure|figcaption|span|strong|em|li)>(?:\s|&nbsp;|<br\s*/?>)*</\1>", re.I)
_STRIP_RE = re.compile(r"<[^>]+>")
_IMG_SRC_RE = re.compile(r"<img([^>]*)\ssrc=\"([^\"]+)\"([^>]*)>", re.I)
_HEADING_RE = re.compile(r"<h[1-6][^>]*>")
KEEP_ATTRS = {"a": ("href", "title"), "img": ("src", "alt", "width", "height")}


# ---------------------------------------------------------------- Inhalts-Pipeline

def strip_tags(text: str) -> str:
    return html_mod.unescape(_STRIP_RE.sub(" ", text or "")).replace("\xa0", " ")


def words(text: str) -> int:
    return len(strip_tags(text).split())


def reading_time(word_count: int) -> int:
    return max(1, math.ceil(word_count / 200))


def excerpt(text: str, limit: int = 160) -> str:
    plain = " ".join(strip_tags(text).split()).replace("[…]", "").replace("[&hellip;]", "").strip()
    if len(plain) <= limit:
        return plain
    cut = plain[:limit].rsplit(" ", 1)[0].rstrip(" ,;:–-")
    return cut + " …"


def fix_caps(title: str) -> str:
    """Versalien-Wörter ab fünf Buchstaben (KRITIK, KOLAMAAVU) werden zu Groß-/Kleinschreibung; kurze Kürzel (NRW, USA) bleiben."""
    if title.isupper():
        return title.title()
    return re.sub(r"\b[A-ZÄÖÜ]{5,}\b", lambda m: m.group(0).capitalize(), title)


def strip_share_widget(body: str) -> str:
    return _SHARE_RE.sub("", body or "")


def video_placeholders(body: str) -> str:
    """YouTube-Einbettungen werden zu Datenschutz-Platzhaltern (Video erst nach Klick laden)."""
    return _YT_IFRAME_RE.sub(lambda m: f"[[VIDEO:{m.group(1)}]]", body)


def drop_dead_images(body: str) -> str:
    body = _DEAD_LINKED_IMG_RE.sub("", body)
    return _DEAD_IMG_RE.sub("", body)


def _rewrite_tag(m: re.Match) -> str:
    closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
    if name == "h1":
        name = "h2"
    elif name in ("h4", "h5", "h6"):
        name = "h3"
    if closing:
        return f"</{name}>"
    keep = KEEP_ATTRS.get(name, ())
    kept = []
    for key, val in _ATTR_RE.findall(attrs):
        if key.lower() in keep:
            kept.append(f'{key.lower()}="{val.strip(chr(34) + chr(39))}"')
    extra = (" " + " ".join(kept)) if kept else ""
    return f"<{name}{extra}>"


def strip_attributes(body: str) -> str:
    """Nur href/title und src/alt/width/height bleiben; h1→h2, h4–h6→h3."""
    return _TAG_RE.sub(_rewrite_tag, body)


def tidy(body: str) -> str:
    body = _LINKED_IMG_RE.sub(r"<figure>\1</figure>", body)
    for _ in range(3):
        body = _EMPTY_RE.sub("", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def clean_body(raw: str) -> str:
    """Komplette Bereinigung eines WordPress-Beitrags für den Prototyp."""
    body = strip_share_widget(raw)
    body = video_placeholders(body)
    body = drop_dead_images(body)
    body = sanitize_html(strip_attributes(body))
    body = tidy(body)
    body = re.sub(r"\[\[VIDEO:([A-Za-z0-9_-]+)\]\]", lambda m: (
        f'<div class="video-embed" data-video="{m.group(1)}"><button type="button" class="video-load">Video laden</button>'
        '<p class="video-hint">YouTube-Video – wird erst nach Klick geladen (Datenschutz).</p></div>'), body)
    return tidy(body)


def inline_images(body: str) -> list[str]:
    return [src for _, src, _ in _IMG_SRC_RE.findall(body) if src.startswith("https://")]


def localize_images(body: str, mapping: dict[str, str | None]) -> str:
    """Ersetzt Bild-URLs durch lokale Dateien; nicht geladene Bilder (None) fliegen samt <figure> raus."""
    def repl(m: re.Match) -> str:
        src = m.group(2)
        local = mapping.get(src, src)
        if local is None:
            return ""
        return f"<img{m.group(1)} src=\"{local}\"{m.group(3)}>"
    return tidy(_IMG_SRC_RE.sub(repl, body))


def split_recipe(body: str) -> dict:
    """Zerlegt einen Rezept-Beitrag in Abschnitte mit Zutaten (ul) und Schritten (p nach „Zubereitung“)."""
    blocks = re.findall(r"<(h2|h3|p|ul|figure)>(.*?)</\1>", body, re.S)
    intro: list[str] = []
    sections: list[dict] = []
    current = {"titel": "", "zutaten": [], "schritte": [], "tipp": []}
    mode = "intro"
    for tag, inner in blocks:
        text = strip_tags(inner).strip()
        if tag in ("h2", "h3"):
            low = text.lower()
            if low.startswith("zutaten"):
                mode = "zutaten"
            elif low.startswith("zubereitung"):
                mode = "schritte"
            elif low.startswith("essensvorschlag") or low.startswith("tipp"):
                mode = "tipp"
            else:
                if current["zutaten"] or current["schritte"]:
                    sections.append(current)
                current = {"titel": text, "zutaten": [], "schritte": [], "tipp": []}
                mode = "text"
        elif tag == "p" and text.lower().rstrip(":") in ("zutaten", "zubereitung"):
            mode = "zutaten" if text.lower().startswith("zutaten") else "schritte"
        elif tag == "ul" and mode == "zutaten":
            current["zutaten"] += [strip_tags(li).strip() for li in re.findall(r"<li>(.*?)</li>", inner, re.S)]
        elif tag == "p" and text:
            if mode == "intro":
                intro.append(f"<p>{inner}</p>")
            elif mode == "schritte":
                current["schritte"].append(text)
            elif mode == "tipp":
                current["tipp"].append(text)
            elif mode == "text" and not current["schritte"]:
                current.setdefault("text", []).append(text)
    if current["zutaten"] or current["schritte"]:
        sections.append(current)
    if sections and not sections[0]["titel"]:
        sections[0]["titel"] = "Grundrezept"
    return {"intro": "\n".join(intro), "abschnitte": sections}


# ---------------------------------------------------------------- Auswahl

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_site() -> dict:
    return load_json(CONTENT / "site.json")


def load_events() -> dict:
    return load_json(CONTENT / "events.json")


def load_posts() -> dict:
    return load_json(CONTENT / "posts.json")


def kino_chips(post: dict) -> list[str]:
    chips = []
    title = post["titel"].lower()
    if "kritik" in post.get("alt_kategorien", []):
        chips.append("kritik")
    if re.search(r"kinostart|kino-highlight|in deutschen kinos|ab \d{1,2}\.", title):
        chips.append("kinostart")
    if re.search(r"konzert|live in|tour\b|show\b", title):
        chips.append("konzert")
    if re.search(r"musik|song|album|single|sänger|komponist", title):
        chips.append("musik")
    return chips


def newest(posts: list[dict]) -> list[dict]:
    return sorted(posts, key=lambda p: (p["datum"], p["id"]), reverse=True)


def select(posts: list[dict], site: dict) -> dict:
    """Welche Beiträge wohin kommen – deterministisch, ohne Dubletten auf der Startseite."""
    by_id = {p["id"]: p for p in posts}
    kultur_re = re.compile(site["kultur_regex"], re.I)
    kueche_re = re.compile(site["kueche_regex"], re.I)
    for p in posts:
        if kultur_re.search(p["titel"] + " " + p.get("excerpt", "")) and "kultur" not in p["kategorien"]:
            p["kategorien"] = p["kategorien"] + ["kultur"]
            p["kultur_fallback"] = True
        if kueche_re.search(p["titel"]) and "kueche" not in p["kategorien"]:
            p["kategorien"] = ["kueche"] + p["kategorien"]
    for p in posts:
        if "production" in p.get("alt_kategorien", []) and "production" not in p["kategorien"]:
            p["kategorien"] = p["kategorien"] + ["production"]
        if not p.get("excerpt"):
            p["excerpt"] = p["standfirst"] = f"{p['titel']} – ein Konzert von Tamil.de Production." if "production" in p["kategorien"] else p["titel"]
    long_enough = [p for p in newest(posts) if p["woerter"] >= MIN_WORDS or set(p["kategorien"]) & {"kueche", "production"}]
    used: set[int] = set()

    def take(cands: list[dict], n: int) -> list[dict]:
        out = []
        for p in cands:
            if p["id"] not in used:
                out.append(p)
                used.add(p["id"])
            if len(out) >= n:
                break
        return out

    hero = [by_id[i] for i in site["hero"] if i in by_id]
    if len(hero) < 3:
        hero = take([p for p in long_enough if p["bild"]["orig_w"] >= HERO_MIN_WIDTH and p["woerter"] >= HERO_MIN_WORDS], 3)
    used.update(p["id"] for p in hero)
    top = [by_id[i] for i in site["top_themen"] if i in by_id]
    neueste = take(long_enough, NEUESTE)
    rubriken = {slug: take([p for p in long_enough if slug in p["kategorien"]], PER_RUBRIK) for slug in site["kategorien"]}
    kategorie_seiten = {slug: [p for p in long_enough if slug in p["kategorien"]][:PER_CATEGORY_PAGE] for slug in site["kategorien"]}
    related = {p["id"]: [q for q in long_enough if q["id"] != p["id"] and set(q["kategorien"]) & set(p["kategorien"])][:RELATED]
               for p in long_enough}
    rezept = by_id.get(site["rezept"]["id"])
    prod = site.get("production", {})
    production = {"konzerte": [by_id[i] for i in prod.get("konzerte", []) if i in by_id], "service": [by_id[i] for i in prod.get("service", []) if i in by_id]}
    return {"hero": hero, "top": top, "neueste": neueste, "rubriken": rubriken, "kategorie_seiten": kategorie_seiten,
            "related": related, "rezept": rezept, "by_id": by_id, "kueche": [p for p in long_enough if "kueche" in p["kategorien"]],
            "production": production}


def used_ids(sel: dict) -> set[int]:
    ids = {p["id"] for p in sel["hero"] + sel["top"] + sel["neueste"]}
    for lst in list(sel["rubriken"].values()) + list(sel["kategorie_seiten"].values()):
        ids.update(p["id"] for p in lst)
    if sel["rezept"]:
        ids.add(sel["rezept"]["id"])
    ids.update(p["id"] for p in sel["production"]["konzerte"] + sel["production"]["service"])
    for pid in list(ids):
        ids.update(q["id"] for q in sel["related"].get(pid, []))
    return ids


# ---------------------------------------------------------------- Snapshot (Export → content/posts.json + Bilder)

def pick_image(media: dict | None) -> tuple[str, int, int] | None:
    if not media or not media.get("source_url"):
        return None
    details = media.get("media_details") or {}
    sizes = details.get("sizes") or {}
    for key in SIZE_PRIORITY:
        s = sizes.get(key)
        if s and s.get("source_url"):
            return s["source_url"], int(details.get("width") or s["width"]), int(details.get("height") or s["height"])
    return media["source_url"], int(details.get("width") or 0), int(details.get("height") or 0)


def fetch_image(url: str, target: Path, max_width: int, quality: int, session=None) -> dict | None:
    """Lädt ein Bild, verkleinert es (JPEG) und gibt Breite/Höhe zurück. Vorhandene Dateien werden wiederverwendet."""
    from PIL import Image
    if target.exists():
        with Image.open(target) as im:
            return {"w": im.width, "h": im.height}
    import requests
    session = session or requests.Session()
    try:
        resp = session.get(url, timeout=60, headers={"User-Agent": "TamilDE-Prototyp/1.0"})
        resp.raise_for_status()
        with Image.open(io.BytesIO(resp.content)) as im:
            im = im.convert("RGB")
            if im.width > max_width:
                im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
            target.parent.mkdir(parents=True, exist_ok=True)
            im.save(target, "JPEG", quality=quality, optimize=True, progressive=True)
            return {"w": im.width, "h": im.height}
    except Exception as exc:  # noqa: BLE001
        print(f"  Bild fehlgeschlagen: {url} ({exc})", file=sys.stderr)
        return None


def post_record(p: dict, inv: dict, media_by_id: dict, cat_by_id: dict, tag_by_id: dict, shift: timedelta) -> dict | None:
    if inv.get("empfehlung") == "löschen":
        return None
    img = pick_image(media_by_id.get(p.get("featured_media")))
    if not img:
        return None
    kategorien = [k for k in inv["neue_kategorie"].split("|") if k and k != "löschen"]
    datum = datetime.fromisoformat(p["date"]) + shift
    body = clean_body(p["content"]["rendered"])
    titel = fix_caps(html_mod.unescape(_STRIP_RE.sub("", p["title"]["rendered"])).strip())
    tags = [tag_by_id[t] for t in p.get("tags", []) if t in tag_by_id and tag_by_id[t].lower() not in TAG_IGNORE]
    markierungen = [tag_by_id[t].lower() for t in p.get("tags", []) if t in tag_by_id and tag_by_id[t].lower() in ("ticker", "live", "tt", "sticker")]
    alt = [cat_by_id.get(c, "") for c in p.get("categories", [])]
    rec = {
        "id": p["id"], "slug": slugify(p["slug"]), "titel": titel, "datum": datum.strftime("%Y-%m-%d"),
        "datum_original": p["date"][:10], "kategorien": kategorien, "alt_kategorien": alt,
        "excerpt": excerpt(p["excerpt"]["rendered"] if isinstance(p.get("excerpt"), dict) else body, 160),
        "standfirst": excerpt(p["excerpt"]["rendered"] if isinstance(p.get("excerpt"), dict) else body, 230),
        "woerter": words(body), "tags": tags, "markierungen": markierungen, "youtube": bool(re.search(r'data-video="', body)),
        "bild": {"url": img[0], "orig_w": img[1], "orig_h": img[2]}, "inhalt_html": body,
    }
    rec["lesezeit"] = reading_time(rec["woerter"])
    rec["chips"] = kino_chips(rec)
    return rec


def page_record(p: dict, conf: dict, shift: timedelta) -> dict:
    raw = p["content"]["rendered"]
    body = clean_body(raw)
    return {"id": p["id"], "slug": p["slug"], "datei": conf.get("datei", ""), "titel": conf.get("titel") or html_mod.unescape(_STRIP_RE.sub("", p["title"]["rendered"])).strip(),
            "tamil": conf.get("tamil", ""), "hinweis": conf.get("hinweis", ""), "kategorie": conf.get("kategorie", ""), "datum_original": p["date"][:10],
            "datum": (datetime.fromisoformat(p["date"]) + shift).strftime("%Y-%m-%d"), "woerter": words(body), "inhalt_html": body,
            "streams": sorted(set(re.findall(r"https?://[^\"' ]+\.m3u8[^\"' ]*", raw)))}


def page_as_post(p: dict, kategorie: str, shift: timedelta) -> dict:
    """Seiten, die eigentlich Beiträge sind (M.I.A., Jahresrückblick): Bild aus dem Inhalt, sonst Bildkarte."""
    rec = {"id": p["id"], "slug": slugify(p["slug"]), "titel": fix_caps(html_mod.unescape(_STRIP_RE.sub("", p["title"]["rendered"])).strip()),
           "datum": (datetime.fromisoformat(p["date"]) + shift).strftime("%Y-%m-%d"), "datum_original": p["date"][:10],
           "kategorien": [kategorie], "alt_kategorien": ["seite"], "tags": [], "markierungen": [], "youtube": False, "inhalt_html": clean_body(p["content"]["rendered"])}
    rec["excerpt"], rec["standfirst"] = excerpt(rec["inhalt_html"], 160), excerpt(rec["inhalt_html"], 230)
    rec["woerter"], rec["lesezeit"], rec["chips"] = words(rec["inhalt_html"]), reading_time(words(rec["inhalt_html"])), []
    imgs = inline_images(rec["inhalt_html"])
    rec["bild"] = {"url": imgs[0], "orig_w": 1200, "orig_h": 675} if imgs else {"url": "", "orig_w": 1200, "orig_h": 675}
    return rec


def brand_assets(export: Path) -> None:
    """Logo und Werbebanner der alten Seite (export/brand/ aus tools/export_site.py --meta-only) nach static/img/."""
    brand = export / "brand"
    for name, target in (("logo.png", "logo.png"), ("ad-leaderboard.jpg", "ad-leaderboard.jpg"), ("ad-sidebar.jpg", "ad-sidebar.jpg")):
        src = brand / name
        if src.exists():
            if name.endswith(".jpg"):
                from PIL import Image
                with Image.open(src) as im:
                    im.convert("RGB").save(IMG / target, "JPEG", quality=80, optimize=True)
            else:
                shutil.copy(src, IMG / target)
        else:
            print(f"  Markendatei fehlt: {src}", file=sys.stderr)


def snapshot(export: Path, shift_dates: bool = True) -> dict:
    site = load_site()
    posts = load_json(export / "posts.json")
    pages = load_json(export / "pages.json") if (export / "pages.json").exists() else []
    media_by_id = {m["id"]: m for m in load_json(export / "media.json")}
    cat_by_id = {c["id"]: c["slug"] for c in load_json(export / "categories.json")}
    tag_by_id = {t["id"]: t["name"] for t in load_json(export / "tags.json")}
    inventory = {int(r["id"]): r for r in csv.DictReader((export / "inventory.csv").open(encoding="utf-8"))}
    stand = date.fromisoformat(site["stand"])
    newest_date = max(date.fromisoformat(p["date"][:10]) for p in posts)
    shift = (stand - timedelta(days=1)) - newest_date if shift_dates else timedelta(0)

    records = [r for r in (post_record(p, inventory.get(p["id"], {}), media_by_id, cat_by_id, tag_by_id, shift) for p in posts) if r]
    for pg in pages:
        if pg["slug"] in site.get("seiten_als_beitrag", {}):
            records.append(page_as_post(pg, site["seiten_als_beitrag"][pg["slug"]], shift))
    seiten = [page_record(pg, site["seiten"][pg["slug"]], shift) for pg in pages if pg["slug"] in site.get("seiten", {})]
    brand_assets(export)
    counts = {slug: sum(1 for r in records if slug in r["kategorien"]) for slug in site["kategorien"]}
    sel = select(records, site)
    for slug in ("kultur", "kueche"):
        counts[slug] = sum(1 for r in records if slug in r["kategorien"])
    ids = used_ids(sel)
    chosen = [r for r in records if r["id"] in ids]
    print(f"Beiträge im Export: {len(posts)}, verwendbar: {len(records)}, im Prototyp: {len(chosen)}; Datumsverschiebung {shift.days} Tage")

    import requests
    session = requests.Session()
    hero_ids = {p["id"] for p in sel["hero"]}
    for r in chosen:
        max_w = 1400 if r["id"] in hero_ids or r["id"] == site["rezept"]["id"] else 900
        info = fetch_image(r["bild"]["url"], IMG / f"p{r['id']}.jpg", max_w, 74, session) if r["bild"].get("url") else None
        if not info and r.get("alt_kategorien") == ["seite"]:
            from news_radar.images import branded_card
            from PIL import Image
            with Image.open(io.BytesIO(branded_card(r["titel"], site["kategorien"][r["kategorien"][0]]["label"], r["slug"]).data)) as im:
                im.convert("RGB").save(IMG / f"p{r['id']}.jpg", "JPEG", quality=76, optimize=True)
            info = {"w": 1200, "h": 675}
        if not info:
            r["bild"]["src"] = None
            continue
        r["bild"].update(src=f"img/p{r['id']}.jpg", **info)
        mapping: dict[str, str | None] = {}
        for n, url in enumerate(inline_images(r["inhalt_html"])[:INLINE_IMAGES_MAX], 1):
            got = fetch_image(url, IMG / f"p{r['id']}-{n}.jpg", 900, 70, session)
            mapping[url] = f"img/p{r['id']}-{n}.jpg" if got else None
        for url in inline_images(r["inhalt_html"])[INLINE_IMAGES_MAX:]:
            mapping[url] = None
        r["inhalt_html"] = localize_images(r["inhalt_html"], mapping)
    chosen = [r for r in chosen if r["bild"].get("src")]
    for r in chosen:
        r["bild"].pop("url", None)

    ev = load_events()
    cards(ev, site)
    out = {"stand": site["stand"], "shift_days": shift.days, "counts": counts, "posts": chosen, "seiten": seiten}
    (CONTENT / "posts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"content/posts.json: {len(chosen)} Beiträge, {sum(1 for _ in IMG.glob('*.jpg'))} Bilder")
    return out


def cards(ev: dict, site: dict) -> None:
    """Tamil.de-Bildkarten für Events ohne Foto (wie im News-Radar), einmalig erzeugt."""
    from news_radar.images import branded_card
    items = [e for e in ev["events"] if e.get("bild_karte")] + [ev["kino_termine"]]
    for e in items:
        slug = e["slug"]
        target = IMG / f"ev-{slug}.jpg"
        if target.exists():
            continue
        label = e.get("kategorie_label") or site["kategorien"].get(e.get("kategorie", "kino"), {}).get("label", "Kino")
        from PIL import Image
        card = branded_card(e.get("bild_karte") or e["titel"], label, slug)
        with Image.open(io.BytesIO(card.data)) as im:
            im.convert("RGB").resize((1200, 675)).save(target, "JPEG", quality=76, optimize=True)


# ---------------------------------------------------------------- Rendering

def fmt_date(iso: str, weekday: bool = False) -> str:
    d = date.fromisoformat(iso[:10])
    s = f"{d.day}. {MONATE[d.month - 1]} {d.year}"
    return f"{WOCHENTAGE[d.weekday()]}, {s}" if weekday else s


def fmt_range(von: str, bis: str | None) -> str:
    a = date.fromisoformat(von)
    if not bis or bis == von:
        return fmt_date(von, weekday=True)
    b = date.fromisoformat(bis)
    if a.month == b.month:
        return f"{a.day}.–{b.day}. {MONATE[a.month - 1]} {a.year}"
    return f"{a.day}. {MONATE[a.month - 1]} – {b.day}. {MONATE[b.month - 1]} {b.year}"


def ad_slot(key: str, site: dict) -> dict:
    lookup = "inarticle" if key == "billboard" else key  # Startseite: Werbeplatz 03 als 970×250
    slot = next(w for w in site["werbeplaetze"] if w["key"] == lookup)
    return {**slot, "desktop": "970 × 250"} if key == "billboard" else slot


def event_months(events: list[dict]) -> list[dict]:
    groups: dict[str, dict] = {}
    for e in sorted(events, key=lambda e: e["von"]):
        d = date.fromisoformat(e["von"])
        key = f"{d.year}-{d.month:02d}"
        groups.setdefault(key, {"key": key, "label": f"{MONATE[d.month - 1]} {d.year}", "events": []})["events"].append(e)
    return list(groups.values())


def month_grid(year: int, month: int, events: list[dict]) -> dict:
    """Monatsraster Mo–So: je Tag die Events, die an diesem Tag stattfinden."""
    first_weekday, days = calendar.monthrange(year, month)
    cells: list[dict | None] = [None] * first_weekday
    for day in range(1, days + 1):
        d = date(year, month, day)
        todays = [e for e in events if date.fromisoformat(e["von"]) <= d <= date.fromisoformat(e.get("bis") or e["von"])]
        cells.append({"day": day, "iso": d.isoformat(), "events": todays, "weekend": d.weekday() >= 5})
    while len(cells) % 7:
        cells.append(None)
    return {"label": f"{MONATE[month - 1]} {year}", "weeks": [cells[i:i + 7] for i in range(0, len(cells), 7)]}


def kino_widget(fakten: dict) -> dict:
    by_land: dict[str, list[str]] = {}
    for k in fakten["kinos"]:
        by_land.setdefault(k["land"], []).append(f"{k['stadt']} · {k['kino']}")
    order = [("DE", "Deutschland"), ("CH", "Schweiz"), ("AT", "Österreich")]
    return {"anzahl": len(fakten["kinos"]), "laender": [{"code": c, "label": l, "kinos": by_land.get(c, [])} for c, l in order if by_land.get(c)]}


def radar_orte(site: dict, ev: dict, by_id: dict) -> list[dict]:
    """Blips für die Radar-Bühne: ein Ort je Stadt, aus Kinoprogramm, Events und Nachrichten (jeweils mit Quelle im Label)."""
    coords = site["staedte"]
    orte: dict[str, dict] = {}

    def add(stadt: str, label: str, art: str, href: str = "", quelle: str = ""):
        if stadt not in coords:
            return
        o = orte.setdefault(stadt, {"name": stadt, "lat": coords[stadt][0], "lon": coords[stadt][1], "art": art, "labels": [], "href": href, "quelle": quelle})
        o["labels"].append(label)
        if art == "kino" and o["art"] != "kino":
            o["art"] = art

    kt = ev["kino_termine"]
    for k in kt["fakten"]["kinos"]:
        add(k["stadt"], f"{kt['film']} im {k['kino']}", "kino", f"{kt['slug']}.html", k.get("quelle", ""))
    for e in ev["events"]:
        if e["land"] != "DACH":
            add(e["stadt"], e["titel"], "event" if e["kategorie"] != "kino" else "kino", e["seite"], e["quelle"]["name"])
    for n in site.get("radar_news", []):
        post = by_id.get(n.get("post"))
        add(n["stadt"], n["label"], "news", article_link(post) if post else "", "Redaktion")
    out = []
    for o in orte.values():
        o["label"] = o["labels"][0] if len(o["labels"]) == 1 else f"{len(o['labels'])} Meldungen"
        out.append(o)
    out.sort(key=lambda o: (o["art"] != "kino", o["name"]))
    return out


def erfasst_log(orte: list[dict]) -> list[dict]:
    """„Gerade erfasst“: die letzten Treffer als Protokollzeilen mit Uhrzeiten (deterministisch für den Prototyp)."""
    minute = 9 * 60 + 12
    rows = []
    for i, o in enumerate(orte[:9]):
        minute -= (7 + (i * 11) % 23)
        rows.append({"zeit": f"{minute // 60:02d}:{minute % 60:02d}", "ort": o["name"], "text": o["labels"][0], "href": o["href"], "art": o["art"]})
    return rows


def ticker_items(sel: dict, ev: dict, kat: dict) -> list[dict]:
    kt = ev["kino_termine"]
    items = [{"k": kat["kino"]["tamil"], "text": f"{kt['film']} läuft in {len(kt['fakten']['kinos'])} Kinos in DE, AT und CH", "href": f"{kt['slug']}.html"}]
    for e in ev["events"][1:4]:
        items.append({"k": kat["events"]["tamil"], "text": f"{e['datum_text'].split(',')[-1].strip()}: {e['titel']}", "href": e["seite"]})
    for p in sel["neueste"][:6]:
        items.append({"k": kat[p["kategorien"][0]]["tamil"], "text": p["titel"], "href": article_link(p)})
    return items


def source_count() -> int:
    try:
        import tomllib
        return len(tomllib.loads((REPO / "sources.toml").read_text(encoding="utf-8")).get("source", []))
    except Exception:  # noqa: BLE001
        return 0


def build_context(bare: bool = False) -> dict:
    site, ev, data = load_site(), load_events(), load_posts()
    site = {**site, **site["site"]}  # site.name/claim/tagline/org neben site.kontakt usw.
    posts = data["posts"]
    sel = select(posts, site)
    kt = ev["kino_termine"]
    kt["liste_html"] = render_kino_liste(kt["fakten"])
    kt["bild"] = {"src": f"img/ev-{kt['slug']}.jpg", "w": 1200, "h": 675}
    for e in ev["events"]:
        e["bild"] = {"src": f"img/p{e['bild_post']}.jpg"} if e.get("bild_post") and e["bild_post"] in sel["by_id"] else {"src": f"img/ev-{e['slug']}.jpg"}
        e["bild"].setdefault("w", 1200)
        e["bild"].setdefault("h", 675)
        e["datum_text"] = fmt_range(e["von"], e.get("bis"))
        e["seite"] = f"event-{e['slug']}.html"
    rezept = split_recipe(sel["rezept"]["inhalt_html"]) if sel["rezept"] else None
    stand = date.fromisoformat(site["stand"])
    orte = radar_orte(site, ev, sel["by_id"])
    radar = {
        "svg": radar_map.svg(orte), "orte": orte, "erfasst": erfasst_log(orte),
        "stats": {"orte": len(orte), "meldungen": sum(len(o["labels"]) for o in orte), "quellen": source_count(), "kinos": len(kt["fakten"]["kinos"])},
        "footer_svg": radar_map.svg([], sweep=False),
    }
    seiten = {pg["slug"]: pg for pg in data.get("seiten", [])}
    tv = dict(site.get("tv", {}))
    if "tv" in seiten:
        tv["seite"] = seiten["tv"]
    return {
        "radar": radar, "ticker": ticker_items(sel, ev, site["kategorien"]), "seiten": seiten, "production": {**site.get("production", {}), **sel["production"]},
        "tv": tv, "werbung_live": site.get("werbung_live", {}), "logo": (IMG / "logo.png").exists(),
        "site": site, "kat": site["kategorien"], "nav": site["nav"], "sel": sel, "posts": posts, "counts": data["counts"],
        "events": ev["events"], "event_months": event_months(ev["events"]), "grid": month_grid(2026, 10, ev["events"]),
        "kino": kt, "kino_widget": kino_widget(kt["fakten"]), "rezept": rezept, "shift_days": data["shift_days"],
        "stand": site["stand"], "stand_text": fmt_date(site["stand"], weekday=True), "jahr": stand.year,
        "fmt_date": fmt_date, "fmt_range": fmt_range, "ad_slot": lambda key: ad_slot(key, site), "format_date_de": format_date_de,
    }


def article_link(p: dict) -> str:
    return f"artikel-{p['slug']}.html"


def split_body(body: str, after: int = 2, min_paragraphs: int = 4) -> tuple[str, str]:
    """Teilt den Fließtext nach dem n-ten Absatz (für den In-Article-Werbeplatz), nur ab min_paragraphs Absätzen."""
    ends = [m.end() for m in re.finditer(r"</p>", body)]
    if len(ends) < min_paragraphs:
        return body, ""
    cut = ends[after - 1]
    return body[:cut], body[cut:]


def _lum(hex_color: str) -> float:
    r, g, b = (int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: str, b: str) -> str:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return f"{(la + 0.05) / (lb + 0.05):.1f}:1"


def render_all(out: Path, bare_index: bool = False) -> list[str]:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True, undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.filters["link"] = article_link
    env.filters["datum"] = fmt_date
    env.filters["split_body"] = split_body
    env.globals["contrast"] = contrast
    ctx = build_context(bare=bare_index)
    out.mkdir(parents=True, exist_ok=True)
    pages: list[tuple[str, str, dict]] = [("index.html", "index.html", {"seite": "start", "titel": "Tamil.de – Nachrichten, Kino und Community", "bare": bare_index})]
    for slug, k in ctx["kat"].items():
        pages.append((f"kategorie-{slug}.html", "kategorie.html", {"seite": slug, "slug": slug, "k": k, "titel": f"{k['label']} – Tamil.de"}))
    for p in ctx["posts"]:
        pages.append((article_link(p), "artikel.html", {"seite": p["kategorien"][0], "p": p, "titel": f"{p['titel']} – Tamil.de"}))
    pages.append((f"{ctx['kino']['slug']}.html", "artikel.html", {"seite": "kino", "p": None, "kinotermine": True, "titel": f"{ctx['kino']['titel']} – Tamil.de"}))
    pages.append(("events.html", "events.html", {"seite": "events", "titel": "Events – Tamil.de"}))
    for e in ctx["events"]:
        pages.append((e["seite"], "event.html", {"seite": "events", "e": e, "titel": f"{e['titel']} – Tamil.de"}))
    pages.append(("kontakt.html", "kontakt.html", {"seite": "kontakt", "titel": "Kontakt & Werben – Tamil.de"}))
    pages.append(("production.html", "production.html", {"seite": "production", "titel": f"{ctx['production']['titel']} – Tamil.de"}))
    pages.append(("tv.html", "tv.html", {"seite": "tv", "titel": "Tamil TV – Tamil.de"}))
    for slug, pg in ctx["seiten"].items():
        if pg["datei"] and slug != "tv":
            pages.append((pg["datei"], "seite.html", {"seite": pg.get("kategorie") or "seite", "pg": pg, "titel": f"{pg['titel']} – Tamil.de"}))
    pages.append(("design-system.html", "design-system.html", {"seite": "design", "titel": "Design-System – Tamil.de Prototyp"}))
    written = []
    for filename, template, extra in pages:
        local = dict(ctx)
        local.update(extra)
        local["bare"] = bool(extra.get("bare", False))
        local.setdefault("kinotermine", False)
        (out / filename).write_text(env.get_template(template).render(**local), encoding="utf-8")
        written.append(filename)
    for name in ("styles.css", "app.js"):
        shutil.copy(STATIC / name, out / name)
    for folder in ("img", "fonts"):
        if (out / folder).exists():
            shutil.rmtree(out / folder)
        shutil.copytree(STATIC / folder, out / folder)
    return written


def check_links(out: Path) -> list[str]:
    """Alle internen Links, Bilder und Assets müssen in dist/ existieren; keine http://-Bilder."""
    problems = []
    for page in sorted(out.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for attr, ref in re.findall(r"(href|src)=\"([^\"#]+)\"", text):
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                if attr == "src" and ref.startswith("http://"):
                    problems.append(f"{page.name}: http-Bild {ref}")
                continue
            if not (out / ref.split("?")[0]).exists():
                problems.append(f"{page.name}: fehlt {ref}")
        if "<title>" not in text:
            problems.append(f"{page.name}: kein <title>")
    return problems


def build(out: Path = DIST, bare_index: bool = False) -> list[str]:
    written = render_all(out, bare_index=bare_index)
    problems = check_links(out)
    if problems:
        for p in problems[:40]:
            print("FEHLER", p, file=sys.stderr)
        raise SystemExit(f"{len(problems)} Probleme in {out}")
    print(f"{out.name}: {len(written)} Seiten")
    return written


SHOT_PAGES = ["index.html", "kategorie-kino.html", "kategorie-kueche.html", "artikel-{hero}", "artikel-{rezept}",
              "{kino}", "events.html", "{event}", "kontakt.html", "production.html", "tv.html", "impressum.html", "design-system.html"]
SHOT_WIDTHS = (390, 820, 1280)


def shots(dist: Path = DIST, widths=SHOT_WIDTHS, only: str | None = None) -> list[Path]:
    from playwright.sync_api import sync_playwright
    ctx = build_context()
    names = {"hero": article_link(ctx["sel"]["hero"][1]).removeprefix("artikel-"), "rezept": article_link(ctx["sel"]["rezept"]).removeprefix("artikel-"),
             "kino": ctx["kino"]["slug"] + ".html", "event": ctx["events"][3]["seite"]}
    pages = [p.format(**names) for p in SHOT_PAGES]
    if only:
        pages = [p for p in pages if only in p]
    SHOTS.mkdir(exist_ok=True)
    files = []
    with sync_playwright() as pw:
        kwargs = {"args": ["--no-sandbox"]}
        if CHROMIUM.exists():
            kwargs["executable_path"] = str(CHROMIUM)
        browser = pw.chromium.launch(**kwargs)
        for width in widths:
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
            for name in pages:
                page.goto((dist / name).resolve().as_uri())
                page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => { i.loading = 'eager'; })")
                page.wait_for_function("[...document.images].every(i => i.complete)", timeout=15000)
                page.evaluate("""async () => { const h = document.body.scrollHeight; for (let y = 0; y < h; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } }""")  # Zähler auslösen
                page.wait_for_timeout(1200)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(900)
                target = SHOTS / f"{name.removesuffix('.html')[:40]}-{width}.png"
                if name == "index.html" and width <= 600:
                    page.screenshot(path=str(SHOTS / f"index-{width}-viewport.png"), full_page=False)
                    files.append(SHOTS / f"index-{width}-viewport.png")
                page.evaluate("document.querySelectorAll('#ad-mobile, .fab-wa').forEach(e => e.remove())")  # fixierte Elemente nur im Viewport-Shot
                page.screenshot(path=str(target), full_page=True)
                scroll_w = page.evaluate("document.documentElement.scrollWidth")
                if scroll_w > width:
                    print(f"WARNUNG {name} @{width}: horizontal scrollbar ({scroll_w}px)", file=sys.stderr)
                files.append(target)
            page.close()
        browser.close()
    print(f"shots/: {len(files)} Screenshots")
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["snapshot", "build", "shots", "artifact", "all"])
    ap.add_argument("--export", type=Path, default=REPO / "export", help="Ordner mit dem Export von tools/export_site.py")
    ap.add_argument("--no-shift", action="store_true", help="Datumsangaben nicht in die Gegenwart verschieben")
    ap.add_argument("--only", help="shots: nur Seiten, deren Name dies enthält")
    args = ap.parse_args(argv)
    if args.cmd == "snapshot":
        snapshot(args.export, shift_dates=not args.no_shift)
    if args.cmd in ("build", "all"):
        build(DIST)
    if args.cmd in ("shots", "all"):
        shots(DIST, only=args.only)
    if args.cmd in ("artifact", "all"):
        build(DIST_ARTIFACT, bare_index=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
