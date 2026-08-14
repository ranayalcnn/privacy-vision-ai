from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
VIDEO_DIR = ROOT / "data/hard_examples_multi/videos"
FRAME_DIR = ROOT / "data/hard_examples_multi/selected_frames"
REPORT = ROOT / "reports/multi_video_frame_selection.json"
TARGET_PER_VIDEO = 120


def safe_write(path: Path, frame: np.ndarray) -> None:
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise RuntimeError(path)
    encoded.tofile(path)


def main() -> None:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for video_index, video_path in enumerate(sorted(VIDEO_DIR.glob("*.mp4")), start=1):
        capture = cv2.VideoCapture(str(video_path))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        if frame_count <= 0:
            raise RuntimeError(f"Cannot read {video_path}")

        bins = np.linspace(0, frame_count, TARGET_PER_VIDEO + 1, dtype=int)
        selected = []
        previous_gray = None
        current_bin = 0
        best = None
        frame_index = 0

        while True:
            ok, frame = capture.read()
            if not ok:
                break
            gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (160, 90))
            sharpness = min(cv2.Laplacian(gray, cv2.CV_64F).var() / 800.0, 1.0)
            motion = (
                float(np.mean(cv2.absdiff(gray, previous_gray))) / 35.0
                if previous_gray is not None
                else 0.0
            )
            score = 0.65 * min(motion, 1.0) + 0.35 * sharpness
            previous_gray = gray

            while current_bin < TARGET_PER_VIDEO and frame_index >= bins[current_bin + 1]:
                if best is not None:
                    selected.append(best)
                best = None
                current_bin += 1
            if current_bin >= TARGET_PER_VIDEO:
                break
            if best is None or score > best[0]:
                best = (score, frame_index, frame.copy())
            frame_index += 1

        if best is not None and len(selected) < TARGET_PER_VIDEO:
            selected.append(best)
        capture.release()

        video_folder = FRAME_DIR / f"video_{video_index:02d}"
        video_folder.mkdir(parents=True, exist_ok=True)
        for rank, (score, source_index, frame) in enumerate(selected):
            filename = f"v{video_index:02d}_{rank:03d}_f{source_index:06d}.jpg"
            safe_write(video_folder / filename, frame)

        records.append(
            {
                "video": video_path.name,
                "fps": fps,
                "source_frames": frame_count,
                "selected_frames": len(selected),
            }
        )
        print(f"{video_path.name}: {frame_count} -> {len(selected)}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Total selected: {sum(item['selected_frames'] for item in records)}")


if __name__ == "__main__":
    main()
