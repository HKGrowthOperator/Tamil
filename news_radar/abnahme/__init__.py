"""Abnahme der Redaktion v2: 50 Szenarien mit FakeClaude, jedes in einer eigenen Datenbank.

  python -m news_radar abnahme [--bericht data/abnahme-bericht.md] [--nur 12]

Je Szenario: Meldungen scannen, Jobs abarbeiten (mit Zeitraffer für Wiederholungen), Ergebnis aus der DB mit der
Erwartung vergleichen. Über alle Szenarien werden die Abnahmekriterien K1–K9 gemessen (keine unbelegte Kernaussage im
Entwurf, keine fremden Links, Budget eingehalten, jeder Aufruf gemessen, keine Doppel-Entwürfe, jedes Bild mit Lizenz,
Kino ohne Modell, kein Absturz, Erwartung erfüllt).
"""

from __future__ import annotations

import base64
import io
import json
import re
import tempfile
import traceback
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from .. import sources
from ..config import Settings, load_settings
from ..store import Store
from ..workflow import costs, jobs, orchestrator, repo
from ..workflow import fake as fake_mod
from ..workflow.fake import FakeAnthropic


@dataclass
class Szenario:
    nr: int
    name: str
    bereich: str
    meldungen: list[dict]
    erwartet: dict
    texte: dict[str, str] = field(default_factory=dict)
    vorlauf: list[dict] = field(default_factory=list)
    fake: dict = field(default_factory=dict)
    einstellungen: dict = field(default_factory=dict)
    suche: list[dict] = field(default_factory=list)
    nachher: str = ""


@dataclass
class Ergebnis:
    szenario: Szenario
    ok: bool
    abweichungen: list[str]
    fakten: dict
    kriterien: dict[str, bool]
    fehler: str = ""


class FakeFehler(Exception):
    """Simulierter API-Fehler (429, Timeout, 529)."""


# ---- Aufbau ---------------------------------------------------------------------------------------

def _datum(wert: str, now: datetime) -> str:
    m = re.fullmatch(r"([+-])(\d+)d", wert or "")
    if not m:
        return wert
    tage = int(m.group(2)) * (1 if m.group(1) == "+" else -1)
    return (now + timedelta(days=tage)).date().isoformat()


def meldung(d: dict, now: datetime) -> sources.NewsItem:
    fakten = d.get("fakten")
    if fakten:
        fakten = {k: (_datum(v, now) if isinstance(v, str) else v) for k, v in fakten.items()}
    item = sources.NewsItem(
        title=d["titel"], url=d.get("url") or f"https://www.example-news.de/{abs(hash(d['titel'])) % 10**8}",
        summary=d.get("zusammenfassung", ""), source=d.get("quelle", "Ruhr Nachrichten"),
        published=now - timedelta(hours=d.get("stunden", 1)), kind=d.get("art", "news"), language=d.get("sprache", "de"),
        facts=fakten, uid_override=d.get("uid", ""), image_url=d.get("bild", ""), ort=d.get("ort", ""),
        fingerprint=d.get("fingerprint", ""),
    )
    return item


