from __future__ import annotations

import subprocess


def restart_service(service_name: str) -> None:
    subprocess.run(["powershell", "-Command", f"Restart-Service -Name '{service_name}'"], check=True)
