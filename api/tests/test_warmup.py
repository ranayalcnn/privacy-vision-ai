from __future__ import annotations

from api.services.warmup import ModelWarmupManager


def test_warmup_manager_reports_progress() -> None:
    manager = ModelWarmupManager()

    initial = manager.status()
    assert initial["status"] == "pending"
    assert initial["ready"] == 0
    assert initial["total"] == 4

    manager._started = True
    manager._set("privacy", "ready")
    progress = manager.status()
    assert progress["status"] == "warming"
    assert progress["ready"] == 1


def test_warmup_manager_reports_ready_and_error() -> None:
    manager = ModelWarmupManager()
    manager._started = True
    for name in ("privacy", "people", "pose", "forklift"):
        manager._set(name, "ready")

    assert manager.status()["status"] == "ready"

    manager._set("pose", "error")
    status = manager.status()
    assert status["status"] == "error"
    assert status["models"]["pose"] == "error"
