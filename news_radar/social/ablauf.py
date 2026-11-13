"""Ablauf F4: erkennen → Regelprüfung → vorbereiten → Karenz → senden (zuerst Instagram, dann Facebook) → Historie.

  python -m news_radar social lauf       (Dienst alle 3 Minuten, nur mit RADAR_SOCIAL=an)

Grundsätze (Vertrag §8, `.claude/rules/vertrag.md`):
- Der Altbestand löst nie etwas aus: der erste Lauf setzt nur die Startmarke; Beiträge davor und aus der Übernahme
  (`radar_uid` alt-…) werden übergangen.
- Höchstens einmal je Beitrag und Kanal (UNIQUE in der Datenbank); spätere Korrekturen am Artikel ändern nichts.
- Unmittelbar vor jedem Aufruf nach außen prüft der Ablauf den Stopp-Schalter des Kanals (und „alles“); jeder Schritt
  steht im Protokoll (`editorial_actions`) mit Kanal und Fassung des Regelwerks.
- Den Zustand „wird gesendet“ setzt ein bedingtes UPDATE (nur aus dem erwarteten Zustand); Stoppen im Cockpit setzt
  ebenso bedingt – wer zuerst schreibt, gewinnt, nie beide.
- Nach einem Abbruch beim Veröffentlichen wird nicht wiederholt: der nächste Lauf gleicht mit den letzten Beiträgen
  des Kontos ab; bleibt es unklar, entscheidet ein Mensch.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Callable

from .. import schalter
from ..store import now_iso
from ..workflow import repo
from . import ERLEDIGT, KANAELE, META_KANAELE, OFFEN, SYSTEM, bild, quelle, regelwerk
from .konfig import Konfig
from .transport import (GraphTransport, MetaFehler, TrockenTransport, UnklarFehler, WarteFehler, ZugangFehler)

TEXT_MAX = 2200          # Instagram
HASHTAGS_MAX = 30
CONTAINER_WARTEN = timedelta(minutes=5)
STARTMARKE = "startmarke"


def _iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat(timespec="seconds")


def _zeit(wert: str | None) -> datetime | None:
    if not wert:
        return None
    dt = datetime.fromisoformat(wert)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def transport_fuer(konf: Konfig, rw: regelwerk.Regelwerk | None = None):
    """Live nur mit RADAR_SOCIAL_LIVE, allen Schlüsseln und – falls übergeben – freigegebenem Regelwerk; `senden`
    prüft die Freigabe ohnehin noch einmal."""
    if konf.live and (rw is None or regelwerk.freigegeben(rw)):
        return GraphTransport(konf)
    return TrockenTransport()


def _protokoll(store, zeile: dict, aktion: str, notiz: str = "", *, wer: str = SYSTEM, ausloeser: str = "dienst",
               regel_fassung: str | None = None):
    """Zeile im Protokoll; `regel_fassung` ist die angewandte Fassung (Standard: die, nach der geprüft wurde)."""
    repo.aktion(store, wer=wer, aktion=aktion, gegenstand_typ="social", gegenstand_id=zeile["id"],
                kanal=zeile["kanal"], regel_fassung=regel_fassung or zeile["regel_fassung"],
                wp_post_id=zeile["wp_post_id"],
                notiz=notiz, ausloeser=ausloeser)


def _setzen(store, zeile_id: int, **felder) -> None:
    felder["aktualisiert"] = now_iso()
    spalten = ", ".join(f"{k} = ?" for k in felder)
    store._write(f"UPDATE social_beitraege SET {spalten} WHERE id = ?", (*felder.values(), zeile_id))


def _zeile(store, zeile_id: int) -> dict:
    return dict(store.db.execute("SELECT * FROM social_beitraege WHERE id = ?", (zeile_id,)).fetchone())


# ---- Startmarke ---------------------------------------------------------------------------------

def startmarke(store) -> datetime | None:
    row = store.db.execute("SELECT wert FROM social_stand WHERE schluessel = ?", (STARTMARKE,)).fetchone()
    return _zeit(row["wert"]) if row else None


def _startmarke_setzen(store, jetzt: datetime) -> None:
    store._write("INSERT OR IGNORE INTO social_stand (schluessel, wert, gesetzt) VALUES (?,?,?)",
                 (STARTMARKE, _iso(jetzt), now_iso()))
    repo.aktion(store, wer=SYSTEM, aktion="social_startmarke", gegenstand_typ="social", gegenstand_id=STARTMARKE,
                notiz=f"Altbestand bis {_iso(jetzt)} löst nichts aus", ausloeser="dienst")


# ---- Vorbereiten --------------------------------------------------------------------------------

def _termin_text(b: quelle.Beitrag) -> str:
    tag = regelwerk._event_tag(b.event_datum)
    if tag is None:
        return ""
    wann = tag.strftime("%d.%m.%Y, %H:%M Uhr") if isinstance(tag, datetime) else tag.strftime("%d.%m.%Y")
    return "Termin: " + " · ".join(t for t in (wann, b.event_ort) if t)


def text_bauen(b: quelle.Beitrag, rw: regelwerk.Regelwerk, rubrik: str, ki: bool, *, hashtags: bool = True,
               whatsapp_url: str = "") -> tuple[str, list[str]]:
    """Titel, Termin, Vorspann, Verweis auf tamil.de, KI-Hinweis, feste Hashtags der Rubrik; höchstens 2200 Zeichen
    (der Vorspann wird gekürzt). Instagram macht den Link nicht anklickbar – der Text verweist trotzdem auf tamil.de."""
    tags = list(rw.hashtags.get(rubrik) or [])[:HASHTAGS_MAX] if hashtags else []
    termin = _termin_text(b) if b.quelle_typ == "termin" else ""
    kopf = "\n".join(t for t in (b.titel, termin) if t)
    verweis = "\n".join(t for t in (f"Mehr auf tamil.de: {b.link}", rw.ki_hinweis if ki else "",
                                    f"WhatsApp-Kanal: {whatsapp_url}" if whatsapp_url else "") if t)
    schluss = " ".join(tags)
    rest = TEXT_MAX - len(kopf) - len(verweis) - len(schluss) - 6
    vorspann = b.vorspann if len(b.vorspann) <= rest else b.vorspann[:max(0, rest - 1)].rsplit(" ", 1)[0] + "…"
    return "\n\n".join(t for t in (kopf, vorspann, verweis, schluss) if t)[:TEXT_MAX], tags


def _bild(store, settings, b: quelle.Beitrag, rw: regelwerk.Regelwerk, rubrik: str) -> tuple[str, str, int | None, bool]:
    """(Dateiname, foto|karte, asset_id, ki_hinweis). Foto nur mit Umfang „social“ (R4), sonst Bildkarte."""
    ordner = settings.data_dir / "social"
    erlaubt, _grund = regelwerk.bild_social(b)
    if erlaubt:
        try:
            ki = b.bild_ki
            daten = bild.foto(b.bild_pfad.read_bytes(), nachweis=(b.asset or {}).get("attribution") or "",
                              ki_hinweis=rw.ki_hinweis if ki else "")
            return bild.ablegen(daten, ordner), "foto", (b.asset or {}).get("id"), ki
        except (OSError, ValueError) as exc:  # Datei kaputt: lieber die Karte als nichts
            store.event("social_bild_fehler", wp_post_id=b.wp_post_id, fehler=str(exc)[:200])
    label = next((c.label for c in settings.categories if c.slug == rubrik), rubrik.title() or "Tamil.de")
    return bild.ablegen(bild.karte(b.titel, label, rubrik), ordner), "karte", None, False


def erkennen(store, settings, abruf: quelle.Abruf, jetzt: datetime, rw: regelwerk.Regelwerk | None = None,
             whatsapp_url: str = "") -> Counter:
    """Neue Beiträge der Website holen, prüfen und vorbereiten. Gibt Zählungen zurück."""
    stats: Counter = Counter()
    sperre = schalter.haelt_an(store, KANAELE)
    if sperre is not None:
        stats["angehalten"] += 1
        return stats
    marke = startmarke(store)
    if marke is None:
        _startmarke_setzen(store, jetzt)
        stats["startmarke_gesetzt"] += 1
        return stats
    rw = rw or regelwerk.aktuell(store)
    posts: list[dict] = []
    for seite in range(1, 6):
        teil = abruf(quelle.abfrage(marke, jetzt, seite))
        posts.extend(teil)
        if len(teil) < 50:
            break
    for post in posts:
        try:
            b = quelle.beitrag_aus_wp(post)
        except (KeyError, TypeError, ValueError):
            stats["unlesbar"] += 1
            continue
        if quelle.altbestand(b, marke):
            stats["altbestand"] += 1
            continue
        if store.db.execute("SELECT 1 FROM social_beitraege WHERE wp_post_id = ? LIMIT 1", (b.wp_post_id,)).fetchone():
            stats["bekannt"] += 1  # R7: Korrekturen lösen nichts erneut aus
            continue
        _anlegen(store, settings, quelle.anreichern(store, settings, b), rw, jetzt, whatsapp_url)
        stats["neu"] += 1
    return stats


def _anlegen(store, settings, b: quelle.Beitrag, rw: regelwerk.Regelwerk, jetzt: datetime, whatsapp_url: str) -> None:
    pruefung = regelwerk.pruefen(b, rw, jetzt)
    auto = regelwerk.automatisch(pruefung)
    gruende = "; ".join(regelwerk.gruende(pruefung))
    rubrik = regelwerk.rubrik(b, rw)
    datei, art, asset_id, ki = _bild(store, settings, b, rw, rubrik)
    text, tags = text_bauen(b, rw, rubrik, ki)
    wa_text, _ = text_bauen(b, rw, rubrik, ki, hashtags=False, whatsapp_url=whatsapp_url)
    karenz = _iso(jetzt + timedelta(minutes=rw.karenz_min))
    for kanal in KANAELE:
        if kanal == "whatsapp":
            status, t, h = "entwurf", wa_text, []
        else:
            status, t, h = ("karenz" if auto else "von_hand"), text, tags
        cur = store._write(
            "INSERT OR IGNORE INTO social_beitraege (wp_post_id, quelle_typ, kanal, status, regel_fassung, "
            "regelpruefung, titel, rubrik, quelle_datum, event_datum, text, hashtags, link, bild_datei, bild_art, "
            "asset_id, ki_hinweis, karenz_bis, fehler, erkannt_at, aktualisiert) VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (b.wp_post_id, b.quelle_typ, kanal, status, rw.fassung, json.dumps(pruefung, ensure_ascii=False),
             b.titel, rubrik, _iso(b.datum) if b.datum else None, b.event_datum or None, t,
             json.dumps(h, ensure_ascii=False), b.link, datei, art, asset_id, 1 if ki else 0,
             karenz if status == "karenz" else None, gruende if status == "von_hand" else None, now_iso(), now_iso()))
        if cur.rowcount != 1:
            continue
        zeile = _zeile(store, cur.lastrowid)
        notiz = {"karenz": f"Karenz bis {karenz}", "von_hand": f"von Hand: {gruende}",
                 "entwurf": "WhatsApp-Entwurf bereit" + (f" (Hinweis: {gruende})" if gruende else "")}[status]
        _protokoll(store, zeile, "social_erkannt", notiz)


# ---- Senden -------------------------------------------------------------------------------------

def naechster_slot(store, kanal: str, rw: regelwerk.Regelwerk, jetzt: datetime) -> tuple[datetime, str]:
    """Frühester zulässiger Zeitpunkt für `kanal` ab `jetzt` und der Grund, falls später (R5 Menge/Abstand, R6)."""
    gesendet = sorted(_zeit(r[0]) for r in store.db.execute(
        "SELECT sende_at FROM social_beitraege WHERE kanal = ? AND sende_at IS NOT NULL", (kanal,)))
    t, grund = jetzt, ""
    for _ in range(20):
        if regelwerk.in_ruhezeit(t, rw):
            t, grund = regelwerk.ende_ruhezeit(t, rw), f"R6 Ruhezeit {rw.ruhe_von}–{rw.ruhe_bis} Uhr"
            continue
        vorher = [g for g in gesendet if g <= t]
        if vorher and t < vorher[-1] + timedelta(minutes=rw.abstand_min):
            t, grund = vorher[-1] + timedelta(minutes=rw.abstand_min), f"R5 {rw.abstand_min} Minuten Abstand"
            continue
        tag = t.astimezone(regelwerk.TZ).date()
        if sum(1 for g in gesendet if g.astimezone(regelwerk.TZ).date() == tag) >= rw.max_je_tag:
            morgen = t.astimezone(regelwerk.TZ) + timedelta(days=1)
            t = morgen.replace(hour=rw.ruhe_bis, minute=0, second=0, microsecond=0)
            grund = f"R5 höchstens {rw.max_je_tag} je Tag"
            continue
        break
    return t, (grund if t > jetzt else "")


def _warten(store, zeile: dict, grund: str, *, protokoll: str = "") -> None:
    """Wartegrund setzen; ins Protokoll nur, wenn er sich ändert (sonst alle drei Minuten dieselbe Zeile)."""
    if zeile.get("wartet_grund") == grund:
        return
    _setzen(store, zeile["id"], wartet_grund=grund)
    if protokoll:
        _protokoll(store, zeile, protokoll, grund)


def _nutzlast(zeile: dict, bild_url: str) -> dict:
    alt = (zeile["titel"] or "")[:1000]
    if zeile["kanal"] == "instagram":
        schritte = [
            {"methode": "POST", "pfad": "/{ig-user-id}/media",
             "daten": {"image_url": bild_url, "caption": zeile["text"], "alt_text": alt}},
            {"methode": "GET", "pfad": "/{container-id}?fields=status_code"},
            {"methode": "GET", "pfad": "/{ig-user-id}/content_publishing_limit"},
            {"methode": "POST", "pfad": "/{ig-user-id}/media_publish", "daten": {"creation_id": "{container-id}"}},
            {"methode": "GET", "pfad": "/{media-id}?fields=permalink"},
        ]
    else:
        schritte = [
            {"methode": "POST", "pfad": "/{page-id}/photos",
             "daten": {"url": bild_url, "caption": zeile["text"], "alt_text_custom": alt, "published": "true"}},
            {"methode": "GET", "pfad": "/{post-id}?fields=permalink_url"},
        ]
    return {"kanal": zeile["kanal"], "bild_datei": zeile["bild_datei"], "schritte": schritte}


def wp_bild_url(settings) -> Callable[[dict], str]:
    """Live: das Social-JPEG als Medium in WordPress hochladen und dessen öffentliche Adresse nutzen (Meta lädt das
    Bild von dort). Im Trockenmodus wird nichts hochgeladen."""
    from .. import images
    from ..wordpress import WordPress

    def hochladen(zeile: dict) -> str:
        wp = WordPress(settings.wp_url, settings.wp_user, settings.wp_app_password)
        bild_datei = settings.data_dir / "social" / zeile["bild_datei"]
        mid = wp.upload_media(images.load_image(bild_datei, credit="Grafik: Tamil.de"), alt=zeile["titel"] or "")
        return wp.media_quelle(mid)

    return hochladen


VERWAIST = timedelta(minutes=10)  # länger als ein Lauf des Dienstes (Timeout 300 s)


def _verwaiste(store, jetzt: datetime) -> Counter:
    """Zeilen, die ein abgebrochener Lauf (Kill, Deploy, Absturz) in „wird gesendet“ zurückgelassen hat: im Trockenlauf
    ging nichts hinaus (zurück auf geplant); live ist der Ausgang unklar (Abgleich, nie blind wiederholen)."""
    stats: Counter = Counter()
    grenze = _iso(jetzt - VERWAIST)
    for r in store.db.execute("SELECT * FROM social_beitraege WHERE status = 'wird_gesendet' AND "
                              "(sende_at IS NULL OR sende_at <= ?)", (grenze,)).fetchall():
        zeile = dict(r)
        if zeile["modus"] == "trocken":
            cur = store._write("UPDATE social_beitraege SET status = 'geplant', geplant_fuer = ?, sende_at = NULL, "
                               "aktualisiert = ? WHERE id = ? AND status = 'wird_gesendet'",
                               (_iso(jetzt), now_iso(), zeile["id"]))
            notiz = "Lauf abgebrochen (Trockenlauf): erneut eingeplant"
        else:
            cur = store._write("UPDATE social_beitraege SET status = 'unklar', fehler = ?, aktualisiert = ? WHERE id = ? "
                               "AND status = 'wird_gesendet'",
                               ("Ausgang unklar: der Lauf brach während des Sendens ab", now_iso(), zeile["id"]))
            notiz = "Lauf abgebrochen: Ausgang unklar, Abgleich folgt"
        if cur.rowcount == 1:
            _protokoll(store, zeile, "social_verwaist", notiz)
            stats["verwaist"] += 1
    return stats


def senden(store, settings, transport, jetzt: datetime, bild_url: Callable[[dict], str] | None = None) -> Counter:
    """Fällige Zeilen nach der Karenz hinausschicken: zuerst Instagram, danach Facebook. Trocken ohne Aufruf; live
    nur, wenn die aktuelle Fassung des Regelwerks von KBS freigegeben ist."""
    stats: Counter = Counter()
    rw = regelwerk.aktuell(store)
    if transport.live and not regelwerk.freigegeben(rw):
        stats["ohne_freigabe"] += 1
        transport = TrockenTransport()
    stats.update(_verwaiste(store, jetzt))
    if transport.live:
        stats.update(_abgleichen(store, transport, jetzt))
    if transport.live and bild_url is None:
        bild_url = wp_bild_url(settings)
    for kanal in META_KANAELE:
        zeilen = [dict(r) for r in store.db.execute(
            "SELECT * FROM social_beitraege WHERE kanal = ? AND status IN ('karenz', 'geplant', 'pausiert') "
            "ORDER BY COALESCE(geplant_fuer, karenz_bis), id", (kanal,))]
        for zeile in zeilen:
            stats.update(_eine(store, settings, transport, rw, zeile, jetzt, bild_url))
    return stats


def _r3_neu(store, rw, zeile: dict, jetzt: datetime) -> bool:
    """R3 gilt beim Senden noch einmal (Ruhezeit und Menge können Stunden verschieben). Was ein Mensch freigegeben
    hat, bleibt freigegeben. True, wenn die Zeile deshalb an einen Menschen geht."""
    if zeile["entschieden_von"]:
        return False
    r3 = regelwerk.pruefe_alter(_zeit(zeile["quelle_datum"]), zeile["quelle_typ"], zeile["event_datum"] or "", rw,
                                jetzt)
    if r3["ergebnis"] == "erfuellt":
        return False
    pruefung = json.loads(zeile["regelpruefung"] or "{}")
    pruefung["R3"] = r3
    grund = f"R3 {regelwerk.REGELN['R3']}: {r3['grund']} (beim Senden geprüft)"
    cur = store._write("UPDATE social_beitraege SET status = 'von_hand', fehler = ?, regelpruefung = ?, wartet_grund = "
                       "NULL, aktualisiert = ? WHERE id = ? AND status = ?",
                       (grund, json.dumps(pruefung, ensure_ascii=False), now_iso(), zeile["id"], zeile["status"]))
    if cur.rowcount == 1:
        _protokoll(store, zeile, "social_von_hand", grund, regel_fassung=rw.fassung)
    return True


def _eine(store, settings, transport, rw, zeile: dict, jetzt: datetime, bild_url) -> Counter:
    stats: Counter = Counter()
    kanal = zeile["kanal"]
    faellig = _zeit(zeile["geplant_fuer"] if zeile["status"] != "karenz" else zeile["karenz_bis"])
    if faellig is not None and faellig > jetzt:
        return stats
    if kanal == "facebook":
        ig = store.db.execute("SELECT status FROM social_beitraege WHERE wp_post_id = ? AND kanal = 'instagram'",
                              (zeile["wp_post_id"],)).fetchone()
        if ig is not None and ig["status"] in OFFEN:
            _warten(store, zeile, "wartet auf Instagram (zuerst Instagram, dann Facebook)")
            return stats
    if _r3_neu(store, rw, zeile, jetzt):
        stats["von_hand"] += 1
        return stats
    slot, grund = naechster_slot(store, kanal, rw, jetzt)
    if slot > jetzt:
        if zeile["status"] != "geplant" or zeile["geplant_fuer"] != _iso(slot) or zeile["wartet_grund"] != grund:
            _setzen(store, zeile["id"], status="geplant", geplant_fuer=_iso(slot), wartet_grund=grund)
        stats["geplant"] += 1
        return stats
    # Kanal (und „alles“); live lädt der erste Kanal das Bild zur Website hoch – das hält der Schalter „website“ an
    for pruef in (kanal, "website") if transport.live and not zeile["bild_url"] else (kanal,):
        sperre = schalter.sperre(store, pruef)
        if sperre is not None:
            _warten(store, zeile, str(schalter.Gestoppt(pruef, sperre)), protokoll="social_angehalten")
            stats["angehalten"] += 1
            return stats
    modus = "live" if transport.live else "trocken"
    # bedingt auf den gelesenen Stand: ändert die Redaktion dazwischen Text oder Status, geht diese Fassung nicht
    cur = store._write("UPDATE social_beitraege SET status = 'wird_gesendet', sende_at = ?, versuche = versuche + 1, "
                       "modus = ?, wartet_grund = NULL, aktualisiert = ? WHERE id = ? AND status = ? AND "
                       "aktualisiert = ? AND geplant_fuer IS ?",
                       (_iso(jetzt), modus, now_iso(), zeile["id"], zeile["status"], zeile["aktualisiert"],
                        zeile["geplant_fuer"]))
    if cur.rowcount != 1:  # inzwischen gestoppt, geändert oder von einem anderen Lauf übernommen
        return stats
    zeile = _zeile(store, zeile["id"])
    _protokoll(store, zeile, "social_senden", f"{modus}: {kanal}; geprüft nach Fassung {zeile['regel_fassung']}",
               regel_fassung=rw.fassung)
    if not transport.live:
        nutzlast = _nutzlast(zeile, f"(Trockenmodus, nicht hochgeladen) {zeile['bild_datei']}")
        _setzen(store, zeile["id"], status="trocken", nutzlast=json.dumps(nutzlast, ensure_ascii=False),
                veroeffentlicht_at=_iso(jetzt), geplant_fuer=None)
        _protokoll(store, zeile, "social_trocken", "vorbereitet und gespeichert, nichts an Meta geschickt",
                   regel_fassung=rw.fassung)
        stats.update({"gesendet": 1, "trocken": 1})
        return stats
    phase = {"entscheidend": False}  # ab dem veröffentlichenden Aufruf ist jeder Abbruch „unklar“
    try:
        if not zeile["bild_url"]:
            _vor_aufruf(store, "website")
            url = bild_url(zeile)
            store._write("UPDATE social_beitraege SET bild_url = ? WHERE wp_post_id = ? AND bild_url IS NULL",
                         (url, zeile["wp_post_id"]))
            zeile["bild_url"] = url
        _setzen(store, zeile["id"], nutzlast=json.dumps(_nutzlast(zeile, zeile["bild_url"]), ensure_ascii=False))
        ergebnis = (_instagram if kanal == "instagram" else _facebook)(store, transport, zeile, jetzt, phase)
    except schalter.Gestoppt as exc:
        _setzen(store, zeile["id"], status="geplant", geplant_fuer=_iso(jetzt), sende_at=None)
        _warten(store, {**zeile, "wartet_grund": None}, str(exc), protokoll="social_angehalten")
        stats["angehalten"] += 1
        return stats
    except UnklarFehler as exc:
        return stats + _unklar(store, zeile, str(exc))
    except ZugangFehler as exc:
        _setzen(store, zeile["id"], status="pausiert", fehler=f"Meta-Fehler {exc.code}: {exc.text}"[:300],
                sende_at=None, geplant_fuer=_iso(jetzt))
        _protokoll(store, zeile, "social_fehler", f"Kanal pausiert: Meta-Fehler {exc.code}")
        if not schalter.gestoppt(store, kanal):
            schalter.setzen(store, kanal, True, wer=SYSTEM, grund=f"Meta-Fehler {exc.code}: {exc.text}")
        stats["pausiert"] += 1
        return stats
    except WarteFehler as exc:
        if phase["entscheidend"]:
            return stats + _unklar(store, zeile, f"Meta-Fehler {exc.code} beim Veröffentlichen: {exc.text}")
        spaeter = jetzt + timedelta(minutes=15 if exc.code == 0 else 60)
        _setzen(store, zeile["id"], status="geplant", geplant_fuer=_iso(spaeter), sende_at=None,
                wartet_grund=f"Meta: {exc.text}"[:300], fehler=f"Meta-Fehler {exc.code}: {exc.text}"[:300])
        _protokoll(store, zeile, "social_warten", f"Meta-Fehler {exc.code}, erneut ab {_iso(spaeter)}")
        stats["warten"] += 1
        return stats
    except MetaFehler as exc:
        _setzen(store, zeile["id"], status="von_hand", sende_at=None, fehler=f"Meta-Fehler {exc.code}: {exc.text}"[:300])
        _protokoll(store, zeile, "social_fehler", f"an einen Menschen: Meta-Fehler {exc.code}")
        stats["von_hand"] += 1
        return stats
    except Exception as exc:  # noqa: BLE001 – nichts darf eine Zeile in „wird gesendet“ zurücklassen
        text = f"{type(exc).__name__}: {exc}"[:250]
        if phase["entscheidend"]:
            return stats + _unklar(store, zeile, text)
        if zeile["versuche"] >= 3:
            _setzen(store, zeile["id"], status="von_hand", sende_at=None, fehler=f"Fehler vor dem Senden: {text}")
            _protokoll(store, zeile, "social_fehler", f"nach {zeile['versuche']} Versuchen an einen Menschen: {text}")
            stats["von_hand"] += 1
        else:
            spaeter = jetzt + timedelta(minutes=15)
            _setzen(store, zeile["id"], status="geplant", geplant_fuer=_iso(spaeter), sende_at=None,
                    fehler=f"Fehler vor dem Senden: {text}", wartet_grund=f"Fehler, erneut ab {_iso(spaeter)}")
            _protokoll(store, zeile, "social_warten", f"Fehler vor dem Senden: {text}")
            stats["warten"] += 1
        return stats
    stats.update(ergebnis)
    return stats


def _unklar(store, zeile: dict, text: str) -> Counter:
    _setzen(store, zeile["id"], status="unklar", fehler=f"Ausgang unklar: {text}"[:300])
    _protokoll(store, zeile, "social_unklar", text)
    return Counter({"unklar": 1})


def _vor_aufruf(store, kanal: str) -> None:
    schalter.pruefen(store, kanal)  # wirft Gestoppt


def _veroeffentlicht(store, zeile: dict, jetzt: datetime, meta_id: str, link: str) -> Counter:
    _setzen(store, zeile["id"], status="veroeffentlicht", meta_id=meta_id, meta_link=link,
            veroeffentlicht_at=_iso(jetzt), geplant_fuer=None, fehler=None)
    _protokoll(store, zeile, "social_veroeffentlicht", f"Kennung {meta_id}")
    return Counter({"gesendet": 1, "veroeffentlicht": 1})


def _instagram(store, t, zeile: dict, jetzt: datetime, phase: dict) -> Counter:
    nutzlast = json.loads(zeile["nutzlast"] or "{}")
    cid = zeile["container_id"]
    if not cid:
        _vor_aufruf(store, "instagram")
        cid = t.ig_container(zeile["bild_url"], zeile["text"], (zeile["titel"] or "")[:1000])
        _setzen(store, zeile["id"], container_id=cid, container_at=_iso(jetzt))
        zeile.update(container_id=cid, container_at=_iso(jetzt))
    _vor_aufruf(store, "instagram")
    status = t.ig_status(cid)
    alt = jetzt - (_zeit(zeile["container_at"]) or jetzt)
    if status in ("ERROR", "EXPIRED") or (status != "FINISHED" and alt > CONTAINER_WARTEN):
        if nutzlast.get("container_neu"):
            raise MetaFehler(0, f"Container {status or 'ohne Status'} auch nach neuem Versuch")
        nutzlast["container_neu"] = 1
        _setzen(store, zeile["id"], status="geplant", geplant_fuer=_iso(jetzt), sende_at=None, container_id=None,
                nutzlast=json.dumps(nutzlast, ensure_ascii=False), wartet_grund=f"Container {status}: einmal neu")
        return Counter({"warten": 1})
    if status != "FINISHED":
        _setzen(store, zeile["id"], status="geplant", geplant_fuer=_iso(jetzt + timedelta(minutes=1)), sende_at=None,
                wartet_grund=f"Instagram bereitet das Bild vor ({status or 'ohne Status'})")
        return Counter({"warten": 1})
    _vor_aufruf(store, "instagram")
    genutzt, grenze = t.ig_limit()
    if genutzt >= grenze:
        raise WarteFehler(9, f"Tagesgrenze von Meta erreicht ({genutzt}/{grenze})")
    _vor_aufruf(store, "instagram")
    phase["entscheidend"] = True
    mid = t.ig_veroeffentlichen(cid)
    try:
        link = t.ig_permalink(mid)
    except Exception:  # noqa: BLE001  # veröffentlicht ist veröffentlicht; der Link fehlt nur in der Historie
        link = ""
    return _veroeffentlicht(store, zeile, jetzt, mid, link)


def _facebook(store, t, zeile: dict, jetzt: datetime, phase: dict) -> Counter:
    _vor_aufruf(store, "facebook")
    phase["entscheidend"] = True
    antwort = t.fb_foto(zeile["bild_url"], zeile["text"], (zeile["titel"] or "")[:1000])
    post_id = antwort.get("post_id") or antwort.get("id")
    try:
        link = t.fb_permalink(post_id)
    except Exception:  # noqa: BLE001 – veröffentlicht ist veröffentlicht; nur der Link fehlt
        link = ""
    return _veroeffentlicht(store, zeile, jetzt, post_id, link)


def _link_im_text(link: str, text) -> bool:
    """Der Link als ganzes Wort (zwischen Leerraum bzw. Anfang/Ende), nicht als Anfang eines längeren Links."""
    if not link:
        return False
    return re.search(rf"(?:^|\s){re.escape(link)}(?=\s|$)", str(text or "")) is not None


def _abgleichen(store, t, jetzt: datetime) -> Counter:
    """Unklare Zeilen mit den letzten Beiträgen des Kontos vergleichen (Treffer über den Link auf tamil.de im Text)."""
    stats: Counter = Counter()
    for kanal in META_KANAELE:
        zeilen = [dict(r) for r in store.db.execute(
            "SELECT * FROM social_beitraege WHERE kanal = ? AND status = 'unklar' ORDER BY id", (kanal,))]
        if not zeilen or schalter.gestoppt(store, kanal):
            continue
        try:
            letzte = t.ig_letzte() if kanal == "instagram" else t.fb_letzte()
        except (MetaFehler, UnklarFehler) as exc:
            store.event("social_abgleich_fehler", kanal=kanal, fehler=str(exc)[:200])
            continue
        for zeile in zeilen:
            treffer = next((e for e in letzte if _link_im_text(zeile["link"], e.get("caption") or e.get("message"))),
                           None)
            if treffer:
                link = treffer.get("permalink") or treffer.get("permalink_url") or ""
                _setzen(store, zeile["id"], status="veroeffentlicht", meta_id=str(treffer.get("id", "")),
                        meta_link=link, veroeffentlicht_at=_iso(jetzt), fehler=None)
                _protokoll(store, zeile, "social_abgleich", f"gefunden: Kennung {treffer.get('id', '')}")
                stats["abgleich_gefunden"] += 1
            else:
                _setzen(store, zeile["id"], status="von_hand",
                        fehler="Ausgang unklar: Beitrag nicht unter den letzten des Kontos – bitte prüfen")
                _protokoll(store, zeile, "social_abgleich", "nicht gefunden: an einen Menschen")
                stats["abgleich_offen"] += 1
    return stats


def lauf(store, settings, konf: Konfig, jetzt: datetime | None = None, *, abruf: quelle.Abruf | None = None,
         transport=None, bild_url=None) -> Counter:
    """Ein Lauf des Dienstes: erkennen, dann senden. Scheitert das Erkennen (Website nicht erreichbar), gehen fällige
    Zeilen trotzdem hinaus; der Fehler steht im Log."""
    jetzt = jetzt or datetime.now(timezone.utc)
    stats = Counter()
    if settings.wp_url or abruf is not None:
        try:
            stats.update(erkennen(store, settings, abruf or quelle.wp_abruf(settings), jetzt,
                                  whatsapp_url=konf.whatsapp_url))
        except Exception as exc:  # noqa: BLE001 – Erkennen ist nur Lesen; das Senden hängt nicht davon ab
            store.event("social_erkennen_fehler", fehler=f"{type(exc).__name__}: {exc}"[:300])
            stats["erkennen_fehler"] += 1
    else:
        stats["ohne_website"] += 1
    stats.update(senden(store, settings, transport or transport_fuer(konf, regelwerk.aktuell(store)), jetzt,
                        bild_url=bild_url))
    return stats


__all__ = ["erkennen", "senden", "lauf", "transport_fuer", "startmarke", "naechster_slot", "text_bauen", "ERLEDIGT"]
