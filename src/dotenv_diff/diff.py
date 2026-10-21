"""Compare an actual .env file against a template such as .env.example."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .parser import EnvEntry


@dataclass
class DiffResult:
    missing: List[str] = field(default_factory=list)
    extra: List[str] = field(default_factory=list)
    empty: List[str] = field(default_factory=list)

    def has_problems(self, strict: bool = False, allow_empty: bool = False) -> bool:
        if self.missing:
            return True
        if strict and self.extra:
            return True
        if not allow_empty and self.empty:
            return True
        return False

    def to_dict(self) -> Dict[str, List[str]]:
        return {"missing": self.missing, "extra": self.extra, "empty": self.empty}


def compare(
    env: Dict[str, EnvEntry],
    template: Dict[str, EnvEntry],
    ignore: List[str] = None,
) -> DiffResult:
    """Return which template keys are missing/empty in env and which env keys are extra."""
    ignored = set(ignore or [])
    result = DiffResult()
    for key in template:
        if key in ignored:
            continue
        if key not in env:
            result.missing.append(key)
        elif env[key].value == "":
            result.empty.append(key)
    for key in env:
        if key not in ignored and key not in template:
            result.extra.append(key)
    return result
