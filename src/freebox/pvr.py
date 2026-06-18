"""Freebox PVR (TV Recording) API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class PvrConfig:
    """PVR global configuration (GET /pvr/config/)."""

    margin_before: int
    margin_after: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PvrConfig:
        return cls(
            margin_before=d.get("margin_before", 0),
            margin_after=d.get("margin_after", 0),
        )


@dataclass
class PvrQuota:
    """PVR disk quota info (GET /pvr/quota/)."""

    quota_exceeded: bool
    needed_tresh: int
    cur_tresh: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PvrQuota:
        return cls(
            quota_exceeded=d.get("quota_exceeded", False),
            needed_tresh=d.get("needed_tresh", 0),
            cur_tresh=d.get("cur_tresh", 0),
        )


@dataclass
class PvrProgrammed:
    """A programmed recording (GET /pvr/programmed/)."""

    id: int
    media: str
    path: str
    channel_uuid: str
    channel_name: str
    channel_type: str
    channel_quality: str
    broadcast_type: str
    name: str
    subname: str
    start: int
    end: int
    state: str
    error: str
    enabled: bool
    altered: bool
    conflict: bool
    has_record_gen: bool
    record_gen_id: int
    overlap_list: list[int] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PvrProgrammed:
        return cls(
            id=d.get("id", 0),
            media=d.get("media", ""),
            path=d.get("path", ""),
            channel_uuid=d.get("channel_uuid", ""),
            channel_name=d.get("channel_name", ""),
            channel_type=d.get("channel_type", ""),
            channel_quality=d.get("channel_quality", ""),
            broadcast_type=d.get("broadcast_type", ""),
            name=d.get("name", ""),
            subname=d.get("subname", ""),
            start=d.get("start", 0),
            end=d.get("end", 0),
            state=d.get("state", ""),
            error=d.get("error", ""),
            enabled=d.get("enabled", False),
            altered=d.get("altered", False),
            conflict=d.get("conflict", False),
            has_record_gen=d.get("has_record_gen", False),
            record_gen_id=d.get("record_gen_id", 0),
            overlap_list=list(d.get("overlap_list") or []),
        )


@dataclass
class PvrFinished:
    """A finished recording (GET /pvr/finished/)."""

    id: int
    media: str
    path: str
    filename: str
    byte_size: int
    channel_uuid: str
    channel_name: str
    channel_type: str
    channel_quality: str
    broadcast_type: str
    name: str
    subname: str
    start: int
    end: int
    state: str
    error: str
    enabled: bool
    altered: bool
    secure: bool
    has_record_gen: bool
    record_gen_id: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PvrFinished:
        return cls(
            id=d.get("id", 0),
            media=d.get("media", ""),
            path=d.get("path", ""),
            filename=d.get("filename", ""),
            byte_size=d.get("byte_size", 0),
            channel_uuid=d.get("channel_uuid", ""),
            channel_name=d.get("channel_name", ""),
            channel_type=d.get("channel_type", ""),
            channel_quality=d.get("channel_quality", ""),
            broadcast_type=d.get("broadcast_type", ""),
            name=d.get("name", ""),
            subname=d.get("subname", ""),
            start=d.get("start", 0),
            end=d.get("end", 0),
            state=d.get("state", ""),
            error=d.get("error", ""),
            enabled=d.get("enabled", False),
            altered=d.get("altered", False),
            secure=d.get("secure", False),
            has_record_gen=d.get("has_record_gen", False),
            record_gen_id=d.get("record_gen_id", 0),
        )


@dataclass
class PvrMedia:
    """A storage medium for PVR recordings (GET /pvr/media/)."""

    media: str
    free_bytes: int
    total_bytes: int
    record_time: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> PvrMedia:
        return cls(
            media=d.get("media", ""),
            free_bytes=d.get("free_bytes", 0),
            total_bytes=d.get("total_bytes", 0),
            record_time=dict(d.get("record_time") or {}),
        )


class Pvr:
    """Freebox PVR (TV Recording) API.

    Obtained via ``fb.pvr``::

        cfg = fb.pvr.config()
        quota = fb.pvr.quota()
        scheduled = fb.pvr.programmed()
        fb.pvr.create_programmed(start=..., end=..., channel_uuid=..., name=...)
        finished = fb.pvr.finished()
        media = fb.pvr.media()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Config ─────────────────────────────────────────────────────────────────

    def config(self) -> PvrConfig:
        """Return the current PVR configuration."""
        return PvrConfig._from_dict(self._client.get("pvr/config/"))

    def set_config(
        self, *, margin_before: int | None = None, margin_after: int | None = None
    ) -> PvrConfig:
        """Update the PVR configuration."""
        payload: dict[str, Any] = {}
        if margin_before is not None:
            payload["margin_before"] = margin_before
        if margin_after is not None:
            payload["margin_after"] = margin_after
        return PvrConfig._from_dict(self._client.put("pvr/config/", json=payload))

    # ── Quota ──────────────────────────────────────────────────────────────────

    def quota(self) -> PvrQuota:
        """Return the current PVR disk quota information."""
        return PvrQuota._from_dict(self._client.get("pvr/quota/"))

    def request_quota(self) -> PvrQuota:
        """Request the next quota threshold (auto-adjusted)."""
        return PvrQuota._from_dict(self._client.put("pvr/quota/", json={}))

    # ── Programmed records ─────────────────────────────────────────────────────

    def programmed(self) -> list[PvrProgrammed]:
        """Return the list of all programmed recordings."""
        result = self._client.get("pvr/programmed/")
        return [PvrProgrammed._from_dict(r) for r in result] if result else []

    def programmed_record(self, id: int) -> PvrProgrammed:
        """Return the programmed recording with the given id."""
        return PvrProgrammed._from_dict(self._client.get(f"pvr/programmed/{id}"))

    def create_programmed(
        self,
        *,
        start: int,
        end: int,
        channel_uuid: str,
        name: str,
        subname: str = "",
        media: str = "",
        path: str = "",
        channel_quality: str = "auto",
    ) -> PvrProgrammed:
        """Create a new programmed recording."""
        payload: dict[str, Any] = {
            "start": start,
            "end": end,
            "channel_uuid": channel_uuid,
            "name": name,
        }
        if subname:
            payload["subname"] = subname
        if media:
            payload["media"] = media
        if path:
            payload["path"] = path
        if channel_quality != "auto":
            payload["channel_quality"] = channel_quality
        return PvrProgrammed._from_dict(
            self._client.post("pvr/programmed/", json=payload)
        )

    def update_programmed(self, id: int, **kwargs: Any) -> PvrProgrammed:
        """Update a programmed recording."""
        return PvrProgrammed._from_dict(
            self._client.put(f"pvr/programmed/{id}", json=kwargs)
        )

    def delete_programmed(self, id: int) -> None:
        """Delete a programmed recording."""
        self._client.delete(f"pvr/programmed/{id}")

    # ── Finished records ───────────────────────────────────────────────────────

    def finished(self) -> list[PvrFinished]:
        """Return the list of all finished recordings."""
        result = self._client.get("pvr/finished/")
        return [PvrFinished._from_dict(r) for r in result] if result else []

    def finished_record(self, id: int) -> PvrFinished:
        """Return the finished recording with the given id."""
        return PvrFinished._from_dict(self._client.get(f"pvr/finished/{id}"))

    def update_finished(self, id: int, **kwargs: Any) -> PvrFinished:
        """Update a finished recording (name, subname)."""
        return PvrFinished._from_dict(
            self._client.put(f"pvr/finished/{id}", json=kwargs)
        )

    def delete_finished(self, id: int) -> None:
        """Delete a finished recording and its associated file."""
        self._client.delete(f"pvr/finished/{id}")

    # ── Storage media ──────────────────────────────────────────────────────────

    def media(self) -> list[PvrMedia]:
        """Return the list of storage media available for recordings."""
        result = self._client.get("pvr/media/")
        return [PvrMedia._from_dict(m) for m in result] if result else []
