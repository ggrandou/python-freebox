"""Unit tests for the TFTP server API."""
import base64

import pytest

from freebox import Freebox, Tftp, TftpConfig
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"


# ── Fixtures ───────────────────────────────────────────────────────────────────

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
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"settings": True}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token="test-app-token",
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Test data ──────────────────────────────────────────────────────────────────

ROOT_B64 = base64.b64encode(b"/ssd2").decode()

CONFIG_DATA = {"enabled": False, "root": ROOT_B64}
CONFIG_DATA_ENABLED = {"enabled": True, "root": ROOT_B64}


# ── TftpConfig ─────────────────────────────────────────────────────────────────

class TestTftpConfig:
    def test_from_dict(self):
        c = TftpConfig._from_dict(CONFIG_DATA)
        assert c.enabled is False
        assert c.root == ROOT_B64

    def test_root_path_decoded(self):
        c = TftpConfig._from_dict(CONFIG_DATA)
        assert c.root_path == "/ssd2"

    def test_root_path_empty(self):
        c = TftpConfig._from_dict({"enabled": False, "root": ""})
        assert c.root_path == ""

    def test_root_path_invalid_b64_fallback(self):
        c = TftpConfig._from_dict({"enabled": False, "root": "/ssd2"})
        assert c.root_path == "/ssd2"

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/tftp/config/", json=api_ok(CONFIG_DATA))
        c = fb.tftp.config()
        assert isinstance(c, TftpConfig)
        assert c.enabled is False
        assert c.root_path == "/ssd2"

    def test_set(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/tftp/config/", method="PUT", json=api_ok(CONFIG_DATA_ENABLED))
        c = fb.tftp.set_config(enabled=True)
        assert isinstance(c, TftpConfig)
        assert c.enabled is True


# ── Property ───────────────────────────────────────────────────────────────────

class TestTftpProperty:
    def test_property(self, fb):
        assert isinstance(fb.tftp, Tftp)
