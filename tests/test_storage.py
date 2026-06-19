"""Unit tests for the storage (disks and partitions) API."""
import base64

import pytest

from freebox import (
    DiskPartition,
    Freebox,
    FsAdvice,
    OperationProgress,
    Storage,
    StorageConfig,
    StorageDisk,
)
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"


# ── Fixtures ───────────────────────────────────────────────────────────────────

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
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"settings": True}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token="test-app-token",
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Test data ──────────────────────────────────────────────────────────────────

PATH_B64  = base64.b64encode(b"/Disque dur").decode()
PATH2_B64 = base64.b64encode(b"/freebox").decode()

PART_1 = {
    "id": 3,
    "disk_id": 1,
    "state": "mounted",
    "fstype": "ext4",
    "label": "Disque dur",
    "path": PATH_B64,
    "total_bytes": 245091500032,
    "used_bytes": 164520534016,
    "free_bytes": 68120969216,
    "fsck_result": "no_run_yet",
}

PART_2 = {
    "id": 1002,
    "disk_id": 1001,
    "state": "mounted",
    "fstype": "vfat",
    "label": "freebox",
    "path": PATH2_B64,
    "total_bytes": 123485184,
    "used_bytes": 512,
    "free_bytes": 123484672,
    "fsck_result": "no_run_yet",
}

DISK_1 = {
    "id": 1,
    "type": "internal",
    "state": "enabled",
    "connector": 0,
    "total_bytes": 250059350016,
    "table_type": "msdos",
    "model": "Hitachi HCC545025B9A300",
    "serial": "GSCH35VC",
    "firmware": "PB2ICC0E",
    "temp": 51,
    "partitions": [PART_1],
    "idle": True,
    "idle_duration": 368,
    "spinning": True,
    "active_duration": 0,
    "time_before_spindown": 232,
    "read_requests": 0,
    "read_error_requests": 0,
    "write_requests": 0,
    "write_error_requests": 0,
}

DISK_2 = {
    "id": 1001,
    "type": "usb",
    "state": "enabled",
    "connector": 1,
    "total_bytes": 125435904,
    "table_type": "gpt",
    "model": "",
    "serial": "",
    "firmware": "",
    "temp": 0,
    "partitions": [PART_2],
    "idle": False,
    "idle_duration": 0,
    "spinning": False,
    "active_duration": 0,
    "time_before_spindown": 0,
    "read_requests": 0,
    "read_error_requests": 0,
    "write_requests": 0,
    "write_error_requests": 0,
}

CONFIG = {
    "external_pm_enabled": True,
    "external_pm_idle_before_spindown": 10,
}

FSADVICE = {
    "fstype": "exfat",
    "table_type": "gpt",
    "reason": "max_file_size",
    "partitions_to_delete": [PART_2],
}


# ── OperationProgress ──────────────────────────────────────────────────────────

class TestOperationProgress:
    def test_from_dict(self):
        op = OperationProgress._from_dict({"done_steps": 5, "max_steps": 10, "percent": 50})
        assert op.done_steps == 5
        assert op.max_steps == 10
        assert op.percent == 50

    def test_defaults(self):
        op = OperationProgress._from_dict({})
        assert op.done_steps == 0
        assert op.max_steps == 0
        assert op.percent == 0


# ── DiskPartition ──────────────────────────────────────────────────────────────

class TestDiskPartition:
    def test_from_dict(self):
        p = DiskPartition._from_dict(PART_1)
        assert p.id == 3
        assert p.disk_id == 1
        assert p.state == "mounted"
        assert p.fstype == "ext4"
        assert p.label == "Disque dur"
        assert p.path == PATH_B64
        assert p.total_bytes == 245091500032
        assert p.fsck_result == "no_run_yet"
        assert p.operation_pct is None

    def test_path_decoded(self):
        p = DiskPartition._from_dict(PART_1)
        assert p.path_decoded == "/Disque dur"

    def test_path_decoded_empty(self):
        p = DiskPartition._from_dict({**PART_1, "path": ""})
        assert p.path_decoded == ""

    def test_path_decoded_invalid_fallback(self):
        p = DiskPartition._from_dict({**PART_1, "path": "/raw/path"})
        assert p.path_decoded == "/raw/path"

    def test_operation_pct_parsed(self):
        d = {**PART_1, "operation_pct": {"done_steps": 1, "max_steps": 5, "percent": 20}}
        p = DiskPartition._from_dict(d)
        assert isinstance(p.operation_pct, OperationProgress)
        assert p.operation_pct.percent == 20


# ── StorageDisk ────────────────────────────────────────────────────────────────

