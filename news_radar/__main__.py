"""CLI: python -m news_radar <befehl>

  run       Ein Lauf (für den systemd-Timer alle 3 Minuten); --max-age-hours 336 für die Erstbefüllung;
            --ohne-ki legt Rohfassungen ohne Claude an (Titel + Quellentext, klar markiert)
  loop      Dauerbetrieb, Lauf alle --interval Sekunden (Standard 180)
  scan      Nur einsammeln + filtern, nichts schreiben (Test der Quellen)
  publish   Alle freigegebenen Entwürfe nach WordPress veröffentlichen (--pruefen: nur Verbindung testen)
  digest    Tageszusammenfassung senden (für den Digest-Timer)
  web       Freigabe-App lokal starten (Entwicklung; Produktion: gunicorn)
  style     Stilbeispiele aus veröffentlichten Tamil.de-Beiträgen lernen
  export    Protokoll als JSONL exportieren
  export-drafts  Entwürfe + Bilder für den HTML-Prototyp exportieren (--quellbilder lädt Vorschaubilder der Quellen)
  agent     export: Aufgabenmappe für einen schreibenden Agenten · import: fertige Beiträge übernehmen (mit Bild)
  bildpool  status | fuellen – Reserve-Bilder je Thema über die Bild-KI anlegen
  quellen   pruefen – jede Quelle live abfragen und bewerten (data/quellen-pruefung.csv) · liste – Register zeigen
  kosten    Kosten je Rolle, Modell und Tag, Budgetstand; --csv für die Fremdkostenabrechnung
  worker    Redaktion v2: Jobs abarbeiten (Dienst; --einmal leert die Schlange und beendet)
  dossier   Entwurf als Dossier recherchieren lassen (--entwurf ID)
  nutzer    anlegen | sperren | liste – Benutzer der Freigabe-App (Rollen redaktion, admin)
  sicherung erstellen | pruefen | wiederherstellen – Datenbank und Bilder (deploy/backup.sh, deploy/restore.sh)
  bericht   --woche: Annahmequote, Fehler, Kosten je Artikel der letzten 7 Tage
  abnahme   51 Szenarien mit FakeClaude durchspielen, Kriterien K1–K9 messen (--bericht Datei)
  bewertung vergleich (Sonnet vs. Opus blind, braucht Schlüssel) | bogen (letzte Entwürfe) | auswerten

Mit RADAR_WORKFLOW=v2 legt `run` Storys und Jobs an (Redaktion v2); `run --mit-jobs` arbeitet sie bis zur Deadline ab.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import requests

from . import filtering, notify, pipeline, sources
from .config import load_settings
from .store import Store
from .writer import STYLE_FILE, RawWriter

KEY_HINT = ("ANTHROPIC_API_KEY fehlt – Schlüssel in .env oder als Secret setzen, "
            "oder `run --ohne-ki` für Rohfassungen ohne KI.")


def pick_writer(ohne_ki: bool, settings):
    """None = Standard-Writer (Claude) wird im Lauf gebaut; RawWriter bei --ohne-ki.

    Ohne Schlüssel und ohne --ohne-ki brechen wir mit Hinweis ab – ein stiller Fallback würde die
    Warteschlange im Betrieb unbemerkt mit Rohfassungen füllen.
    """
    if ohne_ki:
        return RawWriter(settings)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(KEY_HINT)
    return None


def cmd_style(site: str, count: int) -> int:
    resp = requests.get(
        f"{site.rstrip('/')}/wp-json/wp/v2/posts",
        params={"per_page": 30, "_fields": "title,content"},
        headers={"User-Agent": sources.USER_AGENT},
        timeout=20,
    )
    resp.raise_for_status()
    examples = []
    for post in resp.json():
        text = sources.clean_text(re.sub(r"</p>", "\n", post["content"]["rendered"]))
        text = re.sub(r"Share on:.*$", "", text).strip()
        words = len(text.split())
        if 150 <= words <= 700:
            examples.append({"title": sources.clean_text(post["title"]["rendered"]), "text": text[:2200]})
        if len(examples) >= count:
            break
    STYLE_FILE.write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(examples)} Stilbeispiele gespeichert in {STYLE_FILE}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="news_radar", description="Tamil.de News-Radar")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--max-age-hours", type=int, help="z. B. 336 für die Erstbefüllung (14 Tage)")
    run.add_argument("--ohne-ki", action="store_true", help="Rohfassungen ohne Claude (Titel + Quellentext, markiert)")
    run.add_argument("--mit-jobs", action="store_true", help="v2: Jobs im selben Lauf bis zur Deadline abarbeiten")
    run.add_argument("--v1", action="store_true", help="bisherigen Ablauf erzwingen, auch wenn RADAR_WORKFLOW=v2")
    loop = sub.add_parser("loop")
    loop.add_argument("--interval", type=int, default=180)
    loop.add_argument("--ohne-ki", action="store_true", help=argparse.SUPPRESS)
    expd = sub.add_parser("export-drafts")
    expd.add_argument("--file", default="prototyp/content/radar.json")
    expd.add_argument("--bilder", help="Zielordner für die Beitragsbilder (z. B. prototyp/static/img/radar)")
    expd.add_argument("--quellbilder", action="store_true", help="Vorschaubilder der Quellen laden (nur Prototyp)")
    expd.add_argument("--limit", type=int, default=60)
    sub.add_parser("scan")
    pub = sub.add_parser("publish")
    pub.add_argument("--pruefen", action="store_true", help="nur die Verbindung zu WordPress prüfen, nichts veröffentlichen")
    sub.add_parser("digest")
    web = sub.add_parser("web")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8787)
    style = sub.add_parser("style")
    style.add_argument("--site", default="https://www.tamil.de")
    style.add_argument("--count", type=int, default=6)
    exp = sub.add_parser("export")
    exp.add_argument("--file", default="radar-protokoll.jsonl")
    agent = sub.add_parser("agent", help="Agent-Modus: Aufgabenmappe exportieren / fertige Beiträge importieren")
    agent.add_argument("aktion", choices=("export", "import"))
    agent.add_argument("--file", required=True, help="Aufgabenmappe (export) bzw. Ergebnis-JSON (import)")
    agent.add_argument("--limit", type=int, default=20, help="export: höchstens so viele Entwürfe")
    agent.add_argument("--alle", action="store_true", help="export: auch Entwürfe, die keine Rohfassung sind")
    agent.add_argument("--status", default="neu", help="export: Status der Entwürfe (kommagetrennt)")
    agent.add_argument("--ohne-text", action="store_true", help="export: Quelltexte nicht nachladen")
    agent.add_argument("--von", default="agent", help="import: Name für Protokoll und bearbeitet_von")
    agent.add_argument("--v2", action="store_true", help="Redaktion v2: Evidenzpakete statt Rohfassungen")
    pool = sub.add_parser("bildpool", help="Reserve-Bilder je Thema (prompts/bildpool.md)")
    pool.add_argument("aktion", choices=("status", "fuellen"))
    pool.add_argument("--thema", help="nur dieses Thema füllen")
    pool.add_argument("--anzahl", type=int, default=3, help="Zielbestand je Thema")
    pool.add_argument("--mit-budget", action="store_true", help="Kosten messen und am Budget stoppen (für den Timer)")
    quellen = sub.add_parser("quellen", help="Quellen-Register prüfen bzw. anzeigen")
    quellen.add_argument("aktion", choices=("pruefen", "liste"))
    quellen.add_argument("--file", default="data/quellen-pruefung.csv")
    quellen.add_argument("--aktiv", type=int, default=20, help="pruefen: so viele Quellen empfehlen")
    wk = sub.add_parser("worker", help="Redaktion v2: Jobs abarbeiten")
    wk.add_argument("--parallel", type=int, help="Anzahl paralleler Jobs (Standard RADAR_PARALLEL_JOBS)")
    wk.add_argument("--einmal", action="store_true", help="Schlange leeren und beenden")
    ds = sub.add_parser("dossier", help="Entwurf als Dossier recherchieren lassen")
    ds.add_argument("--entwurf", type=int, required=True)
    nu = sub.add_parser("nutzer", help="Benutzer der Freigabe-App")
    nu.add_argument("aktion", choices=("anlegen", "sperren", "liste"))
    nu.add_argument("name", nargs="?")
    nu.add_argument("--rolle", default="redaktion", choices=("redaktion", "admin"))
    sich = sub.add_parser("sicherung", help="Sicherung und Wiederherstellung")
    sich.add_argument("aktion", choices=("erstellen", "pruefen", "wiederherstellen"))
    sich.add_argument("--ziel", default="", help="Ordner der Sicherungen (Standard: <App>/backup)")
    sich.add_argument("--datum", default="", help="pruefen/wiederherstellen: Stand YYYY-MM-DD")
    ber = sub.add_parser("bericht", help="Wochenbericht der Redaktion")
    ber.add_argument("--woche", action="store_true", help="letzte 7 Tage (Standard)")
    ber.add_argument("--tage", type=int, default=7)
    bw = sub.add_parser("bewertung", help="Blindbewertung der Texte (Pilot)")
    bw.add_argument("aktion", choices=("vergleich", "bogen", "auswerten"))
    bw.add_argument("--anzahl", type=int, default=10)
    bw.add_argument("--ordner", default="data/bewertung")
    ab = sub.add_parser("abnahme", help="Abnahme-Szenarien mit FakeClaude")
    ab.add_argument("--bericht", default="data/abnahme-bericht.md")
    ab.add_argument("--nur", type=int, nargs="*", help="nur diese Szenario-Nummern")
    kosten = sub.add_parser("kosten", help="Kosten je Rolle/Modell/Tag und Budgetstand")
    kosten.add_argument("--tage", type=int, default=30)
    kosten.add_argument("--csv", help="alle Aufrufe des Zeitraums als CSV (Fremdkostenabrechnung)")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("httpx", "urllib3", "anthropic", "werkzeug"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    if args.cmd == "style":
        return cmd_style(args.site, args.count)

    if args.cmd == "abnahme":
        from . import abnahme

        ergebnisse = abnahme.alle(args.nur)
        text = abnahme.bericht(ergebnisse)
        Path(args.bericht).parent.mkdir(parents=True, exist_ok=True)
        Path(args.bericht).write_text(text, encoding="utf-8")
        for e in ergebnisse:
            print(f"{'ok  ' if e.ok else 'FEHL'} {e.szenario.nr:2} {e.szenario.name}"
                  + ("" if e.ok else f"  → {'; '.join(e.abweichungen or [k for k, v in e.kriterien.items() if not v])}"))
        bestanden = sum(1 for e in ergebnisse if e.ok)
        print(f"\n{bestanden} von {len(ergebnisse)} Szenarien bestanden → {args.bericht}")
        return 0 if bestanden == len(ergebnisse) else 1

    settings = load_settings()

    if args.cmd == "scan":
        with Store(settings.db_path) as store:
            items = sources.fetch_all(settings, store)
            picked = filtering.select(items, settings, store.seen_uids(), store.recent_titles())
        print(f"\n{len(items)} gesammelt · {len(picked)} relevant\n")
        for i in picked[:40]:
            print(f"{i.score:3} {i.dach_score:2} {i.kind:5} {i.category_hint:13} {i.ort[:12]:12} {i.published:%d.%m %H:%M}  {i.title[:80]}")
        return 0

    if args.cmd == "quellen":
        if args.aktion == "liste":
            for q in settings.alle_quellen:
                print(f"{'an ' if q.enabled else 'aus'}  {q.prioritaet}  {q.type:12} {q.kind:5} {q.country or '–':4} {q.name}")
            print(f"\n{len(settings.sources)} von {len(settings.alle_quellen)} Quellen aktiv")
            return 0
        from .quellencheck import pruefen

        with Store(settings.db_path) as store:
            ranking = pruefen(settings, store, Path(args.file), aktiv=args.aktiv)
        print(f"\n{'Punkte':>6}  {'jetzt':>5} {'14 T.':>5} {'Entw.':>5}  robots    Empfehlung  Quelle")
        for p in ranking:
            print(f"{p.punkte:6.1f}  {p.treffer_jetzt:5} {p.treffer_14_tage:5} {p.entwuerfe_db:5}  {p.robots:9} "
                  f"{p.empfehlung:11} {p.name}{'  (' + p.fehler + ')' if p.fehler else ''}")
        print(f"\n→ {args.file}")
        return 0

    if args.cmd == "sicherung":
        from . import sicherung

        ziel = Path(args.ziel) if args.ziel else settings.data_dir.parent / "backup"
        if args.aktion == "erstellen":
            out = sicherung.erstellen(settings.data_dir, ziel)
            print(f"Sicherung: {out['datenbank']} · {out['bilder']}")
            return 0
        if not args.datum:
            raise SystemExit("--datum YYYY-MM-DD fehlt")
        if args.aktion == "pruefen":
            print(sicherung.pruefen(ziel / f"radar-{sicherung.stand(args.datum)}.sqlite"))
            return 0
        print(f"Wiederhergestellt: {sicherung.wiederherstellen(settings.data_dir, ziel, args.datum)}")
        return 0

    if args.cmd == "bericht":
        from .workflow import repo

        with Store(settings.db_path) as store:
            print(repo.wochenbericht_text(store, args.tage))
        return 0

    if args.cmd == "bewertung":
        from . import bewertung

        ordner = Path(args.ordner)
        if args.aktion == "auswerten":
            for modell, werte in bewertung.auswerten(ordner / "bogen.csv", ordner / "schluessel.json").items():
                print(f"{modell:20} {werte}")
            return 0
        with Store(settings.db_path) as store:
            if args.aktion == "bogen":
                print(f"Bogen → {bewertung.bogen_aus_entwuerfen(store, settings, ordner, args.anzahl)}")
                return 0
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise SystemExit("Der Modellvergleich braucht ANTHROPIC_API_KEY (zwei Textaufrufe je Story).")
            from .workflow import orchestrator

            out = bewertung.vergleich(orchestrator.kontext(settings, store), ordner, args.anzahl)
        print(f"{out['storys']} Storys, {out['fassungen']} Fassungen → {out['bogen']} (Schlüssel erst nach der Bewertung öffnen)")
        return 0

    if args.cmd == "kosten":
        from .workflow import repo
        from .workflow.providers import budget_fuer

        with Store(settings.db_path) as store:
            bericht = repo.kosten_bericht(store, args.tage)
            stand = budget_fuer(settings, store).stand()
            if args.csv:
                import csv

                zeilen = repo.usage_zeilen(store, args.tage)
                with open(args.csv, "w", newline="", encoding="utf-8") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(zeilen[0]) if zeilen else ["id"])
                    w.writeheader()
                    w.writerows(zeilen)
                print(f"{len(zeilen)} Aufrufe → {args.csv}")
        print(f"Budget heute ${stand['tag_usd']:.2f} von ${stand['tag_limit']:.2f} · Monat ${stand['monat_usd']:.2f} "
              f"von ${stand['monat_limit']:.2f}{' · STOPP' if stand['stopp'] else (' · Warnung' if stand['warnung'] else '')}")
        print(f"Letzte {bericht['tage']} Tage: ${bericht['gesamt_usd']:.2f} für {bericht['entwuerfe']} Entwürfe"
              + (f" (${bericht['je_entwurf_usd']:.3f} je Entwurf)" if bericht["je_entwurf_usd"] else ""))
        for r in bericht["je_rolle"]:
            print(f"  {r['rolle']:12} {r['aufrufe']:5} Aufrufe  ${r['usd'] or 0:8.4f}  Fehlversuche {r['fehlversuche']}")
        return 0

    if args.cmd == "export":
        with Store(settings.db_path) as store:
            n = store.export_log(Path(args.file))
        print(f"{n} Protokolleinträge → {args.file}")
        return 0

    if args.cmd == "agent" and args.v2:
        from .agent_v2 import export_v2, import_v2

        with Store(settings.db_path) as store:
            if args.aktion == "export":
                data = export_v2(store, settings, Path(args.file), limit=args.limit)
                print(f"{len(data['storys'])} Storys → {args.file} "
                      f"({sum(len(p['dokumente']) for p in data['storys'])} Dokumente)")
                return 0
            stats = import_v2(store, settings, Path(args.file), von=args.von)
        print(f"{stats['entwuerfe']} Entwürfe, {stats['recherche_noetig']} „Recherche nötig“, {stats['verworfen']} verworfen, "
              f"{len(stats['fehler'])} Fehler")
        for f in stats["fehler"]:
            print(f"  ! {f}")
        return 1 if stats["fehler"] and not stats["entwuerfe"] else 0

    if args.cmd == "nutzer":
        from getpass import getpass

        from .workflow import repo

        with Store(settings.db_path) as store:
            if args.aktion == "liste":
                for n in repo.nutzer_liste(store):
                    print(f"{n['name']:20} {n['rolle']:10} {'aktiv' if n['aktiv'] else 'gesperrt':9} letzter Login {n['letzter_login'] or '–'}")
                return 0
            if not args.name:
                raise SystemExit("Name fehlt: nutzer anlegen NAME [--rolle admin]")
            if args.aktion == "sperren":
                print("gesperrt" if repo.nutzer_sperren(store, args.name) else "unbekannt")
                return 0
            passwort = os.environ.get("RADAR_NEUES_PASSWORT") or getpass(f"Passwort für {args.name} (mind. 10 Zeichen): ")
            repo.nutzer_anlegen(store, args.name, passwort, args.rolle)
        print(f"{args.name} angelegt ({args.rolle})")
        return 0

    if args.cmd == "dossier":
        from .workflow.orchestrator import dossier_anlegen

        with Store(settings.db_path) as store:
            sid = dossier_anlegen(store, args.entwurf, von="cli")
        print(f"Dossier-Story {sid} angelegt – der Worker recherchiert sie (Opus schreibt)")
        return 0

    if args.cmd == "worker":
        from .workflow import orchestrator

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(KEY_HINT.replace("`run --ohne-ki` für Rohfassungen ohne KI",
                                              "`agent export --v2` für Research per Zuruf"))
        stats = orchestrator.worker(settings, parallel=args.parallel, einmal=args.einmal)
        print(", ".join(f"{k} {v}" for k, v in stats.items()) or "keine Jobs")
        return 0

    if args.cmd == "agent":
        from .agent import export_tasks, import_results

        with Store(settings.db_path) as store:
            if args.aktion == "export":
                data = export_tasks(store, settings, Path(args.file), statuses=tuple(s.strip() for s in args.status.split(",")),
                                    nur_roh=not args.alle, limit=args.limit, mit_text=not args.ohne_text)
                mit_text = sum(1 for e in data["entwuerfe"] if e["quelltext"])
                print(f"{len(data['entwuerfe'])} Entwürfe → {args.file} ({mit_text} mit Quelltext, "
                      f"{len(data['bildthemen'])} Bildthemen, Pool: {sum(s['anzahl'] for s in data['bildpool'].values())} Bilder)")
                return 0
            stats = import_results(store, settings, Path(args.file), von=args.von)
        bilder = ", ".join(f"{k} {v}" for k, v in stats["bilder"].items()) or "–"
        print(f"{stats['uebernommen']} übernommen (Bilder: {bilder}), {stats['verworfen']} verworfen, "
              f"{len(stats['fehler'])} Fehler")
        for f in stats["fehler"]:
            print(f"  ! {f}")
        return 1 if stats["fehler"] and not stats["uebernommen"] else 0

    if args.cmd == "bildpool":
        from .bilder import BildPool

        pool = BildPool(settings.bildpool_dir)
        if args.aktion == "fuellen":
            if not settings.gemini_key:
                raise SystemExit("GEMINI_API_KEY fehlt – ohne Bild-KI lässt sich der Pool nicht füllen.")
            if args.mit_budget:
                from .workflow.providers import budget_fuer

                with Store(settings.db_path) as store:
                    erzeugt = pool.fuellen(settings, thema=args.thema, anzahl=args.anzahl, store=store,
                                           budget=budget_fuer(settings, store))
            else:
                erzeugt = pool.fuellen(settings, thema=args.thema, anzahl=args.anzahl)
            print(f"{sum(erzeugt.values())} Bilder erzeugt: " + (", ".join(f"{t} +{n}" for t, n in erzeugt.items()) or "nichts fehlte"))
        status = pool.status()
        print(f"Bildpool {settings.bildpool_dir}: {sum(s['anzahl'] for s in status.values())} Bilder in {len(status)} Themen")
        for thema, s in status.items():
            print(f"  {thema:20} {s['anzahl']:3} Bilder · {s['genutzt']:3}× genutzt")
        return 0

    if args.cmd == "export-drafts":
        from .export import export_drafts

        with Store(settings.db_path) as store:
            stats = export_drafts(store, Path(args.file), Path(args.bilder) if args.bilder else None,
                                  quellbilder=args.quellbilder, limit=args.limit, bilder_quelle=settings.bilder_dir)
        print(f"{stats['entwuerfe']} Entwürfe → {args.file} · {stats['quellbilder']} Quellbilder, "
              f"{stats['bildkarten']} Bildkarten, {stats['ohne_bild']} ohne Bild")
        return 0

    if args.cmd == "publish":
        if not settings.wordpress_enabled:
            print("Keine WordPress-Zugangsdaten in .env (WP_URL, WP_USER, WP_APP_PASSWORD).")
            return 1
        from .publisher import make_wordpress, publish_approved

        if args.pruefen:
            from .wordpress import TamilRadarClient

            wp = make_wordpress(settings)
            if isinstance(wp, TamilRadarClient):
                status = wp.status() or {}
                print(f"Plugin tamil-radar {status.get('plugin')} · WordPress {status.get('wordpress')} · SEO {status.get('seo')}"
                      f" · darf veröffentlichen: {'ja' if status.get('kann_publish') else 'nein (Beiträge gehen als „ausstehend“)'}")
                print("Kategorien: " + ", ".join(sorted(status.get("kategorien") or {})))
            else:
                print("Plugin tamil-radar antwortet nicht – der Radar nutzt die Core-REST (ohne Meta, Termine und Kinoliste).")
            return 0
        with Store(settings.db_path) as store:
            print(pipeline.summary(publish_approved(settings, store, limit=50)))
        return 0

    if args.cmd == "digest":
        with Store(settings.db_path) as store:
            print(notify.digest(settings, store))
        return 0

    if args.cmd == "web":
        from .web import create_app

        create_app(settings).run(host=args.host, port=args.port, debug=args.verbose)
        return 0

    if not settings.wordpress_enabled:
        logging.info("Keine WordPress-Zugangsdaten → Entwürfe warten in der Freigabe-App (%s)", settings.web_url)

    if args.cmd == "run" and settings.workflow == "v2" and not args.v1 and not args.ohne_ki:
        from .workflow import orchestrator

        if args.max_age_hours:
            settings.max_age_hours = args.max_age_hours
        stats = orchestrator.lauf(settings, mit_jobs=args.mit_jobs)
        print(", ".join(f"{k} {v}" for k, v in stats.items() if v))
        return 0

    writer = pick_writer(args.ohne_ki, settings)
    if writer is not None:
        logging.info("Rohfassungen ohne KI – jeder Entwurf wird als „Rohfassung“ markiert")

    if args.cmd == "run":
        if args.max_age_hours:
            settings.max_age_hours = args.max_age_hours
        print(pipeline.summary(pipeline.run(settings, writer=writer)))
        return 0

    while True:  # loop
        started = time.monotonic()
        try:
            print(pipeline.summary(pipeline.run(settings, writer=writer)), flush=True)
        except Exception:  # noqa: BLE001 - Dauerbetrieb nicht abbrechen
            logging.exception("Lauf fehlgeschlagen")
        time.sleep(max(5, args.interval - (time.monotonic() - started)))


if __name__ == "__main__":
    sys.exit(main())
