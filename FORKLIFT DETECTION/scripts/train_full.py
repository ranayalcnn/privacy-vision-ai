"""Run the full YOLO11n baseline training."""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs" / "ultralytics_config"))

from ultralytics import YOLO  # noqa: E402


def main() -> None:
    model = YOLO(str(ROOT / "models" / "forklift_yolo11n_quick_best.pt"))
    model.train(
        data=str(ROOT / "data" / "processed" / "data.yaml"),
        epochs=20,
        fraction=0.50,
        imgsz=416,
        batch=8,
        device=0,
        workers=2,
        patience=8,
        seed=42,
        deterministic=True,
        pretrained=False,
        cache=False,
        project=str(ROOT / "runs"),
        name="forklift_yolo11n_20epoch",
        exist_ok=True,
        plots=True,
        amp=True,
    )


if __name__ == "__main__":
    main()
