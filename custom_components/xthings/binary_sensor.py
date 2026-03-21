"""Binary sensor platform for the Xthings (U-tec) integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up Xthings binary sensor entities from a config entry."""
    coordinator: XthingsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = []
    for device_id, device_info in coordinator.data.devices.items():
        if device_info.is_lock:
            entities.append(
                XthingsConnectivitySensor(coordinator, device_info)
            )

    async_add_entities(entities)


class XthingsConnectivitySensor(XthingsEntity, BinarySensorEntity):
    """Connectivity sensor for a U-tec lock."""

    _attr_name = "Connectivity"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: XthingsDataUpdateCoordinator,
        device_info: XthingsDeviceInfo,
    ) -> None:
        """Initialize the connectivity sensor."""
        super().__init__(coordinator, device_info)
        self._attr_unique_id = f"{device_info.device_id}_connectivity"

    @property
    def is_on(self) -> bool | None:
        """Return True if the device is online."""
        state = self._device_state
        if state is None:
            return None
        return state.online
