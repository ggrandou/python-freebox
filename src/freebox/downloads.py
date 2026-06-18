"""Freebox download manager API."""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── Config sub-objects ────────────────────────────────────────────────────────

@dataclass
class DlRate:
    """Upload/download rate limit pair (in bytes/s; 0 = unlimited)."""

    rx_rate: int
    tx_rate: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DlRate:
        return cls(rx_rate=d.get("rx_rate", 0), tx_rate=d.get("tx_rate", 0))


@dataclass
class DlThrottlingConfig:
    """Throttling schedule and rate limits."""

    normal: DlRate
    slow: DlRate
    schedule: list[str]
    mode: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DlThrottlingConfig:
        return cls(
            normal=DlRate._from_dict(d.get("normal") or {}),
            slow=DlRate._from_dict(d.get("slow") or {}),
            schedule=list(d.get("schedule") or []),
            mode=d.get("mode", ""),
        )


@dataclass
class DlNewsConfig:
    """Newsgroup (NNTP) download configuration."""

    server: str
    port: int
    ssl: bool
    user: str
    nthreads: int
    auto_repair: bool
    lazy_par2: bool
    auto_extract: bool
    erase_tmp: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DlNewsConfig:
        return cls(
            server=d.get("server", ""),
            port=d.get("port", 119),
            ssl=d.get("ssl", False),
            user=d.get("user", ""),
            nthreads=d.get("nthreads", 1),
            auto_repair=d.get("auto_repair", True),
            lazy_par2=d.get("lazy_par2", True),
            auto_extract=d.get("auto_extract", True),
            erase_tmp=d.get("erase_tmp", True),
        )


@dataclass
class DlBtConfig:
    """Bittorrent download configuration."""

    max_peers: int
    stop_ratio: int
    crypto_support: str
    enable_dht: bool
    enable_pex: bool
    announce_timeout: int
    main_port: int
    dht_port: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DlBtConfig:
        return cls(
            max_peers=d.get("max_peers", 50),
            stop_ratio=d.get("stop_ratio", 150),
            crypto_support=d.get("crypto_support", "allowed"),
            enable_dht=d.get("enable_dht", True),
            enable_pex=d.get("enable_pex", True),
            announce_timeout=d.get("announce_timeout", 30),
            main_port=d.get("main_port", 0),
            dht_port=d.get("dht_port", 0),
        )


@dataclass
class DlFeedConfig:
    """RSS feed auto-download configuration."""

    fetch_interval: int
    max_items: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DlFeedConfig:
        return cls(
            fetch_interval=d.get("fetch_interval", 60),
            max_items=d.get("max_items", 0),
        )


@dataclass
class DownloadConfig:
    """Download manager global configuration (GET /downloads/config/).

    ``download_dir`` and ``watch_dir`` are base64-encoded paths.
    Use ``download_dir_decoded`` / ``watch_dir_decoded`` for the plain strings.
    """

    max_downloading_tasks: int
    download_dir: str
    watch_dir: str
    use_watch_dir: bool
    dns1: str
    dns2: str
    throttling: DlThrottlingConfig
    news: DlNewsConfig
    bt: DlBtConfig
    feed: DlFeedConfig

    @property
    def download_dir_decoded(self) -> str:
        """Decoded default download directory."""
        if not self.download_dir:
            return ""
        try:
            return base64.b64decode(self.download_dir).decode()
        except Exception:
            return self.download_dir

    @property
    def watch_dir_decoded(self) -> str:
        """Decoded watch directory."""
        if not self.watch_dir:
            return ""
        try:
            return base64.b64decode(self.watch_dir).decode()
        except Exception:
            return self.watch_dir

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadConfig:
        return cls(
            max_downloading_tasks=d.get("max_downloading_tasks", 5),
            download_dir=d.get("download_dir", ""),
            watch_dir=d.get("watch_dir", ""),
            use_watch_dir=d.get("use_watch_dir", False),
            dns1=d.get("dns1", ""),
            dns2=d.get("dns2", ""),
            throttling=DlThrottlingConfig._from_dict(d.get("throttling") or {}),
            news=DlNewsConfig._from_dict(d.get("news") or {}),
            bt=DlBtConfig._from_dict(d.get("bt") or {}),
            feed=DlFeedConfig._from_dict(d.get("feed") or {}),
        )


