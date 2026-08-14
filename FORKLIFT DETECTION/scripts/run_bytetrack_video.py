"""Track forklifts and people with ByteTrack, smoothed boxes and short-gap hold."""

from __future__ import annotations

import os
from collections import defaultdict, deque
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / "runs" / "ultralytics_config"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "runs" / "matplotlib_config"))

from ultralytics import YOLO  # noqa: E402


SOURCE = (
    ROOT
    / "data"
    / "hard_examples"
    / "forklift_warehouse_8s_15s"
    / "hard_example_8s_15s.mp4"
)
OUTPUT_DIR = ROOT / "outputs" / "forklift_bytetrack"
OUTPUT = OUTPUT_DIR / "forklift_yolo11s_multivideo_bytetrack.mp4"
MODEL = ROOT / "models" / "forklift_yolo11s_multivideo_best.pt"
TRACKER = ROOT / "configs" / "bytetrack_forklift.yaml"

CLASS_NAMES = {0: "forklift", 1: "person"}
COLORS = {0: (0, 165, 255), 1: (0, 220, 0)}
SMOOTHING_ALPHA = 0.55
VELOCITY_ALPHA = 0.65
MAX_GAP_FRAMES = 20
TRAIL_LENGTH = 30
DRAW_TRAILS = False


def intersection_over_union(first: np.ndarray, second: np.ndarray) -> float:
    x1 = max(first[0], second[0])
    y1 = max(first[1], second[1])
    x2 = min(first[2], second[2])
    y2 = min(first[3], second[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    first_area = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
    second_area = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
    union = first_area + second_area - intersection
    return intersection / union if union > 0 else 0.0


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(SOURCE))
    if not capture.isOpened():
        raise SystemExit(f"Cannot open {SOURCE}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        str(OUTPUT),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise SystemExit(f"Cannot create {OUTPUT}")

    model = YOLO(str(MODEL))
    smoothed_boxes: dict[int, np.ndarray] = {}
    velocities: dict[int, np.ndarray] = {}
    track_classes: dict[int, int] = {}
    track_confidences: dict[int, float] = {}
    last_seen: dict[int, int] = {}
    trails: dict[int, deque[tuple[int, int]]] = defaultdict(
        lambda: deque(maxlen=TRAIL_LENGTH)
    )
    frame_index = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        result = model.track(
            frame,
            persist=True,
            tracker=str(TRACKER),
            classes=[0, 1],
            conf=0.03,
            iou=0.60,
            imgsz=640,
            device=0,
            verbose=False,
        )[0]

        active_ids: set[int] = set()
        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            ids = result.boxes.id.int().cpu().tolist()
            classes = result.boxes.cls.int().cpu().tolist()
            confidences = result.boxes.conf.cpu().tolist()

            for box, track_id, class_id, confidence in zip(
                boxes, ids, classes, confidences
            ):
                active_ids.add(track_id)
                previous = smoothed_boxes.get(track_id)
                if previous is None:
                    smoothed = box.astype(float)
                    velocities[track_id] = np.zeros(4, dtype=float)
                else:
                    smoothed = (
                        SMOOTHING_ALPHA * box
                        + (1.0 - SMOOTHING_ALPHA) * previous
                    )
                    measured_velocity = smoothed - previous
                    velocities[track_id] = (
                        VELOCITY_ALPHA * measured_velocity
                        + (1.0 - VELOCITY_ALPHA)
                        * velocities.get(track_id, np.zeros(4, dtype=float))
                    )
                smoothed_boxes[track_id] = smoothed
                track_classes[track_id] = class_id
                track_confidences[track_id] = float(confidence)
                last_seen[track_id] = frame_index
                x1, y1, x2, y2 = smoothed.astype(int)
                trails[track_id].append(((x1 + x2) // 2, (y1 + y2) // 2))

        for track_id, box in list(smoothed_boxes.items()):
            gap = frame_index - last_seen.get(track_id, frame_index)
            if gap > MAX_GAP_FRAMES:
                if gap > 90:
                    smoothed_boxes.pop(track_id, None)
                    velocities.pop(track_id, None)
                    track_classes.pop(track_id, None)
                    track_confidences.pop(track_id, None)
                    trails.pop(track_id, None)
                continue

            class_id = track_classes[track_id]
            is_active = track_id in active_ids
            display_box = box.copy()
            if not is_active:
                display_box = box + velocities.get(
                    track_id, np.zeros(4, dtype=float)
                ) * gap
                overlaps_active = any(
                    other_id != track_id
                    and track_classes.get(other_id) == class_id
                    and intersection_over_union(
                        display_box, smoothed_boxes[other_id]
                    )
                    >= 0.30
                    for other_id in active_ids
                )
                if overlaps_active:
                    continue

            color = COLORS[class_id]
            x1, y1, x2, y2 = display_box.astype(int)
            x1 = max(0, min(width - 1, x1))
            y1 = max(0, min(height - 1, y1))
            x2 = max(0, min(width - 1, x2))
            y2 = max(0, min(height - 1, y2))
            thickness = 3 if is_active else 1
            if not is_active:
                color = tuple(int(channel * 0.55) for channel in color)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            label = (
                f"{CLASS_NAMES[class_id]} ID:{track_id} "
                f"{track_confidences[track_id]:.2f}"
            )
            cv2.putText(
                frame,
                label,
                (x1, max(24, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color,
                2,
                cv2.LINE_AA,
            )
            if DRAW_TRAILS:
                points = list(trails[track_id])
                for start, end in zip(points, points[1:]):
                    cv2.line(frame, start, end, color, 2, cv2.LINE_AA)

        writer.write(frame)
        frame_index += 1

    capture.release()
    writer.release()
    print(f"{OUTPUT} frames={frame_index} fps={fps}")


if __name__ == "__main__":
    main()
