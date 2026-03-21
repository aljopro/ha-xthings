#!/usr/bin/env python3
"""
Standalone test script for the Xthings (U-tec) API.

This script tests the OAuth2 flow and API calls directly against
the xthings cloud service, without requiring Home Assistant.

Usage:
    python3 tests/test_api_live.py

It will:
1. Start a local HTTP server on port 9501 for the OAuth2 callback
2. Open your browser to the xthings authorize URL
3. Catch the authorization code from the callback
4. Exchange the code for access tokens
5. Test all API endpoints (discovery, query, lock, unlock)
6. Save tokens to tests/.tokens.json for reuse

Requirements:
    pip3 install aiohttp

Environment:
    Set these in a .env file in the project root, or export them:
    - XTHINGS_CLIENT_ID
    - XTHINGS_CLIENT_SECRET
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
import webbrowser
from pathlib import Path

import aiohttp
from aiohttp import web

# ── Configuration ───────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
TOKEN_FILE = Path(__file__).parent / ".tokens.json"

OAUTH2_AUTHORIZE_URL = "https://oauth.u-tec.com/authorize"
OAUTH2_TOKEN_URL = "https://oauth.u-tec.com/token"
API_BASE_URL = "https://api.u-tec.com/action"
REDIRECT_URI = "http://localhost:9501"
CALLBACK_PORT = 9501


def load_env() -> dict[str, str]:
    """Load environment variables from .env file."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_credentials() -> tuple[str, str]:
    """Get client_id and client_secret from env or .env file."""
    env = load_env()
    client_id = os.environ.get("XTHINGS_CLIENT_ID") or env.get("XTHINGS_CLIENT_ID")
    client_secret = os.environ.get("XTHINGS_CLIENT_SECRET") or env.get("XTHINGS_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: XTHINGS_CLIENT_ID and XTHINGS_CLIENT_SECRET must be set.")
        print("Create a .env file in the project root with:")
        print("  XTHINGS_CLIENT_ID=your_client_id")
        print("  XTHINGS_CLIENT_SECRET=your_client_secret")
        sys.exit(1)

    return client_id, client_secret


# ── OAuth2 Flow ─────────────────────────────────────────────────

class OAuth2CallbackServer:
    """Temporary HTTP server to catch the OAuth2 callback."""

    def __init__(self):
        self.authorization_code: str | None = None
        self._event = asyncio.Event()

    async def handle_callback(self, request: web.Request) -> web.Response:
        """Handle the OAuth2 callback redirect."""
        # Xthings uses 'authorization_code' instead of 'code'
        self.authorization_code = (
            request.query.get("code")
            or request.query.get("authorization_code")
        )
        state = request.query.get("state", "")

        if self.authorization_code:
            self._event.set()
            return web.Response(
                content_type="text/html",
                text=(
                    "<html><body style='font-family:system-ui;text-align:center;padding:40px'>"
                    "<h1>✅ Authorization Successful!</h1>"
                    f"<p>Code received: <code>{self.authorization_code[:16]}...</code></p>"
                    f"<p>State: <code>{state}</code></p>"
                    "<p>You can close this window.</p>"
                    "</body></html>"
                ),
            )
        error = request.query.get("error", "unknown")
        error_desc = request.query.get("error_description", "No description")
        self._event.set()
        return web.Response(
            content_type="text/html",
            text=(
                "<html><body style='font-family:system-ui;text-align:center;padding:40px'>"
                f"<h1>❌ Authorization Failed</h1>"
                f"<p>Error: {error}</p>"
                f"<p>{error_desc}</p>"
                "</body></html>"
            ),
        )

    async def wait_for_callback(self, timeout: float = 120) -> str | None:
        """Wait for the OAuth2 callback."""
        try:
            await asyncio.wait_for(self._event.wait(), timeout=timeout)
        except TimeoutError:
            return None
        return self.authorization_code

    async def start(self) -> web.AppRunner:
        """Start the callback server."""
        app = web.Application()
        app.router.add_get("/", self.handle_callback)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", CALLBACK_PORT)
        await site.start()
        return runner


