from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class UpdateCandidate:
    version: str
    source: str


class Updater(Protocol):
    def check_for_update(self, current_version: str) -> UpdateCandidate | None:
        ...

    def apply_update(self, candidate: UpdateCandidate, target_dir: Path) -> None:
        ...
