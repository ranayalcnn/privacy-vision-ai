from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs/ultralytics_config"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "runs/matplotlib_config"))

from ultralytics import YOLO


if __name__ == "__main__":
    model = YOLO(str(ROOT / "models/yolo11s.pt"))
    model.train(
        data=str(ROOT / "data/processed/data.yaml"),
        epochs=8,
        fraction=0.50,
        imgsz=512,
        batch=4,
        device=0,
        workers=2,
        patience=5,
        seed=42,
        deterministic=True,
        amp=True,
        cache=False,
        close_mosaic=5,
        project=str(ROOT / "runs"),
        name="forklift_yolo11s_multivideo_fast",
        exist_ok=True,
        plots=True,
    )
