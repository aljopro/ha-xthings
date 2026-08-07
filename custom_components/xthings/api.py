"""Xthings (U-tec) API client and custom OAuth2 implementation."""

from __future__ import annotations

import logging
import uuid
from typing import Any
from urllib.parse import quote

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import _encode_jwt
from homeassistant.helpers.network import get_url

from .const import (
    API_BASE_URL,
    HTTP_OK,
    NS_CONFIGURE,
    NS_DEVICE,
    NS_USER,
    OAUTH2_AUTHORIZE_URL,
    OAUTH2_TOKEN_URL,
)

_LOGGER = logging.getLogger(__name__)


class XthingsOAuth2Implementation(
    config_entry_oauth2_flow.AbstractOAuth2Implementation
):
    """
    Custom OAuth2 implementation for xthings.

    The xthings OAuth2 flow deviates from the standard:
    - The authorize URL requires client_secret as a query parameter.
    - The token endpoint uses GET (not POST) with query parameters.
    - The callback returns 'authorization_code' instead of 'code'.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        """Initialize the OAuth2 implementation."""
        self.hass = hass
        self._domain = domain
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def name(self) -> str:
        """Name of the implementation."""
        return "Xthings (U-tec)"

    @property
    def domain(self) -> str:
        """Domain that is providing the implementation."""
        return self._domain

    @property
    def extra_authorize_data(self) -> dict:
        """Extra data to include in the authorize request."""
        return {}

    async def async_generate_authorize_url(self, flow_id: str) -> str:
        """
        Generate the authorize URL.

        Xthings requires client_secret in the authorize URL query params.
        The state parameter must be a JWT so HA's OAuth callback view can
        decode it and resume the correct config flow.
        """
        redirect_uri = self.redirect_uri
        state = _encode_jwt(
            self.hass, {"flow_id": flow_id, "redirect_uri": redirect_uri}
        )
        return (
            f"{OAUTH2_AUTHORIZE_URL}"
            f"?response_type=code"
            f"&client_id={self._client_id}"
            f"&client_secret={self._client_secret}"
            f"&scope=openapi"
            f"&redirect_uri={quote(redirect_uri, safe='')}"
            f"&state={state}"
        )

    @property
    def redirect_uri(self) -> str:
        """Return the redirect URI."""
        from .const import CONF_REDIRECT_URI  # noqa: PLC0415

        # Check for override set during the config flow
        override = self.hass.data.get(self._domain, {}).get("redirect_uri_override")
        if override:
            return override

        # Check existing config entries for a stored redirect URI
        for entry in self.hass.config_entries.async_entries(self._domain):
            stored = entry.data.get(CONF_REDIRECT_URI)
            if stored:
                return stored

        # Fall back to auto-detection
        try:
            base_url = get_url(self.hass, allow_internal=True, prefer_external=True)
        except Exception:  # noqa: BLE001
            base_url = get_url(self.hass)
        return f"{base_url}/auth/external/callback"

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        """
        Resolve external data to tokens.

        Called after the user completes the OAuth flow. The external_data
        contains the callback query parameters with a standard 'code' param.
        Also accepts 'authorization_code' as a fallback.
        """
        code = external_data.get("code") or external_data.get("authorization_code")
        if not code:
            raise ValueError("No authorization code received from xthings OAuth")

        return await self._async_token_request(code)

    async def _async_token_request(self, code: str) -> dict:
        """
        Exchange authorization code for tokens.

        Xthings uses GET with query parameters instead of POST with body.
        """
        session = async_get_clientsession(self.hass)

        url = (
            f"{OAUTH2_TOKEN_URL}"
            f"?grant_type=authorization_code"
            f"&client_secret={self._client_secret}"
            f"&client_id={self._client_id}"
            f"&code={code}"
            f"&redirect_uri={quote(self.redirect_uri, safe='')}"
        )

        _LOGGER.debug("Requesting token from xthings OAuth")

        async with session.get(url) as resp:
            if resp.status != HTTP_OK:
                error_text = await resp.text()
                _LOGGER.error(
                    "Token request failed with status %s: %s",
                    resp.status,
                    error_text,
                )
                raise RuntimeError(f"Token request failed: {resp.status} {error_text}")
            token_data = await resp.json()

        # Error responses use a wrapped shape: {"code":200,"data":{"error":"..."}}
        if "data" in token_data and "error" in token_data.get("data", {}):
            error_msg = token_data["data"]["error"]
            raise RuntimeError(f"Token request error: {error_msg}")

        if "access_token" not in token_data:
            raise RuntimeError(f"Invalid token response: {token_data}")

        # Ensure token_type is present
        token_data.setdefault("token_type", "Bearer")

        return token_data

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh the access token.

        This is the abstract method HA's AbstractOAuth2Implementation expects
        overridden. Its public wrapper, async_refresh_token(), forces
        expires_in to int and stamps expires_at from it -- do NOT also
        override async_refresh_token() directly, or that normalization gets
        bypassed and the stored token ends up missing expires_at entirely
        (breaks .valid_token with KeyError('expires_at') on every subsequent
        request, since xthings' refresh response doesn't include expires_at
        itself, only expires_in).
        """
        return await self._do_refresh_token(token)

    def _raise_refresh_error(self, resp: Any, message: str) -> None:
        """Raise a refresh-token error, using HA's reauth-aware exception when available.

        OAuth2TokenRequestReauthError was added to Home Assistant core in
        2026.3 (homeassistant/exceptions.py). This integration declares
        support back to 2024.8.0 (see hacs.json), so we can't reference it
        unconditionally -- doing so previously (as
        config_entry_oauth2_flow.OAuth2AuthorizationError, which never
        existed at all) crashed with AttributeError instead of triggering
        HA's reauth flow. Guard with getattr and fall back to a plain
        RuntimeError on older cores that don't have it yet.
        """
        reauth_error = getattr(
            config_entry_oauth2_flow, "OAuth2TokenRequestReauthError", None
        )
        if reauth_error is not None:
            raise reauth_error(
                request_info=resp.request_info,
                history=resp.history,
                status=resp.status,
                message=message,
                domain=self._domain,
            )
        raise RuntimeError(message)

    async def _do_refresh_token(self, token: dict) -> dict:
        """Perform the actual token refresh."""
        refresh_token = token.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("No refresh token available")

        session = async_get_clientsession(self.hass)

        url = (
            f"{OAUTH2_TOKEN_URL}"
            f"?grant_type=refresh_token"
            f"&client_id={self._client_id}"
            f"&client_secret={self._client_secret}"
            f"&refresh_token={refresh_token}"
        )

        _LOGGER.debug("Refreshing xthings OAuth token")

        async with session.get(url) as resp:
            if resp.status != HTTP_OK:
                error_text = await resp.text()
                _LOGGER.error(
                    "Token refresh failed with status %s: %s",
                    resp.status,
                    error_text,
                )
                self._raise_refresh_error(
                    resp, f"Token refresh failed: {resp.status}"
                )
            token_data = await resp.json()

        # U-tec's refresh endpoint wraps BOTH success and error responses in
        # {"code":200,"data":{...}} -- unlike the initial authorization_code
        # exchange, which returns a flat shape. If left nested, access_token/
        # expires_in silently vanish from the top level: HA persists whatever
        # this function returns verbatim as the new stored token, so a raw
        # wrapped dict corrupts token["access_token"]/["expires_at"] for every
        # subsequent request until the next successful unwrap.
        inner = token_data.get("data")
        if isinstance(inner, dict):
            if "error" in inner:
                error_msg = inner["error"]
                self._raise_refresh_error(resp, f"Token refresh error: {error_msg}")
            if "access_token" in inner:
                token_data = {**{k: v for k, v in token_data.items() if k != "data"}, **inner}

        token_data.setdefault("token_type", "Bearer")

        # Preserve refresh_token if the response doesn't include a new one
        if "refresh_token" not in token_data and refresh_token:
            token_data["refresh_token"] = refresh_token

        return token_data