# ── Download Task ─────────────────────────────────────────────────────────────

@dataclass
class DownloadTask:
    """A download task (GET /downloads/).

    ``download_dir`` is base64-encoded.  Use ``download_dir_decoded`` for the
    plain path.
    """

    id: int
    type: str
    name: str
    status: str
    size: int
    queue_pos: int
    io_priority: str
    tx_bytes: int
    rx_bytes: int
    tx_rate: int
    rx_rate: int
    tx_pct: int
    rx_pct: int
    error: str
    created_ts: int
    eta: int
    download_dir: str
    stop_ratio: int
    archive_password: str
    info_hash: str
    piece_length: int

    @property
    def download_dir_decoded(self) -> str:
        """Decoded destination directory."""
        if not self.download_dir:
            return ""
        try:
            return base64.b64decode(self.download_dir).decode()
        except Exception:
            return self.download_dir

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadTask:
        return cls(
            id=d.get("id", 0),
            type=d.get("type", ""),
            name=d.get("name", ""),
            status=d.get("status", ""),
            size=d.get("size", 0),
            queue_pos=d.get("queue_pos", 0),
            io_priority=d.get("io_priority", ""),
            tx_bytes=d.get("tx_bytes", 0),
            rx_bytes=d.get("rx_bytes", 0),
            tx_rate=d.get("tx_rate", 0),
            rx_rate=d.get("rx_rate", 0),
            tx_pct=d.get("tx_pct", 0),
            rx_pct=d.get("rx_pct", 0),
            error=d.get("error", ""),
            created_ts=d.get("created_ts", 0),
            eta=d.get("eta", 0),
            download_dir=d.get("download_dir", ""),
            stop_ratio=d.get("stop_ratio", 0),
            archive_password=d.get("archive_password", ""),
            info_hash=d.get("info_hash", ""),
            piece_length=d.get("piece_length", 0),
        )


# ── Stats ─────────────────────────────────────────────────────────────────────

@dataclass
class DhtStats:
    """DHT (Distributed Hash Table) statistics."""

    enabled: bool
    node_count: int
    enabled_ipv6: bool
    node_count_ipv6: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DhtStats:
        return cls(
            enabled=d.get("enabled", False),
            node_count=d.get("node_count", 0),
            enabled_ipv6=d.get("enabled_ipv6", False),
            node_count_ipv6=d.get("node_count_ipv6", 0),
        )


@dataclass
class DownloadStats:
    """Download manager statistics (GET /downloads/stats/)."""

    nb_tasks: int
    nb_tasks_stopped: int
    nb_tasks_checking: int
    nb_tasks_queued: int
    nb_tasks_extracting: int
    nb_tasks_done: int
    nb_tasks_repairing: int
    nb_tasks_seeding: int
    nb_tasks_downloading: int
    nb_tasks_error: int
    nb_tasks_stopping: int
    nb_tasks_active: int
    nb_rss: int
    nb_rss_items_unread: int
    rx_rate: int
    tx_rate: int
    throttling_mode: str
    throttling_is_scheduled: bool
    throttling_rate: DlRate
    nb_peer: int
    blocklist_entries: int
    blocklist_hits: int
    conn_ready: bool
    dht_stats: DhtStats | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadStats:
        dht = d.get("dht_stats")
        return cls(
            nb_tasks=d.get("nb_tasks", 0),
            nb_tasks_stopped=d.get("nb_tasks_stopped", 0),
            nb_tasks_checking=d.get("nb_tasks_checking", 0),
            nb_tasks_queued=d.get("nb_tasks_queued", 0),
            nb_tasks_extracting=d.get("nb_tasks_extracting", 0),
            nb_tasks_done=d.get("nb_tasks_done", 0),
            nb_tasks_repairing=d.get("nb_tasks_repairing", 0),
            nb_tasks_seeding=d.get("nb_tasks_seeding", 0),
            nb_tasks_downloading=d.get("nb_tasks_downloading", 0),
            nb_tasks_error=d.get("nb_tasks_error", 0),
            nb_tasks_stopping=d.get("nb_tasks_stopping", 0),
            nb_tasks_active=d.get("nb_tasks_active", 0),
            nb_rss=d.get("nb_rss", 0),
            nb_rss_items_unread=d.get("nb_rss_items_unread", 0),
            rx_rate=d.get("rx_rate", 0),
            tx_rate=d.get("tx_rate", 0),
            throttling_mode=d.get("throttling_mode", ""),
            throttling_is_scheduled=d.get("throttling_is_scheduled", False),
            throttling_rate=DlRate._from_dict(d.get("throttling_rate") or {}),
            nb_peer=d.get("nb_peer", 0),
            blocklist_entries=d.get("blocklist_entries", 0),
            blocklist_hits=d.get("blocklist_hits", 0),
            conn_ready=d.get("conn_ready", False),
            dht_stats=DhtStats._from_dict(dht) if dht else None,
        )


