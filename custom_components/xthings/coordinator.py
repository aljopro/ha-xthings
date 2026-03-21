"""Data update coordinator for the Xthings (U-tec) integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import XthingsApiClient, XthingsApiError, XthingsAuthError
from .const import (
    CAP_BATTERY_LEVEL,
    CAP_HEALTH_CHECK,
    CAP_LOCK_STATE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .models import (
    XthingsCoordinatorData,
    XthingsDeviceInfo,
    XthingsDeviceState,
)

_LOGGER = logging.getLogger(__name__)


class XthingsDataUpdateCoordinator(DataUpdateCoordinator[XthingsCoordinatorData]):
    """Coordinator to manage fetching xthings device data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: XthingsApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.config_entry = config_entry
        self.api = api

    async def async_setup(self) -> None:
        """Perform initial setup: discover devices."""
        await self._async_discover_devices()

    async def _async_discover_devices(self) -> None:
        """Discover all devices and cache their info."""
        try:
            devices = await self.api.async_get_devices()
        except XthingsAuthError as err:
            raise ConfigEntryAuthFailed(
                "Authentication failed during device discovery"
            ) from err
        except XthingsApiError as err:
            raise UpdateFailed(
                f"Failed to discover devices: {err}"
            ) from err

        device_map: dict[str, XthingsDeviceInfo] = {}
        for device in devices:
            device_info = device.get("deviceInfo", {})
            device_id = device.get("id", "")
            if not device_id:
                continue

            device_map[device_id] = XthingsDeviceInfo(
                device_id=device_id,
                name=device.get("name", "Unknown Device"),
                category=device.get("category", ""),
                handle_type=device.get("handleType", ""),
                manufacturer=device_info.get("manufacturer", "U-tec"),
                model=device_info.get("model", "Unknown"),
                hw_version=device_info.get("hwVersion", ""),
                custom_data=device.get("customData", {}),
            )

        if not self.data:
            self.data = XthingsCoordinatorData()

        self.data.devices = device_map
        _LOGGER.debug("Discovered %d devices", len(device_map))

    async def _async_update_data(self) -> XthingsCoordinatorData:
        """Fetch updated state for all devices."""
        if not self.data or not self.data.devices:
            # Re-discover if we have no devices yet
            await self._async_discover_devices()

        data = self.data or XthingsCoordinatorData()
        states: dict[str, XthingsDeviceState] = {}

        for device_id, device_info in data.devices.items():
            if not device_info.is_lock:
                continue

            try:
                device_states = await self.api.async_query_device(
                    device_id, device_info.custom_data
                )
            except XthingsAuthError as err:
                raise ConfigEntryAuthFailed(
                    "Authentication failed during device query"
                ) from err
            except XthingsApiError as err:
                _LOGGER.warning(
                    "Failed to query device %s (%s): %s",
                    device_info.name,
                    device_id,
                    err,
                )
                # Preserve previous state if available
                if device_id in (data.states or {}):
                    states[device_id] = data.states[device_id]
                else:
                    states[device_id] = XthingsDeviceState()
                continue

            state = XthingsDeviceState()
            for s in device_states:
                capability = s.get("capability", "")
                name = s.get("name", "")
                value = s.get("value")

                if capability == CAP_HEALTH_CHECK and name == "status":
                    state.online = value == "online"
                elif capability == CAP_LOCK_STATE and name == "lockState":
                    state.lock_state = value
                elif capability == CAP_BATTERY_LEVEL and name == "level":
                    state.battery_level = value

            states[device_id] = state

        data.states = states
        return data

    async def async_request_refresh_after(self, seconds: int) -> None:
        """Schedule a coordinator refresh after a delay.

        Used after lock/unlock commands which return a deferred response.
        """
        async def _delayed_refresh() -> None:
            await asyncio.sleep(seconds)
            await self.async_request_refresh()

        self.hass.async_create_task(_delayed_refresh())
