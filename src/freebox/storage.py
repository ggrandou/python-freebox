"""Freebox storage (disks and partitions) API."""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class OperationProgress:
    """Progress of a disk/partition operation."""

    done_steps: int
    max_steps: int
    percent: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> OperationProgress:
        return cls(
            done_steps=d.get("done_steps", 0),
            max_steps=d.get("max_steps", 0),
            percent=d.get("percent", 0),
        )


@dataclass
class DiskPartition:
    """A disk partition (GET /storage/partition/).

    The ``path`` field is base64-encoded.  Use ``path_decoded`` for the
    plain mount-point string.
    """

    id: int
    disk_id: int
    state: str
    fstype: str
    label: str
    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    fsck_result: str
    operation_pct: OperationProgress | None

    @property
    def path_decoded(self) -> str:
        """Decoded mount point (base64 → plain string)."""
        if not self.path:
            return ""
        try:
            return base64.b64decode(self.path).decode()
        except Exception:
            return self.path

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DiskPartition:
        op = d.get("operation_pct")
        return cls(
            id=d.get("id", 0),
            disk_id=d.get("disk_id", 0),
            state=d.get("state", ""),
            fstype=d.get("fstype", ""),
            label=d.get("label", ""),
            path=d.get("path", ""),
            total_bytes=d.get("total_bytes", 0),
            used_bytes=d.get("used_bytes", 0),
            free_bytes=d.get("free_bytes", 0),
            fsck_result=d.get("fsck_result", ""),
            operation_pct=OperationProgress._from_dict(op) if op else None,
        )


@dataclass
class StorageDisk:
    """A storage disk (GET /storage/disk/)."""

    id: int
    type: str
    state: str
    connector: int
    total_bytes: int
    table_type: str
    model: str
    serial: str
    firmware: str
    temp: int
    partitions: list[DiskPartition]
    operation_pct: OperationProgress | None
    idle: bool
    idle_duration: int
    spinning: bool
    active_duration: int
    time_before_spindown: int
    read_requests: int
    read_error_requests: int
    write_requests: int
    write_error_requests: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StorageDisk:
        op = d.get("operation_pct")
        return cls(
            id=d.get("id", 0),
            type=d.get("type", ""),
            state=d.get("state", ""),
            connector=d.get("connector", 0),
            total_bytes=d.get("total_bytes", 0),
            table_type=d.get("table_type", ""),
            model=d.get("model", ""),
            serial=d.get("serial", ""),
            firmware=d.get("firmware", ""),
            temp=d.get("temp", 0),
            partitions=[DiskPartition._from_dict(p) for p in d.get("partitions", [])],
            operation_pct=OperationProgress._from_dict(op) if op else None,
            idle=d.get("idle", False),
            idle_duration=d.get("idle_duration", 0),
            spinning=d.get("spinning", False),
            active_duration=d.get("active_duration", 0),
            time_before_spindown=d.get("time_before_spindown", 0),
            read_requests=d.get("read_requests", 0),
            read_error_requests=d.get("read_error_requests", 0),
            write_requests=d.get("write_requests", 0),
            write_error_requests=d.get("write_error_requests", 0),
        )


@dataclass
class StorageConfig:
    """External storage power-management configuration."""

    external_pm_enabled: bool
    external_pm_idle_before_spindown: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StorageConfig:
        return cls(
            external_pm_enabled=d.get("external_pm_enabled", False),
            external_pm_idle_before_spindown=d.get("external_pm_idle_before_spindown", 0),
        )


@dataclass
class FsAdvice:
    """Filesystem formatting advice for a disk."""

    fstype: str
    table_type: str
    reason: str
    partitions_to_delete: list[DiskPartition] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FsAdvice:
        return cls(
            fstype=d.get("fstype", ""),
            table_type=d.get("table_type", ""),
            reason=d.get("reason", ""),
            partitions_to_delete=[
                DiskPartition._from_dict(p) for p in d.get("partitions_to_delete", [])
            ],
        )


class Storage:
    """Freebox storage (disks and partitions) API.

    Obtained via ``fb.storage``::

        for disk in fb.storage.disks():
            print(disk.model, disk.total_bytes)
            for part in disk.partitions:
                print(part.label, part.path_decoded, part.free_bytes)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Config ─────────────────────────────────────────────────────────────────

    def config(self) -> StorageConfig:
        """Return the external storage power-management configuration."""
        return StorageConfig._from_dict(self._client.get("storage/config/"))

    def set_config(self, **kwargs: Any) -> StorageConfig:
        """Update the external storage power-management configuration."""
        return StorageConfig._from_dict(
            self._client.put("storage/config/", json=kwargs)
        )

    # ── Disks ──────────────────────────────────────────────────────────────────

    def disks(self) -> list[StorageDisk]:
        """Return all storage disks."""
        result = self._client.get("storage/disk/")
        return [StorageDisk._from_dict(d) for d in result] if result else []

    def disk(self, disk_id: int) -> StorageDisk:
        """Return the disk with the given id."""
        return StorageDisk._from_dict(self._client.get(f"storage/disk/{disk_id}"))

    def set_disk_state(self, disk_id: int, state: str) -> StorageDisk:
        """Enable or disable a disk (state: 'enabled' or 'disabled')."""
        return StorageDisk._from_dict(
            self._client.put(f"storage/disk/{disk_id}", json={"state": state})
        )

    def fsadvice(
        self,
        disk_id: int,
        *,
        partition_id: int | None = None,
        dedicated_disk: bool = False,
    ) -> FsAdvice:
        """Return filesystem formatting advice for a disk.

        Pass ``partition_id`` if the disk already has a partition to check.
        Set ``dedicated_disk=True`` for disks that will only be used with
        the Freebox (typically SATA externals).
        """
        params: dict[str, Any] = {"dedicated_disk": str(dedicated_disk).lower()}
        if partition_id is not None:
            params["partition_id"] = partition_id
        return FsAdvice._from_dict(
            self._client.get(f"storage/disk/{disk_id}/fsadvice", params=params)
        )

    def format_disk(
        self, disk_id: int, *, table_type: str, fs_type: str, label: str
    ) -> None:
        """Format a disk (all data will be lost).

        The operation progress can be monitored via ``disk(disk_id).operation_pct``.
        """
        self._client.put(
            f"storage/disk/{disk_id}/format/",
            json={"table_type": table_type, "fs_type": fs_type, "label": label},
        )

    # ── Partitions ─────────────────────────────────────────────────────────────

    def partitions(self) -> list[DiskPartition]:
        """Return all partitions across all disks."""
        result = self._client.get("storage/partition/")
        return [DiskPartition._from_dict(p) for p in result] if result else []

    def partition(self, partition_id: int) -> DiskPartition:
        """Return the partition with the given id."""
        return DiskPartition._from_dict(
            self._client.get(f"storage/partition/{partition_id}")
        )

    def set_partition_state(self, partition_id: int, state: str) -> DiskPartition:
        """Mount or unmount a partition (state: 'mounted' or 'umounted')."""
        return DiskPartition._from_dict(
            self._client.put(f"storage/partition/{partition_id}", json={"state": state})
        )

    def check_partition(self, partition_id: int, checkmode: str = "ro") -> None:
        """Start a filesystem check on a partition.

        ``checkmode`` is 'ro' for read-only check, 'rw' to attempt repair.
        Progress is available via ``partition(partition_id).operation_pct``.
        """
        self._client.put(
            f"storage/partition/{partition_id}/check/", json={"checkmode": checkmode}
        )
