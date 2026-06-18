"""Unit tests for the file sharing link API."""
import base64

import pytest

from freebox import Freebox, ShareLink, ShareLinks
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def fb(httpx_mock, tmp_path):
    token_file = tmp_path / "token"
    token_file.write_text("test-app-token")
    httpx_mock.add_response(url=f"{BASE}/api_version", json=DISCOVERY_DATA)
    httpx_mock.add_response(
        url=f"{API}/login/",
        json=api_ok({"logged_in": False, "challenge": "chal"}),
    )
    httpx_mock.add_response(
        url=f"{API}/login/session/",
        method="POST",
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"settings": True}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token_file=token_file,
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Test data ──────────────────────────────────────────────────────────────────

PATH_RAW  = base64.b64encode(b"/Disque dur/Photos/Vacances").decode()
PATH_RAW2 = base64.b64encode(b"/Disque dur/shared").decode()

LINK_1 = {
    "token": "gAnweF2Xg5OwcJWn",
    "path": PATH_RAW,
    "name": "Vacances",
    "expire": 1355852344,
    "fullurl": "http://13.37.42.69/api/v8/share/gAnweF2Xg5OwcJWn/",
}

LINK_2 = {
    "token": "s8a+4VtOQNkkQ55f",
    "path": PATH_RAW2,
    "name": "shared",
    "expire": 0,
    "fullurl": "",
}


# ── ShareLink ──────────────────────────────────────────────────────────────────

class TestShareLink:
    def test_from_dict(self):
        l = ShareLink._from_dict(LINK_1)
        assert l.token == "gAnweF2Xg5OwcJWn"
        assert l.path == PATH_RAW
        assert l.name == "Vacances"
        assert l.expire == 1355852344
        assert l.fullurl == "http://13.37.42.69/api/v8/share/gAnweF2Xg5OwcJWn/"

    def test_path_decoded(self):
        l = ShareLink._from_dict(LINK_1)
        assert l.path_decoded == "/Disque dur/Photos/Vacances"

    def test_path_decoded_empty(self):
        l = ShareLink._from_dict({**LINK_1, "path": ""})
        assert l.path_decoded == ""

    def test_path_decoded_invalid_b64_fallback(self):
        l = ShareLink._from_dict({**LINK_1, "path": "/raw/path"})
        assert l.path_decoded == "/raw/path"


# ── ShareLinks API ─────────────────────────────────────────────────────────────

class TestShareLinksApi:
    def test_list(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/share_link/", json=api_ok([LINK_1, LINK_2]))
        links = fb.sharelinks.list()
        assert len(links) == 2
        assert all(isinstance(l, ShareLink) for l in links)
        assert links[0].token == "gAnweF2Xg5OwcJWn"
        assert links[1].token == "s8a+4VtOQNkkQ55f"

    def test_list_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/share_link/", json=api_ok([]))
        assert fb.sharelinks.list() == []

    def test_list_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/share_link/", json=api_ok(None))
        assert fb.sharelinks.list() == []

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/share_link/gAnweF2Xg5OwcJWn", json=api_ok(LINK_1))
        l = fb.sharelinks.get("gAnweF2Xg5OwcJWn")
        assert isinstance(l, ShareLink)
        assert l.token == "gAnweF2Xg5OwcJWn"

    def test_create(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/share_link/", method="POST", json=api_ok(LINK_1))
        l = fb.sharelinks.create(PATH_RAW, expire=1355852344)
        assert isinstance(l, ShareLink)
        assert l.token == "gAnweF2Xg5OwcJWn"

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/share_link/gAnweF2Xg5OwcJWn", method="DELETE", json=api_ok(None)
        )
        fb.sharelinks.delete("gAnweF2Xg5OwcJWn")


# ── Property ───────────────────────────────────────────────────────────────────

class TestShareLinksProperty:
    def test_property(self, fb):
        assert isinstance(fb.sharelinks, ShareLinks)
