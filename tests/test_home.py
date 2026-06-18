"""Unit tests for the Home Automation API."""
import pytest

from freebox import (
    Freebox,
    Home,
    HomeAdapter,
    HomeAdapterType,
    HomeEndpointValue,
    HomeNode,
    HomeNodeEndpoint,
    HomeNodeEndpointUi,
    HomeNodeGroup,
    HomeNodeType,
    HomePairingStep,
    HomePairingStepField,
    HomeTile,
    HomeTileData,
)
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"


# ── Fixture ────────────────────────────────────────────────────────────────────

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
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"home": True}}),
    )
    client = Freebox(
        app_id=APP_ID, app_name=APP_NAME, app_version=APP_VERSION,
        device_name=DEVICE_NAME, token_file=token_file,
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Sample data ────────────────────────────────────────────────────────────────

ADAPTER_TYPE_DICT = {"name": "adapter::rts"}

ADAPTER_DICT = {
    "id": 2,
    "label": "Réseau Rts",
    "status": "active",
    "icon_url": "http://images.com/adapter.png",
    "type": ADAPTER_TYPE_DICT,
    "props": {"Addr": 160},
}

PAIRING_FIELD_DICT = {"widget": "label", "text": "Veuillez patienter…"}

PAIRING_STEP_DICT = {
    "pageid": 2,
    "session": 62328,
    "refresh": 1000,
    "icon_url": "/resources/images/home/pairing/wifi.png",
    "fields": [PAIRING_FIELD_DICT],
}

NODE_TYPE_DICT = {
    "name": "node::rts::shutter",
    "label": "Volet RTS",
    "icon": "shutter",
    "physical": True,
}

ENDPOINT_UI_DICT = {
    "display": "toggle",
    "access": "rw",
    "icon_url": "http://icon.png",
    "unit": "",
    "range": [],
    "icon_color": "",
    "text_color": "",
    "value_color": "",
}

ENDPOINT_DICT = {
    "id": 1,
    "ep_type": "slot",
    "category": "shutter",
    "visibility": "dashboard",
    "access": "rw",
    "label": "Ouvrir/Fermer",
    "name": "toggle",
    "value_type": "bool",
    "value": False,
    "ui": ENDPOINT_UI_DICT,
}

NODE_DICT = {
    "id": 14,
    "adapter": 2,
    "label": "Volet salon",
    "name": "node::rts::shutter",
    "category": "shutter",
    "status": "active",
    "type": NODE_TYPE_DICT,
    "show_endpoints": [ENDPOINT_DICT],
    "signal_links": [],
    "slot_links": [],
}

ENDPOINT_VALUE_DICT = {
    "value": False,
    "value_type": "bool",
    "unit": "",
    "refresh": 0,
}

NODE_GROUP_DICT = {"label": "Salon", "icon_url": "http://icon.png"}

TILE_DATA_DICT = {
    "ep_id": 1,
    "label": "Alarme",
    "value_type": "bool",
    "value": False,
    "refresh": 0,
    "ui": ENDPOINT_UI_DICT,
}

TILE_DICT = {
    "node_id": 14,
    "label": "Volet salon",
    "action": "store",
    "type": "action",
    "group": NODE_GROUP_DICT,
    "data": [TILE_DATA_DICT],
}


# ── HomeAdapterType ────────────────────────────────────────────────────────────

class TestHomeAdapterType:
    def test_fields(self):
        t = HomeAdapterType._from_dict(ADAPTER_TYPE_DICT)
        assert t.name == "adapter::rts"

    def test_defaults(self):
        t = HomeAdapterType._from_dict({})
        assert t.name == ""


# ── HomeAdapter ────────────────────────────────────────────────────────────────

class TestHomeAdapter:
    def test_fields(self):
        a = HomeAdapter._from_dict(ADAPTER_DICT)
        assert a.id == 2
        assert a.label == "Réseau Rts"
        assert a.status == "active"
        assert a.icon_url == "http://images.com/adapter.png"
        assert isinstance(a.type, HomeAdapterType)
        assert a.type.name == "adapter::rts"
        assert a.props == {"Addr": 160}

    def test_no_type(self):
        a = HomeAdapter._from_dict({"id": 1, "label": "cam", "status": "active"})
        assert a.type is None
        assert a.props == {}

    def test_defaults(self):
        a = HomeAdapter._from_dict({})
        assert a.id == 0
        assert a.label == ""
        assert a.props == {}


# ── HomePairingStepField ───────────────────────────────────────────────────────

class TestHomePairingStepField:
    def test_fields(self):
        f = HomePairingStepField._from_dict(PAIRING_FIELD_DICT)
        assert f.widget == "label"
        assert f.text == "Veuillez patienter…"

    def test_defaults(self):
        f = HomePairingStepField._from_dict({})
        assert f.widget == ""
        assert f.text == ""


# ── HomePairingStep ────────────────────────────────────────────────────────────

class TestHomePairingStep:
    def test_fields(self):
        s = HomePairingStep._from_dict(PAIRING_STEP_DICT)
        assert s.pageid == 2
        assert s.session == 62328
        assert s.refresh == 1000
        assert s.icon_url == "/resources/images/home/pairing/wifi.png"
        assert len(s.fields) == 1
        assert s.fields[0].widget == "label"

    def test_defaults(self):
        s = HomePairingStep._from_dict({})
        assert s.pageid == 0
        assert s.fields == []


# ── HomeNodeType ───────────────────────────────────────────────────────────────

class TestHomeNodeType:
    def test_fields(self):
        t = HomeNodeType._from_dict(NODE_TYPE_DICT)
        assert t.name == "node::rts::shutter"
        assert t.label == "Volet RTS"
        assert t.icon == "shutter"
        assert t.physical is True

    def test_defaults(self):
        t = HomeNodeType._from_dict({})
        assert t.name == ""
        assert t.physical is False


# ── HomeNodeEndpointUi ─────────────────────────────────────────────────────────

class TestHomeNodeEndpointUi:
    def test_fields(self):
        u = HomeNodeEndpointUi._from_dict(ENDPOINT_UI_DICT)
        assert u.display == "toggle"
        assert u.access == "rw"
        assert u.icon_url == "http://icon.png"
        assert u.range == []

    def test_defaults(self):
        u = HomeNodeEndpointUi._from_dict({})
        assert u.display == ""
        assert u.access == ""
        assert u.range == []
        assert u.icon_color_range == []


# ── HomeNodeEndpoint ───────────────────────────────────────────────────────────

class TestHomeNodeEndpoint:
    def test_fields(self):
        e = HomeNodeEndpoint._from_dict(ENDPOINT_DICT)
        assert e.id == 1
        assert e.ep_type == "slot"
        assert e.category == "shutter"
        assert e.visibility == "dashboard"
        assert e.access == "rw"
        assert e.label == "Ouvrir/Fermer"
        assert e.name == "toggle"
        assert e.value_type == "bool"
        assert e.value is False
        assert isinstance(e.ui, HomeNodeEndpointUi)
        assert e.ui.display == "toggle"

    def test_no_ui(self):
        e = HomeNodeEndpoint._from_dict({"id": 0, "ep_type": "signal"})
        assert e.ui is None

    def test_defaults(self):
        e = HomeNodeEndpoint._from_dict({})
        assert e.id == 0
        assert e.value is None


# ── HomeNode ───────────────────────────────────────────────────────────────────

class TestHomeNode:
    def test_fields(self):
        n = HomeNode._from_dict(NODE_DICT)
        assert n.id == 14
        assert n.adapter == 2
        assert n.label == "Volet salon"
        assert n.name == "node::rts::shutter"
        assert n.status == "active"
        assert isinstance(n.type, HomeNodeType)
        assert n.type.name == "node::rts::shutter"
        assert len(n.show_endpoints) == 1
        assert n.show_endpoints[0].id == 1
        assert n.signal_links == []
        assert n.slot_links == []

    def test_no_type(self):
        n = HomeNode._from_dict({"id": 1})
        assert n.type is None
        assert n.show_endpoints == []

    def test_defaults(self):
        n = HomeNode._from_dict({})
        assert n.id == 0
        assert n.label == ""


# ── HomeEndpointValue ──────────────────────────────────────────────────────────

class TestHomeEndpointValue:
    def test_bool(self):
        v = HomeEndpointValue._from_dict(ENDPOINT_VALUE_DICT)
        assert v.value is False
        assert v.value_type == "bool"
        assert v.unit == ""
        assert v.refresh == 0

    def test_int(self):
        v = HomeEndpointValue._from_dict({"value": 42, "value_type": "int"})
        assert v.value == 42
        assert v.value_type == "int"

    def test_null(self):
        v = HomeEndpointValue._from_dict({"value": None, "value_type": "void"})
        assert v.value is None
        assert v.value_type == "void"

    def test_defaults(self):
        v = HomeEndpointValue._from_dict({})
        assert v.value is None
        assert v.value_type == ""


# ── HomeNodeGroup / HomeTileData / HomeTile ───────────────────────────────────

class TestHomeNodeGroup:
    def test_fields(self):
        g = HomeNodeGroup._from_dict(NODE_GROUP_DICT)
        assert g.label == "Salon"
        assert g.icon_url == "http://icon.png"

    def test_defaults(self):
        g = HomeNodeGroup._from_dict({})
        assert g.label == ""


class TestHomeTileData:
    def test_fields(self):
        d = HomeTileData._from_dict(TILE_DATA_DICT)
        assert d.ep_id == 1
        assert d.label == "Alarme"
        assert d.value_type == "bool"
        assert d.value is False
        assert d.refresh == 0
        assert isinstance(d.ui, HomeNodeEndpointUi)

    def test_no_ui(self):
        d = HomeTileData._from_dict({"ep_id": 0})
        assert d.ui is None

    def test_defaults(self):
        d = HomeTileData._from_dict({})
        assert d.ep_id == 0
        assert d.value is None


class TestHomeTile:
    def test_fields(self):
        t = HomeTile._from_dict(TILE_DICT)
        assert t.node_id == 14
        assert t.label == "Volet salon"
        assert t.action == "store"
        assert t.type == "action"
        assert isinstance(t.group, HomeNodeGroup)
        assert t.group.label == "Salon"
        assert len(t.data) == 1
        assert t.data[0].ep_id == 1

    def test_no_group(self):
        t = HomeTile._from_dict({"node_id": 1})
        assert t.group is None
        assert t.data == []

    def test_defaults(self):
        t = HomeTile._from_dict({})
        assert t.node_id == 0
        assert t.label == ""


# ── API methods ────────────────────────────────────────────────────────────────

class TestHome:
    def test_home_property(self, fb):
        assert isinstance(fb.home, Home)

    def test_adapters(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/adapters", json=api_ok([ADAPTER_DICT]))
        adapters = fb.home.adapters()
        assert len(adapters) == 1
        assert isinstance(adapters[0], HomeAdapter)
        assert adapters[0].label == "Réseau Rts"

    def test_adapters_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/adapters", json=api_ok([]))
        assert fb.home.adapters() == []

    def test_adapter(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/adapters/2", json=api_ok(ADAPTER_DICT))
        a = fb.home.adapter(2)
        assert isinstance(a, HomeAdapter)
        assert a.id == 2

    def test_set_adapter(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/adapters/2", method="PUT", json={"success": True}
        )
        fb.home.set_adapter(2, status="disabled")
        assert httpx_mock.get_requests()[-1].method == "PUT"

    def test_pairing_step(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/pairing/2", json=api_ok(PAIRING_STEP_DICT))
        step = fb.home.pairing_step(2)
        assert isinstance(step, HomePairingStep)
        assert step.session == 62328

    def test_start_pairing(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/pairing/2", method="POST", json={"success": True}
        )
        fb.home.start_pairing(2)
        assert httpx_mock.get_requests()[-1].method == "POST"

    def test_start_pairing_with_type(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/pairing/2", method="POST", json={"success": True}
        )
        fb.home.start_pairing(2, type="node::domus::sercomm::pir")

    def test_next_pairing_step(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/pairing/2", method="POST", json=api_ok(PAIRING_STEP_DICT)
        )
        step = fb.home.next_pairing_step(2, session=62328, pageid=2, fields=[None, True])
        assert isinstance(step, HomePairingStep)
        assert step.pageid == 2

    def test_stop_pairing(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/pairing/2", method="POST", json={"success": True}
        )
        fb.home.stop_pairing(2, session=62328)

    def test_nodes(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/nodes", json=api_ok([NODE_DICT]))
        nodes = fb.home.nodes()
        assert len(nodes) == 1
        assert isinstance(nodes[0], HomeNode)
        assert nodes[0].label == "Volet salon"

    def test_nodes_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/nodes", json=api_ok([]))
        assert fb.home.nodes() == []

    def test_node(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/nodes/14", json=api_ok(NODE_DICT))
        n = fb.home.node(14)
        assert isinstance(n, HomeNode)
        assert n.id == 14

    def test_set_node(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/nodes/14", method="PUT", json={"success": True}
        )
        fb.home.set_node(14, "Volet chambre")
        assert httpx_mock.get_requests()[-1].method == "PUT"

    def test_delete_node(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/nodes/14", method="DELETE", json={"success": True}
        )
        fb.home.delete_node(14)
        assert httpx_mock.get_requests()[-1].method == "DELETE"

    def test_endpoint_value(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/endpoints/14/1", json=api_ok(ENDPOINT_VALUE_DICT)
        )
        v = fb.home.endpoint_value(14, 1)
        assert isinstance(v, HomeEndpointValue)
        assert v.value is False
        assert v.value_type == "bool"

    def test_set_endpoint_value(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/home/endpoints/14/1", method="PUT", json={"success": True}
        )
        fb.home.set_endpoint_value(14, 1, True)
        assert httpx_mock.get_requests()[-1].method == "PUT"

    def test_tileset(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/tileset/all", json=api_ok([TILE_DICT]))
        tiles = fb.home.tileset()
        assert len(tiles) == 1
        assert isinstance(tiles[0], HomeTile)
        assert tiles[0].node_id == 14

    def test_tileset_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/tileset/all", json=api_ok([]))
        assert fb.home.tileset() == []

    def test_node_tileset(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/home/tileset/14", json=api_ok([TILE_DICT]))
        tiles = fb.home.node_tileset(14)
        assert len(tiles) == 1
        assert isinstance(tiles[0], HomeTile)
