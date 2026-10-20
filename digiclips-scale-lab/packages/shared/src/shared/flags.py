"""Feature flags with deterministic percentage rollout.

Large teams merge unfinished work to trunk behind flags instead of keeping
long-lived branches. A user is bucketed by a stable hash of (flag, user_id), so
the same user always gets the same answer and raising the percentage only ever
adds users (it never flips someone who already had the feature off).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Flag:
    name: str
    enabled: bool
    rollout_percent: int = 0
    allow_roles: tuple[str, ...] = field(default_factory=tuple)

    def bucket(self, user_id: str) -> int:
        digest = hashlib.sha256(f"{self.name}:{user_id}".encode()).hexdigest()
        return int(digest[:8], 16) % 100

    def is_on(self, user_id: str, role: str = "subscriber") -> bool:
        if not self.enabled:
            return False
        if role in self.allow_roles:
            return True
        return self.bucket(user_id) < self.rollout_percent


class FlagStore:
    def __init__(self, flags: dict[str, Flag]):
        self._flags = flags

    @classmethod
    def from_file(cls, path: str | Path) -> "FlagStore":
        raw = json.loads(Path(path).read_text())
        flags = {
            name: Flag(name, cfg["enabled"], cfg.get("rollout_percent", 0), tuple(cfg.get("allow_roles", [])))
            for name, cfg in raw.items()
        }
        return cls(flags)

    def is_on(self, name: str, user_id: str, role: str = "subscriber") -> bool:
        flag = self._flags.get(name)
        return bool(flag and flag.is_on(user_id, role))  # unknown flags fail closed
