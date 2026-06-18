"""Freebox Camera API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class Camera:
    """A camera connected to the Freebox (GET /camera/)."""

    id: str
    node_id: int
    name: str
    stream_url: str
    lan_gid: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Camera:
        return cls(
            id=d.get("id", ""),
            node_id=d.get("node_id", 0),
            name=d.get("name", ""),
            stream_url=d.get("stream_url", ""),
            lan_gid=d.get("lan_gid", ""),
        )


class Cameras:
    """Freebox Camera API.

    Obtained via ``fb.camera``::

        cams = fb.camera.cameras()
        for c in cams:
            print(c.name, c.stream_url)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def cameras(self) -> list[Camera]:
        """Return the list of all cameras."""
        result = self._client.get("camera/")
        return [Camera._from_dict(c) for c in result] if result else []

    def camera(self, id: str) -> Camera:
        """Return the camera with the given id."""
        return Camera._from_dict(self._client.get(f"camera/{id}"))
