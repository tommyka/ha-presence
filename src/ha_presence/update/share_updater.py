from __future__ import annotations

import hashlib
from pathlib import Path
import shutil

from ha_presence.update.base import UpdateCandidate


class ShareUpdater:
    def __init__(self, share_path: Path) -> None:
        self._share_path = share_path

    def check_for_update(self, current_version: str) -> UpdateCandidate | None:
        candidate_file = self._share_path / "VERSION"
        if not candidate_file.exists():
            return None
        version = candidate_file.read_text(encoding="utf-8").strip()
        if version == current_version:
            return None
        return UpdateCandidate(version=version, source=str(self._share_path))

    def apply_update(self, candidate: UpdateCandidate, target_dir: Path) -> None:
        _ = candidate
        manifest = self._share_path / "manifest.sha256"
        if manifest.exists():
            self._verify_manifest(manifest)

        for item in self._share_path.iterdir():
            if item.name in {"manifest.sha256"}:
                continue
            destination = target_dir / item.name
            if item.is_dir():
                if destination.exists():
                    shutil.rmtree(destination)
                shutil.copytree(item, destination)
            else:
                shutil.copy2(item, destination)

    def _verify_manifest(self, manifest: Path) -> None:
        for line in manifest.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            checksum, relative = line.split(maxsplit=1)
            path = self._share_path / relative
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != checksum:
                msg = f"Checksum mismatch for {relative}"
                raise RuntimeError(msg)
