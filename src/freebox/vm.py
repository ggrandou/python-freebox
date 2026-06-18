"""Freebox Virtual Machine API."""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


def _decode_path(path: str) -> str:
    if not path:
        return ""
    try:
        return base64.b64decode(path).decode()
    except Exception:
        return path


# ── Data objects ──────────────────────────────────────────────────────────────

@dataclass
class VmSystemInfo:
    """Host-level resources available to VMs."""

    total_memory: int
    used_memory: int
    total_cpus: int
    used_cpus: int
    usb_ports: list[str]
    usb_used: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VmSystemInfo:
        return cls(
            total_memory=d.get("total_memory", 0),
            used_memory=d.get("used_memory", 0),
            total_cpus=d.get("total_cpus", 0),
            used_cpus=d.get("used_cpus", 0),
            usb_ports=list(d.get("usb_ports") or []),
            usb_used=d.get("usb_used", False),
        )


@dataclass
class VmDistribution:
    """A downloadable VM distribution image."""

    name: str
    url: str
    hash: str
    os: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VmDistribution:
        return cls(
            name=d.get("name", ""),
            url=d.get("url", ""),
            hash=d.get("hash", ""),
            os=d.get("os", ""),
        )


@dataclass
class VmDiskInfo:
    """Information about a virtual disk image."""

    type: str
    actual_size: int
    virtual_size: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VmDiskInfo:
        return cls(
            type=d.get("type", ""),
            actual_size=d.get("actual_size", 0),
            virtual_size=d.get("virtual_size", 0),
        )


@dataclass
class VmDiskTask:
    """A disk creation or resize task."""

    id: int
    type: str
    done: bool
    error: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VmDiskTask:
        return cls(
            id=d.get("id", 0),
            type=d.get("type", ""),
            done=d.get("done", False),
            error=d.get("error", False),
        )


@dataclass
class Vm:
    """A virtual machine configuration and status.

    ``disk_path`` and ``cd_path`` are base64-encoded.
    Use ``disk_path_decoded`` / ``cd_path_decoded`` for plain strings.
    """

    id: int
    name: str
    status: str
    disk_path: str
    disk_type: str
    cd_path: str
    memory: int
    vcpus: int
    mac: str
    os: str
    enable_screen: bool
    bind_usb_ports: list[str]
    enable_cloudinit: bool
    cloudinit_hostname: str
    cloudinit_userdata: str

    @property
    def disk_path_decoded(self) -> str:
        """Decoded disk image path."""
        return _decode_path(self.disk_path)

    @property
    def cd_path_decoded(self) -> str:
        """Decoded CDROM ISO path."""
        return _decode_path(self.cd_path)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Vm:
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            status=d.get("status", ""),
            disk_path=d.get("disk_path", ""),
            disk_type=d.get("disk_type", ""),
            cd_path=d.get("cd_path", ""),
            memory=d.get("memory", 0),
            vcpus=d.get("vcpus", 0),
            mac=d.get("mac", ""),
            os=d.get("os", ""),
            enable_screen=d.get("enable_screen", False),
            bind_usb_ports=list(d.get("bind_usb_ports") or []),
            enable_cloudinit=d.get("enable_cloudinit", False),
            cloudinit_hostname=d.get("cloudinit_hostname", ""),
            cloudinit_userdata=d.get("cloudinit_userdata", ""),
        )


# ── API class ─────────────────────────────────────────────────────────────────

