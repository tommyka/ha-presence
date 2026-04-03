from __future__ import annotations

import logging
from pathlib import Path
import subprocess

from ha_presence.update.base import UpdateCandidate

logger = logging.getLogger(__name__)


class GitUpdater:
    def __init__(self, repo_url: str, ref: str, app_dir: Path) -> None:
        self._repo_url = repo_url
        self._ref = ref
        self._app_dir = app_dir

    def check_for_update(self, current_version: str) -> UpdateCandidate | None:
        remote_sha = self._remote_sha()
        if remote_sha is None:
            logger.warning("Could not resolve remote ref %s from %s", self._ref, self._repo_url)
            return None

        local_sha = self._local_sha()
        if local_sha == remote_sha:
            return None

        return UpdateCandidate(version=remote_sha, source=self._repo_url)

    def apply_update(self, candidate: UpdateCandidate, target_dir: Path) -> None:
        if (target_dir / ".git").exists():
            subprocess.run(["git", "fetch", "--all"], cwd=target_dir, check=True)
            subprocess.run(["git", "checkout", self._ref], cwd=target_dir, check=True)
            subprocess.run(["git", "pull", "--ff-only", "origin", self._ref], cwd=target_dir, check=True)
            return

        subprocess.run(["git", "clone", "--branch", self._ref, self._repo_url, str(target_dir)], check=True)

    def _remote_sha(self) -> str | None:
        """Return the commit SHA the remote ref resolves to, or None on failure."""
        try:
            result = subprocess.run(
                ["git", "ls-remote", self._repo_url, self._ref],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            return None
        line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        return line.split()[0] if line else None

    def _local_sha(self) -> str | None:
        """Return the current HEAD SHA of the local repo, or None if not a git repo."""
        if not (self._app_dir / ".git").exists():
            return None
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self._app_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip() or None
        except subprocess.CalledProcessError:
            return None
