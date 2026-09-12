"""Public module-reloading implementation."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from typing import Any, Callable, Union

ReloadTarget = Union[str, ModuleType, Callable[..., Any]]


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


def _resolve_module(target: ReloadTarget) -> ModuleType:
    if isinstance(target, str):
        if not target.strip():
            raise ValueError("module name must not be empty")
        try:
            return importlib.import_module(target)
        except (ImportError, ValueError) as exc:
            raise ReloadError(
                f"could not import module {target!r}", module_name=target
            ) from exc

    if isinstance(target, ModuleType):
        return target

    module_name = getattr(target, "__module__", None)
    if not isinstance(module_name, str) or module_name in {"builtins", "__main__"}:
        raise TypeError(
            "target must be a module, importable module name, or Python callable"
        )

    module = sys.modules.get(module_name)
    if module is not None:
        return module

    try:
        return importlib.import_module(module_name)
    except (ImportError, ValueError) as exc:
        raise ReloadError(
            f"could not import the module for {target!r}", module_name=module_name
        ) from exc


def _module_names(module_name: str, include_parents: bool) -> tuple[str, ...]:
    if not include_parents:
        return (module_name,)
    parts = module_name.split(".")
    return tuple(".".join(parts[:index]) for index in range(1, len(parts) + 1))


def reload(
    target: ReloadTarget,
    verbose: bool = False,
    *,
    include_parents: bool = True,
) -> ModuleType:
    """Reload the module that owns *target* and optionally its package parents.

    Args:
        target: A module object, importable module name, or Python callable.
        verbose: Print each module name before it is reloaded.
        include_parents: Reload package parents from outermost to innermost.

    Returns:
        The reloaded target module.

    Raises:
        TypeError: If *target* cannot identify a Python module.
        ValueError: If an empty module name is supplied.
        ReloadError: If the target cannot be imported or a module fails to reload.

    Note:
        Existing objects imported with ``from package import name`` are not rebound
        automatically. Re-import those names after calling this function.
    """
    module = _resolve_module(target)
    module_name = getattr(module, "__name__", "")
    if not module_name or module_name in {"builtins", "__main__"}:
        raise ReloadError(
            f"module {module_name or '<unknown>'!r} cannot be safely reloaded",
            module_name=module_name or None,
        )

    reloaded: list[str] = []
    result = module
    for name in _module_names(module_name, include_parents):
        try:
            current = sys.modules.get(name) or importlib.import_module(name)
            if verbose:
                print(f"Reloading {name}", file=sys.stderr)
            current = importlib.reload(current)
        except Exception as exc:
            raise ReloadError(
                f"failed to reload module {name!r}",
                module_name=name,
                reloaded=tuple(reloaded),
            ) from exc
        reloaded.append(name)
        if name == module_name:
            result = current

    return result
