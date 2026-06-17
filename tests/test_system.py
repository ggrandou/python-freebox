import pytest

from freebox import Freebox, System, SystemConfig, SystemExpansion, SystemFan, SystemModelInfo, SystemSensor
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


# ── Fixture data ───────────────────────────────────────────────────────────────

SYSTEM_CONFIG_DATA = {
    "mac": "34:27:92:60:0B:9E",
    "serial": "957601J183400107",
    "firmware_version": "6.6.6",
    "uptime": "2 heures 11 minutes 32 secondes",
    "uptime_val": 7892,
    "board_name": "fbxgw7r",
    "box_authenticated": True,
    "disk_status": "active",
    "usb3_enable": True,
    "user_main_storage": "Disque 1",
    "user_storage_powered": True,
    "sensors": [
        {"id": "t1", "name": "Température 1", "value": 45},
        {"id": "cpu_ap", "name": "Température CPU", "value": 64},
    ],
    "fans": [
        {"id": "main", "name": "Ventilateur 1", "value": 1739},
    ],
    "expansions": [
        {
            "type": "ftth_p2p",
            "present": True,
            "slot": 2,
            "probe_done": True,
            "supported": True,
            "bundle": "959300V181500003",
        }
    ],
    "model_info": {
        "name": "fbxgw7-r1/full",
        "pretty_name": "Freebox v7 (r1)",
        "has_expansions": True,
        "has_lan_sfp": True,
        "has_dect": True,
        "has_home_automation": True,
        "has_femtocell_exp": False,
        "has_fixed_femtocell": False,
        "has_vm": True,
        "has_dsl": False,
        "has_standby": False,
        "has_eco_wifi": False,
        "has_wop": False,
        "has_led_strip": False,
        "has_status_led": True,
        "has_usb3_enable": True,
        "has_lcd_screensaver": False,
    },
}


# ── SystemSensor ───────────────────────────────────────────────────────────────

class TestSystemSensor:
    def test_fields(self):
        s = SystemSensor._from_dict({"id": "t1", "name": "Température 1", "value": 45})
        assert s.id == "t1"
        assert s.name == "Température 1"
        assert s.value == 45

    def test_defaults(self):
        s = SystemSensor._from_dict({})
        assert s.id == ""
        assert s.name == ""
        assert s.value == 0


# ── SystemFan ──────────────────────────────────────────────────────────────────

class TestSystemFan:
    def test_fields(self):
        f = SystemFan._from_dict({"id": "main", "name": "Ventilateur 1", "value": 1739})
        assert f.id == "main"
        assert f.name == "Ventilateur 1"
        assert f.value == 1739

    def test_defaults(self):
        f = SystemFan._from_dict({})
        assert f.id == ""
        assert f.value == 0


# ── SystemExpansion ────────────────────────────────────────────────────────────

class TestSystemExpansion:
    def test_fields(self):
        e = SystemExpansion._from_dict({
            "slot": 2, "probe_done": True, "present": True,
            "supported": True, "type": "ftth_p2p", "bundle": "959300V181500003",
        })
        assert e.slot == 2
        assert e.present is True
        assert e.type == "ftth_p2p"
        assert e.bundle == "959300V181500003"

    def test_defaults(self):
        e = SystemExpansion._from_dict({})
        assert e.slot == 0
        assert e.present is False
        assert e.type == ""


# ── SystemModelInfo ────────────────────────────────────────────────────────────

class TestSystemModelInfo:
    def test_fields(self):
        m = SystemModelInfo._from_dict(SYSTEM_CONFIG_DATA["model_info"])
        assert m.name == "fbxgw7-r1/full"
        assert m.pretty_name == "Freebox v7 (r1)"
        assert m.has_expansions is True
        assert m.has_lan_sfp is True
        assert m.has_vm is True

    def test_defaults(self):
        m = SystemModelInfo._from_dict({})
        assert m.name == ""
        assert m.has_expansions is False
        assert m.has_lan_sfp is False


# ── SystemConfig ───────────────────────────────────────────────────────────────

class TestSystemConfig:
    def test_config_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/system/", json=api_ok(SYSTEM_CONFIG_DATA))
        c = fb.system.config()
        assert isinstance(c, SystemConfig)
        assert c.firmware_version == "6.6.6"
        assert c.mac == "34:27:92:60:0B:9E"
        assert c.serial == "957601J183400107"
        assert c.uptime_val == 7892
        assert c.board_name == "fbxgw7r"
        assert c.box_authenticated is True
        assert c.disk_status == "active"
        assert c.usb3_enable is True
        assert c.user_main_storage == "Disque 1"
        assert c.user_storage_powered is True

    def test_config_sensors(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/system/", json=api_ok(SYSTEM_CONFIG_DATA))
        c = fb.system.config()
        assert len(c.sensors) == 2
        assert c.sensors[0].id == "t1"
        assert c.sensors[1].value == 64

    def test_config_fans(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/system/", json=api_ok(SYSTEM_CONFIG_DATA))
        c = fb.system.config()
        assert len(c.fans) == 1
        assert c.fans[0].value == 1739

    def test_config_expansions(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/system/", json=api_ok(SYSTEM_CONFIG_DATA))
        c = fb.system.config()
        assert len(c.expansions) == 1
        assert c.expansions[0].type == "ftth_p2p"
        assert c.expansions[0].bundle == "959300V181500003"

    def test_config_model_info(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/system/", json=api_ok(SYSTEM_CONFIG_DATA))
        c = fb.system.config()
        assert isinstance(c.model_info, SystemModelInfo)
        assert c.model_info.name == "fbxgw7-r1/full"
        assert c.model_info.has_lan_sfp is True

    def test_config_no_model_info(self):
        c = SystemConfig._from_dict({})
        assert c.model_info is None
        assert c.sensors == []
        assert c.fans == []
        assert c.expansions == []

    def test_reboot(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/system/reboot/", method="POST", json={"success": True})
        fb.system.reboot()
        req = httpx_mock.get_requests()[-1]
        assert req.method == "POST"

    def test_shutdown(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/system/shutdown/", method="POST", json={"success": True})
        fb.system.shutdown()
        req = httpx_mock.get_requests()[-1]
        assert req.method == "POST"

    def test_system_property(self, fb):
        assert isinstance(fb.system, System)
