# Contributing

Thanks for helping out!

## Development setup

```bash
git clone https://github.com/dapeihahaha/dotenv-diff
cd dotenv-diff
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest
pytest
```

## Pull requests

- Keep changes focused; one feature or fix per PR.
- Add or update tests in `tests/` for any behavior change.
- Add a line under **Unreleased** in `CHANGELOG.md`.
- The project has no runtime dependencies — please keep it that way.

## Reporting bugs

Open an issue with the smallest `.env` / `.env.example` pair that reproduces the problem, the command you ran, and the output you expected.
