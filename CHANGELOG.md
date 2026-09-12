# Changelog

All notable changes are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/).

## Unreleased

## 0.3.0 - 2026-09-12

### Added

- Side-effect-free reload planning with `plan` and `ReloadPlan`.
- Deduplicated batch execution with `reload_many` and `ReloadResult`.
- Optional `%reloadm` IPython magic.
- Real-package integration tests and an executable example notebook.
- Python 3.14 support.

### Changed

- Parent cascading is now opt-in.
- Cascades reload children before parents so package re-exports are refreshed.
- Runtime version reporting now comes from installed package metadata.
- Minimum supported Python is now 3.10; Python 3.9 is end-of-life.

## 0.2.0 - 2026-09-12

### Added

- Module names and Python callables as reload targets.
- `include_parents` control for package-chain reloading.
- Typed public API and structured `ReloadError` diagnostics.
- Tests across supported Python versions and package build verification.
- Usage and API documentation.

### Changed

- Supported Python range is now 3.9 through 3.13.
- Development tooling now uses PEP 621 metadata and pinned dependencies.

### Removed

- Stale notebook and insecure password-based publishing workflow.

## 0.1.0 - 2022-04-24

### Added

- Initial module and function reloading helper.
