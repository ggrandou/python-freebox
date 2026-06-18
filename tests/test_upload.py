"""Unit tests for the File Upload API."""
import pytest

from freebox import Freebox, Upload, UploadTask
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

UPLOAD_DATA = {
    "id": 1678139709,
    "size": 54960,
    "uploaded": 54960,
    "status": "done",
    "last_update": 1361465608,
    "start_date": 1361465608,
    "upload_name": "playlist.m3u",
    "dirname": "/Disque 1",
}


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
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token_file=token_file,
        on_pending=lambda _: None,
    )
    client.open()
    return client


class TestUploadTaskDataclass:
    def test_from_dict(self):
        t = UploadTask._from_dict(UPLOAD_DATA)
        assert t.id == 1678139709
        assert t.size == 54960
        assert t.uploaded == 54960
        assert t.status == "done"
        assert t.upload_name == "playlist.m3u"
        assert t.dirname == "/Disque 1"

    def test_defaults(self):
        t = UploadTask._from_dict({})
        assert t.id == 0
        assert t.status == ""


class TestUploadApi:
    def test_ws_url(self, fb):
        url = fb.upload.ws_url()
        assert "ws/upload" in url
        assert url.startswith("wss://")

    def test_tasks(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/upload/", json=api_ok([UPLOAD_DATA]))
        tasks = fb.upload.tasks()
        assert len(tasks) == 1
        assert isinstance(tasks[0], UploadTask)
        assert tasks[0].id == 1678139709

    def test_tasks_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/upload/", json=api_ok([]))
        assert fb.upload.tasks() == []

    def test_tasks_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/upload/", json=api_ok(None))
        assert fb.upload.tasks() == []

    def test_task(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/upload/1678139709",
            json=api_ok(UPLOAD_DATA),
        )
        t = fb.upload.task(1678139709)
        assert t.id == 1678139709

    def test_cancel(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/upload/1678139709/cancel",
            method="DELETE",
            json=api_ok(None),
        )
        fb.upload.cancel(1678139709)

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/upload/1678139709",
            method="DELETE",
            json=api_ok(None),
        )
        fb.upload.delete(1678139709)

    def test_property(self, fb):
        assert isinstance(fb.upload, Upload)
