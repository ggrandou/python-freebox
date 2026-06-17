import pytest

from freebox import (
    ConnectionConfiguration,
    ConnectionIpv6Configuration,
    ConnectionIpv6Delegation,
    ConnectionStatus,
    DDNSConfig,
    DDNSStatus,
    FtthStatus,
    Freebox,
    LteAggregation,
    LteConfiguration,
    XdslInfos,
)
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)
from freebox.discovery import DiscoveryInfo

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


# ── ConnectionStatus ───────────────────────────────────────────────────────────

STATUS_DATA = {
    "state": "up",
    "type": "ethernet",
    "media": "ftth",
    "rate_up": 1024,
    "rate_down": 4096,
    "bandwidth_up": 100_000_000,
    "bandwidth_down": 100_000_000,
    "bytes_up": 5_489_542,
    "bytes_down": 13_332_830,
    "ipv4": "13.37.42.42",
    "ipv6": "2a01:e30:d252:a2a0::1",
    "ipv4_port_range": [0, 65535],
}


class TestConnectionStatus:
    def test_status_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/", json=api_ok(STATUS_DATA))
        s = fb.connection.status()
        assert isinstance(s, ConnectionStatus)
        assert s.state == "up"
        assert s.type == "ethernet"
        assert s.media == "ftth"
        assert s.rate_up == 1024
        assert s.bandwidth_down == 100_000_000
        assert s.ipv4 == "13.37.42.42"
        assert s.ipv6 == "2a01:e30:d252:a2a0::1"
        assert s.ipv4_port_range == (0, 65535)
        assert s.bytes_up == 5_489_542

    def test_status_no_ip_when_down(self, fb, httpx_mock):
        data = {**STATUS_DATA, "state": "down"}
        data.pop("ipv4")
        data.pop("ipv6")
        httpx_mock.add_response(url=f"{API}/connection/", json=api_ok(data))
        s = fb.connection.status()
        assert s.state == "down"
        assert s.ipv4 is None
        assert s.ipv6 is None


# ── ConnectionConfiguration ────────────────────────────────────────────────────

CONFIG_DATA = {
    "ping": True,
    "is_secure_pass": False,
    "remote_access_port": 80,
    "remote_access": False,
    "wol": False,
    "adblock": False,
    "adblock_not_set": False,
    "api_remote_access": True,
    "allow_token_request": True,
    "remote_access_ip": "13.37.42.42",
    "sip_alg": "disabled",
    "remote_access_min_port": 0,
    "remote_access_max_port": 65535,
}


class TestConnectionConfiguration:
    def test_config_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/config/", json=api_ok(CONFIG_DATA))
        c = fb.connection.config()
        assert isinstance(c, ConnectionConfiguration)
        assert c.ping is True
        assert c.remote_access is False
        assert c.wol is False
        assert c.remote_access_ip == "13.37.42.42"
        assert c.sip_alg == "disabled"

    def test_set_config_sends_put(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/connection/config/",
            method="PUT",
            json=api_ok({**CONFIG_DATA, "ping": False, "wol": True}),
        )
        c = fb.connection.set_config(ping=False, wol=True)
        assert c.ping is False
        assert c.wol is True
        req = httpx_mock.get_requests()[-1]
        import json
        body = json.loads(req.content)
        assert body == {"ping": False, "wol": True}


# ── ConnectionIpv6Configuration ────────────────────────────────────────────────

IPV6_DATA = {
    "ipv6_enabled": True,
    "ipv6_firewall": False,
    "ipv6_prefix_firewall": True,
    "ipv6ll": "fe80::224:d4ff:acac:ecec",
    "delegations": [
        {"prefix": "2a01:e30:d252:a2a0::/64", "next_hop": ""},
        {"prefix": "2a01:e30:d252:a2a1::/64", "next_hop": "fe80::1"},
    ],
}


