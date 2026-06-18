"""Freebox Player API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class Player:
    """A Freebox Player device (GET /player)."""

    id: int
    device_name: str
    uid: str
    reachable: bool
    api_version: str
    api_available: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Player:
        return cls(
            id=d.get("id", 0),
            device_name=d.get("device_name", ""),
            uid=d.get("uid", ""),
            reachable=d.get("reachable", False),
            api_version=d.get("api_version", ""),
            api_available=d.get("api_available", False),
        )


@dataclass
class PlayerStatusCapabilities:
    """Capabilities of the active media player."""

    play: bool = False
    pause: bool = False
    stop: bool = False
    next: bool = False
    prev: bool = False
    record: bool = False
    record_stop: bool = False
    seek_forward: bool = False
    seek_backward: bool = False
    seek_to: bool = False
    shuffle: bool = False
    repeat_all: bool = False
    repeat_one: bool = False
    select_stream: bool = False
    select_audio_track: bool = False
    select_srt_track: bool = False

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PlayerStatusCapabilities:
        return cls(
            play=d.get("play", False),
            pause=d.get("pause", False),
            stop=d.get("stop", False),
            next=d.get("next", False),
            prev=d.get("prev", False),
            record=d.get("record", False),
            record_stop=d.get("record_stop", False),
            seek_forward=d.get("seek_forward", False),
            seek_backward=d.get("seek_backward", False),
            seek_to=d.get("seek_to", False),
            shuffle=d.get("shuffle", False),
            repeat_all=d.get("repeat_all", False),
            repeat_one=d.get("repeat_one", False),
            select_stream=d.get("select_stream", False),
            select_audio_track=d.get("select_audio_track", False),
            select_srt_track=d.get("select_srt_track", False),
        )


@dataclass
class PlayerStatusInformations:
    """State of the active media player."""

    name: str
    last_activity: int
    capabilities: PlayerStatusCapabilities = field(
        default_factory=PlayerStatusCapabilities
    )

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PlayerStatusInformations:
        caps_raw = d.get("capabilities") or {}
        return cls(
            name=d.get("name", ""),
            last_activity=d.get("last_activity", 0),
            capabilities=PlayerStatusCapabilities._from_dict(caps_raw),
        )


@dataclass
class PlayerStatusForegroundApp:
    """Context of the currently running application."""

    package_id: str
    cur_url: str
    package: str
    context: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PlayerStatusForegroundApp:
        return cls(
            package_id=d.get("package_id", ""),
            cur_url=d.get("cur_url", ""),
            package=d.get("package", ""),
            context=dict(d.get("context") or {}),
        )


@dataclass
class PlayerStatus:
    """Status of a Freebox Player device (GET /player/{id}/api/v6/status/)."""

    power_state: str
    player: PlayerStatusInformations | None = None
    foreground_app: PlayerStatusForegroundApp | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PlayerStatus:
        player_raw = d.get("player")
        app_raw = d.get("foreground_app")
        return cls(
            power_state=d.get("power_state", ""),
            player=PlayerStatusInformations._from_dict(player_raw) if player_raw else None,
            foreground_app=PlayerStatusForegroundApp._from_dict(app_raw) if app_raw else None,
        )


@dataclass
class PlayerVolume:
    """Playback volume of a player device."""

    mute: bool
    volume: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PlayerVolume:
        return cls(
            mute=d.get("mute", False),
            volume=d.get("volume", 0),
        )


class Players:
    """Freebox Player API.

    Obtained via ``fb.player``::

        players = fb.player.players()
        status = fb.player.status(11)
        vol = fb.player.volume(11)
        fb.player.set_volume(11, volume=50)
        fb.player.open(11, url="tv:?channel=2")
        fb.player.mediactrl(11, cmd="play_pause")
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def players(self) -> list[Player]:
        """Return the list of all Freebox Player devices."""
        result = self._client.get("player")
        return [Player._from_dict(p) for p in result] if result else []

    def status(self, player_id: int) -> PlayerStatus:
        """Return the current status of a player device."""
        return PlayerStatus._from_dict(
            self._client.get(f"player/{player_id}/api/v6/status/")
        )

    def volume(self, player_id: int) -> PlayerVolume:
        """Return the current playback volume of a player device."""
        return PlayerVolume._from_dict(
            self._client.get(f"player/{player_id}/api/v6/control/volume/")
        )

    def set_volume(
        self,
        player_id: int,
        *,
        volume: int | None = None,
        mute: bool | None = None,
    ) -> PlayerVolume:
        """Update the playback volume of a player device."""
        payload: dict[str, Any] = {}
        if volume is not None:
            payload["volume"] = volume
        if mute is not None:
            payload["mute"] = mute
        return PlayerVolume._from_dict(
            self._client.put(f"player/{player_id}/api/v6/control/volume/", json=payload)
        )

    def open(self, player_id: int, *, url: str, type: str = "") -> None:
        """Open a URL on a player device."""
        payload: dict[str, Any] = {"url": url}
        if type:
            payload["type"] = type
        self._client.post(f"player/{player_id}/api/v6/control/open", json=payload)

    def mediactrl(self, player_id: int, *, cmd: str) -> None:
        """Send a media control command to the active media player of a device."""
        self._client.post(
            f"player/{player_id}/api/v6/control/mediactrl/", json={"cmd": cmd}
        )
