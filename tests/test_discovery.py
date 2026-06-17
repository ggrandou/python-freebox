import pytest

from freebox.discovery import DiscoveryInfo, discover_http, discover_remote_port
from tests.conftest import DISCOVERY_DATA

BASE_URL = "https://mafreebox.freebox.fr"


# ── DiscoveryInfo ──────────────────────────────────────────────────────────────

class TestDiscoveryInfo:
    def test_from_dict(self, discovery_info):
        assert discovery_info.uid            == "test-uid-1234"
        assert discovery_info.device_name    == "Freebox Server"
        assert discovery_info.box_model      == "fbxgw8-r1/full"
        assert discovery_info.box_model_name == "Freebox v8 (r1)"
        assert discovery_info.api_version    == "16.0"
        assert discovery_info.api_base_url   == "/api/"
        assert discovery_info.api_domain     == "test.fbxos.fr"
        assert discovery_info.https_available is True
        assert discovery_info.https_port     == 3615

    def test_defaults_for_missing_fields(self):
        info = DiscoveryInfo._from_dict({})
        assert info.uid            == ""
        assert info.api_base_url   == "/api/"
        assert info.https_available is False
        assert info.https_port     == 443

    def test_api_major_version(self, discovery_info):
        assert discovery_info.api_major_version == 16

    def test_api_major_version_minor_ignored(self):
        info = DiscoveryInfo._from_dict({**DISCOVERY_DATA, "api_version": "10.2"})
        assert info.api_major_version == 10

    def test_local_url(self, discovery_info):
        assert discovery_info.local_url == "https://mafreebox.freebox.fr/api/"

    def test_remote_url(self, discovery_info):
        assert discovery_info.remote_url == "https://test.fbxos.fr:3615/api/"


# ── discover_http ──────────────────────────────────────────────────────────────

class TestDiscoverHttp:
    def test_https_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/api_version",
            json=DISCOVERY_DATA,
        )
        info = discover_http()
        assert info.uid == "test-uid-1234"
        assert info.api_major_version == 16

    def test_fallback_to_http_on_https_failure(self, httpx_mock):
        httpx_mock.add_exception(
            Exception("SSL error"),
            url=f"{BASE_URL}/api_version",
        )
        httpx_mock.add_response(
            url=f"http://mafreebox.freebox.fr/api_version",
            json=DISCOVERY_DATA,
        )
        info = discover_http()
        assert info.uid == "test-uid-1234"

    def test_custom_host(self, httpx_mock):
        httpx_mock.add_response(
            url="https://192.168.1.254/api_version",
            json=DISCOVERY_DATA,
        )
        info = discover_http("192.168.1.254")
        assert info.uid == "test-uid-1234"


# ── discover_remote_port ───────────────────────────────────────────────────────

class TestDiscoverRemotePort:
    def test_returns_none_without_dnspython(self, monkeypatch):
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "dns.resolver":
                raise ImportError("dnspython not installed")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        assert discover_remote_port("test.fbxos.fr") is None

    def test_returns_none_on_dns_error(self, monkeypatch):
        import freebox.discovery as disc

        def failing_resolve(*_a, **_kw):
            raise Exception("NXDOMAIN")

        class FakeDns:
            class resolver:
                resolve = staticmethod(failing_resolve)

        monkeypatch.setattr(disc, "dns", FakeDns(), raising=False)
        assert discover_remote_port("test.fbxos.fr") is None
