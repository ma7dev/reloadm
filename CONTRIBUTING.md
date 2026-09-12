# Contributing

## Set up

Install the locked development environment with
[uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked --all-extras
```

## Verify a change

Run the same checks as CI:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m build
uv run python -m twine check dist/*
```

Add tests for behavior changes and update `CHANGELOG.md` for user-visible
changes. Keep the package dependency-free unless a dependency clearly improves
the small public API.

## Releases

There is deliberately no automatic publishing workflow while this repository
and its distribution policy are private. A future PyPI release should use a
protected GitHub environment and PyPI Trusted Publishing (OIDC), never stored
username/password or API-token secrets.
