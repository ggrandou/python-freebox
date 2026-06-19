"""Unit tests for the Language API."""
import pytest

from freebox import Freebox, Lang, LanguageSupport
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"


@pytest.fixture
def fb(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/api_version", json=DISCOVERY_DATA)
    httpx_mock.add_response(
        url=f"{API}/login/",
        json=api_ok({"logged_in": False, "challenge": "chal"}),
    )
    httpx_mock.add_response(
        url=f"{API}/login/session/",
        method="POST",
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token="test-app-token",
        on_pending=lambda _: None,
    )
    client.open()
    return client


class TestLanguageSupportDataclass:
    def test_from_dict(self):
        info = LanguageSupport._from_dict({"lang": "fra", "avalaible": ["fra", "eng"]})
        assert info.lang == "fra"
        assert info.available == ["fra", "eng"]

    def test_defaults(self):
        info = LanguageSupport._from_dict({})
        assert info.lang == ""
        assert info.available == []

    def test_null_available(self):
        info = LanguageSupport._from_dict({"lang": "eng", "avalaible": None})
        assert info.available == []


class TestLangApi:
    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/lang/",
            json=api_ok({"lang": "fra", "avalaible": ["fra", "eng"]}),
        )
        info = fb.lang.get()
        assert isinstance(info, LanguageSupport)
        assert info.lang == "fra"
        assert info.available == ["fra", "eng"]

    def test_set(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/lang/",
            method="POST",
            json=api_ok(None),
        )
        fb.lang.set("eng")

    def test_property(self, fb):
        assert isinstance(fb.lang, Lang)