def _antworten(sz: Szenario) -> tuple[dict, dict]:
    f = sz.fake
    antworten: dict[str, Any] = {}
    fehler: dict[str, Any] = {}
    r = f.get("recherche")
    if r:
        def recherche(user, system, req, art=r):
            out = fake_mod.recherche(user, system, req)
            if art == "leer":
                out["claims"] = []
            elif art == "widerspruch" and out["claims"]:
                kern = next((c for c in out["claims"] if c["kern"]), out["claims"][0])
                out["widersprueche"] = [{"claim_ids": [kern["id"]], "beschreibung": "Datum weicht zwischen Quellen ab"}]
            elif art == "fremde_quelle":
                out["claims"].append({"id": "C99", "aussage": "Erfundene Aussage", "art": "was", "kern": False,
                                      "quellen": ["Q9"], "fundstelle": "x", "sicherheit": 0.9, "support": "offen"})
            elif art == "erfunden":
                for c in out["claims"]:
                    c["fundstelle"] = "diese Stelle steht in keinem Dokument der Story"
            return out
        antworten["recherche"] = recherche
    fc = f.get("faktencheck")
    if fc:
        zaehler = Counter()

        def faktencheck(user, system, req, art=fc):
            out = fake_mod.faktencheck(user, system, req)
            zaehler["n"] += 1
            if out["saetze"]:
                if art == "kern_immer" or (art == "kern_einmal" and zaehler["n"] == 1):
                    out["saetze"][0].update(urteil="widerspruch", kern=True)
                elif art == "neben":
                    out["saetze"][0].update(urteil="ungedeckt", kern=False)
            return out
        antworten["faktencheck"] = faktencheck
    if f.get("signal"):
        rel = 8 if f["signal"] == "ja" else 2
        antworten["signal"] = lambda u, s, r: {"bewertungen": [
            {"nr": m["nr"], "relevanz": rel, "land": "DE", "grund": "Abnahme", "risiko": "keins"}
            for m in (fake_mod.block(u, "meldungen") or [])]}
    if f.get("cluster"):
        ja = f["cluster"] == "ja"
        antworten["cluster"] = lambda u, s, r: {"entscheidungen": [
            {"nr": p["nr"], "gleiche_story": ja, "grund": "Abnahme"} for p in (fake_mod.block(u, "paare") or [])]}
    if f.get("bild_prompt"):
        def text_mit_bild(user, system, req):
            out = fake_mod.text(user, system, req)
            out["bild_prompt"] = "Temple courtyard at dusk with oil lamps, wide angle, no people in focus"
            out["bild_thema"] = "tempelfest"
            return out
        antworten["text"] = text_mit_bild
    if f.get("seo_kaputt"):
        antworten["seo"] = {"falsch": 1}
    for rolle, art in (f.get("fehler") or {}).items():
        if art == "immer":
            fehler[rolle] = FakeFehler(f"{rolle}: Timeout")
        else:  # einmal: erster Aufruf scheitert (429), danach normal
            basis = antworten.get(rolle) or fake_mod.STANDARD[rolle]
            stand = Counter()

            def einmal(user, system, req, basis=basis, stand=stand, rolle=rolle):
                stand["n"] += 1
                if stand["n"] == 1:
                    raise FakeFehler(f"{rolle}: 429 rate limit")
                return basis(user, system, req)
            antworten[rolle] = einmal
    return antworten, fehler


def _png() -> bytes:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (1600, 900), (180, 40, 42)).save(buf, "PNG")
    return buf.getvalue()


def _settings(basis: Settings, data_dir: Path, sz: Szenario) -> Settings:
    from dataclasses import replace

    s = replace(basis, data_dir=data_dir, wp_url="", wp_user="", wp_app_password="", notify_webhook="",
                unsplash_key="", pexels_key="", gemini_key="", web_url="https://radar.test", workflow="v2")
    for k, v in sz.einstellungen.items():
        if not k.startswith("_"):  # _ohne_modell, _vorher_kosten steuern den Lauf, nicht die Settings
            setattr(s, k, v)
    if sz.einstellungen.get("gemini_key"):
        s.bild_retry_pause = 0
    return s


def _zeitraffer(ctx, runden: int = 8) -> Counter:
    gesamt: Counter = Counter()
    for _ in range(runden):
        gesamt.update(orchestrator.abarbeiten(ctx))
        offen = ctx.store.db.execute("SELECT COUNT(*) FROM workflow_jobs WHERE status = 'offen'").fetchone()[0]
        if not offen:
            break
        ctx.store.db.execute("UPDATE workflow_jobs SET naechster_versuch = '2000-01-01' WHERE status = 'offen'")
        ctx.store.db.commit()
    return gesamt


# ---- Ausführen und messen --------------------------------------------------------------------------