class VirtualMachines:
    """Freebox Virtual Machine API.

    Obtained via ``fb.vm``::

        info = fb.vm.info()
        print(f"{info.used_memory} / {info.total_memory} MB used")

        vms = fb.vm.list()
        for v in vms:
            print(v.name, v.status, v.disk_path_decoded)

    Only available on Freebox models with ``has_vm = true`` in system config.
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── System info ────────────────────────────────────────────────────────────

    def info(self) -> VmSystemInfo:
        """Return host-level resource availability for VMs."""
        return VmSystemInfo._from_dict(self._client.get("vm/info/"))

    def distros(self) -> list[VmDistribution]:
        """Return the list of installable VM distribution images."""
        result = self._client.get("vm/distros/")
        return [VmDistribution._from_dict(d) for d in result] if result else []

    # ── VM CRUD ────────────────────────────────────────────────────────────────

    def list(self) -> list[Vm]:
        """Return all configured VMs."""
        result = self._client.get("vm/")
        return [Vm._from_dict(v) for v in result] if result else []

    def get(self, vm_id: int) -> Vm:
        """Return the VM with the given id."""
        return Vm._from_dict(self._client.get(f"vm/{vm_id}"))

    def create(self, **kwargs: Any) -> Vm:
        """Create a new VM.

        Required fields: ``name``, ``disk_path`` (base64), ``disk_type``,
        ``memory`` (MB), ``vcpus``.
        """
        return Vm._from_dict(self._client.post("vm/", json=kwargs))

    def update(self, vm_id: int, **kwargs: Any) -> Vm:
        """Update a stopped VM configuration."""
        return Vm._from_dict(self._client.put(f"vm/{vm_id}", json=kwargs))

    def delete(self, vm_id: int) -> None:
        """Delete a stopped VM (does not delete its disk image)."""
        self._client.delete(f"vm/{vm_id}")

    # ── VM power actions ───────────────────────────────────────────────────────

    def start(self, vm_id: int) -> None:
        """Start a stopped VM."""
        self._client.post(f"vm/{vm_id}/start")

    def stop(self, vm_id: int) -> None:
        """Immediately stop a running VM (no graceful shutdown)."""
        self._client.post(f"vm/{vm_id}/stop")

    def restart(self, vm_id: int) -> None:
        """Immediately restart a running VM (no graceful reboot)."""
        self._client.post(f"vm/{vm_id}/restart")

    def powerbutton(self, vm_id: int) -> None:
        """Send an ACPI power-button event to a running VM."""
        self._client.post(f"vm/{vm_id}/powerbutton")

    # ── WebSocket URLs ─────────────────────────────────────────────────────────

    def console_url(self, vm_id: int) -> str:
        """Return the WebSocket URL for the VM serial console.

        Connect with a WebSocket client using the ``X-Fbx-App-Auth`` header.
        """
        return self._client._ws_url(f"vm/{vm_id}/console")

    def vnc_url(self, vm_id: int) -> str:
        """Return the WebSocket URL for the VM VNC screen.

        Only available when ``Vm.enable_screen`` is ``True``.
        Compatible with noVNC unmodified.
        """
        return self._client._ws_url(f"vm/{vm_id}/vnc")

    # ── Disk operations ────────────────────────────────────────────────────────

    def disk_info(self, disk_path: str) -> VmDiskInfo:
        """Return info about a virtual disk image.

        ``disk_path`` is the base64-encoded path to the disk image.
        """
        return VmDiskInfo._from_dict(
            self._client.post("vm/disk/info", json={"disk_path": disk_path})
        )

    def disk_create(self, disk_path: str, size: int, disk_type: str = "qcow2") -> int:
        """Create a virtual disk image.

        Returns a task id. Monitor completion via the ``vm_disk_task_done``
        WebSocket event.
        """
        result = self._client.post(
            "vm/disk/create",
            json={"disk_path": disk_path, "size": size, "disk_type": disk_type},
        )
        return result if isinstance(result, int) else int(result or 0)

    def disk_resize(self, disk_path: str, size: int, shrink_allow: bool = False) -> int:
        """Resize a virtual disk image.

        Returns a task id. Monitor completion via the ``vm_disk_task_done``
        WebSocket event.
        """
        result = self._client.post(
            "vm/disk/resize",
            json={"disk_path": disk_path, "size": size, "shrink_allow": shrink_allow},
        )
        return result if isinstance(result, int) else int(result or 0)

    def disk_task(self, task_id: int) -> VmDiskTask:
        """Return a disk operation task by id."""
        return VmDiskTask._from_dict(self._client.get(f"vm/disk/task/{task_id}"))

    def delete_disk_task(self, task_id: int) -> None:
        """Delete a completed disk operation task."""
        self._client.delete(f"vm/disk/task/{task_id}")
