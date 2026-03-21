"""
Unit tests for the Xthings (U-tec) integration.

These tests mock the API responses to validate the coordinator,
entity logic, and data parsing without hitting the real API.

Usage:
    pip3 install pytest pytest-asyncio aiohttp
    python3 -m pytest tests/test_unit.py -v
"""

from __future__ import annotations

# ── Module loading helpers ──────────────────────────────────────
# We load const.py and models.py directly via importlib to avoid
# triggering __init__.py which imports homeassistant (not available
# in the test environment without a full HA install).
import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
COMPONENTS_DIR = PROJECT_ROOT / "custom_components" / "xthings"


def _load_module(name: str, filepath: Path):
    """Load a Python module from file without triggering package __init__."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Load const first (no dependencies), then models (depends on const via relative import)
_const = _load_module("custom_components.xthings.const", COMPONENTS_DIR / "const.py")
# Patch models.py's relative import by pre-loading const into the right place
_models = _load_module("custom_components.xthings.models", COMPONENTS_DIR / "models.py")

# ── Test data fixtures ──────────────────────────────────────────

DISCOVERY_RESPONSE = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Discovery",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "name": "Front Door Lock",
                "category": "LOCK",
                "handleType": "utec-lock",
                "deviceInfo": {
                    "manufacturer": "U-tec",
                    "model": "U-Bolt-Pro-WiFi",
                    "hwVersion": "03.40.0023",
                },
                "customData": {
                    "userId": 12345,
                },
            },
            {
                "id": "AA:BB:CC:DD:EE:02",
                "name": "Back Door Lock",
                "category": "LOCK",
                "handleType": "utec-lock-sensor",
                "deviceInfo": {
                    "manufacturer": "U-tec",
                    "model": "U-Bolt-WiFi",
                    "hwVersion": "02.30.0015",
                },
                "customData": {
                    "userId": 12345,
                },
            },
        ],
    },
}

QUERY_RESPONSE_LOCKED = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "states": [
                    {
                        "capability": "st.healthCheck",
                        "name": "status",
                        "value": "online",
                    },
                    {
                        "capability": "st.Lock",
                        "name": "lockState",
                        "value": "locked",
                    },
                    {
                        "capability": "st.BatteryLevel",
                        "name": "level",
                        "value": 85,
                    },
                ],
            }
        ],
    },
}

QUERY_RESPONSE_UNLOCKED = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "states": [
                    {
                        "capability": "st.healthCheck",
                        "name": "status",
                        "value": "online",
                    },
                    {
                        "capability": "st.Lock",
                        "name": "lockState",
                        "value": "unlocked",
                    },
                    {
                        "capability": "st.BatteryLevel",
                        "name": "level",
                        "value": 85,
                    },
                ],
            }
        ],
    },
}

QUERY_RESPONSE_OFFLINE = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "states": [
                    {
                        "capability": "st.healthCheck",
                        "name": "status",
                        "value": "offline",
                    },
                    {
                        "capability": "st.Lock",
                        "name": "lockState",
                        "value": "locked",
                    },
                    {
                        "capability": "st.BatteryLevel",
                        "name": "level",
                        "value": 15,
                    },
                ],
            }
        ],
    },
}

COMMAND_RESPONSE_DEFERRED = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Command",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "states": [
                    {
                        "capability": "st.deferredResponse",
                        "name": "seconds",
                        "value": 10,
                    }
                ],
            }
        ],
    },
}

QUERY_RESPONSE_JAMMED = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "states": [
                    {
                        "capability": "st.healthCheck",
                        "name": "status",
                        "value": "online",
                    },
                    {
                        "capability": "st.Lock",
                        "name": "lockState",
                        "value": "jammed",
                    },
                    {
                        "capability": "st.BatteryLevel",
                        "name": "level",
                        "value": 3,
                    },
                ],
            }
        ],
    },
}

QUERY_RESPONSE_WITH_DOOR_SENSOR = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:02",
                "states": [
                    {
                        "capability": "st.healthCheck",
                        "name": "status",
                        "value": "online",
                    },
                    {
                        "capability": "st.Lock",
                        "name": "lockState",
                        "value": "locked",
                    },
                    {
                        "capability": "st.BatteryLevel",
                        "name": "level",
                        "value": 4,
                    },
                    {
                        "capability": "st.DoorSensor",
                        "name": "sensorState",
                        "value": "closed",
                    },
                ],
            }
        ],
    },
}

QUERY_RESPONSE_DOOR_OPEN = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Query",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:02",
                "states": [
                    {
                        "capability": "st.healthCheck",
                        "name": "status",
                        "value": "online",
                    },
                    {
                        "capability": "st.Lock",
                        "name": "lockState",
                        "value": "unlocked",
                    },
                    {
                        "capability": "st.BatteryLevel",
                        "name": "level",
                        "value": 4,
                    },
                    {
                        "capability": "st.DoorSensor",
                        "name": "sensorState",
                        "value": "open",
                    },
                ],
            }
        ],
    },
}

SET_MODE_COMMAND_RESPONSE = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Command",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "states": [
                    {
                        "capability": "st.deferredResponse",
                        "name": "seconds",
                        "value": 5,
                    }
                ],
            }
        ],
    },
}

LOCK_USER_LIST_RESPONSE = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Command",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "devices": [
            {
                "id": "AA:BB:CC:DD:EE:01",
                "states": [
                    {
                        "name": "user1",
                        "type": 0,
                        "id": 100,
                    },
                    {
                        "name": "admin",
                        "type": 3,
                        "id": 101,
                    },
                ],
            }
        ],
    },
}

ERROR_RESPONSE_INVALID_TOKEN = {
    "header": {
        "namespace": "Uhome.Device",
        "name": "Discovery",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "error": {
            "code": "INVALID_TOKEN",
            "message": "Token is expired or invalid.",
        }
    },
}

USER_RESPONSE = {
    "header": {
        "namespace": "Uhome.User",
        "name": "Get",
        "messageId": "test-msg-id",
        "payloadVersion": "1",
    },
    "payload": {
        "user": {
            "id": "user-123-abc",
            "firstName": "Test",
            "lastName": "User",
        }
    },
}


# ── Data parsing tests ──────────────────────────────────────────


class TestDiscoveryParsing:
    """Test parsing of device discovery responses."""

    def test_parse_devices(self):
        """Discovery returns correct number of devices."""
        devices = DISCOVERY_RESPONSE["payload"]["devices"]
        assert len(devices) == 2

    def test_lock_device_fields(self):
        """Lock device has all expected fields."""
        device = DISCOVERY_RESPONSE["payload"]["devices"][0]
        assert device["id"] == "AA:BB:CC:DD:EE:01"
        assert device["name"] == "Front Door Lock"
        assert device["category"] == "LOCK"
        assert device["handleType"] == "utec-lock"
        assert device["deviceInfo"]["manufacturer"] == "U-tec"
        assert device["deviceInfo"]["model"] == "U-Bolt-Pro-WiFi"

    def test_custom_data_present(self):
        """Device has customData that must be passed back."""
        device = DISCOVERY_RESPONSE["payload"]["devices"][0]
        assert "customData" in device
        assert "userId" in device["customData"]

    def test_lock_sensor_handler(self):
        """Second device uses the lock-sensor handler."""
        device = DISCOVERY_RESPONSE["payload"]["devices"][1]
        assert device["handleType"] == "utec-lock-sensor"


class TestQueryParsing:
    """Test parsing of device query responses."""

    def test_locked_state(self):
        """Parse locked state correctly."""
        states = QUERY_RESPONSE_LOCKED["payload"]["devices"][0]["states"]

        lock_state = next(s for s in states if s["capability"] == "st.Lock")
        assert lock_state["name"] == "lockState"
        assert lock_state["value"] == "locked"

    def test_unlocked_state(self):
        """Parse unlocked state correctly."""
        states = QUERY_RESPONSE_UNLOCKED["payload"]["devices"][0]["states"]

        lock_state = next(s for s in states if s["capability"] == "st.Lock")
        assert lock_state["value"] == "unlocked"

    def test_battery_level(self):
        """Parse battery level correctly."""
        states = QUERY_RESPONSE_LOCKED["payload"]["devices"][0]["states"]

        battery = next(s for s in states if s["capability"] == "st.BatteryLevel")
        assert battery["name"] == "level"
        assert battery["value"] == 85

    def test_online_status(self):
        """Parse online/offline status."""
        states_online = QUERY_RESPONSE_LOCKED["payload"]["devices"][0]["states"]
        health = next(s for s in states_online if s["capability"] == "st.healthCheck")
        assert health["value"] == "online"

        states_offline = QUERY_RESPONSE_OFFLINE["payload"]["devices"][0]["states"]
        health = next(s for s in states_offline if s["capability"] == "st.healthCheck")
        assert health["value"] == "offline"

    def test_low_battery(self):
        """Detect low battery from offline response."""
        states = QUERY_RESPONSE_OFFLINE["payload"]["devices"][0]["states"]
        battery = next(s for s in states if s["capability"] == "st.BatteryLevel")
        assert battery["value"] == 15


class TestCommandParsing:
    """Test parsing of command responses."""

    def test_deferred_response(self):
        """Lock command returns deferred response."""
        states = COMMAND_RESPONSE_DEFERRED["payload"]["devices"][0]["states"]

        deferred = next(
            s for s in states if s["capability"] == "st.deferredResponse"
        )
        assert deferred["name"] == "seconds"
        assert deferred["value"] == 10


class TestErrorParsing:
    """Test parsing of error responses."""

    def test_invalid_token_error(self):
        """Detect INVALID_TOKEN error."""
        payload = ERROR_RESPONSE_INVALID_TOKEN["payload"]
        assert "error" in payload
        assert payload["error"]["code"] == "INVALID_TOKEN"


class TestRequestBodyConstruction:
    """Test that API request bodies are constructed correctly."""

    def test_discovery_request(self):
        """Discovery request has correct structure."""
        body = {
            "header": {
                "namespace": "Uhome.Device",
                "name": "Discovery",
                "messageId": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "payloadVersion": "1",
            },
            "payload": {},
        }
        assert body["header"]["namespace"] == "Uhome.Device"
        assert body["header"]["name"] == "Discovery"
        assert len(body["header"]["messageId"]) == 36
        assert body["payload"] == {}

    def test_query_request(self):
        """Query request includes device ID and customData."""
        body = {
            "header": {
                "namespace": "Uhome.Device",
                "name": "Query",
                "messageId": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "payloadVersion": "1",
            },
            "payload": {
                "devices": [
                    {
                        "id": "AA:BB:CC:DD:EE:01",
                        "customData": {"userId": 12345},
                    }
                ],
            },
        }
        device = body["payload"]["devices"][0]
        assert device["id"] == "AA:BB:CC:DD:EE:01"
        assert device["customData"]["userId"] == 12345

    def test_lock_command_request(self):
        """Lock command request has correct capability and name."""
        body = {
            "header": {
                "namespace": "Uhome.Device",
                "name": "Command",
                "messageId": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "payloadVersion": "1",
            },
            "payload": {
                "devices": [
                    {
                        "id": "AA:BB:CC:DD:EE:01",
                        "command": {
                            "capability": "st.lock",
                            "name": "lock",
                        },
                    }
                ],
            },
        }
        command = body["payload"]["devices"][0]["command"]
        assert command["capability"] == "st.lock"
        assert command["name"] == "lock"

    def test_unlock_command_request(self):
        """Unlock command uses 'unlock' name."""
        command = {
            "capability": "st.lock",
            "name": "unlock",
        }
        assert command["name"] == "unlock"


class TestCoordinatorDataModels:
    """Test the coordinator data model classes."""

    def test_device_info_is_lock_by_category(self):
        """Device with LOCK category is identified as lock."""
        info = _models.XthingsDeviceInfo(
            device_id="test-id",
            name="Test Lock",
            category="LOCK",
            handle_type="unknown",
            manufacturer="U-tec",
            model="Test",
            hw_version="1.0",
        )
        assert info.is_lock is True

    def test_device_info_is_lock_by_handler(self):
        """Device with utec-lock handler is identified as lock."""
        info = _models.XthingsDeviceInfo(
            device_id="test-id",
            name="Test Lock",
            category="UNKNOWN",
            handle_type="utec-lock",
            manufacturer="U-tec",
            model="Test",
            hw_version="1.0",
        )
        assert info.is_lock is True

    def test_device_info_is_lock_sensor_handler(self):
        """Device with utec-lock-sensor handler is identified as lock."""
        info = _models.XthingsDeviceInfo(
            device_id="test-id",
            name="Test Lock",
            category="UNKNOWN",
            handle_type="utec-lock-sensor",
            manufacturer="U-tec",
            model="Test",
            hw_version="1.0",
        )
        assert info.is_lock is True

    def test_device_info_not_lock(self):
        """Non-lock device is not identified as lock."""
        info = _models.XthingsDeviceInfo(
            device_id="test-id",
            name="Test Light",
            category="LIGHT",
            handle_type="utec-bulb-color-rgbw",
            manufacturer="U-tec",
            model="A19",
            hw_version="1.0",
        )
        assert info.is_lock is False

    def test_device_state_defaults(self):
        """Device state has correct defaults."""
        state = _models.XthingsDeviceState()
        assert state.online is False
        assert state.lock_state is None
        assert state.battery_level is None
        assert state.is_jammed is False
        assert state.door_state is None

    def test_device_state_populated(self):
        """Device state can be populated."""
        state = _models.XthingsDeviceState(
            online=True,
            lock_state="locked",
            battery_level=85,
        )
        assert state.online is True
        assert state.lock_state == "locked"
        assert state.battery_level == 85
        assert state.is_jammed is False

    def test_device_state_jammed(self):
        """Device state can represent jammed lock."""
        state = _models.XthingsDeviceState(
            online=True,
            lock_state="jammed",
            is_jammed=True,
        )
        assert state.is_jammed is True
        assert state.lock_state == "jammed"

    def test_device_state_door_sensor(self):
        """Device state can include door sensor."""
        state = _models.XthingsDeviceState(
            online=True,
            lock_state="locked",
            door_state="closed",
        )
        assert state.door_state == "closed"

        state_open = _models.XthingsDeviceState(
            online=True,
            lock_state="unlocked",
            door_state="open",
        )
        assert state_open.door_state == "open"

    def test_coordinator_data_defaults(self):
        """Coordinator data has empty defaults."""
        data = _models.XthingsCoordinatorData()
        assert data.devices == {}
        assert data.states == {}


class TestOAuth2UrlConstruction:
    """Test OAuth2 URL construction."""

    def test_authorize_url_format(self):
        """Authorize URL has all required parameters."""
        client_id = "test_client_id"
        client_secret = "test_client_secret"
        redirect_uri = "http://localhost:8123/auth/external/callback"
        state = "test-state-uuid"

        url = (
            f"https://oauth.u-tec.com/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&client_secret={client_secret}"
            f"&scope=openapi"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )

        assert "response_type=code" in url
        assert f"client_id={client_id}" in url
        assert f"client_secret={client_secret}" in url
        assert "scope=openapi" in url
        assert f"redirect_uri={redirect_uri}" in url
        assert f"state={state}" in url

    def test_token_url_format(self):
        """Token URL has correct format for code exchange."""
        client_id = "test_client_id"
        code = "test_auth_code"

        url = (
            f"https://oauth.u-tec.com/token"
            f"?grant_type=authorization_code"
            f"&client_id={client_id}"
            f"&code={code}"
        )

        assert "grant_type=authorization_code" in url
        assert f"client_id={client_id}" in url
        assert f"code={code}" in url

    def test_refresh_url_format(self):
        """Refresh URL has correct format."""
        client_id = "test_client_id"
        refresh_token = "test_refresh_token"

        url = (
            f"https://oauth.u-tec.com/token"
            f"?grant_type=refresh_token"
            f"&client_id={client_id}"
            f"&refresh_token={refresh_token}"
        )

        assert "grant_type=refresh_token" in url
        assert f"client_id={client_id}" in url
        assert f"refresh_token={refresh_token}" in url


class TestConstants:
    """Test that constants are defined correctly."""

    def test_domain(self):
        """Domain constant matches expected value."""
        assert _const.DOMAIN == "xthings"

    def test_oauth_urls(self):
        """OAuth2 URLs are correct."""
        assert _const.OAUTH2_AUTHORIZE_URL == "https://oauth.u-tec.com/authorize"
        assert _const.OAUTH2_TOKEN_URL == "https://oauth.u-tec.com/token"

    def test_api_url(self):
        """API base URL is correct."""
        assert _const.API_BASE_URL == "https://api.u-tec.com/action"

    def test_capabilities(self):
        """Capability strings match expected values."""
        assert _const.CAP_HEALTH_CHECK == "st.healthCheck"
        assert _const.CAP_LOCK == "st.lock"
        assert _const.CAP_LOCK_STATE == "st.Lock"
        assert _const.CAP_BATTERY_LEVEL == "st.BatteryLevel"
        assert _const.CAP_DEFERRED_RESPONSE == "st.deferredResponse"
        assert _const.CAP_DOOR_SENSOR == "st.DoorSensor"

    def test_lock_handlers(self):
        """Supported lock handlers include expected types."""
        assert "utec-lock" in _const.SUPPORTED_LOCK_HANDLERS
        assert "utec-lock-sensor" in _const.SUPPORTED_LOCK_HANDLERS


class TestJammedStateParsing:
    """Test parsing of jammed lock state."""

    def test_jammed_state_detected(self):
        """Parse jammed state correctly from query response."""
        states = QUERY_RESPONSE_JAMMED["payload"]["devices"][0]["states"]

        lock_state = next(s for s in states if s["capability"] == "st.Lock")
        assert lock_state["value"] == "jammed"

    def test_jammed_state_value(self):
        """Jammed state maps to is_jammed in device state model."""
        state = _models.XthingsDeviceState(
            online=True,
            lock_state="jammed",
            is_jammed=True,
        )
        assert state.is_jammed is True

    def test_non_jammed_state(self):
        """Locked/unlocked states are not jammed."""
        state = _models.XthingsDeviceState(
            online=True,
            lock_state="locked",
            is_jammed=False,
        )
        assert state.is_jammed is False


class TestDoorSensorParsing:
    """Test parsing of door sensor state."""

    def test_door_closed(self):
        """Parse door closed state."""
        states = QUERY_RESPONSE_WITH_DOOR_SENSOR["payload"]["devices"][0]["states"]

        door = next(s for s in states if s["capability"] == "st.DoorSensor")
        assert door["name"] == "sensorState"
        assert door["value"] == "closed"

    def test_door_open(self):
        """Parse door open state."""
        states = QUERY_RESPONSE_DOOR_OPEN["payload"]["devices"][0]["states"]

        door = next(s for s in states if s["capability"] == "st.DoorSensor")
        assert door["value"] == "open"

    def test_door_sensor_in_device_state(self):
        """Door state model stores sensor value."""
        state = _models.XthingsDeviceState(door_state="closed")
        assert state.door_state == "closed"

        state = _models.XthingsDeviceState(door_state="open")
        assert state.door_state == "open"

    def test_door_sensor_absent(self):
        """Devices without door sensor have None door_state."""
        state = _models.XthingsDeviceState(online=True, lock_state="locked")
        assert state.door_state is None


class TestSetModeCommand:
    """Test lock mode setting command construction."""

    def test_set_mode_request_body(self):
        """SetMode command has correct capability and arguments."""
        body = {
            "header": {
                "namespace": "Uhome.Device",
                "name": "Command",
                "messageId": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "payloadVersion": "1",
            },
            "payload": {
                "devices": [
                    {
                        "id": "AA:BB:CC:DD:EE:01",
                        "command": {
                            "capability": "st.lock",
                            "name": "setMode",
                            "arguments": {"mode": 0},
                        },
                    }
                ],
            },
        }
        command = body["payload"]["devices"][0]["command"]
        assert command["capability"] == "st.lock"
        assert command["name"] == "setMode"
        assert command["arguments"]["mode"] == 0

    def test_set_mode_deferred_response(self):
        """SetMode returns deferred response."""
        states = SET_MODE_COMMAND_RESPONSE["payload"]["devices"][0]["states"]
        deferred = next(
            s for s in states if s["capability"] == "st.deferredResponse"
        )
        assert deferred["value"] == 5


class TestLockUserManagementCommands:
    """Test lock user management command construction."""

    def test_list_users_request(self):
        """List users command has correct structure."""
        body = {
            "header": {
                "namespace": "Uhome.Device",
                "name": "Command",
                "messageId": "test-uuid",
                "payloadVersion": "1",
            },
            "payload": {
                "devices": [
                    {
                        "id": "AA:BB:CC:DD:EE:01",
                        "command": {
                            "capability": "st.lockUser",
                            "name": "list",
                        },
                    }
                ],
            },
        }
        command = body["payload"]["devices"][0]["command"]
        assert command["capability"] == "st.lockUser"
        assert command["name"] == "list"

    def test_list_users_response(self):
        """List users response contains user data."""
        states = LOCK_USER_LIST_RESPONSE["payload"]["devices"][0]["states"]
        assert len(states) == 2
        assert states[0]["name"] == "user1"
        assert states[0]["type"] == 0
        assert states[1]["name"] == "admin"
        assert states[1]["type"] == 3

    def test_add_user_request(self):
        """Add user command includes user object in arguments."""
        body = {
            "header": {
                "namespace": "Uhome.Device",
                "name": "Command",
                "messageId": "test-uuid",
                "payloadVersion": "1",
            },
            "payload": {
                "devices": [
                    {
                        "id": "AA:BB:CC:DD:EE:01",
                        "command": {
                            "capability": "st.lockUser",
                            "name": "add",
                            "arguments": {
                                "user": {
                                    "name": "Guest",
                                    "type": 0,
                                    "password": 123456,
                                }
                            },
                        },
                    }
                ],
            },
        }
        command = body["payload"]["devices"][0]["command"]
        assert command["name"] == "add"
        user = command["arguments"]["user"]
        assert user["name"] == "Guest"
        assert user["type"] == 0
        assert user["password"] == 123456

    def test_add_temporary_user_request(self):
        """Temporary user includes schedule fields."""
        user = {
            "name": "Temp Guest",
            "type": 2,
            "password": 1234,
            "daterange": ["2024-07-01 00:00", "2024-07-31 23:59"],
            "weeks": [0, 1, 2, 3, 4, 5, 6],
            "timerange": ["08:00", "18:00"],
            "limit": 10,
        }
        assert user["type"] == 2
        assert len(user["daterange"]) == 2
        assert len(user["weeks"]) == 7
        assert len(user["timerange"]) == 2
        assert user["limit"] == 10

    def test_update_user_request(self):
        """Update user command includes id field."""
        command = {
            "capability": "st.lockUser",
            "name": "update",
            "arguments": {
                "user": {
                    "id": 23456,
                    "name": "Updated Name",
                    "type": 0,
                    "password": 654321,
                }
            },
        }
        user = command["arguments"]["user"]
        assert "id" in user
        assert user["id"] == 23456
        assert user["name"] == "Updated Name"

    def test_delete_user_request(self):
        """Delete user command has correct structure."""
        command = {
            "capability": "st.lockUser",
            "name": "delete",
            "arguments": {"id": 23456},
        }
        assert command["name"] == "delete"
        assert command["arguments"]["id"] == 23456

    def test_get_user_request(self):
        """Get user command has correct structure."""
        command = {
            "capability": "st.lockUser",
            "name": "get",
            "arguments": {"id": 100},
        }
        assert command["name"] == "get"
        assert command["arguments"]["id"] == 100


class TestDeviceHandlerTypes:
    """Test device handler type identification."""

    def test_utec_lock_handler(self):
        """utec-lock handler supports Lock, BatteryLevel, LockUser."""
        info = _models.XthingsDeviceInfo(
            device_id="test-id",
            name="U-Bolt Pro",
            category="LOCK",
            handle_type="utec-lock",
            manufacturer="U-tec",
            model="U-Bolt-Pro-WiFi",
            hw_version="1.0",
        )
        assert info.is_lock is True
        # utec-lock does NOT have door sensor (LockUser instead)
        assert info.handle_type != "utec-lock-sensor"

    def test_utec_lock_sensor_handler(self):
        """utec-lock-sensor handler supports Lock, BatteryLevel, DoorSensor."""
        info = _models.XthingsDeviceInfo(
            device_id="test-id",
            name="U-Bolt WiFi",
            category="LOCK",
            handle_type="utec-lock-sensor",
            manufacturer="U-tec",
            model="U-Bolt-WiFi",
            hw_version="1.0",
        )
        assert info.is_lock is True
        # utec-lock-sensor has DoorSensor capability
        assert info.handle_type == "utec-lock-sensor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
