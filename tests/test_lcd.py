"""Unit tests for the LCD screen API."""
import pytest

from freebox import Freebox, Lcd, LcdConfig
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

CONFIG_DATA = {
    "brightness": 100,
    "orientation": 0,
    "orientation_forced": False,
    "hide_wifi_key": False,
    "led_strip_enabled": True,
    "led_strip_brightness": 80,
    "led_strip_animation": "rainbow",
    "available_led_strip_animations": ["none", "rainbow", "pulse"],
    "hide_status_led": False,
    "screensaver": "disabled",
}

CONFIG_DATA_UPDATED = {**CONFIG_DATA, "brightness": 50, "orientation_forced": True, "orientation": 90}


# ── LcdConfig ──────────────────────────────────────────────────────────────────

class TestLcdConfig:
    def test_from_dict(self):
        c = LcdConfig._from_dict(CONFIG_DATA)
        assert c.brightness == 100
        assert c.orientation == 0
        assert c.orientation_forced is False
        assert c.hide_wifi_key is False
        assert c.led_strip_enabled is True
        assert c.led_strip_brightness == 80
        assert c.led_strip_animation == "rainbow"
        assert c.available_led_strip_animations == ["none", "rainbow", "pulse"]
        assert c.hide_status_led is False
        assert c.screensaver == "disabled"

    def test_from_dict_minimal(self):
        # Older Freebox models return fewer fields
        c = LcdConfig._from_dict({"brightness": 100, "orientation": 0, "orientation_forced": False})
        assert c.brightness == 100
        assert c.led_strip_enabled is False
        assert c.screensaver == ""
        assert c.available_led_strip_animations == []

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lcd/config/", json=api_ok(CONFIG_DATA))
        c = fb.lcd.config()
        assert isinstance(c, LcdConfig)
        assert c.brightness == 100
        assert c.led_strip_animation == "rainbow"

    def test_set(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lcd/config/", method="PUT", json=api_ok(CONFIG_DATA_UPDATED))
        c = fb.lcd.set_config(brightness=50, orientation_forced=True, orientation=90)
        assert isinstance(c, LcdConfig)
        assert c.brightness == 50
        assert c.orientation_forced is True
        assert c.orientation == 90


# ── Property ───────────────────────────────────────────────────────────────────

class TestLcdProperty:
    def test_property(self, fb):
        assert isinstance(fb.lcd, Lcd)
