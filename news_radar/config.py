"""Konfiguration aus Umgebungsvariablen (.env) und sources.toml."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Minimaler .env-Loader; bereits gesetzte Variablen haben Vorrang."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.split(" #", 1)[0].strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


@dataclass
class Source:
    name: str
    type: str
    url: str = ""
    query: str = ""
    language: str = "de"
    provider: str = ""  # kino: cinestar | kinoheld | cineplexx
    endpoint: str = "posts"  # wp_json: posts | mec-events | …
    params: dict = field(default_factory=dict)
    selectors: dict = field(default_factory=dict)  # html: item, title, link, date, summary
    kind: str = "news"  # news | event | kino – Vorgabe für alle Treffer der Quelle
    country: str = ""  # DE | CH | AT, wenn die Quelle eindeutig ein Land abdeckt
    min_score: int | None = None  # Überschreibt die Stichwort-Schwelle (0 = vertrauenswürdige Quelle)
    bezug_noetig: bool = False  # jede Meldung braucht einen Begriff aus [bezug] (Ortsnamen zählen nicht)
    kollywood: bool = False  # Kollywood-Quelle: ihre Nachrichten gelten für die Ausland-Regel als Kino/Entertainment
    max_items: int = 3  # höchstens so viele Treffer je Lauf
    interval_minutes: int = 0  # 0 = bei jedem Lauf abfragen
    # Register (Blueprint): Status, Rechte, Betreiber – `quellen pruefen` schreibt die Messwerte dazu
    enabled: bool = True
    prioritaet: str = "B"  # A = Kernquelle, B = ergänzend, C = nur Hinweise
    betreiber: str = ""
    vertrag: str = ""  # z. B. „Kooperation per Mail 10/2026“; leer = keine Vereinbarung
    rechtlich_geprueft: str = ""  # Datum der Prüfung (YYYY-MM-DD), leer = offen
    robots: str = ""  # erlaubt | verboten | unbekannt (aus der letzten Prüfung)
    paywall: bool = False
    bild_nutzen: bool = False  # Pressebilder der Quelle dürfen übernommen werden (nur mit dokumentierter Erlaubnis)
    notiz: str = ""


@dataclass
class Regions:
    staedte: dict[str, str] = field(default_factory=dict)  # Stadt -> Land (DE/CH/AT)
    laender: dict[str, str] = field(default_factory=dict)  # Begriff -> Land
    aliases: dict[str, list[str]] = field(default_factory=dict)  # Stadt -> andere Schreibweisen
    exakt: set[str] = field(default_factory=set)  # nur mit Großbuchstabe matchen (Essen, Hamm, Bern)
    ausland: list[str] = field(default_factory=list)  # Orte außerhalb von DACH (gegen das Land der Quelle)
    herkunft: list[str] = field(default_factory=list)  # Länder/Regionen (Sri Lanka, Tamil Nadu): nur für Nachrichten
    dach_hinweise: list[str] = field(default_factory=list)  # German, Schweizer, ஜேர்மனி …: nur gegen die Ausland-Regel
    dach_hinweise_wort: list[str] = field(default_factory=list)  # wie dach_hinweise, nur als ganzes Wort (Sion)


# Bildquellen: fest gesperrt, auch wenn jemand sie ins Register schreibt (Host selbst oder eine Subdomain davon)
BILD_GESPERRT = ("instagram.com", "facebook.com", "fbcdn.net", "cdninstagram.com", "tiktok.com", "x.com", "twitter.com",
                 "twimg.com", "youtube.com", "ytimg.com", "pinimg.com", "shutterstock.com", "istockphoto.com",
                 "alamy.com", "picture-alliance.com", "keystone-sda.ch", "keystone.ch", "dpa.com", "reuters.com",
                 "afp.com", "apnews.com", "ap.org", "epa.eu")
BILD_GESPERRT_MARKEN = ("pinterest", "gettyimages", "imago-images")  # unter jeder Endung (pinterest.de, gettyimages.ch …)


def bild_host_gesperrt(host: str) -> bool:
    host = (host or "").lower().rstrip(".").removeprefix("www.")
    if any(host == g or host.endswith("." + g) for g in BILD_GESPERRT):
        return True
    return any(m in host.split(".") for m in BILD_GESPERRT_MARKEN)


GETEILTE_HOSTER = ("wp.com", "wordpress.com", "cloudfront.net", "blogspot.com", "wixstatic.com", "squarespace-cdn.com",
                   "googleusercontent.com", "amazonaws.com", "akamaized.net")
BILDQUELLEN_ARTEN = ("tempel", "verein", "veranstalter", "festival", "kino", "betrieb", "person", "sport")


@dataclass
class Bildquelle:
    """Eintrag im Bildquellen-Register ([[bildquellen]] in sources.toml): Seiten, deren eigenes Bildmaterial tamil.de
    mit dem eingetragenen Nachweis redaktionell verwenden darf (Entscheidung vom 11.11.2026)."""
    host: str
    betreiber: str
    art: str
    nachweis: str
    bild_hosts: list[str] = field(default_factory=list)  # optional: eigenes CDN der Quelle (Subdomains zählen)

    def __post_init__(self) -> None:
        host = (self.host or "").strip()
        for h in (host, *self.bild_hosts):
            if not h or h != h.lower() or h.startswith("www.") or any(c in h for c in "/:@ "):
                raise ValueError(f"Bildquelle: Host klein und ohne www./Pfad angeben ({h!r})")
            if len([t for t in h.split(".") if t]) < 2:
                raise ValueError(f"Bildquelle: Host {h} braucht mindestens zwei Namensteile (z. B. tempel.ch)")
            if bild_host_gesperrt(h):
                raise ValueError(f"Bildquelle: Host {h} ist gesperrt (soziales Netzwerk oder Bildagentur)")
        if not (self.nachweis or "").strip() or not (self.betreiber or "").strip():
            raise ValueError(f"Bildquelle {host}: Nachweis und Betreiber dürfen nicht leer sein")
        if self.art not in BILDQUELLEN_ARTEN:
            raise ValueError(f"Bildquelle {host}: art muss eine von {', '.join(BILDQUELLEN_ARTEN)} sein")
        self.host, self.nachweis, self.betreiber = host, self.nachweis.strip(), self.betreiber.strip()
        self.bild_hosts = list(self.bild_hosts)
        for h in self.bild_hosts:  # geteilte Hoster: dort liegt Material vieler Betreiber, kein eigenes CDN
            if any(h == g or h.endswith("." + g) for g in GETEILTE_HOSTER):
                raise ValueError(f"Bildquelle {host}: bild_hosts {h} ist ein geteilter Hoster")


@dataclass
class Category:
    slug: str
    label: str
    hints: list[str]


# Modell je Rolle (Blueprint): günstige Rollen auf Haiku, Recherche/Faktencheck/Text auf Sonnet, Dossier auf Opus.
# Jede Rolle per .env überschreibbar: RADAR_MODELL_<ROLLE>; RADAR_MODEL bleibt Alias für die Text-Rolle.
ROLLEN_MODELLE = {
    "signal": "claude-haiku-5-5",
    "cluster": "claude-haiku-5-5",
    "recherche": "claude-sonnet-5-5",
    "faktencheck": "claude-sonnet-5-5",
    "text": "claude-sonnet-5-5",
    "lektorat": "claude-haiku-5-5",
    "seo": "claude-haiku-5-5",
    "dossier": "claude-opus-5-5",
    # Zweite KI (Auftrag 13.11.2026): prüft aus frischem Kontext nach der Nachrecherche und jeden fertigen Entwurf –
    # standardmäßig das stärkste Modell der Konfiguration (RADAR_MODELL_PRUEFER)
    "pruefer": "claude-opus-5-5",
}
BILD_REIHENFOLGE = ("archiv", "quelle", "stock", "pool", "ki", "karte")


@dataclass
class Settings:
    sources: list[Source]
    keywords: dict[str, int]
    blocklist: list[str]
    categories: list[Category]
    regions: Regions = field(default_factory=Regions)
    bezug: list[str] = field(default_factory=list)  # Begriffe mit Bezug zur tamilischen Community ([bezug] terms)
    fremdkino: list[str] = field(default_factory=list)  # anderes indisches Kino (Telugu, Bollywood) ([bezug] fremdkino)
    kollywood: list[str] = field(default_factory=list)  # Kollywood und Stars ([bezug] kollywood): Kino für die Ausland-Regel
    blocklist_termine: list[str] = field(default_factory=list)  # Termine, die nie automatisch zur Story werden
    blocklist_termine_wort: list[str] = field(default_factory=list)  # wie blocklist_termine, nur als ganzes Wort
    blocklist_veranstalter: list[str] = field(default_factory=list)  # Veranstalter, deren Termine nie automatisch kommen
    alle_quellen: list[Source] = field(default_factory=list)  # inkl. abgeschalteter (enabled = false)
    bildquellen: list[Bildquelle] = field(default_factory=list)  # Register für den Weg „Bild mit Nachweis“
    anthropic_model: str = "claude-opus-5-5"
    newsapi_key: str = ""
    gnews_token: str = ""
    unsplash_key: str = ""
    pexels_key: str = ""
    gemini_key: str = ""  # Bild-KI (Gemini Nano Banana); leer = Pool/Stock/Karte
    bild_modell: str = "gemini-nano-banana-2.1"
    bild_groesse: str = "1K"  # 1K | 2K | 4K (Großschreibung Pflicht)
    bild_modus: str = "ki"  # ki | pool | stock | karte – wo die Bildkette beginnt
    # KI-Symbolbilder (neu erzeugt oder aus dem Bildpool) nur mit eigenem Ja (Spezifikation Bilder 4.1, L11):
    # Standard aus, unabhängig von GEMINI_API_KEY und BILD_MODUS
    bild_ki_freigabe: bool = False
    bild_retry_pause: float = 2.0
    wp_url: str = ""
    wp_user: str = ""
    wp_app_password: str = ""
    wp_post_status: str = "pending"
    wp_seo_meta: str = "none"  # rankmath | yoast | none
    notify_webhook: str = ""
    web_url: str = "http://127.0.0.1:8787"
    proxy_hops: int = 0  # Reverse-Proxys vor dem Cockpit (Coolify/Traefik: 1) – echte Client-IP und HTTPS erkennen
    lese_token: str = ""  # GET /api/bericht mit Authorization: Bearer – leer = Endpunkt aus
    agent_token: str = ""  # /api/agent/export|import (Agent-Modus übers Netz) – leer = Endpunkte aus
    web_user: str = ""
    web_password: str = ""
    web_secret: str = ""
    max_articles: int = 5
    max_drafts_per_day: int = 40
    max_age_hours: int = 36
    event_max_alter_tage: int = 30  # Termin-Berichte, die laut Quelle älter sind, fallen ohne Datum in der Zukunft heraus
    min_score: int = 4
    min_score_dach: int = 2
    min_relevance: int = 6
    deadline_seconds: int = 270
    fetch_seconds: int = 60
    data_dir: Path = field(default_factory=lambda: ROOT / "data")
    # ---- Redaktion v2 (Multi-Agent) ----
    workflow: str = "v1"  # v1 = ein Aufruf je Beitrag (bisher) · v2 = Rollen, Belege, Jobs
    modelle: dict[str, str] = field(default_factory=lambda: dict(ROLLEN_MODELLE))
    budget_tag_usd: float = 5.0
    budget_monat_usd: float = 150.0
    budget_warnung: float = 0.8
    parallel_jobs: int = 2
    entwuerfe_tag: int = 5  # Pilot: höchstens so viele neue bezahlte Storys je Tag
    nachtrag_entwuerfe_tag: int = 60  # Rückblick: höchstens so viele Nachtrag-Entwürfe je Tag (eigene Grenze)
    bild_reihenfolge: tuple[str, ...] = BILD_REIHENFOLGE
    ki_bilder_je_artikel: int = 1
    recherche_google_news: bool = True  # zweite Quelle über Google-News-RSS suchen (siehe robots-Hinweis im Register)
    modell_aktiv: bool = False  # ANTHROPIC_API_KEY (bzw. RADAR_ANTHROPIC_API_KEY) gesetzt: Worker mit Modell
    kosten_story_usd: float = 1.0  # Kostendeckel je Story (Modellkosten aller Schritte), Dossiers ausgenommen

    def modell_fuer(self, rolle: str) -> str:
        return self.modelle.get(rolle) or ROLLEN_MODELLE.get(rolle) or ROLLEN_MODELLE["text"]

    @property
    def wordpress_enabled(self) -> bool:
        return bool(self.wp_url and self.wp_user and self.wp_app_password)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "radar.sqlite"

    @property
    def bilder_dir(self) -> Path:
        return self.data_dir / "bilder"

    @property
    def bildpool_dir(self) -> Path:
        raw = os.environ.get("BILD_POOL_DIR", "").strip()
        return Path(raw) if raw else self.data_dir / "bildpool"

    def category_slugs(self) -> list[str]:
        return [c.slug for c in self.categories]

    def register_fassung(self) -> str:
        """Fassung des Bildquellen-Registers (Hash der Einträge) für den Beleg eines Lizenz-Datensatzes."""
        import hashlib
        import json
        from dataclasses import asdict

        roh = json.dumps([asdict(b) for b in self.bildquellen], sort_keys=True, ensure_ascii=False, default=str)
        return "register-" + hashlib.sha256(roh.encode("utf-8")).hexdigest()[:12]


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    return int(raw) if raw else default


def _float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip().replace(",", ".")
    return float(raw) if raw else default


def _modelle() -> dict[str, str]:
    modelle = {}
    for rolle, standard in ROLLEN_MODELLE.items():
        wert = os.environ.get(f"RADAR_MODELL_{rolle.upper()}", "").strip()
        if not wert and rolle == "text":
            wert = os.environ.get("RADAR_MODEL", "").strip()
        modelle[rolle] = wert or standard
    return modelle


def _reihenfolge(raw: str) -> tuple[str, ...]:
    teile = tuple(t.strip().lower() for t in raw.split(",") if t.strip() in BILD_REIHENFOLGE)
    return teile if teile else BILD_REIHENFOLGE


def _radar_schluessel() -> None:
    """RADAR_ANTHROPIC_API_KEY gilt nur für den Radar-Prozess: In einer Claude-Code-Umgebung würde ANTHROPIC_API_KEY
    auch die Sitzung selbst über diesen Schlüssel abrechnen lassen. Ein gesetzter ANTHROPIC_API_KEY hat Vorrang."""
    radar = os.environ.get("RADAR_ANTHROPIC_API_KEY", "").strip()
    if radar and not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = radar


def load_settings(sources_file: Path = ROOT / "sources.toml") -> Settings:
    load_dotenv()
    _radar_schluessel()
    raw = tomllib.loads(sources_file.read_text(encoding="utf-8"))
    alle_quellen = [Source(**s) for s in raw.get("source", [])]
    sources = [s for s in alle_quellen if s.enabled]
    reg = raw.get("regions", {})
    regions = Regions(
        staedte={stadt: land.upper() for land, cities in reg.get("staedte", {}).items() for stadt in cities},
        laender={term: land.upper() for land, terms in reg.get("laender", {}).items() for term in terms},
        aliases={k: list(v) for k, v in reg.get("aliases", {}).items()},
        exakt=set(reg.get("exakt", [])),
        ausland=list(reg.get("ausland", [])),
        herkunft=list(reg.get("herkunft", [])),
        dach_hinweise=list(reg.get("dach_hinweise", [])),
        dach_hinweise_wort=list(reg.get("dach_hinweise_wort", [])),
    )
    categories = [
        Category(slug=slug, label=c["label"], hints=[h.lower() for h in c.get("hints", [])])
        for slug, c in raw.get("categories", {}).items()
    ]
    env = os.environ.get
    return Settings(
        sources=sources,
        data_dir=Path(env("RADAR_DATA_DIR")).expanduser() if env("RADAR_DATA_DIR") else ROOT / "data",
        keywords={k.lower(): int(v) for k, v in raw.get("keywords", {}).items()},
        blocklist=[t.lower() for t in raw.get("blocklist", {}).get("terms", [])],
        blocklist_termine=[t.lower() for t in raw.get("blocklist", {}).get("termine", [])],
        blocklist_termine_wort=[t.lower() for t in raw.get("blocklist", {}).get("termine_wort", [])],
        blocklist_veranstalter=[t.lower() for t in raw.get("blocklist", {}).get("veranstalter", [])],
        categories=categories,
        regions=regions,
        bezug=[t.lower() for t in raw.get("bezug", {}).get("terms", [])],
        fremdkino=[t.lower() for t in raw.get("bezug", {}).get("fremdkino", [])],
        kollywood=[t.lower() for t in raw.get("bezug", {}).get("kollywood", [])],
        alle_quellen=alle_quellen,
        bildquellen=[Bildquelle(**b) for b in raw.get("bildquellen", [])],
        anthropic_model=env("RADAR_MODEL", "claude-opus-5-5"),
        newsapi_key=env("NEWSAPI_KEY", ""),
        gnews_token=env("GNEWS_TOKEN", ""),
        unsplash_key=env("UNSPLASH_ACCESS_KEY", ""),
        pexels_key=env("PEXELS_API_KEY", ""),
        gemini_key=env("GEMINI_API_KEY", ""),
        bild_modell=env("BILD_MODELL", "") or "gemini-nano-banana-2.1",
        bild_groesse=(env("BILD_GROESSE", "") or "1K").upper(),
        bild_modus=(env("BILD_MODUS", "") or "ki").lower(),
        bild_ki_freigabe=(env("BILD_KI_FREIGABE", "") or "0").strip().lower() in ("1", "ja", "true", "an"),
        wp_url=env("WP_URL", "").rstrip("/"),
        wp_user=env("WP_USER", ""),
        wp_app_password=env("WP_APP_PASSWORD", ""),
        wp_post_status=env("WP_POST_STATUS", "publish") or "publish",
        wp_seo_meta=(env("WP_SEO_META", "none") or "none").lower(),
        notify_webhook=env("NOTIFY_WEBHOOK_URL", ""),
        web_url=(env("RADAR_WEB_URL", "") or "http://127.0.0.1:8787").rstrip("/"),
        proxy_hops=max(0, _int("RADAR_PROXY_HOPS", 0)),
        lese_token=env("RADAR_LESE_TOKEN", "").strip(),
        agent_token=env("RADAR_AGENT_TOKEN", "").strip(),
        web_user=env("WEB_USER", ""),
        web_password=env("WEB_PASSWORD", ""),
        web_secret=env("WEB_SECRET", ""),
        max_articles=_int("RADAR_MAX_ARTICLES", 5),
        max_drafts_per_day=_int("RADAR_MAX_DRAFTS_PER_DAY", 40),
        max_age_hours=_int("RADAR_MAX_AGE_HOURS", 36),
        event_max_alter_tage=_int("RADAR_EVENT_MAX_ALTER_TAGE", 30),
        min_score=_int("RADAR_MIN_SCORE", 4),
        min_score_dach=_int("RADAR_MIN_SCORE_DACH", 2),
        min_relevance=_int("RADAR_MIN_RELEVANCE", 6),
        deadline_seconds=_int("RADAR_DEADLINE_SECONDS", 270),
        fetch_seconds=_int("RADAR_FETCH_SECONDS", 60),
        workflow=(env("RADAR_WORKFLOW", "") or "v1").lower(),
        modelle=_modelle(),
        budget_tag_usd=_float("RADAR_BUDGET_TAG_USD", 5.0),
        budget_monat_usd=_float("RADAR_BUDGET_MONAT_USD", 150.0),
        budget_warnung=_float("RADAR_BUDGET_WARNUNG", 0.8),
        parallel_jobs=max(1, _int("RADAR_PARALLEL_JOBS", 2)),
        entwuerfe_tag=_int("RADAR_ENTWUERFE_TAG", 5),
        nachtrag_entwuerfe_tag=_int("RADAR_NACHTRAG_TAG", 60),
        bild_reihenfolge=_reihenfolge(env("BILD_REIHENFOLGE", "")),
        ki_bilder_je_artikel=_int("RADAR_KI_BILDER_JE_ARTIKEL", 1),
        recherche_google_news=(env("RADAR_RECHERCHE_GOOGLE_NEWS", "1") or "1") not in ("0", "nein", "false"),
        modell_aktiv=bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
        kosten_story_usd=_float("RADAR_KOSTEN_STORY_USD", 1.0),
    )
