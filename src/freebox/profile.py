"""Freebox Profile Management API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class Profile:
    """A user profile (GET /profile)."""

    id: int
    name: str
    url: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Profile:
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            url=d.get("url", ""),
        )


class Profiles:
    """Freebox Profile Management API.

    Obtained via ``fb.profile``::

        profiles = fb.profile.profiles()
        p = fb.profile.profile(2)
        new = fb.profile.create(name="Alice", url="/resources/images/profile/profile_01.png")
        fb.profile.update(new.id, name="Alicia")
        fb.profile.delete(new.id)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def profiles(self) -> list[Profile]:
        """Return the list of all profiles."""
        result = self._client.get("profile")
        return [Profile._from_dict(p) for p in result] if result else []

    def profile(self, id: int) -> Profile:
        """Return the profile with the given id."""
        return Profile._from_dict(self._client.get(f"profile/{id}"))

    def create(self, *, name: str, url: str = "") -> Profile:
        """Create a new profile."""
        payload: dict[str, Any] = {"name": name}
        if url:
            payload["url"] = url
        return Profile._from_dict(self._client.post("profile/", json=payload))

    def update(self, id: int, *, name: str | None = None, url: str | None = None) -> Profile:
        """Update an existing profile."""
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if url is not None:
            payload["url"] = url
        return Profile._from_dict(self._client.put(f"profile/{id}", json=payload))

    def delete(self, id: int) -> None:
        """Delete a profile."""
        self._client.delete(f"profile/{id}")
