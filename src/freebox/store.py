"""Credential store: app_token, connection URL, and discovery info, keyed by app_id."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from freebox.discovery import DiscoveryInfo


@dataclass
class Credentials:
    """App token, application metadata, connection details, and discovery info."""

    app_token: str
    host: str | None = None
    port: int | None = None
    app_id: str | None = None
    app_name: str | None = None
    device_name: str | None = None
    discovery: DiscoveryInfo | None = field(default=None, compare=True)


class CredentialStore:
    """Locates and manages ``{app_id}.json`` credential files.

    Directories are searched in order when loading:

    1. ``<cwd>/.freebox/``
    2. ``$XDG_CONFIG_HOME/freebox/``  (default: ``~/.config/freebox/``)
    3. ``/etc/freebox/``

    The write target for new credentials is:

    - ``<cwd>/.freebox/``  if that directory already exists
    - ``/etc/freebox/``    if running as root (uid 0)
    - ``$XDG_CONFIG_HOME/freebox/``  otherwise

    When updating existing credentials the file is always rewritten in place,
    regardless of the directory it was found in.
    """

    _GLOBAL_DIR = Path("/etc/freebox")

    def __init__(self, app_id: str) -> None:
        self.app_id = app_id

    @property
    def _filename(self) -> str:
        return f"{self.app_id}.json"

    @staticmethod
    def _user_dir() -> Path:
        xdg = os.environ.get("XDG_CONFIG_HOME", "")
        base = Path(xdg) if xdg else Path.home() / ".config"
        return base / "freebox"

    @staticmethod
    def _local_dir() -> Path:
        return Path.cwd() / ".freebox"

    def _search_dirs(self) -> list[Path]:
        return [self._local_dir(), self._user_dir(), self._GLOBAL_DIR]

    def _write_dir(self) -> Path:
        """Return the directory to use when creating a new credential file."""
        local = self._local_dir()
        if local.is_dir():
            return local
        if hasattr(os, "getuid") and os.getuid() == 0:
            return self._GLOBAL_DIR
        return self._user_dir()

    def find(self) -> Path | None:
        """Return the path of the credential file if it exists, else ``None``."""
        for d in self._search_dirs():
            p = d / self._filename
            if p.is_file():
                return p
        return None

    def load(self) -> Credentials | None:
        """Load and return stored credentials, or ``None`` if not found."""
        path = self.find()
        if path is None:
            return None
        data: dict = json.loads(path.read_text())
        discovery = None
        if "discovery" in data:
            discovery = DiscoveryInfo._from_dict(data["discovery"])
        return Credentials(
            app_token=data["app_token"],
            host=data.get("host"),
            port=data.get("port"),
            app_id=data.get("app_id"),
            app_name=data.get("app_name"),
            device_name=data.get("device_name"),
            discovery=discovery,
        )

    def save(self, credentials: Credentials) -> None:
        """Persist *credentials*.

        If a credential file already exists it is updated in place; otherwise the
        file is created in the directory chosen by :meth:`_write_dir`.
        """
        existing = self.find()
        target_dir = existing.parent if existing is not None else self._write_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / self._filename
        data: dict[str, object] = {"app_token": credentials.app_token}
        if credentials.host is not None:
            data["host"] = credentials.host
        if credentials.port is not None:
            data["port"] = credentials.port
        if credentials.app_id is not None:
            data["app_id"] = credentials.app_id
        if credentials.app_name is not None:
            data["app_name"] = credentials.app_name
        if credentials.device_name is not None:
            data["device_name"] = credentials.device_name
        if credentials.discovery is not None:
            d = credentials.discovery
            data["discovery"] = {
                "uid": d.uid,
                "device_name": d.device_name,
                "box_model": d.box_model,
                "box_model_name": d.box_model_name,
                "api_version": d.api_version,
                "api_base_url": d.api_base_url,
                "api_domain": d.api_domain,
                "https_available": d.https_available,
                "https_port": d.https_port,
            }
        path.write_text(json.dumps(data, indent=2))
        path.chmod(0o600)

    def delete(self) -> None:
        """Remove the credential file if it exists."""
        path = self.find()
        if path is not None:
            path.unlink()