# ── Download Files ────────────────────────────────────────────────────────────

@dataclass
class DownloadFile:
    """A file inside a download task (GET /downloads/{id}/files).

    ``filepath`` is base64-encoded.  Use ``filepath_decoded`` for the plain path.
    """

    id: str
    task_id: int
    filepath: str
    name: str
    mimetype: str
    size: int
    rx: int
    status: str
    error: str
    priority: str
    preview_url: str

    @property
    def filepath_decoded(self) -> str:
        """Decoded file path."""
        if not self.filepath:
            return ""
        try:
            return base64.b64decode(self.filepath).decode()
        except Exception:
            return self.filepath

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadFile:
        return cls(
            id=d.get("id", ""),
            task_id=int(d.get("task_id", 0)),
            filepath=d.get("filepath", ""),
            name=d.get("name", ""),
            mimetype=d.get("mimetype", ""),
            size=d.get("size", 0),
            rx=d.get("rx", 0),
            status=d.get("status", ""),
            error=d.get("error", ""),
            priority=d.get("priority", ""),
            preview_url=d.get("preview_url", ""),
        )


# ── Trackers ──────────────────────────────────────────────────────────────────

@dataclass
class DownloadTracker:
    """A BitTorrent tracker for a download task."""

    announce: str
    is_backup: bool
    status: str
    interval: int
    min_interval: int
    reannounce_in: int
    nseeders: int
    nleechers: int
    is_enabled: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadTracker:
        return cls(
            announce=d.get("announce", ""),
            is_backup=d.get("is_backup", False),
            status=d.get("status", ""),
            interval=d.get("interval", 0),
            min_interval=d.get("min_interval", 0),
            reannounce_in=d.get("reannounce_in", 0),
            nseeders=d.get("nseeders", 0),
            nleechers=d.get("nleechers", 0),
            is_enabled=d.get("is_enabled", True),
        )


# ── Peers ─────────────────────────────────────────────────────────────────────

@dataclass
class DownloadPeer:
    """A BitTorrent peer for a download task."""

    host: str
    port: int
    state: str
    origin: str
    protocol: str
    client: str
    country_code: str
    tx: int
    rx: int
    tx_rate: int
    rx_rate: int
    progress: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadPeer:
        return cls(
            host=d.get("host", ""),
            port=d.get("port", 0),
            state=d.get("state", ""),
            origin=d.get("origin", ""),
            protocol=d.get("protocol", ""),
            client=d.get("client", ""),
            country_code=d.get("country_code", ""),
            tx=d.get("tx", 0),
            rx=d.get("rx", 0),
            tx_rate=d.get("tx_rate", 0),
            rx_rate=d.get("rx_rate", 0),
            progress=d.get("progress", 0),
        )


