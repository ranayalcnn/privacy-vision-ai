from __future__ import annotations

import os
from pathlib import Path
from threading import Lock
from typing import Any

from api.config import settings


class LazyYoloModel:
    """Load one Ultralytics model on first use and then reuse it."""

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self._model: Any | None = None
        self._lock = Lock()
        self._inference_lock = Lock()

    def get(self) -> Any:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    if not self.model_path.is_file():
                        raise FileNotFoundError(
                            f"Model dosyası bulunamadı: {self.model_path}"
                        )
                    yolo_config_dir = settings.runtime_dir / "ultralytics"
                    yolo_config_dir.mkdir(parents=True, exist_ok=True)
                    os.environ.setdefault("YOLO_CONFIG_DIR", str(yolo_config_dir))
                    matplotlib_config_dir = settings.runtime_dir / "matplotlib"
                    matplotlib_config_dir.mkdir(parents=True, exist_ok=True)
                    os.environ.setdefault(
                        "MPLCONFIGDIR",
                        str(matplotlib_config_dir),
                    )
                    from ultralytics import YOLO

                    self._model = YOLO(str(self.model_path))
        return self._model

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        """Serialize predictions because one YOLO instance is shared by requests."""
        model = self.get()
        with self._inference_lock:
            return model.predict(*args, **kwargs)

    def track(self, *args: Any, **kwargs: Any) -> Any:
        """Run a stateful Ultralytics tracker without overlapping frames."""
        model = self.get()
        with self._inference_lock:
            return model.track(*args, **kwargs)

    def reset_tracking(self) -> None:
        """Clear tracker state before starting a different camera or video."""
        model = self.get()
        with self._inference_lock:
            model.predictor = None
