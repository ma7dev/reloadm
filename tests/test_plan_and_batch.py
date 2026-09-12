from __future__ import annotations

import sys
from types import ModuleType

import pytest

import reloadm.main
from reloadm import ReloadResult, plan, reload_many


def test_plan_is_side_effect_free_and_orders_children_first() -> None:
    result = plan(
        ["example.alpha.feature", "example.beta.feature"], include_parents=True
    )

    assert result.requested == ("example.alpha.feature", "example.beta.feature")
    assert result.modules == (
        "example.alpha.feature",
        "example.beta.feature",
        "example.alpha",
        "example.beta",
        "example",
    )
    assert "example.alpha.feature" not in sys.modules


def test_plan_deduplicates_targets_and_shared_parents() -> None:
    result = plan(["example.feature", "example.feature"], include_parents=True)

    assert result.requested == ("example.feature", "example.feature")
    assert result.modules == ("example.feature", "example")


def test_plan_orders_explicit_parent_after_child() -> None:
    result = plan(["example", "example.feature"], include_parents=True)

    assert result.requested == ("example", "example.feature")
    assert result.modules == ("example.feature", "example")


def test_plan_requires_at_least_one_target() -> None:
    with pytest.raises(ValueError, match="at least one"):
        plan([])


def test_reload_many_returns_report(monkeypatch: pytest.MonkeyPatch) -> None:
    modules = {
        name: ModuleType(name) for name in ("example", "example.alpha", "example.beta")
    }
    for name, module in modules.items():
        module.__file__ = f"/{name.replace('.', '/')}.py"
        monkeypatch.setitem(sys.modules, name, module)

    seen: list[str] = []

    def fake_reload(module: ModuleType) -> ModuleType:
        seen.append(module.__name__)
        return module

    monkeypatch.setattr(reloadm.main.importlib, "reload", fake_reload)

    result = reload_many(
        [modules["example.alpha"], modules["example.beta"]], include_parents=True
    )

    assert isinstance(result, ReloadResult)
    assert result.requested == ("example.alpha", "example.beta")
    assert result.planned == ("example.alpha", "example.beta", "example")
    assert result.reloaded == result.planned
    assert seen == list(result.planned)
    assert result.duration_seconds >= 0
    assert dict(result.target_files)["example.alpha"].endswith("example/alpha.py")


def test_reload_many_imports_missing_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    child = ModuleType("example.feature")
    parent = ModuleType("example")
    monkeypatch.setitem(sys.modules, child.__name__, child)
    monkeypatch.delitem(sys.modules, parent.__name__, raising=False)
    monkeypatch.setattr(
        reloadm.main.importlib,
        "import_module",
        lambda name: parent if name == "example" else child,
    )
    monkeypatch.setattr(reloadm.main.importlib, "reload", lambda module: module)

    result = reload_many(child, include_parents=True)

    assert result.reloaded == ("example.feature", "example")
