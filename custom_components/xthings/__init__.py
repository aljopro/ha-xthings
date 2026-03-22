"""The Xthings (U-tec) integration."""

from __future__ import annotations

import logging
from secrets import token_hex

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .api import XthingsApiClient
from .const import (
    CLOUDHOOK_URL_KEY,
    CONF_USE_WEBHOOK,
    CONF_WEBHOOK_URL,
    DOMAIN,
    WEBHOOK_ID_KEY,
    WEBHOOK_SCAN_INTERVAL,
)
from .coordinator import XthingsDataUpdateCoordinator
from .webhook import async_register_webhook, async_unregister_webhook

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.LOCK, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xthings (U-tec) from a config entry."""
    # Get the OAuth2 implementation and create a session
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )
    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)

    # Create the API client
    api = XthingsApiClient(hass, session)

    # Determine if webhooks are requested
    use_webhook = entry.options.get(CONF_USE_WEBHOOK, False)
    webhook_url: str | None = None

    if use_webhook:
        webhook_id = entry.data.get(WEBHOOK_ID_KEY) or token_hex(16)

        # Manual URL takes priority; fall back to Nabu Casa cloudhook
        manual_url = entry.options.get(CONF_WEBHOOK_URL, "").strip()
        if manual_url:
            # User supplied their own externally-reachable URL; build the
            # full webhook path from it.
            webhook_url = f"{manual_url.rstrip('/')}/api/webhook/{webhook_id}"
            # Persist webhook_id
            if WEBHOOK_ID_KEY not in entry.data:
                hass.config_entries.async_update_entry(
                    entry, data={**entry.data, WEBHOOK_ID_KEY: webhook_id}
                )
        elif "cloud" in hass.config.components:
            webhook_url = await _async_get_cloudhook_url(hass, entry, webhook_id)

        if webhook_url:
            # Register the local HA webhook handler
            async_register_webhook(hass, webhook_id)

            # Register the URL with the Xthings API
            try:
                await api.async_register_notification_url(webhook_url)
                _LOGGER.info("Registered webhook URL with Xthings API")
            except Exception:
                _LOGGER.exception("Failed to register notification URL")
                webhook_url = None
                async_unregister_webhook(hass, webhook_id)

    # Create and initialize the coordinator
    scan_interval = WEBHOOK_SCAN_INTERVAL if webhook_url else None
    coordinator = XthingsDataUpdateCoordinator(
        hass, entry, api, scan_interval=scan_interval
    )
    await coordinator.async_setup()
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator for platform access
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options changes to reload
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Xthings config entry."""
    # Unregister webhook if active
    webhook_id = entry.data.get(WEBHOOK_ID_KEY)
    if webhook_id:
        async_unregister_webhook(hass, webhook_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_get_cloudhook_url(
    hass: HomeAssistant, entry: ConfigEntry, webhook_id: str
) -> str | None:
    """Create or retrieve a Nabu Casa cloudhook URL."""
    # Save webhook_id into entry data if new
    if WEBHOOK_ID_KEY not in entry.data:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, WEBHOOK_ID_KEY: webhook_id}
        )

    # Return cached cloudhook URL if available
    if CLOUDHOOK_URL_KEY in entry.data:
        return str(entry.data[CLOUDHOOK_URL_KEY])

    try:
        cloud = hass.components.cloud  # type: ignore[attr-defined]
        url: str = await cloud.async_create_cloudhook(webhook_id)
    except Exception:
        _LOGGER.exception("Failed to create cloudhook")
        return None
    else:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CLOUDHOOK_URL_KEY: url}
        )
        return url
