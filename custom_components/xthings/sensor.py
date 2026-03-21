"""Sensor platform for the Xthings (U-tec) integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import XthingsDataUpdateCoordinator
from .entity import XthingsEntity
from .models import XthingsDeviceInfo


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xthings sensor entities from a config entry."""
    coordinator: XthingsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        XthingsBatterySensor(coordinator, device_info)
        for device_info in coordinator.data.devices.values()
        if device_info.is_lock
    ]

    async_add_entities(entities)


class XthingsBatterySensor(XthingsEntity, SensorEntity):
    """Battery level sensor for a U-tec lock."""

    _attr_name = "Battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: XthingsDataUpdateCoordinator,
        device_info: XthingsDeviceInfo,
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator, device_info)
        self._attr_unique_id = f"{device_info.device_id}_battery"

    @property
    def native_value(self) -> int | None:
        """Return the battery level percentage."""
        state = self._device_state
        if state is None:
            return None
        return state.battery_level
