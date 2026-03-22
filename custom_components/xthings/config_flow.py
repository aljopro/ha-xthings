"""Config flow for the Xthings (U-tec) integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    SOURCE_REAUTH,
    ConfigEntry,
    OptionsFlowWithConfigEntry,
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import CONF_USE_WEBHOOK, CONF_WEBHOOK_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class XthingsOAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler,
    domain=DOMAIN,
):
    """Handle the OAuth2 config flow for Xthings (U-tec)."""

    DOMAIN = DOMAIN

    @staticmethod
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> XthingsOptionsFlowHandler:
        """Return the options flow handler."""
        return XthingsOptionsFlowHandler(config_entry)

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data to include in the authorize request."""
        return {}

    async def async_oauth_create_entry(self, data: dict) -> FlowResult:
        """Create or update the config entry after successful OAuth."""
        if self.source == SOURCE_REAUTH:
            entry_id = self.context.get("entry_id", "")
            reauth_entry = self.hass.config_entries.async_get_entry(entry_id)
            if reauth_entry is not None:
                self.hass.config_entries.async_update_entry(reauth_entry, data=data)
                await self.hass.config_entries.async_reload(entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_create_entry(title="Xthings (U-tec)", data=data)

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle re-authentication when the token has expired."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm re-authentication."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")

        return await self.async_step_user()


class XthingsOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle Xthings options (e.g. webhook toggle)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Strip empty webhook_url so it doesn't persist as blank
            if not user_input.get(CONF_WEBHOOK_URL):
                user_input.pop(CONF_WEBHOOK_URL, None)
            return self.async_create_entry(title="", data=user_input)

        cloud_available = "cloud" in self.hass.config.components

        current_use_webhook = self.config_entry.options.get(CONF_USE_WEBHOOK, False)
        current_webhook_url = self.config_entry.options.get(CONF_WEBHOOK_URL, "")

        schema = vol.Schema(
            {
                vol.Optional(CONF_USE_WEBHOOK, default=current_use_webhook): bool,
                vol.Optional(CONF_WEBHOOK_URL, default=current_webhook_url): str,
            }
        )

        description_placeholders = {
            "cloud_status": "connected" if cloud_available else "not connected",
        }

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders=description_placeholders,
        )
