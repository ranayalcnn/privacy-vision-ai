from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from blur import apply_blur
from tracker import ObjectTracker
from yolo_detector import YOLODetector


WINDOW_NAME = "YOLO Face Blur + Tracking"


def process_video(source: str | Path, output: str | Path | None = None) -> None:
    """Run the recovered video face-blur and person-tracking application."""
    detector = YOLODetector()
    tracker = ObjectTracker()
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"Video açılamadı: {source}")

    writer = None
    if output is not None:
        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(
            str(output),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 960, 540)
    try:
        while True:
            success, frame = capture.read()
            if not success:
                break

            people = tracker.track_people(frame)
            for face in detector.detect_faces(frame):
                apply_blur(frame, face)

            for person in people:
                x1, y1, x2, y2 = person["box"]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 190, 110), 2)
                cv2.putText(
                    frame,
                    f"ID: {person['id']}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 190, 110),
                    2,
                )

            if writer is not None:
                writer.write(frame)
            cv2.imshow(WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="Video face blur and tracking")
    parser.add_argument("source", nargs="?", default="video.mp4")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    process_video(args.source, args.output)


if __name__ == "__main__":
    main()
