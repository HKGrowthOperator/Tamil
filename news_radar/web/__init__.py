"""Freigabe-App (Vertrag B.2): Feed, Bearbeiten, Freigeben, Direkt posten, Dashboard, Protokoll.

Start (Entwicklung): python -m news_radar web
Start (Produktion):  gunicorn -w 2 --threads 4 -b 127.0.0.1:8787 --timeout 120 "news_radar.web:create_app()"
"""

from __future__ import annotations

import hmac
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, g, redirect, request, session, url_for

from ..config import Settings, load_settings
from ..store import Store

PUBLIC_ENDPOINTS = {"ui.login", "ui.gesund", "ui.manifest", "ui.service_worker", "static"}


def get_store() -> Store:
    if "store" not in g:
        g.store = Store(g.settings.db_path)
    return g.store


def create_app(settings: Settings | None = None, testing: bool = False) -> Flask:
    settings = settings or load_settings()
    if not settings.web_secret and not testing:
        raise RuntimeError("WEB_SECRET fehlt in .env (z. B. `python -c 'import secrets;print(secrets.token_urlsafe(32))'`)")
    app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/static")
    app.config.update(
        SECRET_KEY=settings.web_secret or secrets.token_urlsafe(32),
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=settings.web_url.startswith("https"),
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
        TESTING=testing,
    )
    app.extensions["settings"] = settings
    app.extensions.setdefault("writer", None)  # lazily: Writer(settings); Tests setzen einen Fake
    app.extensions.setdefault("wordpress", None)

    from .views import ui

    app.register_blueprint(ui)

    @app.before_request
    def _auth():
        g.settings = settings
        if request.endpoint in PUBLIC_ENDPOINTS or request.path.startswith("/static/"):
            return None
        if not session.get("user"):
            return redirect(url_for("ui.login", next=request.path if request.method == "GET" else "/"))
        if request.method == "POST":
            token = request.form.get("_csrf", "")
            if not token or not hmac.compare_digest(token, session.get("csrf", "")):
                abort(400, "Formular abgelaufen – bitte Seite neu laden.")
        return None

    @app.after_request
    def _no_cache(resp):
        if resp.mimetype == "text/html":
            resp.headers["Cache-Control"] = "private, no-store"
        return resp

    @app.teardown_appcontext
    def _close(_exc):
        store = g.pop("store", None)
        if store is not None:
            store.close()

    @app.context_processor
    def _globals():
        return {
            "csrf_token": csrf_token,
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


def check_login(settings: Settings, user: str, password: str) -> bool:
    ok = bool(settings.web_user) and hmac.compare_digest(user, settings.web_user) and hmac.compare_digest(password, settings.web_password)
    if not ok:
        time.sleep(0.7)
    return ok


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


__all__ = ["create_app", "get_store", "check_login", "Path"]
