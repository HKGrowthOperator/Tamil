"""Zugänge zum lokalen WordPress aus der Umgebung (siehe conftest.py). Eigenes Modul, damit Tests sie importieren
können, ohne sich auf den Modulnamen „conftest“ zu verlassen."""

import os

URL = os.environ.get("WP_TEST_URL", "").rstrip("/")
USER = os.environ.get("WP_TEST_USER", "")
PW = os.environ.get("WP_TEST_APP_PASSWORD", "")
ADMIN_PW = os.environ.get("WP_ADMIN_APP_PASSWORD", "")
ADMIN_USER = os.environ.get("WP_ADMIN_USER") or ("admin" if ADMIN_PW else "")
WP_CLI = os.environ.get("WP_TEST_WP_CLI", "")
