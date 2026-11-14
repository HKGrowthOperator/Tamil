"""FakeMeta: nachgestellte Graph API für Tests und Abnahme (kein Netz). Zählt jeden Aufruf mit seinen Daten.

  FakeMeta()                                         alles gelingt
  FakeMeta(container_status=["IN_PROGRESS", ...])    Container braucht mehrere Abfragen (letzter Wert bleibt)
  FakeMeta(abbruch_bei=("ig_veroeffentlichen",),
           kommt_an=True)                            Verbindung bricht beim ersten Aufruf ab; Meta hat ihn trotzdem
  FakeMeta(fehler={"ig_container": ZugangFehler(190, "…")})   der Aufruf wirft die Ausnahme
"""

from __future__ import annotations

from .transport import UnklarFehler


class FakeMeta:
    live = True

    def __init__(self, *, container_status=("FINISHED",), abbruch_bei=(), kommt_an=True, fehler=None,
                 limit=(0, 100)):
        self.aufrufe: list[tuple[str, dict]] = []
        self._status = list(container_status)
        self._abbruch = set(abbruch_bei)
        self._kommt_an = kommt_an
        self._fehler = dict(fehler or {})
        self._limit = limit
        self._container: dict[str, dict] = {}
        self.ig_beitraege: list[dict] = []
        self.fb_beitraege: list[dict] = []
        self._n = 0

    def _auf(self, name: str, **daten) -> None:
        self.aufrufe.append((name, daten))
        if name in self._fehler:
            raise self._fehler.pop(name)

    def _id(self, art: str) -> str:
        self._n += 1
        return f"{art}{17841400000 + self._n}"

    def ig_container(self, image_url: str, caption: str, alt_text: str) -> str:
        self._auf("ig_container", image_url=image_url, caption=caption, alt_text=alt_text)
        cid = self._id("c")
        self._container[cid] = {"caption": caption}
        return cid

    def ig_status(self, container_id: str) -> str:
        self._auf("ig_status", container_id=container_id)
        return self._status.pop(0) if len(self._status) > 1 else self._status[0]

    def ig_limit(self) -> tuple[int, int]:
        self._auf("ig_limit")
        return self._limit

    def ig_veroeffentlichen(self, container_id: str) -> str:
        self._auf("ig_veroeffentlichen", container_id=container_id)
        mid = self._id("m")
        if "ig_veroeffentlichen" in self._abbruch:
            self._abbruch.discard("ig_veroeffentlichen")
            if self._kommt_an:
                self.ig_beitraege.append({"id": mid, "caption": self._container[container_id]["caption"],
                                          "permalink": f"https://www.instagram.com/p/{mid}/"})
            raise UnklarFehler("Verbindung abgebrochen (Fake)")
        self.ig_beitraege.append({"id": mid, "caption": self._container[container_id]["caption"],
                                  "permalink": f"https://www.instagram.com/p/{mid}/"})
        return mid

    def ig_permalink(self, media_id: str) -> str:
        self._auf("ig_permalink", media_id=media_id)
        return f"https://www.instagram.com/p/{media_id}/"

    def ig_letzte(self) -> list[dict]:
        self._auf("ig_letzte")
        return list(reversed(self.ig_beitraege))

    def fb_foto(self, url: str, caption: str, alt_text: str) -> dict:
        self._auf("fb_foto", url=url, caption=caption, alt_text=alt_text)
        pid = self._id("p")
        eintrag = {"id": pid, "message": caption, "permalink_url": f"https://www.facebook.com/{pid}"}
        if "fb_foto" in self._abbruch:
            self._abbruch.discard("fb_foto")
            if self._kommt_an:
                self.fb_beitraege.append(eintrag)
            raise UnklarFehler("Verbindung abgebrochen (Fake)")
        self.fb_beitraege.append(eintrag)
        return {"id": pid, "post_id": pid}

    def fb_permalink(self, post_id: str) -> str:
        self._auf("fb_permalink", post_id=post_id)
        return f"https://www.facebook.com/{post_id}"

    def fb_letzte(self) -> list[dict]:
        self._auf("fb_letzte")
        return list(reversed(self.fb_beitraege))
