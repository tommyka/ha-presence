#!/usr/bin/env bash
# Removes the ha-presence systemd service.
# Usage: sudo ./uninstall.sh [--user ha-presence]
set -euo pipefail

SERVICE_USER="ha-presence"
SERVICE_NAME="ha-presence"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

usage() {
    echo "Usage: sudo $0 [--user <service-user>]"
    echo ""
    echo "  --user  System user that was created for the service (will be removed)"
    echo "          Default: ${SERVICE_USER}"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --user) SERVICE_USER="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ $EUID -ne 0 ]]; then
    echo "Error: this script must be run as root (use sudo)" >&2
    exit 1
fi

if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "Stopping service: ${SERVICE_NAME}"
    systemctl stop "$SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "Disabling service: ${SERVICE_NAME}"
    systemctl disable "$SERVICE_NAME"
fi

if [[ -f "$SERVICE_FILE" ]]; then
    echo "Removing ${SERVICE_FILE}"
    rm "$SERVICE_FILE"
    systemctl daemon-reload
fi

if id "$SERVICE_USER" &>/dev/null; then
    echo "Removing system user: ${SERVICE_USER}"
    userdel "$SERVICE_USER"
fi

echo ""
echo "Done. The install directory was left in place — remove it manually if needed."
