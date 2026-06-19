"""Unit tests for the Virtual Machine API."""
import base64

import pytest

from freebox import Freebox, Vm, VirtualMachines, VmDiskInfo, VmDiskTask, VmDistribution, VmSystemInfo
from tests.conftest import (
    APP_ID,
    APP_NAME,
    APP_VERSION,
    DEVICE_NAME,
    DISCOVERY_DATA,
    SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

_DISK_PATH = base64.b64encode(b"/Disque dur/vm/debian.qcow2").decode()
_CD_PATH = base64.b64encode(b"/Disque dur/iso/debian.iso").decode()


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def fb(httpx_mock):
    httpx_mock.add_response(url=f"{BASE}/api_version", json=DISCOVERY_DATA)
    httpx_mock.add_response(
        url=f"{API}/login/",
        json=api_ok({"logged_in": False, "challenge": "chal"}),
    )
    httpx_mock.add_response(
        url=f"{API}/login/session/",
        method="POST",
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"vm": True}}),
    )
    client = Freebox(
        app_id=APP_ID,
        app_name=APP_NAME,
        app_version=APP_VERSION,
        device_name=DEVICE_NAME,
        token="test-app-token",
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Test data ─────────────────────────────────────────────────────────────────

SYSINFO_DICT = {
    "total_memory": 4096,
    "used_memory": 512,
    "total_cpus": 4,
    "used_cpus": 1,
    "usb_ports": ["usb-external-type-a", "usb-external-type-c"],
    "usb_used": False,
}

DISTRO_DICT = {
    "name": "Debian 12",
    "url": "https://cloud.debian.org/images/cloud/bookworm/debian-12-generic-arm64.qcow2",
    "hash": "sha256:abc123",
    "os": "debian",
}

VM_DICT = {
    "id": 1,
    "name": "my-debian",
    "status": "stopped",
    "disk_path": _DISK_PATH,
    "disk_type": "qcow2",
    "cd_path": _CD_PATH,
    "memory": 512,
    "vcpus": 1,
    "mac": "de:ad:be:ef:00:01",
    "os": "debian",
    "enable_screen": True,
    "bind_usb_ports": [],
    "enable_cloudinit": False,
    "cloudinit_hostname": "",
    "cloudinit_userdata": "",
}

DISKINFO_DICT = {
    "type": "qcow2",
    "actual_size": 536870912,
    "virtual_size": 21474836480,
}

DISKTASK_DICT = {
    "id": 42,
    "type": "create",
    "done": True,
    "error": False,
}


# ── VmSystemInfo ──────────────────────────────────────────────────────────────

def test_sysinfo_from_dict():
    s = VmSystemInfo._from_dict(SYSINFO_DICT)
    assert s.total_memory == 4096
    assert s.used_memory == 512
    assert s.total_cpus == 4
    assert s.used_cpus == 1
    assert s.usb_ports == ["usb-external-type-a", "usb-external-type-c"]
    assert s.usb_used is False


def test_sysinfo_defaults():
    s = VmSystemInfo._from_dict({})
    assert s.total_memory == 0
    assert s.usb_ports == []
    assert s.usb_used is False


# ── VmDistribution ────────────────────────────────────────────────────────────

def test_distro_from_dict():
    d = VmDistribution._from_dict(DISTRO_DICT)
    assert d.name == "Debian 12"
    assert d.os == "debian"
    assert d.hash == "sha256:abc123"


def test_distro_defaults():
    d = VmDistribution._from_dict({})
    assert d.name == ""
    assert d.url == ""


# ── Vm ────────────────────────────────────────────────────────────────────────

def test_vm_from_dict():
    v = Vm._from_dict(VM_DICT)
    assert v.id == 1
    assert v.name == "my-debian"
    assert v.status == "stopped"
    assert v.disk_type == "qcow2"
    assert v.memory == 512
    assert v.vcpus == 1
    assert v.mac == "de:ad:be:ef:00:01"
    assert v.os == "debian"
    assert v.enable_screen is True
    assert v.bind_usb_ports == []
    assert v.enable_cloudinit is False


def test_vm_disk_path_decoded():
    v = Vm._from_dict(VM_DICT)
    assert v.disk_path_decoded == "/Disque dur/vm/debian.qcow2"


def test_vm_cd_path_decoded():
    v = Vm._from_dict(VM_DICT)
    assert v.cd_path_decoded == "/Disque dur/iso/debian.iso"


def test_vm_empty_cd_path():
    v = Vm._from_dict(dict(VM_DICT, cd_path=""))
    assert v.cd_path_decoded == ""


def test_vm_defaults():
    v = Vm._from_dict({})
    assert v.id == 0
    assert v.name == ""
    assert v.status == ""
    assert v.bind_usb_ports == []
    assert v.disk_path_decoded == ""


# ── VmDiskInfo ────────────────────────────────────────────────────────────────

def test_diskinfo_from_dict():
    d = VmDiskInfo._from_dict(DISKINFO_DICT)
    assert d.type == "qcow2"
    assert d.actual_size == 536870912
    assert d.virtual_size == 21474836480


def test_diskinfo_defaults():
    d = VmDiskInfo._from_dict({})
    assert d.type == ""
    assert d.actual_size == 0


# ── VmDiskTask ────────────────────────────────────────────────────────────────

def test_disktask_from_dict():
    t = VmDiskTask._from_dict(DISKTASK_DICT)
    assert t.id == 42
    assert t.type == "create"
    assert t.done is True
    assert t.error is False


def test_disktask_defaults():
    t = VmDiskTask._from_dict({})
    assert t.id == 0
    assert t.done is False
    assert t.error is False


# ── API: info / distros ───────────────────────────────────────────────────────

def test_info(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/info/", json=api_ok(SYSINFO_DICT))
    s = fb.vm.info()
    assert isinstance(s, VmSystemInfo)
    assert s.total_memory == 4096


def test_distros(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/distros/", json=api_ok([DISTRO_DICT]))
    ds = fb.vm.distros()
    assert len(ds) == 1
    assert ds[0].name == "Debian 12"


def test_distros_empty(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/distros/", json=api_ok(None))
    assert fb.vm.distros() == []


# ── API: VM CRUD ──────────────────────────────────────────────────────────────

def test_list(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/", json=api_ok([VM_DICT]))
    vms = fb.vm.list()
    assert len(vms) == 1
    assert vms[0].name == "my-debian"


def test_list_empty(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/", json=api_ok([]))
    assert fb.vm.list() == []


def test_list_null(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/", json=api_ok(None))
    assert fb.vm.list() == []


def test_get(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/1", json=api_ok(VM_DICT))
    v = fb.vm.get(1)
    assert v.id == 1
    assert v.status == "stopped"


def test_create(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/", method="POST", json=api_ok(VM_DICT))
    v = fb.vm.create(
        name="my-debian",
        disk_path=_DISK_PATH,
        disk_type="qcow2",
        memory=512,
        vcpus=1,
    )
    assert v.name == "my-debian"


def test_update(fb, httpx_mock):
    updated = dict(VM_DICT, memory=1024)
    httpx_mock.add_response(url=f"{API}/vm/1", method="PUT", json=api_ok(updated))
    v = fb.vm.update(1, memory=1024)
    assert v.memory == 1024


def test_delete(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/1", method="DELETE", json=api_ok(None))
    fb.vm.delete(1)


# ── API: power actions ────────────────────────────────────────────────────────

def test_start(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/1/start", method="POST", json=api_ok(None))
    fb.vm.start(1)


def test_stop(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/1/stop", method="POST", json=api_ok(None))
    fb.vm.stop(1)


def test_restart(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/1/restart", method="POST", json=api_ok(None))
    fb.vm.restart(1)


def test_powerbutton(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/vm/1/powerbutton", method="POST", json=api_ok(None))
    fb.vm.powerbutton(1)


# ── API: WebSocket URLs ───────────────────────────────────────────────────────

def test_console_url(fb):
    url = fb.vm.console_url(1)
    assert "vm/1/console" in url
    assert url.startswith("wss://")


def test_vnc_url(fb):
    url = fb.vm.vnc_url(1)
    assert "vm/1/vnc" in url
    assert url.startswith("wss://")


# ── API: disk operations ──────────────────────────────────────────────────────

def test_disk_info(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/vm/disk/info",
        method="POST",
        json=api_ok(DISKINFO_DICT),
    )
    d = fb.vm.disk_info(_DISK_PATH)
    assert d.type == "qcow2"
    assert d.virtual_size == 21474836480


def test_disk_create(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/vm/disk/create",
        method="POST",
        json=api_ok(42),
    )
    task_id = fb.vm.disk_create(_DISK_PATH, 10 * 1024 ** 3)
    assert task_id == 42


def test_disk_resize(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/vm/disk/resize",
        method="POST",
        json=api_ok(43),
    )
    task_id = fb.vm.disk_resize(_DISK_PATH, 20 * 1024 ** 3)
    assert task_id == 43


def test_disk_task(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/vm/disk/task/42",
        json=api_ok(DISKTASK_DICT),
    )
    t = fb.vm.disk_task(42)
    assert t.id == 42
    assert t.done is True


def test_delete_disk_task(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/vm/disk/task/42",
        method="DELETE",
        json=api_ok(None),
    )
    fb.vm.delete_disk_task(42)


# ── Property ──────────────────────────────────────────────────────────────────

def test_freebox_vm_property(fb):
    assert isinstance(fb.vm, VirtualMachines)
