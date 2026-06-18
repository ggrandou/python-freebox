"""Unit tests for the download manager API."""
import base64

import pytest

from freebox import (
    DhtStats,
    DlBtConfig,
    DlFeedConfig,
    DlNewsConfig,
    DlRate,
    DlThrottlingConfig,
    DownloadBlacklistEntry,
    DownloadConfig,
    DownloadFeed,
    DownloadFeedItem,
    DownloadFile,
    DownloadPeer,
    DownloadStats,
    DownloadTask,
    DownloadTracker,
    Downloads,
    Freebox,
)
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
    api_ok,
)

BASE = "https://mafreebox.freebox.fr"
API  = f"{BASE}/api/v16"

DLDIR_B64 = base64.b64encode(b"/Disque dur/Telechargements/").decode()
WATCHDIR_B64 = base64.b64encode(b"/Disque dur/.queue").decode()
FILE_B64 = base64.b64encode(b"/Disque dur/Telechargements/debian.iso").decode()


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

TASK_1 = {
    "id": 16, "type": "bt", "name": "debian-8.7.1-amd64-CD-1.iso",
    "status": "downloading", "size": 660600000, "queue_pos": 2,
    "io_priority": "normal", "tx_bytes": 3460, "rx_bytes": 147450,
    "tx_rate": 202, "rx_rate": 10950, "tx_pct": 0, "rx_pct": 150,
    "error": "none", "created_ts": 1485513882, "eta": 60290,
    "download_dir": DLDIR_B64, "stop_ratio": 150,
    "archive_password": "", "info_hash": "A7055D06E5A8F7F816EC01AC7F7F5243", "piece_length": 524288,
}

STATS_DATA = {
    "nb_tasks": 3, "nb_tasks_stopped": 1, "nb_tasks_checking": 0,
    "nb_tasks_queued": 0, "nb_tasks_extracting": 0, "nb_tasks_done": 1,
    "nb_tasks_repairing": 0, "nb_tasks_seeding": 1, "nb_tasks_downloading": 1,
    "nb_tasks_error": 0, "nb_tasks_stopping": 0, "nb_tasks_active": 2,
    "nb_rss": 2, "nb_rss_items_unread": 5, "rx_rate": 14222, "tx_rate": 4294,
    "throttling_mode": "normal", "throttling_is_scheduled": True,
    "throttling_rate": {"rx_rate": 0, "tx_rate": 0},
    "nb_peer": 12, "blocklist_entries": 4, "blocklist_hits": 42,
    "conn_ready": True,
    "dht_stats": {"enabled": True, "node_count": 100, "enabled_ipv6": False, "node_count_ipv6": 0},
}

CONFIG_DATA = {
    "max_downloading_tasks": 5, "download_dir": DLDIR_B64,
    "watch_dir": WATCHDIR_B64, "use_watch_dir": True,
    "dns1": "", "dns2": "",
    "throttling": {"normal": {"rx_rate": 0, "tx_rate": 0}, "slow": {"rx_rate": 512, "tx_rate": 42}, "schedule": ["normal"] * 168, "mode": "normal"},
    "news": {"server": "news.free.fr", "port": 119, "ssl": False, "user": "", "nthreads": 1, "auto_repair": True, "lazy_par2": True, "auto_extract": True, "erase_tmp": True},
    "bt": {"max_peers": 50, "stop_ratio": 150, "crypto_support": "allowed", "enable_dht": True, "enable_pex": True, "announce_timeout": 30, "main_port": 6881, "dht_port": 6882},
    "feed": {"fetch_interval": 60, "max_items": 0},
}

FILE_DATA = {
    "id": "16-1", "task_id": "16", "filepath": FILE_B64,
    "name": "debian.iso", "mimetype": "application/x-cd-image",
    "size": 660600000, "rx": 147450, "status": "done",
    "error": "none", "priority": "normal", "preview_url": "",
}

TRACKER_DATA = {
    "announce": "http://bttracker.debian.org:6969/announce",
    "is_backup": False, "status": "announced",
    "interval": 900, "min_interval": 60, "reannounce_in": 790,
    "nseeders": 10, "nleechers": 5, "is_enabled": True,
}

