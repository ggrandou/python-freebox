"""Freebox call log and voicemail API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class CallEntry:
    """A call log entry (GET /call/log/)."""

    id: int
    type: str
    datetime: int
    number: str
    name: str
    duration: int
    new: bool
    contact_id: int
    line_id: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> CallEntry:
        return cls(
            id=d.get("id", 0),
            type=d.get("type", ""),
            datetime=d.get("datetime", 0),
            number=d.get("number", ""),
            name=d.get("name", ""),
            duration=d.get("duration", 0),
            new=d.get("new", False),
            contact_id=d.get("contact_id", 0),
            line_id=d.get("line_id", 0),
        )


@dataclass
class CallAccount:
    """Phone account information (GET /call/account)."""

    phone_number: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> CallAccount:
        return cls(phone_number=d.get("phone_number", ""))


@dataclass
class VoicemailEntry:
    """A voicemail entry (GET /call/voicemail/)."""

    id: str
    country_code: str
    phone_number: str
    date: int
    read: bool
    duration: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VoicemailEntry:
        return cls(
            id=d.get("id", ""),
            country_code=str(d.get("country_code", "")),
            phone_number=d.get("phone_number", ""),
            date=d.get("date", 0),
            read=d.get("read", False),
            duration=d.get("duration", 0),
        )


class Call:
    """Freebox call log and voicemail API.

    Obtained via ``fb.call``::

        entries = fb.call.list()
        for e in entries:
            print(e.type, e.number, e.name)

        vms = fb.call.voicemails()
        for vm in vms:
            print(vm.phone_number, vm.duration)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Call log ───────────────────────────────────────────────────────────────

    def list(self) -> list[CallEntry]:
        """Return all call log entries."""
        result = self._client.get("call/log/")
        return [CallEntry._from_dict(e) for e in result] if result else []

    def get(self, call_id: int) -> CallEntry:
        """Return the call log entry with the given id."""
        return CallEntry._from_dict(self._client.get(f"call/log/{call_id}"))

    def mark_as_read(self, call_id: int) -> CallEntry:
        """Mark a call log entry as read (new=False)."""
        return CallEntry._from_dict(
            self._client.put(f"call/log/{call_id}", json={"new": False})
        )

    def delete(self, call_id: int) -> None:
        """Delete the call log entry with the given id."""
        self._client.delete(f"call/log/{call_id}")

    def delete_all(self) -> None:
        """Delete all call log entries."""
        self._client.post("call/log/delete_all/")

    def mark_all_as_read(self) -> None:
        """Mark all call log entries as read."""
        self._client.post("call/log/mark_all_as_read/")

    # ── Account ────────────────────────────────────────────────────────────────

    def account(self) -> CallAccount:
        """Return the phone account (subscription number)."""
        return CallAccount._from_dict(self._client.get("call/account"))

    # ── Voicemail ──────────────────────────────────────────────────────────────

    def voicemails(self) -> list[VoicemailEntry]:
        """Return all voicemail entries."""
        result = self._client.get("call/voicemail/")
        return [VoicemailEntry._from_dict(v) for v in result] if result else []

    def get_voicemail(self, vm_id: str) -> VoicemailEntry:
        """Return the voicemail entry with the given id."""
        return VoicemailEntry._from_dict(self._client.get(f"call/voicemail/{vm_id}"))

    def mark_voicemail_as_read(self, vm_id: str) -> VoicemailEntry:
        """Mark a voicemail entry as read."""
        return VoicemailEntry._from_dict(
            self._client.put(f"call/voicemail/{vm_id}", json={"read": True})
        )

    def delete_voicemail(self, vm_id: str) -> None:
        """Delete the voicemail entry with the given id."""
        self._client.delete(f"call/voicemail/{vm_id}")

    def download_voicemail(self, vm_id: str) -> bytes:
        """Download the voicemail audio file in WAV format."""
        return self._client.get_bytes(f"call/voicemail/{vm_id}/audio_file")
