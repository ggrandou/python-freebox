"""Unit tests for the Firewall API."""
import pytest

from freebox import DmzConfig, Firewall, Freebox, IncomingPort, PortForwarding
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


# ── Test data ──────────────────────────────────────────────────────────────────

DMZ_DATA = {"enabled": False, "ip": ""}

DMZ_DATA_ENABLED = {"enabled": True, "ip": "192.168.1.42"}

REDIR_1 = {
    "id": 1,
    "enabled": True,
    "ip_proto": "tcp",
    "wan_port_start": 69,
    "wan_port_end": 69,
    "lan_ip": "192.168.1.22",
    "lan_port": 69,
    "src_ip": "8.8.8.8",
    "comment": "",
    "hostname": "android-c5fe44a2c27be1e2",
    "host": None,
}

REDIR_2 = {
    "id": 2,
    "enabled": True,
    "ip_proto": "udp",
    "wan_port_start": 1337,
    "wan_port_end": 1340,
    "lan_ip": "192.168.1.22",
    "lan_port": 1337,
    "src_ip": "0.0.0.0",
    "comment": "",
    "hostname": "android-c5fe44a2c27be1e2",
    "host": None,
}

INCOMING_HTTP = {
    "id": "http",
    "enabled": False,
    "active": False,
    "type": "tcp",
    "in_port": 80,
    "min_port": 0,
    "max_port": 65535,
    "netns": "init",
    "readonly": False,
}

INCOMING_BT = {
    "id": "bittorrent-main",
    "enabled": True,
    "active": True,
    "type": "tcp",
    "in_port": 17591,
    "min_port": 0,
    "max_port": 65535,
    "netns": "vpn",
    "readonly": False,
}


# ── DmzConfig ─────────────────────────────────────────────────────────────────

class TestDmzConfig:
    def test_from_dict_disabled(self):
        d = DmzConfig._from_dict(DMZ_DATA)
        assert d.enabled is False
        assert d.ip == ""

    def test_from_dict_enabled(self):
        d = DmzConfig._from_dict(DMZ_DATA_ENABLED)
        assert d.enabled is True
        assert d.ip == "192.168.1.42"

    def test_dmz_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/fw/dmz/", json=api_ok(DMZ_DATA))
        d = fb.firewall.dmz()
        assert isinstance(d, DmzConfig)
        assert d.enabled is False
        assert d.ip == ""

    def test_dmz_set(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/fw/dmz/", method="PUT", json=api_ok(DMZ_DATA_ENABLED))
        d = fb.firewall.set_dmz(enabled=True, ip="192.168.1.42")
        assert isinstance(d, DmzConfig)
        assert d.enabled is True
        assert d.ip == "192.168.1.42"


# ── PortForwarding ─────────────────────────────────────────────────────────────

class TestPortForwarding:
    def test_from_dict(self):
        pf = PortForwarding._from_dict(REDIR_1)
        assert pf.id == 1
        assert pf.enabled is True
        assert pf.ip_proto == "tcp"
        assert pf.wan_port_start == 69
        assert pf.wan_port_end == 69
        assert pf.lan_ip == "192.168.1.22"
        assert pf.lan_port == 69
        assert pf.src_ip == "8.8.8.8"
        assert pf.comment == ""
        assert pf.hostname == "android-c5fe44a2c27be1e2"

    def test_list(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/fw/redir/", json=api_ok([REDIR_1, REDIR_2]))
        rules = fb.firewall.port_forwardings()
        assert len(rules) == 2
        assert all(isinstance(r, PortForwarding) for r in rules)
        assert rules[0].id == 1
        assert rules[1].id == 2
        assert rules[1].ip_proto == "udp"

    def test_get_one(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/fw/redir/1", json=api_ok(REDIR_1))
        pf = fb.firewall.port_forwarding(1)
        assert isinstance(pf, PortForwarding)
        assert pf.id == 1

    def test_add(self, fb, httpx_mock):
        new_redir = {**REDIR_1, "id": 3, "lan_port": 4242, "wan_port_start": 4242, "wan_port_end": 4242}
        httpx_mock.add_response(url=f"{API}/fw/redir/", method="POST", json=api_ok(new_redir))
        pf = fb.firewall.add_port_forwarding(
            ip_proto="tcp",
            wan_port_start=4242,
            wan_port_end=4242,
            lan_ip="192.168.1.22",
            lan_port=4242,
        )
        assert isinstance(pf, PortForwarding)
        assert pf.id == 3

    def test_update(self, fb, httpx_mock):
        updated = {**REDIR_1, "enabled": False}
        httpx_mock.add_response(url=f"{API}/fw/redir/1", method="PUT", json=api_ok(updated))
        pf = fb.firewall.set_port_forwarding(1, enabled=False)
        assert isinstance(pf, PortForwarding)
        assert pf.enabled is False

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/fw/redir/1", method="DELETE", json=api_ok(None))
        fb.firewall.delete_port_forwarding(1)


# ── IncomingPort ───────────────────────────────────────────────────────────────

class TestIncomingPort:
    def test_from_dict(self):
        p = IncomingPort._from_dict(INCOMING_BT)
        assert p.id == "bittorrent-main"
        assert p.enabled is True
        assert p.active is True
        assert p.type == "tcp"
        assert p.in_port == 17591
        assert p.min_port == 0
        assert p.max_port == 65535
        assert p.netns == "vpn"
        assert p.readonly is False

    def test_list(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/fw/incoming/", json=api_ok([INCOMING_HTTP, INCOMING_BT]))
        ports = fb.firewall.incoming_ports()
        assert len(ports) == 2
        assert all(isinstance(p, IncomingPort) for p in ports)
        assert ports[0].id == "http"
        assert ports[1].id == "bittorrent-main"

    def test_get_one(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/fw/incoming/bittorrent-main", json=api_ok(INCOMING_BT))
        p = fb.firewall.incoming_port("bittorrent-main")
        assert isinstance(p, IncomingPort)
        assert p.id == "bittorrent-main"

    def test_update(self, fb, httpx_mock):
        updated = {**INCOMING_BT, "in_port": 3615}
        httpx_mock.add_response(
            url=f"{API}/fw/incoming/bittorrent-main", method="PUT", json=api_ok(updated)
        )
        p = fb.firewall.set_incoming_port("bittorrent-main", in_port=3615)
        assert isinstance(p, IncomingPort)
        assert p.in_port == 3615


# ── Firewall property on Freebox ───────────────────────────────────────────────

class TestFirewallProperty:
    def test_firewall_property_returns_firewall(self, fb):
        assert isinstance(fb.firewall, Firewall)
