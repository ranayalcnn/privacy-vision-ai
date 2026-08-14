"""Run the selected forklift model on the sample video."""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs" / "ultralytics_config"))

from ultralytics import YOLO  # noqa: E402


def main() -> None:
    model = YOLO(str(ROOT / "models" / "forklift_yolo11n_quick_best.pt"))
    model.predict(
        source=str(ROOT / "samples" / "forklift_warehouse_pexels.mp4"),
        imgsz=512,
        conf=0.25,
        iou=0.7,
        device=0,
        save=True,
        save_txt=False,
        project=str(ROOT / "outputs"),
        name="forklift_video_detection",
        exist_ok=True,
        stream=False,
        verbose=False,
    )


if __name__ == "__main__":
    main()
