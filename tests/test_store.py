import json
import os
import stat

import pytest

from freebox.discovery import DiscoveryInfo
from freebox.store import CredentialStore, Credentials


APP_ID = "com.example.testapp"
TOKEN = "test-app-token-abc123"

DISCOVERY = DiscoveryInfo(
    uid="uid-1234",
    device_name="Freebox Server",
    box_model="fbxgw8-r1/full",
    box_model_name="Freebox v8 (r1)",
    api_version="16.0",
    api_base_url="/api/",
    api_domain="test.fbxos.fr",
    https_available=True,
    https_port=3615,
)


@pytest.fixture
def store(tmp_path, monkeypatch):
    """CredentialStore with XDG_CONFIG_HOME pointing to tmp_path, no local .freebox."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    return CredentialStore(APP_ID)


# ── Filename ───────────────────────────────────────────────────────────────────

def test_filename(store):
    assert store._filename == f"{APP_ID}.json"


# ── _write_dir: local .freebox exists ─────────────────────────────────────────

def test_write_dir_local_if_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    (tmp_path / ".freebox").mkdir()
    s = CredentialStore(APP_ID)
    assert s._write_dir() == tmp_path / ".freebox"


def test_write_dir_user_when_no_local(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = tmp_path / "config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config))
    s = CredentialStore(APP_ID)
    assert s._write_dir() == config / "freebox"


def test_write_dir_xdg_config_home(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    custom = tmp_path / "custom_xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(custom))
    s = CredentialStore(APP_ID)
    assert s._write_dir() == custom / "freebox"


# ── find ───────────────────────────────────────────────────────────────────────

def test_find_returns_none_when_missing(store):
    assert store.find() is None


def test_find_returns_path_when_present(store, tmp_path):
    d = tmp_path / "config" / "freebox"
    d.mkdir(parents=True)
    p = d / f"{APP_ID}.json"
    p.write_text(json.dumps({"app_token": TOKEN}))
    assert store.find() == p


def test_find_prefers_local_over_user(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    user_dir = tmp_path / "config" / "freebox"
    user_dir.mkdir(parents=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    local_dir = tmp_path / ".freebox"
    local_dir.mkdir()

    (user_dir / f"{APP_ID}.json").write_text(json.dumps({"app_token": "user-token"}))
    (local_dir / f"{APP_ID}.json").write_text(json.dumps({"app_token": "local-token"}))

    s = CredentialStore(APP_ID)
    assert s.find() == local_dir / f"{APP_ID}.json"


# ── load ───────────────────────────────────────────────────────────────────────

def test_load_returns_none_when_missing(store):
    assert store.load() is None


def test_load_returns_credentials(store, tmp_path):
    d = tmp_path / "config" / "freebox"
    d.mkdir(parents=True)
    (d / f"{APP_ID}.json").write_text(json.dumps({
        "app_token": TOKEN,
        "host": "mafreebox.freebox.fr",
        "port": 3615,
    }))
    creds = store.load()
    assert creds == Credentials(app_token=TOKEN, host="mafreebox.freebox.fr", port=3615)


def test_load_token_only(store, tmp_path):
    d = tmp_path / "config" / "freebox"
    d.mkdir(parents=True)
    (d / f"{APP_ID}.json").write_text(json.dumps({"app_token": TOKEN}))
    creds = store.load()
    assert creds == Credentials(app_token=TOKEN)


def test_save_roundtrip_with_app_info(store):
    creds = Credentials(
        app_token=TOKEN,
        app_id="com.example.myapp",
        app_name="My App",
        device_name="my-laptop",
    )
    store.save(creds)
    assert store.load() == creds


# ── save ───────────────────────────────────────────────────────────────────────

def test_save_creates_file(store, tmp_path):
    store.save(Credentials(app_token=TOKEN))
    assert store.find() is not None


def test_save_sets_permissions(store):
    store.save(Credentials(app_token=TOKEN))
    path = store.find()
    assert path is not None
    assert path.stat().st_mode & 0o777 == 0o600


def test_save_roundtrip(store):
    creds = Credentials(app_token=TOKEN, host="example.com", port=8443)
    store.save(creds)
    assert store.load() == creds


def test_save_omits_none_fields(store, tmp_path):
    store.save(Credentials(app_token=TOKEN))
    path = store.find()
    data = json.loads(path.read_text())
    assert "host" not in data
    assert "port" not in data
    assert "app_id" not in data
    assert "app_name" not in data
    assert "device_name" not in data
    assert "discovery" not in data


def test_save_roundtrip_with_discovery(store):
    creds = Credentials(app_token=TOKEN, host="mafreebox.freebox.fr", discovery=DISCOVERY)
    store.save(creds)
    assert store.load() == creds


def test_save_discovery_serialized_as_dict(store):
    store.save(Credentials(app_token=TOKEN, discovery=DISCOVERY))
    data = json.loads(store.find().read_text())
    d = data["discovery"]
    assert d["uid"] == DISCOVERY.uid
    assert d["device_name"] == DISCOVERY.device_name
    assert d["box_model"] == DISCOVERY.box_model
    assert d["box_model_name"] == DISCOVERY.box_model_name
    assert d["api_version"] == DISCOVERY.api_version
    assert d["api_base_url"] == DISCOVERY.api_base_url
    assert d["api_domain"] == DISCOVERY.api_domain
    assert d["https_available"] == DISCOVERY.https_available
    assert d["https_port"] == DISCOVERY.https_port


def test_save_updates_existing_in_place(tmp_path, monkeypatch):
    """Updating creds rewrites the same file, not a new location."""
    monkeypatch.chdir(tmp_path)
    local_dir = tmp_path / ".freebox"
    local_dir.mkdir()
    user_dir = tmp_path / "config" / "freebox"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    s = CredentialStore(APP_ID)

    s.save(Credentials(app_token="token1", host="mafreebox.freebox.fr"))
    first_path = s.find()
    assert first_path is not None

    s.save(Credentials(app_token="token2", host="other.fbxos.fr"))
    assert s.find() == first_path
    assert s.load().app_token == "token2"
    assert not (user_dir / f"{APP_ID}.json").exists()


# ── delete ─────────────────────────────────────────────────────────────────────

def test_delete_removes_file(store):
    store.save(Credentials(app_token=TOKEN))
    assert store.find() is not None
    store.delete()
    assert store.find() is None


def test_delete_noop_when_missing(store):
    store.delete()  # must not raise


# ── search order ───────────────────────────────────────────────────────────────

def test_search_order_local_user_global(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    user_dir = tmp_path / "config" / "freebox"
    user_dir.mkdir(parents=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    s = CredentialStore(APP_ID)
    (user_dir / f"{APP_ID}.json").write_text(json.dumps({"app_token": "user-token"}))
    assert s.load().app_token == "user-token"

    local_dir = tmp_path / ".freebox"
    local_dir.mkdir()
    (local_dir / f"{APP_ID}.json").write_text(json.dumps({"app_token": "local-token"}))
    assert s.load().app_token == "local-token"
