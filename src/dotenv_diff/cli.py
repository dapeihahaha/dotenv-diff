"""Command-line interface: ``dotenv-diff [ENV] [TEMPLATE]``."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .diff import compare
from .parser import ParseError, duplicate_keys, parse_file

EXIT_OK = 0
EXIT_PROBLEMS = 1
EXIT_ERROR = 2


def _color(enabled: bool):
    def paint(code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if enabled else text

    return paint


def _symbols(stream) -> tuple:
    """Use ✓/✗ when the stream can encode them, else plain ASCII (e.g. cp1252 on Windows)."""
    try:
        "✓✗".encode(getattr(stream, "encoding", None) or "ascii")
        return "✓", "✗"
    except (UnicodeEncodeError, LookupError):
        return "OK", "FAIL"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dotenv-diff",
        description="Compare a .env file against .env.example and report missing, "
        "extra, and empty variables.",
    )
    p.add_argument("env", nargs="?", default=".env", help="env file (default: .env)")
    p.add_argument(
        "template",
        nargs="?",
        default=".env.example",
        help="template file (default: .env.example)",
    )
    p.add_argument(
        "--strict", action="store_true", help="also fail on keys not in the template"
    )
    p.add_argument(
        "--allow-empty", action="store_true", help="do not fail on empty values"
    )
    p.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="KEY",
        help="ignore a key (repeatable)",
    )
    p.add_argument(
        "--format", choices=["text", "json"], default="text", help="output format"
    )
    p.add_argument("--no-color", action="store_true", help="disable colored output")
    p.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    for path in (args.env, args.template):
        if not Path(path).is_file():
            print(f"dotenv-diff: file not found: {path}", file=sys.stderr)
            return EXIT_ERROR
    try:
        env = parse_file(args.env)
        template = parse_file(args.template)
    except ParseError as exc:
        print(f"dotenv-diff: {exc}", file=sys.stderr)
        return EXIT_ERROR

    result = compare(env, template, ignore=args.ignore)
    failed = result.has_problems(strict=args.strict, allow_empty=args.allow_empty)
    dupes = duplicate_keys(Path(args.env).read_text(encoding="utf-8"))

    if args.format == "json":
        payload = result.to_dict()
        payload["duplicates"] = dupes
        payload["ok"] = not failed
        print(json.dumps(payload, indent=2))
        return EXIT_PROBLEMS if failed else EXIT_OK

    use_color = not args.no_color and sys.stdout.isatty() and "NO_COLOR" not in os.environ
    paint = _color(use_color)
    sections = [
        ("Missing", result.missing, "31", True),
        ("Empty", result.empty, "33", not args.allow_empty),
        ("Extra", result.extra, "36", args.strict),
        ("Duplicate", dupes, "35", False),
    ]
    for title, keys, code, fatal in sections:
        if not keys:
            continue
        label = title if fatal else f"{title} (warning)"
        print(paint(code, f"{label}: {len(keys)}"))
        for key in keys:
            print(f"  - {key}")

    ok_mark, fail_mark = _symbols(sys.stdout)
    if failed:
        print(paint("31", f"{fail_mark} {args.env} does not match {args.template}"))
        return EXIT_PROBLEMS
    print(paint("32", f"{ok_mark} {args.env} matches {args.template}"))
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
