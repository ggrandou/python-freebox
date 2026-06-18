"""Freebox RRD Stats API."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


class RRDDatabase(str, Enum):
    """RRD database identifier."""

    NET = "net"
    TEMP = "temp"
    DSL = "dsl"
    SWITCH = "switch"


@dataclass
class RRDSample:
    """One time-stamped sample returned by the RRD API."""

    time: int
    values: dict[str, int] = field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RRDSample:
        t = d.get("time", 0)
        values = {k: v for k, v in d.items() if k != "time"}
        return cls(time=t, values=values)


@dataclass
class RRDResult:
    """Response returned by ``POST /rrd/``."""

    date_start: int
    date_end: int
    data: list[RRDSample] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RRDResult:
        return cls(
            date_start=d.get("date_start", 0),
            date_end=d.get("date_end", 0),
            data=[RRDSample._from_dict(s) for s in d.get("data", [])],
        )


class Rrd:
    """Freebox RRD Stats API.

    Obtained via ``fb.rrd``::

        result = fb.rrd.fetch(RRDDatabase.TEMP, fields=["cpum", "cpub"])
        for sample in result.data:
            print(sample.time, sample.values)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def fetch(
        self,
        db: RRDDatabase | str,
        *,
        date_start: int | None = None,
        date_end: int | None = None,
        precision: int | None = None,
        fields: list[str] | None = None,
    ) -> RRDResult:
        """Return RRD statistics for the given database.

        Args:
            db: Database to query (net, temp, dsl, switch).
            date_start: Start timestamp (optional, adjusted to available resolution).
            date_end: End timestamp (optional, adjusted to available resolution).
            precision: Multiply all values by this factor before returning.
            fields: Restrict to these fields; returns all fields when omitted.
        """
        db_value = db.value if isinstance(db, RRDDatabase) else db
        params: list[tuple[str, str]] = [("db", db_value)]
        if date_start is not None:
            params.append(("date_start", str(date_start)))
        if date_end is not None:
            params.append(("date_end", str(date_end)))
        if precision is not None:
            params.append(("precision", str(precision)))
        if fields is not None:
            for f in fields:
                params.append(("fields[]", f))
        result = self._client.get("rrd/", params=params)
        return RRDResult._from_dict(result)
