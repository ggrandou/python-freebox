import pytest

from freebox import Freebox, Switch, SwitchPortConfig, SwitchPortMacEntry, SwitchPortStats, SwitchPortStatus
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

PORT_STATUS_UP = {
    "id": 1,
    "link": "up",
    "duplex": "full",
    "speed": "1000",
    "mode": "1000BaseT-FD",
    "mac_list": [
        {"mac": "00:24:D4:7E:00:4C", "hostname": "my-pc"},
    ],
}

PORT_STATUS_DOWN = {
    "id": 2,
    "link": "down",
    "duplex": "half",
    "speed": "10",
    "mode": "10BaseT-HD",
}

PORT_CONFIG_DATA = {
    "id": 1,
    "speed": "auto",
    "duplex": "auto",
}

PORT_STATS_DATA = {
    "rx_bad_bytes": 0,
    "rx_broadcast_packets": 45,
    "rx_bytes_rate": 608,
    "rx_err_packets": 0,
    "rx_fcs_packets": 0,
    "rx_fragments_packets": 0,
    "rx_good_bytes": 20018805,
    "rx_good_packets": 114296,
    "rx_jabber_packets": 0,
    "rx_multicast_packets": 1217,
    "rx_oversize_packets": 0,
    "rx_packets_rate": 4,
    "rx_pause": 0,
    "rx_undersize_packets": 0,
    "rx_unicast_packets": 113034,
    "tx_broadcast_packets": 25895,
    "tx_bytes": 25316860,
    "tx_bytes_rate": 736,
    "tx_collisions": 0,
    "tx_deferred": 0,
    "tx_excessive": 0,
    "tx_fcs": 0,
    "tx_late": 0,
    "tx_multicast_packets": 27962,
    "tx_multiple": 0,
    "tx_packets": 166266,
    "tx_packets_rate": 6,
    "tx_pause": 0,
    "tx_single": 0,
    "tx_unicast_packets": 112409,
}


# ── SwitchPortMacEntry ─────────────────────────────────────────────────────────

class TestSwitchPortMacEntry:
    def test_fields(self):
        e = SwitchPortMacEntry._from_dict({"mac": "AA:BB:CC:DD:EE:FF", "hostname": "laptop"})
        assert e.mac == "AA:BB:CC:DD:EE:FF"
        assert e.hostname == "laptop"

    def test_defaults(self):
        e = SwitchPortMacEntry._from_dict({})
        assert e.mac == ""
        assert e.hostname == ""


# ── SwitchPortStatus ───────────────────────────────────────────────────────────

class TestSwitchPortStatus:
    def test_fields_up(self):
        s = SwitchPortStatus._from_dict(PORT_STATUS_UP)
        assert s.id == 1
        assert s.link == "up"
        assert s.duplex == "full"
        assert s.speed == "1000"
        assert s.mode == "1000BaseT-FD"
        assert len(s.mac_list) == 1
        assert s.mac_list[0].mac == "00:24:D4:7E:00:4C"
        assert s.mac_list[0].hostname == "my-pc"

    def test_fields_down_no_mac_list(self):
        s = SwitchPortStatus._from_dict(PORT_STATUS_DOWN)
        assert s.id == 2
        assert s.link == "down"
        assert s.mac_list == []

    def test_defaults(self):
        s = SwitchPortStatus._from_dict({})
        assert s.id == 0
        assert s.link == ""
        assert s.mac_list == []


# ── SwitchPortConfig ───────────────────────────────────────────────────────────

class TestSwitchPortConfig:
    def test_fields(self):
        c = SwitchPortConfig._from_dict(PORT_CONFIG_DATA)
        assert c.id == 1
        assert c.speed == "auto"
        assert c.duplex == "auto"

    def test_defaults(self):
        c = SwitchPortConfig._from_dict({})
        assert c.id == 0
        assert c.speed == "auto"
        assert c.duplex == "auto"


# ── SwitchPortStats ────────────────────────────────────────────────────────────

class TestSwitchPortStats:
    def test_fields(self):
        s = SwitchPortStats._from_dict(PORT_STATS_DATA)
        assert s.rx_good_bytes == 20018805
        assert s.rx_bytes_rate == 608
        assert s.tx_bytes == 25316860
        assert s.tx_bytes_rate == 736
        assert s.rx_unicast_packets == 113034
        assert s.tx_unicast_packets == 112409
        assert s.rx_broadcast_packets == 45
        assert s.tx_broadcast_packets == 25895
        assert s.rx_multicast_packets == 1217
        assert s.tx_multicast_packets == 27962
        assert s.tx_collisions == 0

    def test_defaults(self):
        s = SwitchPortStats._from_dict({})
        assert s.rx_good_bytes == 0
        assert s.tx_bytes == 0
        assert s.rx_bytes_rate == 0


# ── Switch API methods ─────────────────────────────────────────────────────────

class TestSwitch:
    def test_status(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/switch/status/",
            json=api_ok([PORT_STATUS_UP, PORT_STATUS_DOWN]),
        )
        ports = fb.switch.status()
        assert len(ports) == 2
        assert isinstance(ports[0], SwitchPortStatus)
        assert ports[0].link == "up"
        assert ports[1].link == "down"

    def test_status_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/switch/status/", json=api_ok([]))
        assert fb.switch.status() == []

    def test_port_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/switch/port/1",
            json=api_ok(PORT_CONFIG_DATA),
        )
        cfg = fb.switch.port_config(1)
        assert isinstance(cfg, SwitchPortConfig)
        assert cfg.id == 1
        assert cfg.speed == "auto"
        assert cfg.duplex == "auto"

    def test_set_port_config(self, fb, httpx_mock):
        updated = {"id": 1, "speed": "100", "duplex": "full"}
        httpx_mock.add_response(
            url=f"{API}/switch/port/1",
            method="PUT",
            json=api_ok(updated),
        )
        cfg = fb.switch.set_port_config(1, speed="100", duplex="full")
        assert isinstance(cfg, SwitchPortConfig)
        assert cfg.speed == "100"
        assert cfg.duplex == "full"
        req = httpx_mock.get_requests()[-1]
        assert req.method == "PUT"

    def test_port_stats(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/switch/port/1/stats",
            json=api_ok(PORT_STATS_DATA),
        )
        stats = fb.switch.port_stats(1)
        assert isinstance(stats, SwitchPortStats)
        assert stats.rx_good_bytes == 20018805
        assert stats.tx_bytes == 25316860

    def test_switch_property(self, fb):
        assert isinstance(fb.switch, Switch)
