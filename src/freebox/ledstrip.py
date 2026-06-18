"""Freebox LED strip API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class LedstripStatus:
    """Current LED strip status (GET /ledstrip/status)."""

    use_planning: bool
    next_change: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LedstripStatus:
        return cls(
            use_planning=d.get("use_planning", False),
            next_change=d.get("next_change", 0),
        )


@dataclass
class LedstripPlanning:
    """LED strip weekly planning (GET/PUT /ledstrip/planning).

    ``mapping`` is a flat array of ``resolution * 7`` booleans: ``True`` means
    the LED strip is disabled for that slot.  Slot 0 is Monday at 00:00; each
    slot spans ``60 * 24 / resolution`` minutes.
    """

    use_planning: bool
    planning_mode: str
    resolution: int
    mapping: list[bool] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LedstripPlanning:
        return cls(
            use_planning=d.get("use_planning", False),
            planning_mode=d.get("planning_mode", ""),
            resolution=d.get("resolution", 48),
            mapping=d.get("mapping", []),
        )


class Ledstrip:
    """Freebox LED strip API.

    Obtained via ``fb.ledstrip``::

        status   = fb.ledstrip.status()
        planning = fb.ledstrip.planning()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def status(self) -> LedstripStatus:
        """Return the current LED strip status."""
        return LedstripStatus._from_dict(self._client.get("ledstrip/status"))

    def planning(self) -> LedstripPlanning:
        """Return the current LED strip weekly planning."""
        return LedstripPlanning._from_dict(self._client.get("ledstrip/planning/"))

    def set_planning(self, **kwargs: Any) -> LedstripPlanning:
        """Update the LED strip weekly planning.

        Pass only the fields to change, e.g.
        ``set_planning(use_planning=True, planning_mode="ledstrip_off")``.
        """
        return LedstripPlanning._from_dict(self._client.put("ledstrip/planning", json=kwargs))
