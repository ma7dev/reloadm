"""Reload Python modules during interactive development."""

from importlib.metadata import PackageNotFoundError, version

from reloadm.main import (
    ReloadError,
    ReloadPlan,
    ReloadResult,
    ReloadTarget,
    plan,
    reload,
    reload_many,
)

__all__ = [
    "ReloadError",
    "ReloadPlan",
    "ReloadResult",
    "ReloadTarget",
    "plan",
    "reload",
    "reload_many",
]

try:
    __version__ = version("reloadm")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0.0.0+unknown"