async def get_tokens_oauth(client_id: str, client_secret: str) -> dict:
    """Run the full OAuth2 flow to get tokens."""
    callback_server = OAuth2CallbackServer()
    runner = await callback_server.start()

    state = str(uuid.uuid4())
    auth_url = (
        f"{OAUTH2_AUTHORIZE_URL}"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&client_secret={client_secret}"
        f"&scope=openapi"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )

    print("\n🔐 Opening browser for authorization...")
    print(f"   URL: {auth_url[:80]}...")
    webbrowser.open(auth_url)
    print(f"   Waiting for callback on {REDIRECT_URI} ...")

    code = await callback_server.wait_for_callback(timeout=120)
    await runner.cleanup()

    if not code:
        print("❌ Timed out waiting for authorization callback.")
        sys.exit(1)

    print(f"✅ Got authorization code: {code[:16]}...")

    # Exchange code for tokens
    token_url = (
        f"{OAUTH2_TOKEN_URL}"
        f"?grant_type=authorization_code"
        f"&client_id={client_id}"
        f"&code={code}"
    )

    print("\n🔑 Exchanging code for tokens...")
    async with aiohttp.ClientSession() as session, session.get(token_url) as resp:
        print(f"   Token response status: {resp.status}")
        body = await resp.text()
        print(f"   Token response body: {body[:200]}")

        if resp.status != 200:
            print("❌ Token exchange failed!")
            sys.exit(1)

        tokens = json.loads(body)

    tokens.setdefault("token_type", "Bearer")
    print(f"✅ Got access token: {tokens.get('access_token', 'MISSING')[:16]}...")
    print(f"   Has refresh_token: {'refresh_token' in tokens}")
    if "expires_in" in tokens:
        print(f"   Expires in: {tokens['expires_in']} seconds")

    # Save tokens
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
    print(f"   Saved tokens to {TOKEN_FILE}")

    return tokens


