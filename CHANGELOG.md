# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-10-21

### Added
- `dotenv-diff` CLI comparing an env file against a template.
- Reports missing, extra, empty, and duplicate keys.
- `--strict`, `--allow-empty`, `--ignore`, `--format json`, `--no-color` options; honors `NO_COLOR`.
- Parser supporting comments, `export` prefix, quoted values, and inline comments.
- Python API: `parse_file`, `parse_text`, `compare`.
