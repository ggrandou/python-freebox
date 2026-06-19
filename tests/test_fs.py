"""Unit tests for the File System API."""
import base64

import pytest

from freebox import FileInfo, Freebox, Fs, FsLsResult, FsTask
from tests.conftest import (
    APP_ID,
    APP_NAME,
    APP_VERSION,
    DEVICE_NAME,
    DISCOVERY_DATA,
    SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API = f"{BASE}/api/v16"

_ROOT_PATH = base64.b64encode(b"/").decode()
_HOME_PATH = base64.b64encode(b"/Disque dur").decode()
_FILE_PATH = base64.b64encode(b"/Disque dur/test.txt").decode()


# ── Fixtures ──────────────────────────────────────────────────────────────────

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
        json=api_ok({"session_token": SESSION_TOKEN, "permissions": {"explorer": True}}),
    )
    client = Freebox(
        app_id=APP_ID,
        app_name=APP_NAME,
        app_version=APP_VERSION,
        device_name=DEVICE_NAME,
        token="test-app-token",
        on_pending=lambda _: None,
    )
    client.open()
    return client


# ── Test data ─────────────────────────────────────────────────────────────────

FILEINFO_DICT = {
    "path": _HOME_PATH,
    "name": "Disque dur",
    "mimetype": "inode/directory",
    "type": "dir",
    "size": 0,
    "modification": 1700000000,
    "index": 0,
    "link": False,
    "hidden": False,
    "target": "",
    "foldercount": 3,
    "filecount": 12,
}

FILEINFO2_DICT = {
    "path": _FILE_PATH,
    "name": "test.txt",
    "mimetype": "text/plain",
    "type": "file",
    "size": 1024,
    "modification": 1700001000,
    "index": 1,
    "link": False,
    "hidden": False,
    "target": "",
    "foldercount": 0,
    "filecount": 0,
}

FSTASK_DICT = {
    "id": 42,
    "type": "cp",
    "state": "running",
    "error": "",
    "created_ts": 1700000000,
    "started_ts": 1700000001,
    "done_ts": 0,
    "duration": 5,
    "progress": 5000,
    "eta": 3,
    "from": "/Disque dur/src",
    "to": "/Disque dur/dst",
    "nfiles": 10,
    "nfiles_done": 5,
    "total_bytes": 2000000,
    "total_bytes_done": 1000000,
    "curr_bytes": 500000,
    "curr_bytes_done": 250000,
    "rate": 100000,
    "src": [_HOME_PATH],
    "dst": _FILE_PATH,
}


# ── FileInfo ──────────────────────────────────────────────────────────────────

def test_fileinfo_from_dict():
    fi = FileInfo._from_dict(FILEINFO_DICT)
    assert fi.name == "Disque dur"
    assert fi.type == "dir"
    assert fi.size == 0
    assert fi.foldercount == 3
    assert fi.filecount == 12
    assert fi.path_decoded == "/Disque dur"
    assert fi.target_decoded == ""


def test_fileinfo_path_decoded():
    fi = FileInfo._from_dict(FILEINFO2_DICT)
    assert fi.path_decoded == "/Disque dur/test.txt"
    assert fi.name == "test.txt"
    assert fi.size == 1024


def test_fileinfo_link_target():
    d = dict(FILEINFO_DICT, link=True, target=_FILE_PATH)
    fi = FileInfo._from_dict(d)
    assert fi.link is True
    assert fi.target_decoded == "/Disque dur/test.txt"


def test_fileinfo_empty_target():
    fi = FileInfo._from_dict(FILEINFO_DICT)
    assert fi.target_decoded == ""


def test_fileinfo_defaults():
    fi = FileInfo._from_dict({})
    assert fi.name == ""
    assert fi.type == ""
    assert fi.size == 0
    assert fi.path_decoded == ""


# ── FsLsResult ────────────────────────────────────────────────────────────────

def test_fslsresult_from_dict():
    d = {"entries": [FILEINFO_DICT, FILEINFO2_DICT], "cursor": "next-cursor"}
    r = FsLsResult._from_dict(d)
    assert len(r.entries) == 2
    assert r.cursor == "next-cursor"
    assert r.entries[0].name == "Disque dur"
    assert r.entries[1].name == "test.txt"


def test_fslsresult_empty_entries():
    r = FsLsResult._from_dict({"entries": None, "cursor": ""})
    assert r.entries == []
    assert r.cursor == ""


def test_fslsresult_no_cursor():
    r = FsLsResult._from_dict({"entries": [FILEINFO_DICT]})
    assert r.cursor == ""
    assert len(r.entries) == 1


# ── FsTask ────────────────────────────────────────────────────────────────────

def test_fstask_from_dict():
    t = FsTask._from_dict(FSTASK_DICT)
    assert t.id == 42
    assert t.type == "cp"
    assert t.state == "running"
    assert t.progress == 5000
    assert t.from_path == "/Disque dur/src"
    assert t.to == "/Disque dur/dst"
    assert t.nfiles == 10
    assert t.nfiles_done == 5
    assert t.rate == 100000
    assert t.src == [_HOME_PATH]


def test_fstask_defaults():
    t = FsTask._from_dict({})
    assert t.id == 0
    assert t.type == ""
    assert t.from_path == ""
    assert t.src == []
    assert t.dst == ""


# ── API: ls ───────────────────────────────────────────────────────────────────

def test_ls(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/ls/{_HOME_PATH}",
        json=api_ok({"entries": [FILEINFO_DICT, FILEINFO2_DICT], "cursor": ""}),
    )
    result = fb.fs.ls(_HOME_PATH)
    assert isinstance(result, FsLsResult)
    assert len(result.entries) == 2
    assert result.entries[0].name == "Disque dur"


