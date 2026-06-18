"""Freebox Standby API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class StandbyStatus:
    """Standby status (GET /standby/status)."""

    use_planning: bool
    planning_mode: str
    next_change: int
    available_planning_modes: list[str] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StandbyStatus:
        return cls(
            use_planning=d.get("use_planning", False),
            planning_mode=d.get("planning_mode", ""),
            next_change=d.get("next_change", 0),
            available_planning_modes=list(d.get("available_planning_modes") or []),
        )


@dataclass
class StandbyConfig:
    """Standby configuration (GET/PUT /standby/config/)."""

    use_planning: bool
    planning_mode: str
    resolution: int
    mapping: list[bool] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StandbyConfig:
        return cls(
            use_planning=d.get("use_planning", False),
            planning_mode=d.get("planning_mode", ""),
            resolution=d.get("resolution", 0),
            mapping=list(d.get("mapping") or []),
        )


class Standby:
    """Freebox Standby API.

    Obtained via ``fb.standby``::

        status = fb.standby.status()
        cfg = fb.standby.config()
        fb.standby.set_config(use_planning=True, planning_mode="standby",
                              mapping=[...])
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def status(self) -> StandbyStatus:
        """Return the current standby status."""
        return StandbyStatus._from_dict(self._client.get("standby/status"))

    def config(self) -> StandbyConfig:
        """Return the current standby configuration."""
        return StandbyConfig._from_dict(self._client.get("standby/config/"))

    def set_config(
        self,
        *,
        use_planning: bool | None = None,
        planning_mode: str | None = None,
        mapping: list[bool] | None = None,
    ) -> StandbyConfig:
        """Update the standby configuration."""
        payload: dict[str, Any] = {}
        if use_planning is not None:
            payload["use_planning"] = use_planning
        if planning_mode is not None:
            payload["planning_mode"] = planning_mode
        if mapping is not None:
            payload["mapping"] = mapping
        return StandbyConfig._from_dict(
            self._client.put("standby/config", json=payload)
        )
