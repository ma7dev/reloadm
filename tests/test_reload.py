from __future__ import annotations

import math
import sys
from types import ModuleType
from typing import Any

import pytest

import reloadm.main
from reloadm import ReloadError, reload


def test_reload_module_then_parents_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    modules = {
        name: ModuleType(name)
        for name in ("example", "example.tools", "example.tools.math")
    }
    monkeypatch.setattr(reloadm.main.importlib, "import_module", modules.__getitem__)
    monkeypatch.setattr(reloadm.main.sys, "modules", modules)
    seen = []

    def fake_reload(module: ModuleType) -> ModuleType:
        seen.append(module.__name__)
        return module

    monkeypatch.setattr(reloadm.main.importlib, "reload", fake_reload)

    result = reload(modules["example.tools.math"], include_parents=True)

    assert result is modules["example.tools.math"]
    assert seen == ["example.tools.math", "example.tools", "example"]


def test_reload_only_target(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("example.feature")
    monkeypatch.setitem(sys.modules, module.__name__, module)
    seen = []

    def fake_reload(current: ModuleType) -> ModuleType:
        seen.append(current.__name__)
        return current

    monkeypatch.setattr(reloadm.main.importlib, "reload", fake_reload)

    assert reload(module) is module
    assert seen == ["example.feature"]


def test_resolves_module_name(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("named_module")
    monkeypatch.setattr(reloadm.main.importlib, "import_module", lambda name: module)
    monkeypatch.setattr(reloadm.main.importlib, "reload", lambda current: current)

    assert reload("named_module") is module


def test_resolves_callable_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("callable_owner")

    def target() -> None:
        pass

    target.__module__ = module.__name__
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(reloadm.main.importlib, "reload", lambda current: current)

    assert reload(target, include_parents=False) is module


def test_resolves_class_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("class_owner")

    class Target:
        pass

    Target.__module__ = module.__name__
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(reloadm.main.importlib, "reload", lambda current: current)

    assert reload(Target) is module


def test_resolves_bound_method_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("method_owner")

    class Target:
        def method(self) -> None:
            pass

    Target.__module__ = module.__name__
    Target.method.__module__ = module.__name__
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(reloadm.main.importlib, "reload", lambda current: current)

    assert reload(Target().method) is module


def test_imports_callable_owner_when_not_loaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = ModuleType("lazy_owner")

    def target() -> None:
        pass

    target.__module__ = module.__name__
    monkeypatch.delitem(sys.modules, module.__name__, raising=False)
    monkeypatch.setattr(reloadm.main.importlib, "import_module", lambda name: module)
    monkeypatch.setattr(reloadm.main.importlib, "reload", lambda current: current)

    assert reload(target, include_parents=False) is module


def test_wraps_callable_owner_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def target() -> None:
        pass

    target.__module__ = "missing_owner"
    monkeypatch.delitem(sys.modules, target.__module__, raising=False)

    def fail_import(name: str) -> ModuleType:
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(reloadm.main.importlib, "import_module", fail_import)

    with pytest.raises(ReloadError) as caught:
        reload(target)

    assert caught.value.module_name == "missing_owner"


def test_verbose_reports_reloaded_module(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = ModuleType("verbose_module")
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(reloadm.main.importlib, "reload", lambda current: current)

    reload(module, verbose=True, include_parents=False)

    assert capsys.readouterr().err == "Reloading verbose_module\n"


@pytest.mark.parametrize("target", [None, 42, object(), len])
def test_rejects_targets_without_python_module(target: Any) -> None:
    with pytest.raises(TypeError, match="target must be"):
        reload(target)  # type: ignore[arg-type]


def test_rejects_empty_module_name() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        reload("  ")


def test_wraps_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_import(name: str) -> ModuleType:
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(reloadm.main.importlib, "import_module", fail_import)

    with pytest.raises(ReloadError) as caught:
        reload("missing.module")

    assert caught.value.module_name == "missing.module"
    assert isinstance(caught.value.__cause__, ModuleNotFoundError)


def test_reports_partial_parent_reload(monkeypatch: pytest.MonkeyPatch) -> None:
    modules = {name: ModuleType(name) for name in ("example", "example.feature")}
    monkeypatch.setattr(reloadm.main.importlib, "import_module", modules.__getitem__)
    monkeypatch.setattr(reloadm.main.sys, "modules", modules)

    def fake_reload(module: ModuleType) -> ModuleType:
        if module.__name__ == "example":
            raise RuntimeError("broken source")
        return module

    monkeypatch.setattr(reloadm.main.importlib, "reload", fake_reload)

    with pytest.raises(ReloadError) as caught:
        reload(modules["example.feature"], include_parents=True)

    assert caught.value.module_name == "example"
    assert caught.value.reloaded == ("example.feature",)
    assert isinstance(caught.value.__cause__, RuntimeError)


@pytest.mark.parametrize("name", ["builtins", "__main__", ""])
def test_rejects_unsafe_module(name: str) -> None:
    module = ModuleType(name)
    with pytest.raises(ReloadError, match="cannot be safely reloaded"):
        reload(module)


def test_rejects_extension_module() -> None:
    with pytest.raises(ReloadError, match="extension module"):
        reload(math)
