"""Base entity for the Xthings (U-tec) integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import XthingsDataUpdateCoordinator
from .models import XthingsDeviceInfo, XthingsDeviceState


class XthingsEntity(CoordinatorEntity[XthingsDataUpdateCoordinator]):
    """Base class for all Xthings entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: XthingsDataUpdateCoordinator,
        device_info: XthingsDeviceInfo,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, context=device_info.device_id)

        self._device_id = device_info.device_id
        self._device_info = device_info

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_info.device_id)},
            name=device_info.name,
            manufacturer=device_info.manufacturer,
            model=device_info.model,
            sw_version=device_info.hw_version,
        )

    @property
    def _device_state(self) -> XthingsDeviceState | None:
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
