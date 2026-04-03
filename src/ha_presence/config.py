from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
import socket
import tomllib
from typing import Any


class UpdateSource(str, Enum):
    NONE = "none"
    GIT = "git"
    SHARE = "share"


@dataclass
class ServiceConfig:
    hostname: str
    site: str
    heartbeat_seconds: int
    mqtt_host: str
    mqtt_port: int
    mqtt_username: str | None
    mqtt_password: str | None
    mqtt_topic_prefix: str
    update_source: UpdateSource
    update_location: str | None
    update_ref: str
    update_poll_seconds: int

    @property
    def base_topic(self) -> str:
        return f"{self.mqtt_topic_prefix}/{self.site}/{self.hostname}"


def _env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def _load_file(path: Path | None) -> dict[str, Any]:
    """Load TOML settings file. Searches standard locations when path is None."""
    candidates: list[Path] = (
        [path]
        if path is not None
        else [
            Path(_env("HA_PRESENCE_CONFIG") or "") if _env("HA_PRESENCE_CONFIG") else None,
            Path("ha-presence.toml"),
            Path.home() / ".config" / "ha-presence" / "config.toml",
        ]
    )
    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            with candidate.open("rb") as f:
                return tomllib.load(f)
    return {}


def _file_str(data: dict[str, Any], section: str, key: str) -> str | None:
    """Get a string value from a TOML section, returning None if absent."""
    val = data.get(section, {}).get(key)
    return str(val) if val is not None else None


def _resolve(env_name: str, data: dict[str, Any], section: str, key: str, default: str | None = None) -> str | None:
    """Return the first non-None value: env var → file → default."""
    return _env(env_name) or _file_str(data, section, key) or default


def load_config(config_file: Path | None = None) -> ServiceConfig:
    """Load config from a TOML file and/or environment variables.

    Environment variables always take precedence over file values.
    When *config_file* is None the following locations are tried in order:
      1. Path from ``HA_PRESENCE_CONFIG`` environment variable
      2. ``ha-presence.toml`` in the current working directory
      3. ``~/.config/ha-presence/config.toml``
    """
    data = _load_file(config_file)

    hostname = _resolve("HA_PRESENCE_HOSTNAME", data, "presence", "hostname", socket.gethostname()) or socket.gethostname()
    site = _resolve("HA_PRESENCE_SITE", data, "presence", "site", "home") or "home"

    if " " in hostname:
        msg = "HA_PRESENCE_HOSTNAME / presence.hostname must not contain spaces (used in MQTT topics)"
        raise ValueError(msg)

    source = UpdateSource(_resolve("HA_PRESENCE_UPDATE_SOURCE", data, "update", "source", "none") or "none")
    location = _resolve("HA_PRESENCE_UPDATE_LOCATION", data, "update", "location")
    if source in {UpdateSource.GIT, UpdateSource.SHARE} and not location:
        msg = "HA_PRESENCE_UPDATE_LOCATION / update.location is required when update source is git or share"
        raise ValueError(msg)

    return ServiceConfig(
        hostname=hostname,
        site=site,
        heartbeat_seconds=int(_resolve("HA_PRESENCE_HEARTBEAT_SECONDS", data, "presence", "heartbeat_seconds", "30") or "30"),
        mqtt_host=_resolve("HA_PRESENCE_MQTT_HOST", data, "mqtt", "host", "localhost") or "localhost",
        mqtt_port=int(_resolve("HA_PRESENCE_MQTT_PORT", data, "mqtt", "port", "1883") or "1883"),
        mqtt_username=_resolve("HA_PRESENCE_MQTT_USERNAME", data, "mqtt", "username"),
        mqtt_password=_resolve("HA_PRESENCE_MQTT_PASSWORD", data, "mqtt", "password"),
        mqtt_topic_prefix=_resolve("HA_PRESENCE_MQTT_TOPIC_PREFIX", data, "mqtt", "topic_prefix", "ha-presence") or "ha-presence",
        update_source=source,
        update_location=location,
        update_ref=_resolve("HA_PRESENCE_UPDATE_REF", data, "update", "ref", "main") or "main",
        update_poll_seconds=int(_resolve("HA_PRESENCE_UPDATE_POLL_SECONDS", data, "update", "poll_seconds", "300") or "300"),
    )
