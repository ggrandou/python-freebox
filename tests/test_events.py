import json
from unittest.mock import MagicMock, patch

import pytest

from freebox import EventStream, Freebox, Notification
from freebox.discovery import DiscoveryInfo
from freebox.exceptions import AuthenticationError, FreeboxError, InsufficientRightsError
from tests.conftest import (
    APP_ID, APP_NAME, APP_VERSION, DEVICE_NAME,
    DISCOVERY_DATA, SESSION_TOKEN,
)

WS_URL = "wss://mafreebox.freebox.fr/api/v16/ws/event"


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_stream(events=None, token=SESSION_TOKEN):
    import ssl
    return EventStream(
        url=WS_URL,
        session_token=token,
        events=events or ["vm_state_changed"],
        ssl_ctx=ssl.create_default_context(),
    )


def _mock_conn(recv_messages: list[str], register_ok: bool = True) -> MagicMock:
    """Build a mock websocket connection."""
    conn = MagicMock()
    register_resp = json.dumps({"success": register_ok, "action": "register"})
    if not register_ok:
        register_resp = json.dumps({
            "success": False,
            "error_code": "insufficient_rights",
            "msg": "Permission denied",
        })
    conn.recv.side_effect = [register_resp] + recv_messages
    return conn


# ── EventStream unit tests ─────────────────────────────────────────────────────

class TestEventStream:
    def test_enter_sends_register_action(self):
        conn = _mock_conn([])
        stream = make_stream(events=["vm_state_changed", "lan_host_l3addr_reachable"])

        with patch("websockets.sync.client.connect", return_value=conn):
            stream.__enter__()

        sent = json.loads(conn.send.call_args[0][0])
        assert sent["action"] == "register"
        assert sent["events"] == ["vm_state_changed", "lan_host_l3addr_reachable"]

    def test_enter_sends_auth_header(self):
        conn = _mock_conn([])
        stream = make_stream(token="my-session-token")

        with patch("websockets.sync.client.connect", return_value=conn) as mock_connect:
            stream.__enter__()

        headers = mock_connect.call_args.kwargs["additional_headers"]
        assert headers["X-Fbx-App-Auth"] == "my-session-token"

    def test_enter_raises_on_register_failure(self):
        conn = _mock_conn([], register_ok=False)
        stream = make_stream()

        with patch("websockets.sync.client.connect", return_value=conn):
            with pytest.raises(InsufficientRightsError, match="Permission denied"):
                stream.__enter__()

        conn.close.assert_called_once()

    def test_exit_closes_connection(self):
        conn = _mock_conn([])
        stream = make_stream()

        with patch("websockets.sync.client.connect", return_value=conn):
            with stream:
                pass

        conn.close.assert_called_once()

    def test_iterates_notifications(self):
        notifications = [
            json.dumps({
                "action": "notification",
                "success": True,
                "source": "vm",
                "event": "state_changed",
                "result": {"id": 1, "status": "running"},
            }),
            json.dumps({
                "action": "notification",
                "success": True,
                "source": "lan",
                "event": "host_l3addr_reachable",
                "result": {"id": "aa:bb:cc:dd:ee:ff"},
            }),
        ]
        conn = _mock_conn(notifications)
        conn.recv.side_effect = [
            json.dumps({"success": True, "action": "register"}),
        ] + notifications

        # After the last notification, simulate a clean connection close.
        import websockets.exceptions
        conn.recv.side_effect = (
            json.dumps({"success": True, "action": "register"}),
            notifications[0],
            notifications[1],
            websockets.exceptions.ConnectionClosedOK(None, None),
        )

        stream = make_stream()
        with patch("websockets.sync.client.connect", return_value=conn):
            with stream as s:
                received = list(s)

        assert len(received) == 2
        assert received[0] == Notification(source="vm", event="state_changed", result={"id": 1, "status": "running"})
        assert received[1] == Notification(source="lan", event="host_l3addr_reachable", result={"id": "aa:bb:cc:dd:ee:ff"})

    def test_stops_on_connection_closed(self):
        import websockets.exceptions
        conn = MagicMock()
        conn.recv.side_effect = [
            json.dumps({"success": True, "action": "register"}),
            websockets.exceptions.ConnectionClosedOK(None, None),
        ]
        stream = make_stream()

        with patch("websockets.sync.client.connect", return_value=conn):
            with stream as s:
                received = list(s)

        assert received == []

    def test_notification_without_result(self):
        import websockets.exceptions
        conn = MagicMock()
        conn.recv.side_effect = [
            json.dumps({"success": True, "action": "register"}),
            json.dumps({"action": "notification", "success": True, "source": "vm", "event": "disk_task_done"}),
            websockets.exceptions.ConnectionClosedOK(None, None),
        ]
        stream = make_stream()

        with patch("websockets.sync.client.connect", return_value=conn):
            with stream as s:
                received = list(s)

        assert received == [Notification(source="vm", event="disk_task_done", result=None)]


# ── Freebox.events() ───────────────────────────────────────────────────────────

class TestFreeboxEvents:
    def _make_open_freebox(self) -> Freebox:
        fb = Freebox(
            app_id=APP_ID,
            app_name=APP_NAME,
            app_version=APP_VERSION,
            device_name=DEVICE_NAME,
            on_pending=lambda _: None,
        )
        fb.discovery = DiscoveryInfo._from_dict(DISCOVERY_DATA)
        fb._auth.session_token = SESSION_TOKEN
        return fb

    def test_events_returns_event_stream(self):
        fb = self._make_open_freebox()
        stream = fb.events(["vm_state_changed"])
        assert isinstance(stream, EventStream)

    def test_events_uses_correct_ws_url(self):
        fb = self._make_open_freebox()
        stream = fb.events(["vm_state_changed"])
        assert stream._url == WS_URL

    def test_events_with_custom_port(self):
        fb = Freebox(
            app_id=APP_ID,
            app_name=APP_NAME,
            app_version=APP_VERSION,
            device_name=DEVICE_NAME,
            port=8443,
            on_pending=lambda _: None,
        )
        fb.discovery = DiscoveryInfo._from_dict(DISCOVERY_DATA)
        fb._auth.session_token = SESSION_TOKEN
        stream = fb.events(["vm_state_changed"])
        assert stream._url == "wss://mafreebox.freebox.fr:8443/api/v16/ws/event"

    def test_events_raises_when_not_connected(self):
        fb = Freebox(
            app_id=APP_ID,
            app_name=APP_NAME,
            app_version=APP_VERSION,
            device_name=DEVICE_NAME,
            on_pending=lambda _: None,
        )
        with pytest.raises(AuthenticationError):
            fb.events(["vm_state_changed"])
