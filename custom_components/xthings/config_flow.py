"""Config flow for the Xthings (U-tec) integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class XthingsOAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler,
    domain=DOMAIN,
):
    """Handle the OAuth2 config flow for Xthings (U-tec)."""

    DOMAIN = DOMAIN

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
                self.hass.config_entries.async_update_entry(
                    reauth_entry, data=data
                )
                await self.hass.config_entries.async_reload(entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_create_entry(title="Xthings (U-tec)", data=data)

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> FlowResult:
        """Handle re-authentication when the token has expired."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm re-authentication."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")

        return await self.async_step_user()
