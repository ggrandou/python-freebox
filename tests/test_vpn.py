import pytest

from freebox import (
    Freebox,
    VPNClientConfig,
    VPNClientPPTPConfig,
    VPNClientStats,
    VPNClientStatus,
    VPNClientWireGuardConfig,
    VPNClientWireGuardIP,
    VPNConnection,
    VPNIPPool,
    VPNIPReservation,
    VPNOpenVpnConfig,
    VPNPPTPConfig,
    VPNServer,
    VPNServerConfig,
    VPNUser,
    VPNWireGuardServerConfig,
    VPNWireGuardUserConfig,
    VpnClient,
    VpnServer,
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


# ── Fixture data ───────────────────────────────────────────────────────────────

OPENVPN_SERVER = {
    "name": "openvpn_routed",
    "type": "openvpn",
    "state": "stopped",
    "connection_count": 0,
    "auth_connection_count": 0,
}

PPTP_SERVER = {
    "name": "pptp",
    "type": "pptp",
    "state": "started",
    "connection_count": 1,
    "auth_connection_count": 1,
}

WIREGUARD_SERVER = {
    "name": "wireguard",
    "type": "wireguard",
    "state": "stopped",
    "connection_count": 0,
    "auth_connection_count": 0,
}

OPENVPN_SERVER_CONFIG = {
    "id": "openvpn_routed",
    "type": "openvpn",
    "enabled": False,
    "enable_ipv4": True,
    "enable_ipv6": False,
    "port": 1194,
    "min_port": 1024,
    "max_port": 65535,
    "port_ike": 0,
    "port_nat": 0,
    "ip_start": "192.168.27.65",
    "ip_end": "192.168.27.95",
    "ip6_start": "",
    "ip6_end": "",
    "conf_openvpn": {
        "cipher": "aes128",
        "disable_fragment": False,
        "use_tcp": False,
    },
}

PPTP_SERVER_CONFIG = {
    "id": "pptp",
    "type": "pptp",
    "enabled": True,
    "enable_ipv4": False,
    "enable_ipv6": False,
    "port": 1723,
    "min_port": 0,
    "max_port": 0,
    "port_ike": 0,
    "port_nat": 0,
    "ip_start": "192.168.27.1",
    "ip_end": "192.168.27.64",
    "ip6_start": "",
    "ip6_end": "",
    "conf_pptp": {
        "mppe": "require",
        "allowed_auth": {"pap": False, "chap": False, "mschapv2": True},
    },
}

WIREGUARD_SERVER_CONFIG = {
    "id": "wireguard",
    "type": "wireguard",
    "enabled": False,
    "enable_ipv4": False,
    "enable_ipv6": False,
    "port": 51820,
    "min_port": 1024,
    "max_port": 65535,
    "port_ike": 0,
    "port_nat": 0,
    "ip_start": "",
    "ip_end": "",
    "ip6_start": "",
    "ip6_end": "",
    "conf_wireguard": {"mtu": 1420},
}

STANDARD_USER = {
    "login": "alice",
    "type": "standard",
    "password_set": True,
    "ip_reservation": "192.168.27.70",
}

WIREGUARD_USER = {
    "login": "bob",
    "type": "wireguard",
    "password_set": False,
    "ip_reservation": "192.168.27.71",
    "conf_wireguard": {"keepalive": 25, "psk": True},
}

IP_POOL_DATA = {
    "ip_start": "192.168.27.65",
    "ip_end": "192.168.27.95",
    "reservations": [
        {"login": "alice", "ip": "192.168.27.70"},
    ],
}

CONNECTION_DATA = {
    "id": "pptp-1",
    "vpn": "pptp",
    "user": "alice",
    "authenticated": True,
    "auth_time": 1392895603,
    "src_ip": "93.184.216.119",
    "src_port": 51234,
    "local_ip": "192.168.27.65",
    "rx_bytes": 1024,
    "tx_bytes": 512,
}

PPTP_CLIENT_CONFIG = {
    "id": "vpn0",
    "description": "office vpn",
    "type": "pptp",
    "active": True,
    "conf_pptp": {
        "remote_host": "vpn.example.org",
        "username": "alice",
        "mppe": "require",
        "allowed_auth": {"eap": False, "pap": False, "chap": False, "mschap": False, "mschapv2": True},
    },
}

WIREGUARD_CLIENT_CONFIG = {
    "id": "vpn1",
    "description": "home wg",
    "type": "wireguard",
    "active": False,
    "conf_wireguard": {
        "remote_addr": "192.0.2.1",
        "remote_port": 51820,
        "remote_public_key": "QZnLR0TYPbPbhfVWeLVRf1zsPC0JXG/woVmsmEkgsw8=",
        "remote_preshared_key": "",
        "local_priv_key": "TdbS1Y0RHZ6rRNSxlEUssD/pnRDfrHMFfJPLl5icvQg=",
        "local_addr": [{"ip": "198.51.100.10", "len": 24}],
        "dns": ["198.51.100.53"],
    },
}

CLIENT_STATUS_DATA = {
    "enabled": True,
    "active_vpn": "vpn0",
    "active_vpn_description": "office vpn",
    "type": "pptp",
    "state": "up",
    "last_up": 1392904510,
    "last_try": 1392904509,
    "next_try": 0,
    "last_error": "none",
    "stats": {
        "rate_up": 100,
        "rate_down": 200,
        "bytes_up": 1024,
        "bytes_down": 4096,
    },
}


# ── VPNServer dataclass ────────────────────────────────────────────────────────

class TestVPNServer:
    def test_fields(self):
        s = VPNServer._from_dict(OPENVPN_SERVER)
        assert s.name == "openvpn_routed"
        assert s.type == "openvpn"
        assert s.state == "stopped"
        assert s.connection_count == 0
        assert s.auth_connection_count == 0

    def test_defaults(self):
        s = VPNServer._from_dict({})
        assert s.name == ""
        assert s.connection_count == 0


# ── VPNServerConfig dataclass ──────────────────────────────────────────────────

class TestVPNServerConfig:
    def test_openvpn(self):
        c = VPNServerConfig._from_dict(OPENVPN_SERVER_CONFIG)
        assert c.id == "openvpn_routed"
        assert c.type == "openvpn"
        assert c.enabled is False
        assert c.port == 1194
        assert c.conf_openvpn is not None
        assert c.conf_openvpn.cipher == "aes128"
        assert c.conf_pptp is None
        assert c.conf_ipsec is None
        assert c.conf_wireguard is None

    def test_pptp(self):
        c = VPNServerConfig._from_dict(PPTP_SERVER_CONFIG)
        assert c.id == "pptp"
        assert c.conf_pptp is not None
        assert c.conf_pptp.mppe == "require"
        assert c.conf_pptp.allowed_auth["mschapv2"] is True
        assert c.conf_openvpn is None

    def test_wireguard(self):
        c = VPNServerConfig._from_dict(WIREGUARD_SERVER_CONFIG)
        assert c.conf_wireguard is not None
        assert c.conf_wireguard.mtu == 1420

    def test_defaults(self):
        c = VPNServerConfig._from_dict({})
        assert c.id == ""
        assert c.enabled is False
        assert c.conf_pptp is None
        assert c.conf_openvpn is None


# ── VPNUser dataclass ──────────────────────────────────────────────────────────

class TestVPNUser:
    def test_standard(self):
        u = VPNUser._from_dict(STANDARD_USER)
        assert u.login == "alice"
        assert u.type == "standard"
        assert u.password_set is True
        assert u.ip_reservation == "192.168.27.70"
        assert u.conf_wireguard is None

    def test_wireguard(self):
        u = VPNUser._from_dict(WIREGUARD_USER)
        assert u.login == "bob"
        assert u.conf_wireguard is not None
        assert u.conf_wireguard.keepalive == 25
        assert u.conf_wireguard.psk is True

    def test_defaults(self):
        u = VPNUser._from_dict({})
        assert u.login == ""
        assert u.type == "standard"
        assert u.password_set is False


# ── VPNIPPool dataclass ────────────────────────────────────────────────────────

class TestVPNIPPool:
    def test_fields(self):
        p = VPNIPPool._from_dict(IP_POOL_DATA)
        assert p.ip_start == "192.168.27.65"
        assert p.ip_end == "192.168.27.95"
        assert len(p.reservations) == 1
        assert p.reservations[0].login == "alice"
        assert p.reservations[0].ip == "192.168.27.70"

    def test_empty_reservations(self):
        p = VPNIPPool._from_dict({"ip_start": "10.0.0.1", "ip_end": "10.0.0.254"})
        assert p.reservations == []


# ── VPNConnection dataclass ────────────────────────────────────────────────────

class TestVPNConnection:
    def test_fields(self):
        c = VPNConnection._from_dict(CONNECTION_DATA)
        assert c.id == "pptp-1"
        assert c.vpn == "pptp"
        assert c.user == "alice"
        assert c.authenticated is True
        assert c.src_ip == "93.184.216.119"
        assert c.rx_bytes == 1024
        assert c.tx_bytes == 512

    def test_defaults(self):
        c = VPNConnection._from_dict({})
        assert c.id == ""
        assert c.authenticated is False
        assert c.rx_bytes == 0


# ── VPNClientConfig dataclass ──────────────────────────────────────────────────

class TestVPNClientConfig:
    def test_pptp(self):
        c = VPNClientConfig._from_dict(PPTP_CLIENT_CONFIG)
        assert c.id == "vpn0"
        assert c.description == "office vpn"
        assert c.type == "pptp"
        assert c.active is True
        assert c.conf_pptp is not None
        assert c.conf_pptp.remote_host == "vpn.example.org"
        assert c.conf_pptp.username == "alice"
        assert c.conf_wireguard is None

    def test_wireguard(self):
        c = VPNClientConfig._from_dict(WIREGUARD_CLIENT_CONFIG)
        assert c.type == "wireguard"
        assert c.active is False
        assert c.conf_wireguard is not None
        assert c.conf_wireguard.remote_addr == "192.0.2.1"
        assert c.conf_wireguard.remote_port == 51820
        assert len(c.conf_wireguard.local_addr) == 1
        assert c.conf_wireguard.local_addr[0].ip == "198.51.100.10"
        assert c.conf_wireguard.local_addr[0].len == 24
        assert c.conf_wireguard.dns == ["198.51.100.53"]
        assert c.conf_pptp is None

    def test_defaults(self):
        c = VPNClientConfig._from_dict({})
        assert c.id == ""
        assert c.active is False
        assert c.conf_pptp is None
        assert c.conf_wireguard is None


# ── VPNClientStatus dataclass ──────────────────────────────────────────────────

class TestVPNClientStatus:
    def test_fields(self):
        s = VPNClientStatus._from_dict(CLIENT_STATUS_DATA)
        assert s.enabled is True
        assert s.active_vpn == "vpn0"
        assert s.type == "pptp"
        assert s.state == "up"
        assert s.last_error == "none"
        assert s.stats is not None
        assert s.stats.rate_up == 100
        assert s.stats.bytes_down == 4096

    def test_no_stats(self):
        s = VPNClientStatus._from_dict({"enabled": False, "state": "down"})
        assert s.enabled is False
        assert s.stats is None


# ── VpnServer API ──────────────────────────────────────────────────────────────

class TestVpnServerAPI:
    def test_servers(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/",
            json=api_ok([OPENVPN_SERVER, PPTP_SERVER, WIREGUARD_SERVER]),
        )
        servers = fb.vpn_server.servers()
        assert len(servers) == 3
        assert isinstance(servers[0], VPNServer)
        assert servers[0].name == "openvpn_routed"
        assert servers[1].state == "started"

    def test_servers_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/vpn/", json=api_ok([]))
        assert fb.vpn_server.servers() == []

    def test_server_config_openvpn(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/openvpn_routed/config/",
            json=api_ok(OPENVPN_SERVER_CONFIG),
        )
        cfg = fb.vpn_server.server_config("openvpn_routed")
        assert isinstance(cfg, VPNServerConfig)
        assert cfg.id == "openvpn_routed"
        assert cfg.conf_openvpn is not None
        assert cfg.conf_openvpn.cipher == "aes128"

    def test_set_server_config(self, fb, httpx_mock):
        updated = {**OPENVPN_SERVER_CONFIG, "enabled": True}
        httpx_mock.add_response(
            url=f"{API}/vpn/openvpn_routed/config/",
            method="PUT",
            json=api_ok(updated),
        )
        cfg = fb.vpn_server.set_server_config("openvpn_routed", enabled=True)
        assert isinstance(cfg, VPNServerConfig)
        assert cfg.enabled is True
        req = httpx_mock.get_requests()[-1]
        assert req.method == "PUT"

    def test_users(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/user/",
            json=api_ok([STANDARD_USER, WIREGUARD_USER]),
        )
        users = fb.vpn_server.users()
        assert len(users) == 2
        assert isinstance(users[0], VPNUser)
        assert users[0].login == "alice"
        assert users[1].conf_wireguard is not None

    def test_user(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/user/alice",
            json=api_ok(STANDARD_USER),
        )
        u = fb.vpn_server.user("alice")
        assert isinstance(u, VPNUser)
        assert u.login == "alice"

    def test_add_user(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/user/",
            method="POST",
            json=api_ok(STANDARD_USER),
        )
        u = fb.vpn_server.add_user("alice", "secret123")
        assert isinstance(u, VPNUser)
        req = httpx_mock.get_requests()[-1]
        assert req.method == "POST"

    def test_update_user(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/user/alice",
            method="PUT",
            json=api_ok({**STANDARD_USER, "password_set": True}),
        )
        u = fb.vpn_server.update_user("alice", password="newpass")
        assert isinstance(u, VPNUser)
        req = httpx_mock.get_requests()[-1]
        assert req.method == "PUT"

    def test_delete_user(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/user/alice",
            method="DELETE",
            json={"success": True},
        )
        fb.vpn_server.delete_user("alice")
        req = httpx_mock.get_requests()[-1]
        assert req.method == "DELETE"

    def test_ip_pool(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/ip_pool/",
            json=api_ok(IP_POOL_DATA),
        )
        pool = fb.vpn_server.ip_pool()
        assert isinstance(pool, VPNIPPool)
        assert pool.ip_start == "192.168.27.65"
        assert len(pool.reservations) == 1

    def test_connections(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/connection/",
            json=api_ok([CONNECTION_DATA]),
        )
        conns = fb.vpn_server.connections()
        assert len(conns) == 1
        assert isinstance(conns[0], VPNConnection)
        assert conns[0].user == "alice"

    def test_connections_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/vpn/connection/", json=api_ok([]))
        assert fb.vpn_server.connections() == []

    def test_delete_connection(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn/connection/pptp-1",
            method="DELETE",
            json={"success": True},
        )
        fb.vpn_server.delete_connection("pptp-1")
        req = httpx_mock.get_requests()[-1]
        assert req.method == "DELETE"

    def test_vpn_server_property(self, fb):
        assert isinstance(fb.vpn_server, VpnServer)


# ── VpnClient API ──────────────────────────────────────────────────────────────

class TestVpnClientAPI:
    def test_configs(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn_client/config/",
            json=api_ok([PPTP_CLIENT_CONFIG, WIREGUARD_CLIENT_CONFIG]),
        )
        configs = fb.vpn_client.configs()
        assert len(configs) == 2
        assert isinstance(configs[0], VPNClientConfig)
        assert configs[0].active is True
        assert configs[1].active is False

    def test_configs_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/vpn_client/config/", json=api_ok([]))
        assert fb.vpn_client.configs() == []

    def test_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn_client/config/vpn0",
            json=api_ok(PPTP_CLIENT_CONFIG),
        )
        cfg = fb.vpn_client.config("vpn0")
        assert isinstance(cfg, VPNClientConfig)
        assert cfg.id == "vpn0"

    def test_add_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn_client/config/",
            method="POST",
            json=api_ok(PPTP_CLIENT_CONFIG),
        )
        cfg = fb.vpn_client.add_config(type="pptp", description="office vpn")
        assert isinstance(cfg, VPNClientConfig)
        req = httpx_mock.get_requests()[-1]
        assert req.method == "POST"

    def test_update_config(self, fb, httpx_mock):
        updated = {**PPTP_CLIENT_CONFIG, "active": False}
        httpx_mock.add_response(
            url=f"{API}/vpn_client/config/vpn0",
            method="PUT",
            json=api_ok(updated),
        )
        cfg = fb.vpn_client.update_config("vpn0", active=False)
        assert isinstance(cfg, VPNClientConfig)
        req = httpx_mock.get_requests()[-1]
        assert req.method == "PUT"

    def test_delete_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn_client/config/vpn0",
            method="DELETE",
            json={"success": True},
        )
        fb.vpn_client.delete_config("vpn0")
        req = httpx_mock.get_requests()[-1]
        assert req.method == "DELETE"

    def test_status(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn_client/status",
            json=api_ok(CLIENT_STATUS_DATA),
        )
        status = fb.vpn_client.status()
        assert isinstance(status, VPNClientStatus)
        assert status.state == "up"
        assert status.stats is not None
        assert status.stats.bytes_up == 1024

    def test_log(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/vpn_client/log",
            json=api_ok("2024-01-01 12:00:00 info: VPN up"),
        )
        log = fb.vpn_client.log()
        assert "VPN up" in log

    def test_vpn_client_property(self, fb):
        assert isinstance(fb.vpn_client, VpnClient)