class TestConnectionIpv6Configuration:
    def test_ipv6_config_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/ipv6/config/", json=api_ok(IPV6_DATA))
        c = fb.connection.ipv6_config()
        assert isinstance(c, ConnectionIpv6Configuration)
        assert c.ipv6_enabled is True
        assert c.ipv6_firewall is False
        assert c.ipv6ll == "fe80::224:d4ff:acac:ecec"
        assert len(c.delegations) == 2
        assert isinstance(c.delegations[0], ConnectionIpv6Delegation)
        assert c.delegations[1].next_hop == "fe80::1"

    def test_set_ipv6_config(self, fb, httpx_mock):
        updated = {**IPV6_DATA, "ipv6_firewall": True}
        httpx_mock.add_response(
            url=f"{API}/connection/ipv6/config/",
            method="PUT",
            json=api_ok(updated),
        )
        c = fb.connection.set_ipv6_config(ipv6_firewall=True)
        assert c.ipv6_firewall is True


# ── XdslInfos ──────────────────────────────────────────────────────────────────

XDSL_DATA = {
    "status": {"status": "showtime", "protocol": "adsl2plus_a", "uptime": 5017, "modulation": "adsl"},
    "down": {"maxrate": 30636, "rate": 28031, "snr": 7, "attn": 0, "es": 43, "ses": 43,
             "phyr": True, "ginp": False, "nitro": True, "fec": 0, "crc": 0, "hec": 0,
             "rxmt": 0, "rxmt_corr": 0, "rxmt_uncorr": 0},
    "up":   {"maxrate": 1022, "rate": 1022, "snr": 15, "attn": 23, "es": 0, "ses": 0,
             "phyr": False, "ginp": False, "nitro": True, "fec": 0, "crc": 0, "hec": 0},
}


class TestXdsl:
    def test_xdsl_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/xdsl/", json=api_ok(XDSL_DATA))
        x = fb.connection.xdsl()
        assert isinstance(x, XdslInfos)
        assert x.status.status == "showtime"
        assert x.status.protocol == "adsl2plus_a"
        assert x.status.uptime == 5017
        assert x.down.rate == 28031
        assert x.down.phyr is True
        assert x.up.snr == 15
        assert x.up.maxrate == 1022


# ── FtthStatus ─────────────────────────────────────────────────────────────────

FTTH_DATA = {
    "sfp_present": True,
    "sfp_alim_ok": True,
    "sfp_has_power_report": True,
    "sfp_has_signal": False,
    "link": False,
    "sfp_serial": "DE104900000471",
    "sfp_model": "SPBD-1250E4H2RDB",
    "sfp_vendor": "DELTA",
    "sfp_pwr_tx": -1172,
    "sfp_pwr_rx": -3698,
}


class TestFtth:
    def test_ftth_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/ftth/", json=api_ok(FTTH_DATA))
        f = fb.connection.ftth()
        assert isinstance(f, FtthStatus)
        assert f.sfp_present is True
        assert f.link is False
        assert f.sfp_model == "SPBD-1250E4H2RDB"
        assert f.sfp_pwr_tx == -1172


# ── LTE ───────────────────────────────────────────────────────────────────────

LTE_DATA = {
    "enabled": True,
    "state": "connected",
    "fsm_state": "poll_network",
    "radio": {
        "associated": True,
        "plmn": 20801,
        "signal_level": 4,
        "gcid": "abcdef123456",
        "ue_active": False,
        "bands": [
            {"band": 3, "enabled": True, "bandwidth": 20, "rsrq": -10,
             "rsrp": -90, "rssi": -70, "pci": 42},
        ],
    },
    "network": {
        "pdn_up": True,
        "has_ipv4": False,
        "has_ipv6": True,
        "ipv4": "0.0.0.0",
        "ipv4_netmask": "0.0.0.0",
        "ipv4_dns": "0.0.0.0",
        "ipv6": "2a2a:e0e:beeb:eded::1",
        "ipv6_netmask": "ffff:ffff:ffff:ffff::",
        "ipv6_dns": "2a2a::1",
    },
    "sim": {
        "present": True,
        "pin_locked": False,
        "puk_locked": False,
        "iccid": "1234567890123456789",
        "pin_remaining": 3,
        "puk_remaining": 10,
    },
}

