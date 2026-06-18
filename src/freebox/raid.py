"""Freebox RAID API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class RaidDisk:
    """Basic disk information within a RAID member."""

    model: str
    serial: str
    firmware: str
    temp: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RaidDisk:
        return cls(
            model=d.get("model", ""),
            serial=d.get("serial", ""),
            firmware=d.get("firmware", ""),
            temp=d.get("temp", 0),
        )


@dataclass
class RaidMember:
    """A member disk of a RAID array."""

    id: int
    array_id: int
    role: str
    set_name: str
    set_uuid: str
    dev_uuid: str
    device_location: str
    total_bytes: int
    active_device: int
    corrected_read_errors: int
    sct_erc_supported: bool
    sct_erc_enabled: bool
    disk: RaidDisk | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RaidMember:
        disk_raw = d.get("disk")
        return cls(
            id=d.get("id", 0),
            array_id=d.get("array_id", 0),
            role=d.get("role", ""),
            set_name=d.get("set_name", ""),
            set_uuid=d.get("set_uuid", ""),
            dev_uuid=d.get("dev_uuid", ""),
            device_location=d.get("device_location", ""),
            total_bytes=d.get("total_bytes", 0),
            active_device=d.get("active_device", 0),
            corrected_read_errors=d.get("corrected_read_errors", 0),
            sct_erc_supported=d.get("sct_erc_supported", False),
            sct_erc_enabled=d.get("sct_erc_enabled", False),
            disk=RaidDisk._from_dict(disk_raw) if disk_raw else None,
        )


@dataclass
class RaidArray:
    """A RAID array (GET /storage/raid/)."""

    id: int
    state: str
    name: str
    level: str
    disk_id: int
    uuid: str
    sync_action: str
    sysfs_state: str
    array_size: int
    raid_disks: int
    sync_speed: int
    sync_completed_pos: int
    sync_completed_end: int
    sync_completed_percent: int
    check_interval: int
    last_check: int
    next_check: int
    degraded: bool
    members: list[RaidMember] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RaidArray:
        members = [RaidMember._from_dict(m) for m in (d.get("members") or [])]
        return cls(
            id=d.get("id", 0),
            state=d.get("state", ""),
            name=d.get("name", ""),
            level=d.get("level", ""),
            disk_id=d.get("disk_id", 0),
            uuid=d.get("uuid", ""),
            sync_action=d.get("sync_action", ""),
            sysfs_state=d.get("sysfs_state", ""),
            array_size=d.get("array_size", 0),
            raid_disks=d.get("raid_disks", 0),
            sync_speed=d.get("sync_speed", 0),
            sync_completed_pos=d.get("sync_completed_pos", 0),
            sync_completed_end=d.get("sync_completed_end", 0),
            sync_completed_percent=d.get("sync_completed_percent", 0),
            check_interval=d.get("check_interval", 0),
            last_check=d.get("last_check", 0),
            next_check=d.get("next_check", 0),
            degraded=d.get("degraded", False),
            members=members,
        )


class Raid:
    """Freebox RAID API.

    Obtained via ``fb.raid``::

        arrays = fb.raid.arrays()
        arr = fb.raid.array(0)
        fb.raid.create(level="raid1", name="MyArray", member_ids=[1, 2])
        fb.raid.set_state(0, state="running")
        fb.raid.delete(0)
        fb.raid.forcestart(0)
        fb.raid.remove_faulty(0)
        fb.raid.add_members(0, member_ids=[3])
        fb.raid.add_spares(0)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def arrays(self) -> list[RaidArray]:
        """Return the list of all RAID arrays."""
        result = self._client.get("storage/raid/")
        return [RaidArray._from_dict(a) for a in result] if result else []

    def array(self, id: int) -> RaidArray:
        """Return the RAID array with the given id."""
        return RaidArray._from_dict(self._client.get(f"storage/raid/{id}"))

    def create(self, *, level: str, name: str, member_ids: list[int]) -> RaidArray:
        """Create a new RAID array."""
        payload: dict[str, Any] = {
            "level": level,
            "name": name,
            "members": [{"id": mid} for mid in member_ids],
        }
        return RaidArray._from_dict(self._client.post("storage/raid/", json=payload))

    def set_state(self, id: int, *, state: str) -> RaidArray:
        """Start or stop a RAID array (state: 'running' or 'stopped')."""
        return RaidArray._from_dict(
            self._client.put(f"storage/raid/{id}", json={"id": id, "state": state})
        )

    def delete(self, id: int) -> None:
        """Delete a RAID array."""
        self._client.delete(f"storage/raid/{id}")

    def forcestart(self, id: int) -> None:
        """Force-start a degraded RAID array (state must be 'error')."""
        self._client.post(f"storage/raid/{id}/forcestart")

    def remove_faulty(self, id: int) -> None:
        """Remove all faulty members from a RAID array."""
        self._client.delete(f"storage/raid/{id}/members/faulty")

    def add_members(self, id: int, *, member_ids: list[int]) -> None:
        """Add new members to a RAID array that has missing members."""
        payload = {"members": [{"id": mid} for mid in member_ids]}
        self._client.put(f"storage/raid/{id}/members", json=payload)

    def add_spares(self, id: int) -> None:
        """Re-add out-of-sync spare members to a RAID array."""
        self._client.post(f"storage/raid/{id}/members/addspares")
