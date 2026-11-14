"""Freigabe-App (Vertrag B.2): Feed, Bearbeiten, Freigeben, Direkt posten, Dashboard, Protokoll.

Start (Entwicklung): python -m news_radar web
Start (Produktion):  gunicorn -w 2 --threads 4 -b 127.0.0.1:8787 --timeout 120 "news_radar.web:create_app()"
"""

from __future__ import annotations

import hmac
import secrets
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, abort, g, redirect, render_template, request, session, url_for

from ..config import Settings, load_settings
from ..render import safe_url
from ..store import Store

PUBLIC_ENDPOINTS = {"ui.login", "ui.gesund", "ui.manifest", "ui.service_worker", "static",
                    # prüfen ihr eigenes Bearer-Token (RADAR_LESE_TOKEN bzw. RADAR_AGENT_TOKEN), kein Cookie, kein CSRF
                    "api.bericht", "api.agent_export", "api.agent_import", "api.agent_vorschlag",
                    "api.agent_bild"}
MIN_PASSWORT = 12


def gleich(a: str | None, b: str | None) -> bool:
    """Zeitkonstanter Vergleich, der auch bei Umlauten und anderen Nicht-ASCII-Zeichen nicht abstürzt."""
    return hmac.compare_digest((a or "").encode("utf-8"), (b or "").encode("utf-8"))


class Drossel:
    """Fehlversuche beim Login je Schlüssel (IP, Benutzername) in einem Zeitfenster zählen. Kein Schlafen im Worker:
    wer das Limit erreicht, bekommt bis zum Ende des Fensters sofort 429."""

    def __init__(self, grenzen: dict[str, int] | None = None, fenster: int = 15 * 60, uhr=time.monotonic):
        self.grenzen = grenzen or {"ip": 10, "nutzer": 20}
        self.fenster = fenster
        self.uhr = uhr
        self._fehler: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def _frisch(self, schluessel: str) -> list[float]:
        grenze = self.uhr() - self.fenster
        liste = [t for t in self._fehler.get(schluessel, []) if t > grenze]
        if liste:
            self._fehler[schluessel] = liste
        else:
            self._fehler.pop(schluessel, None)
        return liste

    def gesperrt(self, schluessel: dict[str, str]) -> bool:
        with self._lock:
            return any(len(self._frisch(f"{art}:{wert}")) >= self.grenzen.get(art, 10) for art, wert in schluessel.items())

    def fehler(self, schluessel: dict[str, str]) -> None:
        with self._lock:
            if len(self._fehler) > 10_000:  # Speicher begrenzen
                self._fehler.clear()
            for art, wert in schluessel.items():
                self._fehler.setdefault(f"{art}:{wert}", []).append(self.uhr())

    def erfolg(self, schluessel: dict[str, str]) -> None:
        with self._lock:
            self._fehler.pop(f"ip:{schluessel.get('ip', '')}", None)


def client_ip() -> str:
    """Hinter cloudflared kommt jede Anfrage von 127.0.0.1 – dann zählt der Header von Cloudflare."""
    addr = request.remote_addr or ""
    if addr in ("127.0.0.1", "::1"):
        return request.headers.get("CF-Connecting-IP", "").strip()[:64] or addr
    return addr


def get_store() -> Store:
    if "store" not in g:
        g.store = Store(g.settings.db_path)
    return g.store


