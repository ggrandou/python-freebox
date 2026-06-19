"""Unit tests for the PVR (TV Recording) API."""
import pytest

from freebox import (
    Freebox,
    Pvr,
    PvrConfig,
    PvrFinished,
    PvrMedia,
    PvrProgrammed,
    PvrQuota,
)
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

PRECORD_DATA = {
    "id": 236,
    "media": "NO NAME",
    "path": "Enregistrements",
    "channel_uuid": "uuid-webtv-201",
    "channel_name": "France 2",
    "channel_type": "iptv",
    "channel_quality": "auto",
    "broadcast_type": "tv",
    "name": "Test",
    "subname": "Sub Test",
    "start": 1403541361,
    "end": 1403541511,
    "state": "finished",
    "error": "none",
    "enabled": True,
    "altered": True,
    "conflict": False,
    "has_record_gen": False,
    "record_gen_id": 0,
    "overlap_list": [],
}

FRECORD_DATA = {
    "id": 5,
    "media": "Disque dur",
    "path": "Enregistrements",
    "filename": "M6 - Fier de ma maison.m2ts",
    "byte_size": 4433869440,
    "channel_uuid": "uuid-webtv-613",
    "channel_name": "M6",
    "channel_type": "dvb",
    "channel_quality": "hd",
    "broadcast_type": "tv",
    "name": "Fier de ma maison",
    "subname": "",
    "start": 1372343700,
    "end": 1372348200,
    "state": "finished",
    "error": "none",
    "enabled": True,
    "altered": True,
    "secure": False,
    "has_record_gen": False,
    "record_gen_id": 0,
}


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
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token="test-app-token",
        on_pending=lambda _: None,
    )
    client.open()
    return client


class TestPvrConfigDataclass:
    def test_from_dict(self):
        cfg = PvrConfig._from_dict({"margin_before": 10, "margin_after": 5})
        assert cfg.margin_before == 10
        assert cfg.margin_after == 5

    def test_defaults(self):
        cfg = PvrConfig._from_dict({})
        assert cfg.margin_before == 0
        assert cfg.margin_after == 0


class TestPvrQuotaDataclass:
    def test_from_dict(self):
        quota = PvrQuota._from_dict({"quota_exceeded": True, "needed_tresh": 80, "cur_tresh": 40})
        assert quota.quota_exceeded is True
        assert quota.needed_tresh == 80
        assert quota.cur_tresh == 40

    def test_defaults(self):
        quota = PvrQuota._from_dict({})
        assert quota.quota_exceeded is False


class TestPvrProgrammedDataclass:
    def test_from_dict(self):
        r = PvrProgrammed._from_dict(PRECORD_DATA)
        assert r.id == 236
        assert r.name == "Test"
        assert r.channel_uuid == "uuid-webtv-201"
        assert r.overlap_list == []

    def test_defaults(self):
        r = PvrProgrammed._from_dict({})
        assert r.id == 0
        assert r.overlap_list == []


class TestPvrFinishedDataclass:
    def test_from_dict(self):
        r = PvrFinished._from_dict(FRECORD_DATA)
        assert r.id == 5
        assert r.filename == "M6 - Fier de ma maison.m2ts"
        assert r.byte_size == 4433869440
        assert r.secure is False

    def test_defaults(self):
        r = PvrFinished._from_dict({})
        assert r.id == 0
        assert r.secure is False


class TestPvrMediaDataclass:
    def test_from_dict(self):
        m = PvrMedia._from_dict({
            "media": "Disque dur",
            "free_bytes": 39700000000,
            "total_bytes": 244950000000,
            "record_time": {"dvb": {"sd": 48461}},
        })
        assert m.media == "Disque dur"
        assert m.free_bytes == 39700000000
        assert "dvb" in m.record_time

    def test_defaults(self):
        m = PvrMedia._from_dict({})
        assert m.media == ""
        assert m.record_time == {}


class TestPvrApi:
    def test_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/config/",
            json=api_ok({"margin_before": 10, "margin_after": 5}),
        )
        cfg = fb.pvr.config()
        assert isinstance(cfg, PvrConfig)
        assert cfg.margin_before == 10

    def test_set_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/config/",
            method="PUT",
            json=api_ok({"margin_before": 5, "margin_after": 3}),
        )
        cfg = fb.pvr.set_config(margin_before=5)
        assert cfg.margin_before == 5

    def test_quota(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/quota/",
            json=api_ok({"quota_exceeded": True, "needed_tresh": 80, "cur_tresh": 40}),
        )
        quota = fb.pvr.quota()
        assert isinstance(quota, PvrQuota)
        assert quota.quota_exceeded is True

    def test_request_quota(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/quota/",
            method="PUT",
            json=api_ok({"quota_exceeded": False, "needed_tresh": 80, "cur_tresh": 80}),
        )
        quota = fb.pvr.request_quota()
        assert quota.quota_exceeded is False

    def test_programmed(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/pvr/programmed/", json=api_ok([PRECORD_DATA]))
        records = fb.pvr.programmed()
        assert len(records) == 1
        assert isinstance(records[0], PvrProgrammed)

    def test_programmed_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/pvr/programmed/", json=api_ok([]))
        assert fb.pvr.programmed() == []

    def test_programmed_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/pvr/programmed/", json=api_ok(None))
        assert fb.pvr.programmed() == []

    def test_programmed_record(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/pvr/programmed/236", json=api_ok(PRECORD_DATA))
        r = fb.pvr.programmed_record(236)
        assert r.id == 236

    def test_create_programmed(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/programmed/",
            method="POST",
            json=api_ok({**PRECORD_DATA, "id": 300}),
        )
        r = fb.pvr.create_programmed(
            start=1403541361, end=1403541511,
            channel_uuid="uuid-webtv-201", name="Test",
        )
        assert r.id == 300

    def test_update_programmed(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/programmed/236",
            method="PUT",
            json=api_ok({**PRECORD_DATA, "name": "test 2"}),
        )
        r = fb.pvr.update_programmed(236, name="test 2")
        assert r.name == "test 2"

    def test_delete_programmed(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/programmed/236",
            method="DELETE",
            json=api_ok(None),
        )
        fb.pvr.delete_programmed(236)

    def test_finished(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/pvr/finished/", json=api_ok([FRECORD_DATA]))
        records = fb.pvr.finished()
        assert len(records) == 1
        assert isinstance(records[0], PvrFinished)

    def test_finished_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/pvr/finished/", json=api_ok([]))
        assert fb.pvr.finished() == []

    def test_finished_record(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/pvr/finished/5", json=api_ok(FRECORD_DATA))
        r = fb.pvr.finished_record(5)
        assert r.id == 5

    def test_update_finished(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/finished/5",
            method="PUT",
            json=api_ok({**FRECORD_DATA, "subname": "Champions"}),
        )
        r = fb.pvr.update_finished(5, subname="Champions")
        assert r.subname == "Champions"

    def test_delete_finished(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/finished/5",
            method="DELETE",
            json=api_ok(None),
        )
        fb.pvr.delete_finished(5)

    def test_media(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/pvr/media/",
            json=api_ok([{
                "media": "Disque dur",
                "free_bytes": 39700000000,
                "total_bytes": 244950000000,
                "record_time": {"dvb": {"sd": 48461, "hd": 35245}},
            }]),
        )
        media = fb.pvr.media()
        assert len(media) == 1
        assert isinstance(media[0], PvrMedia)
        assert media[0].media == "Disque dur"

    def test_property(self, fb):
        assert isinstance(fb.pvr, Pvr)
