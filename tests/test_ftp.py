"""Unit tests for the FTP server API."""
import pytest

from freebox import Freebox, Ftp, FtpConfig
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

CONFIG_DATA = {
    "enabled": False,
    "allow_anonymous": False,
    "allow_anonymous_write": False,
    "allow_remote_access": False,
    "weak_password": True,
    "port_ctrl": 3615,
    "port_data": 1337,
    "username": "freebox",
    "remote_domain": "",
}

CONFIG_DATA_ENABLED = {**CONFIG_DATA, "enabled": True, "weak_password": False}


# ── FtpConfig ──────────────────────────────────────────────────────────────────

class TestFtpConfig:
    def test_from_dict(self):
        c = FtpConfig._from_dict(CONFIG_DATA)
        assert c.enabled is False
        assert c.allow_anonymous is False
        assert c.allow_anonymous_write is False
        assert c.allow_remote_access is False
        assert c.weak_password is True
        assert c.port_ctrl == 3615
        assert c.port_data == 1337
        assert c.username == "freebox"
        assert c.remote_domain == ""

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/ftp/config/", json=api_ok(CONFIG_DATA))
        c = fb.ftp.config()
        assert isinstance(c, FtpConfig)
        assert c.enabled is False
        assert c.port_ctrl == 3615

    def test_set(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/ftp/config/", method="PUT", json=api_ok(CONFIG_DATA_ENABLED))
        c = fb.ftp.set_config(enabled=True)
        assert isinstance(c, FtpConfig)
        assert c.enabled is True
        assert c.weak_password is False

    def test_partial_response(self):
        c = FtpConfig._from_dict({"enabled": True, "allow_anonymous": False, "allow_anonymous_write": False})
        assert c.enabled is True
        assert c.port_ctrl == 0
        assert c.username == ""


# ── Property ───────────────────────────────────────────────────────────────────

class TestFtpProperty:
    def test_property(self, fb):
        assert isinstance(fb.ftp, Ftp)
