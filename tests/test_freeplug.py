"""Unit tests for the Freeplug (CPL) API."""
import pytest

from freebox import Freebox, Freeplug, FreeplugNetwork, FreeplugNode
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

NODE_STA = {
    "id": "00:24:D4:36:4C:CF",
    "net_id": "c8:f7:b9:83:f5:10:01",
    "net_role": "sta",
    "model": "int6400",
    "local": True,
    "has_network": True,
    "eth_port_status": "up",
    "eth_full_duplex": True,
    "eth_speed": 100,
    "inactive": 1,
    "rx_rate": 148,
    "tx_rate": 148,
}

NODE_CCO = {
    "id": "00:24:D4:1B:15:D0",
    "net_id": "c8:f7:b9:83:f5:10:01",
    "net_role": "cco",
    "model": "int6400",
    "local": False,
    "has_network": True,
    "eth_port_status": "up",
    "eth_full_duplex": True,
    "eth_speed": 100,
    "inactive": 1,
    "rx_rate": -1,
    "tx_rate": -1,
}

NETWORK_DATA = {
    "id": "c8:f7:b9:83:f5:10:01",
    "members": [NODE_STA, NODE_CCO],
}


# ── FreeplugNode ───────────────────────────────────────────────────────────────

class TestFreeplugNode:
    def test_from_dict_sta(self):
        n = FreeplugNode._from_dict(NODE_STA)
        assert n.id == "00:24:D4:36:4C:CF"
        assert n.net_id == "c8:f7:b9:83:f5:10:01"
        assert n.net_role == "sta"
        assert n.model == "int6400"
        assert n.local is True
        assert n.has_network is True
        assert n.eth_port_status == "up"
        assert n.eth_full_duplex is True
        assert n.eth_speed == 100
        assert n.inactive == 1
        assert n.rx_rate == 148
        assert n.tx_rate == 148

    def test_from_dict_cco_no_rate(self):
        n = FreeplugNode._from_dict(NODE_CCO)
        assert n.net_role == "cco"
        assert n.local is False
        assert n.rx_rate == -1
        assert n.tx_rate == -1


# ── FreeplugNetwork ────────────────────────────────────────────────────────────

class TestFreeplugNetwork:
    def test_from_dict(self):
        net = FreeplugNetwork._from_dict(NETWORK_DATA)
        assert net.id == "c8:f7:b9:83:f5:10:01"
        assert len(net.members) == 2
        assert all(isinstance(m, FreeplugNode) for m in net.members)

    def test_networks(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/freeplug/", json=api_ok([NETWORK_DATA]))
        nets = fb.freeplug.networks()
        assert len(nets) == 1
        assert isinstance(nets[0], FreeplugNetwork)
        assert nets[0].id == "c8:f7:b9:83:f5:10:01"
        assert len(nets[0].members) == 2

    def test_networks_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/freeplug/", json=api_ok([]))
        assert fb.freeplug.networks() == []

    def test_networks_null(self, fb, httpx_mock):
        # Real Freebox returns null when no Freeplug hardware is present
        httpx_mock.add_response(url=f"{API}/freeplug/", json=api_ok(None))
        assert fb.freeplug.networks() == []

    def test_node(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/freeplug/00:24:D4:36:4C:CF/", json=api_ok(NODE_STA)
        )
        n = fb.freeplug.node("00:24:D4:36:4C:CF")
        assert isinstance(n, FreeplugNode)
        assert n.id == "00:24:D4:36:4C:CF"

    def test_reset(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/freeplug/00:24:D4:36:4C:CF/reset/", method="POST", json=api_ok(None)
        )
        fb.freeplug.reset("00:24:D4:36:4C:CF")


# ── Property ───────────────────────────────────────────────────────────────────

class TestFreeplugProperty:
    def test_property(self, fb):
        assert isinstance(fb.freeplug, Freeplug)
