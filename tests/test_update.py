import pytest

from freebox import Freebox, Update, UpdateStatus, UpgradeState
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


# ── UpgradeState ───────────────────────────────────────────────────────────────

class TestUpgradeState:
    def test_fields(self):
        s = UpgradeState._from_dict({
            "state": "downloading",
            "old_version": "4.2.8",
            "new_version": "4.3.0",
            "percent": 42,
            "error_string": "",
        })
        assert s.state == "downloading"
        assert s.old_version == "4.2.8"
        assert s.new_version == "4.3.0"
        assert s.percent == 42
        assert s.error_string == ""

    def test_defaults(self):
        s = UpgradeState._from_dict({})
        assert s.state == ""
        assert s.old_version == ""
        assert s.new_version == ""
        assert s.percent == 0
        assert s.error_string == ""

    def test_error_state(self):
        s = UpgradeState._from_dict({
            "state": "download_failed",
            "error_string": "network error",
        })
        assert s.state == "download_failed"
        assert s.error_string == "network error"


# ── UpdateStatus ───────────────────────────────────────────────────────────────

class TestUpdateStatus:
    def test_up_to_date(self):
        s = UpdateStatus._from_dict({"state": "up_to_date"})
        assert s.state == "up_to_date"
        assert s.upgrade_state is None

    def test_auto_up_to_date(self):
        s = UpdateStatus._from_dict({"state": "auto_up_to_date"})
        assert s.state == "auto_up_to_date"
        assert s.upgrade_state is None

    def test_upgrading_with_upgrade_state(self):
        s = UpdateStatus._from_dict({
            "state": "upgrading",
            "upgrade_state": {
                "state": "downloading",
                "old_version": "4.2.8",
                "new_version": "4.3.0",
                "percent": 75,
                "error_string": "",
            },
        })
        assert s.state == "upgrading"
        assert isinstance(s.upgrade_state, UpgradeState)
        assert s.upgrade_state.state == "downloading"
        assert s.upgrade_state.percent == 75

    def test_defaults(self):
        s = UpdateStatus._from_dict({})
        assert s.state == ""
        assert s.upgrade_state is None


# ── Update API ─────────────────────────────────────────────────────────────────

class TestUpdate:
    def test_status_up_to_date(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/update/",
            json=api_ok({"state": "up_to_date"}),
        )
        s = fb.update.status()
        assert isinstance(s, UpdateStatus)
        assert s.state == "up_to_date"
        assert s.upgrade_state is None

    def test_status_upgrading(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/update/",
            json=api_ok({
                "state": "upgrading",
                "upgrade_state": {
                    "state": "writing",
                    "old_version": "4.2.8",
                    "new_version": "4.3.0",
                    "percent": 100,
                    "error_string": "",
                },
            }),
        )
        s = fb.update.status()
        assert s.state == "upgrading"
        assert isinstance(s.upgrade_state, UpgradeState)
        assert s.upgrade_state.state == "writing"

    def test_update_property(self, fb):
        assert isinstance(fb.update, Update)
