"""Compare .env files against .env.example templates."""

__version__ = "0.1.0"

from .diff import DiffResult, compare
from .parser import EnvEntry, ParseError, parse_file, parse_text

__all__ = [
    "DiffResult",
    "EnvEntry",
    "ParseError",
    "compare",
    "parse_file",
    "parse_text",
    "__version__",
]