def ausfuehren(sz: Szenario, basis: Settings | None = None, ordner: Path | None = None) -> Ergebnis:
    basis = basis or load_settings()
    now = datetime.now(timezone.utc)
    tmp = Path(tempfile.mkdtemp(prefix=f"abnahme-{sz.nr:02d}-", dir=ordner))
    s = _settings(basis, tmp / "data", sz)
    antworten, fehler = _antworten(sz)
    client = FakeAnthropic(antworten, ablehnen=tuple(sz.fake.get("ablehnen", ())),
                           abschneiden=tuple(sz.fake.get("abschneiden", ())), fehler=fehler,
                           fallback_modell=sz.fake.get("fallback") or {})
    texte = sz.texte
    png = base64.b64encode(_png()).decode()
    kw = dict(fetch_text=lambda url: texte.get(url, ""), suche=lambda q: list(sz.suche),
              bild_transport=lambda h, b: (200, {"status": "completed", "outputs": [{"type": "image", "data": png}]}))
    stats: Counter = Counter()
    fehltext = ""
    with Store(s.db_path) as store:
        if sz.einstellungen.get("_ohne_modell"):  # nie den echten Client: Kontext ohne Modell von Hand
            from ..agents import Kontext

            ctx = Kontext(settings=s, store=store, budget=costs.Budget(store, s.budget_tag_usd, s.budget_monat_usd), **kw)
        else:
            ctx = orchestrator.kontext(s, store, client=client, **kw)
        if sz.einstellungen.get("_vorher_kosten"):
            from ..workflow.providers import usage_protokollieren

            usage_protokollieren(store, rolle="vorher", provider="vorlauf", modell="claude-sonnet-5-5",
                                 usd=float(sz.einstellungen["_vorher_kosten"]))
        try:
            if sz.vorlauf:
                stats.update(orchestrator.scan(ctx, [meldung(m, now) for m in sz.vorlauf]))
                _zeitraffer(ctx)
                stats = Counter()
            stats.update({k: v for k, v in orchestrator.scan(ctx, [meldung(m, now) for m in sz.meldungen]).items()
                          if isinstance(v, int)})
            stats.update({f"job_{k}": v for k, v in _zeitraffer(ctx).items()})
            if sz.nachher:
                stats.update(NACHHER[sz.nachher](ctx, sz, now))
        except Exception:  # noqa: BLE001 – ein Absturz ist selbst ein Abnahmefehler (K8)
            fehltext = traceback.format_exc(limit=6)
        fakten = _fakten(store, client, stats)
        kriterien = _kriterien(store, client, s, fehltext)
    abweichungen = _vergleichen(sz.erwartet, fakten) if not fehltext else [f"Absturz: {fehltext.splitlines()[-1]}"]
    kriterien["K9 Erwartung erfüllt"] = not abweichungen
    return Ergebnis(sz, not abweichungen and all(kriterien.values()), abweichungen, fakten, kriterien, fehltext)


def _fakten(store: Store, client: FakeAnthropic, stats: Counter) -> dict:
    drafts = store.list_drafts(limit=500)
    storys = repo.stories(store, limit=500)
    usage = [dict(r) for r in store.db.execute("SELECT * FROM agent_usage")]
    return {
        "entwuerfe": len(drafts),
        "storys": len(storys),
        "status": dict(Counter(s["status"] for s in storys)),
        "rollen": client.rollen(),
        "aufrufe": len(client.requests),
        "jobs": jobs.zaehlen(store),
        "hinweise": " | ".join(h for d in drafts for h in d["hinweise"]) + " | " +
                    " | ".join(s.get("notiz") or "" for s in storys),
        "bild": sorted({d["bild_origin"] for d in drafts if d.get("bild_origin")}),
        "typ": sorted({d["typ"] for d in drafts}),
        "kosten": round(sum(u["kosten_usd"] for u in usage), 6),
        "usage_status": sorted({u["status"] for u in usage}),
        "stats": dict(stats),
        "texte": " ".join((d.get("titel") or "") + " " + (d.get("inhalt_html") or "") for d in drafts),
        "laengen": sorted({s.get("laenge") or "" for s in storys}),
        "prio": sorted({j["prio"] for j in jobs.liste(store)}),
        "veroeffentlicht": sum(1 for d in drafts if d["status"] == "veroeffentlicht"),
        "dokumente": store.db.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0],
        "modelle": sorted({u["modell"] for u in usage if u["modell"]}),
        "ereignisse": sorted({r[0] for r in store.db.execute("SELECT DISTINCT event FROM log")}),
        "bloecke_dicht": all(
            r["user"].count(f"</{name}>") <= 1 for r in client.requests
            for name in ("dokumente", "meldungen", "story", "claims", "entwurf", "paare", "quellen")),
    }


