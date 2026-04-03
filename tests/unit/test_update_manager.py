from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ha_presence.config import ServiceConfig, UpdateSource
from ha_presence.update.manager import UpdateManager


class TestUpdateManager(unittest.TestCase):
    def _cfg(self, source: UpdateSource, location: str | None) -> ServiceConfig:
        return ServiceConfig(
            hostname="h",
            site="s",
            heartbeat_seconds=30,
            mqtt_host="localhost",
            mqtt_port=1883,
            mqtt_username=None,
            mqtt_password=None,
            mqtt_topic_prefix="home",
            update_source=source,
            update_location=location,
            update_ref="main",
            update_poll_seconds=300,
        )

    def test_none_source_returns_no_update(self) -> None:
        cfg = self._cfg(UpdateSource.NONE, None)
        manager = UpdateManager(cfg, app_dir=Path.cwd())
        self.assertIsNone(manager.check_for_update("0.1.0"))

    def test_share_update_detects_new_version(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            share = Path(td)
            (share / "VERSION").write_text("9.9.9", encoding="utf-8")
            cfg = self._cfg(UpdateSource.SHARE, str(share))
            manager = UpdateManager(cfg, app_dir=Path.cwd())
            candidate = manager.check_for_update("0.1.0")
            self.assertIsNotNone(candidate)
            assert candidate is not None
            self.assertEqual(candidate.version, "9.9.9")
