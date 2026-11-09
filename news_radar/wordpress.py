"""WordPress-REST-Anbindung (Vertrag Pos. B.3.2) mit Anwendungspasswort."""

from __future__ import annotations

import logging
import re
import unicodedata

import requests

from .images import FeaturedImage

log = logging.getLogger(__name__)


def slugify(text: str, max_len: int = 70) -> str:
    text = text.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:max_len].rstrip("-") or "beitrag"


class WordPress:
    def __init__(self, base_url: str, user: str, app_password: str, session: requests.Session | None = None):
        self.api = f"{base_url.rstrip('/')}/wp-json/wp/v2"
        self.http = session or requests.Session()
        self.http.auth = (user, app_password)
        self.http.headers["User-Agent"] = "TamilDE-NewsRadar/1.0"
        self._categories: dict[str, int] | None = None
        self._tags: dict[str, int] = {}

    def _req(self, method: str, path: str, **kwargs) -> dict | list:
        resp = self.http.request(method, f"{self.api}/{path}", timeout=30, **kwargs)
        if resp.status_code >= 400:
            raise RuntimeError(f"WordPress {method} {path} -> {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    def category_id(self, slug: str) -> int | None:
        if self._categories is None:
            cats = self._req("GET", "categories", params={"per_page": 100, "_fields": "id,slug"})
            self._categories = {c["slug"]: c["id"] for c in cats}
        return self._categories.get(slug)

    def tag_id(self, name: str) -> int:
        key = name.strip().lower()
        if key in self._tags:
            return self._tags[key]
        found = self._req("GET", "tags", params={"search": name, "per_page": 20, "_fields": "id,name"})
        for tag in found:
            if tag["name"].strip().lower() == key:
                self._tags[key] = tag["id"]
                return tag["id"]
        created = self._req("POST", "tags", json={"name": name.strip()})
        self._tags[key] = created["id"]
        return created["id"]

    def upload_media(self, image: FeaturedImage, alt: str) -> int:
        media = self._req(
            "POST",
            "media",
            data=image.data,
            headers={"Content-Disposition": f'attachment; filename="{image.filename}"', "Content-Type": image.mime},
        )
        self._req("POST", f"media/{media['id']}", json={"alt_text": alt, "caption": image.credit})
        return media["id"]

    def create_post(
        self,
        *,
        title: str,
        content: str,
        excerpt: str,
        status: str,
        category_slug: str,
        tags: list[str],
        media_id: int | None,
        slug: str,
        meta: dict | None = None,
    ) -> dict:
        payload: dict = {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "status": status,
            "slug": slug,
            "tags": [self.tag_id(t) for t in tags if t.strip()],
        }
        cat_id = self.category_id(category_slug) or self.category_id("news")
        if cat_id:
            payload["categories"] = [cat_id]
        if media_id:
            payload["featured_media"] = media_id
        if meta:
            payload["meta"] = meta
        return self._req("POST", "posts", json=payload)

    def edit_link(self, post: dict) -> str:
        base = self.api.removesuffix("/wp-json/wp/v2")
        return f"{base}/wp-admin/post.php?post={post['id']}&action=edit"


class TamilRadarClient:
    """Plugin-Pfad (tamil-radar/v1): ein Aufruf legt Beitrag, Bild, Kategorie, Schlagworte, Meta und SEO an.

    Dubletten erkennt das Plugin an `meta.radar_uid` (409) – `create()` liefert dann {"duplikat": True, "id", "link",
    "edit_link"}, statt zu werfen. Alles andere ≥ 400 wirft RuntimeError wie der Core-Client.
    """

    def __init__(self, base_url: str, user: str, app_password: str, session: requests.Session | None = None):
        self.base = base_url.rstrip("/")
        self.api = f"{self.base}/wp-json/tamil-radar/v1"
        self.http = session or requests.Session()
        self.http.auth = (user, app_password)
        self.http.headers["User-Agent"] = "TamilDE-NewsRadar/1.0"

    def _req(self, method: str, path: str, **kwargs) -> tuple[int, dict]:
        resp = self.http.request(method, f"{self.api}/{path}", timeout=60, **kwargs)
        try:
            data = resp.json()
        except ValueError:
            data = {"text": resp.text[:300]}
        return resp.status_code, data if isinstance(data, dict) else {"data": data}

    def status(self) -> dict | None:
        """None, wenn das Plugin nicht antwortet (dann greift der Core-Client)."""
        try:
            code, data = self._req("GET", "status")
        except requests.RequestException as exc:
            log.info("tamil-radar/v1/status nicht erreichbar: %s", exc)
            return None
        return data if code == 200 and "plugin" in data else None

    def create(self, payload: dict) -> dict:
        code, data = self._req("POST", "beitrag", json=payload)
        if code == 409:
            extra = data.get("data") if isinstance(data.get("data"), dict) else {}
            return {"duplikat": True, "id": extra.get("id"), "link": extra.get("link"), "edit_link": extra.get("edit_link")}
        if code >= 400:
            raise RuntimeError(f"WordPress POST beitrag -> {code}: {str(data)[:300]}")
        return data

    def get(self, uid: str) -> dict | None:
        code, data = self._req("GET", f"beitrag/{uid}")
        return data if code == 200 else None

    def update(self, uid: str, payload: dict) -> dict:
        code, data = self._req("PUT", f"beitrag/{uid}", json=payload)
        if code >= 400:
            raise RuntimeError(f"WordPress PUT beitrag/{uid} -> {code}: {str(data)[:300]}")
        return data

    def edit_link(self, post: dict) -> str:
        return post.get("edit_link") or f"{self.base}/wp-admin/post.php?post={post.get('id')}&action=edit"


def make_client(base_url: str, user: str, app_password: str, session: requests.Session | None = None):
    """Plugin-Client, wenn das Tamil.de-Plugin antwortet, sonst der Core-REST-Client."""
    client = TamilRadarClient(base_url, user, app_password, session)
    if client.status() is not None:
        return client
    return WordPress(base_url, user, app_password, session)
