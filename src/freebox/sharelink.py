"""Freebox file sharing link API."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class ShareLink:
    """A file sharing link (GET/POST/DELETE /share_link/).

    The ``path`` field is the base64-encoded absolute path on the Freebox
    storage.  Use ``path_decoded`` to get the plain string.
    """

    token: str
    path: str
    name: str
    expire: int
    fullurl: str

    @property
    def path_decoded(self) -> str:
        """Decoded path (base64 → plain string)."""
        if not self.path:
            return ""
        try:
            return base64.b64decode(self.path).decode()
        except Exception:
            return self.path

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ShareLink:
        return cls(
            token=d.get("token", ""),
            path=d.get("path", ""),
            name=d.get("name", ""),
            expire=d.get("expire", 0),
            fullurl=d.get("fullurl", ""),
        )


class ShareLinks:
    """Freebox file sharing link API.

    Obtained via ``fb.sharelinks``::

        links = fb.sharelinks.list()
        for link in links:
            print(link.token, link.path_decoded, link.fullurl)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def list(self) -> list[ShareLink]:
        """Return all active file sharing links."""
        result = self._client.get("share_link/")
        return [ShareLink._from_dict(l) for l in result] if result else []

    def get(self, token: str) -> ShareLink:
        """Return the file sharing link with the given token."""
        return ShareLink._from_dict(self._client.get(f"share_link/{token}"))

    def create(self, path: str, expire: int = 0) -> ShareLink:
        """Create a new file sharing link.

        ``path`` must be the base64-encoded absolute path on the Freebox
        storage.  ``expire`` is a Unix timestamp (0 = no expiration).
        """
        return ShareLink._from_dict(
            self._client.post("share_link/", json={"path": path, "expire": expire})
        )

    def delete(self, token: str) -> None:
        """Delete a file sharing link."""
        self._client.delete(f"share_link/{token}")
