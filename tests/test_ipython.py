from __future__ import annotations

import pytest

import reloadm.ipython
from reloadm import ReloadResult
from reloadm.ipython import ReloadMagics, _parse_line, load_ipython_extension


def test_parse_ipython_magic() -> None:
    assert _parse_line("--parents package.one package.two") == (
        ("package.one", "package.two"),
        True,
    )


def test_parse_ipython_magic_rejects_unknown_option() -> None:
    with pytest.raises(ValueError, match="unknown option"):
        _parse_line("--unknown package")


def test_parse_ipython_magic_requires_module() -> None:
    with pytest.raises(ValueError, match="usage"):
        _parse_line("--parents")


def test_ipython_magic_executes_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = ReloadResult(
        requested=("package.one",),
        planned=("package.one", "package"),
        reloaded=("package.one", "package"),
        target_files=(),
        duration_seconds=0.1,
    )
    seen: dict[str, object] = {}

    def fake_reload_many(
        targets: tuple[str, ...], verbose: bool, *, include_parents: bool
    ) -> ReloadResult:
        seen.update(
            targets=targets,
            verbose=verbose,
            include_parents=include_parents,
        )
        return expected

    monkeypatch.setattr(reloadm.ipython, "reload_many", fake_reload_many)

    result = ReloadMagics(shell=None).reloadm("--parents package.one")

    assert result is expected
    assert seen == {
        "targets": ("package.one",),
        "verbose": True,
        "include_parents": True,
    }


def test_load_ipython_extension_registers_magics() -> None:
    registered: list[type[ReloadMagics]] = []

    class Shell:
        def register_magics(self, magic: type[ReloadMagics]) -> None:
            registered.append(magic)

    load_ipython_extension(Shell())

    assert registered == [ReloadMagics]