def test_ls_with_params(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/ls/{_HOME_PATH}?onlyFolder=true&limit=10",
        json=api_ok({"entries": [FILEINFO_DICT], "cursor": "abc"}),
    )
    result = fb.fs.ls(_HOME_PATH, only_folder=True, limit=10)
    assert result.cursor == "abc"
    assert len(result.entries) == 1


def test_ls_null_result(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/ls/{_HOME_PATH}",
        json=api_ok(None),
    )
    result = fb.fs.ls(_HOME_PATH)
    assert result.entries == []
    assert result.cursor == ""


# ── API: info ─────────────────────────────────────────────────────────────────

def test_info(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/info/{_HOME_PATH}",
        json=api_ok(FILEINFO_DICT),
    )
    fi = fb.fs.info(_HOME_PATH)
    assert isinstance(fi, FileInfo)
    assert fi.name == "Disque dur"
    assert fi.type == "dir"


def test_batch_info(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/info",
        method="POST",
        json=api_ok([FILEINFO_DICT, FILEINFO2_DICT]),
    )
    items = fb.fs.batch_info([_HOME_PATH, _FILE_PATH])
    assert len(items) == 2
    assert items[0].name == "Disque dur"
    assert items[1].name == "test.txt"


def test_batch_info_null(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/info",
        method="POST",
        json=api_ok(None),
    )
    items = fb.fs.batch_info([_HOME_PATH])
    assert items == []


# ── API: tasks ────────────────────────────────────────────────────────────────

def test_tasks(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/tasks/",
        json=api_ok([FSTASK_DICT]),
    )
    tasks = fb.fs.tasks()
    assert len(tasks) == 1
    assert tasks[0].id == 42


def test_tasks_empty(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/fs/tasks/", json=api_ok([]))
    assert fb.fs.tasks() == []


def test_tasks_null(fb, httpx_mock):
    httpx_mock.add_response(url=f"{API}/fs/tasks/", json=api_ok(None))
    assert fb.fs.tasks() == []


def test_task(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/tasks/42",
        json=api_ok(FSTASK_DICT),
    )
    t = fb.fs.task(42)
    assert t.id == 42
    assert t.type == "cp"


def test_update_task(fb, httpx_mock):
    paused = dict(FSTASK_DICT, state="paused")
    httpx_mock.add_response(
        url=f"{API}/fs/tasks/42",
        method="PUT",
        json=api_ok(paused),
    )
    t = fb.fs.update_task(42, "paused")
    assert t.state == "paused"


def test_delete_task(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/tasks/42",
        method="DELETE",
        json=api_ok(None),
    )
    fb.fs.delete_task(42)


def test_task_hash(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/tasks/42/hash",
        json=api_ok({"hash": "d41d8cd98f00b204e9800998ecf8427e"}),
    )
    h = fb.fs.task_hash(42)
    assert h == "d41d8cd98f00b204e9800998ecf8427e"


# ── API: file operations ──────────────────────────────────────────────────────

def test_mv(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/mv/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="mv")),
    )
    t = fb.fs.mv([_FILE_PATH], _HOME_PATH)
    assert isinstance(t, FsTask)
    assert t.type == "mv"


def test_cp(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/cp/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="cp")),
    )
    t = fb.fs.cp([_FILE_PATH], _HOME_PATH)
    assert t.type == "cp"


def test_rm(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/rm/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="rm")),
    )
    t = fb.fs.rm([_FILE_PATH])
    assert t.type == "rm"


def test_cat(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/cat/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="cat")),
    )
    t = fb.fs.cat([_FILE_PATH], _HOME_PATH)
    assert t.type == "cat"


def test_archive(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/archive/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="archive")),
    )
    t = fb.fs.archive([_FILE_PATH], _HOME_PATH)
    assert t.type == "archive"


def test_extract(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/extract/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="extract")),
    )
    t = fb.fs.extract(_FILE_PATH, _HOME_PATH, password="secret")
    assert t.type == "extract"


def test_repair(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/repair/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="repair")),
    )
    t = fb.fs.repair(_FILE_PATH)
    assert t.type == "repair"


def test_hash(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/hash/",
        method="POST",
        json=api_ok(dict(FSTASK_DICT, type="hash", state="queued")),
    )
    t = fb.fs.hash(_FILE_PATH, "sha1")
    assert t.type == "hash"


# ── API: synchronous operations ───────────────────────────────────────────────

def test_mkdir(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/fs/mkdir/",
        method="POST",
        json=api_ok(None),
    )
    fb.fs.mkdir(_HOME_PATH, "NewFolder")


def test_rename(fb, httpx_mock):
    new_path = base64.b64encode(b"/Disque dur/renamed.txt").decode()
    httpx_mock.add_response(
        url=f"{API}/fs/rename/",
        method="POST",
        json=api_ok(new_path),
    )
    result = fb.fs.rename(_FILE_PATH, "renamed.txt")
    assert result == new_path


# ── API: download ──────────────────────────────────────────────────────────────

def test_download(fb, httpx_mock):
    httpx_mock.add_response(
        url=f"{API}/dl/{_FILE_PATH}",
        content=b"Hello, World!",
    )
    data = fb.fs.download(_FILE_PATH)
    assert data == b"Hello, World!"


# ── Fs property on Freebox ────────────────────────────────────────────────────

def test_freebox_fs_property(fb):
    assert isinstance(fb.fs, Fs)
