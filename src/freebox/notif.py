"""Freebox Notification API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class NotificationTarget:
    """A registered push-notification target device.

    Note: the ``id`` field is documented by Freebox but not returned by the
    v16 API in practice; it defaults to ``None`` when absent.
    """

    name: str
    type: str
    last_use: int
    api_url: str
    message_type: str
    subscriptions: list[str] = field(default_factory=list)
    id: str | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> NotificationTarget:
        return cls(
            id=d.get("id") or None,
            name=d.get("name", ""),
            type=d.get("type", ""),
            last_use=d.get("last_use", 0),
            api_url=d.get("api_url", ""),
            message_type=d.get("message_type", ""),
            subscriptions=list(d.get("subscriptions", [])),
        )


class Notif:
    """Freebox Notification API.

    Obtained via ``fb.notif``::

        targets = fb.notif.get_targets()
        for t in targets:
            print(t.id, t.name, t.type)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def get_targets(self) -> list[NotificationTarget]:
        """Return all registered notification targets."""
        result = self._client.get("notif/targets")
        return [NotificationTarget._from_dict(t) for t in (result or [])]

    def get_target(self, target_id: str) -> NotificationTarget:
        """Return the notification target with the given id."""
        result = self._client.get(f"notif/targets/{target_id}")
        if isinstance(result, list):
            return NotificationTarget._from_dict(result[0])
        return NotificationTarget._from_dict(result)

    def create_target(
        self,
        *,
        name: str,
        type: str,
        token: str,
        api_url: str,
        message_type: str = "notification",
        subscriptions: list[str] | None = None,
    ) -> None:
        """Register a new notification target device.

        Args:
            name: Human-readable device name.
            type: Device type: ``ios``, ``android``, or ``firebase``.
            token: Push notification service token.
            api_url: URL of the notification relay server.
            message_type: ``notification`` (with title/body) or ``data`` (payload only).
            subscriptions: Event types to subscribe to (phone, download, security,
                box_state, lan_host, password_change).
        """
        payload: dict[str, Any] = {
            "name": name,
            "type": type,
            "token": token,
            "api_url": api_url,
            "message_type": message_type,
        }
        if subscriptions is not None:
            payload["subscriptions"] = subscriptions
        self._client.post("notif/targets/", json=payload)

    def update_target(
        self,
        target_id: str,
        *,
        name: str | None = None,
        type: str | None = None,
        token: str | None = None,
        api_url: str | None = None,
        message_type: str | None = None,
        subscriptions: list[str] | None = None,
    ) -> None:
        """Update the notification target with the given id."""
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if type is not None:
            payload["type"] = type
        if token is not None:
            payload["token"] = token
        if api_url is not None:
            payload["api_url"] = api_url
        if message_type is not None:
            payload["message_type"] = message_type
        if subscriptions is not None:
            payload["subscriptions"] = subscriptions
        self._client.put(f"notif/targets/{target_id}", json=payload)

    def delete_target(self, target_id: str) -> None:
        """Delete the notification target with the given id."""
        self._client.delete(f"notif/targets/{target_id}")
