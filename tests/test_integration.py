"""
Integration tests for the Xthings (U-tec) custom component.

These tests use the real Home Assistant ``hass`` fixture provided by
pytest-homeassistant-custom-component.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    STATE_LOCKED,
    STATE_UNLOCKED,
)
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xthings.const import DOMAIN
from custom_components.xthings.models import (
    XthingsCoordinatorData,
    XthingsDeviceInfo,
    XthingsDeviceState,
)

from .conftest import (
    MOCK_CONFIG_ENTRY_DATA,
    MOCK_DEVICE_ID,
    MOCK_DEVICE_ID_2,
    MOCK_QUERY_UNLOCKED,
)

# ── Helpers ─────────────────────────────────────────────────────


def _mock_oauth2_session() -> MagicMock:
    """Create a mock OAuth2Session."""
    session = MagicMock()
    session.token = {
        "access_token": "mock-access-token",
        "refresh_token": "mock-refresh-token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    session.async_ensure_token_valid = AsyncMock()
    return session


def _create_config_entry() -> MockConfigEntry:
    """Create a MockConfigEntry for the xthings integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Xthings (U-tec)",
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id="xthings-test-user",
    )


# ── Setup / teardown tests ─────────────────────────────────────


@pytest.mark.asyncio
async def test_setup_entry(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test that async_setup_entry creates coordinator and forwards platforms."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        result = await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert result is True
    assert entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test that async_unload_entry cleans up."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

    assert result is True
    assert entry.entry_id not in hass.data.get(DOMAIN, {})


# ── Lock entity tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_lock_entity_locked(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test that lock entity reports locked when API returns 'locked'."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("lock.front_door_lock")
    assert state is not None
    assert state.state == STATE_LOCKED


@pytest.mark.asyncio
async def test_lock_entity_unlocked(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test that lock entity reports unlocked."""
    # Override mock to return unlocked state
    mock_api.async_query_device = AsyncMock(
        return_value=MOCK_QUERY_UNLOCKED["payload"]["devices"][0]["states"],
    )

    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("lock.front_door_lock")
    assert state is not None
    assert state.state == STATE_UNLOCKED


@pytest.mark.asyncio
async def test_lock_command(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test calling the lock service sends a lock command."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Call the lock service
        await hass.services.async_call(
            "lock",
            "lock",
            {"entity_id": "lock.front_door_lock"},
            blocking=True,
        )
        await hass.async_block_till_done()

    mock_api.async_lock.assert_called_once_with(MOCK_DEVICE_ID, {"userId": 12345})


@pytest.mark.asyncio
async def test_unlock_command(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test calling the unlock service sends an unlock command."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        # Call the unlock service
        await hass.services.async_call(
            "lock",
            "unlock",
            {"entity_id": "lock.front_door_lock"},
            blocking=True,
        )
        await hass.async_block_till_done()

    mock_api.async_unlock.assert_called_once_with(MOCK_DEVICE_ID, {"userId": 12345})


# ── Battery sensor tests ───────────────────────────────────────


@pytest.mark.asyncio
async def test_battery_sensor(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test battery sensor reports correct percentage."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("sensor.front_door_lock_battery")
    assert state is not None
    assert state.state == "85"


@pytest.mark.asyncio
async def test_multiple_devices(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test that both lock devices are created."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Both locks should exist
    lock1 = hass.states.get("lock.front_door_lock")
    lock2 = hass.states.get("lock.back_door_lock")
    assert lock1 is not None
    assert lock2 is not None

    # Both battery sensors should exist
    bat1 = hass.states.get("sensor.front_door_lock_battery")
    bat2 = hass.states.get("sensor.back_door_lock_battery")
    assert bat1 is not None
    assert bat2 is not None


# ── Coordinator tests ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_coordinator_discovery(hass: HomeAssistant, mock_api: AsyncMock) -> None:
    """Test that the coordinator discovers devices on setup."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Coordinator should have discovered both devices
    assert len(coordinator.data.devices) == 2
    assert MOCK_DEVICE_ID in coordinator.data.devices
    assert MOCK_DEVICE_ID_2 in coordinator.data.devices

    # Device info should be correct
    device = coordinator.data.devices[MOCK_DEVICE_ID]
    assert device.name == "Front Door Lock"
    assert device.is_lock is True
    assert device.model == "U-Bolt-Pro-WiFi"


@pytest.mark.asyncio
async def test_coordinator_state_parsing(
    hass: HomeAssistant, mock_api: AsyncMock
) -> None:
    """Test that coordinator correctly parses device state."""
    entry = _create_config_entry()
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.async_get_config_entry_implementation",
            return_value=AsyncMock(),
        ),
        patch(
            "custom_components.xthings.config_entry_oauth2_flow.OAuth2Session",
            return_value=_mock_oauth2_session(),
        ),
        patch(
            "custom_components.xthings.XthingsApiClient",
            return_value=mock_api,
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id]
    state = coordinator.data.states.get(MOCK_DEVICE_ID)

    assert state is not None
    assert state.online is True
    assert state.lock_state == "locked"
    assert state.battery_level == 85


# ── Data model tests (no hass needed but included for coverage) ─


class TestModels:
    """Test data model dataclasses."""

    def test_device_info_is_lock_by_category(self) -> None:
        """Device with LOCK category is a lock."""
        info = XthingsDeviceInfo(
            device_id="id",
            name="Lock",
            category="LOCK",
            handle_type="unknown",
            manufacturer="U-tec",
            model="Test",
            hw_version="1.0",
        )
        assert info.is_lock is True

    def test_device_info_is_lock_by_handler(self) -> None:
        """Device with utec-lock handler is a lock."""
        info = XthingsDeviceInfo(
            device_id="id",
            name="Lock",
            category="UNKNOWN",
            handle_type="utec-lock",
            manufacturer="U-tec",
            model="Test",
            hw_version="1.0",
        )
        assert info.is_lock is True

    def test_device_info_not_lock(self) -> None:
        """Non-lock device is not a lock."""
        info = XthingsDeviceInfo(
            device_id="id",
            name="Light",
            category="LIGHT",
            handle_type="utec-bulb",
            manufacturer="U-tec",
            model="A19",
            hw_version="1.0",
        )
        assert info.is_lock is False

    def test_device_state_defaults(self) -> None:
        """Defaults are correct."""
        state = XthingsDeviceState()
        assert state.online is False
        assert state.lock_state is None
        assert state.battery_level is None

    def test_coordinator_data_defaults(self) -> None:
        """Empty defaults."""
        data = XthingsCoordinatorData()
        assert data.devices == {}
        assert data.states == {}
