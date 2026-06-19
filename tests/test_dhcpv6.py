import json

import pytest

from freebox import Dhcpv6, Dhcpv6Config, Freebox
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


# ── Fixtures data ──────────────────────────────────────────────────────────────

DHCPV6_CONFIG_DATA = {
    "enabled": True,
    "use_custom_dns": False,
    "dns": ["2620:0:ccc::a", "2620:0:ccc::1"],
}


# ── Dhcpv6Config ───────────────────────────────────────────────────────────────

class TestDhcpv6Config:
    def test_config_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/dhcpv6/config/", json=api_ok(DHCPV6_CONFIG_DATA))
        c = fb.dhcpv6.config()
        assert isinstance(c, Dhcpv6Config)
        assert c.enabled is True
        assert c.use_custom_dns is False
        assert c.dns == ["2620:0:ccc::a", "2620:0:ccc::1"]

    def test_config_defaults(self):
        c = Dhcpv6Config._from_dict({})
        assert c.enabled is False
        assert c.use_custom_dns is False
        assert c.dns == []

    def test_set_config(self, fb, httpx_mock):
        updated = {**DHCPV6_CONFIG_DATA, "use_custom_dns": True}
        httpx_mock.add_response(
            url=f"{API}/dhcpv6/config/", method="PUT", json=api_ok(updated)
        )
        c = fb.dhcpv6.set_config(use_custom_dns=True)
        assert c.use_custom_dns is True
        req = httpx_mock.get_requests()[-1]
        assert json.loads(req.content) == {"use_custom_dns": True}

    def test_set_config_enabled(self, fb, httpx_mock):
        updated = {**DHCPV6_CONFIG_DATA, "enabled": False}
        httpx_mock.add_response(
            url=f"{API}/dhcpv6/config/", method="PUT", json=api_ok(updated)
        )
        c = fb.dhcpv6.set_config(enabled=False)
        assert c.enabled is False
        req = httpx_mock.get_requests()[-1]
        assert json.loads(req.content) == {"enabled": False}

    def test_dhcpv6_property(self, fb):
        assert isinstance(fb.dhcpv6, Dhcpv6)
