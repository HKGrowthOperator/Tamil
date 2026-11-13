"""Abnahme-Nachläufe für den Eingang (Festlegung F1, Szenarien ab 80): Einsendungen über den Fake-Transport der
Website, Vorbereitung mit FakeClaude (oder ohne Modell), Entscheidung wie im Cockpit, Weg bis in den Kalender.
Alle Personendaten sind erfunden (example.test)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from .. import eingang, lizenz, publisher, schalter
from ..wordpress import TamilRadarClient
from ..workflow import repo
from .wp_eingang import FakeWordPressEingang

PERSON = ("Erika Beispiel", "erika@example.test")


def termin(now: datetime, tage: int = 30, **kw) -> dict:
    beginn = (now + timedelta(days=tage)).astimezone(eingang.TZ).replace(hour=18, minute=30, second=0, microsecond=0)
    return {"titel": "Pongal-Fest Testverein", "beginn": beginn.isoformat(), "ende": beginn.replace(hour=22).isoformat(),
            "ort": "Gemeindesaal, Beispielstraße 1", "stadt": "Essen", "land": "DE", "veranstalter": "Testverein e. V.",
            "beschreibung": "Tanz, Musik und Essen. Alle Familien sind willkommen.", "eintritt": "10 Euro, Kinder frei",
            "ticket_link": "https://tickets.example.test/pongal", **kw}


def _client(wp: FakeWordPressEingang) -> TamilRadarClient:
    return TamilRadarClient("https://www.tamil.test", "ki-agent", "app-pw", session=wp)


def _ohne_personendaten(store) -> int:
    """1, wenn weder Protokoll noch Ereignislog einen Namen oder eine Adresse des Einsenders enthalten."""
    zeilen = [str(dict(r)) for r in store.db.execute("SELECT * FROM editorial_actions")]
    zeilen += [str(r) for r in store.iter_log()]
    zeilen += [str(d) for d in store.list_drafts(limit=500)]
    return int(not any(p in z for z in zeilen for p in PERSON))


def bis_kalender(ctx, sz, now: datetime) -> dict:
    """Termin einreichen → Eingang mit Hinweisen → bearbeiten → übernehmen → freigeben → im Kalender (Plugin-Meta)."""
    store, wp = ctx.store, FakeWordPressEingang()
    c = _client(wp)
    v = wp.einreichen("event", termin(now), bild=_foto(), bild_typ="image/jpeg")
    out = Counter({f"eingang_{k}": n for k, n in eingang.lauf(store, c, ctx.claude, jetzt=now).items()})
    e = eingang.holen(store, v)
    out["hinweise"] = len(e["hinweise"])
    did = eingang.uebernehmen(store, ctx.settings, v, von="priya", client=c,
                              felder={"titel": "Pongal-Fest des Testvereins in Essen"})
    d = store.get_draft(did)
    out["vermerk"] = int(eingang.VERMERK in d["hinweise"])
    out["wp_uebernommen"] = int(wp.zeile(v)["status"] == "uebernommen")
    out["bild_ohne_sperre"] = int(bool(d["bild_datei"]) and lizenz.sperre(store, d) == "")
    store.set_status(did, "freigeben", von="priya")
    publisher.publish_approved(ctx.settings, store, wp=c)
    out["veroeffentlicht_wp"] = len(wp.beitraege)
    meta = wp.beitraege[0]["meta"] if wp.beitraege else {}
    out["kalender_vollstaendig"] = int(all(meta.get(k) for k in ("event_datum", "event_ort", "event_preis",
                                                                 "event_veranstalter", "event_ende")))
    out["bild_gesendet"] = int(bool(wp.beitraege and wp.beitraege[0].get("bild", {}).get("daten")))
    out["bild_lizenz_wp"] = int(meta.get("bild_lizenz") == "nutzungsrecht")
    out["ohne_personendaten"] = _ohne_personendaten(store)
    return dict(out)


def _foto() -> bytes:
    """JPEG mit EXIF (Hersteller): wird beim Übernehmen ohne Metadaten neu gespeichert."""
    import io

    from PIL import Image

    buf = io.BytesIO()
    ex = Image.Exif()
    ex[0x010F] = "Kamera"
    Image.new("RGB", (1600, 900), (180, 40, 42)).save(buf, "JPEG", exif=ex)
    return buf.getvalue()


def dublette(ctx, sz, now: datetime) -> dict:
    store, wp = ctx.store, FakeWordPressEingang()
    wp.einreichen("event", termin(now))
    wp.einreichen("event", termin(now, titel="Pongal Fest – Testverein"), email="max@example.test")
    eingang.lauf(store, _client(wp), ctx.claude, jetzt=now)
    erste, zweite = sorted(eingang.liste(store), key=lambda e: e["wp_id"])
    return {"erste_ohne_dublette": int(not erste["dublette_von"]),
            "zweite_dublette": int(any(h.startswith("mögliche Dublette") for h in zweite["hinweise"]))}


def im_stopp(ctx, sz, now: datetime) -> dict:
    """Schalter „Eingang“ an: kein Aufruf an die Website, Einsendung bleibt dort liegen; danach geht es weiter."""
    store, wp = ctx.store, FakeWordPressEingang()
    wp.einreichen("event", termin(now))
    schalter.setzen(store, "eingang", True, wer="abnahme", grund="Rechtstexte fehlen")
    vorher = eingang.lauf(store, _client(wp), ctx.claude, jetzt=now)
    out = {"aufrufe_im_stopp": len(wp.aufrufe), "neu_im_stopp": vorher["neu"],
           "liegt_auf_website": int(wp.zeilen[0]["status"] == "eingegangen")}
    schalter.setzen(store, "eingang", False, wer="abnahme")
    danach = eingang.lauf(store, _client(wp), ctx.claude, jetzt=now)
    return {**out, "neu_danach": danach["neu"], "vorbereitet_danach": danach["vorbereitet"]}


def ohne_modell(ctx, sz, now: datetime) -> dict:
    store, wp = ctx.store, FakeWordPressEingang()
    wp.einreichen("event", termin(now, tage=-10, land="LK"))
    out = eingang.lauf(store, _client(wp), ctx.claude, jetzt=now)
    e = eingang.liste(store)[0]
    return {"vorbereitet": out["vorbereitet"], "modell": out["modell"],
            "entwurf_regeln": int((e["entwurf"] or {}).get("quelle") == "regeln"),
            "hinweis_vergangen": int("Datum in der Vergangenheit" in e["hinweise"]),
            "hinweis_ausserhalb": int(any(h.startswith("Ort außerhalb DACH") for h in e["hinweise"]))}


def erfindet(ctx, sz, now: datetime) -> dict:
    """Das Modell ergänzt eine Zahl und einen Link: der Modell-Entwurf wird verworfen, es gilt der aus den Feldern."""
    store, wp = ctx.store, FakeWordPressEingang()
    wp.einreichen("event", termin(now))
    out = eingang.lauf(store, _client(wp), ctx.claude, jetzt=now)
    e = eingang.liste(store)[0]
    return {"modell": out["modell"], "entwurf_regeln": int(e["entwurf"]["quelle"] == "regeln"),
            "verworfen": int(any("Modell-Entwurf verworfen" in h for h in e["hinweise"])),
            "ohne_erfundenes": int("500" not in str(e["entwurf"]) and "erfunden" not in str(e["entwurf"]))}


def kooperation(ctx, sz, now: datetime) -> dict:
    """Kooperation: nur Status und Notiz, kein Entwurf; leser darf nicht entscheiden; Status geht an die Website."""
    from ..web.rechte import darf

    store, wp = ctx.store, FakeWordPressEingang()
    c = _client(wp)
    v = wp.einreichen("kooperation", {"organisation": "Kulturhaus Beispiel", "anliegen": "Gemeinsame Lesereihe"})
    eingang.lauf(store, c, ctx.claude, jetzt=now)
    out = Counter()
    try:
        eingang.uebernehmen(store, ctx.settings, v, von="priya", client=c, felder={})
    except ValueError:
        out["uebernehmen_abgewiesen"] = 1
    eingang.notiz_setzen(store, v, "Rückruf am Montag", von="priya")
    eingang.abschliessen(store, v, "erledigt", von="priya", client=c)
    out["wp_erledigt"] = int(wp.zeile(v)["status"] == "erledigt")
    out["leser_darf"] = int(darf("eingang_entscheiden", "leser"))
    out["redaktion_darf"] = int(darf("eingang_entscheiden", "redaktion"))
    out["ohne_personendaten"] = _ohne_personendaten(store)
    return dict(out)


def unklar(ctx, sz, now: datetime) -> dict:
    """Abbruch nach dem Senden: der Radar fragt nach und gleicht ab, statt blind zu wiederholen; ein anderer Abschluss
    auf der Website wird vermerkt, nicht überschrieben."""
    store, wp = ctx.store, FakeWordPressEingang()
    c = _client(wp)
    v1 = wp.einreichen("kontakt", {"nachricht": "Bitte um Rückruf"})
    v2 = wp.einreichen("kontakt", {"nachricht": "Noch eine Frage"})
    eingang.lauf(store, c, ctx.claude, jetzt=now)
    wp.abbruch_nach_senden.add(v1)
    vorher = len(wp.aufrufe)
    eingang.abschliessen(store, v1, "erledigt", von="priya", client=c)
    wp.zeile(v2)["status"] = "spam"
    eingang.abschliessen(store, v2, "erledigt", von="priya", client=c)
    posts = sum(1 for m, r in wp.aufrufe[vorher:] if m == "POST" and r == f"einsendung/{v1}/status")
    return {"abgeglichen": int(eingang.holen(store, v1)["wp_status"] == "erledigt"), "status_posts_v1": posts,
            "konflikt_vermerkt": int(eingang.holen(store, v2)["wp_status"] == "spam"),
            "offen_danach": eingang.melden(store, c)["gemeldet"]}


def loeschfrist(ctx, sz, now: datetime) -> dict:
    store, wp = ctx.store, FakeWordPressEingang()
    c = _client(wp)
    alt, spam, neu = (wp.einreichen("kontakt", {"nachricht": f"Nachricht {i}"}) for i in range(3))
    eingang.lauf(store, c, ctx.claude, jetzt=now)
    for v, st, tage in ((alt, "erledigt", 91), (spam, "spam", 8), (neu, "erledigt", 30)):
        eingang.abschliessen(store, v, st, von="priya", client=c)
        store._write("UPDATE einsendungen SET abgeschlossen_at = ? WHERE vorgangsnummer = ?",
                     ((now - timedelta(days=tage)).astimezone(timezone.utc).isoformat(timespec="seconds"), v))
    out = eingang.loeschen(store, jetzt=now)
    return {"geloescht": out["geloescht"], "spam_geloescht": out["spam"],
            "bleibt": len(eingang.liste(store, ansicht="alle")),
            "protokoll": len(repo.aktionen_liste(store, aktion="eingang_geloescht"))}


NACHHER = {"eingang_kalender": bis_kalender, "eingang_dublette": dublette, "eingang_stopp": im_stopp,
           "eingang_ohne_modell": ohne_modell, "eingang_erfindet": erfindet, "eingang_kooperation": kooperation,
           "eingang_unklar": unklar, "eingang_loeschfrist": loeschfrist}


def erfindet_antwort(user: str, system: str, req: dict) -> dict:
    from ..workflow import fake

    out = fake.eingang(user, system, req)
    out["teaser"] = "Rund 500 Gäste werden erwartet."
    out["absaetze"] = out["absaetze"] + ["Mehr unter https://erfunden.example/pongal"]
    return out