AGGREGATION_DATA = {
    "enabled": True,
    "tunnel": {
        "lte":  {"connected": True,  "last_error": "no_error",
                 "tx_flows_rate": 0, "tx_max_rate": 0, "tx_used_rate": 0,
                 "rx_flows_rate": 0, "rx_max_rate": 0, "rx_used_rate": 0},
        "xdsl": {"connected": True,  "last_error": "no_error",
                 "tx_flows_rate": 0, "tx_max_rate": 4_428_750, "tx_used_rate": 134,
                 "rx_flows_rate": 0, "rx_max_rate": 12_502_000, "rx_used_rate": 120},
    },
}


class TestLte:
    def test_lte_backup_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/lte/backup", json=api_ok(LTE_DATA))
        lte = fb.connection.lte("backup")
        assert isinstance(lte, LteConfiguration)
        assert lte.enabled is True
        assert lte.state == "connected"
        assert lte.radio.associated is True
        assert lte.radio.plmn == 20801
        assert lte.radio.signal_level == 4
        assert len(lte.radio.bands) == 1
        assert lte.radio.bands[0].band == 3
        assert lte.radio.bands[0].rsrp == -90
        assert lte.network.pdn_up is True
        assert lte.network.has_ipv6 is True
        assert lte.network.ipv6 == "2a2a:e0e:beeb:eded::1"
        assert lte.sim.present is True
        assert lte.sim.iccid == "1234567890123456789"

    def test_lte_aggregation_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/lte/aggregation", json=api_ok(LTE_DATA))
        lte = fb.connection.lte("aggregation")
        assert isinstance(lte, LteConfiguration)

    def test_aggregation_status(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/connection/aggregation", json=api_ok(AGGREGATION_DATA))
        agg = fb.connection.aggregation()
        assert isinstance(agg, LteAggregation)
        assert agg.enabled is True
        assert agg.tunnel.lte.connected is True
        assert agg.tunnel.xdsl.rx_max_rate == 12_502_000
        assert agg.tunnel.xdsl.tx_used_rate == 134

    def test_set_aggregation(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/connection/aggregation",
            method="PUT",
            json=api_ok({**AGGREGATION_DATA, "enabled": False}),
        )
        agg = fb.connection.set_aggregation(enabled=False)
        assert agg.enabled is False
        req = httpx_mock.get_requests()[-1]
        import json
        assert json.loads(req.content) == {"enabled": False}


# ── DynDNS ─────────────────────────────────────────────────────────────────────

class TestDDNS:
    def test_ddns_status(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/connection/ddns/dyndns/status/",
            json=api_ok({"status": "ok", "next_refresh": 1234, "last_refresh": 1000,
                         "next_retry": 0, "last_error": 0}),
        )
        s = fb.connection.ddns_status("dyndns")
        assert isinstance(s, DDNSStatus)
        assert s.status == "ok"
        assert s.next_refresh == 1234

    def test_ddns_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/connection/ddns/noip/",
            json=api_ok({"enabled": True, "hostname": "myhost.noip.me", "user": "me"}),
        )
        c = fb.connection.ddns_config("noip")
        assert isinstance(c, DDNSConfig)
        assert c.hostname == "myhost.noip.me"
        assert c.user == "me"

    def test_set_ddns_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/connection/ddns/noip/",
            method="PUT",
            json=api_ok({"enabled": False, "hostname": "myhost.noip.me", "user": "me"}),
        )
        c = fb.connection.set_ddns_config("noip", enabled=False, password="secret")
        assert c.enabled is False
        req = httpx_mock.get_requests()[-1]
        import json
        body = json.loads(req.content)
        assert body == {"enabled": False, "password": "secret"}
