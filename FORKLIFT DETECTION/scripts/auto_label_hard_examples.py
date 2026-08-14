from __future__ import annotations

import json
import os
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/hard_examples/forklift_warehouse_8s_15s/images"
LABELS = ROOT / "data/hard_examples/forklift_warehouse_8s_15s/labels_auto"
PREVIEWS = ROOT / "data/hard_examples/forklift_warehouse_8s_15s/previews_auto"
REPORT = ROOT / "reports/hard_example_auto_labels.json"
CONTACT_SHEET = ROOT / "reports/hard_example_auto_labels_contact_sheet.jpg"
MODEL_ID = "IDEA-Research/grounding-dino-tiny"
CLASS_NAMES = ["forklift", "person"]
PROMPT = [["a complete forklift truck", "a person"]]


def cv_read(path: Path) -> np.ndarray:
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def cv_write(path: Path, image: np.ndarray) -> None:
    ok, encoded = cv2.imencode(path.suffix, image)
    if not ok:
        raise RuntimeError(f"Could not encode {path}")
    encoded.tofile(path)


def yolo_line(class_id: int, box: list[float], width: int, height: int) -> str:
    x1, y1, x2, y2 = box
    xc = ((x1 + x2) / 2) / width
    yc = ((y1 + y2) / 2) / height
    bw = (x2 - x1) / width
    bh = (y2 - y1) / height
    return f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}"


def main() -> None:
    LABELS.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(ROOT / "runs/huggingface"))

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained(MODEL_ID, local_files_only=True)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(
        MODEL_ID, local_files_only=True
    ).to(device)
    model.eval()

    records: list[dict] = []
    preview_paths: list[Path] = []
    images = sorted(SOURCE.glob("*.jpg"))

    for image_path in images:
        image = Image.open(image_path).convert("RGB")
        width, height = image.size
        inputs = processor(images=image, text=PROMPT, return_tensors="pt").to(device)
        with torch.inference_mode():
            outputs = model(**inputs)
        result = processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=0.22,
            text_threshold=0.18,
            target_sizes=[(height, width)],
        )[0]

        candidates: dict[int, list[tuple[float, list[float]]]] = {0: [], 1: []}
        for score, label, box in zip(
            result["scores"].cpu().tolist(),
            result["text_labels"],
            result["boxes"].cpu().tolist(),
        ):
            label_lower = str(label).lower()
            class_id = 0 if "forklift" in label_lower else 1 if "person" in label_lower else -1
            if class_id >= 0:
                candidates[class_id].append((float(score), [float(v) for v in box]))

        selected: list[dict] = []
        for class_id in (0, 1):
            if not candidates[class_id]:
                continue
            # The clip contains one forklift and one worker. Prefer the highest-confidence
            # complete object; area is only a small tie-breaker.
            score, box = max(
                candidates[class_id],
                key=lambda item: item[0] + 0.03 * ((item[1][2] - item[1][0]) * (item[1][3] - item[1][1])) / (width * height),
            )
            selected.append(
                {"class_id": class_id, "class_name": CLASS_NAMES[class_id], "score": score, "box": box}
            )

        lines = [yolo_line(item["class_id"], item["box"], width, height) for item in selected]
        (LABELS / f"{image_path.stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

        canvas = cv_read(image_path)
        colors = [(0, 220, 0), (0, 180, 255)]
        for item in selected:
            x1, y1, x2, y2 = map(int, item["box"])
            color = colors[item["class_id"]]
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 3)
            cv2.putText(
                canvas,
                f'{item["class_name"]} {item["score"]:.2f}',
                (x1, max(25, y1 - 7)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color,
                2,
                cv2.LINE_AA,
            )
        preview_path = PREVIEWS / image_path.name
        cv_write(preview_path, canvas)
        preview_paths.append(preview_path)
        records.append({"image": image_path.name, "detections": selected})
        print(f"{image_path.name}: " + ", ".join(f'{x["class_name"]}={x["score"]:.2f}' for x in selected))

    thumbs = []
    for path in preview_paths:
        frame = cv_read(path)
        frame = cv2.resize(frame, (320, 180))
        thumbs.append(frame)
    rows = []
    for start in range(0, len(thumbs), 6):
        row = thumbs[start : start + 6]
        while len(row) < 6:
            row.append(np.full((180, 320, 3), 255, dtype=np.uint8))
        rows.append(cv2.hconcat(row))
    cv_write(CONTACT_SHEET, cv2.vconcat(rows))
    REPORT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Completed {len(images)} images on {device}. Contact sheet: {CONTACT_SHEET}")


if __name__ == "__main__":
    main()