def _vergleichen(erwartet: dict, f: dict) -> list[str]:
    ab: list[str] = []
    for key, soll in erwartet.items():
        if key in ("entwuerfe", "storys", "aufrufe", "veroeffentlicht"):
            if f[key] != soll:
                ab.append(f"{key}: {f[key]} statt {soll}")
        elif key == "aufrufe_max" and f["aufrufe"] > soll:
            ab.append(f"aufrufe: {f['aufrufe']} > {soll}")
        elif key == "status":
            for st, n in soll.items():
                if f["status"].get(st, 0) != n:
                    ab.append(f"Storys „{st}“: {f['status'].get(st, 0)} statt {n}")
        elif key == "jobs":
            for st, n in soll.items():
                if f["jobs"].get(st, 0) != n:
                    ab.append(f"Jobs „{st}“: {f['jobs'].get(st, 0)} statt {n}")
        elif key == "stats":
            for st, n in soll.items():
                if f["stats"].get(st, 0) != n:
                    ab.append(f"Scan „{st}“: {f['stats'].get(st, 0)} statt {n}")
        elif key == "rollen_mit":
            fehlt = [r for r in soll if r not in f["rollen"]]
            if fehlt:
                ab.append(f"Rollen fehlen: {fehlt}")
        elif key == "rollen_ohne":
            da = [r for r in soll if r in f["rollen"]]
            if da:
                ab.append(f"Rollen hätten nicht laufen dürfen: {da}")
        elif key == "rolle_anzahl":
            for r, n in soll.items():
                if f["rollen"].count(r) != n:
                    ab.append(f"Rolle {r}: {f['rollen'].count(r)}× statt {n}×")
        elif key == "hinweis":
            for teil in ([soll] if isinstance(soll, str) else soll):
                if teil not in f["hinweise"]:
                    ab.append(f"Hinweis fehlt: „{teil}“")
        elif key == "bild":
            if soll not in f["bild"]:
                ab.append(f"Bild {f['bild']} statt {soll}")
        elif key == "typ":
            if soll not in f["typ"]:
                ab.append(f"Typ {f['typ']} statt {soll}")
        elif key == "kosten_max" and f["kosten"] > soll:
            ab.append(f"Kosten ${f['kosten']} > ${soll}")
        elif key == "kosten_min" and f["kosten"] < soll:
            ab.append(f"Kosten ${f['kosten']} < ${soll}")
        elif key == "usage_status":
            for st in soll:
                if st not in f["usage_status"]:
                    ab.append(f"usage-Status {st} fehlt ({f['usage_status']})")
        elif key == "text_ohne":
            for teil in ([soll] if isinstance(soll, str) else soll):
                if teil.lower() in f["texte"].lower():
                    ab.append(f"Text enthält „{teil}“")
        elif key == "laenge":
            if soll not in f["laengen"]:
                ab.append(f"Länge {f['laengen']} statt {soll}")
        elif key == "prio":
            if soll not in f["prio"]:
                ab.append(f"Priorität {f['prio']} ohne {soll}")
        elif key == "dokumente" and f["dokumente"] != soll:
            ab.append(f"Dokumente: {f['dokumente']} statt {soll}")
        elif key == "modell" and soll not in f["modelle"]:
            ab.append(f"Modell {soll} fehlt ({f['modelle']})")
        elif key == "ereignis" and soll not in f["ereignisse"]:
            ab.append(f"Ereignis {soll} fehlt")
        elif key == "bloecke_dicht" and f["bloecke_dicht"] != soll:
            ab.append("Ein Datenblock wurde durch Text aus dem Netz geschlossen")
    return ab


