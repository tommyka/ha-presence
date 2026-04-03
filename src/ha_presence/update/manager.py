from __future__ import annotations

from pathlib import Path

from ha_presence.config import ServiceConfig, UpdateSource
from ha_presence.update.base import UpdateCandidate, Updater
from ha_presence.update.git_updater import GitUpdater
from ha_presence.update.share_updater import ShareUpdater


class UpdateManager:
    def __init__(self, config: ServiceConfig, app_dir: Path) -> None:
        self._config = config
        self._app_dir = app_dir

    def _updater(self) -> Updater | None:
        if self._config.update_source == UpdateSource.NONE:
            return None
        if self._config.update_location is None:
            msg = "Update location cannot be empty when update source is configured"
            raise ValueError(msg)

        if self._config.update_source == UpdateSource.GIT:
            return GitUpdater(self._config.update_location, self._config.update_ref)
        if self._config.update_source == UpdateSource.SHARE:
            return ShareUpdater(Path(self._config.update_location))

        msg = f"Unsupported update source: {self._config.update_source}"
        raise ValueError(msg)

    def check_for_update(self, current_version: str) -> UpdateCandidate | None:
        updater = self._updater()
        if updater is None:
            return None
        return updater.check_for_update(current_version)

    def apply_update(self, candidate: UpdateCandidate) -> None:
        updater = self._updater()
        if updater is None:
            msg = "Update source is disabled"
            raise RuntimeError(msg)
        updater.apply_update(candidate, self._app_dir)
