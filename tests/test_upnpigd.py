"""Unit tests for the UPnP IGD API."""
import pytest

from freebox import Freebox, UpnpIgd, UpnpIgdConfig, UpnpIgdRedir
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

CONFIG_DATA = {"enabled": False, "version": 1}

CONFIG_DATA_ENABLED = {"enabled": True, "version": 2}

REDIR_DATA = {
    "id": "0.0.0.0-53644-udp",
    "enabled": True,
    "proto": "udp",
    "ext_src_ip": "0.0.0.0",
    "ext_port": 53644,
    "int_ip": "192.168.1.44",
    "int_port": 16402,
    "desc": "iC53644",
    "remaining": 0,
    "host": None,
}


# ── UpnpIgdConfig ──────────────────────────────────────────────────────────────

class TestUpnpIgdConfig:
    def test_from_dict(self):
        c = UpnpIgdConfig._from_dict(CONFIG_DATA)
        assert c.enabled is False
        assert c.version == 1

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/upnpigd/config/", json=api_ok(CONFIG_DATA))
        c = fb.upnpigd.config()
        assert isinstance(c, UpnpIgdConfig)
        assert c.enabled is False
        assert c.version == 1

    def test_set(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/upnpigd/config/", method="PUT", json=api_ok(CONFIG_DATA_ENABLED))
        c = fb.upnpigd.set_config(enabled=True, version=2)
        assert isinstance(c, UpnpIgdConfig)
        assert c.enabled is True
        assert c.version == 2


# ── UpnpIgdRedir ──────────────────────────────────────────────────────────────

class TestUpnpIgdRedir:
    def test_from_dict(self):
        r = UpnpIgdRedir._from_dict(REDIR_DATA)
        assert r.id == "0.0.0.0-53644-udp"
        assert r.enabled is True
        assert r.proto == "udp"
        assert r.ext_src_ip == "0.0.0.0"
        assert r.ext_port == 53644
        assert r.int_ip == "192.168.1.44"
        assert r.int_port == 16402
        assert r.desc == "iC53644"
        assert r.remaining == 0

    def test_list(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/upnpigd/redir/", json=api_ok([REDIR_DATA]))
        redirs = fb.upnpigd.redirs()
        assert len(redirs) == 1
        assert isinstance(redirs[0], UpnpIgdRedir)
        assert redirs[0].id == "0.0.0.0-53644-udp"

    def test_list_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/upnpigd/redir/", json=api_ok([]))
        assert fb.upnpigd.redirs() == []

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/upnpigd/redir/0.0.0.0-53644-udp", method="DELETE", json=api_ok(None)
        )
        fb.upnpigd.delete_redir("0.0.0.0-53644-udp")


# ── Property ───────────────────────────────────────────────────────────────────

class TestUpnpIgdProperty:
    def test_property(self, fb):
        assert isinstance(fb.upnpigd, UpnpIgd)
