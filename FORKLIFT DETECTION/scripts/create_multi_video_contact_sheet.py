from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/hard_examples_multi/selected_frames"
OUTPUT = ROOT / "reports/multi_video_selected_contact_sheet.jpg"


def main() -> None:
    rows = []
    for folder in sorted(SOURCE.iterdir()):
        images = sorted(folder.glob("*.jpg"))
        indices = np.linspace(0, len(images) - 1, 12, dtype=int)
        thumbs = []
        for index in indices:
            frame = cv2.imdecode(np.fromfile(images[index], np.uint8), cv2.IMREAD_COLOR)
            thumbs.append(cv2.resize(frame, (240, 135)))
        rows.append(cv2.hconcat(thumbs))
    sheet = cv2.vconcat(rows)
    ok, encoded = cv2.imencode(".jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise RuntimeError(OUTPUT)
    encoded.tofile(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
