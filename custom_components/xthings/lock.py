"""Lock platform for the Xthings (U-tec) integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import XthingsDataUpdateCoordinator
from .entity import XthingsEntity
from .models import XthingsDeviceInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xthings lock entities from a config entry."""
    coordinator: XthingsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[XthingsLockEntity] = [
        XthingsLockEntity(coordinator, device_info)
        for device_info in coordinator.data.devices.values()
        if device_info.is_lock
    ]

    async_add_entities(entities)


class XthingsLockEntity(XthingsEntity, LockEntity):
    """Representation of a U-tec lock via the xthings API."""

    _attr_name = None  # Use device name as entity name

    def __init__(
        self,
        coordinator: XthingsDataUpdateCoordinator,
        device_info: XthingsDeviceInfo,
    ) -> None:
        """Initialize the lock entity."""
        super().__init__(coordinator, device_info)
        self._attr_unique_id = f"{device_info.device_id}_lock"
        self._locking: bool = False
        self._unlocking: bool = False
        self._clear_locking_handle: Any = None
        self._clear_unlocking_handle: Any = None
        self._command_in_flight: bool = False

    @property
    def is_locked(self) -> bool | None:
        """Return True if the lock is locked."""
        state = self._device_state
        if state is None or state.lock_state is None:
            return None
        return state.lock_state == "locked"

    @property
    def is_locking(self) -> bool:
        """Return True if the lock is in the process of locking."""
        return self._locking

    @property
    def is_unlocking(self) -> bool:
        """Return True if the lock is in the process of unlocking."""
        return self._unlocking

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Clear in-progress flags when we receive fresh data after a command
        if self._command_in_flight:
            self._command_in_flight = False
            self._locking = False
            self._unlocking = False
            # Cancel scheduled timeouts since coordinator update arrived
            if self._clear_locking_handle:
                self._clear_locking_handle.cancel()
                self._clear_locking_handle = None
            if self._clear_unlocking_handle:
                self._clear_unlocking_handle.cancel()
                self._clear_unlocking_handle = None
        super()._handle_coordinator_update()

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the device."""
        _LOGGER.debug("Locking %s (%s)", self._device_info.name, self._device_id)

        # Cancel any pending flag clear
        if self._clear_locking_handle:
            self._clear_locking_handle.cancel()
            self._clear_locking_handle = None

        self._locking = True
        self.async_write_ha_state()

        try:
            deferred_seconds = await self.coordinator.api.async_lock(
                self._device_id, self._device_info.custom_data
            )

            # Mark that a command is in flight so coordinator update clears flags
            self._command_in_flight = True

            # Schedule a refresh after the deferred response period
            if deferred_seconds:
                await self.coordinator.async_request_refresh_after(deferred_seconds + 2)
            else:
                await self.coordinator.async_request_refresh()

            # Safety timeout: clear flag if coordinator update doesn't arrive
            timeout = (deferred_seconds + 5) if deferred_seconds else 5
            self._clear_locking_handle = self.hass.loop.call_later(
                timeout,
                self._timeout_clear_flags,
            )
        except Exception:
            _LOGGER.exception("Failed to lock %s", self._device_info.name)
            self._locking = False
            self._command_in_flight = False
            self.async_write_ha_state()
            raise

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the device."""
        _LOGGER.debug("Unlocking %s (%s)", self._device_info.name, self._device_id)

        # Cancel any pending flag clear
        if self._clear_unlocking_handle:
            self._clear_unlocking_handle.cancel()
            self._clear_unlocking_handle = None

        self._unlocking = True
        self.async_write_ha_state()

        try:
            deferred_seconds = await self.coordinator.api.async_unlock(
                self._device_id, self._device_info.custom_data
            )

            # Mark that a command is in flight so coordinator update clears flags
            self._command_in_flight = True

            # Schedule a refresh after the deferred response period
            if deferred_seconds:
                await self.coordinator.async_request_refresh_after(deferred_seconds + 2)
            else:
                await self.coordinator.async_request_refresh()

            # Safety timeout: clear flag if coordinator update doesn't arrive
            timeout = (deferred_seconds + 5) if deferred_seconds else 5
            self._clear_unlocking_handle = self.hass.loop.call_later(
                timeout,
                self._timeout_clear_flags,
            )
        except Exception:
            _LOGGER.exception("Failed to unlock %s", self._device_info.name)
            self._unlocking = False
            self._command_in_flight = False
            self.async_write_ha_state()
            raise

    def _timeout_clear_flags(self) -> None:
        """Safety timeout to clear in-progress flags."""
        self._locking = False
        self._unlocking = False
        self._command_in_flight = False
        self._clear_locking_handle = None
        self._clear_unlocking_handle = None
        self.async_write_ha_state()
