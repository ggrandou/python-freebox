import pytest

from freebox import Freebox, Notif, NotificationTarget
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"

TARGET_1 = {
    "id": "11111111-2222-3333-4444-555555555555",
    "name": "iPhone de Xavier",
    "type": "ios",
    "last_use": 0,
    "api_url": "https://monserver.example.com/mon_app",
    "message_type": "notification",
    "subscriptions": ["security", "phone"],
}

TARGET_2 = {
    "id": "22222222-1111-3333-4444-555555555555",
    "name": "mamy",
    "type": "android",
    "last_use": 1234567890,
    "api_url": "https://monserver.example.com/mon_app",
    "message_type": "data",
    "subscriptions": ["phone"],
}


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


# ── NotificationTarget dataclass ───────────────────────────────────────────────

class TestNotificationTarget:
    def test_from_dict_full(self):
        t = NotificationTarget._from_dict(TARGET_1)
        assert t.id == "11111111-2222-3333-4444-555555555555"
        assert t.name == "iPhone de Xavier"
        assert t.type == "ios"
        assert t.last_use == 0
        assert t.api_url == "https://monserver.example.com/mon_app"
        assert t.message_type == "notification"
        assert t.subscriptions == ["security", "phone"]

    def test_from_dict_defaults(self):
        t = NotificationTarget._from_dict({})
        assert t.id is None
        assert t.name == ""
        assert t.type == ""
        assert t.last_use == 0
        assert t.api_url == ""
        assert t.message_type == ""
        assert t.subscriptions == []

    def test_from_dict_no_id(self):
        """v16 API does not return an id field."""
        d = {k: v for k, v in TARGET_1.items() if k != "id"}
        t = NotificationTarget._from_dict(d)
        assert t.id is None
        assert t.name == "iPhone de Xavier"

    def test_from_dict_data_message_type(self):
        t = NotificationTarget._from_dict(TARGET_2)
        assert t.type == "android"
        assert t.message_type == "data"
        assert t.last_use == 1234567890


# ── Notif API ─────────────────────────────────────────────────────────────────

class TestNotif:
    def test_notif_property(self, fb):
        assert isinstance(fb.notif, Notif)

    def test_get_targets(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/notif/targets",
            json=api_ok([TARGET_1, TARGET_2]),
        )
        targets = fb.notif.get_targets()
        assert len(targets) == 2
        assert isinstance(targets[0], NotificationTarget)
        assert targets[0].id == TARGET_1["id"]
        assert targets[1].type == "android"

    def test_get_targets_empty(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/notif/targets",
            json=api_ok([]),
        )
        assert fb.notif.get_targets() == []

    def test_get_target(self, fb, httpx_mock):
        tid = TARGET_1["id"]
        httpx_mock.add_response(
            url=f"{API}/notif/targets/{tid}",
            json=api_ok([TARGET_1]),
        )
        t = fb.notif.get_target(tid)
        assert isinstance(t, NotificationTarget)
        assert t.id == tid
        assert t.name == "iPhone de Xavier"

    def test_get_target_single_object(self, fb, httpx_mock):
        tid = TARGET_1["id"]
        httpx_mock.add_response(
            url=f"{API}/notif/targets/{tid}",
            json=api_ok(TARGET_1),
        )
        t = fb.notif.get_target(tid)
        assert t.id == tid

    def test_create_target(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/notif/targets/",
            method="POST",
            json=api_ok(None),
        )
        fb.notif.create_target(
            name="My Phone",
            type="ios",
            token="tok123",
            api_url="https://example.com/notif",
            message_type="notification",
            subscriptions=["download", "phone"],
        )

    def test_create_target_minimal(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/notif/targets/",
            method="POST",
            json=api_ok(None),
        )
        fb.notif.create_target(
            name="Test",
            type="firebase",
            token="tok456",
            api_url="https://example.com/notif",
        )

    def test_update_target(self, fb, httpx_mock):
        tid = TARGET_2["id"]
        httpx_mock.add_response(
            url=f"{API}/notif/targets/{tid}",
            method="PUT",
            json=api_ok(None),
        )
        fb.notif.update_target(
            tid,
            name="mamy updated",
            subscriptions=["phone", "download"],
        )

    def test_update_target_all_fields(self, fb, httpx_mock):
        tid = TARGET_1["id"]
        httpx_mock.add_response(
            url=f"{API}/notif/targets/{tid}",
            method="PUT",
            json=api_ok(None),
        )
        fb.notif.update_target(
            tid,
            name="New Name",
            type="android",
            token="new-token",
            api_url="https://newurl.example.com",
            message_type="data",
            subscriptions=["security"],
        )

    def test_delete_target(self, fb, httpx_mock):
        tid = TARGET_2["id"]
        httpx_mock.add_response(
            url=f"{API}/notif/targets/{tid}",
            method="DELETE",
            json=api_ok(None),
        )
        fb.notif.delete_target(tid)
