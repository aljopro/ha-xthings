# Xthings (U-tec) Integration for Home Assistant

[![HACS Validation](https://github.com/aljopro/ha-xthings/actions/workflows/validate.yml/badge.svg)](https://github.com/aljopro/ha-xthings/actions/workflows/validate.yml)
[![Lint](https://github.com/aljopro/ha-xthings/actions/workflows/lint.yml/badge.svg)](https://github.com/aljopro/ha-xthings/actions/workflows/lint.yml)

A custom Home Assistant integration for **U-tec ULTRALOQ** WiFi smart locks via the [Xthings OpenAPI](https://developer.xthings.com/hc/en-us/sections/39589678120985-Developer-Documentation).

## Supported Devices

| Device | Handler Type | Features |
|--------|-------------|----------|
| U-Bolt Pro WiFi | `utec-lock` | Lock/Unlock, Battery Level |
| U-Bolt WiFi | `utec-lock` | Lock/Unlock, Battery Level |
| Locks with door sensor | `utec-lock-sensor` | Lock/Unlock, Battery Level, Door Sensor |

> **Note:** This integration has only been tested with the **U-Bolt Pro WiFi** and **U-Bolt WiFi** locks. Other U-tec WiFi devices may work but are untested.

## Features

- **Lock Entity** — Lock and unlock your U-tec locks from Home Assistant
- **Battery Sensor** — Monitor battery level as a percentage
- **Online Status** — Entity availability reflects device connectivity
- **OAuth2 Authentication** — Secure cloud authentication via the Xthings OpenAPI
- **Automatic Token Refresh** — Tokens are refreshed automatically when they expire
- **Polling** — Device state is polled every 60 seconds
- **Push Notifications (Webhook)** — Optional near-instant state updates via the Xthings notification API

## Prerequisites

1. A U-tec WiFi lock connected to the Xthings / ULTRALOQ app
2. **OpenAPI activated** in the Xthings app (Settings → OpenAPI)
3. Your **Client ID** and **Client Secret** from the OpenAPI settings

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the **⋮** menu → **Custom repositories**
3. Add `https://github.com/aljopro/ha-xthings` with category **Integration**
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

### Step 4 (Optional): Enable Push Notifications

By default, the integration polls for state changes every 60 seconds. You can enable **push notifications** for near-instant updates when a lock is operated, a device goes offline, etc.

1. Go to **Settings → Devices & Services**
2. Find the **Xthings (U-tec)** integration and click **Configure**
3. Toggle on **Enable push notifications (webhook)**
4. Choose your URL method (see below)
5. Click **Update** — the integration will reload automatically

#### Option A: With Nabu Casa Cloud

If you have [Nabu Casa Home Assistant Cloud](https://www.nabucasa.com/), leave the **External Home Assistant URL** field blank. A secure cloudhook URL is created automatically — no port forwarding or DNS setup required.

#### Option B: Without Nabu Casa (Manual URL)

If you don't have Nabu Casa but your Home Assistant instance is reachable from the internet, enter your **external base URL** in the text field. For example:

- `https://my-ha.duckdns.org`
- `https://ha.example.com`

The integration appends the webhook path automatically (e.g. `https://my-ha.duckdns.org/api/webhook/<id>`).

**Common ways to expose Home Assistant externally:**

| Method | Example URL |
|--------|-------------|
| [DuckDNS](https://www.home-assistant.io/integrations/duckdns/) + Let's Encrypt | `https://myha.duckdns.org` |
| [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) | `https://ha.yourdomain.com` |
| Reverse proxy (nginx, Caddy, Traefik) | `https://ha.yourdomain.com` |
| Router port forwarding + DDNS | `https://myha.ddns.net:8123` |

> **Important:** The URL must be reachable from the public internet (HTTPS recommended). The Xthings cloud servers will POST notifications to this URL. Local-only addresses (e.g. `http://192.168.1.x:8123`) will not work.

#### How push notifications work

When webhooks are enabled, the Xthings API sends HTTP POST notifications to your Home Assistant whenever:

- A **device state changes** (lock/unlock, battery level, online/offline)
- A **device is added or removed** from your account
- A **device is deleted**

The integration still polls as a safety net, but at a slower interval (every 5 minutes instead of 60 seconds).

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
- When webhooks are enabled, state changes are pushed instantly via HTTP POST and polling is reduced to a 5-minute safety net

## Troubleshooting

### "Authentication failed" errors
- Verify your Client ID and Client Secret are correct
- Check that OpenAPI is still activated in the Xthings app
- Try removing and re-adding the integration

### Lock state not updating
- The integration polls every 60 seconds by default (5 minutes when webhooks are active)
- After a lock/unlock command, rapid polling checks every 3 seconds for up to 30 seconds
- If you have webhooks enabled, verify your external URL is reachable from the internet
- Check the Home Assistant logs for API errors: **Settings → System → Logs**, filter for `xthings`

### "Device unavailable"
- The lock may be offline (out of WiFi range, batteries dead)
- Check the lock's connectivity in the Xthings app

## Development

```bash
# Clone the repository
git clone https://github.com/aljopro/ha-xthings.git
cd ha-xthings

# Install dev dependencies
scripts/setup

# Run the linter
scripts/lint

# Start a local HA instance with the component
scripts/develop

# Or use Docker
docker compose up
```

For architecture details and Xthings API documentation, see the [`docs/`](docs/) folder and [`.instructions.md`](.instructions.md).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution workflow, branch strategy, and release process.

## License

MIT License — see [LICENSE](LICENSE) for details.
