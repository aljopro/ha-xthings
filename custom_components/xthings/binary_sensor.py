"""Binary sensor platform for the Xthings (U-tec) integration."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import XthingsDataUpdateCoordinator
from .models import XthingsDeviceInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xthings binary sensor entities from a config entry."""
    coordinator: XthingsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[XthingsConnectivitySensor] = []
    for device_id, device_info in coordinator.data.devices.items():
        if device_info.is_lock:
            entities.append(
                XthingsConnectivitySensor(coordinator, device_info)
            )

    async_add_entities(entities)


class XthingsConnectivitySensor(
    CoordinatorEntity[XthingsDataUpdateCoordinator], BinarySensorEntity
):
    """Connectivity sensor for a U-tec lock."""

    _attr_has_entity_name = True
    _attr_name = "Connectivity"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: XthingsDataUpdateCoordinator,
        device_info: XthingsDeviceInfo,
    ) -> None:
        """Initialize the connectivity sensor."""
        super().__init__(coordinator, context=device_info.device_id)

        self._device_id = device_info.device_id
        self._device_info = device_info

        self._attr_unique_id = f"{device_info.device_id}_connectivity"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_info.device_id)},
            name=device_info.name,
            manufacturer=device_info.manufacturer,
            model=device_info.model,
            sw_version=device_info.hw_version,
        )

    @property
    def _device_state(self):
        """Get the current device state from coordinator data."""
        if self.coordinator.data and self.coordinator.data.states:
            return self.coordinator.data.states.get(self._device_id)
        return None

    @property
    def available(self) -> bool:
        """Return True if we have state data from the coordinator."""
        if not super().available:
            return False
        return self._device_state is not None

    @property
    def is_on(self) -> bool | None:
        """Return True if the device is online."""
        state = self._device_state
        if state is None:
            return None
        return state.online

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
