"""Freebox Update API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class UpgradeState:
    """Details of an in-progress firmware upgrade."""

    state: str
    old_version: str
    new_version: str
    percent: int
    error_string: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UpgradeState:
        return cls(
            state=d.get("state", ""),
            old_version=d.get("old_version", ""),
            new_version=d.get("new_version", ""),
            percent=d.get("percent", 0),
            error_string=d.get("error_string", ""),
        )


@dataclass
class UpdateStatus:
    """Firmware update status (GET /update/)."""

    state: str
    upgrade_state: UpgradeState | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UpdateStatus:
        raw = d.get("upgrade_state")
        return cls(
            state=d.get("state", ""),
            upgrade_state=UpgradeState._from_dict(raw) if raw else None,
        )


class Update:
    """Freebox Update API.

    Obtained via ``fb.update``::

        status = fb.update.status()
        print(status.state)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def status(self) -> UpdateStatus:
        """Return the current firmware update status."""
        return UpdateStatus._from_dict(self._client.get("update/"))
