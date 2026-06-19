import json

import pytest

from freebox import (
    Dhcp,
    DhcpConfig,
    DhcpDynamicLease,
    DhcpOption,
    DhcpStaticLease,
    Freebox,
)
from freebox.dhcp import _decode_domain_search, _encode_domain_search
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


# ── DhcpOption type conversion ────────────────────────────────────────────────

class TestDhcpOptionTypes:
    # bool
    def test_bool_true(self):
        opt = DhcpOption._from_dict({"id": "ip_fwd", "val": "true"})
        assert opt.val is True
        assert isinstance(opt.val, bool)

    def test_bool_false(self):
        opt = DhcpOption._from_dict({"id": "ip_fwd", "val": "false"})
        assert opt.val is False

    def test_bool_one(self):
        opt = DhcpOption._from_dict({"id": "ip_fwd", "val": "1"})
        assert opt.val is True

    def test_bool_zero(self):
        opt = DhcpOption._from_dict({"id": "ip_fwd", "val": "0"})
        assert opt.val is False

    def test_bool_encode_true(self):
        opt = DhcpOption(id="ip_fwd", val=True)
        assert opt._to_dict() == {"id": "ip_fwd", "val": "true"}

    def test_bool_encode_false(self):
        opt = DhcpOption(id="ip_fwd", val=False)
        assert opt._to_dict() == {"id": "ip_fwd", "val": "false"}

    # integer (u8)
    def test_u8_decode(self):
        opt = DhcpOption._from_dict({"id": "tcp_ttl", "val": "64"})
        assert opt.val == 64
        assert isinstance(opt.val, int)

    def test_u8_encode(self):
        opt = DhcpOption(id="tcp_ttl", val=64)
        assert opt._to_dict() == {"id": "tcp_ttl", "val": "64"}

    # integer (u16)
    def test_u16_decode(self):
        opt = DhcpOption._from_dict({"id": "mtu", "val": "1500"})
        assert opt.val == 1500

    # integer (u32)
    def test_u32_decode(self):
        opt = DhcpOption._from_dict({"id": "arp_cache_timeout", "val": "3600"})
        assert opt.val == 3600

    # signed integer (s32)
    def test_s32_decode_negative(self):
        opt = DhcpOption._from_dict({"id": "time_offset", "val": "-3600"})
        assert opt.val == -3600

    def test_s32_encode_negative(self):
        opt = DhcpOption(id="time_offset", val=-3600)
        assert opt._to_dict() == {"id": "time_offset", "val": "-3600"}

    # string
    def test_string_decode(self):
        opt = DhcpOption._from_dict({"id": "hostname", "val": "my-device"})
        assert opt.val == "my-device"
        assert isinstance(opt.val, str)

    def test_string_encode(self):
        opt = DhcpOption(id="hostname", val="my-device")
        assert opt._to_dict() == {"id": "hostname", "val": "my-device"}

    # single IP (kept as str)
    def test_ip_decode(self):
        opt = DhcpOption._from_dict({"id": "rs_address", "val": "192.168.1.1"})
        assert opt.val == "192.168.1.1"
        assert isinstance(opt.val, str)

    # ip_list
    def test_ip_list_single(self):
        opt = DhcpOption._from_dict({"id": "log_server", "val": "192.168.1.38"})
        assert opt.val == ["192.168.1.38"]
        assert isinstance(opt.val, list)

    def test_ip_list_multiple(self):
        opt = DhcpOption._from_dict({"id": "ntp_server", "val": "192.168.1.38, 192.168.1.42"})
        assert opt.val == ["192.168.1.38", "192.168.1.42"]

    def test_ip_list_encode(self):
        opt = DhcpOption(id="ntp_server", val=["192.168.1.38", "192.168.1.42"])
        assert opt._to_dict() == {"id": "ntp_server", "val": "192.168.1.38, 192.168.1.42"}

    def test_ip_list_encode_single(self):
        opt = DhcpOption(id="log_server", val=["192.168.1.38"])
        assert opt._to_dict() == {"id": "log_server", "val": "192.168.1.38"}

    # hexstring (→ bytes)
    def test_hexstring_decode(self):
        opt = DhcpOption._from_dict({"id": "vendor_specific", "val": "C0A801FE"})
        assert opt.val == b"\xc0\xa8\x01\xfe"
        assert isinstance(opt.val, bytes)

    def test_hexstring_encode(self):
        opt = DhcpOption(id="vendor_specific", val=b"\xc0\xa8\x01\xfe")
        assert opt._to_dict() == {"id": "vendor_specific", "val": "C0A801FE"}

    # domain_search (hexstring RFC 3397 → list[str])
    def test_domain_search_decode(self):
        hexval = _encode_domain_search(["local", "example.com"])
        opt = DhcpOption._from_dict({"id": "domain_search", "val": hexval})
        assert opt.val == ["local", "example.com"]
        assert isinstance(opt.val, list)

    def test_domain_search_encode(self):
        opt = DhcpOption(id="domain_search", val=["local", "example.com"])
        d = opt._to_dict()
        assert d["id"] == "domain_search"
        # round-trip: decoding the encoded value gives back the original list
        assert _decode_domain_search(d["val"]) == ["local", "example.com"]

    def test_domain_search_roundtrip(self):
        domains = ["home.arpa", "local", "corp.example.com"]
        opt = DhcpOption(id="domain_search", val=domains)
        restored = DhcpOption._from_dict(opt._to_dict())
        assert restored.val == domains

    def test_domain_search_empty(self):
        opt = DhcpOption._from_dict({"id": "domain_search", "val": ""})
        assert opt.val == []

    # unknown option (kept as str)
    def test_unknown_option(self):
        opt = DhcpOption._from_dict({"id": "custom_option_99", "val": "some_value"})
        assert opt.val == "some_value"
        assert isinstance(opt.val, str)


