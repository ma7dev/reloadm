# Changelog

All notable changes are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/).

## Unreleased

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