# ── Blacklist ─────────────────────────────────────────────────────────────────

@dataclass
class DownloadBlacklistEntry:
    """A BitTorrent peer blacklist entry."""

    host: str
    reason: str
    expire: int
    is_global: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadBlacklistEntry:
        return cls(
            host=d.get("host", ""),
            reason=d.get("reason", ""),
            expire=d.get("expire", 0),
            is_global=d.get("global", False),
        )


# ── RSS Feeds ─────────────────────────────────────────────────────────────────

@dataclass
class DownloadFeed:
    """An RSS feed subscription (GET /downloads/feeds/)."""

    id: int
    status: str
    url: str
    title: str
    desc: str
    image_url: str
    nb_read: int
    nb_unread: int
    auto_download: bool
    fetch_ts: int
    pub_ts: int
    error: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadFeed:
        return cls(
            id=d.get("id") or d.get("feed_id", 0),
            status=d.get("status", ""),
            url=d.get("url", ""),
            title=d.get("title", ""),
            desc=d.get("desc", ""),
            image_url=d.get("image_url", ""),
            nb_read=d.get("nb_read", 0),
            nb_unread=d.get("nb_unread", 0),
            auto_download=d.get("auto_download", False),
            fetch_ts=d.get("fetch_ts", 0),
            pub_ts=d.get("pub_ts", 0),
            error=d.get("error", ""),
        )


@dataclass
class DownloadFeedItem:
    """An item inside an RSS feed (GET /downloads/feeds/{id}/items/)."""

    id: int
    feed_id: int
    title: str
    desc: str
    author: str
    link: str
    is_read: bool
    is_downloaded: bool
    fetch_ts: int
    pub_ts: int
    enclosure_url: str
    enclosure_type: str
    enclosure_length: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> DownloadFeedItem:
        return cls(
            id=d.get("id", 0),
            feed_id=d.get("feed_id", 0),
            title=d.get("title", ""),
            desc=d.get("desc", ""),
            author=d.get("author", ""),
            link=d.get("link", ""),
            is_read=d.get("is_read", False),
            is_downloaded=d.get("is_downloaded", False),
            fetch_ts=d.get("fetch_ts", 0),
            pub_ts=d.get("pub_ts", 0),
            enclosure_url=d.get("enclosure_url", ""),
            enclosure_type=d.get("enclosure_type", ""),
            enclosure_length=d.get("enclosure_length", 0),
        )


# ── API class ─────────────────────────────────────────────────────────────────

