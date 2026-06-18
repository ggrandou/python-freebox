"""Freebox Language API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class LanguageSupport:
    """Current language and available languages (GET /lang/)."""

    lang: str
    available: list[str] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LanguageSupport:
        return cls(
            lang=d.get("lang", ""),
            available=list(d.get("avalaible") or []),
        )


class Lang:
    """Freebox Language API.

    Obtained via ``fb.lang``::

        info = fb.lang.get()
        print(info.lang, info.available)
        fb.lang.set("eng")
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def get(self) -> LanguageSupport:
        """Return the current language and list of supported languages."""
        return LanguageSupport._from_dict(self._client.get("lang/"))

    def set(self, lang: str) -> None:
        """Set the current language (ISO 639-3 alpha-3 code, e.g. 'fra', 'eng')."""
        self._client.post("lang/", json={"lang": lang})
