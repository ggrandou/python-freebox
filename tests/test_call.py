"""Unit tests for the call log and voicemail API."""
import pytest

from freebox import Call, CallAccount, CallEntry, Freebox, VoicemailEntry
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

CALL_1 = {
    "id": 69,
    "type": "missed",
    "datetime": 1359546363,
    "number": "0102030405",
    "name": "Romain Bureau",
    "duration": 1,
    "new": True,
    "contact_id": 56,
    "line_id": 0,
}

CALL_2 = {
    "id": 68,
    "type": "outgoing",
    "datetime": 1359545960,
    "number": "**1",
    "name": "**1",
    "duration": 5,
    "new": False,
    "contact_id": 0,
    "line_id": 0,
}

VM_1 = {
    "id": "20221215_154135_r0334371508.au",
    "country_code": "33",
    "phone_number": "699999999",
    "date": 1671115295,
    "read": False,
    "duration": 8,
}


# ── CallEntry ──────────────────────────────────────────────────────────────────

class TestCallEntry:
    def test_from_dict(self):
        e = CallEntry._from_dict(CALL_1)
        assert e.id == 69
        assert e.type == "missed"
        assert e.datetime == 1359546363
        assert e.number == "0102030405"
        assert e.name == "Romain Bureau"
        assert e.duration == 1
        assert e.new is True
        assert e.contact_id == 56
        assert e.line_id == 0

    def test_from_dict_defaults(self):
        e = CallEntry._from_dict({})
        assert e.id == 0
        assert e.type == ""
        assert e.new is False


# ── CallAccount ────────────────────────────────────────────────────────────────

class TestCallAccount:
    def test_from_dict(self):
        a = CallAccount._from_dict({"phone_number": "0999999999"})
        assert a.phone_number == "0999999999"

    def test_from_dict_defaults(self):
        a = CallAccount._from_dict({})
        assert a.phone_number == ""


# ── VoicemailEntry ─────────────────────────────────────────────────────────────

class TestVoicemailEntry:
    def test_from_dict(self):
        v = VoicemailEntry._from_dict(VM_1)
        assert v.id == "20221215_154135_r0334371508.au"
        assert v.country_code == "33"
        assert v.phone_number == "699999999"
        assert v.date == 1671115295
        assert v.read is False
        assert v.duration == 8

    def test_country_code_int_coerced_to_str(self):
        v = VoicemailEntry._from_dict({**VM_1, "country_code": 33})
        assert v.country_code == "33"

    def test_from_dict_defaults(self):
        v = VoicemailEntry._from_dict({})
        assert v.id == ""
        assert v.read is False


# ── Call API ───────────────────────────────────────────────────────────────────

class TestCallApi:
    def test_list(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/call/log/", json=api_ok([CALL_1, CALL_2]))
        entries = fb.call.list()
        assert len(entries) == 2
        assert all(isinstance(e, CallEntry) for e in entries)
        assert entries[0].id == 69
        assert entries[1].id == 68

    def test_list_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/call/log/", json=api_ok([]))
        assert fb.call.list() == []

    def test_list_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/call/log/", json=api_ok(None))
        assert fb.call.list() == []

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/call/log/69", json=api_ok(CALL_1))
        e = fb.call.get(69)
        assert isinstance(e, CallEntry)
        assert e.id == 69

    def test_mark_as_read(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/call/log/69", method="PUT",
            json=api_ok({**CALL_1, "new": False}),
        )
        e = fb.call.mark_as_read(69)
        assert e.new is False

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/call/log/69", method="DELETE", json=api_ok(None)
        )
        fb.call.delete(69)

    def test_delete_all(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/call/log/delete_all/", method="POST", json=api_ok(None)
        )
        fb.call.delete_all()

    def test_mark_all_as_read(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/call/log/mark_all_as_read/", method="POST", json=api_ok(None)
        )
        fb.call.mark_all_as_read()

    def test_account(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/call/account", json=api_ok({"phone_number": "0999999999"})
        )
        a = fb.call.account()
        assert isinstance(a, CallAccount)
        assert a.phone_number == "0999999999"

    def test_voicemails(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/call/voicemail/", json=api_ok([VM_1]))
        vms = fb.call.voicemails()
        assert len(vms) == 1
        assert isinstance(vms[0], VoicemailEntry)
        assert vms[0].id == "20221215_154135_r0334371508.au"

    def test_voicemails_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/call/voicemail/", json=api_ok([]))
        assert fb.call.voicemails() == []

    def test_voicemails_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/call/voicemail/", json=api_ok(None))
        assert fb.call.voicemails() == []

    def test_get_voicemail(self, fb, httpx_mock):
        vm_id = "20221215_154135_r0334371508.au"
        httpx_mock.add_response(
            url=f"{API}/call/voicemail/{vm_id}", json=api_ok(VM_1)
        )
        v = fb.call.get_voicemail(vm_id)
        assert isinstance(v, VoicemailEntry)
        assert v.id == vm_id

    def test_mark_voicemail_as_read(self, fb, httpx_mock):
        vm_id = "20221215_154135_r0334371508.au"
        httpx_mock.add_response(
            url=f"{API}/call/voicemail/{vm_id}", method="PUT",
            json=api_ok({**VM_1, "read": True}),
        )
        v = fb.call.mark_voicemail_as_read(vm_id)
        assert v.read is True

    def test_delete_voicemail(self, fb, httpx_mock):
        vm_id = "20221215_154135_r0334371508.au"
        httpx_mock.add_response(
            url=f"{API}/call/voicemail/{vm_id}", method="DELETE", json=api_ok(None)
        )
        fb.call.delete_voicemail(vm_id)

    def test_download_voicemail(self, fb, httpx_mock):
        vm_id = "20221215_154135_r0334371508.au"
        wav_data = b"RIFF\x00\x00\x00\x00WAVEfmt "
        httpx_mock.add_response(
            url=f"{API}/call/voicemail/{vm_id}/audio_file",
            content=wav_data,
            headers={"Content-Type": "audio/wav"},
        )
        data = fb.call.download_voicemail(vm_id)
        assert data == wav_data


# ── Property ───────────────────────────────────────────────────────────────────

class TestCallProperty:
    def test_property(self, fb):
        assert isinstance(fb.call, Call)
