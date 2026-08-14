"""Create a short hard-example clip and extract frames for corrective labeling."""

from __future__ import annotations

from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "samples" / "forklift_warehouse_pexels.mp4"
OUTPUT_DIR = ROOT / "data" / "hard_examples" / "forklift_warehouse_8s_15s"
CLIP = OUTPUT_DIR / "hard_example_8s_15s.mp4"
FRAMES_DIR = OUTPUT_DIR / "images"

START_SECOND = 8.0
END_SECOND = 15.0
EXTRACT_EVERY_N_FRAMES = 5


def write_image(path: Path, frame) -> None:
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise RuntimeError(f"Could not encode {path}")
    path.write_bytes(encoded.tobytes())


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
capture = cv2.VideoCapture(str(SOURCE))
if not capture.isOpened():
    raise SystemExit(f"Cannot open {SOURCE}")

fps = capture.get(cv2.CAP_PROP_FPS)
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
start_frame = int(START_SECOND * fps)
end_frame = int(END_SECOND * fps)
capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

writer = cv2.VideoWriter(
    str(CLIP),
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height),
)
if not writer.isOpened():
    capture.release()
    raise SystemExit(f"Cannot create {CLIP}")

source_frame_index = start_frame
clip_frame_index = 0
extracted = 0
while source_frame_index < end_frame:
    ok, frame = capture.read()
    if not ok:
        break
    writer.write(frame)
    if clip_frame_index % EXTRACT_EVERY_N_FRAMES == 0:
        timestamp_ms = int(source_frame_index / fps * 1000)
        write_image(FRAMES_DIR / f"frame_{timestamp_ms:06d}ms.jpg", frame)
        extracted += 1
    source_frame_index += 1
    clip_frame_index += 1

capture.release()
writer.release()
print(f"clip={CLIP} frames={clip_frame_index} extracted_images={extracted}")
