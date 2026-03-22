"""Webhook handler for Xthings (U-tec) push notifications."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import web
from homeassistant.components.webhook import (
    async_register as webhook_register,
)
from homeassistant.components.webhook import (
    async_unregister as webhook_unregister,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_handle_webhook(
    hass: HomeAssistant,
    webhook_id: str,  # noqa: ARG001 - required by HA webhook callback signature
    request: web.Request,
) -> web.Response:
    """Handle an incoming webhook from the Xthings API."""
    try:
        data: dict[str, Any] = await request.json()
    except ValueError:
        _LOGGER.warning("Received non-JSON webhook payload")
        return web.Response(status=400)

    header = data.get("header", {})
    namespace = header.get("namespace", "")
    name = header.get("name", "")
    payload = data.get("payload", {})

    _LOGGER.debug(
        "Webhook received: %s.%s (messageId=%s)",
        namespace,
        name,
        header.get("messageId", "unknown"),
    )

    # Route to the correct coordinator
    if DOMAIN not in hass.data:
        return web.Response(status=200)

    for coordinator in hass.data[DOMAIN].values():
        if hasattr(coordinator, "async_process_webhook"):
            await coordinator.async_process_webhook(namespace, name, payload)

    return web.Response(status=200)


def async_register_webhook(
    hass: HomeAssistant,
    webhook_id: str,
) -> None:
    """Register the webhook with Home Assistant."""
    webhook_register(
        hass,
        DOMAIN,
        "Xthings Notifications",
        webhook_id,
        async_handle_webhook,
    )
    _LOGGER.debug("Registered webhook %s", webhook_id)


def async_unregister_webhook(
    hass: HomeAssistant,
    webhook_id: str,
) -> None:
    """Unregister the webhook from Home Assistant."""
    webhook_unregister(hass, webhook_id)
    _LOGGER.debug("Unregistered webhook %s", webhook_id)