PEER_DATA = {
    "host": "1.2.3.4", "port": 51413, "state": "ready",
    "origin": "tracker", "protocol": "tcp", "client": "Transmission 3.0",
    "country_code": "FR", "tx": 0, "rx": 8929,
    "tx_rate": 0, "rx_rate": 0, "progress": 91,
}

BL_ENTRY = {
    "host": "8.8.8.8", "reason": "user", "expire": 300, "global": True,
}

FEED_DATA = {
    "id": 2, "status": "ready", "url": "http://example.com/feed.rss",
    "title": "Test Feed", "desc": "A test feed", "image_url": "",
    "nb_read": 0, "nb_unread": 3, "auto_download": False,
    "fetch_ts": 1350469391, "pub_ts": 1350583600, "error": "none",
}

FEED_ITEM = {
    "id": 100, "feed_id": 2, "title": "debian-6.iso", "desc": "",
    "author": "debian", "link": "http://example.com/d.torrent",
    "is_read": False, "is_downloaded": False,
    "fetch_ts": 1350657317, "pub_ts": 1350657300,
    "enclosure_url": "", "enclosure_type": "", "enclosure_length": 0,
}


# ── DlRate ────────────────────────────────────────────────────────────────────

class TestDlRate:
    def test_from_dict(self):
        r = DlRate._from_dict({"rx_rate": 512, "tx_rate": 42})
        assert r.rx_rate == 512
        assert r.tx_rate == 42

    def test_defaults(self):
        r = DlRate._from_dict({})
        assert r.rx_rate == 0
        assert r.tx_rate == 0


# ── DownloadTask ───────────────────────────────────────────────────────────────

class TestDownloadTask:
    def test_from_dict(self):
        t = DownloadTask._from_dict(TASK_1)
        assert t.id == 16
        assert t.type == "bt"
        assert t.name == "debian-8.7.1-amd64-CD-1.iso"
        assert t.status == "downloading"
        assert t.rx_pct == 150
        assert t.download_dir == DLDIR_B64

    def test_download_dir_decoded(self):
        t = DownloadTask._from_dict(TASK_1)
        assert t.download_dir_decoded == "/Disque dur/Telechargements/"

    def test_download_dir_empty(self):
        t = DownloadTask._from_dict({**TASK_1, "download_dir": ""})
        assert t.download_dir_decoded == ""


# ── DownloadConfig ─────────────────────────────────────────────────────────────

class TestDownloadConfig:
    def test_from_dict(self):
        c = DownloadConfig._from_dict(CONFIG_DATA)
        assert c.max_downloading_tasks == 5
        assert c.download_dir == DLDIR_B64
        assert c.use_watch_dir is True
        assert c.throttling.mode == "normal"
        assert c.news.server == "news.free.fr"
        assert c.bt.max_peers == 50
        assert c.feed.fetch_interval == 60

    def test_download_dir_decoded(self):
        c = DownloadConfig._from_dict(CONFIG_DATA)
        assert c.download_dir_decoded == "/Disque dur/Telechargements/"

    def test_watch_dir_decoded(self):
        c = DownloadConfig._from_dict(CONFIG_DATA)
        assert c.watch_dir_decoded == "/Disque dur/.queue"


# ── DownloadStats ──────────────────────────────────────────────────────────────

class TestDownloadStats:
    def test_from_dict(self):
        s = DownloadStats._from_dict(STATS_DATA)
        assert s.nb_tasks == 3
        assert s.rx_rate == 14222
        assert s.throttling_mode == "normal"
        assert isinstance(s.dht_stats, DhtStats)
        assert s.dht_stats.enabled is True

    def test_no_dht_stats(self):
        s = DownloadStats._from_dict({**STATS_DATA, "dht_stats": None})
        assert s.dht_stats is None


# ── DownloadFile ───────────────────────────────────────────────────────────────

class TestDownloadFile:
    def test_from_dict(self):
        f = DownloadFile._from_dict(FILE_DATA)
        assert f.id == "16-1"
        assert f.task_id == 16
        assert f.name == "debian.iso"
        assert f.filepath == FILE_B64

    def test_filepath_decoded(self):
        f = DownloadFile._from_dict(FILE_DATA)
        assert f.filepath_decoded == "/Disque dur/Telechargements/debian.iso"


