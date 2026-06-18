"""Freebox Network Control (parental filter) API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class NetworkControl:
    """Network access control for a profile (GET/PUT /network_control/{profile_id})."""

    profile_id: int
    current_mode: str
    rule_mode: str
    override: bool
    override_mode: str
    override_until: int
    next_change: int
    macs: list[str]
    resolution: int
    cdayranges: list[str]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> NetworkControl:
        return cls(
            profile_id=d.get("profile_id", 0),
            current_mode=d.get("current_mode", ""),
            rule_mode=d.get("rule_mode", ""),
            override=d.get("override", False),
            override_mode=d.get("override_mode", ""),
            override_until=d.get("override_until", 0),
            next_change=d.get("next_change", 0),
            macs=d.get("macs", []),
            resolution=d.get("resolution", 288),
            cdayranges=d.get("cdayranges", []),
        )


@dataclass
class NetworkControlRule:
    """A scheduled access rule within a Network Control profile."""

    id: int
    profile_id: int
    name: str
    mode: str
    start_time: int
    end_time: int
    weekdays: list[bool]
    enabled: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> NetworkControlRule:
        return cls(
            id=d.get("id", 0),
            profile_id=d.get("profile_id", 0),
            name=d.get("name", ""),
            mode=d.get("mode", ""),
            start_time=d.get("start_time", 0),
            end_time=d.get("end_time", 0),
            weekdays=d.get("weekdays", []),
            enabled=d.get("enabled", True),
        )


class NetControl:
    """Freebox Network Control (parental filter) API.

    Obtained via ``fb.netcontrol``::

        controls = fb.netcontrol.controls()
        for nc in controls:
            print(nc.profile_id, nc.current_mode)

        rules = fb.netcontrol.rules(profile_id=3)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Network Control ────────────────────────────────────────────────────────

    def controls(self) -> list[NetworkControl]:
        """Return the network access control for all profiles."""
        result = self._client.get("network_control")
        return [NetworkControl._from_dict(c) for c in result] if result else []

    def control(self, profile_id: int) -> NetworkControl:
        """Return the network access control for a specific profile."""
        return NetworkControl._from_dict(self._client.get(f"network_control/{profile_id}"))

    def set_control(self, profile_id: int, **kwargs: Any) -> NetworkControl:
        """Update the network access control for a profile.

        Pass only the fields to change, e.g.
        ``set_control(3, override=True, override_mode="denied")``.
        """
        return NetworkControl._from_dict(
            self._client.put(f"network_control/{profile_id}", json=kwargs)
        )

    # ── Migration ──────────────────────────────────────────────────────────────

    def migration_status(self) -> bool:
        """Return whether the default-mode migration has been applied."""
        return self._client.get("network_control/migrate").get("default_mode_migrated", False)

    def migrate(self) -> bool:
        """Apply the default-mode migration (sets default to 'allowed').

        Returns True if migration was applied.
        """
        result = self._client.post("network_control/migrate")
        return result.get("default_mode_migrated", False) if result else False

    # ── Rules ──────────────────────────────────────────────────────────────────

    def rules(self, profile_id: int) -> list[NetworkControlRule]:
        """Return the list of access rules for a profile."""
        return [
            NetworkControlRule._from_dict(r)
            for r in self._client.get(f"network_control/{profile_id}/rules")
        ]

    def rule(self, profile_id: int, rule_id: int) -> NetworkControlRule:
        """Return a specific access rule."""
        return NetworkControlRule._from_dict(
            self._client.get(f"network_control/{profile_id}/rules/{rule_id}")
        )

    def add_rule(self, profile_id: int, **kwargs: Any) -> NetworkControlRule:
        """Create a new access rule for a profile.

        Pass rule fields as keyword arguments: ``mode``, ``name``,
        ``start_time``, ``end_time``, ``weekdays``, ``enabled``.
        """
        return NetworkControlRule._from_dict(
            self._client.post(f"network_control/{profile_id}/rules/", json=kwargs)
        )

    def set_rule(self, profile_id: int, rule_id: int, **kwargs: Any) -> NetworkControlRule:
        """Update an access rule."""
        return NetworkControlRule._from_dict(
            self._client.put(f"network_control/{profile_id}/rules/{rule_id}", json=kwargs)
        )

    def delete_rule(self, profile_id: int, rule_id: int) -> None:
        """Delete an access rule."""
        self._client.delete(f"network_control/{profile_id}/rules/{rule_id}")
