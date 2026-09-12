"""Public module-reloading implementation."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from importlib.machinery import ExtensionFileLoader
from pathlib import Path
from time import perf_counter
from types import ModuleType
from typing import Any

ReloadTarget = str | ModuleType | Callable[..., Any]


class ReloadError(RuntimeError):
    """Raised when reloadm cannot safely resolve or reload a target."""

    def __init__(
        self,
        message: str,
        *,
        module_name: str | None = None,
        reloaded: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.module_name = module_name
        self.reloaded = reloaded


@dataclass(frozen=True)
class ReloadPlan:
    """A side-effect-free description of the requested reload order."""

    requested: tuple[str, ...]
    modules: tuple[str, ...]


@dataclass(frozen=True)
class ReloadResult:
    """Details from a completed multi-module reload."""

    requested: tuple[str, ...]
    planned: tuple[str, ...]
    reloaded: tuple[str, ...]
    target_files: tuple[tuple[str, str | None], ...]
    duration_seconds: float


def _module_name(target: ReloadTarget) -> str:
    if isinstance(target, str):
        name = target.strip()
        if not name:
            raise ValueError("module name must not be empty")
        return name

    if isinstance(target, ModuleType):
        name = getattr(target, "__name__", "")
        if name:
            return name
        raise ReloadError(
            "module '<unknown>' cannot be safely reloaded", module_name=None
        )

    module_name = getattr(target, "__module__", None)
    if isinstance(module_name, str) and module_name not in {"builtins", "__main__"}:
        return module_name

    raise TypeError(
        "target must be a module, importable module name, or Python callable"
    )


def _resolve_module(target: ReloadTarget) -> ModuleType:
    name = _module_name(target)
    if name in {"builtins", "__main__"}:
        raise ReloadError(
            f"module {name!r} cannot be safely reloaded", module_name=name
        )

    if isinstance(target, ModuleType):
        return target

    module = sys.modules.get(name)
    if module is not None:
        return module

    try:
        return importlib.import_module(name)
    except (ImportError, ValueError) as exc:
        raise ReloadError(
            f"could not import module {name!r}", module_name=name
        ) from exc


def _parent_names(module_name: str) -> tuple[str, ...]:
    parts = module_name.split(".")
    return tuple(".".join(parts[:index]) for index in range(len(parts) - 1, 0, -1))


def _normalize_targets(
    targets: ReloadTarget | Iterable[ReloadTarget],
) -> tuple[ReloadTarget, ...]:
    if isinstance(targets, (str, ModuleType)) or callable(targets):
        return (targets,)
    normalized = tuple(targets)
    if not normalized:
        raise ValueError("at least one reload target is required")
    return normalized


def plan(
    targets: ReloadTarget | Iterable[ReloadTarget],
    *,
    include_parents: bool = False,
) -> ReloadPlan:
    """Return the reload order without importing or reloading any module.

    Targets are scheduled first. When ``include_parents`` is enabled, unique
    parents follow from nearest to outermost so package re-exports see the new
    child definitions.
    """
    requested = tuple(_module_name(target) for target in _normalize_targets(targets))
    target_names = tuple(dict.fromkeys(requested))
    if not include_parents:
        return ReloadPlan(requested=requested, modules=target_names)

    candidates = list(target_names)
    for target_name in target_names:
        candidates.extend(_parent_names(target_name))
    unique = tuple(dict.fromkeys(candidates))
    child_first = tuple(sorted(unique, key=lambda name: -name.count(".")))
    return ReloadPlan(
        requested=requested,
        modules=child_first,
    )


def _target_file(module: ModuleType) -> str | None:
    raw = getattr(module, "__file__", None)
    return str(Path(raw).resolve()) if isinstance(raw, str) else None


def _ensure_reloadable(module: ModuleType) -> None:
    spec = getattr(module, "__spec__", None)
    loader = getattr(spec, "loader", None)
    origin = getattr(spec, "origin", None)
    if isinstance(loader, ExtensionFileLoader) or origin == "built-in":
        raise ReloadError(
            f"extension module {module.__name__!r} cannot be safely reloaded",
            module_name=module.__name__,
        )


def reload_many(
    targets: ReloadTarget | Iterable[ReloadTarget],
    verbose: bool = False,
    *,
    include_parents: bool = False,
) -> ReloadResult:
    """Reload one or more targets and return a structured execution report."""
    normalized = _normalize_targets(targets)
    reload_plan = plan(normalized, include_parents=include_parents)

    resolved: dict[str, ModuleType] = {}
    for target in normalized:
        module = _resolve_module(target)
        resolved[module.__name__] = module

    reloaded: list[str] = []
    files: list[tuple[str, str | None]] = []
    started = perf_counter()
    for name in reload_plan.modules:
        try:
            current = resolved.get(name) or sys.modules.get(name)
            if current is None:
                current = importlib.import_module(name)
            _ensure_reloadable(current)
            if verbose:
                print(f"Reloading {name}", file=sys.stderr)
            current = importlib.reload(current)
        except ReloadError as exc:
            raise ReloadError(
                str(exc),
                module_name=exc.module_name,
                reloaded=tuple(reloaded),
            ) from exc
        except Exception as exc:
            raise ReloadError(
                f"failed to reload module {name!r}",
                module_name=name,
                reloaded=tuple(reloaded),
            ) from exc
        resolved[name] = current
        reloaded.append(name)
        files.append((name, _target_file(current)))

    return ReloadResult(
        requested=reload_plan.requested,
        planned=reload_plan.modules,
        reloaded=tuple(reloaded),
        target_files=tuple(files),
        duration_seconds=perf_counter() - started,
    )


def reload(
    target: ReloadTarget,
    verbose: bool = False,
    *,
    include_parents: bool = False,
) -> ModuleType:
    """Reload the module that owns *target* and optionally its package parents.

    Parent cascading is opt-in because package initializers can have side
    effects. When enabled, the target is reloaded first and parents follow from
    nearest to outermost, repairing common package-level re-exports.
    """
    module = _resolve_module(target)
    reload_many(module, verbose=verbose, include_parents=include_parents)
    return sys.modules.get(module.__name__, module)
