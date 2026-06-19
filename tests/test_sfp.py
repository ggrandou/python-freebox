import json

import pytest

from freebox import Freebox, Sfp, SfpConfig, SfpStatus
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


# ── Fixture data ───────────────────────────────────────────────────────────────

SFP_STATUS_DATA = {
    "type": "copper_1g",
    "present": True,
    "link": True,
    "supported": True,
    "vendor_name": "SFP Vendor",
    "serial_number": "1122334455",
    "part_number": "SFP-V-Part-01R",
    "power_good": True,
    "hardware_rev": "A",
    "eeprom_valid": True,
}

SFP_CONFIG_DATA = {
    "sfp_type_forced": False,
    "sfp_type_forced_value": "",
    "available_sfp_types": ["p2p_1g", "p2p_10g", "copper_1g", "copper_sgmii_1g"],
}


# ── SfpStatus ──────────────────────────────────────────────────────────────────

class TestSfpStatus:
    def test_status_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/sfp/status", json=api_ok(SFP_STATUS_DATA))
        s = fb.sfp.status()
        assert isinstance(s, SfpStatus)
        assert s.present is True
        assert s.type == "copper_1g"
        assert s.link is True
        assert s.supported is True
        assert s.vendor_name == "SFP Vendor"
        assert s.serial_number == "1122334455"
        assert s.part_number == "SFP-V-Part-01R"
        assert s.power_good is True
        assert s.hardware_rev == "A"
        assert s.eeprom_valid is True

    def test_status_defaults(self):
        s = SfpStatus._from_dict({})
        assert s.present is False
        assert s.eeprom_valid is False
        assert s.supported is False
        assert s.type == ""
        assert s.power_good is False
        assert s.link is False
        assert s.vendor_name == ""
        assert s.part_number == ""
        assert s.hardware_rev == ""
        assert s.serial_number == ""


# ── SfpConfig ──────────────────────────────────────────────────────────────────

class TestSfpConfig:
    def test_config_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/sfp/config/", json=api_ok(SFP_CONFIG_DATA))
        c = fb.sfp.config()
        assert isinstance(c, SfpConfig)
        assert c.sfp_type_forced is False
        assert c.sfp_type_forced_value == ""
        assert c.available_sfp_types == ["p2p_1g", "p2p_10g", "copper_1g", "copper_sgmii_1g"]

    def test_config_defaults(self):
        c = SfpConfig._from_dict({})
        assert c.sfp_type_forced is False
        assert c.sfp_type_forced_value == ""
        assert c.available_sfp_types == []

    def test_set_config(self, fb, httpx_mock):
        updated = {**SFP_CONFIG_DATA, "sfp_type_forced": True, "sfp_type_forced_value": "copper_1g"}
        httpx_mock.add_response(
            url=f"{API}/sfp/config/", method="PUT", json=api_ok(updated)
        )
        c = fb.sfp.set_config(sfp_type_forced=True, sfp_type_forced_value="copper_1g")
        assert c.sfp_type_forced is True
        assert c.sfp_type_forced_value == "copper_1g"
        req = httpx_mock.get_requests()[-1]
        assert json.loads(req.content) == {
            "sfp_type_forced": True,
            "sfp_type_forced_value": "copper_1g",
        }

    def test_set_config_disable_force(self, fb, httpx_mock):
        updated = {**SFP_CONFIG_DATA, "sfp_type_forced": False, "sfp_type_forced_value": ""}
        httpx_mock.add_response(
            url=f"{API}/sfp/config/", method="PUT", json=api_ok(updated)
        )
        c = fb.sfp.set_config(sfp_type_forced=False)
        assert c.sfp_type_forced is False
        req = httpx_mock.get_requests()[-1]
        assert json.loads(req.content) == {"sfp_type_forced": False}

    def test_sfp_property(self, fb):
        assert isinstance(fb.sfp, Sfp)