def _origin(url: str) -> str:
    """Schema + Host (+ Port) einer Adresse, wie CSP sie erwartet."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}" if parts.scheme and parts.netloc else ""


def _embedded(settings: Settings) -> bool:
    """Wird das Cockpit unter HTTPS von einem anderen Host (WordPress-Backend) eingebettet?"""
    return bool(settings.wp_url) and settings.web_url.startswith("https") and _origin(settings.wp_url) != _origin(settings.web_url)


def create_app(settings: Settings | None = None, testing: bool = False) -> Flask:
    settings = settings or load_settings()
    if not settings.web_secret and not testing:
        raise RuntimeError("WEB_SECRET fehlt in .env (z. B. `python -c 'import secrets;print(secrets.token_urlsafe(32))'`)")
    if settings.web_user and len(settings.web_password or "") < MIN_PASSWORT and not testing:
        raise RuntimeError(f"WEB_PASSWORD fehlt oder ist kürzer als {MIN_PASSWORT} Zeichen – ohne Passwort startet das "
                           "Cockpit nicht (oder WEB_USER leer lassen und nur Benutzer aus `nutzer anlegen` verwenden)")
    app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/static")
    app.config.update(
        SECRET_KEY=settings.web_secret or secrets.token_urlsafe(32),
        # Im WordPress-Backend eingebettet (iframe, anderer Host) braucht das Cookie SameSite=None – das geht nur mit
        # Secure, also nur unter HTTPS. Lokal (http) bleibt es bei Lax; dort öffnet das Backend das Cockpit im Tab.
        SESSION_COOKIE_SAMESITE="None" if _embedded(settings) else "Lax",
        SESSION_COOKIE_SECURE=settings.web_url.startswith("https"),
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
        TESTING=testing,
    )
    app.extensions["settings"] = settings
    app.extensions.setdefault("writer", None)  # lazily: Writer(settings); Tests setzen einen Fake
    app.extensions.setdefault("wordpress", None)
    app.extensions["drossel"] = Drossel()
    app.jinja_env.filters["safe_url"] = safe_url

    from .api import api
    from .betrieb import betrieb
    from .eingang import eingang_bp
    from .redaktion import red
    from .social import social
    from .views import ui

    app.register_blueprint(ui)
    app.register_blueprint(red)
    app.register_blueprint(betrieb)
    app.register_blueprint(eingang_bp)
    app.register_blueprint(api)
    app.register_blueprint(social)

    @app.errorhandler(403)
    def _verboten(exc):
        text = exc.description if getattr(exc, "description", "").startswith("Ihre Rolle") else \
            "Dafür fehlt Ihrer Rolle das Recht. Ansehen geht weiter."
        return render_template("fehler.html", titel="Keine Berechtigung", text=text), 403
    if settings.proxy_hops:
        # Hinter Coolify/Traefik: echte Client-IP (Login-Drossel) und HTTPS aus den X-Forwarded-Kopfzeilen
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=settings.proxy_hops, x_proto=settings.proxy_hops,
                                x_host=settings.proxy_hops)

    @app.before_request
    def _auth():
        g.settings = settings
        if request.endpoint in PUBLIC_ENDPOINTS or request.path.startswith("/static/"):
            return None
        sitzung = sitzung_gueltig(settings, get_store(), session.get("sid", ""), session.get("user", ""))
        if sitzung is None:
            if session.get("user"):
                session.pop("user", None)
                session.pop("rolle", None)
                session.pop("sid", None)
            return redirect(url_for("ui.login", next=request.path if request.method == "GET" else "/"))
        session["rolle"] = sitzung["rolle"]  # Rollenwechsel wirkt sofort
        if request.method == "POST":
            token = request.form.get("_csrf", "")
            if not token or not gleich(token, session.get("csrf", "")):
                abort(400, "Formular abgelaufen – bitte Seite neu laden.")
        return None

    frame_ancestors = "frame-ancestors 'self'" + (f" {_origin(settings.wp_url)}" if settings.wp_url else "")
    # Kein Inline-Skript, keine Plugins, keine fremde <base>: ein durchgerutschtes onerror= läuft nicht
    csp = f"script-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; {frame_ancestors}"

    @app.after_request
    def _headers(resp):
        if resp.mimetype == "text/html":
            resp.headers["Cache-Control"] = "private, no-store"
        # Einbetten nur durch die eigene Seite und das WordPress-Backend (WP_URL) – sonst Clickjacking-Schutz
        resp.headers["Content-Security-Policy"] = csp
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "same-origin"
        return resp

    @app.teardown_appcontext
    def _close(_exc):
        store = g.pop("store", None)
        if store is not None:
            store.close()

    @app.context_processor
    def _globals():
        import math

        def letzter_lauf():
            runs = get_store().recent_runs(1)
            return runs[0] if runs else None

        def offen():
            counts = get_store().counts_by_status()
            return sum(counts.get(s, 0) for s in ("neu", "bearbeitet", "zurueckgestellt"))

        def polar(i: int, n: int, r: float) -> tuple[float, float]:
            a = 2 * math.pi * i / max(n, 1) - math.pi / 2
            return round(50 + r * math.cos(a), 1), round(50 + r * math.sin(a), 1)

        def budget():
            if "budget_stand" not in g:
                from .redaktion import budget_stand

                g.budget_stand = budget_stand(get_store())
            return g.budget_stand

        def recherche_offen():
            return get_store().db.execute("SELECT COUNT(*) FROM stories WHERE status = 'recherche_erforderlich'").fetchone()[0]

        def eingang_offen():
            return get_store().db.execute("SELECT COUNT(*) FROM einsendungen WHERE status IN ('abgeholt', "
                                          "'vorbereitet')").fetchone()[0]

        def stopps():
            if "stopps" not in g:
                from .. import schalter

                g.stopps = schalter.aktive(get_store())
            return g.stopps

        from .rechte import darf

        return {
            "darf": darf,
            "schalter_label": lambda k: __import__("news_radar.schalter", fromlist=["LABEL"]).LABEL.get(k, k),
            "stopps": stopps,
            "budget": budget,
            "recherche_offen": recherche_offen,
            "eingang_offen": eingang_offen,
            "ist_admin": session.get("rolle") == "admin",
            "csrf_token": csrf_token,
            "letzter_lauf": letzter_lauf,
            "offen": offen,
            "polar": polar,
            "settings": settings,
            "fmt_dt": fmt_dt,
            "age": age,
            "category_label": lambda slug: next((c.label for c in settings.categories if c.slug == slug), slug),
            "wordpress_enabled": settings.wordpress_enabled or app.extensions.get("wordpress") is not None,
        }

    return app


def csrf_token() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def anmelden(settings: Settings, user: str, password: str, store: Store | None = None) -> tuple[str, str] | None:
    """(Rolle, Konto) oder None. Zuerst die Benutzer-Tabelle (Konto „db“), dann WEB_USER aus der .env (Konto „env“,
    immer admin – der Notzugang, wenn niemand mehr in der Tabelle steht). Ohne Passwort gibt es keinen .env-Zugang."""
    if store is not None:
        from ..workflow import repo

        nutzer = repo.nutzer_pruefen(store, user, password)
        if nutzer:
            return nutzer["rolle"], "db"
    if settings.web_user and settings.web_password and gleich(user, settings.web_user) and gleich(password, settings.web_password):
        return "admin", "env"
    return None


def check_login(settings: Settings, user: str, password: str, store: Store | None = None) -> str | None:
    """Nur die Rolle (redaktion | admin) oder None."""
    ergebnis = anmelden(settings, user, password, store)
    return ergebnis[0] if ergebnis else None


def sitzung_gueltig(settings: Settings, store: Store, sid: str, user: str) -> dict | None:
    """Die Sitzung aus dem Cookie gegen die Tabelle `sitzungen` prüfen: abgemeldet, gesperrt, abgelaufen oder ein
    geändertes .env-Konto beenden sie sofort – auch für eine kopierte Cookie-Datei."""
    if not sid or not user:
        return None
    from ..workflow import repo

    sitzung = repo.sitzung_pruefen(store, sid)
    if sitzung is None or not gleich(sitzung["nutzer"], user):
        return None
    if sitzung["konto"] == "env":
        if not (settings.web_user and settings.web_password and gleich(user, settings.web_user)):
            return None
        sitzung["rolle"] = "admin"
    return sitzung


def fmt_dt(value: str | None, with_time: bool = True) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    if dt.tzinfo:
        from zoneinfo import ZoneInfo

        dt = dt.astimezone(ZoneInfo("Europe/Berlin"))
    return dt.strftime("%d.%m.%Y %H:%M" if with_time else "%d.%m.%Y")


def age(value: str | None) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return ""
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    minutes = int((datetime.now(timezone.utc) - dt).total_seconds() // 60)
    if minutes < 60:
        return f"vor {minutes} Min."
    if minutes < 60 * 24:
        return f"vor {minutes // 60} Std."
    return f"vor {minutes // (60 * 24)} Tagen"


__all__ = ["create_app", "get_store", "check_login", "anmelden", "gleich", "Path"]
