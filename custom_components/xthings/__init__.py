"""The Xthings (U-tec) integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .api import XthingsApiClient
from .const import DOMAIN
from .coordinator import XthingsDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LOCK, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xthings (U-tec) from a config entry."""
    # Get the OAuth2 implementation and create a session
    implementation = await config_entry_oauth2_flow.async_get_config_entry_implementation(
        hass, entry
    )
    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)

    # Create the API client
    api = XthingsApiClient(hass, session)

    # Create and initialize the coordinator
    coordinator = XthingsDataUpdateCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator for platform access
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Xthings config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
