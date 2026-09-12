import reloadm


def test_public_api() -> None:
    assert reloadm.__all__ == ["ReloadError", "ReloadTarget", "reload"]
    assert reloadm.__version__ == "0.2.0"
