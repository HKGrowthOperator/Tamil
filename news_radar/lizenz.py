"""Lizenz-Datensatz je Bild (docs/spezifikation/bilder-und-lizenzen.md, Abschnitt 3).

- Positivliste der Lizenz-Kürzel mit höchstem Umfang (3.2); `umfang` ist eine kommagetrennte Menge aus
  `website,social,print` in fester Reihenfolge (die Social-Spur liest genau dieses Format).
- `datensatz` leitet aus einem Bild der Kette (Karte, KI, Pool, Stock, Upload) die Felder ab; was nicht feststeht,
  bleibt leer – ein leeres Pflichtfeld sperrt die Freigabe, statt etwas zu erfinden.
- `fehlend` sagt, was an einem Datensatz fehlt (3.1, „vollständig“); `sperre` ist das Gate für Freigabe,
  Sammelfreigabe und Veröffentlichen (3.3): ohne vollständigen Datensatz mit Umfang `website` und ohne Alt-Text (5.5)
  geht kein Bild hinaus.
- `nachfuehren` ergänzt Datensätze im Altbestand aus vorhandenen Commons- und Register-Angaben, wo diese vollständig
  sind, und lässt alles andere unverändert.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import quote, urlsplit

from .store import OPEN_STATES, now_iso

UMFAENGE = ("website", "social", "print")
ALLE = frozenset(UMFAENGE)
WEB_SOCIAL = frozenset({"website", "social"})
CC_VERSIONEN = ("1.0", "2.0", "2.5", "3.0", "4.0")
BEARBEITUNGEN = ("keine", "zugeschnitten", "eingepasst", "Logo-Leiste", "KI-Hinweis")
HERKUENFTE = ("archiv", "register", "quelle", "commons", "stock", "ki", "pool", "karte", "upload")
ALT_MIN, ALT_MAX = 5, 160
KI_CREDIT = "Symbolbild: KI-generiert · Tamil.de"  # wie bilder.KI_CREDIT (ohne Importkreis)
KARTE_CREDIT = "Grafik: Tamil.de"
STOCK_URL = {"pexels": "https://www.pexels.com/license/", "unsplash": "https://unsplash.com/license"}


@dataclass(frozen=True)
class Art:
    hoechst: frozenset          # höchster Umfang (3.2)
    nennung: bool = False       # Urheber Pflicht (Namensnennung)
    url: bool = False           # Lizenz-Adresse Pflicht
    beleg_datei: bool = False   # Beleg der Erlaubnis Pflicht (Datei oder Text der Redaktion)


FEST: dict[str, Art] = {
    "eigen": Art(ALLE),
    "nutzungsrecht": Art(ALLE, beleg_datei=True),
    "presse-redaktionell": Art(frozenset({"website"})),
    "cc0-1.0": Art(ALLE, url=True),
    "pdm-1.0": Art(ALLE, url=True),
    "pexels": Art(WEB_SOCIAL, nennung=True, url=True),
    "unsplash": Art(WEB_SOCIAL, nennung=True, url=True),
    "ki-symbolbild": Art(WEB_SOCIAL),
    "tamil-grafik": Art(ALLE),
}
_CC = re.compile(r"cc-by(-sa)?-(\d\.\d)")
# Was die Redaktion im Formular wählen darf: KI-Bild und Bildkarte entstehen nur im Radar selbst
FORMULAR_KUERZEL = ("eigen", "nutzungsrecht", "presse-redaktionell", "cc-by", "cc-by-sa", "cc0-1.0", "pdm-1.0",
                    "pexels", "unsplash")
NAMEN = {"eigen": "eigenes Werk", "nutzungsrecht": "Nutzungsrecht (schriftlich)",
         "presse-redaktionell": "Pressematerial, redaktionell", "cc0-1.0": "CC0 1.0", "pdm-1.0": "Public Domain Mark 1.0",
         "pexels": "Pexels-Lizenz", "unsplash": "Unsplash-Lizenz", "ki-symbolbild": "KI-Symbolbild",
         "tamil-grafik": "Bildkarte Tamil.de", "cc-by": "CC BY", "cc-by-sa": "CC BY-SA"}

# Bezeichnungen für „Lizenz fehlt: <Feld>“
FELDNAMEN = {"datensatz": "Datensatz", "sha256": "Prüfsumme", "herkunft": "Herkunft", "rechteinhaber": "Rechteinhaber",
             "urheber": "Urheber", "lizenz_kuerzel": "Lizenz", "lizenz_url": "Lizenz-Adresse",
             "umfang": "Umfang", "website": "Umfang Website", "attribution": "Nachweis", "ablauf": "Ablauf",
             "quelle_url": "Quelle", "bild_url": "Bildadresse", "bearbeitung": "Bearbeitung", "beleg": "Beleg",
             "geprueft_von": "Geprüft von", "geprueft_am": "Geprüft am", "ki": "KI-Kennzeichen",
             "ki_modell": "KI-Modell", "prompt_hash": "Prompt", "alt": "Alt-Text"}


def art(kuerzel: str) -> Art | None:
    if kuerzel in FEST:
        return FEST[kuerzel]
    m = _CC.fullmatch(kuerzel or "")
    if m and m.group(2) in CC_VERSIONEN:
        return Art(ALLE, nennung=True, url=True)
    return None


def gueltig(kuerzel: str) -> bool:
    return art(kuerzel) is not None


def lizenz_url(kuerzel: str) -> str:
    """Adresse des Lizenztexts (automatisch gesetzt bei CC und Stock, 3.4)."""
    m = _CC.fullmatch(kuerzel or "")
    if m:
        return f"https://creativecommons.org/licenses/by{'-sa' if m.group(1) else ''}/{m.group(2)}/"
    return {"cc0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
            "pdm-1.0": "https://creativecommons.org/publicdomain/mark/1.0/", **STOCK_URL}.get(kuerzel, "")


def lizenz_name(kuerzel: str) -> str:
    m = _CC.fullmatch(kuerzel or "")
    if m:
        return f"CC BY{'-SA' if m.group(1) else ''} {m.group(2)}"
    return NAMEN.get(kuerzel, kuerzel)


_PFADE = ((re.compile(r"/licenses/by/(\d\.\d)(?:/[a-z]{2})?"), "cc-by-{}"),
          (re.compile(r"/licenses/by-sa/(\d\.\d)(?:/[a-z]{2})?"), "cc-by-sa-{}"),
          (re.compile(r"/publicdomain/zero/(1\.0)"), "cc0-{}"),
          (re.compile(r"/publicdomain/mark/(1\.0)"), "pdm-{}"))


def kuerzel_aus_url(url: str) -> str:
    """Kürzel aus einer Lizenz-Adresse bei creativecommons.org (exakte Pfade, sonst leer)."""
    teile = urlsplit((url or "").strip() if "://" in (url or "") else "https:" + (url or "").strip())
    if (teile.hostname or "").lower() not in ("creativecommons.org", "www.creativecommons.org") or teile.query:
        return ""
    for rx, muster in _PFADE:
        m = rx.fullmatch(teile.path.rstrip("/"))
        if m:
            k = muster.format(m.group(1))
            return k if gueltig(k) else ""
    return ""


# ---- Umfang ---------------------------------------------------------------------------------------

def umfang_menge(text: str | None) -> set[str]:
    """Menge aus dem gespeicherten Text; Freitext aus dem Altbestand ergibt eine leere Menge."""
    teile = [t.strip().lower() for t in (text or "").split(",")]
    if not teile or any(t not in UMFAENGE for t in teile):
        return set()
    return set(teile)


def umfang_text(menge) -> str:
    return ",".join(u for u in UMFAENGE if u in set(menge))


def umfang_fuer(kuerzel: str, wunsch=None) -> str:
    """Standard-Umfang je Kürzel (höchster Umfang aus 3.2), höchstens der Wunsch."""
    a = art(kuerzel)
    if a is None:
        return ""
    return umfang_text(a.hoechst if wunsch is None else a.hoechst & set(wunsch))


# ---- Nachweis (3.5) --------------------------------------------------------------------------------

def nachweis_vorschlag(kuerzel: str, *, urheber: str = "", rechteinhaber: str = "", bearbeitung: str = "",
                       quelle: str = "") -> str:
    zusatz = ", zugeschnitten" if bearbeitung == "zugeschnitten" else ""
    if kuerzel == "eigen":
        return f"Foto: Tamil.de / {urheber}" if urheber else "Foto: Tamil.de"
    if kuerzel == "nutzungsrecht":
        return f"Foto: {urheber or rechteinhaber}" if (urheber or rechteinhaber) else ""
    if kuerzel == "presse-redaktionell":
        return f"Foto: {rechteinhaber}" if rechteinhaber else ""
    if _CC.fullmatch(kuerzel or ""):
        return f"Foto: {urheber} / Wikimedia Commons, {lizenz_name(kuerzel)}{zusatz}" if urheber else ""
    if kuerzel in ("cc0-1.0", "pdm-1.0"):
        return f"Foto: {urheber} / Wikimedia Commons, gemeinfrei" if urheber else "Foto: Wikimedia Commons, gemeinfrei"
    if kuerzel in STOCK_URL:
        return f"Symbolfoto: {urheber} / {quelle or kuerzel.capitalize()}" if urheber else ""
    if kuerzel == "ki-symbolbild":
        return KI_CREDIT
    if kuerzel == "tamil-grafik":
        return KARTE_CREDIT
    return ""


def alt_fuer_karte(titel: str) -> str:
    return f"Grafik mit der Überschrift: {titel}"[:ALT_MAX]


def alt_fehler(alt: str | None, titel: str = "") -> str:
    """Leer, wenn der Alt-Text taugt (5.5): 5 bis 160 Zeichen, nicht gleich dem Titel."""
    alt = (alt or "").strip()
    if not alt:
        return "Alt-Text fehlt"
    if len(alt) < ALT_MIN or len(alt) > ALT_MAX:
        return f"Alt-Text muss {ALT_MIN} bis {ALT_MAX} Zeichen haben"
    if titel and alt.casefold() == titel.strip().casefold():
        return "Alt-Text darf nicht der Titel sein"
    return ""


# ---- Vollständigkeit (3.1) -------------------------------------------------------------------------

def automatisch(geprueft_von: str | None) -> bool:
    """Vom Radar selbst festgestellt (Dienst, Agent, Nachführung) – nicht von einer Person im Cockpit."""
    v = geprueft_von or ""
    return v == "dienst" or v.startswith(("agent:", "nachfuehrung"))


def fehlend(asset: dict | None, *, heute: str | None = None) -> list[str]:
    """Schlüssel der fehlenden oder ungültigen Pflichtfelder (leer = vollständig, ohne Blick auf den Umfang)."""
    if not asset:
        return ["datensatz"]
    a = {k: (str(v).strip() if v is not None else "") for k, v in asset.items()}
    out = []
    for feld in ("sha256", "herkunft", "rechteinhaber", "lizenz_kuerzel", "umfang", "attribution", "bearbeitung",
                 "beleg", "geprueft_von", "geprueft_am"):
        if not a.get(feld):
            out.append(feld)
    kuerzel = a.get("lizenz_kuerzel", "")
    lz = art(kuerzel)
    if kuerzel and lz is None:
        out.append("lizenz_kuerzel")
    menge = umfang_menge(a.get("umfang"))
    if a.get("umfang") and (not menge or (lz is not None and not menge <= lz.hoechst)):
        out.append("umfang")
    if lz is not None:
        if lz.nennung and (not a.get("urheber") or _unbekannt(a.get("urheber", ""))):
            out.append("urheber")
        if lz.url and not a.get("lizenz_url"):
            out.append("lizenz_url")
    if a.get("herkunft") == "archiv" and not a.get("urheber"):
        out.append("urheber")
    if a.get("bearbeitung") and any(t.strip() not in BEARBEITUNGEN for t in a["bearbeitung"].split(",")):
        out.append("bearbeitung")
    herkunft = a.get("herkunft", "")
    ki = herkunft in ("ki", "pool") or kuerzel == "ki-symbolbild"
    if not (herkunft in ("ki", "pool", "karte", "archiv") or kuerzel in ("eigen", "ki-symbolbild", "tamil-grafik")) \
            and not a.get("quelle_url"):
        out.append("quelle_url")
    if herkunft in ("register", "quelle", "commons", "stock") and automatisch(a.get("geprueft_von")) \
            and not a.get("bild_url"):
        out.append("bild_url")
    if ki:
        if a.get("ki") not in ("1", "True", "true"):
            out.append("ki")
        for feld in ("ki_modell", "prompt_hash"):
            if not a.get(feld):
                out.append(feld)
    if a.get("ablauf"):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a["ablauf"]) or a["ablauf"] < (heute or date.today().isoformat()):
            out.append("ablauf")
    return list(dict.fromkeys(out))


def _unbekannt(name: str) -> bool:
    from .bildvorschlag import unbekannt

    return unbekannt(name)


def vollstaendig(asset: dict | None) -> bool:
    return not fehlend(asset)


def luecken(store, row: dict) -> list[str]:
    """Was am Bild eines Entwurfs fehlt (Schlüssel aus FELDNAMEN); leer, wenn er kein Bild hat oder alles stimmt."""
    if not row.get("bild_datei"):
        return []
    asset = asset_fuer(store, row)
    out = fehlend(asset)
    if asset and "umfang" not in out and "website" not in umfang_menge(asset.get("umfang")):
        out.append("website")
    if alt_fehler(row.get("bild_alt"), row.get("titel") or ""):
        out.append("alt")
    return out


def asset_fuer(store, row: dict) -> dict | None:
    from .workflow import repo

    return repo.asset_fuer_entwurf(store, row["id"], row.get("bild_datei") or "")


def meldung(luecken_: list[str]) -> str:
    return "Lizenz fehlt: " + ", ".join(FELDNAMEN.get(f, f) for f in luecken_)


def sperre(store, row: dict) -> str:
    """Gate für Freigabe und Sammelfreigabe (3.3): leer = frei, sonst „Lizenz fehlt: <Feld>, …“."""
    fehlt = luecken(store, row)
    return meldung(fehlt) if fehlt else ""


class LizenzFehlt(RuntimeError):
    """Unmittelbar vor dem Senden an WordPress: Datensatz unvollständig – nichts gesendet."""


def pruefen_fuer_wp(store, row: dict) -> dict | None:
    """Wirft LizenzFehlt („Lizenz unvollständig: …“); gibt sonst den Datensatz (oder None ohne Bild) zurück."""
    fehlt = luecken(store, row)
    if fehlt:
        raise LizenzFehlt("Lizenz unvollständig: " + ", ".join(FELDNAMEN.get(f, f) for f in fehlt))
    return asset_fuer(store, row) if row.get("bild_datei") else None


# ---- Datensatz aus einem Bild der Kette ------------------------------------------------------------

def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest() if prompt else ""


def datensatz(image, *, titel: str = "", von: str = "dienst", alt: str = "") -> dict:
    """Felder des Lizenz-Datensatzes für ein Bild aus images/bilder (FeaturedImage). Herkunft aus `image.origin`;
    nur was der Radar selbst festgestellt hat. Upload: alles offen bis zur Eingabe der Redaktion (3.4)."""
    origin = image.origin
    jetzt = now_iso()
    basis = {"geprueft_von": von, "geprueft_am": jetzt}
    if origin == "karte":
        return {"herkunft": "karte", **basis, "rechteinhaber": "Tamil.de", "lizenz_kuerzel": "tamil-grafik",
                "lizenz": "eigene Grafik", "umfang": umfang_fuer("tamil-grafik"),
                "attribution": KARTE_CREDIT, "bearbeitung": "keine", "beleg": "eigene Grafik (images.branded_card)",
                "alt": alt_fuer_karte(titel) if titel else alt}
    if origin in ("ki", "pool"):
        prompt = getattr(image, "prompt", "") or ""
        modell = getattr(image, "modell", "") or ""
        return {"herkunft": origin, **basis, "ki": True, "rechteinhaber": "Tamil.de (KI-generiert)",
                "lizenz_kuerzel": "ki-symbolbild", "lizenz": "KI-generiert – Symbolbild, keine Abbildung des Ereignisses",
                "umfang": umfang_fuer("ki-symbolbild"), "attribution": KI_CREDIT, "bearbeitung": "zugeschnitten",
                "beleg": f"Bild-KI ({modell})" + (" aus dem Bildpool" if origin == "pool" else "") if modell else "",
                "ki_modell": modell, "prompt_hash": prompt_hash(prompt), "alt": alt}
    if origin in STOCK_URL:
        urheber = getattr(image, "urheber", "") or ""
        return {"herkunft": "stock", **basis, "rechteinhaber": urheber, "urheber": urheber,
                "lizenz_kuerzel": origin, "lizenz": lizenz_name(origin), "lizenz_url": STOCK_URL[origin],
                "umfang": umfang_fuer(origin), "attribution": image.credit, "bearbeitung": "zugeschnitten",
                "quelle_url": getattr(image, "quelle_url", "") or "", "bild_url": getattr(image, "bild_url", "") or "",
                "beleg": f"{origin}-api {jetzt}", "alt": alt}
    # upload und alles Unbekannte: nur, was sicher ist (Herkunft, Datei); die Redaktion trägt den Rest ein
    return {"herkunft": "upload" if origin not in HERKUENFTE else origin, "attribution": image.credit or "",
            "bearbeitung": "zugeschnitten", "alt": alt}


def anlegen(store, *, datei: str, daten: bytes, felder: dict, story_id: int | None = None,
            draft_id: int | None = None) -> int:
    """Gemeinsamer Speicherweg: jeder Bildweg legt hier seinen Datensatz an."""
    from .workflow import repo

    felder = dict(felder)
    herkunft = felder.pop("herkunft")
    ki = bool(felder.pop("ki", False))
    return repo.asset_anlegen(store, datei=datei, herkunft=herkunft, ki=ki, story_id=story_id, draft_id=draft_id,
                              daten=daten, **felder)


# ---- Nachführung des Altbestands -------------------------------------------------------------------

def _commons_ergaenzen(asset: dict) -> dict | None:
    """Commons-Datensatz aus dem Agent-Weg vor V9: Lizenztext „<Kurzname> (<Adresse>)“, Rechteinhaber = Urheber."""
    m = re.fullmatch(r"(.+) \((https://creativecommons\.org/[^)\s]+)\)", (asset.get("lizenz") or "").strip())
    kuerzel = kuerzel_aus_url(m.group(2)) if m else ""
    seite = asset.get("quelle_url") or ""
    datei = re.match(r"https://commons\.wikimedia\.org/wiki/File:(.+)$", seite)
    if not kuerzel or not datei or not asset.get("attribution"):
        return None
    urheber = "" if asset.get("rechteinhaber") in ("", "gemeinfrei") else asset["rechteinhaber"]
    if art(kuerzel).nennung and not urheber:
        return None
    hinweis = "Hinweis von Commons" in (asset.get("umfang") or "")
    return {"urheber": urheber, "lizenz_kuerzel": kuerzel, "lizenz_url": m.group(2),
            "umfang": umfang_text({"website"} if hinweis else art(kuerzel).hoechst),
            # Dateiseite und Datei sind auf Commons eindeutig verknüpft: Special:FilePath liefert genau diese Datei
            "bild_url": "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(datei.group(1), safe=""),
            "bearbeitung": "zugeschnitten",
            "beleg": f"nachgeführt aus Commons-Angaben vom {asset.get('erstellt', '')[:16]} (Datensatz {asset['id']})"}


def _register_ergaenzen(store, asset: dict, row: dict) -> dict | None:
    """Register-Datensatz (Weg „quelle“) vor V9: Bildadresse nur, wenn `quelle_bild` des Entwurfs dieselbe Adresse
    ist, die laut Protokoll abgerufen wurde (gleicher Hash) – sonst bleibt der Datensatz offen."""
    from .bildvorschlag import adress_hash

    kandidat = (row.get("quelle_bild") or "").strip()
    if not kandidat or not asset.get("attribution") or not asset.get("rechteinhaber") or not asset.get("quelle_url"):
        return None
    h = adress_hash(kandidat)
    if not store.db.execute("SELECT 1 FROM editorial_actions WHERE draft_id = ? AND aktion = 'bild' AND notiz LIKE ?",
                            (row["id"], f"%Asset {asset['id']},%#{h}%")).fetchone():
        return None
    return {"lizenz_kuerzel": "presse-redaktionell", "umfang": "website", "bild_url": kandidat,
            "bearbeitung": "zugeschnitten",
            "beleg": f"nachgeführt aus Register-Angaben vom {asset.get('erstellt', '')[:16]} (Datensatz {asset['id']})"}


def nachfuehren(store, settings, *, von: str = "nachfuehrung") -> dict:
    """Altbestand: für jeden noch nicht veröffentlichten Entwurf mit Bild den Datensatz ergänzen, wo die vorhandenen
    Angaben vollständig sind (Commons, Register mit belegter Bildadresse, Bildkarte). Nichts wird erfunden; was
    offen bleibt, zeigt im Cockpit „Lizenz fehlt“. Gibt Zähler zurück: ergaenzt, karte, offen, schon."""
    from .workflow import repo

    zaehler = {"ergaenzt": 0, "karte": 0, "offen": 0, "schon": 0}
    status = (*OPEN_STATES, "freigegeben", "fehler")
    rows = [dict(r) for r in store.db.execute(
        f"SELECT id, story_id, titel, bild_datei, bild_origin, bild_credit, bild_alt, quelle_bild FROM drafts "
        f"WHERE bild_datei IS NOT NULL AND bild_datei != '' AND status IN ({','.join('?' for _ in status)})", status)]
    for row in rows:
        asset = repo.asset_fuer_entwurf(store, row["id"], row["bild_datei"])
        if asset and not fehlend(asset):
            zaehler["schon"] += 1
            continue
        neu: dict | None = None
        if asset and asset.get("herkunft") == "commons":
            neu = _commons_ergaenzen(asset)
        elif asset and asset.get("herkunft") in ("quelle", "register"):
            neu = _register_ergaenzen(store, asset, row)
        elif asset and asset.get("herkunft") == "karte" or (asset is None and row.get("bild_origin") == "karte"):
            pfad = settings.bilder_dir / row["bild_datei"]
            if pfad.is_file():
                felder = {k: v for k, v in datensatz(_Karte(), titel="").items() if k not in ("alt", "herkunft")}
                neu = {**felder, "beleg": "Bildkarte laut Entwurf (bild_origin), nachgeführt"}
                if asset is None:
                    repo.asset_anlegen(store, datei=row["bild_datei"], herkunft="karte", story_id=row.get("story_id"),
                                       draft_id=row["id"], daten=pfad.read_bytes(),
                                       **{**neu, "geprueft_von": von, "geprueft_am": now_iso(),
                                          "alt": row.get("bild_alt") or ""})
                    zaehler["karte"] += 1
                    continue
        if neu is None:
            zaehler["offen"] += 1
            continue
        neu = {**neu, "geprueft_von": von, "geprueft_am": now_iso()}
        if not asset.get("sha256"):
            pfad = settings.bilder_dir / row["bild_datei"]
            if pfad.is_file():
                neu["sha256"] = hashlib.sha256(pfad.read_bytes()).hexdigest()
        if not asset.get("alt") and row.get("bild_alt"):
            neu["alt"] = row["bild_alt"]
        sets = ", ".join(f"{k} = ?" for k in neu)
        store._write(f"UPDATE assets SET {sets}, draft_id = COALESCE(draft_id, ?) WHERE id = ?",
                     (*neu.values(), row["id"], asset["id"]))
        if fehlend({**asset, **neu}):
            zaehler["offen"] += 1
        else:
            zaehler["ergaenzt"] += 1
    return zaehler


class _Karte:
    origin = "karte"
    credit = KARTE_CREDIT


# ---- Formular „Lizenz eintragen“ (3.4) -------------------------------------------------------------

# Auswahl im Formular → (Herkunft im Datensatz, erlaubte Kürzel, Bezeichnung)
FORMULAR_HERKUNFT = {
    "eigen": ("upload", ("eigen",), "eigenes Foto"),
    "dritte": ("upload", ("nutzungsrecht",), "Foto von Dritten mit Erlaubnis"),
    "archiv": ("archiv", ("eigen", "nutzungsrecht"), "Archiv"),
    "register": ("register", ("presse-redaktionell", "nutzungsrecht"), "Register-Quelle"),
    "commons": ("commons", ("cc-by", "cc-by-sa", "cc0-1.0", "pdm-1.0"), "Wikimedia Commons"),
    "pexels": ("stock", ("pexels",), "Pexels"),
    "unsplash": ("stock", ("unsplash",), "Unsplash"),
    "presse": ("upload", ("presse-redaktionell",), "Pressematerial (Verleih/Veranstalter)"),
}
BELEG_MAX = 5 * 1024 * 1024
_BELEG_TYPEN = ((b"%PDF-", "pdf"), (b"\x89PNG\r\n\x1a\n", "png"), (b"\xff\xd8\xff", "jpg"))
TEXT_MAX = 200


def formular_herkunft_aus(herkunft: str, kuerzel: str) -> str:
    """Vorbelegung der Auswahl „Herkunft“ aus einem vorhandenen Datensatz."""
    if herkunft in ("commons", "archiv"):
        return herkunft
    if herkunft in ("register", "quelle"):
        return "register"
    if kuerzel in STOCK_URL:
        return kuerzel
    return {"eigen": "eigen", "nutzungsrecht": "dritte", "presse-redaktionell": "presse"}.get(kuerzel, "")


def _wert(form, name: str) -> str:
    return " ".join(str(form.get(name) or "").split())[:TEXT_MAX]


def _umfang_aus(form) -> set[str]:
    werte = form.getlist("umfang") if hasattr(form, "getlist") else form.get("umfang") or []
    if isinstance(werte, str):
        werte = [werte]
    return {w for w in werte if w in UMFAENGE}


def _adresse(url: str) -> bool:
    teile = urlsplit(url)
    return teile.scheme in ("http", "https") and bool(teile.hostname) and " " not in url


def formular_pruefen(form, beleg: tuple[str, bytes] | None, *, titel: str = "",
                     heute: str | None = None) -> tuple[dict, list[str]]:
    """Prüfung nach 3.4. Gibt (Felder für den Datensatz, Fehler) zurück; bei Fehlern ist nichts zu speichern.
    `beleg` = (Dateiname, Inhalt) einer hochgeladenen Belegdatei oder None."""
    fehler: list[str] = []
    wahl = _wert(form, "herkunft")
    if wahl not in FORMULAR_HERKUNFT:
        return {}, ["Herkunft fehlt"]
    herkunft, erlaubt, bezeichnung = FORMULAR_HERKUNFT[wahl]
    basis = _wert(form, "lizenz")
    kuerzel = basis
    if basis in ("cc-by", "cc-by-sa"):
        version = _wert(form, "version")
        kuerzel = f"{basis}-{version}" if version in CC_VERSIONEN else ""
        if not kuerzel:
            fehler.append("CC-Version fehlt")
    if basis not in erlaubt:
        fehler.append(f"Lizenz passt nicht zur Herkunft „{bezeichnung}“" if basis else "Lizenz fehlt")
        kuerzel = ""
    lz = art(kuerzel) if kuerzel else None
    urheber, rechteinhaber = _wert(form, "urheber"), _wert(form, "rechteinhaber")
    if not rechteinhaber:
        fehler.append("Rechteinhaber fehlt")
    if lz is not None and lz.nennung and (not urheber or _unbekannt(urheber)):
        fehler.append("Urheber fehlt (Namensnennung, „unbekannt“ geht nicht)")
    if herkunft == "archiv" and not urheber:
        fehler.append("Urheber fehlt (Archiv)")
    umfang = _umfang_aus(form)
    if not umfang:
        fehler.append("Umfang fehlt")
    elif lz is not None and not umfang <= lz.hoechst:
        fehler.append("Umfang höchstens: " + ", ".join(u.capitalize() for u in UMFAENGE if u in lz.hoechst))
    quelle = str(form.get("quelle_url") or "").strip()
    if kuerzel != "eigen" and not quelle:
        fehler.append("Quelle fehlt (Adresse der Seite)")
    elif quelle and (len(quelle) > 2000 or not _adresse(quelle)):
        fehler.append("Quelle: nur eine http- oder https-Adresse")
    beleg_text = _wert(form, "beleg")
    endung = ""
    if beleg is not None:
        daten = beleg[1]
        endung = next((e for magic, e in _BELEG_TYPEN if daten.startswith(magic)), "")
        if len(daten) > BELEG_MAX:
            fehler.append("Beleg zu groß (höchstens 5 MB)")
            endung = ""
        elif not endung:
            fehler.append("Beleg: nur PDF, PNG oder JPEG")
    if kuerzel == "nutzungsrecht" and not beleg_text and not endung:
        fehler.append("Beleg fehlt (Nutzungsrecht: Datei oder Text, z. B. „Mail vom …“)")
    ablauf = _wert(form, "ablauf")
    if ablauf and (not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ablauf) or ablauf <= (heute or date.today().isoformat())):
        fehler.append("Ablauf muss ein Datum in der Zukunft sein")
    alt = " ".join(str(form.get("alt") or "").split())
    if alt_fehler(alt, titel):
        fehler.append(alt_fehler(alt, titel))
    nachweis = _wert(form, "nachweis") or nachweis_vorschlag(kuerzel, urheber=urheber, rechteinhaber=rechteinhaber,
                                                             bearbeitung="zugeschnitten",
                                                             quelle=bezeichnung if herkunft == "stock" else "")
    if not nachweis:
        fehler.append("Nachweis fehlt")
    if fehler:
        return {}, list(dict.fromkeys(fehler))
    felder = {
        "herkunft": herkunft, "urheber": urheber, "rechteinhaber": rechteinhaber, "lizenz_kuerzel": kuerzel,
        "lizenz": lizenz_name(kuerzel), "lizenz_url": lizenz_url(kuerzel), "umfang": umfang_text(umfang),
        "attribution": nachweis, "ablauf": ablauf, "quelle_url": quelle, "bearbeitung": "zugeschnitten",
        "beleg": f"Eingabe im Cockpit ({bezeichnung})" + (f": {beleg_text}" if beleg_text else ""), "alt": alt,
    }
    if endung:
        felder["_beleg_endung"] = endung
    return felder, []


def beleg_ablegen(data_dir, daten: bytes, endung: str, text: str = "") -> str:
    """Belegdatei unter data/belege/ (nicht öffentlich, nicht unter /bild/); Name = Prüfsumme, nie der Upload-Name."""
    ordner = data_dir / "belege"
    ordner.mkdir(parents=True, exist_ok=True)
    try:
        ordner.chmod(0o700)
    except OSError:
        pass
    name = f"{hashlib.sha256(daten).hexdigest()[:24]}.{endung}"
    pfad = ordner / name
    if not pfad.exists():
        pfad.write_bytes(daten)
        pfad.chmod(0o600)
    return f"{text}; Datei belege/{name}" if text else f"Datei belege/{name}"
