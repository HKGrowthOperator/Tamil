"""SSRF-Schutz, Weiterleitungen, Größenlimit und bedingte Abrufe von net.safe_get – ohne Netz."""

import pytest

from news_radar import net

ECHTE_SAFE_SESSION = net._safe_session  # vor dem Test-Fixture, das sie durch requests ersetzt


class Resp:
    def __init__(self, status=200, body=b"ok", headers=None):
        self.status_code = status
        self._body = body
        self.headers = {"Content-Type": "text/html; charset=utf-8", **(headers or {})}
        self.closed = False

    def iter_content(self, size):
        for i in range(0, len(self._body), size):
            yield self._body[i:i + size]

    def close(self):
        self.closed = True


class Session:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def get(self, url, **kw):
        self.calls.append((url, kw))
        return self.routes[url]


PUBLIC = lambda host: ["93.184.216.34"]  # noqa: E731


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/admin", "http://localhost:8787/", "http://10.0.0.5/", "http://192.168.1.1/",
    "http://169.254.169.254/latest/meta-data/", "http://[::1]/", "http://[::ffff:127.0.0.1]/", "http://0.0.0.0/",
])
def test_internal_addresses_are_blocked(url):
    resolve = lambda host: ["127.0.0.1"] if host == "localhost" else []  # noqa: E731
    with pytest.raises(net.UnsafeURL):
        net.check_url(url, resolve)


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/x", "gopher://x", "https://user:pw@example.com/"])
def test_schemes_and_credentials_are_blocked(url):
    with pytest.raises(net.UnsafeURL):
        net.check_url(url, PUBLIC)


def test_hostname_resolving_to_private_address_is_blocked():
    with pytest.raises(net.UnsafeURL):
        net.check_url("https://intern.example.com/", lambda host: ["93.184.216.34", "10.1.2.3"])


def test_redirect_to_internal_address_is_blocked():
    session = Session({"https://example.com/a": Resp(302, headers={"Location": "http://169.254.169.254/latest"})})
    with pytest.raises(net.UnsafeURL):
        net.safe_get("https://example.com/a", session=session, resolve=PUBLIC)
    assert len(session.calls) == 1


def test_redirects_are_followed_and_limited():
    session = Session({
        "https://example.com/a": Resp(301, headers={"Location": "/b"}),
        "https://example.com/b": Resp(200, b"<p>hallo</p>"),
    })
    got = net.safe_get("https://example.com/a", session=session, resolve=PUBLIC)
    assert got.url == "https://example.com/b" and got.text == "<p>hallo</p>"
    assert all(kw["allow_redirects"] is False for _, kw in session.calls)
    loop = Session({"https://example.com/x": Resp(302, headers={"Location": "/x"})})
    with pytest.raises(net.UnsafeURL):
        net.safe_get("https://example.com/x", session=loop, resolve=PUBLIC)


def test_size_limit_and_content_type():
    big = Session({"https://example.com/big": Resp(200, b"x" * 2000)})
    with pytest.raises(net.ResponseTooLarge):
        net.safe_get("https://example.com/big", session=big, resolve=PUBLIC, max_bytes=1000)
    declared = Session({"https://example.com/d": Resp(200, b"x", headers={"Content-Length": "999999"})})
    with pytest.raises(net.ResponseTooLarge):
        net.safe_get("https://example.com/d", session=declared, resolve=PUBLIC, max_bytes=1000)
    html = Session({"https://example.com/bild.jpg": Resp(200, b"<html>")})
    with pytest.raises(net.WrongContentType):
        net.safe_get("https://example.com/bild.jpg", session=html, resolve=PUBLIC, accept=net.IMAGE_TYPES)


def test_http_errors_and_conditional_requests():
    session = Session({"https://example.com/feed": Resp(429)})
    with pytest.raises(net.HTTPError) as err:
        net.safe_get("https://example.com/feed", session=session, resolve=PUBLIC)
    assert err.value.status == 429
    cond = Session({"https://example.com/rss": Resp(304, b"", headers={"ETag": '"abc"'})})
    got = net.safe_get("https://example.com/rss", session=cond, resolve=PUBLIC, etag='"abc"', last_modified="Mon")
    assert got.not_modified and got.etag == '"abc"'
    sent = cond.calls[0][1]["headers"]
    assert sent["If-None-Match"] == '"abc"' and sent["If-Modified-Since"] == "Mon"


def test_idna_host_is_checked_as_requests_connects_to_it():
    gesehen = []
    net.check_url("https://evilß.com/", lambda host: gesehen.append(host) or ["93.184.216.34"])
    assert gesehen == ["xn--evil-yna.com"]


def test_peer_address_is_checked_after_connect(monkeypatch):
    """DNS-Rebinding: die Vorabprüfung sieht eine öffentliche Adresse, die Verbindung landet auf 127.0.0.1."""
    import http.server
    import socket
    import threading

    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(net, "_SAFE_SESSION", None)
    monkeypatch.setattr(net, "_safe_session", ECHTE_SAFE_SESSION)
    srv = http.server.HTTPServer(("127.0.0.1", 0), http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    orig = socket.getaddrinfo
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, *a, **kw: orig("127.0.0.1" if host == "rebind.test" else host, *a, **kw))
    try:
        with pytest.raises(net.UnsafeURL):
            net.safe_get(f"http://rebind.test:{srv.server_address[1]}/", resolve=PUBLIC)
    finally:
        srv.shutdown()

