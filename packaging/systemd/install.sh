#!/usr/bin/env bash
# Installs ha-presence as a systemd service.
# Usage: sudo ./install.sh [--dir /opt/ha-presence] [--user ha-presence]
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVICE_USER="ha-presence"
SERVICE_NAME="ha-presence"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

usage() {
    echo "Usage: sudo $0 [--dir <install-dir>] [--user <service-user>]"
    echo ""
    echo "  --dir   Directory where the project is (or will be) installed"
    echo "          Default: ${INSTALL_DIR}"
    echo "  --user  System user to run the service as"
    echo "          Default: ${SERVICE_USER}"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)  INSTALL_DIR="$2"; shift 2 ;;
        --user) SERVICE_USER="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ $EUID -ne 0 ]]; then
    echo "Error: this script must be run as root (use sudo)" >&2
    exit 1
fi

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating system user: ${SERVICE_USER}"
    useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
fi

# Ensure the install directory exists and is owned by the service user
mkdir -p "$INSTALL_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Run uv sync as the service user so the .venv is set up
echo "Running uv sync in ${INSTALL_DIR}"
sudo -u "$SERVICE_USER" uv sync --directory "$INSTALL_DIR" --no-dev

# Write the systemd unit file
echo "Writing ${SERVICE_FILE}"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=HA Presence Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
ExecStart=${INSTALL_DIR}/.venv/bin/ha-presence run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo ""
echo "Done. Service '${SERVICE_NAME}' is enabled and running."
echo "  Logs:   journalctl -u ${SERVICE_NAME} -f"
echo "  Status: systemctl status ${SERVICE_NAME}"
