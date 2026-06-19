import pytest

from freebox import (
    Freebox,
    Wifi,
    WifiGlobalConfig,
    WifiSteeringConfig,
    WifiGlobalState,
    ExpectedPhy,
    WifiAp,
    WifiApConfig,
    WifiApStatus,
    WifiApHtConfig,
    WifiApHeConfig,
    WifiAllowedComb,
    WifiApChannelSurveyData,
    WifiNeighbor,
    WifiNeighborCap,
    WifiChannelUsage,
    WifiStation,
    WifiStationFlags,
    WifiStationStats,
    WifiBss,
    WifiBssConfig,
    WifiBssStatus,
    WifiPlanning,
    WifiMacFilter,
    WifiDiagItem,
    WifiDiag,
    WifiWpsConfig,
    WifiWpsSession,
    WifiCustomKeyConfig,
    WifiCustomKeyParams,
    WifiCustomKey,
    WifiMLOConfig,
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


# ── Sample data ────────────────────────────────────────────────────────────────

GLOBAL_CONFIG_DATA = {
    "enabled": True,
    "mac_filter_state": "blacklist",
}

STEERING_CONFIG_DATA = {"steering_level": 2}

GLOBAL_STATE_DATA = {
    "state": "enabled",
    "power_saving_capability": "unsupported_box_model",
    "expected_phys": [
        {"band": "2d4g", "phy_id": 0, "detected": True},
        {"band": "5g",   "phy_id": 1, "detected": True},
    ],
}

AP_DATA = {
    "id": 0,
    "name": "2.4G",
    "capabilities": {"2d4g": {"shortgi20": True}},
    "config": {
        "band": "2d4g",
        "channel_width": "40",
        "primary_channel": 9,
        "secondary_channel": 13,
        "dfs_enabled": False,
        "ht": {"ht_enabled": True, "ac_enabled": False},
        "he": {"enabled": False},
    },
    "status": {
        "state": "active",
        "channel_width": "20",
        "primary_channel": 9,
        "secondary_channel": 0,
        "dfs_cac_remaining_time": 0,
        "dfs_disabled": False,
    },
}

ALLOWED_COMB_DATA = {
    "band": "2d4g",
    "channel_width": "20",
    "need_dfs": False,
    "dfs_cac_time": 0,
    "psc": False,
    "primary": 1,
    "secondary": 0,
}

SURVEY_DATA = {
    "timestamp": 1651135474996,
    "busy_percent": 65,
    "tx_percent": 2,
    "rx_percent": 56,
    "rx_bss_percent": 0,
}

NEIGHBOR_DATA = {
    "bssid": "00:24:D4:BA:BB:EE",
    "ssid": "Freebox-future",
    "band": "2d4g",
    "channel_width": "20",
    "channel": 1,
    "secondary_channel": 0,
    "signal": -27,
    "capabilities": {"legacy": False, "ht": True, "vht": False},
}

CHANNEL_USAGE_DATA = {
    "band": "2d4g",
    "channel": 1,
    "noise_level": -66,
    "rx_busy_percent": 35,
}

STATION_DATA = {
    "id": "00:24:D4:AC:DC:88-18:AF:36:15:69:42",
    "mac": "18:AF:36:15:69:42",
    "bssid": "00:24:D4:AC:DC:88",
    "hostname": "iPhone",
    "state": "authenticated",
    "inactive": 168,
    "conn_duration": 263,
    "rx_bytes": 781,
    "tx_bytes": 2651,
    "tx_rate": 0,
    "rx_rate": 0,
    "signal": -38,
    "flags": {"legacy": False, "ht": False, "vht": False, "he": False, "authorized": True},
    "last_rx": {"bitrate": 110, "mcs": -1, "vht_mcs": -1, "width": "20", "shortgi": False},
    "last_tx": {"bitrate": 360, "mcs": -1, "vht_mcs": -1, "width": "20", "shortgi": False},
}

BSS_DATA = {
    "id": "00:24:D4:AA:BB:CC",
    "phy_id": 0,
    "use_shared_params": False,
    "disable_wep": False,
    "partners": [],
    "config": {
        "enabled": True,
        "ssid": "r0ro 2.4",
        "hide_ssid": False,
        "encryption": "wpa2_psk_ccmp",
        "key": "secret",
        "eapol_version": 2,
        "gcmp256": False,
    },
    "bss_params": {
        "enabled": True,
        "ssid": "r0ro 2.4",
        "hide_ssid": False,
        "encryption": "wpa2_psk_ccmp",
        "key": "secret",
        "eapol_version": 2,
        "gcmp256": False,
    },
    "shared_bss_params": {
        "enabled": True,
        "ssid": "r0ro",
        "hide_ssid": False,
        "encryption": "wpa2_psk_ccmp",
        "key": "sharedkey",
        "eapol_version": 2,
        "gcmp256": False,
    },
    "status": {
        "state": "active",
        "sta_count": 1,
        "authorized_sta_count": 1,
        "custom_key_ssid": "",
    },
}

PLANNING_DATA = {
    "use_planning": False,
    "resolution": 48,
    "mapping": ["on"] * (7 * 48),
}

MAC_FILTER_DATA = {
    "id": "00:07:CB:01:02:03",
    "mac": "00:07:CB:01:02:03",
    "comment": "test",
    "type": "whitelist",
    "hostname": "00:07:CB:01:02:03",
}

DIAG_ITEM_AP = {"ap_id": 0, "code": "channel_width", "severity": "minor"}
DIAG_ITEM_BSS = {"bssid": "02:00:00:00:00:08", "code": "network_security", "severity": "major"}

DIAG_DATA = {"aps": [DIAG_ITEM_AP], "bsss": [DIAG_ITEM_BSS]}

WPS_CONFIG_DATA = {"enabled": True}

WPS_SESSION_DATA = {
    "id": 1,
    "bss_uuid": "6a55ea3d-29fa-4bd9-b1e3-22a49a3ca134",
    "ssid": "r0ro 5G",
    "active": False,
    "result": "failed_timeout",
    "start_date": 1516012531,
    "end_date": 1516012651,
    "mac": "00:00:00:00:00:00",
}

CUSTOM_KEY_CONFIG_DATA = {
    "ssid": "Freebox-guest",
    "ssid_read_only": False,
    "hide_ssid": False,
    "encryption": "wpa2_psk",
}

CUSTOM_KEY_PARAMS_DATA = {
    "description": "soiree",
    "key": "YY5Sg74W3VNxrmfwAz7aCY7OVqRVG2JN",
    "max_use_count": 100,
    "duration": 86400,
    "access_type": "full",
}

CUSTOM_KEY_DATA = {
    "id": 8,
    "remaining": 86376,
    "params": CUSTOM_KEY_PARAMS_DATA,
}

MLO_CONFIG_DATA = {"partners": [0, 1]}


# ── WifiGlobalConfig ────────────────────────────────────────────────────────────

class TestWifiGlobalConfig:
    def test_fields(self):
        c = WifiGlobalConfig._from_dict(GLOBAL_CONFIG_DATA)
        assert c.enabled is True
        assert c.mac_filter_state == "blacklist"

    def test_defaults(self):
        c = WifiGlobalConfig._from_dict({})
        assert c.enabled is False
        assert c.mac_filter_state == "disabled"


# ── WifiSteeringConfig ──────────────────────────────────────────────────────────

class TestWifiSteeringConfig:
    def test_fields(self):
        c = WifiSteeringConfig._from_dict(STEERING_CONFIG_DATA)
        assert c.steering_level == 2

    def test_defaults(self):
        c = WifiSteeringConfig._from_dict({})
        assert c.steering_level == 0


# ── ExpectedPhy / WifiGlobalState ───────────────────────────────────────────────

class TestExpectedPhy:
    def test_fields(self):
        p = ExpectedPhy._from_dict({"band": "5g", "phy_id": 1, "detected": True})
        assert p.band == "5g"
        assert p.phy_id == 1
        assert p.detected is True

    def test_defaults(self):
        p = ExpectedPhy._from_dict({})
        assert p.band == ""
        assert p.phy_id == 0
        assert p.detected is False


class TestWifiGlobalState:
    def test_fields(self):
        s = WifiGlobalState._from_dict(GLOBAL_STATE_DATA)
        assert s.state == "enabled"
        assert s.power_saving_capability == "unsupported_box_model"
        assert len(s.expected_phys) == 2
        assert s.expected_phys[0].band == "2d4g"
        assert s.expected_phys[1].band == "5g"

    def test_defaults(self):
        s = WifiGlobalState._from_dict({})
        assert s.state == ""
        assert s.power_saving_capability == ""
        assert s.expected_phys == []


# ── WifiApHtConfig / WifiApHeConfig / WifiApConfig / WifiApStatus / WifiAp ────

class TestWifiApHtConfig:
    def test_fields(self):
        h = WifiApHtConfig._from_dict({"ht_enabled": True, "ac_enabled": False})
        assert h.ht_enabled is True
        assert h.ac_enabled is False

    def test_defaults(self):
        h = WifiApHtConfig._from_dict({})
        assert h.ht_enabled is False
        assert h.ac_enabled is False


class TestWifiApHeConfig:
    def test_fields(self):
        h = WifiApHeConfig._from_dict({"enabled": True})
        assert h.enabled is True

    def test_defaults(self):
        assert WifiApHeConfig._from_dict({}).enabled is False


class TestWifiApConfig:
    def test_fields(self):
        c = WifiApConfig._from_dict(AP_DATA["config"])
        assert c.band == "2d4g"
        assert c.channel_width == "40"
        assert c.primary_channel == 9
        assert c.secondary_channel == 13
        assert c.dfs_enabled is False
        assert c.ht is not None
        assert c.ht.ht_enabled is True
        assert c.he is not None
        assert c.he.enabled is False

    def test_no_ht_he(self):
        c = WifiApConfig._from_dict({"band": "5g", "channel_width": "80"})
        assert c.ht is None
        assert c.he is None

    def test_defaults(self):
        c = WifiApConfig._from_dict({})
        assert c.band == ""
        assert c.channel_width == ""
        assert c.primary_channel == 0


class TestWifiApStatus:
    def test_fields(self):
        s = WifiApStatus._from_dict(AP_DATA["status"])
        assert s.state == "active"
        assert s.channel_width == "20"
        assert s.primary_channel == 9
        assert s.dfs_cac_remaining_time == 0
        assert s.dfs_disabled is False
        assert s.temp_disable_remaining_time is None

    def test_temp_disable(self):
        s = WifiApStatus._from_dict({"state": "disabled_temp", "temp_disable_remaining_time": 300})
        assert s.temp_disable_remaining_time == 300


class TestWifiAp:
    def test_fields(self):
        ap = WifiAp._from_dict(AP_DATA)
        assert ap.id == 0
        assert ap.name == "2.4G"
        assert ap.capabilities == {"2d4g": {"shortgi20": True}}
        assert isinstance(ap.config, WifiApConfig)
        assert isinstance(ap.status, WifiApStatus)

    def test_no_config_no_status(self):
        ap = WifiAp._from_dict({"id": 1, "name": "5G"})
        assert ap.config is None
        assert ap.status is None


# ── WifiAllowedComb ────────────────────────────────────────────────────────────

class TestWifiAllowedComb:
    def test_fields(self):
        c = WifiAllowedComb._from_dict(ALLOWED_COMB_DATA)
        assert c.band == "2d4g"
        assert c.channel_width == "20"
        assert c.need_dfs is False
        assert c.primary == 1
        assert c.secondary == 0
        assert c.psc is False

    def test_defaults(self):
        c = WifiAllowedComb._from_dict({})
        assert c.band == ""
        assert c.primary == 0


# ── WifiApChannelSurveyData ────────────────────────────────────────────────────

class TestWifiApChannelSurveyData:
    def test_fields(self):
        s = WifiApChannelSurveyData._from_dict(SURVEY_DATA)
        assert s.timestamp == 1651135474996
        assert s.busy_percent == 65
        assert s.tx_percent == 2
        assert s.rx_percent == 56
        assert s.rx_bss_percent == 0

    def test_defaults(self):
        s = WifiApChannelSurveyData._from_dict({})
        assert s.busy_percent == 0


# ── WifiNeighbor ───────────────────────────────────────────────────────────────

class TestWifiNeighborCap:
    def test_fields(self):
        c = WifiNeighborCap._from_dict({"legacy": False, "ht": True, "vht": False})
        assert c.ht is True
        assert c.legacy is False

    def test_defaults(self):
        c = WifiNeighborCap._from_dict({})
        assert c.legacy is False
        assert c.ht is False
        assert c.vht is False


class TestWifiNeighbor:
    def test_fields(self):
        n = WifiNeighbor._from_dict(NEIGHBOR_DATA)
        assert n.bssid == "00:24:D4:BA:BB:EE"
        assert n.ssid == "Freebox-future"
        assert n.band == "2d4g"
        assert n.channel == 1
        assert n.signal == -27
        assert n.capabilities is not None
        assert n.capabilities.ht is True

    def test_no_capabilities(self):
        n = WifiNeighbor._from_dict({"bssid": "AA:BB:CC:DD:EE:FF"})
        assert n.capabilities is None


# ── WifiChannelUsage ───────────────────────────────────────────────────────────

class TestWifiChannelUsage:
    def test_fields(self):
        u = WifiChannelUsage._from_dict(CHANNEL_USAGE_DATA)
        assert u.channel == 1
        assert u.band == "2d4g"
        assert u.noise_level == -66
        assert u.rx_busy_percent == 35

    def test_defaults(self):
        u = WifiChannelUsage._from_dict({})
        assert u.channel == 0
        assert u.noise_level == 0


# ── WifiStationStats / WifiStationFlags / WifiStation ─────────────────────────

class TestWifiStationStats:
    def test_fields(self):
        s = WifiStationStats._from_dict(STATION_DATA["last_rx"])
        assert s.bitrate == 110
        assert s.mcs == -1
        assert s.vht_mcs == -1
        assert s.width == "20"
        assert s.shortgi is False

    def test_defaults(self):
        s = WifiStationStats._from_dict({})
        assert s.bitrate == -1
        assert s.mcs == -1


class TestWifiStationFlags:
    def test_fields(self):
        f = WifiStationFlags._from_dict(STATION_DATA["flags"])
        assert f.authorized is True
        assert f.ht is False
        assert f.vht is False
        assert f.he is False
        assert f.legacy is False

    def test_defaults(self):
        f = WifiStationFlags._from_dict({})
        assert f.authorized is False


class TestWifiStation:
    def test_fields(self):
        s = WifiStation._from_dict(STATION_DATA)
        assert s.mac == "18:AF:36:15:69:42"
        assert s.bssid == "00:24:D4:AC:DC:88"
        assert s.hostname == "iPhone"
        assert s.state == "authenticated"
        assert s.signal == -38
        assert s.rx_bytes == 781
        assert s.tx_bytes == 2651
        assert isinstance(s.flags, WifiStationFlags)
        assert s.flags.authorized is True
        assert isinstance(s.last_rx, WifiStationStats)
        assert s.last_rx.bitrate == 110
        assert isinstance(s.last_tx, WifiStationStats)
        assert s.last_tx.bitrate == 360

    def test_no_flags_no_stats(self):
        s = WifiStation._from_dict({"mac": "AA:BB:CC:DD:EE:FF"})
        assert s.flags is None
        assert s.last_rx is None
        assert s.last_tx is None

    def test_defaults(self):
        s = WifiStation._from_dict({})
        assert s.mac == ""
        assert s.signal == 0


# ── WifiBssConfig / WifiBssStatus / WifiBss ───────────────────────────────────

class TestWifiBssConfig:
    def test_fields(self):
        c = WifiBssConfig._from_dict(BSS_DATA["config"])
        assert c.enabled is True
        assert c.ssid == "r0ro 2.4"
        assert c.encryption == "wpa2_psk_ccmp"
        assert c.key == "secret"
        assert c.eapol_version == 2
        assert c.hide_ssid is False
        assert c.gcmp256 is False

    def test_defaults(self):
        c = WifiBssConfig._from_dict({})
        assert c.enabled is False
        assert c.ssid == ""


class TestWifiBssStatus:
    def test_fields(self):
        s = WifiBssStatus._from_dict(BSS_DATA["status"])
        assert s.state == "active"
        assert s.sta_count == 1
        assert s.authorized_sta_count == 1

    def test_defaults(self):
        s = WifiBssStatus._from_dict({})
        assert s.state == ""
        assert s.sta_count == 0


class TestWifiBss:
    def test_fields(self):
        b = WifiBss._from_dict(BSS_DATA)
        assert b.id == "00:24:D4:AA:BB:CC"
        assert b.phy_id == 0
        assert b.use_shared_params is False
        assert isinstance(b.config, WifiBssConfig)
        assert b.config.ssid == "r0ro 2.4"
        assert isinstance(b.bss_params, WifiBssConfig)
        assert isinstance(b.shared_bss_params, WifiBssConfig)
        assert b.shared_bss_params.ssid == "r0ro"
        assert isinstance(b.status, WifiBssStatus)
        assert b.partners == []

    def test_no_configs(self):
        b = WifiBss._from_dict({"id": "00:11:22:33:44:55"})
        assert b.config is None
        assert b.bss_params is None
        assert b.shared_bss_params is None
        assert b.status is None


# ── WifiPlanning ───────────────────────────────────────────────────────────────

class TestWifiPlanning:
    def test_fields(self):
        p = WifiPlanning._from_dict(PLANNING_DATA)
        assert p.use_planning is False
        assert p.resolution == 48
        assert len(p.mapping) == 7 * 48
        assert p.mapping[0] == "on"

    def test_defaults(self):
        p = WifiPlanning._from_dict({})
        assert p.use_planning is False
        assert p.mapping == []


# ── WifiMacFilter ──────────────────────────────────────────────────────────────

class TestWifiMacFilter:
    def test_fields(self):
        f = WifiMacFilter._from_dict(MAC_FILTER_DATA)
        assert f.id == "00:07:CB:01:02:03"
        assert f.mac == "00:07:CB:01:02:03"
        assert f.type == "whitelist"
        assert f.comment == "test"
        assert f.hostname == "00:07:CB:01:02:03"

    def test_defaults(self):
        f = WifiMacFilter._from_dict({})
        assert f.id == ""
        assert f.type == ""


# ── Wifi API methods ───────────────────────────────────────────────────────────

class TestWifi:
    def test_wifi_property(self, fb):
        assert isinstance(fb.wifi, Wifi)

    def test_config(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/config/", json=api_ok(GLOBAL_CONFIG_DATA))
        cfg = fb.wifi.config()
        assert isinstance(cfg, WifiGlobalConfig)
        assert cfg.enabled is True

    def test_set_config(self, fb, httpx_mock):
        updated = {**GLOBAL_CONFIG_DATA, "enabled": False}
        httpx_mock.add_response(url=f"{API}/wifi/config/", method="PUT", json=api_ok(updated))
        cfg = fb.wifi.set_config(enabled=False)
        assert isinstance(cfg, WifiGlobalConfig)
        assert cfg.enabled is False
        assert httpx_mock.get_requests()[-1].method == "PUT"

    def test_reset_config(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/config/reset/", method="POST", json={"success": True})
        fb.wifi.reset_config()

    def test_steering_config(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/steering/config/", json=api_ok(STEERING_CONFIG_DATA))
        sc = fb.wifi.steering_config()
        assert isinstance(sc, WifiSteeringConfig)
        assert sc.steering_level == 2

    def test_set_steering_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/steering/config/", method="PUT", json=api_ok({"steering_level": 1})
        )
        sc = fb.wifi.set_steering_config(steering_level=1)
        assert sc.steering_level == 1

    def test_state(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/state/", json=api_ok(GLOBAL_STATE_DATA))
        s = fb.wifi.state()
        assert isinstance(s, WifiGlobalState)
        assert s.state == "enabled"
        assert s.power_saving_capability == "unsupported_box_model"
        assert len(s.expected_phys) == 2

    def test_aps(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/", json=api_ok([AP_DATA]))
        aps = fb.wifi.aps()
        assert len(aps) == 1
        assert isinstance(aps[0], WifiAp)
        assert aps[0].name == "2.4G"

    def test_ap(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0", json=api_ok(AP_DATA))
        ap = fb.wifi.ap(0)
        assert isinstance(ap, WifiAp)
        assert ap.id == 0

    def test_set_ap(self, fb, httpx_mock):
        updated = {**AP_DATA, "config": {**AP_DATA["config"], "primary_channel": 6}}
        httpx_mock.add_response(url=f"{API}/wifi/ap/0", method="PUT", json=api_ok(updated))
        ap = fb.wifi.set_ap(0, config={"primary_channel": 6})
        assert isinstance(ap, WifiAp)
        assert httpx_mock.get_requests()[-1].method == "PUT"

    def test_ap_allowed_channel_combs(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/ap/0/allowed_channel_comb", json=api_ok([ALLOWED_COMB_DATA])
        )
        combs = fb.wifi.ap_allowed_channel_combs(0)
        assert len(combs) == 1
        assert isinstance(combs[0], WifiAllowedComb)
        assert combs[0].primary == 1

    def test_ap_stations(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/stations/", json=api_ok([STATION_DATA]))
        stations = fb.wifi.ap_stations(0)
        assert len(stations) == 1
        assert isinstance(stations[0], WifiStation)
        assert stations[0].mac == "18:AF:36:15:69:42"

    def test_ap_station(self, fb, httpx_mock):
        mac = "18:AF:36:15:69:42"
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/stations/{mac}", json=api_ok(STATION_DATA))
        s = fb.wifi.ap_station(0, mac)
        assert isinstance(s, WifiStation)
        assert s.mac == mac

    def test_ap_channel_survey_history(self, fb, httpx_mock):
        ts = 1651135474000
        httpx_mock.add_response(
            url=f"{API}/wifi/ap/0/channel_survey_history/{ts}", json=api_ok([SURVEY_DATA])
        )
        history = fb.wifi.ap_channel_survey_history(0, ts)
        assert len(history) == 1
        assert isinstance(history[0], WifiApChannelSurveyData)
        assert history[0].busy_percent == 65

    def test_ap_neighbors(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/neighbors/", json=api_ok([NEIGHBOR_DATA]))
        neighbors = fb.wifi.ap_neighbors(0)
        assert len(neighbors) == 1
        assert isinstance(neighbors[0], WifiNeighbor)
        assert neighbors[0].ssid == "Freebox-future"

    def test_ap_channel_usage(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/channel_usage/", json=api_ok([CHANNEL_USAGE_DATA]))
        usage = fb.wifi.ap_channel_usage(0)
        assert len(usage) == 1
        assert isinstance(usage[0], WifiChannelUsage)
        assert usage[0].channel == 1

    def test_restart_ap(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/restart", method="POST", json={"success": True})
        fb.wifi.restart_ap(0)

    def test_scan_ap_neighbors(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/ap/0/neighbors/scan", method="POST", json={"success": True}
        )
        fb.wifi.scan_ap_neighbors(0)

    def test_bss_list(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/bss/", json=api_ok([BSS_DATA]))
        bsses = fb.wifi.bss_list()
        assert len(bsses) == 1
        assert isinstance(bsses[0], WifiBss)
        assert bsses[0].id == "00:24:D4:AA:BB:CC"

    def test_bss(self, fb, httpx_mock):
        bss_id = "00:24:D4:AA:BB:CC"
        httpx_mock.add_response(url=f"{API}/wifi/bss/{bss_id}", json=api_ok(BSS_DATA))
        b = fb.wifi.bss(bss_id)
        assert isinstance(b, WifiBss)
        assert b.phy_id == 0

    def test_set_bss(self, fb, httpx_mock):
        bss_id = "00:24:D4:AA:BB:CC"
        updated = {**BSS_DATA}
        httpx_mock.add_response(url=f"{API}/wifi/bss/{bss_id}", method="PUT", json=api_ok(updated))
        b = fb.wifi.set_bss(bss_id, config={"key": "newkey"})
        assert isinstance(b, WifiBss)
        assert httpx_mock.get_requests()[-1].method == "PUT"

    def test_planning(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/planning/", json=api_ok(PLANNING_DATA))
        p = fb.wifi.planning()
        assert isinstance(p, WifiPlanning)
        assert p.use_planning is False
        assert p.resolution == 48

    def test_set_planning(self, fb, httpx_mock):
        updated = {**PLANNING_DATA, "use_planning": True}
        httpx_mock.add_response(url=f"{API}/wifi/planning/", method="PUT", json=api_ok(updated))
        p = fb.wifi.set_planning(use_planning=True)
        assert p.use_planning is True

    def test_mac_filters(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/mac_filter/", json=api_ok([MAC_FILTER_DATA]))
        filters = fb.wifi.mac_filters()
        assert len(filters) == 1
        assert isinstance(filters[0], WifiMacFilter)
        assert filters[0].type == "whitelist"

    def test_mac_filter(self, fb, httpx_mock):
        fid = "00:07:CB:01:02:03"
        httpx_mock.add_response(url=f"{API}/wifi/mac_filter/{fid}", json=api_ok(MAC_FILTER_DATA))
        f = fb.wifi.mac_filter(fid)
        assert isinstance(f, WifiMacFilter)
        assert f.comment == "test"

    def test_add_mac_filter(self, fb, httpx_mock):
        new_filter = {
            "id": "00:07:CB:CB:07:00",
            "mac": "00:07:CB:CB:07:00",
            "comment": "new",
            "type": "blacklist",
            "hostname": "00:07:CB:CB:07:00",
        }
        httpx_mock.add_response(url=f"{API}/wifi/mac_filter/", method="POST", json=api_ok(new_filter))
        f = fb.wifi.add_mac_filter("00:07:CB:CB:07:00", "blacklist", "new")
        assert isinstance(f, WifiMacFilter)
        assert f.type == "blacklist"
        assert httpx_mock.get_requests()[-1].method == "POST"

    def test_set_mac_filter(self, fb, httpx_mock):
        fid = "00:07:CB:01:02:03"
        updated = {**MAC_FILTER_DATA, "type": "blacklist", "comment": "filtre de test"}
        httpx_mock.add_response(url=f"{API}/wifi/mac_filter/{fid}", method="PUT", json=api_ok(updated))
        f = fb.wifi.set_mac_filter(fid, type="blacklist", comment="filtre de test")
        assert f.type == "blacklist"

    def test_delete_mac_filter(self, fb, httpx_mock):
        fid = "00:07:CB:01:02:03"
        httpx_mock.add_response(
            url=f"{API}/wifi/mac_filter/{fid}", method="DELETE", json={"success": True}
        )
        fb.wifi.delete_mac_filter(fid)
        assert httpx_mock.get_requests()[-1].method == "DELETE"

    def test_default_config(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/default", json=api_ok(GLOBAL_CONFIG_DATA))
        cfg = fb.wifi.default_config()
        assert isinstance(cfg, WifiGlobalConfig)
        assert cfg.enabled is True

    def test_ap_default(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/default", json=api_ok(AP_DATA))
        ap = fb.wifi.ap_default(0)
        assert isinstance(ap, WifiAp)
        assert ap.id == 0

    def test_bss_default(self, fb, httpx_mock):
        bss_id = "00:24:D4:AA:BB:CC"
        httpx_mock.add_response(url=f"{API}/wifi/bss/{bss_id}/default", json=api_ok(BSS_DATA))
        b = fb.wifi.bss_default(bss_id)
        assert isinstance(b, WifiBss)

    def test_diag(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/diag", json=api_ok(DIAG_DATA))
        d = fb.wifi.diag()
        assert isinstance(d, WifiDiag)
        assert len(d.aps) == 1
        assert d.aps[0].ap_id == 0
        assert d.aps[0].code == "channel_width"
        assert d.aps[0].severity == "minor"
        assert len(d.bsss) == 1
        assert d.bsss[0].bssid == "02:00:00:00:00:08"

    def test_fix_diag(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/diag", method="POST", json={"success": True})
        fb.wifi.fix_diag(aps=[{"ap_id": 0, "code": "channel_width"}])
        assert httpx_mock.get_requests()[-1].method == "POST"

    def test_ap_diag(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/diag", json=api_ok([DIAG_ITEM_AP]))
        items = fb.wifi.ap_diag(0)
        assert len(items) == 1
        assert isinstance(items[0], WifiDiagItem)
        assert items[0].code == "channel_width"

    def test_fix_ap_diag(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/ap/0/diag", method="POST", json={"success": True})
        fb.wifi.fix_ap_diag(0, ["channel_width"])
        assert httpx_mock.get_requests()[-1].method == "POST"

    def test_bss_diag(self, fb, httpx_mock):
        bss_id = "02:00:00:00:00:08"
        httpx_mock.add_response(url=f"{API}/wifi/bss/{bss_id}/diag", json=api_ok([DIAG_ITEM_BSS]))
        items = fb.wifi.bss_diag(bss_id)
        assert len(items) == 1
        assert isinstance(items[0], WifiDiagItem)
        assert items[0].bssid == bss_id

    def test_fix_bss_diag(self, fb, httpx_mock):
        bss_id = "02:00:00:00:00:08"
        httpx_mock.add_response(
            url=f"{API}/wifi/bss/{bss_id}/diag", method="POST", json={"success": True}
        )
        fb.wifi.fix_bss_diag(bss_id, ["network_security"])
        assert httpx_mock.get_requests()[-1].method == "POST"

    def test_bss_mlo_config(self, fb, httpx_mock):
        bss_id = "00:24:D4:AA:BB:CC"
        httpx_mock.add_response(
            url=f"{API}/wifi/bss/{bss_id}/mlo/config", json=api_ok(MLO_CONFIG_DATA)
        )
        m = fb.wifi.bss_mlo_config(bss_id)
        assert isinstance(m, WifiMLOConfig)
        assert m.partners == [0, 1]

    def test_bss_mlo_allowed_combs(self, fb, httpx_mock):
        bss_id = "00:24:D4:AA:BB:CC"
        httpx_mock.add_response(
            url=f"{API}/wifi/bss/{bss_id}/mlo/allowed_comb", json=api_ok([[0, 1], [0]])
        )
        combs = fb.wifi.bss_mlo_allowed_combs(bss_id)
        assert combs == [[0, 1], [0]]

    def test_wps_config(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/wps/config/", json=api_ok(WPS_CONFIG_DATA))
        cfg = fb.wifi.wps_config()
        assert isinstance(cfg, WifiWpsConfig)
        assert cfg.enabled is True

    def test_set_wps_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/wps/config/", method="PUT", json=api_ok({"enabled": False})
        )
        cfg = fb.wifi.set_wps_config(enabled=False)
        assert cfg.enabled is False

    def test_wps_sessions(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/wps/sessions/", json=api_ok([WPS_SESSION_DATA]))
        sessions = fb.wifi.wps_sessions()
        assert len(sessions) == 1
        assert isinstance(sessions[0], WifiWpsSession)
        assert sessions[0].result == "failed_timeout"
        assert sessions[0].active is False

    def test_wps_sessions_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/wps/sessions/", json=api_ok([]))
        assert fb.wifi.wps_sessions() == []

    def test_start_wps(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/wps/start/", method="POST", json=api_ok(1))
        session_id = fb.wifi.start_wps("14:0C:76:87:04:38")
        assert session_id == 1

    def test_clear_wps_sessions(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/wps/sessions/", method="DELETE", json={"success": True}
        )
        fb.wifi.clear_wps_sessions()
        assert httpx_mock.get_requests()[-1].method == "DELETE"

    def test_custom_keys_config(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/custom_keys/config/", json=api_ok(CUSTOM_KEY_CONFIG_DATA)
        )
        cfg = fb.wifi.custom_keys_config()
        assert isinstance(cfg, WifiCustomKeyConfig)
        assert cfg.ssid == "Freebox-guest"
        assert cfg.ssid_read_only is False

    def test_set_custom_keys_config(self, fb, httpx_mock):
        updated = {**CUSTOM_KEY_CONFIG_DATA, "ssid": "my-guest"}
        httpx_mock.add_response(
            url=f"{API}/wifi/custom_keys/config/", method="PUT", json=api_ok(updated)
        )
        cfg = fb.wifi.set_custom_keys_config(ssid="my-guest")
        assert cfg.ssid == "my-guest"

    def test_custom_keys(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/custom_key/", json=api_ok([CUSTOM_KEY_DATA]))
        keys = fb.wifi.custom_keys()
        assert len(keys) == 1
        assert isinstance(keys[0], WifiCustomKey)
        assert keys[0].id == 8
        assert keys[0].remaining == 86376
        assert isinstance(keys[0].params, WifiCustomKeyParams)
        assert keys[0].params.access_type == "full"

    def test_custom_key(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/custom_key/8", json=api_ok(CUSTOM_KEY_DATA))
        k = fb.wifi.custom_key(8)
        assert isinstance(k, WifiCustomKey)
        assert k.id == 8

    def test_add_custom_key(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/custom_key/", method="POST", json=api_ok(CUSTOM_KEY_DATA)
        )
        k = fb.wifi.add_custom_key(description="soiree", duration=86400, access_type="full")
        assert isinstance(k, WifiCustomKey)
        assert httpx_mock.get_requests()[-1].method == "POST"

    def test_delete_custom_key(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/custom_key/8", method="DELETE", json={"success": True}
        )
        fb.wifi.delete_custom_key(8)
        assert httpx_mock.get_requests()[-1].method == "DELETE"

    def test_temp_disable_state(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/temp_disable", json=api_ok({"remaining": 267}))
        remaining = fb.wifi.temp_disable_state()
        assert remaining == 267

    def test_temp_disable_state_zero(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/wifi/temp_disable", json=api_ok({"remaining": 0}))
        assert fb.wifi.temp_disable_state() == 0

    def test_temp_disable(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/wifi/temp_disable", method="POST", json={"success": True}
        )
        fb.wifi.temp_disable(1200, "2d4g")
        assert httpx_mock.get_requests()[-1].method == "POST"


# ── New dataclass unit tests ───────────────────────────────────────────────────

class TestWifiDiagItem:
    def test_ap_item(self):
        item = WifiDiagItem._from_dict(DIAG_ITEM_AP)
        assert item.ap_id == 0
        assert item.bssid is None
        assert item.code == "channel_width"
        assert item.severity == "minor"

    def test_bss_item(self):
        item = WifiDiagItem._from_dict(DIAG_ITEM_BSS)
        assert item.bssid == "02:00:00:00:00:08"
        assert item.ap_id is None
        assert item.severity == "major"

    def test_defaults(self):
        item = WifiDiagItem._from_dict({})
        assert item.code == ""
        assert item.severity == ""
        assert item.ap_id is None
        assert item.bssid is None


class TestWifiDiag:
    def test_fields(self):
        d = WifiDiag._from_dict(DIAG_DATA)
        assert len(d.aps) == 1
        assert len(d.bsss) == 1

    def test_empty(self):
        d = WifiDiag._from_dict({})
        assert d.aps == []
        assert d.bsss == []


class TestWifiWpsConfig:
    def test_fields(self):
        c = WifiWpsConfig._from_dict({"enabled": True})
        assert c.enabled is True

    def test_defaults(self):
        c = WifiWpsConfig._from_dict({})
        assert c.enabled is False


class TestWifiWpsSession:
    def test_fields(self):
        s = WifiWpsSession._from_dict(WPS_SESSION_DATA)
        assert s.id == 1
        assert s.bss_uuid == "6a55ea3d-29fa-4bd9-b1e3-22a49a3ca134"
        assert s.ssid == "r0ro 5G"
        assert s.active is False
        assert s.result == "failed_timeout"
        assert s.start_date == 1516012531
        assert s.end_date == 1516012651
        assert s.mac == "00:00:00:00:00:00"

    def test_defaults(self):
        s = WifiWpsSession._from_dict({})
        assert s.id == 0
        assert s.active is False
        assert s.result == ""


class TestWifiCustomKeyConfig:
    def test_fields(self):
        c = WifiCustomKeyConfig._from_dict(CUSTOM_KEY_CONFIG_DATA)
        assert c.ssid == "Freebox-guest"
        assert c.ssid_read_only is False
        assert c.hide_ssid is False
        assert c.encryption == "wpa2_psk"

    def test_defaults(self):
        c = WifiCustomKeyConfig._from_dict({})
        assert c.ssid == ""
        assert c.ssid_read_only is False


class TestWifiCustomKeyParams:
    def test_fields(self):
        p = WifiCustomKeyParams._from_dict(CUSTOM_KEY_PARAMS_DATA)
        assert p.description == "soiree"
        assert p.key == "YY5Sg74W3VNxrmfwAz7aCY7OVqRVG2JN"
        assert p.max_use_count == 100
        assert p.duration == 86400
        assert p.access_type == "full"

    def test_defaults(self):
        p = WifiCustomKeyParams._from_dict({})
        assert p.description == ""
        assert p.max_use_count == 0
        assert p.access_type == "full"


class TestWifiCustomKey:
    def test_fields(self):
        k = WifiCustomKey._from_dict(CUSTOM_KEY_DATA)
        assert k.id == 8
        assert k.remaining == 86376
        assert isinstance(k.params, WifiCustomKeyParams)
        assert k.params.access_type == "full"

    def test_no_params(self):
        k = WifiCustomKey._from_dict({"id": 1, "remaining": 0})
        assert k.params is None

    def test_defaults(self):
        k = WifiCustomKey._from_dict({})
        assert k.id == 0
        assert k.remaining == 0


class TestWifiMLOConfig:
    def test_fields(self):
        m = WifiMLOConfig._from_dict(MLO_CONFIG_DATA)
        assert m.partners == [0, 1]

    def test_empty(self):
        m = WifiMLOConfig._from_dict({})
        assert m.partners == []
