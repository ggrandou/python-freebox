"""Unit tests for the Network Control (parental filter) API."""
import pytest

from freebox import Freebox, NetControl, NetworkControl, NetworkControlRule
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

NC_DATA = {
    "profile_id": 5,
    "current_mode": "allowed",
    "rule_mode": "allowed",
    "override": False,
    "override_mode": "denied",
    "override_until": 0,
    "next_change": 0,
    "macs": ["D8:A2:CA:FE:BA:DF", "D0:23:BE:DE:AD:EF"],
    "resolution": 288,
    "cdayranges": [],
}

NC_DATA_2 = {**NC_DATA, "profile_id": 3, "current_mode": "denied", "override": True}

RULE_DATA = {
    "id": 1,
    "profile_id": 5,
    "name": "School hours",
    "mode": "denied",
    "start_time": 28800,
    "end_time": 54000,
    "weekdays": [True, True, True, True, True, False, False, False],
    "enabled": True,
}

MIGRATE_DATA = {"default_mode_migrated": False}
MIGRATE_DONE = {"default_mode_migrated": True}


# ── NetworkControl ─────────────────────────────────────────────────────────────

class TestNetworkControl:
    def test_from_dict(self):
        nc = NetworkControl._from_dict(NC_DATA)
        assert nc.profile_id == 5
        assert nc.current_mode == "allowed"
        assert nc.rule_mode == "allowed"
        assert nc.override is False
        assert nc.override_mode == "denied"
        assert nc.override_until == 0
        assert nc.next_change == 0
        assert nc.macs == ["D8:A2:CA:FE:BA:DF", "D0:23:BE:DE:AD:EF"]
        assert nc.resolution == 288
        assert nc.cdayranges == []

    def test_controls(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/network_control", json=api_ok([NC_DATA, NC_DATA_2]))
        controls = fb.netcontrol.controls()
        assert len(controls) == 2
        assert all(isinstance(c, NetworkControl) for c in controls)
        assert controls[0].profile_id == 5
        assert controls[1].profile_id == 3

    def test_controls_null(self, fb, httpx_mock):
        # Real Freebox returns null when no profiles are configured
        httpx_mock.add_response(url=f"{API}/network_control", json=api_ok(None))
        assert fb.netcontrol.controls() == []

    def test_control(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/network_control/5", json=api_ok(NC_DATA))
        nc = fb.netcontrol.control(5)
        assert isinstance(nc, NetworkControl)
        assert nc.profile_id == 5
        assert nc.current_mode == "allowed"

    def test_set_control(self, fb, httpx_mock):
        updated = {**NC_DATA, "override": True, "override_mode": "denied"}
        httpx_mock.add_response(url=f"{API}/network_control/5", method="PUT", json=api_ok(updated))
        nc = fb.netcontrol.set_control(5, override=True, override_mode="denied")
        assert isinstance(nc, NetworkControl)
        assert nc.override is True
        assert nc.override_mode == "denied"


# ── Migration ──────────────────────────────────────────────────────────────────

class TestMigration:
    def test_migration_status_false(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/network_control/migrate", json=api_ok(MIGRATE_DATA))
        assert fb.netcontrol.migration_status() is False

    def test_migrate(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/network_control/migrate", method="POST", json=api_ok(MIGRATE_DONE)
        )
        assert fb.netcontrol.migrate() is True


# ── NetworkControlRule ─────────────────────────────────────────────────────────

class TestNetworkControlRule:
    def test_from_dict(self):
        r = NetworkControlRule._from_dict(RULE_DATA)
        assert r.id == 1
        assert r.profile_id == 5
        assert r.name == "School hours"
        assert r.mode == "denied"
        assert r.start_time == 28800
        assert r.end_time == 54000
        assert r.weekdays == [True, True, True, True, True, False, False, False]
        assert r.enabled is True

    def test_rules(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/network_control/5/rules", json=api_ok([RULE_DATA]))
        rules = fb.netcontrol.rules(5)
        assert len(rules) == 1
        assert isinstance(rules[0], NetworkControlRule)
        assert rules[0].id == 1

    def test_rule(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/network_control/5/rules/1", json=api_ok(RULE_DATA))
        r = fb.netcontrol.rule(5, 1)
        assert isinstance(r, NetworkControlRule)
        assert r.id == 1

    def test_add_rule(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/network_control/5/rules/", method="POST", json=api_ok(RULE_DATA)
        )
        r = fb.netcontrol.add_rule(5, mode="denied", name="School hours",
                                   start_time=28800, end_time=54000)
        assert isinstance(r, NetworkControlRule)
        assert r.mode == "denied"

    def test_set_rule(self, fb, httpx_mock):
        updated = {**RULE_DATA, "enabled": False}
        httpx_mock.add_response(
            url=f"{API}/network_control/5/rules/1", method="PUT", json=api_ok(updated)
        )
        r = fb.netcontrol.set_rule(5, 1, enabled=False)
        assert isinstance(r, NetworkControlRule)
        assert r.enabled is False

    def test_delete_rule(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/network_control/5/rules/1", method="DELETE", json=api_ok(None)
        )
        fb.netcontrol.delete_rule(5, 1)


# ── Property ───────────────────────────────────────────────────────────────────

class TestNetControlProperty:
    def test_property(self, fb):
        assert isinstance(fb.netcontrol, NetControl)
