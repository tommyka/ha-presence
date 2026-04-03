from __future__ import annotations

import subprocess


def restart_service(service_name: str) -> None:
    subprocess.run(["systemctl", "restart", service_name], check=True)
