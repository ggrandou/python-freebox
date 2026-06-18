"""Freebox File Upload API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class UploadTask:
    """A file upload task (GET /upload/)."""

    id: int
    size: int
    uploaded: int
    status: str
    start_date: int
    last_update: int
    upload_name: str
    dirname: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UploadTask:
        return cls(
            id=d.get("id", 0),
            size=d.get("size", 0),
            uploaded=d.get("uploaded", 0),
            status=d.get("status", ""),
            start_date=d.get("start_date", 0),
            last_update=d.get("last_update", 0),
            upload_name=d.get("upload_name", ""),
            dirname=d.get("dirname", ""),
        )


class Upload:
    """Freebox File Upload API.

    Obtained via ``fb.upload``::

        ws_url = fb.upload.ws_url()
        tasks = fb.upload.tasks()
        task = fb.upload.task(task_id)
        fb.upload.cancel(task_id)
        fb.upload.delete(task_id)

    To actually upload files, connect to the WebSocket URL returned by
    ``ws_url()`` and follow the WebSocket File Upload protocol.
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def ws_url(self) -> str:
        """Return the WebSocket URL for the file upload API."""
        return self._client._ws_url("ws/upload")

    def tasks(self) -> list[UploadTask]:
        """Return the list of all upload tasks."""
        result = self._client.get("upload/")
        return [UploadTask._from_dict(t) for t in result] if result else []

    def task(self, id: int) -> UploadTask:
        """Return the upload task with the given id."""
        return UploadTask._from_dict(self._client.get(f"upload/{id}"))

    def cancel(self, id: int) -> None:
        """Cancel an in-progress upload."""
        self._client.delete(f"upload/{id}/cancel")

    def delete(self, id: int) -> None:
        """Delete an upload task."""
        self._client.delete(f"upload/{id}")
