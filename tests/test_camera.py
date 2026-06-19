"""Unit tests for the Camera API."""
import pytest

from freebox import Camera, Cameras, Freebox
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

CAM_DATA = {
    "id": "012345678901",
    "node_id": 0,
    "name": "Caméra du salon",
    "stream_url": "/camera/stream/012345678901/stream.m3u8",
    "lan_gid": "ether-3c:98:72:fa:36:15",
}


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


class TestCameraDataclass:
    def test_from_dict(self):
        c = Camera._from_dict(CAM_DATA)
        assert c.id == "012345678901"
        assert c.node_id == 0
        assert c.name == "Caméra du salon"
        assert c.stream_url == "/camera/stream/012345678901/stream.m3u8"
        assert c.lan_gid == "ether-3c:98:72:fa:36:15"

    def test_defaults(self):
        c = Camera._from_dict({})
        assert c.id == ""
        assert c.node_id == 0
        assert c.name == ""


class TestCameraApi:
    def test_cameras(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/camera/",
            json=api_ok([CAM_DATA]),
        )
        cams = fb.camera.cameras()
        assert len(cams) == 1
        assert isinstance(cams[0], Camera)
        assert cams[0].id == "012345678901"

    def test_cameras_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/camera/", json=api_ok([]))
        assert fb.camera.cameras() == []

    def test_cameras_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/camera/", json=api_ok(None))
        assert fb.camera.cameras() == []

    def test_camera(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/camera/012345678901",
            json=api_ok(CAM_DATA),
        )
        c = fb.camera.camera("012345678901")
        assert c.id == "012345678901"

    def test_property(self, fb):
        assert isinstance(fb.camera, Cameras)
