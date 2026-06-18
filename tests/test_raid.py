"""Unit tests for the RAID API."""
import pytest

from freebox import Freebox, Raid, RaidArray, RaidDisk, RaidMember
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

MEMBER_DATA = {
    "id": 1000,
    "array_id": 0,
    "role": "active",
    "set_name": "Freebox",
    "set_uuid": "a4f1fbf3-f8e7-453f-19ec-842d6f4e2895",
    "dev_uuid": "666793c9-2d04-9d9e-5c8a-2f13eb7f2e9e",
    "device_location": "sata-internal-p1",
    "total_bytes": 1000000000000,
    "active_device": 0,
    "corrected_read_errors": 0,
    "sct_erc_supported": False,
    "sct_erc_enabled": False,
    "disk": {
        "model": "WDC WD10JUCX-56WPNY0",
        "serial": "WD-WX91A42F69NE",
        "firmware": "02.01A02",
        "temp": 43,
    },
}

ARRAY_DATA = {
    "id": 0,
    "state": "running",
    "name": "Freebox",
    "level": "raid5",
    "disk_id": 6000,
    "uuid": "a4f1fbf3-f8e7-453f-19ec-842d6f4e2895",
    "sync_action": "idle",
    "sysfs_state": "clear",
    "array_size": 3000000000000,
    "raid_disks": 4,
    "sync_speed": 0,
    "sync_completed_pos": 0,
    "sync_completed_end": 0,
    "sync_completed_percent": 0,
    "check_interval": 0,
    "last_check": 1576082428,
    "next_check": 0,
    "degraded": False,
    "members": [MEMBER_DATA],
}


@pytest.fixture
def fb(httpx_mock, tmp_path):
    token_file = tmp_path / "token"
    token_file.write_text("test-app-token")
    httpx_mock.add_response(url=f"{BASE}/api_version", json=DISCOVERY_DATA)
    httpx_mock.add_response(
        url=f"{API}/login/",
        json=api_ok({"logged_in": False, "challenge": "chal"}),
    )
    httpx_mock.add_response(
        url=f"{API}/login/session/",
        method="POST",
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token_file=token_file,
        on_pending=lambda _: None,
    )
    client.open()
    return client


class TestRaidDiskDataclass:
    def test_from_dict(self):
        d = RaidDisk._from_dict({"model": "WD", "serial": "SN1", "firmware": "01", "temp": 43})
        assert d.model == "WD"
        assert d.temp == 43

    def test_defaults(self):
        d = RaidDisk._from_dict({})
        assert d.model == ""
        assert d.temp == 0


class TestRaidMemberDataclass:
    def test_from_dict(self):
        m = RaidMember._from_dict(MEMBER_DATA)
        assert m.id == 1000
        assert m.role == "active"
        assert m.total_bytes == 1000000000000
        assert m.disk is not None
        assert isinstance(m.disk, RaidDisk)
        assert m.disk.model == "WDC WD10JUCX-56WPNY0"
        assert m.disk.temp == 43

    def test_no_disk(self):
        data = {**MEMBER_DATA, "disk": None}
        m = RaidMember._from_dict(data)
        assert m.disk is None

    def test_defaults(self):
        m = RaidMember._from_dict({})
        assert m.id == 0
        assert m.role == ""


class TestRaidArrayDataclass:
    def test_from_dict(self):
        a = RaidArray._from_dict(ARRAY_DATA)
        assert a.id == 0
        assert a.state == "running"
        assert a.level == "raid5"
        assert a.degraded is False
        assert len(a.members) == 1
        assert isinstance(a.members[0], RaidMember)

    def test_no_members(self):
        data = {**ARRAY_DATA, "members": None}
        a = RaidArray._from_dict(data)
        assert a.members == []

    def test_defaults(self):
        a = RaidArray._from_dict({})
        assert a.id == 0
        assert a.members == []


class TestRaidApi:
    def test_arrays(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/raid/", json=api_ok([ARRAY_DATA]))
        arrays = fb.raid.arrays()
        assert len(arrays) == 1
        assert isinstance(arrays[0], RaidArray)
        assert arrays[0].id == 0

    def test_arrays_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/raid/", json=api_ok([]))
        assert fb.raid.arrays() == []

    def test_arrays_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/raid/", json=api_ok(None))
        assert fb.raid.arrays() == []

    def test_array(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/storage/raid/0", json=api_ok(ARRAY_DATA))
        a = fb.raid.array(0)
        assert a.id == 0
        assert a.name == "Freebox"

    def test_create(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/raid/",
            method="POST",
            json=api_ok({**ARRAY_DATA, "level": "raid1"}),
        )
        a = fb.raid.create(level="raid1", name="MyArray", member_ids=[1000, 2000])
        assert a.level == "raid1"

    def test_set_state(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/raid/0",
            method="PUT",
            json=api_ok({**ARRAY_DATA, "state": "stopped"}),
        )
        a = fb.raid.set_state(0, state="stopped")
        assert a.state == "stopped"

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/raid/0",
            method="DELETE",
            json=api_ok(None),
        )
        fb.raid.delete(0)

    def test_forcestart(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/raid/0/forcestart",
            method="POST",
            json=api_ok(None),
        )
        fb.raid.forcestart(0)

    def test_remove_faulty(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/raid/0/members/faulty",
            method="DELETE",
            json=api_ok(None),
        )
        fb.raid.remove_faulty(0)

    def test_add_members(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/raid/0/members",
            method="PUT",
            json=api_ok(None),
        )
        fb.raid.add_members(0, member_ids=[3000])

    def test_add_spares(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/storage/raid/0/members/addspares",
            method="POST",
            json=api_ok(None),
        )
        fb.raid.add_spares(0)

    def test_property(self, fb):
        assert isinstance(fb.raid, Raid)
