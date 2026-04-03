from __future__ import annotations

import logging
from pathlib import Path
import signal
import threading
import time

from ha_presence import __version__
from ha_presence.config import ServiceConfig
from ha_presence.mqtt_client import MqttPublisher
from ha_presence.presence import PresenceState, build_presence_payload
from ha_presence.update.manager import UpdateManager

logger = logging.getLogger(__name__)


class PresenceService:
    def __init__(self, config: ServiceConfig, app_dir: Path) -> None:
        self._config = config
        self._mqtt = MqttPublisher(config)
        self._updater = UpdateManager(config, app_dir)
        self._stop_event = threading.Event()
        self._state = PresenceState(
            hostname=config.hostname,
            started_monotonic=time.monotonic(),
            version=__version__,
        )

    def run(self) -> None:
        self._install_signal_handlers()
        self._mqtt.connect()
        self._mqtt.publish_discovery()

        next_update_check = time.monotonic()
        try:
            while not self._stop_event.is_set():
                payload = build_presence_payload(self._state)
                self._mqtt.publish_status(payload)
                self._mqtt.publish_attributes(payload)

                now = time.monotonic()
                if now >= next_update_check:
                    self._check_and_log_update()
                    next_update_check = now + self._config.update_poll_seconds

                self._stop_event.wait(self._config.heartbeat_seconds)
        finally:
            self._mqtt.close()

    def stop(self) -> None:
        self._stop_event.set()

    def _check_and_log_update(self) -> None:
        candidate = self._updater.check_for_update(self._state.version)
        if candidate is None:
            return
        logger.info("Update available: version=%s source=%s", candidate.version, candidate.source)

    def _install_signal_handlers(self) -> None:
        for signame in ("SIGINT", "SIGTERM"):
            sig = getattr(signal, signame, None)
            if sig is None:
                continue
            signal.signal(sig, lambda _s, _f: self.stop())
