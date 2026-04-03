from __future__ import annotations

import unittest

from ha_presence.main import build_parser


class TestCli(unittest.TestCase):
    def test_parser_accepts_run(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["run"])
        self.assertEqual(args.command, "run")
