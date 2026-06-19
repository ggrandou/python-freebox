"""Unit tests for the Player API."""
import pytest

from freebox import (
    Freebox,
    Player,
    PlayerStatus,
    PlayerStatusCapabilities,
    PlayerStatusForegroundApp,
    PlayerStatusInformations,
    PlayerVolume,
    Players,
)
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

PLAYER_DATA = {
    "id": 11,
    "device_name": "Freebox Player",
    "uid": "123456789012345678911234567892123",
    "reachable": True,
    "api_version": "6.0",
    "api_available": True,
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


class TestPlayerDataclass:
    def test_from_dict(self):
        p = Player._from_dict(PLAYER_DATA)
        assert p.id == 11
        assert p.device_name == "Freebox Player"
        assert p.reachable is True
        assert p.api_version == "6.0"
        assert p.api_available is True

    def test_defaults(self):
        p = Player._from_dict({})
        assert p.id == 0
        assert p.reachable is False


class TestPlayerStatusCapabilitiesDataclass:
    def test_from_dict(self):
        caps = PlayerStatusCapabilities._from_dict({"play": True, "pause": True})
        assert caps.play is True
        assert caps.pause is True
        assert caps.stop is False

    def test_defaults(self):
        caps = PlayerStatusCapabilities._from_dict({})
        assert caps.play is False


class TestPlayerStatusDataclass:
    def test_from_dict_minimal(self):
        status = PlayerStatus._from_dict({"power_state": "standby"})
        assert status.power_state == "standby"
        assert status.player is None
        assert status.foreground_app is None

    def test_from_dict_full(self):
        status = PlayerStatus._from_dict({
            "power_state": "running",
            "player": {
                "name": "tv",
                "last_activity": 1000000,
                "capabilities": {"play": True},
            },
            "foreground_app": {
                "package_id": "fr.freebox.tv",
                "cur_url": "tv:?channel=2",
                "package": "tv",
            },
        })
        assert status.power_state == "running"
        assert status.player is not None
        assert isinstance(status.player, PlayerStatusInformations)
        assert status.player.name == "tv"
        assert status.player.capabilities.play is True
        assert status.foreground_app is not None
        assert isinstance(status.foreground_app, PlayerStatusForegroundApp)
        assert status.foreground_app.package_id == "fr.freebox.tv"


class TestPlayerVolumeDataclass:
    def test_from_dict(self):
        vol = PlayerVolume._from_dict({"mute": False, "volume": 25})
        assert vol.mute is False
        assert vol.volume == 25

    def test_defaults(self):
        vol = PlayerVolume._from_dict({})
        assert vol.mute is False
        assert vol.volume == 0


class TestPlayersApi:
    def test_players(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/player", json=api_ok([PLAYER_DATA]))
        players = fb.player.players()
        assert len(players) == 1
        assert isinstance(players[0], Player)
        assert players[0].id == 11

    def test_players_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/player", json=api_ok([]))
        assert fb.player.players() == []

    def test_players_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/player", json=api_ok(None))
        assert fb.player.players() == []

    def test_status(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/player/11/api/v6/status/",
            json=api_ok({"power_state": "standby"}),
        )
        status = fb.player.status(11)
        assert isinstance(status, PlayerStatus)
        assert status.power_state == "standby"

    def test_volume(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/player/11/api/v6/control/volume/",
            json=api_ok({"mute": False, "volume": 25}),
        )
        vol = fb.player.volume(11)
        assert isinstance(vol, PlayerVolume)
        assert vol.volume == 25

    def test_set_volume(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/player/11/api/v6/control/volume/",
            method="PUT",
            json=api_ok({"mute": False, "volume": 50}),
        )
        vol = fb.player.set_volume(11, volume=50)
        assert vol.volume == 50

    def test_open(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/player/11/api/v6/control/open",
            method="POST",
            json=api_ok(None),
        )
        fb.player.open(11, url="tv:?channel=2")

    def test_mediactrl(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/player/11/api/v6/control/mediactrl/",
            method="POST",
            json=api_ok(None),
        )
        fb.player.mediactrl(11, cmd="play_pause")

    def test_property(self, fb):
        assert isinstance(fb.player, Players)
