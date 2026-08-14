from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs/ultralytics_config"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "runs/matplotlib_config"))

from ultralytics import YOLO


if __name__ == "__main__":
    YOLO(str(ROOT / "runs/forklift_hardclip_finetune/weights/last.pt")).train(resume=True)