# ── DownloadFeed & FeedItem ────────────────────────────────────────────────────

class TestDownloadFeed:
    def test_from_dict(self):
        f = DownloadFeed._from_dict(FEED_DATA)
        assert f.id == 2
        assert f.title == "Test Feed"
        assert f.nb_unread == 3
        assert f.auto_download is False

    def test_feed_id_fallback(self):
        d = {**FEED_DATA, "id": None, "feed_id": 6}
        f = DownloadFeed._from_dict(d)
        assert f.id == 6


class TestDownloadFeedItem:
    def test_from_dict(self):
        i = DownloadFeedItem._from_dict(FEED_ITEM)
        assert i.id == 100
        assert i.feed_id == 2
        assert i.is_read is False
        assert i.is_downloaded is False


# ── Downloads API ──────────────────────────────────────────────────────────────

class TestDownloadsApi:
    def test_list(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/", json=api_ok([TASK_1]))
        tasks = fb.downloads.list()
        assert len(tasks) == 1
        assert isinstance(tasks[0], DownloadTask)

    def test_list_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/", json=api_ok([]))
        assert fb.downloads.list() == []

    def test_list_null(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/", json=api_ok(None))
        assert fb.downloads.list() == []

    def test_get(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16", json=api_ok(TASK_1))
        t = fb.downloads.get(16)
        assert isinstance(t, DownloadTask)
        assert t.id == 16

    def test_update(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/downloads/16", method="PUT",
            json=api_ok({**TASK_1, "status": "stopped"}),
        )
        t = fb.downloads.update(16, status="stopped")
        assert t.status == "stopped"

    def test_delete(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16", method="DELETE", json=api_ok(None))
        fb.downloads.delete(16)

    def test_erase(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/erase", method="DELETE", json=api_ok(None))
        fb.downloads.erase(16)

    def test_add_single(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/add", method="POST", json=api_ok({"id": 23}))
        result = fb.downloads.add("http://example.com/file.torrent")
        assert result == 23

    def test_add_multiple(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/add", method="POST", json=api_ok({"id": [32, 33, 34]}))
        result = fb.downloads.add(["http://a.com/1.rnd", "http://b.com/2.rnd"])
        assert result == [32, 33, 34]

    def test_add_file(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/add", method="POST", json=api_ok({"id": 42}))
        result = fb.downloads.add_file(b"torrent data", "file.torrent")
        assert result == 42

    def test_log(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/log", json=api_ok("line1\nline2\n"))
        log = fb.downloads.log(16)
        assert "line1" in log

    def test_stats(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/stats", json=api_ok(STATS_DATA))
        s = fb.downloads.stats()
        assert isinstance(s, DownloadStats)
        assert s.nb_tasks == 3

    def test_config(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/config/", json=api_ok(CONFIG_DATA))
        c = fb.downloads.config()
        assert isinstance(c, DownloadConfig)
        assert c.max_downloading_tasks == 5

    def test_set_config(self, fb, httpx_mock):
        updated = {**CONFIG_DATA, "max_downloading_tasks": 3}
        httpx_mock.add_response(url=f"{API}/downloads/config/", method="PUT", json=api_ok(updated))
        c = fb.downloads.set_config(max_downloading_tasks=3)
        assert c.max_downloading_tasks == 3

    def test_set_throttling(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/downloads/throttling", method="PUT",
            json=api_ok({"throttling": "slow", "is_scheduled": False}),
        )
        result = fb.downloads.set_throttling("slow")
        assert result["throttling"] == "slow"

    def test_files(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/files", json=api_ok([FILE_DATA]))
        files = fb.downloads.files(16)
        assert len(files) == 1
        assert isinstance(files[0], DownloadFile)

    def test_set_file_priority(self, fb, httpx_mock):
        httpx_mock.add_response(
            url=f"{API}/downloads/16/files/16-1", method="PUT", json=api_ok(None)
        )
        fb.downloads.set_file_priority(16, "16-1", "high")

    def test_trackers(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/trackers", json=api_ok([TRACKER_DATA]))
        trackers = fb.downloads.trackers(16)
        assert len(trackers) == 1
        assert isinstance(trackers[0], DownloadTracker)
        assert trackers[0].nseeders == 10

    def test_add_tracker(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/trackers", method="POST", json=api_ok(None))
        fb.downloads.add_tracker(16, "udp://tracker.example.com:80")

    def test_delete_tracker(self, fb, httpx_mock):
        url = "udp%3A%2F%2Ftracker.example.com%3A80"
        httpx_mock.add_response(url=f"{API}/downloads/16/trackers/{url}", method="DELETE", json=api_ok(None))
        fb.downloads.delete_tracker(16, url)

    def test_peers(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/peers", json=api_ok([PEER_DATA]))
        peers = fb.downloads.peers(16)
        assert len(peers) == 1
        assert isinstance(peers[0], DownloadPeer)
        assert peers[0].host == "1.2.3.4"

    def test_pieces(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/pieces", json=api_ok("XXXXX....."))
        pieces = fb.downloads.pieces(16)
        assert pieces == "XXXXX....."

    def test_blacklist(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/blacklist", json=api_ok([BL_ENTRY]))
        bl = fb.downloads.blacklist(16)
        assert len(bl) == 1
        assert isinstance(bl[0], DownloadBlacklistEntry)
        assert bl[0].host == "8.8.8.8"
        assert bl[0].is_global is True

    def test_add_blacklist_entry(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/blacklist", method="POST", json=api_ok(BL_ENTRY))
        e = fb.downloads.add_blacklist_entry("8.8.8.8", expire=300)
        assert isinstance(e, DownloadBlacklistEntry)

    def test_delete_blacklist_entry(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/blacklist/8.8.8.8", method="DELETE", json=api_ok(None))
        fb.downloads.delete_blacklist_entry("8.8.8.8")

    def test_clear_blacklist(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/16/blacklist/empty", method="DELETE", json=api_ok(None))
        fb.downloads.clear_blacklist(16)

    def test_feeds(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/", json=api_ok([FEED_DATA]))
        feeds = fb.downloads.feeds()
        assert len(feeds) == 1
        assert isinstance(feeds[0], DownloadFeed)

    def test_feeds_empty(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/", json=api_ok([]))
        assert fb.downloads.feeds() == []

    def test_get_feed(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2", json=api_ok(FEED_DATA))
        f = fb.downloads.get_feed(2)
        assert isinstance(f, DownloadFeed)
        assert f.id == 2

    def test_add_feed(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/", method="POST", json=api_ok(FEED_DATA))
        f = fb.downloads.add_feed("http://example.com/feed.rss")
        assert isinstance(f, DownloadFeed)

    def test_update_feed(self, fb, httpx_mock):
        updated = {**FEED_DATA, "auto_download": True}
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2", method="PUT", json=api_ok(updated))
        f = fb.downloads.update_feed(2, auto_download=True)
        assert f.auto_download is True

    def test_delete_feed(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2", method="DELETE", json=api_ok(None))
        fb.downloads.delete_feed(2)

    def test_fetch_feed(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2/fetch", method="POST", json=api_ok(None))
        fb.downloads.fetch_feed(2)

    def test_fetch_all_feeds(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/fetch", method="POST", json=api_ok(None))
        fb.downloads.fetch_all_feeds()

    def test_feed_items(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2/items/", json=api_ok([FEED_ITEM]))
        items = fb.downloads.feed_items(2)
        assert len(items) == 1
        assert isinstance(items[0], DownloadFeedItem)

    def test_update_feed_item(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2/items/100", method="PUT", json=api_ok(None))
        fb.downloads.update_feed_item(2, 100, is_read=True)

    def test_download_feed_item(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2/items/100/download", method="POST", json=api_ok(None))
        fb.downloads.download_feed_item(2, 100)

    def test_mark_feed_items_read(self, fb, httpx_mock):
        httpx_mock.add_response(url=f"{API}/downloads/feeds/2/items/mark_all_as_read", method="POST", json=api_ok(None))
        fb.downloads.mark_feed_items_read(2)


# ── Property ───────────────────────────────────────────────────────────────────

class TestDownloadsProperty:
    def test_property(self, fb):
        assert isinstance(fb.downloads, Downloads)
