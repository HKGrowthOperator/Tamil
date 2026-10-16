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
