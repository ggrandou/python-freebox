"""Unit tests for the Profile Management API."""
import pytest

from freebox import Freebox, Profile, Profiles
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

PROFILE_DATA = {
    "id": 2,
    "name": "r0ro",
    "url": "/resources/images/profile/profile_04.png",
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


class TestProfileDataclass:
    def test_from_dict(self):
        p = Profile._from_dict(PROFILE_DATA)
        assert p.id == 2
        assert p.name == "r0ro"
        assert p.url == "/resources/images/profile/profile_04.png"

    def test_defaults(self):
        p = Profile._from_dict({})
        assert p.id == 0
        assert p.name == ""
        assert p.url == ""


class TestProfilesApi:
    def test_profiles(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/profile",
            json=api_ok([PROFILE_DATA]),
        )
        profiles = fb.profile.profiles()
        assert len(profiles) == 1
        assert isinstance(profiles[0], Profile)
        assert profiles[0].id == 2

    def test_profiles_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/profile", json=api_ok([]))
        assert fb.profile.profiles() == []

    def test_profiles_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/profile", json=api_ok(None))
        assert fb.profile.profiles() == []

    def test_profile(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/profile/2",
            json=api_ok(PROFILE_DATA),
        )
        p = fb.profile.profile(2)
        assert p.id == 2
        assert p.name == "r0ro"

    def test_create(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/profile/",
            method="POST",
            json=api_ok({"id": 3, "name": "Pierrot", "url": "/resources/images/profile/profile_04.png"}),
        )
        p = fb.profile.create(name="Pierrot")
        assert p.id == 3
        assert p.name == "Pierrot"

    def test_update(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/profile/3",
            method="PUT",
            json=api_ok({"id": 3, "name": "Pierrot updated", "url": "/resources/images/profile/profile_02.png"}),
        )
        p = fb.profile.update(3, name="Pierrot updated")
        assert p.name == "Pierrot updated"

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/profile/2",
            method="DELETE",
            json=api_ok(None),
        )
        fb.profile.delete(2)

    def test_property(self, fb):
        assert isinstance(fb.profile, Profiles)
