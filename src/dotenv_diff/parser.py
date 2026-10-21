"""A small, dependency-free parser for .env files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


@dataclass
class EnvEntry:
    key: str
    value: str
    line: int


class ParseError(ValueError):
    def __init__(self, path: str, line: int, message: str) -> None:
        super().__init__(f"{path}:{line}: {message}")
        self.path = path
        self.line = line


def _strip_inline_comment(value: str) -> str:
    # An unquoted value ends at " #" (a hash preceded by whitespace).
    match = re.search(r"\s+#", value)
    if match:
        value = value[: match.start()]
    return value.strip()


def _parse_value(raw: str, path: str, lineno: int) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    quote = raw[0]
    if quote in ("'", '"'):
        end = raw.find(quote, 1)
        if end == -1:
            raise ParseError(path, lineno, "unterminated quoted value")
        value = raw[1:end]
        if quote == '"':
            value = (
                value.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')
            )
        return value
    return _strip_inline_comment(raw)


def parse_text(text: str, path: str = "<string>") -> Dict[str, EnvEntry]:
    """Parse .env content into an ordered mapping of key -> EnvEntry.

    Supports comments, blank lines, an optional ``export`` prefix, and
    single- or double-quoted values. Later duplicates override earlier ones.
    """
    entries: Dict[str, EnvEntry] = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].lstrip()
        if "=" not in stripped:
            raise ParseError(path, lineno, f"expected KEY=VALUE, got {stripped!r}")
        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        if not _KEY_RE.match(key):
            raise ParseError(path, lineno, f"invalid key {key!r}")
        entries[key] = EnvEntry(key, _parse_value(raw_value, path, lineno), lineno)
    return entries


def parse_file(path: str) -> Dict[str, EnvEntry]:
    return parse_text(Path(path).read_text(encoding="utf-8"), path=path)


def duplicate_keys(text: str) -> List[str]:
    """Return keys that are defined more than once, in first-seen order."""
    seen: Dict[str, int] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].lstrip()
        key = stripped.split("=", 1)[0].strip()
        seen[key] = seen.get(key, 0) + 1
    return [k for k, n in seen.items() if n > 1]
