import pytest

from freebox import Freebox, Rrd, RRDDatabase, RRDResult, RRDSample
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"


# ── Fixtures ───────────────────────────────────────────────────────────────────

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
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"settings": True}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token_file=token_file,
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Fixture data ───────────────────────────────────────────────────────────────

RRD_RESULT_DATA = {
    "date_start": 1353048060,
    "date_end": 1353069660,
    "data": [
        {"temp1": 540, "cpum": 480, "time": 1353060840},
        {"temp1": 545, "cpum": 485, "time": 1353060900},
        {"temp1": 540, "cpum": 480, "time": 1353060960},
    ],
}


# ── RRDDatabase ────────────────────────────────────────────────────────────────

class TestRRDDatabase:
    def test_values(self):
        assert RRDDatabase.NET == "net"
        assert RRDDatabase.TEMP == "temp"
        assert RRDDatabase.DSL == "dsl"
        assert RRDDatabase.SWITCH == "switch"

    def test_value(self):
        assert RRDDatabase.NET.value == "net"


# ── RRDSample ──────────────────────────────────────────────────────────────────

class TestRRDSample:
    def test_fields(self):
        s = RRDSample._from_dict({"time": 1353060840, "temp1": 540, "cpum": 480})
        assert s.time == 1353060840
        assert s.values == {"temp1": 540, "cpum": 480}

    def test_defaults(self):
        s = RRDSample._from_dict({})
        assert s.time == 0
        assert s.values == {}

    def test_time_excluded_from_values(self):
        s = RRDSample._from_dict({"time": 100, "rate_up": 1024})
        assert "time" not in s.values
        assert s.values["rate_up"] == 1024


# ── RRDResult ──────────────────────────────────────────────────────────────────

class TestRRDResult:
    def test_fields(self):
        r = RRDResult._from_dict(RRD_RESULT_DATA)
        assert r.date_start == 1353048060
        assert r.date_end == 1353069660
        assert len(r.data) == 3

    def test_samples(self):
        r = RRDResult._from_dict(RRD_RESULT_DATA)
        assert r.data[0].time == 1353060840
        assert r.data[0].values["temp1"] == 540
        assert r.data[1].values["cpum"] == 485

    def test_defaults(self):
        r = RRDResult._from_dict({})
        assert r.date_start == 0
        assert r.date_end == 0
        assert r.data == []


# ── Rrd.fetch ──────────────────────────────────────────────────────────────────

class TestRrd:
    def test_fetch_basic(self, fb, httpx_mock):
        httpx_mock.add_response(method="GET", json=api_ok(RRD_RESULT_DATA))
        result = fb.rrd.fetch(RRDDatabase.TEMP)
        assert isinstance(result, RRDResult)
        assert result.date_start == 1353048060
        assert len(result.data) == 3

    def test_fetch_sends_db(self, fb, httpx_mock):
        httpx_mock.add_response(method="GET", json=api_ok(RRD_RESULT_DATA))
        fb.rrd.fetch(RRDDatabase.NET)
        req = httpx_mock.get_requests()[-1]
        assert "db=net" in str(req.url)

    def test_fetch_with_fields(self, fb, httpx_mock):
        httpx_mock.add_response(method="GET", json=api_ok(RRD_RESULT_DATA))
        fb.rrd.fetch(RRDDatabase.TEMP, fields=["temp1"])
        req = httpx_mock.get_requests()[-1]
        assert "fields%5B%5D=temp1" in str(req.url)

    def test_fetch_with_precision(self, fb, httpx_mock):
        httpx_mock.add_response(method="GET", json=api_ok(RRD_RESULT_DATA))
        fb.rrd.fetch(RRDDatabase.TEMP, precision=10)
        req = httpx_mock.get_requests()[-1]
        assert "precision=10" in str(req.url)

    def test_fetch_with_date_range(self, fb, httpx_mock):
        httpx_mock.add_response(method="GET", json=api_ok(RRD_RESULT_DATA))
        fb.rrd.fetch(RRDDatabase.TEMP, date_start=1353048060, date_end=1353069660)
        req = httpx_mock.get_requests()[-1]
        url = str(req.url)
        assert "date_start=1353048060" in url
        assert "date_end=1353069660" in url

    def test_fetch_no_optional_fields_by_default(self, fb, httpx_mock):
        httpx_mock.add_response(method="GET", json=api_ok(RRD_RESULT_DATA))
        fb.rrd.fetch(RRDDatabase.NET)
        req = httpx_mock.get_requests()[-1]
        url = str(req.url)
        assert "fields" not in url
        assert "precision" not in url
        assert "date_start" not in url
        assert "date_end" not in url

    def test_fetch_string_db(self, fb, httpx_mock):
        httpx_mock.add_response(method="GET", json=api_ok(RRD_RESULT_DATA))
        fb.rrd.fetch("switch")
        req = httpx_mock.get_requests()[-1]
        assert "db=switch" in str(req.url)

    def test_rrd_property(self, fb):
        assert isinstance(fb.rrd, Rrd)
