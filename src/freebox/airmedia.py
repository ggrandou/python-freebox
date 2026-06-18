"""Freebox AirMedia streaming API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class AirMediaConfig:
    """AirMedia server configuration (GET /airmedia/config/)."""

    enabled: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AirMediaConfig:
        return cls(enabled=d.get("enabled", False))


@dataclass
class AirMediaReceiver:
    """An AirMedia receiver (GET /airmedia/receivers/).

    ``capabilities`` is a dict with boolean keys: photo, audio, video, screen.
    """

    name: str
    password_protected: bool
    capabilities: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AirMediaReceiver:
        return cls(
            name=d.get("name", ""),
            password_protected=d.get("password_protected", False),
            capabilities=dict(d.get("capabilities") or {}),
        )


class AirMedia:
    """Freebox AirMedia streaming API.

    Obtained via ``fb.airmedia``::

        receivers = fb.airmedia.receivers()
        for r in receivers:
            print(r.name, r.capabilities)

        fb.airmedia.send(
            "Freebox Player",
            action="start",
            media_type="video",
            media="http://example.com/movie.mp4",
        )
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> AirMediaConfig:
        """Return the current AirMedia server configuration."""
        return AirMediaConfig._from_dict(self._client.get("airmedia/config/"))

    def set_config(self, *, enabled: bool, password: str = "") -> AirMediaConfig:
        """Update the AirMedia server configuration."""
        payload: dict[str, Any] = {"enabled": enabled}
        if password:
            payload["password"] = password
        return AirMediaConfig._from_dict(
            self._client.put("airmedia/config/", json=payload)
        )

    def receivers(self) -> list[AirMediaReceiver]:
        """Return all AirMedia receivers reachable by the Freebox."""
        result = self._client.get("airmedia/receivers/")
        return [AirMediaReceiver._from_dict(r) for r in result] if result else []

    def send(
        self,
        receiver_name: str,
        *,
        action: str,
        media_type: str = "",
        media: str = "",
        password: str = "",
        position: int = 0,
    ) -> None:
        """Send a playback request to an AirMedia receiver.

        ``action`` is 'start' or 'stop'.
        ``media_type`` is 'photo' or 'video'.
        ``media`` is a URL (for video) or a base64-encoded Freebox path (for photo).
        ``position`` is the start position in percent * 1000 (video only).
        ``password`` is required if the receiver is password-protected.
        """
        payload: dict[str, Any] = {"action": action}
        if media_type:
            payload["media_type"] = media_type
        if media:
            payload["media"] = media
        if password:
            payload["password"] = password
        if position:
            payload["position"] = position
        self._client.post(f"airmedia/receivers/{receiver_name}/", json=payload)
