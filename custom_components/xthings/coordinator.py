"""Data update coordinator for the Xthings (U-tec) integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import XthingsApiClient, XthingsApiError, XthingsAuthError
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .models import (
    XthingsCoordinatorData,
    XthingsDeviceInfo,
    XthingsDeviceState,
)

_LOGGER = logging.getLogger(__name__)

# Xthings battery level is integer 1-5, map to approximate percentage
BATTERY_LEVEL_MAP = {1: 10, 2: 30, 3: 50, 4: 75, 5: 100}

# Rapid polling after commands
RAPID_POLL_INTERVAL = 3  # seconds between rapid polls
RAPID_POLL_MAX_CHECKS = 10  # max rapid polls before backing off


def _battery_level_to_percent(level: int | None) -> int | None:
    """Convert xthings battery level (1-5) to a percentage."""
    if level is None:
        return None
    return BATTERY_LEVEL_MAP.get(level, max(0, min(100, level * 20)))


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
        self._rapid_poll_count: int = 0
        self._rapid_poll_unsub: CALLBACK_TYPE | None = None

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
            raise UpdateFailed(f"Failed to discover devices: {err}") from err

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
            _LOGGER.debug(
                "Raw states for %s (%s): %s",
                device_info.name,
                device_id,
                device_states,
            )
            for s in device_states:
                capability = s.get("capability", "").lower()
                name = s.get("name", "")
                value = s.get("value")

                if capability == "st.healthcheck" and name == "status":
                    state.online = str(value).lower() == "online"
                elif capability == "st.lock" and name == "lockState":
                    state.lock_state = str(value).lower()
                elif capability == "st.batterylevel" and name == "level":
                    # API returns 1-5 scale, map to percentage
                    state.battery_level = _battery_level_to_percent(value)

            states[device_id] = state

        data.states = states
        return data

    async def async_request_refresh_after(self, seconds: int) -> None:
        """Schedule rapid polling after a deferred command response."""
        # Cancel any existing rapid poll schedule
        self.cancel_rapid_poll()

        async def _start_rapid_polling() -> None:
            await asyncio.sleep(seconds)
            self._rapid_poll_count = 0
            await self.async_request_refresh()
            self._schedule_next_rapid_poll()

        self.hass.async_create_task(_start_rapid_polling())

    def start_rapid_polling(self) -> None:
        """Start rapid polling immediately (no deferred delay)."""
        self.cancel_rapid_poll()
        self._rapid_poll_count = 0
        self._schedule_next_rapid_poll()

    def _schedule_next_rapid_poll(self) -> None:
        """Schedule the next rapid poll if under the max check count."""
        if self._rapid_poll_count >= RAPID_POLL_MAX_CHECKS:
            _LOGGER.debug(
                "Rapid polling complete after %d checks",
                self._rapid_poll_count,
            )
            self._rapid_poll_unsub = None
            return

        self._rapid_poll_unsub = async_call_later(
            self.hass,
            RAPID_POLL_INTERVAL,
            self._async_rapid_poll_tick,
        )

    async def _async_rapid_poll_tick(self, _now: Any) -> None:
        """Execute one rapid poll tick."""
        self._rapid_poll_count += 1
        _LOGGER.debug(
            "Rapid poll %d/%d",
            self._rapid_poll_count,
            RAPID_POLL_MAX_CHECKS,
        )
        await self.async_request_refresh()
        self._schedule_next_rapid_poll()

    def cancel_rapid_poll(self) -> None:
        """Cancel any pending rapid poll."""
        if self._rapid_poll_unsub:
            self._rapid_poll_unsub()
            self._rapid_poll_unsub = None
        self._rapid_poll_count = 0
