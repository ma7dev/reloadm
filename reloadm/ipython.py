"""Optional IPython line magic for explicit module reloading."""

from __future__ import annotations

import shlex
from typing import Protocol

from IPython.core.magic import Magics, line_magic, magics_class

from reloadm.main import ReloadResult, reload_many


class _IPythonShell(Protocol):
    def register_magics(self, magic: type[Magics]) -> None: ...


def _parse_line(line: str) -> tuple[tuple[str, ...], bool]:
    arguments = shlex.split(line)
    include_parents = False
    modules: list[str] = []
    for argument in arguments:
        if argument in {"-p", "--parents"}:
            include_parents = True
        elif argument.startswith("-"):
            raise ValueError(f"unknown option: {argument}")
        else:
            modules.append(argument)
    if not modules:
        raise ValueError("usage: %reloadm [--parents] MODULE [MODULE ...]")
    return tuple(modules), include_parents


@magics_class
class ReloadMagics(Magics):
    """Register the ``%reloadm`` line magic."""

    @line_magic
    def reloadm(self, line: str) -> ReloadResult:
        """Reload named modules, optionally followed by their package parents."""
        modules, include_parents = _parse_line(line)
        return reload_many(modules, verbose=True, include_parents=include_parents)


def load_ipython_extension(ipython: _IPythonShell) -> None:
    """Load ``reloadm.ipython`` with IPython's extension mechanism."""
    ipython.register_magics(ReloadMagics)
