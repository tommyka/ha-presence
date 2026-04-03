# HA Presence Service (Python)

Cross-platform service (Linux + Windows) that publishes host availability to Home Assistant via MQTT and can self-update from either a git repository or a network share.

## Current status
This is an initial scaffold with:
- Presence payload generation
- Config loading from a settings file and/or environment variables
- MQTT client wrapper
- Update interfaces and manager
- Linux/Windows platform adapters
- CLI commands: `run`, `check-update`, `apply-update`

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run ha-presence run
```

## Configuration

Settings are loaded from a TOML file and environment variables. **Environment variables always take precedence over file values.**

### Settings file

Copy the example file and edit it:

```bash
cp ha-presence.example.toml ha-presence.toml
```

The following locations are checked in order:
1. Path passed via `--config FILE`
2. `HA_PRESENCE_CONFIG` environment variable
3. `ha-presence.toml` in the current working directory
4. `~/.config/ha-presence/config.toml`

### Environment variables

| Variable | Description |
|---|---|
| `HA_PRESENCE_CONFIG` | Path to a TOML settings file |
| `HA_PRESENCE_HOSTNAME` | Identifier for this host (default: system hostname). **Must not contain spaces** — it is used as part of MQTT topic paths. Use hyphens instead, e.g. `my-laptop`. |
| `HA_PRESENCE_SITE` | Logical site name used in MQTT topics (default: `home`) |
| `HA_PRESENCE_HEARTBEAT_SECONDS` | Heartbeat publish interval (default: `30`) |
| `HA_PRESENCE_MQTT_HOST` | MQTT broker address (default: `localhost`) |
| `HA_PRESENCE_MQTT_PORT` | MQTT broker port (default: `1883`) |
| `HA_PRESENCE_MQTT_USERNAME` | MQTT username |
| `HA_PRESENCE_MQTT_PASSWORD` | MQTT password |
| `HA_PRESENCE_MQTT_TOPIC_PREFIX` | MQTT topic prefix (default: `ha-presence`) |
| `HA_PRESENCE_UPDATE_SOURCE` | `none` \| `git` \| `share` (default: `none`) |
| `HA_PRESENCE_UPDATE_LOCATION` | Git URL or share path (required when source is not `none`) |
| `HA_PRESENCE_UPDATE_REF` | Git ref to track (default: `main`) |
| `HA_PRESENCE_UPDATE_POLL_SECONDS` | Update poll interval (default: `300`) |

## Development

```bash
uv sync
uv run pytest
```

## Packaging

**Linux (systemd)**

```bash
sudo ./packaging/systemd/install.sh --dir /opt/ha-presence
```

Options:
- `--dir` — where the project lives (default: `/opt/ha-presence`)
- `--user` — system user to run the service as (default: `ha-presence`, created if missing)

The script creates the user, runs `uv sync`, writes the unit file with the correct paths, and enables + starts the service.

**Windows**

```powershell
.\packaging\windows\install_service.ps1 -WorkingDir "C:\ha-presence"
```

Options:
- `-WorkingDir` — where the project lives (default: `C:\ha-presence`)
- `-UvExe` — path to `uv` if it's not on `PATH` (default: `uv`)


