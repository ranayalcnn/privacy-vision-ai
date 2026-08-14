"""Run a short YOLO11n smoke-test training on the prepared dataset."""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs" / "ultralytics_config"))

from ultralytics import YOLO  # noqa: E402


def main() -> None:
    model = YOLO("yolo11n.pt")
    model.train(
        data=str(ROOT / "data" / "processed" / "data.yaml"),
        epochs=5,
        fraction=0.10,
        imgsz=512,
        batch=4,
        device=0,
        workers=2,
        patience=5,
        seed=42,
        deterministic=True,
        pretrained=True,
        cache=False,
        project=str(ROOT / "runs"),
        name="forklift_yolo11n_smoke",
        exist_ok=True,
        plots=True,
        amp=True,
    )


if __name__ == "__main__":
    main()