class XthingsApiClient:
    """
    API client for the xthings (U-tec) cloud API.

    All API calls go to a single POST endpoint. The specific operation
    is determined by the namespace and name fields in the request body.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize the API client."""
        self.hass = hass
        self._session = session
        self._http = async_get_clientsession(hass)

    async def _async_request(
        self,
        namespace: str,
        name: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an API request to xthings.

        All requests go to POST https://api.u-tec.com/action with
        a JSON body containing header (namespace, name, messageId,
        payloadVersion) and payload.
        """
        # Ensure token is valid
        await self._session.async_ensure_token_valid()
        access_token = self._session.token["access_token"]

        message_id = str(uuid.uuid4())

        request_body = {
            "header": {
                "namespace": namespace,
                "name": name,
                "messageId": message_id,
                "payloadVersion": "1",
            },
            "payload": payload or {},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        _LOGGER.debug("API request: %s.%s (messageId=%s)", namespace, name, message_id)

        async with self._http.post(
            API_BASE_URL, json=request_body, headers=headers
        ) as resp:
            if resp.status != HTTP_OK:
                error_text = await resp.text()
                _LOGGER.error(
                    "API request failed with status %s: %s",
                    resp.status,
                    error_text,
                )
                raise XthingsApiError(f"API request failed: {resp.status} {error_text}")

            response_data = await resp.json()

        # Check for API-level errors
        response_payload = response_data.get("payload", {})
        if "error" in response_payload:
            error = response_payload["error"]
            error_code = error.get("code", "UNKNOWN")
            error_message = error.get("message", "Unknown error")

            if error_code == "INVALID_TOKEN":
                raise XthingsAuthError(error_message)

            raise XthingsApiError(f"[{error_code}] {error_message}")

        return response_data

    # ── User endpoints ──────────────────────────────────────────

    async def async_get_user(self) -> dict[str, Any]:
        """Get the authenticated user's information."""
        response = await self._async_request(NS_USER, "Get")
        return response.get("payload", {}).get("user", {})

    # ── Device endpoints ────────────────────────────────────────

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Discover all devices associated with the account."""
        response = await self._async_request(NS_DEVICE, "Discovery")
        return response.get("payload", {}).get("devices", [])

    async def async_query_device(
        self,
        device_id: str,
        custom_data: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query the current state of a device.

        Returns a list of state objects with capability, name, and value.
        """
        device_payload: dict[str, Any] = {"id": device_id}
        if custom_data:
            device_payload["customData"] = custom_data

        response = await self._async_request(
            NS_DEVICE,
            "Query",
            {"devices": [device_payload]},
        )

        devices = response.get("payload", {}).get("devices", [])
        if not devices:
            return []

        return devices[0].get("states", [])

    async def async_lock(
        self,
        device_id: str,
        custom_data: dict[str, Any] | None = None,
    ) -> int | None:
        """
        Send a lock command to a device.

        Returns the deferred response timeout in seconds, or None.
        """
        return await self._async_lock_command(device_id, "lock", custom_data)

    async def async_unlock(
        self,
        device_id: str,
        custom_data: dict[str, Any] | None = None,
    ) -> int | None:
        """
        Send an unlock command to a device.

        Returns the deferred response timeout in seconds, or None.
        """
        return await self._async_lock_command(device_id, "unlock", custom_data)

    async def _async_lock_command(
        self,
        device_id: str,
        command_name: str,
        custom_data: dict[str, Any] | None = None,
    ) -> int | None:
        """
        Send a lock/unlock command.

        Returns the deferred response seconds if the command is async.
        """
        device_payload: dict[str, Any] = {
            "id": device_id,
            "command": {
                "capability": "st.lock",
                "name": command_name,
            },
        }
        if custom_data:
            device_payload["customData"] = custom_data

        response = await self._async_request(
            NS_DEVICE,
            "Command",
            {"devices": [device_payload]},
        )

        # Check for deferred response
        devices = response.get("payload", {}).get("devices", [])
        if devices:
            states = devices[0].get("states", [])
            for state in states:
                if state.get("capability", "").lower() == "st.deferredresponse":
                    return state.get("value")

        return None

    # ── Notification endpoints ──────────────────────────────────

    async def async_register_notification_url(
        self,
        url: str,
        access_token: str | None = None,
    ) -> dict[str, Any]:
        """Register a webhook URL for push notifications."""
        if access_token is None:
            await self._session.async_ensure_token_valid()
            access_token = self._session.token["access_token"]

        response = await self._async_request(
            NS_CONFIGURE,
            "Set",
            {
                "configure": {
                    "notification": {
                        "access_token": access_token,
                        "url": url,
                    }
                }
            },
        )
        _LOGGER.info("Registered notification URL: %s", url)
        return response


class XthingsApiError(Exception):
    """General API error from xthings."""


class XthingsAuthError(XthingsApiError):
    """Authentication error from xthings (e.g., INVALID_TOKEN)."""
