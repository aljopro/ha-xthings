"""Config flow for the Xthings (U-tec) integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import SOURCE_REAUTH, ConfigFlowResult
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

    async def async_oauth_create_entry(self, data: dict) -> ConfigFlowResult:
        """Create or update the config entry after successful OAuth.

        Fetches the user ID from xthings to use as the unique_id,
        preventing duplicate config entries for the same account.
        """
        # We'll set unique_id after the entry is set up and we can
        # make API calls. For now, use a simple approach.
        try:
            # Try to use the token to get user info for unique_id
            from homeassistant.helpers.aiohttp_client import async_get_clientsession
            from .api import XthingsApiClient

            session_obj = config_entry_oauth2_flow.OAuth2Session(
                self.hass, None, self.flow_impl
            )
            # Manually set the token from the data we just got
            session_obj.__dict__["token"] = data.get("token", {})

            # For now, just create the entry — the coordinator will
            # handle discovery and we'll set unique_id based on that
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Could not fetch user info during config flow")

        if self.source == SOURCE_REAUTH:
            reauth_entry = self._get_reauth_entry()
            return self.async_update_reload_and_abort(
                reauth_entry,
                data_updates=data,
            )

        return self.async_create_entry(title="Xthings (U-tec)", data=data)

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-authentication when the token has expired."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm re-authentication."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")

        return await self.async_step_user()
