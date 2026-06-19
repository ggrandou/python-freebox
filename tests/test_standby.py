"""Unit tests for the Standby API."""
import pytest

from freebox import Freebox, Standby, StandbyConfig, StandbyStatus
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


class TestStandbyStatusDataclass:
    def test_from_dict(self):
        status = StandbyStatus._from_dict({
            "use_planning": True,
            "planning_mode": "standby",
            "next_change": 1651135474996,
            "available_planning_modes": ["wifi_off", "standby"],
        })
        assert status.use_planning is True
        assert status.planning_mode == "standby"
        assert status.next_change == 1651135474996
        assert status.available_planning_modes == ["wifi_off", "standby"]

    def test_defaults(self):
        status = StandbyStatus._from_dict({})
        assert status.use_planning is False
        assert status.planning_mode == ""
        assert status.next_change == 0
        assert status.available_planning_modes == []

    def test_null_modes(self):
        status = StandbyStatus._from_dict({"available_planning_modes": None})
        assert status.available_planning_modes == []


class TestStandbyConfigDataclass:
    def test_from_dict(self):
        mapping = [False] * 48 * 7
        cfg = StandbyConfig._from_dict({
            "use_planning": False,
            "planning_mode": "suspend",
            "mapping": mapping,
            "resolution": 48,
        })
        assert cfg.use_planning is False
        assert cfg.planning_mode == "suspend"
        assert cfg.resolution == 48
        assert len(cfg.mapping) == 48 * 7

    def test_defaults(self):
        cfg = StandbyConfig._from_dict({})
        assert cfg.use_planning is False
        assert cfg.resolution == 0
        assert cfg.mapping == []


class TestStandbyApi:
    def test_status(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/standby/status",
            json=api_ok({
                "use_planning": True,
                "planning_mode": "standby",
                "next_change": 1651135474996,
                "available_planning_modes": ["wifi_off", "standby"],
            }),
        )
        status = fb.standby.status()
        assert isinstance(status, StandbyStatus)
        assert status.planning_mode == "standby"

    def test_config(self, fb, httpx_mock):
        mapping = [False] * 48 * 7
        httpx_mock.add_response(
            url=f"{API}/standby/config/",
            json=api_ok({
                "use_planning": False,
                "planning_mode": "suspend",
                "mapping": mapping,
                "resolution": 48,
            }),
        )
        cfg = fb.standby.config()
        assert isinstance(cfg, StandbyConfig)
        assert cfg.resolution == 48

    def test_set_config(self, fb, httpx_mock):
        mapping = [False] * 48 * 7
        httpx_mock.add_response(
            url=f"{API}/standby/config",
            method="PUT",
            json=api_ok({
                "use_planning": True,
                "planning_mode": "standby",
                "mapping": mapping,
                "resolution": 48,
            }),
        )
        cfg = fb.standby.set_config(use_planning=True, planning_mode="standby")
        assert cfg.use_planning is True

    def test_property(self, fb):
        assert isinstance(fb.standby, Standby)