class TestStorageDisk:
    def test_from_dict(self):
        d = StorageDisk._from_dict(DISK_1)
        assert d.id == 1
        assert d.type == "internal"
        assert d.model == "Hitachi HCC545025B9A300"
        assert d.temp == 51
        assert d.spinning is True
        assert len(d.partitions) == 1
        assert isinstance(d.partitions[0], DiskPartition)
        assert d.operation_pct is None

    def test_no_partitions(self):
        d = StorageDisk._from_dict({**DISK_1, "partitions": []})
        assert d.partitions == []


# ── StorageConfig ──────────────────────────────────────────────────────────────

class TestStorageConfig:
    def test_from_dict(self):
        c = StorageConfig._from_dict(CONFIG)
        assert c.external_pm_enabled is True
        assert c.external_pm_idle_before_spindown == 10

    def test_defaults(self):
        c = StorageConfig._from_dict({})
        assert c.external_pm_enabled is False
        assert c.external_pm_idle_before_spindown == 0


# ── FsAdvice ───────────────────────────────────────────────────────────────────

class TestFsAdvice:
    def test_from_dict(self):
        a = FsAdvice._from_dict(FSADVICE)
        assert a.fstype == "exfat"
        assert a.table_type == "gpt"
        assert a.reason == "max_file_size"
        assert len(a.partitions_to_delete) == 1
        assert isinstance(a.partitions_to_delete[0], DiskPartition)

    def test_no_partitions_to_delete(self):
        a = FsAdvice._from_dict({**FSADVICE, "partitions_to_delete": []})
        assert a.partitions_to_delete == []


# ── Storage API ────────────────────────────────────────────────────────────────

class TestStorageApi:
    def test_config(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/config/", json=api_ok(CONFIG))
        c = fb.storage.config()
        assert isinstance(c, StorageConfig)
        assert c.external_pm_enabled is True

    def test_set_config(self, fb, httpx_mock):
        updated = {**CONFIG, "external_pm_enabled": False}
        httpx_mock.add_response(
            url=f"{API}/storage/config/", method="PUT", json=api_ok(updated)
        )
        c = fb.storage.set_config(external_pm_enabled=False)
        assert c.external_pm_enabled is False

    def test_disks(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/disk/", json=api_ok([DISK_1, DISK_2]))
        disks = fb.storage.disks()
        assert len(disks) == 2
        assert all(isinstance(d, StorageDisk) for d in disks)
        assert disks[0].id == 1
        assert disks[1].id == 1001

    def test_disks_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/disk/", json=api_ok([]))
        assert fb.storage.disks() == []

    def test_disks_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/disk/", json=api_ok(None))
        assert fb.storage.disks() == []

    def test_disk(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/disk/1", json=api_ok(DISK_1))
        d = fb.storage.disk(1)
        assert isinstance(d, StorageDisk)
        assert d.id == 1

    def test_set_disk_state(self, fb, httpx_mock):
        disabled = {**DISK_2, "state": "disabled"}
        httpx_mock.add_response(
            url=f"{API}/storage/disk/1001", method="PUT", json=api_ok(disabled)
        )
        d = fb.storage.set_disk_state(1001, "disabled")
        assert d.state == "disabled"

    def test_fsadvice(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/disk/1000/fsadvice?dedicated_disk=false&partition_id=1002",
            json=api_ok(FSADVICE),
        )
        a = fb.storage.fsadvice(1000, partition_id=1002, dedicated_disk=False)
        assert isinstance(a, FsAdvice)
        assert a.reason == "max_file_size"

    def test_format_disk(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/disk/1001/format/", method="PUT", json=api_ok(None)
        )
        fb.storage.format_disk(1001, table_type="gpt", fs_type="ext4", label="data")

    def test_partitions(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/partition/", json=api_ok([PART_1, PART_2])
        )
        parts = fb.storage.partitions()
        assert len(parts) == 2
        assert all(isinstance(p, DiskPartition) for p in parts)

    def test_partitions_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/partition/", json=api_ok([]))
        assert fb.storage.partitions() == []

    def test_partitions_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/partition/", json=api_ok(None))
        assert fb.storage.partitions() == []

    def test_partition(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/partition/3", json=api_ok(PART_1)
        )
        p = fb.storage.partition(3)
        assert isinstance(p, DiskPartition)
        assert p.id == 3

    def test_set_partition_state(self, fb, httpx_mock):
        umounted = {**PART_2, "state": "umounted"}
        httpx_mock.add_response(
            url=f"{API}/storage/partition/1002", method="PUT", json=api_ok(umounted)
        )
        p = fb.storage.set_partition_state(1002, "umounted")
        assert p.state == "umounted"

    def test_check_partition(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/partition/3/check/", method="PUT", json=api_ok(None)
        )
        fb.storage.check_partition(3, checkmode="ro")


# ── Property ───────────────────────────────────────────────────────────────────

class TestStorageProperty:
    def test_property(self, fb):
        assert isinstance(fb.storage, Storage)
