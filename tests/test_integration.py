from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

from reloadm import ReloadError, reload


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    stat = path.stat()
    os.utime(path, (stat.st_atime, stat.st_mtime + 2))
    importlib.invalidate_caches()


def _forget_package(name: str) -> None:
    for module_name in tuple(sys.modules):
        if module_name == name or module_name.startswith(f"{name}."):
            sys.modules.pop(module_name, None)


def test_parent_cascade_repairs_package_reexport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "reloadm_fixture"
    package.mkdir()
    _write(package / "__init__.py", "from .feature import value\n")
    _write(package / "feature.py", "value = 1\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    parent = importlib.import_module("reloadm_fixture")
    child = importlib.import_module("reloadm_fixture.feature")
    try:
        _write(package / "feature.py", "value = 222\n")
        reload(child, include_parents=True)

        assert child.value == 222
        assert parent.value == 222
    finally:
        _forget_package("reloadm_fixture")


def test_parent_initializers_are_not_rerun_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "reloadm_safe_default"
    package.mkdir()
    _write(package / "__init__.py", "runs = globals().get('runs', 0) + 1\n")
    _write(package / "feature.py", "value = 1\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    parent = importlib.import_module("reloadm_safe_default")
    child = importlib.import_module("reloadm_safe_default.feature")
    try:
        reload(child)
        assert parent.runs == 1
    finally:
        _forget_package("reloadm_safe_default")


def test_syntax_error_preserves_original_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "reloadm_broken"
    package.mkdir()
    _write(package / "__init__.py", "")
    _write(package / "feature.py", "value = 1\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    child = importlib.import_module("reloadm_broken.feature")
    try:
        _write(package / "feature.py", "this is not valid python !!!\n")
        with pytest.raises(ReloadError) as caught:
            reload(child)

        assert caught.value.module_name == "reloadm_broken.feature"
        assert caught.value.reloaded == ()
        assert isinstance(caught.value.__cause__, SyntaxError)
    finally:
        _forget_package("reloadm_broken")


def test_namespace_package_can_be_reloaded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "reloadm_namespace"
    package.mkdir()
    _write(package / "feature.py", "value = 1\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    namespace = importlib.import_module("reloadm_namespace")
    try:
        assert reload(namespace) is namespace
    finally:
        _forget_package("reloadm_namespace")
