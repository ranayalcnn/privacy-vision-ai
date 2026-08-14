from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs/ultralytics_config"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "runs/matplotlib_config"))

from ultralytics import YOLO


def main() -> None:
    model = YOLO(str(ROOT / "models/forklift_yolo11n_quick_best.pt"))
    model.train(
        data=str(ROOT / "data/processed/data.yaml"),
        epochs=10,
        imgsz=512,
        batch=8,
        device=0,
        workers=2,
        patience=5,
        seed=42,
        deterministic=True,
        pretrained=False,
        cache=False,
        lr0=0.001,
        close_mosaic=5,
        project=str(ROOT / "runs"),
        name="forklift_hardclip_finetune",
        exist_ok=True,
        plots=True,
        amp=True,
    )


if __name__ == "__main__":
    main()