def _kriterien(store: Store, client: FakeAnthropic, s: Settings, fehltext: str) -> dict[str, bool]:
    k: dict[str, bool] = {}
    drafts = store.list_drafts(limit=500)
    unbelegt = []
    fremde_links = []
    for d in drafts:
        if not d.get("story_id"):
            continue
        story = repo.story(store, d["story_id"])
        if story and story["typ"] != "kino" and not any("Agent-Modus" in h for h in d["hinweise"]):
            kern = [c for c in repo.claims(store, d["story_id"]) if c.kern]
            if any(c.support != "bestaetigt" for c in kern) or not kern:
                unbelegt.append(d["id"])
        urls = {doc.url for doc in repo.dokumente(store, d["story_id"])}
        for href in re.findall(r'href="([^"]+)"', d.get("inhalt_html") or ""):
            if href not in urls:
                fremde_links.append(href)
    k["K1 keine unbelegte Kernaussage im Entwurf"] = not unbelegt
    k["K2 Links nur auf Quellen der Story"] = not fremde_links
    kosten = store.db.execute("SELECT COALESCE(SUM(kosten_usd), 0) FROM agent_usage").fetchone()[0]
    k["K3 Budget eingehalten"] = kosten <= s.budget_tag_usd + 1e-9  # inkl. Vorbelastung (_vorher_kosten)
    anthropic_zeilen = store.db.execute("SELECT COUNT(*) FROM agent_usage WHERE provider = 'anthropic'").fetchone()[0]
    k["K4 jeder Modellaufruf gemessen"] = anthropic_zeilen == len(client.requests)
    doppelt = store.db.execute("SELECT COUNT(*) FROM (SELECT story_id FROM drafts WHERE story_id IS NOT NULL "
                               "GROUP BY story_id HAVING COUNT(*) > 1)").fetchone()[0]
    k["K5 keine Doppel-Entwürfe je Story"] = doppelt == 0
    ohne_lizenz = [d["id"] for d in drafts if d.get("bild_datei") and not (repo.asset_fuer_datei(store, d["bild_datei"]) or {}).get("lizenz")]
    k["K6 jedes Bild mit Lizenz"] = not ohne_lizenz
    kino_modell = store.db.execute(
        "SELECT COUNT(*) FROM agent_usage u JOIN stories s ON s.id = u.story_id WHERE s.typ = 'kino' "
        "AND u.provider = 'anthropic'").fetchone()[0]
    k["K7 Kino ohne Modellaufruf"] = kino_modell == 0
    k["K8 kein Absturz"] = not fehltext
    return k


# ---- Nachläufe ------------------------------------------------------------------------------------

def _kino_update(ctx, sz: Szenario, now: datetime) -> dict:
    neu = [meldung(m, now) for m in sz.erwartet.get("_update", [])]
    return {f"update_{k}": v for k, v in orchestrator.scan(ctx, neu).items() if isinstance(v, int)}


def _kino_nach_veroeffentlichung(ctx, sz: Szenario, now: datetime) -> dict:
    d = ctx.store.list_drafts("neu")[0]
    ctx.store.claim_draft(d["id"], von="abnahme")
    ctx.store.mark_published(d["id"], 900, "https://www.tamil.de/x/")
    return _kino_update(ctx, sz, now)


def _wp_timeout(ctx, sz: Szenario, now: datetime) -> dict:
    import requests

    from .. import publisher
    from ..wordpress import TamilRadarClient

    class Resp:
        def __init__(self, code, data):
            self.status_code, self._data, self.text = code, data, ""

        def json(self):
            return self._data

    class Session:
        def __init__(self):
            self.posts, self.headers, self.auth, self.verloren = {}, {}, None, True

        def request(self, method, url, timeout=None, json=None, **kw):
            uid = json["meta"]["radar_uid"]
            if uid in self.posts:
                return Resp(409, {"data": {"status": 409, "id": self.posts[uid], "link": "https://www.tamil.de/p/"}})
            self.posts[uid] = 700 + len(self.posts)
            if self.verloren:
                self.verloren = False
                raise requests.Timeout("Antwort verloren")
            return Resp(201, {"id": self.posts[uid], "link": "https://www.tamil.de/p/", "status": "publish"})

    session = Session()
    wp = TamilRadarClient("https://www.tamil.de", "u", "p", session=session)
    store = ctx.store
    d = store.list_drafts("neu")[0]
    store.set_status(d["id"], "freigeben", von="abnahme")
    publisher.publish_approved(ctx.settings, store, wp=wp)
    store.set_status(d["id"], "erneut", von="abnahme")
    publisher.publish_approved(ctx.settings, store, wp=wp)
    return {"wp_posts": len(session.posts)}


def _agent_v2(ctx, sz: Szenario, now: datetime) -> dict:
    from ..agent_v2 import export_v2, import_v2

    tmp = ctx.settings.data_dir
    mappe = export_v2(ctx.store, ctx.settings, tmp / "m.json", ctx=ctx)
    ergebnisse = []
    for p in mappe["storys"]:
        dokus = fake_mod.recherche("<dokumente>\n" + json.dumps(p["dokumente"]) + "\n</dokumente>", "", {})
        beitrag = fake_mod.text("<story>\n" + json.dumps({"titel": p["titel"], "ort": p["ort"]}) + "\n</story>\n<claims>\n"
                                + json.dumps(dokus["claims"]) + "\n</claims>", "", {})
        ergebnisse.append({"story_id": p["story_id"], "claims": dokus["claims"], "widersprueche": [], "beitrag": beitrag})
    (tmp / "e.json").write_text(json.dumps({"ergebnisse": ergebnisse}), encoding="utf-8")
    stats = import_v2(ctx.store, ctx.settings, tmp / "e.json", von="cloud-sitzung", ctx=ctx)
    return {"agent_entwuerfe": stats["entwuerfe"]}


