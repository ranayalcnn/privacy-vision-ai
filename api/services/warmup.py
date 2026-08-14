from __future__ import annotations

from threading import Lock, Thread

import numpy as np

from api.services.forklift import forklift_service
from api.services.people import people_service
from api.services.pose import pose_service
from api.services.privacy import privacy_service


class ModelWarmupManager:
    """Warm inference models in the background without delaying API startup."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._started = False
        self._models = {
            "privacy": "pending",
            "people": "pending",
            "pose": "pending",
            "forklift": "pending",
        }

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._started = True
        Thread(target=self._run, name="model-warmup", daemon=True).start()

    def _run(self) -> None:
        image = np.zeros((320, 320, 3), dtype=np.uint8)
        tasks = {
            "privacy": lambda: privacy_service._model.predict(
                image,
                conf=0.30,
                imgsz=320,
                max_det=1,
                verbose=False,
            ),
            "people": lambda: people_service._model.predict(
                image,
                classes=[0],
                conf=0.25,
                imgsz=320,
                max_det=1,
                verbose=False,
            ),
            "pose": lambda: pose_service._model.predict(
                image,
                conf=0.25,
                imgsz=320,
                max_det=1,
                verbose=False,
            ),
            "forklift": lambda: forklift_service._model.predict(
                image,
                conf=0.25,
                imgsz=320,
                max_det=1,
                verbose=False,
            ),
        }
        for name, task in tasks.items():
            self._set(name, "loading")
            try:
                task()
            except Exception:
                self._set(name, "error")
            else:
                self._set(name, "ready")

    def _set(self, name: str, status: str) -> None:
        with self._lock:
            self._models[name] = status

    def status(self) -> dict:
        with self._lock:
            models = dict(self._models)
            started = self._started
        ready = sum(value == "ready" for value in models.values())
        errors = sum(value == "error" for value in models.values())
        overall = (
            "ready"
            if ready == len(models)
            else "error"
            if errors
            else "warming"
            if started
            else "pending"
        )
        return {
            "status": overall,
            "ready": ready,
            "total": len(models),
            "models": models,
        }


model_warmup_manager = ModelWarmupManager()