# ── domain_search encoding details ────────────────────────────────────────────

class TestDomainSearchEncoding:
    def test_encode_single_label(self):
        assert _encode_domain_search(["local"]) == "056C6F63616C00"

    def test_encode_multi_label(self):
        # "example" (7) + "com" (3) + root
        expected = "076578616D706C65" + "03" + "636F6D" + "00"
        assert _encode_domain_search(["example.com"]) == expected

    def test_encode_multiple_domains(self):
        result = _encode_domain_search(["local", "example.com"])
        assert result.startswith("056C6F63616C00")

    def test_encode_trailing_dot(self):
        assert _encode_domain_search(["local."]) == _encode_domain_search(["local"])

    def test_encode_empty_list(self):
        assert _encode_domain_search([]) == ""

    def test_decode_single_label(self):
        assert _decode_domain_search("056C6F63616C00") == ["local"]

    def test_decode_multiple_domains(self):
        hexval = _encode_domain_search(["local", "example.com"])
        assert _decode_domain_search(hexval) == ["local", "example.com"]

    def test_decode_lowercase_hex(self):
        assert _decode_domain_search("056c6f63616c00") == ["local"]

    def test_decode_compression_pointer(self):
        # "example.com" at offset 0, then "sub" + pointer→offset 0
        example_com = bytes([7]) + b"example" + bytes([3]) + b"com" + bytes([0])
        sub_ptr = bytes([3]) + b"sub" + bytes([0xC0, 0x00])
        data = example_com + sub_ptr
        assert _decode_domain_search(data.hex()) == ["example.com", "sub.example.com"]

    def test_encode_label_too_long(self):
        with pytest.raises(ValueError, match="too long"):
            _encode_domain_search(["a" * 64 + ".com"])


# ── API response fixtures ──────────────────────────────────────────────────────

DHCP_CONFIG_DATA = {
    "enabled": True,
    "sticky_assign": True,
    "ip_range_start": "192.168.1.2",
    "ip_range_end": "192.168.1.50",
    "always_broadcast": False,
    "ignore_out_of_range_hint": False,
    "gateway": "192.168.1.254",
    "netmask": "255.255.255.0",
    "boot_server": "",
    "boot_file": "",
    "dns": ["192.168.1.254", "", "", "", ""],
    "options": [
        {"id": "ip_fwd", "val": "true"},
        {"id": "tcp_ttl", "val": "64"},
    ],
}

STATIC_LEASE_DATA = {
    "id": "00:DE:AD:B0:0B:55",
    "mac": "00:DE:AD:B0:0B:55",
    "ip": "192.168.1.10",
    "comment": "My PC",
    "hostname": "my-pc",
    "options": [{"id": "log_server", "val": "192.168.1.38"}],
    "host": None,
}

STATIC_LEASE_DATA_2 = {
    "id": "00:DE:AD:B0:0B:69",
    "mac": "00:DE:AD:B0:0B:69",
    "ip": "192.168.1.11",
    "comment": "",
    "hostname": "printer",
    "options": [],
    "host": None,
}

DYNAMIC_LEASE_DATA = {
    "mac": "13:37:00:00:01:03",
    "ip": "192.168.1.22",
    "hostname": "android-phone",
    "lease_remaining": 123456,
    "assign_time": 1555555555,
    "refresh_time": 1555555555,
    "is_static": False,
    "options": [{"id": "ntp_server", "val": "192.168.1.38"}],
    "host": None,
}


# ── DhcpConfig ─────────────────────────────────────────────────────────────────

