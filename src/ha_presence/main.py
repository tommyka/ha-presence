from __future__ import annotations

import argparse
from pathlib import Path

from ha_presence import __version__
from ha_presence.config import load_config
from ha_presence.logging_setup import configure_logging
from ha_presence.service import PresenceService
from ha_presence.update.manager import UpdateManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ha-presence")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--config",
        metavar="FILE",
        type=Path,
        default=None,
        help="Path to a TOML settings file (default: ha-presence.toml or ~/.config/ha-presence/config.toml)",
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run", help="Run the presence service")
    sub.add_parser("check-update", help="Check if an update is available")
    sub.add_parser("apply-update", help="Apply available update")
    return parser


def main() -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(config_file=args.config)
    app_dir = Path.cwd()

    if args.command == "run":
        PresenceService(config, app_dir=app_dir).run()
        return 0

    manager = UpdateManager(config, app_dir=app_dir)
    candidate = manager.check_for_update(__version__)

    if args.command == "check-update":
        if candidate is None:
            print("No update available")
            return 0
        print(f"Update available: {candidate.version} from {candidate.source}")
        return 0

    if args.command == "apply-update":
        if candidate is None:
            print("No update available")
            return 0
        manager.apply_update(candidate)
        print(f"Applied update: {candidate.version}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
