import cv2

from ultralytics import YOLO

from config import (
    DETECT_INTERVAL,
    CONFIDENCE,
    IMAGE_SIZE,
)
from mode import PrivacyMode
from privacy_compliance import PrivacyAudit, fail_safe


class Processor:
    def __init__(self, audit_path="privacy_audit.jsonl"):
        self.model = YOLO("yolov8n-face.pt")

        self.trackers = []
        self.frame_count = 0
        self.privacy_mode = PrivacyMode()
        self.audit = PrivacyAudit(audit_path)

    @staticmethod
    def create_tracker():
        if hasattr(cv2, "legacy"):
            if hasattr(cv2.legacy, "TrackerCSRT_create"):
                return cv2.legacy.TrackerCSRT_create()

            if hasattr(cv2.legacy, "TrackerKCF_create"):
                return cv2.legacy.TrackerKCF_create()

        if hasattr(cv2, "TrackerCSRT_create"):
            return cv2.TrackerCSRT_create()

        if hasattr(cv2, "TrackerKCF_create"):
            return cv2.TrackerKCF_create()

        return None

    def detect_faces(self, frame):
        results = self.model.predict(
            frame,
            conf=CONFIDENCE,
            imgsz=IMAGE_SIZE,
            max_det=10,
            verbose=False,
        )

        boxes = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, box)

                width = x2 - x1
                height = y2 - y1

                if width < 25 or height < 25:
                    continue

                pad_x = int(width * 0.15)
                pad_y = int(height * 0.20)

                x1 = max(0, x1 - pad_x)
                y1 = max(0, y1 - pad_y)
                x2 = min(frame.shape[1], x2 + pad_x)
                y2 = min(frame.shape[0], y2 + pad_y)

                boxes.append(
                    (x1, y1, x2, y2)
                )

        return boxes

    def start_trackers(self, frame, boxes):
        self.trackers = []

        for x1, y1, x2, y2 in boxes:
            tracker = self.create_tracker()

            if tracker is None:
                continue

            width = x2 - x1
            height = y2 - y1

            tracker.init(
                frame,
                (x1, y1, width, height),
            )

            self.trackers.append(tracker)

    def update_trackers(self, frame):
        boxes = []

        for tracker in self.trackers:
            success, box = tracker.update(frame)

            if not success:
                continue

            x, y, width, height = map(int, box)

            if width < 20 or height < 20:
                continue

            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(frame.shape[1], x + width)
            y2 = min(frame.shape[0], y + height)

            if x2 > x1 and y2 > y1:
                boxes.append(
                    (x1, y1, x2, y2)
                )

        return boxes

    def blur_faces(self, frame, boxes):
        self.privacy_mode.apply(frame, boxes)
        for x1, y1, x2, y2 in boxes:
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (214, 156, 62),
                2,
            )

    def process(self, frame):
        self.frame_count += 1

        should_detect = (
            not self.trackers
            or self.frame_count % DETECT_INTERVAL == 0
        )

        if should_detect:
            boxes = self.detect_faces(frame)

            if boxes:
                self.start_trackers(frame, boxes)
            else:
                self.trackers = []
        else:
            boxes = self.update_trackers(frame)

            if not boxes:
                self.trackers = []

        if boxes:
            self.blur_faces(frame, boxes)
            self.audit.write("frame_anonymized", frame_number=self.frame_count,
                             face_count=len(boxes), mode=self.privacy_mode.mode)
        else:
            frame = fail_safe(frame)
            self.audit.write("fail_safe_applied", frame_number=self.frame_count,
                             reason="no_reliable_face_detection")

        return frame, len(boxes)


def draw_info(
    frame,
    fps,
    latency,
    queue_size,
    dropped,
    faces,
):
    texts = [
        f"FPS: {fps:.1f}",
        f"Latency: {latency:.1f} ms",
        f"Queue: {queue_size}",
        f"Dropped: {dropped}",
        f"Faces: {faces}",
    ]

    for index, text in enumerate(texts):
        cv2.putText(
            frame,
            text,
            (15, 30 + index * 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (240, 238, 234),
            1,
            cv2.LINE_AA,
        )