def _quelle_ergaenzen(ctx, sz: Szenario, now: datetime) -> dict:
    sid = repo.stories(ctx.store, "recherche_erforderlich")[0]["id"]
    orchestrator.quelle_ergaenzen(ctx.store, sid, sz.erwartet["_url"], von="abnahme")
    return {f"nach_{k}": v for k, v in _zeitraffer(ctx).items()}


def _dossier(ctx, sz: Szenario, now: datetime) -> dict:
    d = ctx.store.list_drafts("neu")[0]
    orchestrator.dossier_anlegen(ctx.store, d["id"], von="abnahme")
    return {f"dossier_{k}": v for k, v in _zeitraffer(ctx).items()}


NACHHER: dict[str, Callable] = {
    "kino_update": _kino_update, "kino_veroeffentlicht": _kino_nach_veroeffentlichung, "wp_timeout": _wp_timeout,
    "agent_v2": _agent_v2, "quelle_ergaenzen": _quelle_ergaenzen, "dossier": _dossier,
}


def alle(nur: list[int] | None = None, basis: Settings | None = None, ordner: Path | None = None,
         behalten: bool = False) -> list[Ergebnis]:
    """Alle (oder die gewählten) Szenarien; die Datenbanken liegen unter <data>/abnahme-laeufe und werden danach
    gelöscht (mit `behalten` bleiben sie zum Nachsehen liegen)."""
    import shutil

    from .szenarien import SZENARIEN

    basis = basis or load_settings()
    wurzel = ordner or (basis.data_dir / "abnahme-laeufe")
    wurzel.mkdir(parents=True, exist_ok=True)
    lauf = Path(tempfile.mkdtemp(prefix="lauf-", dir=wurzel))
    try:
        return [ausfuehren(sz, basis, lauf) for sz in SZENARIEN if not nur or sz.nr in nur]
    finally:
        if not behalten:
            shutil.rmtree(lauf, ignore_errors=True)


def bericht(ergebnisse: list[Ergebnis]) -> str:
    ok = sum(1 for e in ergebnisse if e.ok)
    kriterien: dict[str, list[int]] = {}
    for e in ergebnisse:
        for name, wert in e.kriterien.items():
            kriterien.setdefault(name, [])
            if not wert:
                kriterien[name].append(e.szenario.nr)
    zeilen = [
        f"# Abnahme Redaktion v2 – {datetime.now(timezone.utc):%d.%m.%Y %H:%M} UTC",
        "",
        f"**{ok} von {len(ergebnisse)} Szenarien bestanden.** Alle Läufe mit FakeClaude (keine echten Modellaufrufe), "
        "jedes Szenario in einer eigenen Datenbank.",
        "",
        "## Kriterien",
        "",
        "| Kriterium | Ergebnis |",
        "|---|---|",
    ]
    for name, fehl in kriterien.items():
        zeilen.append(f"| {name} | {'erfüllt' if not fehl else 'verletzt in ' + ', '.join(map(str, fehl))} |")
    zeilen += ["", "## Szenarien", "", "| Nr. | Bereich | Szenario | Ergebnis | Entwürfe | Aufrufe | Kosten |", "|---|---|---|---|---|---|---|"]
    for e in ergebnisse:
        f = e.fakten
        status = "bestanden" if e.ok else "**nicht bestanden**: " + "; ".join(e.abweichungen or
                                                                              [k for k, v in e.kriterien.items() if not v])
        zeilen.append(f"| {e.szenario.nr} | {e.szenario.bereich} | {e.szenario.name} | {status} | {f.get('entwuerfe', '–')} "
                      f"| {f.get('aufrufe', '–')} | ${f.get('kosten', 0):.4f} |")
    return "\n".join(zeilen) + "\n"


__all__ = ["Szenario", "Ergebnis", "ausfuehren", "alle", "bericht", "date"]
