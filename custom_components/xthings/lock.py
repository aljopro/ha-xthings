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

    entities: list[XthingsLockEntity] = []
    for device_id, device_info in coordinator.data.devices.items():
        if device_info.is_lock:
            entities.append(
                XthingsLockEntity(coordinator, device_info)
            )

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
        return self._attr_is_locking if hasattr(self, "_attr_is_locking") else False

    @property
    def is_unlocking(self) -> bool:
        """Return True if the lock is in the process of unlocking."""
        return self._attr_is_unlocking if hasattr(self, "_attr_is_unlocking") else False

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the device."""
        _LOGGER.debug("Locking %s (%s)", self._device_info.name, self._device_id)

        self._attr_is_locking = True
        self.async_write_ha_state()

        try:
            deferred_seconds = await self.coordinator.api.async_lock(
                self._device_id, self._device_info.custom_data
            )

            # Schedule a refresh after the deferred response period
            if deferred_seconds:
                await self.coordinator.async_request_refresh_after(deferred_seconds + 2)
            else:
                await self.coordinator.async_request_refresh()
        except Exception:
            _LOGGER.exception("Failed to lock %s", self._device_info.name)
            raise
        finally:
            self._attr_is_locking = False
            self.async_write_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the device."""
        _LOGGER.debug("Unlocking %s (%s)", self._device_info.name, self._device_id)

        self._attr_is_unlocking = True
        self.async_write_ha_state()

        try:
            deferred_seconds = await self.coordinator.api.async_unlock(
                self._device_id, self._device_info.custom_data
            )

            # Schedule a refresh after the deferred response period
            if deferred_seconds:
                await self.coordinator.async_request_refresh_after(deferred_seconds + 2)
            else:
                await self.coordinator.async_request_refresh()
        except Exception:
            _LOGGER.exception("Failed to unlock %s", self._device_info.name)
            raise
        finally:
            self._attr_is_unlocking = False
            self.async_write_ha_state()