class TestDhcpConfig:
    def test_config_fields(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/dhcp/config/", json=api_ok(DHCP_CONFIG_DATA))
        c = fb.dhcp.config()
        assert isinstance(c, DhcpConfig)
        assert c.enabled is True
        assert c.sticky_assign is True
        assert c.ip_range_start == "192.168.1.2"
        assert c.ip_range_end == "192.168.1.50"
        assert c.always_broadcast is False
        assert c.gateway == "192.168.1.254"
        assert c.netmask == "255.255.255.0"
        assert c.dns == ["192.168.1.254", "", "", "", ""]
        assert len(c.options) == 2
        assert isinstance(c.options[0], DhcpOption)
        assert c.options[0].id == "ip_fwd"
        assert c.options[0].val is True          # decoded bool
        assert c.options[1].id == "tcp_ttl"
        assert c.options[1].val == 64            # decoded int

    def test_set_config(self, fb, httpx_mock):
        updated = {**DHCP_CONFIG_DATA, "enabled": False}
        httpx_mock.add_response(url=f"{API}/dhcp/config/", method="PUT", json=api_ok(updated))
        c = fb.dhcp.set_config(enabled=False)
        assert c.enabled is False
        req = httpx_mock.get_requests()[-1]
        assert json.loads(req.content) == {"enabled": False}


# ── DhcpStaticLease ────────────────────────────────────────────────────────────

class TestStaticLeases:
    def test_static_leases_fields(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/dhcp/static_lease/",
            json=api_ok([STATIC_LEASE_DATA, STATIC_LEASE_DATA_2]),
        )
        leases = fb.dhcp.static_leases()
        assert len(leases) == 2
        assert isinstance(leases[0], DhcpStaticLease)
        assert leases[0].id == "00:DE:AD:B0:0B:55"
        assert leases[0].mac == "00:DE:AD:B0:0B:55"
        assert leases[0].ip == "192.168.1.10"
        assert leases[0].comment == "My PC"
        assert leases[0].hostname == "my-pc"
        assert len(leases[0].options) == 1
        assert leases[0].options[0].id == "log_server"
        assert leases[0].options[0].val == ["192.168.1.38"]  # ip_list
        assert leases[0].host is None
        assert leases[1].options == []

    def test_static_lease_by_id(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/dhcp/static_lease/00:DE:AD:B0:0B:55",
            json=api_ok(STATIC_LEASE_DATA),
        )
        lease = fb.dhcp.static_lease("00:DE:AD:B0:0B:55")
        assert isinstance(lease, DhcpStaticLease)
        assert lease.id == "00:DE:AD:B0:0B:55"
        assert lease.ip == "192.168.1.10"

    def test_add_static_lease(self, fb, httpx_mock):
        new_lease = {
            "id": "00:00:00:11:11:11",
            "mac": "00:00:00:11:11:11",
            "ip": "192.168.1.222",
            "comment": "",
            "hostname": "00:00:00:11:11:11",
            "options": [],
            "host": None,
        }
        httpx_mock.add_response(
            url=f"{API}/dhcp/static_lease/",
            method="POST",
            json=api_ok(new_lease),
        )
        lease = fb.dhcp.add_static_lease("00:00:00:11:11:11", "192.168.1.222")
        assert isinstance(lease, DhcpStaticLease)
        assert lease.mac == "00:00:00:11:11:11"
        assert lease.ip == "192.168.1.222"
        assert json.loads(httpx_mock.get_requests()[-1].content) == {
            "mac": "00:00:00:11:11:11", "ip": "192.168.1.222",
        }

    def test_set_static_lease(self, fb, httpx_mock):
        updated = {**STATIC_LEASE_DATA, "comment": "Updated"}
        httpx_mock.add_response(
            url=f"{API}/dhcp/static_lease/00:DE:AD:B0:0B:55",
            method="PUT",
            json=api_ok(updated),
        )
        lease = fb.dhcp.set_static_lease("00:DE:AD:B0:0B:55", comment="Updated")
        assert lease.comment == "Updated"
        assert json.loads(httpx_mock.get_requests()[-1].content) == {"comment": "Updated"}

    def test_delete_static_lease(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/dhcp/static_lease/00:DE:AD:B0:0B:55",
            method="DELETE",
            json={"success": True},
        )
        fb.dhcp.delete_static_lease("00:DE:AD:B0:0B:55")
        assert httpx_mock.get_requests()[-1].method == "DELETE"


# ── DhcpDynamicLease ───────────────────────────────────────────────────────────

class TestDynamicLeases:
    def test_dynamic_leases_fields(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/dhcp/dynamic_lease/",
            json=api_ok([DYNAMIC_LEASE_DATA]),
        )
        leases = fb.dhcp.dynamic_leases()
        assert len(leases) == 1
        lease = leases[0]
        assert isinstance(lease, DhcpDynamicLease)
        assert lease.mac == "13:37:00:00:01:03"
        assert lease.ip == "192.168.1.22"
        assert lease.hostname == "android-phone"
        assert lease.lease_remaining == 123456
        assert lease.assign_time == 1555555555
        assert lease.is_static is False
        assert len(lease.options) == 1
        assert lease.options[0].id == "ntp_server"
        assert lease.options[0].val == ["192.168.1.38"]  # ip_list

    def test_dynamic_leases_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/dhcp/dynamic_lease/", json=api_ok([]))
        assert fb.dhcp.dynamic_leases() == []
