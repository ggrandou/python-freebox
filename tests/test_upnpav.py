"""Unit tests for the UPnP AV API."""
import pytest

from freebox import Freebox, UpnpAv, UpnpAvConfig
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


class TestUpnpAvConfigDataclass:
    def test_from_dict(self):
        cfg = UpnpAvConfig._from_dict({"enabled": True})
        assert cfg.enabled is True

    def test_disabled(self):
        cfg = UpnpAvConfig._from_dict({"enabled": False})
        assert cfg.enabled is False

    def test_defaults(self):
        cfg = UpnpAvConfig._from_dict({})
        assert cfg.enabled is False


class TestUpnpAvApi:
    def test_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/upnpav/config/",
            json=api_ok({"enabled": True}),
        )
        cfg = fb.upnpav.config()
        assert isinstance(cfg, UpnpAvConfig)
        assert cfg.enabled is True

    def test_set_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/upnpav/config/",
            method="PUT",
            json=api_ok({"enabled": False}),
        )
        cfg = fb.upnpav.set_config(enabled=False)
        assert cfg.enabled is False

    def test_property(self, fb):
        assert isinstance(fb.upnpav, UpnpAv)
