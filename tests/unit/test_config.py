from __future__ import annotations

import os
import tempfile
from pathlib import Path
import unittest

from ha_presence.config import UpdateSource, load_config


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self._old = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old)

    def test_defaults_load(self) -> None:
        os.environ.pop("HA_PRESENCE_UPDATE_SOURCE", None)
        cfg = load_config()
        self.assertEqual(cfg.update_source, UpdateSource.NONE)
        self.assertEqual(cfg.heartbeat_seconds, 30)

    def test_requires_location_for_git(self) -> None:
        os.environ["HA_PRESENCE_UPDATE_SOURCE"] = "git"
        os.environ.pop("HA_PRESENCE_UPDATE_LOCATION", None)
        with self.assertRaises(ValueError):
            load_config()

    def test_hostname_with_space_raises(self) -> None:
        os.environ["HA_PRESENCE_HOSTNAME"] = "my laptop"
        with self.assertRaises(ValueError):
            load_config()

    def test_file_values_are_loaded(self) -> None:
        toml = b"""
[presence]
site = "office"
heartbeat_seconds = 60

[mqtt]
host = "broker.local"
port = 8883
topic_prefix = "work"

[update]
source = "none"
ref = "main"
poll_seconds = 600
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml)
            path = Path(f.name)
        try:
            cfg = load_config(config_file=path)
            self.assertEqual(cfg.site, "office")
            self.assertEqual(cfg.heartbeat_seconds, 60)
            self.assertEqual(cfg.mqtt_host, "broker.local")
            self.assertEqual(cfg.mqtt_port, 8883)
            self.assertEqual(cfg.mqtt_topic_prefix, "work")
            self.assertEqual(cfg.update_poll_seconds, 600)
        finally:
            path.unlink()

    def test_env_overrides_file(self) -> None:
        toml = b"""
[presence]
site = "office"

[mqtt]
host = "broker.local"
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            f.write(toml)
            path = Path(f.name)
        try:
            os.environ["HA_PRESENCE_SITE"] = "override-site"
            cfg = load_config(config_file=path)
            self.assertEqual(cfg.site, "override-site")
            self.assertEqual(cfg.mqtt_host, "broker.local")  # still from file
        finally:
            path.unlink()

