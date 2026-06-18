"""Freebox file system API."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


def _decode_path(path: str) -> str:
    """Decode a base64-encoded Freebox path, returning it as-is on failure."""
    if not path:
        return ""
    try:
        return base64.b64decode(path).decode()
    except Exception:
        return path


# ── FileInfo ──────────────────────────────────────────────────────────────────

@dataclass
class FileInfo:
    """A file or directory entry (GET /fs/ls/{path} or GET /fs/info/{path}).

    ``path`` and ``target`` are base64-encoded.
    Use ``path_decoded`` / ``target_decoded`` for plain strings.
    """

    path: str
    name: str
    mimetype: str
    type: str
    size: int
    modification: int
    index: int
    link: bool
    hidden: bool
    target: str
    foldercount: int
    filecount: int

    @property
    def path_decoded(self) -> str:
        """Decoded file/folder path."""
        return _decode_path(self.path)

    @property
    def target_decoded(self) -> str:
        """Decoded symlink target path."""
        return _decode_path(self.target)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FileInfo:
        return cls(
            path=d.get("path", ""),
            name=d.get("name", ""),
            mimetype=d.get("mimetype", ""),
            type=d.get("type", ""),
            size=d.get("size", 0),
            modification=d.get("modification", 0),
            index=d.get("index", 0),
            link=d.get("link", False),
            hidden=d.get("hidden", False),
            target=d.get("target", ""),
            foldercount=d.get("foldercount", 0),
            filecount=d.get("filecount", 0),
        )


@dataclass
class FsLsResult:
    """Result of a directory listing (GET /fs/ls/{path}).

    ``cursor`` is non-empty when there are more entries to fetch.
    Pass it as the ``cursor`` parameter to the next ``ls()`` call.
    """

    entries: list[FileInfo]
    cursor: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FsLsResult:
        entries = [FileInfo._from_dict(e) for e in d.get("entries") or []]
        return cls(entries=entries, cursor=d.get("cursor", ""))


# ── FsTask ────────────────────────────────────────────────────────────────────

@dataclass
class FsTask:
    """A file system task (copy, move, delete, extract, archive, …).

    ``progress`` is scaled by 100: a value of 5000 means 50%.
    ``from_path`` and ``to`` are plain text paths (not base64).
    """

    id: int
    type: str
    state: str
    error: str
    created_ts: int
    started_ts: int
    done_ts: int
    duration: int
    progress: int
    eta: int
    from_path: str
    to: str
    nfiles: int
    nfiles_done: int
    total_bytes: int
    total_bytes_done: int
    curr_bytes: int
    curr_bytes_done: int
    rate: int
    src: list[str]
    dst: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FsTask:
        return cls(
            id=d.get("id", 0),
            type=d.get("type", ""),
            state=d.get("state", ""),
            error=d.get("error", ""),
            created_ts=d.get("created_ts", 0),
            started_ts=d.get("started_ts", 0),
            done_ts=d.get("done_ts", 0),
            duration=d.get("duration", 0),
            progress=d.get("progress", 0),
            eta=d.get("eta", 0),
            from_path=d.get("from", ""),
            to=d.get("to", ""),
            nfiles=d.get("nfiles", 0),
            nfiles_done=d.get("nfiles_done", 0),
            total_bytes=d.get("total_bytes", 0),
            total_bytes_done=d.get("total_bytes_done", 0),
            curr_bytes=d.get("curr_bytes", 0),
            curr_bytes_done=d.get("curr_bytes_done", 0),
            rate=d.get("rate", 0),
            src=list(d.get("src") or []),
            dst=d.get("dst", ""),
        )


# ── API class ─────────────────────────────────────────────────────────────────

class Fs:
    """Freebox file system API.

    Obtained via ``fb.fs``::

        result = fb.fs.ls(root_b64)
        for entry in result.entries:
            print(entry.name, entry.type, entry.size)

        task = fb.fs.mv([src_b64], dst_b64)
        # poll until task.state == "done"
        while True:
            t = fb.fs.task(task.id)
            if t.state in ("done", "failed"):
                break

    All paths passed to the API must be base64-encoded as returned by ``ls``.
    Use ``base64.b64encode(path.encode()).decode()`` to encode a plain string.
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Directory listing ──────────────────────────────────────────────────────

    def ls(
        self,
        path: str,
        *,
        only_folder: bool = False,
        count_sub_folder: bool = False,
        remove_hidden: bool = False,
        limit: int | None = None,
        cursor: str = "",
    ) -> FsLsResult:
        """List files and folders at the given base64-encoded path.

        Pass the returned ``cursor`` to the next call to page through results.
        """
        params: dict[str, Any] = {}
        if only_folder:
            params["onlyFolder"] = "true"
        if count_sub_folder:
            params["countSubFolder"] = "true"
        if remove_hidden:
            params["removeHidden"] = "true"
        if limit is not None:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        result = self._client.get(f"fs/ls/{path}", params=params)
        return FsLsResult._from_dict(result or {})

    def info(self, path: str) -> FileInfo:
        """Return info for the file or folder at the given base64-encoded path."""
        return FileInfo._from_dict(self._client.get(f"fs/info/{path}"))

    def batch_info(self, paths: list[str]) -> list[FileInfo]:
        """Return info for multiple base64-encoded paths in one request.

        Invalid paths are silently ignored by the Freebox.
        """
        result = self._client.post("fs/info", json=paths)
        return [FileInfo._from_dict(e) for e in result] if result else []

    # ── Tasks ──────────────────────────────────────────────────────────────────

    def tasks(self) -> list[FsTask]:
        """Return all active file system tasks."""
        result = self._client.get("fs/tasks/")
        return [FsTask._from_dict(t) for t in result] if result else []

    def task(self, task_id: int) -> FsTask:
        """Return the file system task with the given id."""
        return FsTask._from_dict(self._client.get(f"fs/tasks/{task_id}"))

    def update_task(self, task_id: int, state: str) -> FsTask:
        """Update a task state (running / paused)."""
        return FsTask._from_dict(
            self._client.put(f"fs/tasks/{task_id}", json={"state": state})
        )

    def delete_task(self, task_id: int) -> None:
        """Cancel and delete a file system task."""
        self._client.delete(f"fs/tasks/{task_id}")

    def task_hash(self, task_id: int) -> str:
        """Return the hash value computed by a completed hash task."""
        result = self._client.get(f"fs/tasks/{task_id}/hash")
        return (result or {}).get("hash", "")

    # ── File operations (return a task) ────────────────────────────────────────

    def mv(
        self, files: list[str], dst: str, mode: str = "overwrite"
    ) -> FsTask:
        """Move files to a destination directory.

        ``files`` and ``dst`` are base64-encoded paths.
        ``mode`` is one of: overwrite, both, recent, skip.
        """
        return FsTask._from_dict(
            self._client.post("fs/mv/", json={"files": files, "dst": dst, "mode": mode})
        )

    def cp(
        self, files: list[str], dst: str, mode: str = "overwrite"
    ) -> FsTask:
        """Copy files to a destination directory.

        ``files`` and ``dst`` are base64-encoded paths.
        """
        return FsTask._from_dict(
            self._client.post("fs/cp/", json={"files": files, "dst": dst, "mode": mode})
        )

    def rm(self, files: list[str]) -> FsTask:
        """Remove files.  ``files`` is a list of base64-encoded paths."""
        return FsTask._from_dict(
            self._client.post("fs/rm/", json={"files": files})
        )

    def cat(
        self,
        files: list[str],
        dst: str,
        *,
        multi_volumes: bool = False,
        delete_files: bool = False,
        overwrite: bool = False,
        append: bool = False,
    ) -> FsTask:
        """Concatenate files into a single destination file."""
        return FsTask._from_dict(
            self._client.post(
                "fs/cat/",
                json={
                    "files": files,
                    "dst": dst,
                    "multi_volumes": multi_volumes,
                    "delete_files": delete_files,
                    "overwrite": overwrite,
                    "append": append,
                },
            )
        )

    def archive(self, files: list[str], dst: str) -> FsTask:
        """Create a ZIP archive from the given files.

        ``files`` is a list of base64-encoded paths.
        ``dst`` is the base64-encoded destination path (including filename).
        """
        return FsTask._from_dict(
            self._client.post("fs/archive/", json={"files": files, "dst": dst})
        )

    def extract(
        self,
        src: str,
        dst: str,
        *,
        password: str = "",
        delete_archive: bool = False,
        overwrite: bool = False,
    ) -> FsTask:
        """Extract an archive to a destination directory.

        ``src`` and ``dst`` are base64-encoded paths.
        """
        return FsTask._from_dict(
            self._client.post(
                "fs/extract/",
                json={
                    "src": src,
                    "dst": dst,
                    "password": password,
                    "delete_archive": delete_archive,
                    "overwrite": overwrite,
                },
            )
        )

    def repair(self, src: str, *, delete_archive: bool = False) -> FsTask:
        """Repair corrupted files using a .par2 file.

        ``src`` is the base64-encoded path to the .par2 file.
        """
        return FsTask._from_dict(
            self._client.post(
                "fs/repair/", json={"src": src, "delete_archive": delete_archive}
            )
        )

    def hash(self, src: str, hash_type: str = "md5") -> FsTask:
        """Start a hash computation task.

        ``src`` is the base64-encoded path to the file to hash.
        ``hash_type`` is 'md5', 'sha1', etc.
        Once done, retrieve the result with ``task_hash(task.id)``.
        """
        return FsTask._from_dict(
            self._client.post("fs/hash/", json={"src": src, "hash_type": hash_type})
        )

    # ── Synchronous operations ─────────────────────────────────────────────────

    def mkdir(self, parent: str, dirname: str) -> None:
        """Create a directory synchronously.

        ``parent`` is the base64-encoded parent directory path.
        ``dirname`` is the plain-text name for the new directory.
        """
        self._client.post("fs/mkdir/", json={"parent": parent, "dirname": dirname})

    def rename(self, src: str, dst: str) -> str:
        """Rename a file or folder synchronously.

        ``src`` is the base64-encoded source path.
        ``dst`` is the plain-text new name (without path).
        Returns the base64-encoded new path.
        """
        return self._client.post("fs/rename/", json={"src": src, "dst": dst}) or ""

    # ── Download ───────────────────────────────────────────────────────────────

    def download(self, path: str) -> bytes:
        """Download a file by its base64-encoded path.

        Returns the raw file content as bytes.
        """
        return self._client.get_bytes(f"dl/{path}")
