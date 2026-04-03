from __future__ import annotations

from pathlib import Path
import subprocess

from ha_presence.update.base import UpdateCandidate


class GitUpdater:
    def __init__(self, repo_url: str, ref: str) -> None:
        self._repo_url = repo_url
        self._ref = ref

    def check_for_update(self, current_version: str) -> UpdateCandidate | None:
        _ = current_version
        return UpdateCandidate(version=self._ref, source=self._repo_url)

    def apply_update(self, candidate: UpdateCandidate, target_dir: Path) -> None:
        _ = candidate
        if (target_dir / ".git").exists():
            subprocess.run(["git", "fetch", "--all"], cwd=target_dir, check=True)
            subprocess.run(["git", "checkout", self._ref], cwd=target_dir, check=True)
            subprocess.run(["git", "pull", "--ff-only", "origin", self._ref], cwd=target_dir, check=True)
            return

        subprocess.run(["git", "clone", "--branch", self._ref, self._repo_url, str(target_dir)], check=True)
