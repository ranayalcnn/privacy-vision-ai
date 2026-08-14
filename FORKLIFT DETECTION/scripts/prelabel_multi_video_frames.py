from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs/ultralytics_config"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "runs/matplotlib_config"))

from ultralytics import YOLO


SOURCE = ROOT / "data/hard_examples_multi/selected_frames"
LABELS = ROOT / "data/hard_examples_multi/prelabels"
MODEL = ROOT / "models/forklift_yolo11n_hardclip_best.pt"


def main() -> None:
    model = YOLO(str(MODEL))
    images = sorted(SOURCE.rglob("*.jpg"))
    forklift_images = person_images = empty_images = 0
    chunk_size = 16
    for start in range(0, len(images), chunk_size):
        chunk = images[start : start + chunk_size]
        results = model.predict(
            [str(path) for path in chunk],
            classes=[0, 1],
            conf=0.30,
            iou=0.60,
            imgsz=512,
            device=0,
            batch=8,
            verbose=False,
        )
        for image_path, result in zip(chunk, results):
            relative = image_path.relative_to(SOURCE)
            label_path = LABELS / relative.parent / f"{image_path.stem}.txt"
            label_path.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            classes_present = set()
            if result.boxes is not None:
                for class_id, xywhn in zip(
                    result.boxes.cls.int().cpu().tolist(),
                    result.boxes.xywhn.cpu().tolist(),
                ):
                    x, y, w, h = xywhn
                    area = w * h
                    aspect = w / max(h, 1e-6)
                    if class_id == 0 and (
                        area > 0.38 or aspect < 0.22 or aspect > 2.8
                    ):
                        continue
                    if class_id == 1 and area > 0.22:
                        continue
                    lines.append(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
                    classes_present.add(class_id)
            label_path.write_text(
                "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
            )
            forklift_images += int(0 in classes_present)
            person_images += int(1 in classes_present)
            empty_images += int(not classes_present)
        print(f"processed={min(start + chunk_size, len(images))}/{len(images)}", flush=True)
    print(
        f"images={len(images)} forklift={forklift_images} "
        f"person={person_images} empty={empty_images}"
    )


if __name__ == "__main__":
    main()
