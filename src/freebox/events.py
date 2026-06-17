"""WebSocket event stream for the Freebox API."""
from __future__ import annotations

import json
import ssl
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from freebox.auth import raise_for_error_code
from freebox.exceptions import FreeboxError


@dataclass
class Notification:
    """A WebSocket notification pushed by the Freebox."""

    source: str
    event: str
    result: Any = field(default=None)


class EventStream:
    """Synchronous iterator over Freebox WebSocket event notifications.

    Obtain one from :meth:`~freebox.Freebox.events` and use it as a context
    manager::

        with fb.events(["vm_state_changed", "lan_host_l3addr_reachable"]) as stream:
            for notification in stream:
                print(notification.source, notification.event, notification.result)

    Iteration stops when the server closes the connection.  Any other error
    propagates as an exception.
    """

    def __init__(
        self,
        url: str,
        session_token: str,
        events: list[str],
        ssl_ctx: ssl.SSLContext,
    ) -> None:
        self._url = url
        self._token = session_token
        self._events = events
        self._ssl = ssl_ctx
        self._conn: Any = None

    def __enter__(self) -> EventStream:
        import websockets.sync.client as _ws
        import websockets.exceptions as _exc

        self._exc_mod = _exc
        self._conn = _ws.connect(
            self._url,
            additional_headers={"X-Fbx-App-Auth": self._token},
            ssl=self._ssl,
        )
        self._conn.send(json.dumps({"action": "register", "events": self._events}))
        resp = json.loads(self._conn.recv())
        if not resp.get("success"):
            self._conn.close()
            self._conn = None
            code = resp.get("error_code", "unknown")
            msg = resp.get("msg", "WebSocket register failed")
            raise_for_error_code(code, msg)
        return self

    def __exit__(self, *_: object) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __iter__(self) -> Iterator[Notification]:
        return self

    def __next__(self) -> Notification:
        if self._conn is None:
            raise StopIteration
        try:
            raw = self._conn.recv()
        except self._exc_mod.ConnectionClosed:
            raise StopIteration
        data = json.loads(raw)
        return Notification(
            source=data.get("source", ""),
            event=data.get("event", ""),
            result=data.get("result"),
        )
