import pytest

from freebox import Freebox
from freebox.exceptions import AuthenticationError, TokenRevoked
from tests.conftest import (
    APP_ID, APP_NAME, APP_TOKEN, APP_VERSION, CHALLENGE,
    DEVICE_NAME, DISCOVERY_DATA, SESSION_TOKEN, TRACK_ID,
    api_err, api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"


# ── Helpers ────────────────────────────────────────────────────────────────────

def add_discovery(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/api_version", json=DISCOVERY_DATA)


def add_login(httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/login/",
        json=api_ok({"logged_in": False, "challenge": CHALLENGE}),
    )


def add_session(httpx_mock, token=SESSION_TOKEN, permissions=None):
    httpx_mock.add_response(
        url=f"{API}/login/session/",
        method="POST",
        json=api_ok({
            "session_token": token,
            "permissions": permissions or {"settings": True},
        }),
    )


def add_logout(httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/login/logout/",
        method="POST",
        json=api_ok(),
    )


def make_freebox(token_file=None, on_pending=None) -> Freebox:
    return Freebox(
        app_id=APP_ID,
        app_name=APP_NAME,
        app_version=APP_VERSION,
        device_name=DEVICE_NAME,
        token_file=token_file,
        on_pending=on_pending or (lambda _: None),
    )


# ── open / close ───────────────────────────────────────────────────────────────

class TestOpen:
    def test_open_with_existing_token(self, httpx_mock, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text(APP_TOKEN)

        add_discovery(httpx_mock)
        add_login(httpx_mock)
        add_session(httpx_mock)

        fb = make_freebox(token_file=token_file)
        fb.open()

        assert fb.discovery.uid == "test-uid-1234"
        assert fb._auth.session_token == SESSION_TOKEN
        assert fb.permissions == {"settings": True}

    def test_open_registers_when_no_token(self, httpx_mock, tmp_path):
        token_file = tmp_path / "token"

        add_discovery(httpx_mock)
        httpx_mock.add_response(
            url=f"{API}/login/authorize/",
            method="POST",
            json=api_ok({"track_id": TRACK_ID, "app_token": APP_TOKEN}),
        )
        httpx_mock.add_response(
            url=f"{API}/login/authorize/{TRACK_ID}",
            json=api_ok({"status": "granted"}),
        )
        add_login(httpx_mock)
        add_session(httpx_mock)

        fb = make_freebox(token_file=token_file)
        fb.open()

        assert token_file.read_text() == APP_TOKEN
        assert fb._auth.session_token == SESSION_TOKEN

    def test_close_sends_logout(self, httpx_mock, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text(APP_TOKEN)

        add_discovery(httpx_mock)
        add_login(httpx_mock)
        add_session(httpx_mock)
        add_logout(httpx_mock)

        fb = make_freebox(token_file=token_file)
        fb.open()
        fb.close()

        assert fb._auth.session_token is None
        assert fb.permissions == {}

    def test_context_manager(self, httpx_mock, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text(APP_TOKEN)

        add_discovery(httpx_mock)
        add_login(httpx_mock)
        add_session(httpx_mock)
        add_logout(httpx_mock)

        with make_freebox(token_file=token_file) as fb:
            assert fb._auth.session_token == SESSION_TOKEN
        assert fb._auth.session_token is None


# ── HTTP methods ───────────────────────────────────────────────────────────────

class TestHttpMethods:
    @pytest.fixture(autouse=True)
    def opened_fb(self, httpx_mock, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text(APP_TOKEN)
        add_discovery(httpx_mock)
        add_login(httpx_mock)
        add_session(httpx_mock)
        self.fb = make_freebox(token_file=token_file)
        self.fb.open()

    def test_get(self, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/", json=api_ok({"state": "up"}))
        result = self.fb.get("connection/")
        assert result == {"state": "up"}

    def test_get_sends_auth_header(self, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/", json=api_ok({}))
        self.fb.get("connection/")
        request = httpx_mock.get_requests()[-1]
        assert request.headers["X-Fbx-App-Auth"] == SESSION_TOKEN

    def test_post(self, httpx_mock):
        httpx_mock.add_response(url=f"{API}/download/add/", method="POST", json=api_ok({"id": 1}))
        result = self.fb.post("download/add/", json={"url": "http://example.com/file"})
        assert result == {"id": 1}

    def test_put(self, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lan/config/", method="PUT", json=api_ok({"mode": "router"}))
        result = self.fb.put("lan/config/", json={"mode": "router"})
        assert result == {"mode": "router"}

    def test_delete(self, httpx_mock):
        httpx_mock.add_response(url=f"{API}/download/1/", method="DELETE", json=api_ok())
        result = self.fb.delete("download/1/")
        assert result is None


# ── Auto-recovery ──────────────────────────────────────────────────────────────

class TestAutoRecovery:
    @pytest.fixture(autouse=True)
    def opened_fb(self, httpx_mock, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text(APP_TOKEN)
        add_discovery(httpx_mock)
        add_login(httpx_mock)
        add_session(httpx_mock)
        self.fb = make_freebox(token_file=token_file)
        self.fb.open()
        self.httpx_mock = httpx_mock
        self.token_file = token_file

    def test_renews_session_on_auth_required(self):
        self.httpx_mock.add_response(
            url=f"{API}/system/",
            json=api_err("auth_required"),
        )
        add_login(self.httpx_mock)
        add_session(self.httpx_mock, token="new-session-token")
        self.httpx_mock.add_response(
            url=f"{API}/system/",
            json=api_ok({"firmware_version": "4.12.1"}),
        )

        result = self.fb.get("system/")
        assert result == {"firmware_version": "4.12.1"}
        assert self.fb._auth.session_token == "new-session-token"

    def test_reregisters_on_invalid_token(self):
        self.httpx_mock.add_response(
            url=f"{API}/system/",
            json=api_err("invalid_token"),
        )
        self.httpx_mock.add_response(
            url=f"{API}/login/authorize/",
            method="POST",
            json=api_ok({"track_id": TRACK_ID, "app_token": "new-app-token"}),
        )
        self.httpx_mock.add_response(
            url=f"{API}/login/authorize/{TRACK_ID}",
            json=api_ok({"status": "granted"}),
        )
        add_login(self.httpx_mock)
        add_session(self.httpx_mock, token="new-session-token")
        self.httpx_mock.add_response(
            url=f"{API}/system/",
            json=api_ok({"firmware_version": "4.12.1"}),
        )

        result = self.fb.get("system/")
        assert result == {"firmware_version": "4.12.1"}
        assert self.token_file.read_text() == "new-app-token"

    def test_does_not_retry_twice_on_auth_required(self):
        self.httpx_mock.add_response(
            url=f"{API}/system/",
            json=api_err("auth_required"),
        )
        add_login(self.httpx_mock)
        add_session(self.httpx_mock)
        self.httpx_mock.add_response(
            url=f"{API}/system/",
            json=api_err("auth_required"),
        )

        with pytest.raises(AuthenticationError):
            self.fb.get("system/")
