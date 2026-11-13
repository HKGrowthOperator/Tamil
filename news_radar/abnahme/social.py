"""Abnahme F4 (Festlegung Social, Tests T1–T3) ohne Konten: Fake-Website (lesende REST-Antworten) und FakeMeta als
nachgestellte Schnittstelle bzw. der Trocken-Transport. Feste Uhr (Montag 9 Uhr Berlin), damit die Ruhezeit nie
zufällig greift. Jeder Fall liefert Zählungen, die das Szenario erwartet; kein Modellaufruf, kein Netz.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone

from .. import schalter
from ..social import ablauf, aktionen
from ..social.fake import FakeMeta
from ..social.transport import TrockenTransport
from ..workflow import repo

START = datetime(2026, 11, 16, 8, 0, tzinfo=timezone.utc)
NACH_KARENZ = START + timedelta(minutes=11)


def _post(pid: int, titel: str, *, rubrik: str = "community", stunden: float = 0.5, uid: str | None = None,
          event: str = "", tags: tuple[str, ...] = ()) -> dict:
    datum = (START - timedelta(hours=stunden)).replace(tzinfo=None).isoformat(timespec="seconds")
    return {"id": pid, "date_gmt": datum, "link": f"https://www.tamil.de/abnahme-{pid}/",
            "title": {"rendered": titel}, "excerpt": {"rendered": "<p>Vorspann aus der Abnahme.</p>"},
            "meta": {"radar_uid": uid if uid is not None else f"radar-abnahme-{pid}", "event_datum": event,
                     "event_ort": "Festhalle Bern" if event else ""},
            "_embedded": {"wp:term": [[{"taxonomy": "category", "slug": rubrik}],
                                      [{"taxonomy": "post_tag", "name": t} for t in tags]]}}


def _start(ctx, posts: list[dict]) -> Counter:
    """Erster Lauf setzt die Startmarke (eine Stunde vor START), der zweite erkennt die Beiträge."""
    ablauf.erkennen(ctx.store, ctx.settings, lambda p: [], START - timedelta(hours=1))
    return ablauf.erkennen(ctx.store, ctx.settings, lambda p: list(posts), START)


def _zeilen(ctx, **wo) -> list[dict]:
    sql = "SELECT * FROM social_beitraege" + (" WHERE " + " AND ".join(f"{k} = ?" for k in wo) if wo else "")
    return [dict(r) for r in ctx.store.db.execute(sql + " ORDER BY id", tuple(wo.values()))]


def _url(zeile: dict) -> str:
    return f"https://www.tamil.de/wp-content/uploads/{zeile['bild_datei']}"


def t1_artikel(ctx) -> dict:
    _start(ctx, [_post(701, "Tamilische Schule in Hamm feiert zehn Jahre")])
    meta = FakeMeta()
    vorher = ablauf.senden(ctx.store, ctx.settings, meta, START + timedelta(minutes=9), bild_url=_url)
    ablauf.senden(ctx.store, ctx.settings, meta, NACH_KARENZ, bild_url=_url)
    ig, fb = _zeilen(ctx, kanal="instagram")[0], _zeilen(ctx, kanal="facebook")[0]
    namen = [a[0] for a in meta.aufrufe]
    return {"vor_karenz_gesendet": vorher["gesendet"],
            "veroeffentlicht": sum(z["status"] == "veroeffentlicht" for z in (ig, fb)),
            "links": sum(bool(z["meta_link"]) for z in (ig, fb)), "kennungen": sum(bool(z["meta_id"]) for z in (ig, fb)),
            "instagram_zuerst": int(namen.index("ig_veroeffentlichen") < namen.index("fb_foto")),
            "regel_fassung": int(ig["regel_fassung"] == fb["regel_fassung"] == "1")}


def t2_termine(ctx) -> dict:
    zukunft = (START + timedelta(days=12)).date().isoformat() + " 18:00"
    vergangen = (START - timedelta(days=2)).date().isoformat()
    _start(ctx, [_post(711, "Maaveerar-Gedenken in Bern", rubrik="events", event=zukunft),
                 _post(712, "Deepavali-Feier in Zürich", rubrik="events", event=vergangen)])
    meta = FakeMeta()
    ablauf.senden(ctx.store, ctx.settings, meta, NACH_KARENZ, bild_url=_url)
    zukunft_z = [z for z in _zeilen(ctx, wp_post_id=711) if z["kanal"] != "whatsapp"]
    alt_z = [z for z in _zeilen(ctx, wp_post_id=712) if z["kanal"] != "whatsapp"]
    return {"termin_veroeffentlicht": sum(z["status"] == "veroeffentlicht" for z in zukunft_z),
            "vergangen_uebersprungen": sum(z["status"] == "von_hand" and "R3" in (z["fehler"] or "") for z in alt_z),
            "aufrufe_vergangen": sum(1 for _n, d in meta.aufrufe if "Deepavali" in str(d))}


def t3_heikel(ctx) -> dict:
    _start(ctx, [_post(721, "Urteil im Prozess gegen Schleuser", rubrik="news", tags=("Justiz",))])
    meta = FakeMeta()
    for minuten in (11, 30, 60):
        ablauf.senden(ctx.store, ctx.settings, meta, START + timedelta(minutes=minuten), bild_url=_url)
    zeilen = [z for z in _zeilen(ctx) if z["kanal"] != "whatsapp"]
    return {"von_hand": sum(z["status"] == "von_hand" for z in zeilen),
            "grund_r2": sum("R2" in (z["fehler"] or "") for z in zeilen), "meta_aufrufe": len(meta.aufrufe),
            "in_ansicht": len(aktionen.ansicht(ctx.store)["von_hand"])}


def stopp_instagram(ctx) -> dict:
    schalter.setzen(ctx.store, "instagram", True, wer="abnahme", grund="Abnahme: Kanal Instagram angehalten")
    _start(ctx, [_post(731, "Tamil-Sportfest in Wuppertal", rubrik="sport")])
    meta = FakeMeta()
    for minuten in (11, 14, 17):
        ablauf.senden(ctx.store, ctx.settings, meta, START + timedelta(minutes=minuten), bild_url=_url)
    zeilen = repo.aktionen_liste(ctx.store, aktion="social_angehalten", kanal="instagram")
    return {"meta_aufrufe": len(meta.aufrufe),
            "gesendet": sum(z["status"] in ("veroeffentlicht", "trocken") for z in _zeilen(ctx)),
            "protokoll_grund": sum("Abnahme: Kanal Instagram angehalten" in (z["notiz"] or "") for z in zeilen)}


def whatsapp(ctx) -> dict:
    _start(ctx, [_post(741, "Kochabend im Tempel Hamm", rubrik="kueche")])
    wa = _zeilen(ctx, kanal="whatsapp")[0]
    aktionen.gepostet(ctx.store, wa["id"], wer="abnahme-redaktion")
    z = repo.aktionen_liste(ctx.store, aktion="whatsapp_gepostet")
    return {"gepostet": int(_zeilen(ctx, kanal="whatsapp")[0]["status"] == "gepostet"),
            "protokoll_person": sum(r["wer"] == "abnahme-redaktion" and r["kanal"] == "whatsapp" for r in z),
            "protokoll_zeit": sum(bool(r["ts"]) for r in z)}


def altbestand(ctx) -> dict:
    alt = [_post(751, "Alter Beitrag aus 2024", stunden=3), _post(752, "Übernommener Beitrag", uid="alt-4711")]
    stats = _start(ctx, alt)
    meta = FakeMeta()
    ablauf.senden(ctx.store, ctx.settings, meta, NACH_KARENZ, bild_url=_url)
    return {"altbestand": stats["altbestand"], "zeilen": len(_zeilen(ctx)), "meta_aufrufe": len(meta.aufrufe)}


def abbruch(ctx) -> dict:
    _start(ctx, [_post(761, "Tamilische Bibliothek in Zürich eröffnet")])
    meta = FakeMeta(abbruch_bei=("ig_veroeffentlichen",), kommt_an=True)
    ablauf.senden(ctx.store, ctx.settings, meta, NACH_KARENZ, bild_url=_url)
    unklar = _zeilen(ctx, kanal="instagram")[0]["status"] == "unklar"
    ablauf.senden(ctx.store, ctx.settings, meta, NACH_KARENZ + timedelta(minutes=3), bild_url=_url)
    ig = _zeilen(ctx, kanal="instagram")[0]
    return {"erst_unklar": int(unklar), "abgleich_gefunden": int(ig["status"] == "veroeffentlicht"),
            "veroeffentlichen_aufrufe": [a[0] for a in meta.aufrufe].count("ig_veroeffentlichen"),
            "instagram_beitraege": len(meta.ig_beitraege)}


def trocken(ctx) -> dict:
    _start(ctx, [_post(771, "Bharatanatyam-Abend in Köln", rubrik="kultur")])
    ablauf.senden(ctx.store, ctx.settings, TrockenTransport(), NACH_KARENZ)  # wirft bei jedem Aufruf nach außen
    zeilen = [z for z in _zeilen(ctx) if z["kanal"] != "whatsapp"]
    return {"trocken": sum(z["status"] == "trocken" for z in zeilen),
            "nutzlast": sum(bool(json.loads(z["nutzlast"] or "{}").get("schritte")) for z in zeilen),
            "ohne_kennung": sum(not z["meta_id"] for z in zeilen)}


FAELLE = {"t1": t1_artikel, "t2": t2_termine, "t3": t3_heikel, "stopp_instagram": stopp_instagram,
          "whatsapp": whatsapp, "altbestand": altbestand, "abbruch": abbruch, "trocken": trocken}


def ausfuehren(ctx, sz, now) -> dict:
    return FAELLE[sz.einstellungen["_social"]](ctx)
