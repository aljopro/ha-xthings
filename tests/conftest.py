"""Fixtures for Xthings integration tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.xthings.const import DOMAIN
from custom_components.xthings.models import (
    XthingsCoordinatorData,
    XthingsDeviceInfo,
    XthingsDeviceState,
)

# ── Pytest-homeassistant-custom-component fixtures ──────────────


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None, None, None]:
    """
    Automatically enable custom integrations in all tests.

    The ``enable_custom_integrations`` fixture comes from
    pytest-homeassistant-custom-component and patches loader.py
    so that custom_components/ is discovered.
    """
    return


# ── Mock data ───────────────────────────────────────────────────

MOCK_DEVICE_ID = "AA:BB:CC:DD:EE:01"
MOCK_DEVICE_ID_2 = "AA:BB:CC:DD:EE:02"

MOCK_TOKEN = {
    "access_token": "mock-access-token",
    "refresh_token": "mock-refresh-token",
    "token_type": "Bearer",
    "expires_in": 3600,
}

MOCK_CONFIG_ENTRY_DATA = {
    "auth_implementation": DOMAIN,
    "token": MOCK_TOKEN,
}

MOCK_DISCOVERY_RESPONSE = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Discovery",
        "messageId": "mock-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": MOCK_DEVICE_ID,
                "name": "Front Door Lock",
                "category": "LOCK",
                "handleType": "utec-lock",
                "deviceInfo": {
                    "manufacturer": "U-tec",
                    "model": "U-Bolt-Pro-WiFi",
                    "hwVersion": "03.40.0023",
                },
                "customData": {"userId": 12345},
            },
            {
                "id": MOCK_DEVICE_ID_2,
                "name": "Back Door Lock",
                "category": "LOCK",
                "handleType": "utec-lock-sensor",
                "deviceInfo": {
                    "manufacturer": "U-tec",
                    "model": "U-Bolt-WiFi",
                    "hwVersion": "02.30.0015",
                },
                "customData": {"userId": 12345},
            },
        ],
    },
}

MOCK_QUERY_LOCKED = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "mock-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": MOCK_DEVICE_ID,
                "states": [
                    {"capability": "st.healthCheck", "name": "status", "value": "online"},
                    {"capability": "st.Lock", "name": "lockState", "value": "locked"},
                    {"capability": "st.BatteryLevel", "name": "level", "value": 85},
                ],
            }
        ],
    },
}

MOCK_QUERY_UNLOCKED = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "mock-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": MOCK_DEVICE_ID,
                "states": [
                    {"capability": "st.healthCheck", "name": "status", "value": "online"},
                    {"capability": "st.Lock", "name": "lockState", "value": "unlocked"},
                    {"capability": "st.BatteryLevel", "name": "level", "value": 72},
                ],
            }
        ],
    },
}

MOCK_COMMAND_DEFERRED = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Command",
        "messageId": "mock-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": MOCK_DEVICE_ID,
                "states": [
                    {"capability": "st.deferredResponse", "name": "seconds", "value": 10},
                ],
            }
        ],
    },
}


# ── Helpers ─────────────────────────────────────────────────────


def build_coordinator_data(
    locked: bool = True,
    online: bool = True,
    battery: int = 85,
) -> XthingsCoordinatorData:
    """Build a mock XthingsCoordinatorData for testing."""
    data = XthingsCoordinatorData()
    data.devices = {
        MOCK_DEVICE_ID: XthingsDeviceInfo(
            device_id=MOCK_DEVICE_ID,
            name="Front Door Lock",
            category="LOCK",
            handle_type="utec-lock",
            manufacturer="U-tec",
            model="U-Bolt-Pro-WiFi",
            hw_version="03.40.0023",
            custom_data={"userId": 12345},
        ),
        MOCK_DEVICE_ID_2: XthingsDeviceInfo(
            device_id=MOCK_DEVICE_ID_2,
            name="Back Door Lock",
            category="LOCK",
            handle_type="utec-lock-sensor",
            manufacturer="U-tec",
            model="U-Bolt-WiFi",
            hw_version="02.30.0015",
            custom_data={"userId": 12345},
        ),
    }
    data.states = {
        MOCK_DEVICE_ID: XthingsDeviceState(
            online=online,
            lock_state="locked" if locked else "unlocked",
            battery_level=battery,
        ),
        MOCK_DEVICE_ID_2: XthingsDeviceState(
            online=True,
            lock_state="locked",
            battery_level=60,
        ),
    }
    return data


@pytest.fixture
def mock_api() -> Generator[AsyncMock, None, None]:
    """Return a mocked XthingsApiClient."""
    with patch(
        "custom_components.xthings.api.XthingsApiClient",
        autospec=True,
    ) as mock_cls:
        api = mock_cls.return_value
        api.async_get_devices = AsyncMock(
            return_value=MOCK_DISCOVERY_RESPONSE["payload"]["devices"],
        )
        api.async_query_device = AsyncMock(
            return_value=MOCK_QUERY_LOCKED["payload"]["devices"][0]["states"],
        )
        api.async_lock = AsyncMock(return_value=10)
        api.async_unlock = AsyncMock(return_value=10)
        api.async_get_user = AsyncMock(
            return_value={"id": "user-123", "firstName": "Test", "lastName": "User"},
        )
        yield api


@pytest.fixture
def mock_coordinator_data() -> XthingsCoordinatorData:
    """Return pre-built coordinator data for entity tests."""
    return build_coordinator_data()
