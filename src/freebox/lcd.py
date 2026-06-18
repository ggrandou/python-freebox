"""Freebox LCD screen API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from freebox.client import Freebox


@dataclass
class LcdConfig:
    """LCD screen configuration (GET/PUT /lcd/config/)."""

    brightness: int
    orientation: int
    orientation_forced: bool
    hide_wifi_key: bool
    led_strip_enabled: bool
    led_strip_brightness: int
    led_strip_animation: str
    available_led_strip_animations: list[str]
    hide_status_led: bool
    screensaver: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LcdConfig:
        return cls(
            brightness=d.get("brightness", 0),
            orientation=d.get("orientation", 0),
            orientation_forced=d.get("orientation_forced", False),
            hide_wifi_key=d.get("hide_wifi_key", False),
            led_strip_enabled=d.get("led_strip_enabled", False),
            led_strip_brightness=d.get("led_strip_brightness", 0),
            led_strip_animation=d.get("led_strip_animation", ""),
            available_led_strip_animations=d.get("available_led_strip_animations", []),
            hide_status_led=d.get("hide_status_led", False),
            screensaver=d.get("screensaver", ""),
        )


class Lcd:
    """Freebox LCD screen API.

    Obtained via ``fb.lcd``::

        cfg = fb.lcd.config()
        print(cfg.brightness, cfg.orientation)
    """

    def __init__(self, client: Freebox) -> None:
        self._client = client

    def config(self) -> LcdConfig:
        """Return the current LCD screen configuration."""
        return LcdConfig._from_dict(self._client.get("lcd/config/"))

    def set_config(self, **kwargs: Any) -> LcdConfig:
        """Update the LCD screen configuration.

        Pass only the fields to change, e.g. ``set_config(brightness=50)``.
        """
        return LcdConfig._from_dict(self._client.put("lcd/config/", json=kwargs))
