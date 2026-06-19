"""Unit tests for the LED strip API."""
import pytest

from freebox import Freebox, Ledstrip, LedstripPlanning, LedstripStatus
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

STATUS_DATA = {"use_planning": True, "next_change": 1651135474996}

PLANNING_DATA = {
    "use_planning": False,
    "planning_mode": "ledstrip_off",
    "resolution": 48,
    "mapping": [False] * (48 * 7),
}

PLANNING_ENABLED = {**PLANNING_DATA, "use_planning": True}


# ── LedstripStatus ─────────────────────────────────────────────────────────────

class TestLedstripStatus:
    def test_from_dict(self):
        s = LedstripStatus._from_dict(STATUS_DATA)
        assert s.use_planning is True
        assert s.next_change == 1651135474996

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/ledstrip/status", json=api_ok(STATUS_DATA))
        s = fb.ledstrip.status()
        assert isinstance(s, LedstripStatus)
        assert s.use_planning is True
        assert s.next_change == 1651135474996


# ── LedstripPlanning ───────────────────────────────────────────────────────────

class TestLedstripPlanning:
    def test_from_dict(self):
        p = LedstripPlanning._from_dict(PLANNING_DATA)
        assert p.use_planning is False
        assert p.planning_mode == "ledstrip_off"
        assert p.resolution == 48
        assert len(p.mapping) == 48 * 7
        assert all(v is False for v in p.mapping)

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/ledstrip/planning/", json=api_ok(PLANNING_DATA))
        p = fb.ledstrip.planning()
        assert isinstance(p, LedstripPlanning)
        assert p.resolution == 48
        assert len(p.mapping) == 48 * 7

    def test_set(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/ledstrip/planning", method="PUT", json=api_ok(PLANNING_ENABLED))
        p = fb.ledstrip.set_planning(use_planning=True)
        assert isinstance(p, LedstripPlanning)
        assert p.use_planning is True

    def test_empty_mapping(self):
        p = LedstripPlanning._from_dict({"use_planning": False, "planning_mode": "ledstrip_off", "resolution": 48})
        assert p.mapping == []


# ── Property ───────────────────────────────────────────────────────────────────

class TestLedstripProperty:
    def test_property(self, fb):
        assert isinstance(fb.ledstrip, Ledstrip)