async def load_or_refresh_tokens(client_id: str) -> dict | None:
    """Load saved tokens and refresh if needed."""
    if not TOKEN_FILE.exists():
        return None

    tokens = json.loads(TOKEN_FILE.read_text())
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    if not access_token:
        return None

    print(f"📂 Loaded saved tokens: {access_token[:16]}...")

    # Try a test request to see if token is still valid
    async with aiohttp.ClientSession() as session:
        test_body = {
            "header": {
                "namespace": "Uhome.User",
                "name": "Get",
                "messageId": str(uuid.uuid4()),
                "payloadVersion": "1",
            },
            "payload": {},
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        async with session.post(API_BASE_URL, json=test_body, headers=headers) as resp:
            data = await resp.json()
            if "error" not in data.get("payload", {}):
                print("✅ Saved tokens are still valid!")
                return tokens
            print(f"⚠️  Token expired: {data['payload']['error']}")

    # Try refresh
    if refresh_token:
        print("🔄 Attempting token refresh...")
        refresh_url = (
            f"{OAUTH2_TOKEN_URL}"
            f"?grant_type=refresh_token"
            f"&client_id={client_id}"
            f"&refresh_token={refresh_token}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(refresh_url) as resp:
                if resp.status == 200:
                    new_tokens = await resp.json()
                    new_tokens.setdefault("token_type", "Bearer")
                    if "refresh_token" not in new_tokens:
                        new_tokens["refresh_token"] = refresh_token
                    TOKEN_FILE.write_text(json.dumps(new_tokens, indent=2))
                    print(f"✅ Token refreshed: {new_tokens.get('access_token', '')[:16]}...")
                    return new_tokens
                print(f"❌ Refresh failed: {resp.status} {await resp.text()}")

    return None


# ── API Test Functions ──────────────────────────────────────────

async def api_request(
    session: aiohttp.ClientSession,
    access_token: str,
    namespace: str,
    name: str,
    payload: dict | None = None,
) -> dict:
    """Make an API request to xthings."""
    message_id = str(uuid.uuid4())
    body = {
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

    async with session.post(API_BASE_URL, json=body, headers=headers) as resp:
        response = await resp.json()
        return response


async def test_get_user(session: aiohttp.ClientSession, token: str) -> dict:
    """Test: Get user information."""
    print("\n── Test: Get User Info ──")
    response = await api_request(session, token, "Uhome.User", "Get")
    payload = response.get("payload", {})

    if "error" in payload:
        print(f"   ❌ Error: {payload['error']}")
        return {}

    user = payload.get("user", {})
    print(f"   User ID: {user.get('id', 'N/A')}")
    print(f"   Name: {user.get('FirstName', '')} {user.get('lastName', '')}")
    return user


async def test_discover_devices(session: aiohttp.ClientSession, token: str) -> list:
    """Test: Discover devices."""
    print("\n── Test: Discover Devices ──")
    response = await api_request(session, token, "Uhome.Device", "Discovery")
    payload = response.get("payload", {})

    if "error" in payload:
        print(f"   ❌ Error: {payload['error']}")
        return []

    devices = payload.get("devices", [])
    print(f"   Found {len(devices)} device(s):")
    for i, device in enumerate(devices, 1):
        info = device.get("deviceInfo", {})
        print(f"\n   Device {i}:")
        print(f"     ID:       {device.get('id', 'N/A')}")
        print(f"     Name:     {device.get('name', 'N/A')}")
        print(f"     Category: {device.get('category', 'N/A')}")
        print(f"     Handler:  {device.get('handleType', 'N/A')}")
        print(f"     Model:    {info.get('model', 'N/A')}")
        print(f"     Mfr:      {info.get('manufacturer', 'N/A')}")
        print(f"     FW:       {info.get('hwVersion', 'N/A')}")
        if device.get("customData"):
            print(f"     Custom:   {json.dumps(device['customData'])}")

    return devices


async def test_query_device(
    session: aiohttp.ClientSession,
    token: str,
    device_id: str,
    custom_data: dict | None = None,
) -> list:
    """Test: Query device status."""
    print(f"\n── Test: Query Device {device_id[:20]}... ──")

    device_payload: dict = {"id": device_id}
    if custom_data:
        device_payload["customData"] = custom_data

    response = await api_request(
        session, token, "Uhome.Device", "Query",
        {"devices": [device_payload]},
    )
    payload = response.get("payload", {})

    if "error" in payload:
        print(f"   ❌ Error: {payload['error']}")
        return []

    devices = payload.get("devices", [])
    if not devices:
        print("   No device data returned")
        return []

    states = devices[0].get("states", [])
    print(f"   Got {len(states)} state(s):")
    for state in states:
        cap = state.get("capability", "?")
        name = state.get("name", "?")
        value = state.get("value", "?")
        print(f"     {cap}.{name} = {value}")

    return states


async def test_lock_command(
    session: aiohttp.ClientSession,
    token: str,
    device_id: str,
    command: str,
    custom_data: dict | None = None,
) -> dict:
    """Test: Lock/unlock command."""
    print(f"\n── Test: {command.upper()} {device_id[:20]}... ──")

    device_payload: dict = {
        "id": device_id,
        "command": {
            "capability": "st.lock",
            "name": command,
        },
    }
    if custom_data:
        device_payload["customData"] = custom_data

    response = await api_request(
        session, token, "Uhome.Device", "Command",
        {"devices": [device_payload]},
    )
    payload = response.get("payload", {})

    if "error" in payload:
        print(f"   ❌ Error: {payload['error']}")
        return {}

    devices = payload.get("devices", [])
    if devices:
        states = devices[0].get("states", [])
        for state in states:
            cap = state.get("capability", "?")
            name = state.get("name", "?")
            value = state.get("value", "?")
            print(f"   Response: {cap}.{name} = {value}")
            if cap == "st.deferredResponse":
                print(f"   ⏳ Deferred response: poll again in {value} seconds")

    return response


# ── Main ────────────────────────────────────────────────────────

async def main():
    """Run all tests."""
    print("=" * 60)
    print("Xthings (U-tec) API Test Suite")
    print("=" * 60)

    client_id, client_secret = get_credentials()
    print(f"\n📋 Client ID: {client_id[:16]}...")

    # Try to use saved tokens first
    tokens = await load_or_refresh_tokens(client_id)
    if not tokens:
        tokens = await get_tokens_oauth(client_id, client_secret)

    access_token = tokens["access_token"]

    async with aiohttp.ClientSession() as session:
        # Test 1: Get user info
        user = await test_get_user(session, access_token)

        # Test 2: Discover devices
        devices = await test_discover_devices(session, access_token)

        if not devices:
            print("\n⚠️  No devices found. Make sure your locks are set up in the Xthings app.")
            return

        # Test 3: Query each lock device
        lock_devices = []
        for device in devices:
            category = device.get("category", "").upper()
            handle_type = device.get("handleType", "")
            if category == "LOCK" or handle_type in ("utec-lock", "utec-lock-sensor"):
                lock_devices.append(device)
                await test_query_device(
                    session, access_token,
                    device["id"],
                    device.get("customData"),
                )

        if not lock_devices:
            print("\n⚠️  No lock devices found among your devices.")
            return

        # Test 4: Lock/unlock (interactive)
        print("\n" + "=" * 60)
        print("Lock Control Tests")
        print("=" * 60)

        test_device = lock_devices[0]
        device_id = test_device["id"]
        custom_data = test_device.get("customData")
        print(f"\nTest device: {test_device.get('name', 'Unknown')} ({device_id[:20]}...)")

        while True:
            print("\nOptions:")
            print("  [l] Lock")
            print("  [u] Unlock")
            print("  [q] Query status")
            print("  [x] Exit")
            choice = input("\nChoice: ").strip().lower()

            if choice == "l":
                await test_lock_command(session, access_token, device_id, "lock", custom_data)
                print("   Waiting 12s for deferred response...")
                await asyncio.sleep(12)
                await test_query_device(session, access_token, device_id, custom_data)
            elif choice == "u":
                await test_lock_command(session, access_token, device_id, "unlock", custom_data)
                print("   Waiting 12s for deferred response...")
                await asyncio.sleep(12)
                await test_query_device(session, access_token, device_id, custom_data)
            elif choice == "q":
                await test_query_device(session, access_token, device_id, custom_data)
            elif choice == "x":
                break
            else:
                print("   Invalid choice")

    print("\n✅ Tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
