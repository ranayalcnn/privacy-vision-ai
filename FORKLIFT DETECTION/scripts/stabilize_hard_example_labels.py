from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/hard_examples/forklift_warehouse_8s_15s"
SOURCE = BASE / "images"
LABELS = BASE / "labels_final"
PREVIEWS = BASE / "previews_final"
REPORT = ROOT / "reports/hard_example_auto_labels.json"
CONTACT = ROOT / "reports/hard_example_final_labels_contact_sheet.jpg"


def cv_write(path: Path, image: np.ndarray) -> None:
    ok, encoded = cv2.imencode(path.suffix, image)
    if not ok:
        raise RuntimeError(f"Could not encode {path}")
    encoded.tofile(path)


def yolo_line(class_id: int, box: list[float], width: int, height: int) -> str:
    x1, y1, x2, y2 = box
    return (
        f"{class_id} {((x1+x2)/2)/width:.6f} {((y1+y2)/2)/height:.6f} "
        f"{(x2-x1)/width:.6f} {(y2-y1)/height:.6f}"
    )


def main() -> None:
    LABELS.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    records = json.loads(REPORT.read_text(encoding="utf-8"))
    forklift_boxes = [
        next(item["box"] for item in record["detections"] if item["class_id"] == 0)
        for record in records
    ]
    person_boxes = [
        next(item["box"] for item in record["detections"] if item["class_id"] == 1)
        for record in records
    ]

    previews = []
    for index, record in enumerate(records):
        image_path = SOURCE / record["image"]
        width, height = Image.open(image_path).size
        person = person_boxes[index]
        # In this fixed-camera clip the operator remains in the forklift cabin.
        # Grounding DINO finds the operator reliably but sometimes confuses pallet
        # columns with the mast. Anchor a consistent full-vehicle box to the cabin.
        box = [
            max(0, person[0] - 0.075 * width),
            0.14 * height,
            min(width, person[2] + 0.12 * width),
            height,
        ]
        lines = [yolo_line(0, box, width, height), yolo_line(1, person, width, height)]
        (LABELS / f"{image_path.stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

        canvas = cv2.cvtColor(np.asarray(Image.open(image_path).convert("RGB")), cv2.COLOR_RGB2BGR)
        for class_name, selected, color in (
            ("forklift", box, (0, 220, 0)),
            ("person", person, (0, 180, 255)),
        ):
            x1, y1, x2, y2 = map(int, selected)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 3)
            cv2.putText(canvas, class_name, (x1, max(25, y1 - 7)), 0, 0.65, color, 2)
        preview_path = PREVIEWS / image_path.name
        cv_write(preview_path, canvas)
        previews.append(cv2.resize(canvas, (320, 180)))

    rows = []
    for start in range(0, len(previews), 6):
        row = previews[start : start + 6]
        row += [np.full((180, 320, 3), 255, np.uint8)] * (6 - len(row))
        rows.append(cv2.hconcat(row))
    cv_write(CONTACT, cv2.vconcat(rows))
    print(f"Stabilized {len(records)} labels: {CONTACT}")


if __name__ == "__main__":
    main()
