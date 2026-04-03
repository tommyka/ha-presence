from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import platform
import socket
import time


@dataclass
class PresenceState:
    hostname: str
    started_monotonic: float
    version: str


def build_presence_payload(state: PresenceState) -> dict[str, str | int | float]:
    return {
        "host": state.hostname,
        "state": "online",
        "ts": datetime.now(timezone.utc).isoformat(),
        "uptime_s": int(time.monotonic() - state.started_monotonic),
        "ip": _best_effort_ip(),
        "platform": platform.platform(),
        "version": state.version,
    }


def _best_effort_ip() -> str:
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "unknown"
