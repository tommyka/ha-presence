from __future__ import annotations

from pathlib import Path
import sys

import servicemanager
import win32event
import win32service
import win32serviceutil

from ha_presence.config import load_config
from ha_presence.logging_setup import configure_logging
from ha_presence.service import PresenceService


# Project root is 4 levels up from this file:
# windows_service.py → platform/ → ha_presence/ → src/ → project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class HAPresenceWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "HAPresenceService"
    _svc_display_name_ = "HA Presence Service"
    _svc_description_ = "Host presence MQTT service for Home Assistant"

    def __init__(self, args: list[str]) -> None:
        win32serviceutil.ServiceFramework.__init__(self, args)
        self._stop_event = win32event.CreateEvent(None, 0, 0, None)
        self._presence: PresenceService | None = None

    def SvcStop(self) -> None:
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self._presence is not None:
            self._presence.stop()
        win32event.SetEvent(self._stop_event)

    def SvcDoRun(self) -> None:
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        configure_logging()
        config = load_config()
        self._presence = PresenceService(config, app_dir=_PROJECT_ROOT)
        self._presence.run()


def handle_command(action: str) -> None:
    """Run a pywin32 service management command (install, remove, start, stop)."""
    win32serviceutil.HandleCommandLine(
        HAPresenceWindowsService,
        argv=[sys.argv[0], action],
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Launched by the SCM — initialise and hand off to pywin32
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(HAPresenceWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(HAPresenceWindowsService)