class Downloads:
    """Freebox download manager API.

    Obtained via ``fb.downloads``::

        tasks = fb.downloads.list()
        for t in tasks:
            print(t.name, t.status, t.rx_pct / 100, "%")

        stats = fb.downloads.stats()
        print(stats.rx_rate, "B/s down,", stats.tx_rate, "B/s up")
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Tasks ──────────────────────────────────────────────────────────────────

    def list(self) -> list[DownloadTask]:
        """Return all download tasks."""
        result = self._client.get("downloads/")
        return [DownloadTask._from_dict(t) for t in result] if result else []

    def get(self, task_id: int) -> DownloadTask:
        """Return the download task with the given id."""
        return DownloadTask._from_dict(self._client.get(f"downloads/{task_id}"))

    def update(self, task_id: int, **kwargs: Any) -> DownloadTask:
        """Update a download task (e.g. status, io_priority, queue_pos)."""
        return DownloadTask._from_dict(
            self._client.put(f"downloads/{task_id}", json=kwargs)
        )

    def delete(self, task_id: int) -> None:
        """Remove a download task, keeping downloaded files."""
        self._client.delete(f"downloads/{task_id}")

    def erase(self, task_id: int) -> None:
        """Remove a download task and delete all downloaded files."""
        self._client.delete(f"downloads/{task_id}/erase")

    def add(
        self,
        url: str | list[str],
        *,
        download_dir: str = "",
        filename: str = "",
        recursive: bool = False,
        username: str = "",
        password: str = "",
        archive_password: str = "",
        cookies: str = "",
        hash_: str = "",
    ) -> int | list[int]:
        """Add one or more download tasks by URL or magnet link.

        ``url`` can be a single URL or a list of URLs.
        Returns a task id (single URL) or a list of task ids (multiple URLs).

        Note: the request is form-encoded, not JSON.
        """
        data: dict[str, Any] = {}
        if isinstance(url, list):
            data["download_url_list"] = "\n".join(url)
        else:
            data["download_url"] = url
        if download_dir:
            data["download_dir"] = download_dir
        if filename:
            data["filename"] = filename
        if recursive:
            data["recursive"] = "true"
        if username:
            data["username"] = username
        if password:
            data["password"] = password
        if archive_password:
            data["archive_password"] = archive_password
        if cookies:
            data["cookies"] = cookies
        if hash_:
            data["hash"] = hash_
        result = self._client.post("downloads/add", data=data)
        task_id = result["id"]
        return task_id

    def add_file(
        self,
        file_content: bytes,
        filename: str,
        *,
        download_dir: str = "",
        archive_password: str = "",
    ) -> int:
        """Add a download task by uploading a .torrent or .nzb file.

        Returns the new task id.
        """
        files: dict[str, Any] = {
            "download_file": (filename, file_content, "application/octet-stream")
        }
        data: dict[str, str] = {}
        if download_dir:
            data["download_dir"] = download_dir
        if archive_password:
            data["archive_password"] = archive_password
        result = self._client.post("downloads/add", files=files, data=data)
        return result["id"]

    def log(self, task_id: int) -> str:
        """Return the log for a download task."""
        return self._client.get(f"downloads/{task_id}/log") or ""

    # ── Stats ──────────────────────────────────────────────────────────────────

    def stats(self) -> DownloadStats:
        """Return download manager statistics."""
        return DownloadStats._from_dict(self._client.get("downloads/stats"))

    # ── Config ─────────────────────────────────────────────────────────────────

    def config(self) -> DownloadConfig:
        """Return the download manager configuration."""
        return DownloadConfig._from_dict(self._client.get("downloads/config/"))

    def set_config(self, **kwargs: Any) -> DownloadConfig:
        """Update the download manager configuration."""
        return DownloadConfig._from_dict(
            self._client.put("downloads/config/", json=kwargs)
        )

    def set_throttling(self, mode: str) -> dict[str, Any]:
        """Force the throttling mode (normal / slow / hibernate / schedule)."""
        return self._client.put("downloads/throttling", json={"throttling": mode}) or {}

    # ── Files ──────────────────────────────────────────────────────────────────

    def files(self, task_id: int) -> list[DownloadFile]:
        """Return the files for a download task."""
        result = self._client.get(f"downloads/{task_id}/files")
        return [DownloadFile._from_dict(f) for f in result] if result else []

    def set_file_priority(self, task_id: int, file_id: str, priority: str) -> None:
        """Set the download priority of a file inside a download task."""
        self._client.put(f"downloads/{task_id}/files/{file_id}", json={"priority": priority})

    # ── Trackers ───────────────────────────────────────────────────────────────

    def trackers(self, task_id: int) -> list[DownloadTracker]:
        """Return the BitTorrent trackers for a download task."""
        result = self._client.get(f"downloads/{task_id}/trackers")
        return [DownloadTracker._from_dict(t) for t in result] if result else []

    def add_tracker(self, task_id: int, announce: str) -> None:
        """Add a BitTorrent tracker to a download task."""
        self._client.post(f"downloads/{task_id}/trackers", json={"announce": announce})

    def update_tracker(self, task_id: int, announce: str, **kwargs: Any) -> None:
        """Update a BitTorrent tracker (e.g. is_enabled)."""
        self._client.put(f"downloads/{task_id}/trackers/{announce}", json=kwargs)

    def delete_tracker(self, task_id: int, announce: str) -> None:
        """Remove a BitTorrent tracker from a download task."""
        self._client.delete(f"downloads/{task_id}/trackers/{announce}")

    # ── Peers ──────────────────────────────────────────────────────────────────

    def peers(self, task_id: int) -> list[DownloadPeer]:
        """Return the BitTorrent peers for a download task."""
        result = self._client.get(f"downloads/{task_id}/peers")
        return [DownloadPeer._from_dict(p) for p in result] if result else []

    def pieces(self, task_id: int) -> str:
        """Return the piece status string for a BitTorrent download task."""
        return self._client.get(f"downloads/{task_id}/pieces") or ""

    # ── Blacklist ──────────────────────────────────────────────────────────────

    def blacklist(self, task_id: int) -> list[DownloadBlacklistEntry]:
        """Return the blacklist entries for a download task."""
        result = self._client.get(f"downloads/{task_id}/blacklist")
        return [DownloadBlacklistEntry._from_dict(e) for e in result] if result else []

    def add_blacklist_entry(self, host: str, expire: int = 0) -> DownloadBlacklistEntry:
        """Add a host to the global BitTorrent blacklist."""
        return DownloadBlacklistEntry._from_dict(
            self._client.post("downloads/blacklist", json={"host": host, "expire": expire})
        )

    def delete_blacklist_entry(self, host: str) -> None:
        """Delete a specific entry from the global BitTorrent blacklist."""
        self._client.delete(f"downloads/blacklist/{host}")

    def clear_blacklist(self, task_id: int) -> None:
        """Clear the blacklist for a download task (removes global entries too)."""
        self._client.delete(f"downloads/{task_id}/blacklist/empty")

    # ── RSS Feeds ──────────────────────────────────────────────────────────────

    def feeds(self) -> list[DownloadFeed]:
        """Return all RSS feed subscriptions."""
        result = self._client.get("downloads/feeds/")
        return [DownloadFeed._from_dict(f) for f in result] if result else []

    def get_feed(self, feed_id: int) -> DownloadFeed:
        """Return the RSS feed with the given id."""
        return DownloadFeed._from_dict(self._client.get(f"downloads/feeds/{feed_id}"))

    def add_feed(self, url: str) -> DownloadFeed:
        """Subscribe to a new RSS feed."""
        return DownloadFeed._from_dict(
            self._client.post("downloads/feeds/", json={"url": url})
        )

    def update_feed(self, feed_id: int, **kwargs: Any) -> DownloadFeed:
        """Update an RSS feed subscription (e.g. auto_download)."""
        return DownloadFeed._from_dict(
            self._client.put(f"downloads/feeds/{feed_id}", json=kwargs)
        )

    def delete_feed(self, feed_id: int) -> None:
        """Delete an RSS feed subscription and all its items."""
        self._client.delete(f"downloads/feeds/{feed_id}")

    def fetch_feed(self, feed_id: int) -> None:
        """Force a refresh of one RSS feed."""
        self._client.post(f"downloads/feeds/{feed_id}/fetch")

    def fetch_all_feeds(self) -> None:
        """Force a refresh of all RSS feeds."""
        self._client.post("downloads/feeds/fetch")

    def feed_items(self, feed_id: int) -> list[DownloadFeedItem]:
        """Return all items in an RSS feed."""
        result = self._client.get(f"downloads/feeds/{feed_id}/items/")
        return [DownloadFeedItem._from_dict(i) for i in result] if result else []

    def update_feed_item(self, feed_id: int, item_id: int, **kwargs: Any) -> None:
        """Update an RSS feed item (e.g. is_read)."""
        self._client.put(f"downloads/feeds/{feed_id}/items/{item_id}", json=kwargs)

    def download_feed_item(self, feed_id: int, item_id: int) -> None:
        """Enqueue an RSS feed item for download."""
        self._client.post(f"downloads/feeds/{feed_id}/items/{item_id}/download")

    def mark_feed_items_read(self, feed_id: int) -> None:
        """Mark all items in an RSS feed as read."""
        self._client.post(f"downloads/feeds/{feed_id}/items/mark_all_as_read")
