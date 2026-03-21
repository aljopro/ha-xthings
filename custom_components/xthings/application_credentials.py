"""Application credentials for the Xthings (U-tec) integration."""

from __future__ import annotations

from homeassistant.components.application_credentials import (
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .api import XthingsOAuth2Implementation
from .const import DOMAIN, OAUTH2_AUTHORIZE_URL, OAUTH2_TOKEN_URL


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return the authorization server for xthings OAuth2."""
    return AuthorizationServer(
        authorize_url=OAUTH2_AUTHORIZE_URL,
        token_url=OAUTH2_TOKEN_URL,
    )


async def async_get_auth_implementation(
    hass: HomeAssistant,
    auth_domain: str,
    credential: ClientCredential,
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return a custom auth implementation.

    Xthings uses a non-standard OAuth2 flow (GET for token endpoint,
    client_secret in authorize URL, 'authorization_code' callback param),
    so we need a custom implementation instead of the default.
    """
    return XthingsOAuth2Implementation(
        hass,
        DOMAIN,
        client_id=credential.client_id,
        client_secret=credential.client_secret,
    )
