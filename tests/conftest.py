import pytest

from freebox.auth import Auth
from freebox.discovery import DiscoveryInfo

# ── Shared constants ───────────────────────────────────────────────────────────

APP_ID      = "fr.freebox.test"
APP_NAME    = "Test App"
APP_VERSION = "0.1"
DEVICE_NAME = "test-device"

APP_TOKEN     = "app-token-abc123"
SESSION_TOKEN = "session-token-xyz789"
CHALLENGE     = "challenge-string"
TRACK_ID      = 42

DISCOVERY_DATA = {
    "uid":            "test-uid-1234",
    "device_name":    "Freebox Server",
    "box_model":      "fbxgw8-r1/full",
    "box_model_name": "Freebox v8 (r1)",
    "api_version":    "16.0",
    "api_base_url":   "/api/",
    "api_domain":     "test.fbxos.fr",
    "https_available": True,
    "https_port":     3615,
}

# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def discovery_info() -> DiscoveryInfo:
    return DiscoveryInfo._from_dict(DISCOVERY_DATA)


@pytest.fixture
def auth(tmp_path) -> Auth:
    return Auth(
        app_id=APP_ID,
        app_name=APP_NAME,
        app_version=APP_VERSION,
        device_name=DEVICE_NAME,
        token_file=tmp_path / "token",
        on_pending=lambda msg: None,  # suppress output
    )


def api_ok(result=None):
    """Build a successful API response body."""
    return {"success": True, "result": result}


def api_err(code, msg="error"):
    """Build a failed API response body."""
    return {"success": False, "error_code": code, "msg": msg}
