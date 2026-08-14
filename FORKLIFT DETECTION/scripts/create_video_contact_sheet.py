"""Create contact sheets for inspecting the source and tracked videos."""

from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
VIDEOS = {
    "source": ROOT / "samples" / "forklift_warehouse_pexels.mp4",
    "tracked": ROOT
    / "outputs"
    / "forklift_bytetrack"
    / "forklift_bytetrack_predicted_v2.mp4",
}
OUTPUT = ROOT / "reports" / "video_contact_sheet.jpg"


def sample_video(path: Path, count: int = 10) -> list[tuple[float, np.ndarray]]:
    capture = cv2.VideoCapture(str(path))
    frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    sampled = []
    for index in np.linspace(0, max(0, frames - 1), count).astype(int):
        capture.set(cv2.CAP_PROP_POS_FRAMES, int(index))
        ok, frame = capture.read()
        if not ok:
            continue
        frame = cv2.resize(frame, (384, 216))
        timestamp = index / fps if fps else 0
        cv2.putText(
            frame,
            f"{timestamp:.1f}s",
            (10, 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        sampled.append((timestamp, frame))
    capture.release()
    return sampled


rows = []
for name, path in VIDEOS.items():
    frames = [frame for _, frame in sample_video(path)]
    row = np.hstack(frames)
    cv2.putText(
        row,
        name,
        (10, row.shape[0] - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )
    rows.append(row)

sheet = np.vstack(rows)
ok, encoded = cv2.imencode(".jpg", sheet)
if not ok:
    raise SystemExit("Could not encode contact sheet")
OUTPUT.write_bytes(encoded.tobytes())
print(OUTPUT)
