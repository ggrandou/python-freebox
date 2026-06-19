"""Unit tests for the Network Share (Samba / AFP) API."""
import pytest

from freebox import AfpConfig, Freebox, NetShare, SambaConfig
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

SAMBA_DATA = {
    "file_share_enabled": True,
    "print_share_enabled": True,
    "logon_enabled": False,
    "logon_user": "freebox",
    "workgroup": "WORKGROUP",
    "smbv2_enabled": True,
}

AFP_DATA = {
    "enabled": False,
    "guest_allow": True,
    "login_name": "freebox",
    "server_type": "airport",
}


# ── SambaConfig ────────────────────────────────────────────────────────────────

class TestSambaConfig:
    def test_from_dict(self):
        c = SambaConfig._from_dict(SAMBA_DATA)
        assert c.file_share_enabled is True
        assert c.print_share_enabled is True
        assert c.logon_enabled is False
        assert c.logon_user == "freebox"
        assert c.workgroup == "WORKGROUP"
        assert c.smbv2_enabled is True

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/netshare/samba/", json=api_ok(SAMBA_DATA))
        c = fb.netshare.samba()
        assert isinstance(c, SambaConfig)
        assert c.workgroup == "WORKGROUP"
        assert c.file_share_enabled is True

    def test_set(self, fb, httpx_mock):
        updated = {**SAMBA_DATA, "print_share_enabled": False}
        httpx_mock.add_response(url=f"{API}/netshare/samba/", method="PUT", json=api_ok(updated))
        c = fb.netshare.set_samba(print_share_enabled=False)
        assert isinstance(c, SambaConfig)
        assert c.print_share_enabled is False


# ── AfpConfig ──────────────────────────────────────────────────────────────────

class TestAfpConfig:
    def test_from_dict(self):
        c = AfpConfig._from_dict(AFP_DATA)
        assert c.enabled is False
        assert c.guest_allow is True
        assert c.login_name == "freebox"
        assert c.server_type == "airport"

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/netshare/afp/", json=api_ok(AFP_DATA))
        c = fb.netshare.afp()
        assert isinstance(c, AfpConfig)
        assert c.enabled is False
        assert c.server_type == "airport"

    def test_set(self, fb, httpx_mock):
        updated = {**AFP_DATA, "guest_allow": False}
        httpx_mock.add_response(url=f"{API}/netshare/afp/", method="PUT", json=api_ok(updated))
        c = fb.netshare.set_afp(guest_allow=False)
        assert isinstance(c, AfpConfig)
        assert c.guest_allow is False


# ── Property ───────────────────────────────────────────────────────────────────

class TestNetShareProperty:
    def test_property(self, fb):
        assert isinstance(fb.netshare, NetShare)
