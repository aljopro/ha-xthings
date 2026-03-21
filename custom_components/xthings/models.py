"""
Data models for the Xthings (U-tec) integration.

Kept separate from coordinator.py so they can be imported
and tested without the homeassistant dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .const import CATEGORY_LOCK, SUPPORTED_LOCK_HANDLERS


@dataclass
class XthingsDeviceInfo:
    """Cached device information from Discovery."""

    device_id: str
    name: str
    category: str
    handle_type: str
    manufacturer: str
    model: str
    hw_version: str
    custom_data: dict[str, Any] = field(default_factory=dict)

    @property
    def is_lock(self) -> bool:
        """Return True if this device is a lock."""
        return (
            self.category.upper() == CATEGORY_LOCK
            or self.handle_type in SUPPORTED_LOCK_HANDLERS
        )


@dataclass
class XthingsDeviceState:
    """Current state of a device."""

    online: bool = False
    lock_state: str | None = None  # "locked" / "unlocked" / "jammed" / "unknown"
    battery_level: int | None = None
    is_jammed: bool = False
    door_state: str | None = None  # "closed" / "open" / "unknown" (utec-lock-sensor)


@dataclass
class XthingsCoordinatorData:
    """Data structure held by the coordinator."""

    devices: dict[str, XthingsDeviceInfo] = field(default_factory=dict)
    states: dict[str, XthingsDeviceState] = field(default_factory=dict)
