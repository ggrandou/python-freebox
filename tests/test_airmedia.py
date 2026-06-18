"""Unit tests for the AirMedia streaming API."""
import pytest

from freebox import AirMedia, AirMediaConfig, AirMediaReceiver, Freebox
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


# ── Test data ──────────────────────────────────────────────────────────────────

RECEIVER_PLAYER = {
    "name": "Freebox Player",
    "password_protected": True,
    "capabilities": {"photo": True, "audio": True, "video": True, "screen": False},
}

RECEIVER_SERVER = {
    "name": "Freebox Server",
    "password_protected": False,
    "capabilities": {"photo": False, "audio": True, "video": False, "screen": False},
}


# ── AirMediaConfig ─────────────────────────────────────────────────────────────

class TestAirMediaConfig:
    def test_from_dict(self):
        c = AirMediaConfig._from_dict({"enabled": True})
        assert c.enabled is True

    def test_from_dict_disabled(self):
        c = AirMediaConfig._from_dict({"enabled": False})
        assert c.enabled is False

    def test_defaults(self):
        c = AirMediaConfig._from_dict({})
        assert c.enabled is False


# ── AirMediaReceiver ───────────────────────────────────────────────────────────

class TestAirMediaReceiver:
    def test_from_dict(self):
        r = AirMediaReceiver._from_dict(RECEIVER_PLAYER)
        assert r.name == "Freebox Player"
        assert r.password_protected is True
        assert r.capabilities["video"] is True
        assert r.capabilities["screen"] is False

    def test_no_capabilities(self):
        r = AirMediaReceiver._from_dict({"name": "Test", "password_protected": False})
        assert r.capabilities == {}

    def test_null_capabilities(self):
        r = AirMediaReceiver._from_dict(
            {"name": "Test", "password_protected": False, "capabilities": None}
        )
        assert r.capabilities == {}

    def test_defaults(self):
        r = AirMediaReceiver._from_dict({})
        assert r.name == ""
        assert r.password_protected is False


# ── AirMedia API ───────────────────────────────────────────────────────────────

class TestAirMediaApi:
    def test_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/airmedia/config/", json=api_ok({"enabled": True})
        )
        c = fb.airmedia.config()
        assert isinstance(c, AirMediaConfig)
        assert c.enabled is True

    def test_set_config_enabled(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/airmedia/config/", method="PUT",
            json=api_ok({"enabled": True}),
        )
        c = fb.airmedia.set_config(enabled=True)
        assert c.enabled is True

    def test_set_config_with_password(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/airmedia/config/", method="PUT",
            json=api_ok({"enabled": True}),
        )
        c = fb.airmedia.set_config(enabled=True, password="3615")
        assert c.enabled is True

    def test_receivers(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/airmedia/receivers/",
            json=api_ok([RECEIVER_PLAYER, RECEIVER_SERVER]),
        )
        receivers = fb.airmedia.receivers()
        assert len(receivers) == 2
        assert all(isinstance(r, AirMediaReceiver) for r in receivers)
        assert receivers[0].name == "Freebox Player"
        assert receivers[1].name == "Freebox Server"

    def test_receivers_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/airmedia/receivers/", json=api_ok([]))
        assert fb.airmedia.receivers() == []

    def test_receivers_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/airmedia/receivers/", json=api_ok(None))
        assert fb.airmedia.receivers() == []

    def test_send_start_video(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/airmedia/receivers/Freebox%20Player/",
            method="POST",
            json=api_ok(None),
        )
        fb.airmedia.send(
            "Freebox%20Player",
            action="start",
            media_type="video",
            media="http://example.com/movie.mp4",
        )

    def test_send_stop(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/airmedia/receivers/Freebox%20Player/",
            method="POST",
            json=api_ok(None),
        )
        fb.airmedia.send("Freebox%20Player", action="stop")

    def test_send_photo_with_password(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/airmedia/receivers/Freebox%20Player/",
            method="POST",
            json=api_ok(None),
        )
        fb.airmedia.send(
            "Freebox%20Player",
            action="start",
            media_type="photo",
            media="L0Rpc3F1ZSBkdXI=",
            password="1111",
        )


# ── Property ───────────────────────────────────────────────────────────────────

class TestAirMediaProperty:
    def test_property(self, fb):
        assert isinstance(fb.airmedia, AirMedia)
