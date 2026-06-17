import json

import pytest

from freebox import (
    Freebox,
    LanConfig,
    LanHost,
    LanHostL2Ident,
    LanHostL3Connectivity,
    LanHostName,
    LanHostType,
    LanInterface,
    Route,
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


# ── LanConfig ──────────────────────────────────────────────────────────────────

LAN_CONFIG_DATA = {
    "ip": "192.168.1.254",
    "name": "Freebox Server",
    "name_dns": "freebox-server",
    "name_mdns": "Freebox-Server",
    "name_netbios": "Freebox_Server",
    "mode": "router",
}


class TestLanConfig:
    def test_config_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lan/config/", json=api_ok(LAN_CONFIG_DATA))
        c = fb.lan.config()
        assert isinstance(c, LanConfig)
        assert c.ip == "192.168.1.254"
        assert c.name == "Freebox Server"
        assert c.name_dns == "freebox-server"
        assert c.name_mdns == "Freebox-Server"
        assert c.name_netbios == "Freebox_Server"
        assert c.mode == "router"

    def test_set_config(self, fb, httpx_mock):
        updated = {**LAN_CONFIG_DATA, "ip": "192.168.69.254", "name": "Freebox Custom"}
        httpx_mock.add_response(url=f"{API}/lan/config/", method="PUT", json=api_ok(updated))
        c = fb.lan.set_config(ip="192.168.69.254", name="Freebox Custom")
        assert c.ip == "192.168.69.254"
        assert c.name == "Freebox Custom"
        req = httpx_mock.get_requests()[-1]
        body = json.loads(req.content)
        assert body == {"ip": "192.168.69.254", "name": "Freebox Custom"}


# ── Routes ─────────────────────────────────────────────────────────────────────

ROUTES_DATA = [
    {"prefix": "192.168.42.0/24", "gateway": "192.168.1.38", "enabled": True, "description": "VPN"},
    {"prefix": "192.168.24.240/28", "gateway": "192.168.1.38", "enabled": False, "description": ""},
]


class TestRoutes:
    def test_routes_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lan/routes", json=api_ok(ROUTES_DATA))
        routes = fb.lan.routes()
        assert len(routes) == 2
        assert isinstance(routes[0], Route)
        assert routes[0].prefix == "192.168.42.0/24"
        assert routes[0].gateway == "192.168.1.38"
        assert routes[0].enabled is True
        assert routes[0].description == "VPN"
        assert routes[1].enabled is False

    def test_set_routes(self, fb, httpx_mock):
        new_routes = [
            Route(prefix="192.168.42.0/24", gateway="192.168.1.38", enabled=True, description="Only route"),
        ]
        httpx_mock.add_response(
            url=f"{API}/lan/routes/",
            method="PUT",
            json=api_ok([{"prefix": "192.168.42.0/24", "gateway": "192.168.1.38",
                          "enabled": True, "description": "Only route"}]),
        )
        result = fb.lan.set_routes(new_routes)
        assert len(result) == 1
        assert result[0].description == "Only route"
        req = httpx_mock.get_requests()[-1]
        body = json.loads(req.content)
        assert body == [{"prefix": "192.168.42.0/24", "gateway": "192.168.1.38",
                         "enabled": True, "description": "Only route"}]


# ── LAN Browser ────────────────────────────────────────────────────────────────

INTERFACES_DATA = [{"name": "pub", "host_count": 3}]

HOST_DATA = {
    "id": "ether-d0:23:db:36:15:aa",
    "primary_name": "iPhone r0ro",
    "primary_name_manual": True,
    "host_type": "smartphone",
    "persistent": True,
    "reachable": True,
    "active": True,
    "last_time_reachable": 1360669498,
    "last_activity": 1360669498,
    "first_activity": 1360000000,
    "vendor_name": "Apple, Inc.",
    "domain_name": "iphone-r0ro",
    "l2ident": {"id": "d0:23:db:36:15:aa", "type": "mac_address"},
    "names": [{"name": "iPhone-r0ro", "source": "dhcp"}],
    "l3connectivities": [
        {
            "addr": "192.168.1.20",
            "af": "ipv4",
            "active": True,
            "reachable": True,
            "last_activity": 1360669498,
            "last_time_reachable": 1360669498,
        }
    ],
    "info": {},
}

HOST_DATA_2 = {
    "id": "ether-00:24:d4:7e:00:4c",
    "primary_name": "Freebox Player",
    "primary_name_manual": False,
    "host_type": "freebox_player",
    "persistent": False,
    "reachable": True,
    "active": True,
    "last_time_reachable": 1360669491,
    "last_activity": 1360669491,
    "vendor_name": "FREEBOX SA",
    "domain_name": "",
    "l2ident": {"id": "00:24:d4:7e:00:4c", "type": "mac_address"},
    "names": [{"name": "Freebox Player", "source": "dhcp"}],
    "l3connectivities": [
        {"addr": "192.168.1.30", "af": "ipv4", "active": True, "reachable": True,
         "last_activity": 1360669491, "last_time_reachable": 1360669491}
    ],
    "info": {},
}

HOST_TYPES_DATA = [
    {"icon": "/resources/images/lan/ic_device_computer.png", "type": "workstation",
     "name": "Ordinateur", "category": "personal_device"},
    {"icon": "/resources/images/lan/ic_device_printer.png", "type": "printer",
     "name": "Imprimante", "category": "network"},
]


class TestLanBrowser:
    def test_interfaces(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lan/browser/interfaces/", json=api_ok(INTERFACES_DATA))
        ifaces = fb.lan.interfaces()
        assert len(ifaces) == 1
        assert isinstance(ifaces[0], LanInterface)
        assert ifaces[0].name == "pub"
        assert ifaces[0].host_count == 3

    def test_hosts(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/lan/browser/pub/",
            json=api_ok([HOST_DATA, HOST_DATA_2]),
        )
        hosts = fb.lan.hosts("pub")
        assert len(hosts) == 2
        assert isinstance(hosts[0], LanHost)
        assert hosts[0].id == "ether-d0:23:db:36:15:aa"
        assert hosts[0].primary_name == "iPhone r0ro"
        assert hosts[0].primary_name_manual is True
        assert hosts[0].reachable is True
        assert hosts[0].vendor_name == "Apple, Inc."
        assert len(hosts[0].l2ident) == 1
        assert isinstance(hosts[0].l2ident[0], LanHostL2Ident)
        assert hosts[0].l2ident[0].id == "d0:23:db:36:15:aa"
        assert hosts[0].l2ident[0].type == "mac_address"
        assert len(hosts[0].names) == 1
        assert isinstance(hosts[0].names[0], LanHostName)
        assert hosts[0].names[0].name == "iPhone-r0ro"
        assert hosts[0].names[0].source == "dhcp"
        assert len(hosts[0].l3connectivities) == 1
        assert isinstance(hosts[0].l3connectivities[0], LanHostL3Connectivity)
        assert hosts[0].l3connectivities[0].addr == "192.168.1.20"
        assert hosts[0].l3connectivities[0].af == "ipv4"
        assert hosts[0].first_activity == 1360000000

    def test_host(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/lan/browser/pub/ether-00:24:d4:7e:00:4c/",
            json=api_ok(HOST_DATA_2),
        )
        h = fb.lan.host("pub", "ether-00:24:d4:7e:00:4c")
        assert isinstance(h, LanHost)
        assert h.id == "ether-00:24:d4:7e:00:4c"
        assert h.primary_name == "Freebox Player"
        assert h.host_type == "freebox_player"
        assert h.domain_name == ""

    def test_set_host(self, fb, httpx_mock):
        updated = {**HOST_DATA_2, "primary_name": "Freebox TV", "primary_name_manual": True}
        httpx_mock.add_response(
            url=f"{API}/lan/browser/pub/ether-00:24:d4:7e:00:4c/",
            method="PUT",
            json=api_ok(updated),
        )
        h = fb.lan.set_host("pub", "ether-00:24:d4:7e:00:4c", primary_name="Freebox TV")
        assert h.primary_name == "Freebox TV"
        assert h.primary_name_manual is True
        req = httpx_mock.get_requests()[-1]
        body = json.loads(req.content)
        assert body == {"primary_name": "Freebox TV"}

    def test_host_types(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lan/browser/types/", json=api_ok(HOST_TYPES_DATA))
        types = fb.lan.host_types()
        assert len(types) == 2
        assert isinstance(types[0], LanHostType)
        assert types[0].type == "workstation"
        assert types[0].category == "personal_device"
        assert types[1].type == "printer"


# ── Wake on LAN ────────────────────────────────────────────────────────────────

class TestWakeOnLan:
    def test_wake_on_lan(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lan/wol/pub/", method="POST", json={"success": True})
        fb.lan.wake_on_lan("pub", "00:24:d4:7e:00:4c")
        req = httpx_mock.get_requests()[-1]
        body = json.loads(req.content)
        assert body == {"mac": "00:24:d4:7e:00:4c", "password": ""}

    def test_wake_on_lan_with_password(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/lan/wol/pub/", method="POST", json={"success": True})
        fb.lan.wake_on_lan("pub", "00:24:d4:7e:00:4c", password="secret")
        req = httpx_mock.get_requests()[-1]
        body = json.loads(req.content)
        assert body == {"mac": "00:24:d4:7e:00:4c", "password": "secret"}
