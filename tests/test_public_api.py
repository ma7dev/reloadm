import reloadm


def test_public_api() -> None:
    assert reloadm.__all__ == [
        "ReloadError",
        "ReloadPlan",
        "ReloadResult",
        "ReloadTarget",
        "plan",
        "reload",
        "reload_many",
    ]
    assert reloadm.__version__ == "0.3.0"
