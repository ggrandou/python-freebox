"""Freebox Home Automation API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


# ── Data objects ──────────────────────────────────────────────────────────────

@dataclass
class HomeAdapterType:
    """Technical type of a home automation adapter."""

    name: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeAdapterType:
        return cls(name=d.get("name", ""))


@dataclass
class HomeAdapter:
    """A home automation adapter (dongle or built-in controller)."""

    id: int
    label: str
    status: str
    icon_url: str
    type: HomeAdapterType | None
    props: dict[str, Any]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeAdapter:
        return cls(
            id=d.get("id", 0),
            label=d.get("label", ""),
            status=d.get("status", ""),
            icon_url=d.get("icon_url", ""),
            type=HomeAdapterType._from_dict(d["type"]) if "type" in d else None,
            props=dict(d.get("props") or {}),
        )


@dataclass
class HomePairingStepField:
    """A UI element shown during a pairing step."""

    widget: str
    text: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomePairingStepField:
        return cls(
            widget=d.get("widget", ""),
            text=str(d.get("text", "")),
        )


@dataclass
class HomePairingStep:
    """One step in an interactive pairing workflow."""

    pageid: int
    session: int
    refresh: int
    icon_url: str
    fields: list[HomePairingStepField]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomePairingStep:
        return cls(
            pageid=d.get("pageid", 0),
            session=d.get("session", 0),
            refresh=d.get("refresh", 0),
            icon_url=d.get("icon_url", ""),
            fields=[HomePairingStepField._from_dict(f) for f in d.get("fields") or []],
        )


@dataclass
class HomeNodeType:
    """Type descriptor for a home automation node."""

    name: str
    label: str
    icon: str
    physical: bool

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeNodeType:
        return cls(
            name=d.get("name", ""),
            label=d.get("label", ""),
            icon=d.get("icon", ""),
            physical=d.get("physical", False),
        )


@dataclass
class HomeNodeEndpointUi:
    """Display/UI descriptor for a node endpoint."""

    display: str
    access: str
    icon_url: str
    unit: str
    range: list[float]
    icon_color: str
    text_color: str
    value_color: str
    icon_color_range: list[str]
    text_color_range: list[str]
    value_color_range: list[str]
    status_text_range: list[str]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeNodeEndpointUi:
        return cls(
            display=d.get("display", ""),
            access=d.get("access", ""),
            icon_url=d.get("icon_url", ""),
            unit=d.get("unit", ""),
            range=list(d.get("range") or []),
            icon_color=d.get("icon_color", ""),
            text_color=d.get("text_color", ""),
            value_color=d.get("value_color", ""),
            icon_color_range=list(d.get("icon_color_range") or []),
            text_color_range=list(d.get("text_color_range") or []),
            value_color_range=list(d.get("value_color_range") or []),
            status_text_range=list(d.get("status_text_range") or []),
        )


@dataclass
class HomeNodeEndpoint:
    """An endpoint (signal or slot) exposed by a home automation node."""

    id: int
    ep_type: str
    category: str
    visibility: str
    access: str
    label: str
    name: str
    value_type: str
    value: Any
    ui: HomeNodeEndpointUi | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeNodeEndpoint:
        return cls(
            id=d.get("id", 0),
            ep_type=d.get("ep_type", ""),
            category=d.get("category", ""),
            visibility=d.get("visibility", ""),
            access=d.get("access", ""),
            label=d.get("label", ""),
            name=d.get("name", ""),
            value_type=d.get("value_type", ""),
            value=d.get("value"),
            ui=HomeNodeEndpointUi._from_dict(d["ui"]) if "ui" in d else None,
        )


@dataclass
class HomeNode:
    """A home automation node (physical device or virtual object)."""

    id: int
    adapter: int
    label: str
    name: str
    category: str
    status: str
    type: HomeNodeType | None
    show_endpoints: list[HomeNodeEndpoint]
    signal_links: list[Any]
    slot_links: list[Any]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeNode:
        return cls(
            id=d.get("id", 0),
            adapter=d.get("adapter", 0),
            label=d.get("label", ""),
            name=d.get("name", ""),
            category=d.get("category", ""),
            status=d.get("status", ""),
            type=HomeNodeType._from_dict(d["type"]) if "type" in d else None,
            show_endpoints=[HomeNodeEndpoint._from_dict(e) for e in d.get("show_endpoints") or []],
            signal_links=list(d.get("signal_links") or []),
            slot_links=list(d.get("slot_links") or []),
        )


@dataclass
class HomeEndpointValue:
    """Current value of a node endpoint."""

    value: Any
    value_type: str
    unit: str
    refresh: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeEndpointValue:
        return cls(
            value=d.get("value"),
            value_type=d.get("value_type", ""),
            unit=d.get("unit", ""),
            refresh=d.get("refresh", 0),
        )


@dataclass
class HomeNodeGroup:
    """Group label and icon for a home tile."""

    label: str
    icon_url: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeNodeGroup:
        return cls(
            label=d.get("label", ""),
            icon_url=d.get("icon_url", ""),
        )


@dataclass
class HomeTileData:
    """One data point shown on a home tile."""

    ep_id: int
    label: str
    value_type: str
    value: Any
    refresh: int
    ui: HomeNodeEndpointUi | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeTileData:
        return cls(
            ep_id=d.get("ep_id", 0),
            label=d.get("label", ""),
            value_type=d.get("value_type", ""),
            value=d.get("value"),
            refresh=d.get("refresh", 0),
            ui=HomeNodeEndpointUi._from_dict(d["ui"]) if "ui" in d else None,
        )


@dataclass
class HomeTile:
    """A user-friendly tile representing one or more node endpoints."""

    node_id: int
    label: str
    action: str
    type: str
    group: HomeNodeGroup | None
    data: list[HomeTileData]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> HomeTile:
        return cls(
            node_id=d.get("node_id", 0),
            label=d.get("label", ""),
            action=d.get("action", ""),
            type=d.get("type", ""),
            group=HomeNodeGroup._from_dict(d["group"]) if "group" in d else None,
            data=[HomeTileData._from_dict(x) for x in d.get("data") or []],
        )


# ── API class ─────────────────────────────────────────────────────────────────

class Home:
    """Freebox Home Automation API.

    Obtained via ``fb.home``::

        adapters = fb.home.adapters()
        nodes    = fb.home.nodes()
        tiles    = fb.home.tileset()
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    # ── Adapters ───────────────────────────────────────────────────────────────

    def adapters(self) -> list[HomeAdapter]:
        """Return the list of registered home automation adapters."""
        return [HomeAdapter._from_dict(a) for a in self._client.get("home/adapters") or []]

    def adapter(self, adapter_id: int) -> HomeAdapter:
        """Return the adapter with the given id."""
        return HomeAdapter._from_dict(self._client.get(f"home/adapters/{adapter_id}"))

    def set_adapter(self, adapter_id: int, **kwargs: Any) -> None:
        """Update an adapter (e.g. change its ``status``).

        Accepted keyword arguments: ``status`` (``"disabled"`` / ``"active"``).
        """
        self._client.put(f"home/adapters/{adapter_id}", json=kwargs)

    # ── Pairing ────────────────────────────────────────────────────────────────

    def pairing_step(self, adapter_id: int) -> HomePairingStep:
        """Return the current pairing step for the given adapter."""
        return HomePairingStep._from_dict(self._client.get(f"home/pairing/{adapter_id}"))

    def start_pairing(self, adapter_id: int, type: str = "") -> None:  # noqa: A002
        """Start the pairing process on the given adapter.

        ``type`` is required for the domus adapter
        (e.g. ``"node::domus::sercomm::pir"``).
        """
        payload: dict[str, Any] = {"op": "start"}
        if type:
            payload["type"] = type
        self._client.post(f"home/pairing/{adapter_id}", json=payload)

    def next_pairing_step(
        self,
        adapter_id: int,
        session: int,
        pageid: int,
        fields: list[Any],
    ) -> HomePairingStep:
        """Submit the current pairing step and return the next one."""
        return HomePairingStep._from_dict(
            self._client.post(
                f"home/pairing/{adapter_id}",
                json={"op": "next", "session": session, "pageid": pageid, "fields": fields},
            )
        )

    def stop_pairing(self, adapter_id: int, session: int) -> None:
        """Cancel an ongoing pairing session."""
        self._client.post(f"home/pairing/{adapter_id}", json={"op": "stop", "session": session})

    # ── Nodes ──────────────────────────────────────────────────────────────────

    def nodes(self) -> list[HomeNode]:
        """Return the list of all home automation nodes."""
        return [HomeNode._from_dict(n) for n in self._client.get("home/nodes") or []]

    def node(self, node_id: int) -> HomeNode:
        """Return the node with the given id."""
        return HomeNode._from_dict(self._client.get(f"home/nodes/{node_id}"))

    def set_node(self, node_id: int, label: str) -> None:
        """Rename the node with the given id."""
        self._client.put(f"home/nodes/{node_id}", json={"label": label})

    def delete_node(self, node_id: int) -> None:
        """Remove a node from the automation network."""
        self._client.delete(f"home/nodes/{node_id}")

    # ── Endpoint values ────────────────────────────────────────────────────────

    def endpoint_value(self, node_id: int, endpoint_id: int) -> HomeEndpointValue:
        """Return the current value of a node endpoint."""
        return HomeEndpointValue._from_dict(
            self._client.get(f"home/endpoints/{node_id}/{endpoint_id}")
        )

    def set_endpoint_value(self, node_id: int, endpoint_id: int, value: Any) -> None:
        """Push a new value to a node slot endpoint."""
        self._client.put(
            f"home/endpoints/{node_id}/{endpoint_id}", json={"value": value}
        )

    # ── Tileset ────────────────────────────────────────────────────────────────

    def tileset(self) -> list[HomeTile]:
        """Return the full tile list for all nodes."""
        return [HomeTile._from_dict(t) for t in self._client.get("home/tileset/all") or []]

    def node_tileset(self, node_id: int) -> list[HomeTile]:
        """Return the tile list for a specific node."""
        return [HomeTile._from_dict(t) for t in self._client.get(f"home/tileset/{node_id}") or []]
