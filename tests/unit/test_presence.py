from __future__ import annotations

import time
import unittest

from ha_presence.presence import PresenceState, build_presence_payload


class TestPresence(unittest.TestCase):
    def test_payload_contains_required_fields(self) -> None:
        state = PresenceState(hostname="host-a", started_monotonic=time.monotonic() - 5, version="1.2.3")
        payload = build_presence_payload(state)

        self.assertEqual(payload["host"], "host-a")
        self.assertEqual(payload["state"], "online")
        self.assertEqual(payload["version"], "1.2.3")
        self.assertIn("uptime_s", payload)
