from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "data/hard_examples_multi/selected_frames"
LABELS = ROOT / "data/hard_examples_multi/prelabels"
OUTPUT = ROOT / "reports/multi_video_prelabels_contact_sheet.jpg"
COLORS = {0: (0, 220, 0), 1: (0, 180, 255)}


def main() -> None:
    rows = []
    for folder in sorted(IMAGES.iterdir()):
        paths = sorted(folder.glob("*.jpg"))
        indices = np.linspace(0, len(paths) - 1, 12, dtype=int)
        thumbs = []
        for index in indices:
            image_path = paths[index]
            frame = cv2.imdecode(np.fromfile(image_path, np.uint8), cv2.IMREAD_COLOR)
            height, width = frame.shape[:2]
            label_path = LABELS / folder.name / f"{image_path.stem}.txt"
            for line in label_path.read_text(encoding="utf-8").splitlines():
                class_id, xc, yc, bw, bh = map(float, line.split()[:5])
                class_id = int(class_id)
                x1, y1 = int((xc - bw / 2) * width), int((yc - bh / 2) * height)
                x2, y2 = int((xc + bw / 2) * width), int((yc + bh / 2) * height)
                cv2.rectangle(frame, (x1, y1), (x2, y2), COLORS[class_id], 4)
            thumbs.append(cv2.resize(frame, (240, 135)))
        rows.append(cv2.hconcat(thumbs))
    ok, encoded = cv2.imencode(".jpg", cv2.vconcat(rows), [cv2.IMWRITE_JPEG_QUALITY, 91])
    if not ok:
        raise RuntimeError(OUTPUT)
    encoded.tofile(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
