from __future__ import annotations

import argparse
from pathlib import Path
import sys

from ha_presence import __version__
from ha_presence.config import ServiceConfig, load_config
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
    sub.add_parser("show-config", help="Print the resolved configuration and exit")
    if sys.platform == "win32":
        sub.add_parser("install-service", help="Register ha-presence as a Windows service (run as Administrator)")
        sub.add_parser("uninstall-service", help="Remove the Windows service registration (run as Administrator)")
    return parser


def main() -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "install-service":
        from ha_presence.platform.windows_service import handle_command
        handle_command("install")
        return 0

    if args.command == "uninstall-service":
        from ha_presence.platform.windows_service import handle_command
        handle_command("remove")
        return 0

    config = load_config(config_file=args.config)
    app_dir = Path.cwd()

    if args.command == "show-config":
        _print_config(config)
        return 0

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


def _print_config(config: ServiceConfig) -> None:
    password = "***" if config.mqtt_password else None
    rows = [
        ("presence.hostname",          config.hostname),
        ("presence.site",              config.site),
        ("presence.heartbeat_seconds", config.heartbeat_seconds),
        ("mqtt.host",                  config.mqtt_host),
        ("mqtt.port",                  config.mqtt_port),
        ("mqtt.username",              config.mqtt_username or "(not set)"),
        ("mqtt.password",              password or "(not set)"),
        ("mqtt.topic_prefix",          config.mqtt_topic_prefix),
        ("mqtt.base_topic",            config.base_topic),
        ("update.source",              config.update_source.value),
        ("update.location",            config.update_location or "(not set)"),
        ("update.ref",                 config.update_ref),
        ("update.poll_seconds",        config.update_poll_seconds),
    ]
    width = max(len(k) for k, _ in rows)
    print("Resolved configuration:")
    print("-" * (width + 20))
    for key, value in rows:
        print(f"  {key:<{width}}  {value}")


if __name__ == "__main__":
    raise SystemExit(main())
