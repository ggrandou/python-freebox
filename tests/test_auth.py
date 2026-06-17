import hashlib
import hmac
import stat

import pytest

from freebox.auth import Auth, AuthorizationStatus, _compute_password, raise_for_error_code
from freebox.exceptions import (
    AppsDenied,
    AuthenticationError,
    AuthorizationDenied,
    AuthorizationTimeout,
    DeniedFromExternalIP,
    FreeboxError,
    InsufficientRightsError,
    RateLimited,
    TokenRevoked,
)
from tests.conftest import APP_TOKEN, CHALLENGE, SESSION_TOKEN, TRACK_ID


# ── _compute_password ──────────────────────────────────────────────────────────

def test_compute_password():
    expected = hmac.new(APP_TOKEN.encode(), CHALLENGE.encode(), hashlib.sha1).hexdigest()
    assert _compute_password(APP_TOKEN, CHALLENGE) == expected


# ── raise_for_error_code ───────────────────────────────────────────────────────

@pytest.mark.parametrize("code,exc_class", [
    ("auth_required",           AuthenticationError),
    ("pending_token",           AuthenticationError),
    ("invalid_token",           TokenRevoked),
    ("insufficient_rights",     InsufficientRightsError),
    ("denied_from_external_ip", DeniedFromExternalIP),
    ("ratelimited",             RateLimited),
    ("new_apps_denied",         AppsDenied),
    ("apps_denied",             AppsDenied),
    ("unknown_code",            FreeboxError),
])
def test_raise_for_error_code(code, exc_class):
    with pytest.raises(exc_class) as exc_info:
        raise_for_error_code(code, "test message")
    assert exc_info.value.error_code == code


# ── Token persistence ──────────────────────────────────────────────────────────

class TestTokenPersistence:
    def test_load_token_no_file(self, auth):
        assert auth.load_token() is False
        assert auth.app_token is None

    def test_load_token_empty_file(self, auth):
        auth.token_file.write_text("   ")
        assert auth.load_token() is False
        assert auth.app_token is None

    def test_load_token_success(self, auth):
        auth.token_file.write_text(APP_TOKEN)
        assert auth.load_token() is True
        assert auth.app_token == APP_TOKEN

    def test_load_token_strips_whitespace(self, auth):
        auth.token_file.write_text(f"  {APP_TOKEN}\n")
        auth.load_token()
        assert auth.app_token == APP_TOKEN

    def test_save_token_writes_file(self, auth):
        auth.save_token(APP_TOKEN)
        assert auth.token_file.read_text() == APP_TOKEN

    def test_save_token_sets_permissions(self, auth):
        auth.save_token(APP_TOKEN)
        mode = auth.token_file.stat().st_mode & 0o777
        assert mode == 0o600

    def test_save_token_sets_attribute(self, auth):
        auth.save_token(APP_TOKEN)
        assert auth.app_token == APP_TOKEN

    def test_save_token_no_file(self, auth):
        auth.token_file = None
        auth.save_token(APP_TOKEN)  # should not raise
        assert auth.app_token == APP_TOKEN

    def test_clear_token_removes_file(self, auth):
        auth.token_file.write_text(APP_TOKEN)
        auth.app_token = APP_TOKEN
        auth.clear_token()
        assert not auth.token_file.exists()
        assert auth.app_token is None

    def test_clear_token_no_file(self, auth):
        auth.clear_token()  # should not raise when file is absent


# ── Registration ───────────────────────────────────────────────────────────────

class TestRegister:
    def _make_request(self, statuses: list[str]):
        """Return a fake request callable that cycles through authorization statuses."""
        status_iter = iter(statuses)

        def request(method, path, *, authenticated=False, json=None):
            if path == "login/authorize/":
                return {"track_id": TRACK_ID, "app_token": APP_TOKEN}
            if path == f"login/authorize/{TRACK_ID}":
                return {"status": next(status_iter)}
            raise AssertionError(f"Unexpected request: {method} {path}")

        return request

    def test_granted_immediately(self, auth):
        auth.register(self._make_request(["granted"]))
        assert auth.app_token == APP_TOKEN

    def test_pending_then_granted(self, auth, monkeypatch):
        monkeypatch.setattr("freebox.auth.time.sleep", lambda _: None)
        auth.register(self._make_request(["pending", "pending", "granted"]))
        assert auth.app_token == APP_TOKEN

    def test_denied(self, auth):
        with pytest.raises(AuthorizationDenied):
            auth.register(self._make_request(["denied"]))

    def test_timeout(self, auth):
        with pytest.raises(AuthorizationTimeout):
            auth.register(self._make_request(["timeout"]))

    def test_prompts_user(self, tmp_path):
        messages = []
        auth = Auth("id", "App", "1.0", "dev",
                    token_file=tmp_path / "tok",
                    on_pending=messages.append)
        auth.register(self._make_request(["granted"]))
        assert any("Freebox" in m for m in messages)

    def test_token_saved_to_file(self, auth):
        auth.register(self._make_request(["granted"]))
        assert auth.token_file.read_text() == APP_TOKEN


# ── Session ────────────────────────────────────────────────────────────────────

class TestSession:
    def _make_request(self, permissions=None):
        def request(method, path, *, authenticated=False, json=None):
            if method == "GET" and path == "login/":
                return {"logged_in": False, "challenge": CHALLENGE}
            if method == "POST" and path == "login/session/":
                assert json["password"] == _compute_password(APP_TOKEN, CHALLENGE)
                return {
                    "session_token": SESSION_TOKEN,
                    "permissions": permissions or {"settings": True, "downloader": True},
                }
            if method == "POST" and path == "login/logout/":
                return None
            raise AssertionError(f"Unexpected request: {method} {path}")

        return request

    def test_open_session(self, auth):
        auth.app_token = APP_TOKEN
        auth.open_session(self._make_request())
        assert auth.session_token == SESSION_TOKEN

    def test_open_session_stores_permissions(self, auth):
        auth.app_token = APP_TOKEN
        auth.open_session(self._make_request({"downloader": True}))
        assert auth.permissions == {"downloader": True}

    def test_close_session(self, auth):
        auth.app_token = APP_TOKEN
        auth.session_token = SESSION_TOKEN
        auth.permissions = {"settings": True}
        auth.close_session(self._make_request())
        assert auth.session_token is None
        assert auth.permissions == {}

    def test_close_session_noop_when_not_open(self, auth):
        calls = []
        auth.close_session(lambda *a, **kw: calls.append(a))
        assert calls == []
