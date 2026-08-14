"""Convert the generated AVI detection result to a broadly playable MP4."""

from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "outputs"
    / "forklift_video_detection"
    / "forklift_warehouse_pexels.avi"
)
DESTINATION = (
    ROOT
    / "outputs"
    / "forklift_video_detection"
    / "forklift_detection_result.mp4"
)

capture = cv2.VideoCapture(str(SOURCE))
if not capture.isOpened():
    raise SystemExit(f"Cannot open {SOURCE}")

fps = capture.get(cv2.CAP_PROP_FPS)
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
writer = cv2.VideoWriter(
    str(DESTINATION),
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height),
)
if not writer.isOpened():
    capture.release()
    raise SystemExit(f"Cannot create {DESTINATION}")

frames = 0
while True:
    ok, frame = capture.read()
    if not ok:
        break
    writer.write(frame)
    frames += 1

capture.release()
writer.release()
print(f"{DESTINATION} frames={frames} fps={fps}")
