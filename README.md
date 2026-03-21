# Xthings (U-tec) Integration for Home Assistant

[![HACS Validation](https://github.com/jensen/ha-xthings/actions/workflows/validate.yml/badge.svg)](https://github.com/jensen/ha-xthings/actions/workflows/validate.yml)
[![Hassfest](https://github.com/jensen/ha-xthings/actions/workflows/hassfest.yml/badge.svg)](https://github.com/jensen/ha-xthings/actions/workflows/hassfest.yml)

A custom Home Assistant integration for **U-tec ULTRALOQ** WiFi smart locks via the [Xthings OpenAPI](https://developer.xthings.com/hc/en-us/sections/39589678120985-Developer-Documentation).

## Supported Devices

| Device | Handler Type | Features |
|--------|-------------|----------|
| U-Bolt Pro WiFi | `utec-lock` | Lock/Unlock, Battery Level |
| U-Bolt WiFi | `utec-lock` | Lock/Unlock, Battery Level |
| Locks with door sensor | `utec-lock-sensor` | Lock/Unlock, Battery Level, Door Sensor |

## Features

- **Lock Entity** — Lock and unlock your U-tec locks from Home Assistant
- **Battery Sensor** — Monitor battery level as a percentage
- **Online Status** — Entity availability reflects device connectivity
- **OAuth2 Authentication** — Secure cloud authentication via the Xthings OpenAPI
- **Automatic Token Refresh** — Tokens are refreshed automatically when they expire
- **Polling** — Device state is polled every 60 seconds

## Prerequisites

1. A U-tec WiFi lock connected to the Xthings / ULTRALOQ app
2. **OpenAPI activated** in the Xthings app (Settings → OpenAPI)
3. Your **Client ID** and **Client Secret** from the OpenAPI settings

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the **⋮** menu → **Custom repositories**
3. Add `https://github.com/jensen/ha-xthings` with category **Integration**
4. Click **Download** on the Xthings (U-tec) card
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/xthings` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

### Step 1: Add Application Credentials

1. Go to **Settings → Devices & Services → Application Credentials**
2. Click **Add Application Credentials**
3. Select **Xthings (U-tec)**
4. Enter your **Client ID** and **Client Secret** from the Xthings app

### Step 2: Update Redirect URI

In the Xthings / ULTRALOQ app, update the **Redirect URI** to match your Home Assistant instance:

- **If using Nabu Casa:** `https://<your-id>.ui.nabu.casa/auth/external/callback`
- **If using local access:** `http://<your-ha-ip>:8123/auth/external/callback`

### Step 3: Add the Integration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Xthings**
3. Follow the OAuth2 authorization flow
4. Your locks will be discovered automatically

## Entities Created

For each discovered lock, the integration creates:

| Entity | Type | Description |
|--------|------|-------------|
| `lock.<name>` | Lock | Lock/unlock control and state |
| `sensor.<name>_battery` | Sensor | Battery level (%) |

## How It Works

- All API calls go through `POST https://api.u-tec.com/action`
- Lock/unlock commands are **asynchronous** — the API returns a deferred response, and the integration polls for the updated state after a short delay
- Device discovery happens on first setup and when state queries return no devices
- The integration uses HA's `DataUpdateCoordinator` for efficient polling

## Troubleshooting

### "Authentication failed" errors
- Verify your Client ID and Client Secret are correct
- Check that OpenAPI is still activated in the Xthings app
- Try removing and re-adding the integration

### Lock state not updating
- The integration polls every 60 seconds by default
- After a lock/unlock command, there's a ~12 second delay for the deferred response
- Check the Home Assistant logs for API errors: **Settings → System → Logs**, filter for `xthings`

### "Device unavailable"
- The lock may be offline (out of WiFi range, batteries dead)
- Check the lock's connectivity in the Xthings app

## Development

```bash
# Clone the repository
git clone https://github.com/jensen/ha-xthings.git

# The integration code is in custom_components/xthings/
```

## License

MIT License — see [LICENSE](LICENSE) for details.
