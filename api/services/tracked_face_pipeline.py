from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from api.services.model_loader import LazyYoloModel
from realtime_pipeline.config import DETECT_INTERVAL, IMAGE_SIZE
from realtime_pipeline.mode import PrivacyMode
from realtime_pipeline.privacy_compliance import PrivacyAudit


class TrackedFacePipeline:
    """Web adapter around the user's original privacy pipeline behavior."""

    def __init__(
        self,
        model_path: Path,
        audit_path: Path,
        confidence: float,
        image_size: int = IMAGE_SIZE,
        minimum_face_size: int = 6,
    ) -> None:
        self.model = LazyYoloModel(model_path)
        self.confidence = confidence
        self.image_size = image_size
        self.minimum_face_size = minimum_face_size
        self.detect_interval = DETECT_INTERVAL
        self.privacy_mode = PrivacyMode()
        self.audit = PrivacyAudit(audit_path)
        self.tracked_boxes: list[tuple[int, int, int, int]] = []
        self.previous_gray: np.ndarray | None = None
        self.frame_count = 0

    def reset(self) -> None:
        self.tracked_boxes = []
        self.previous_gray = None
        self.frame_count = 0

    def detect_faces(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        results = self.model.predict(
            frame,
            conf=min(self.confidence, 0.18),
            imgsz=self.image_size,
            iou=0.45,
            max_det=50,
            verbose=False,
        )
        boxes = []
        for result in results:
            if result.boxes is None:
                continue
            for raw_box in result.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, raw_box)
                width, height = x2 - x1, y2 - y1
                if width < self.minimum_face_size or height < self.minimum_face_size:
                    continue
                pad_x = int(width * 0.20)
                pad_y = int(height * 0.25)
                boxes.append(
                    (
                        max(0, x1 - pad_x),
                        max(0, y1 - pad_y),
                        min(frame.shape[1], x2 + pad_x),
                        min(frame.shape[0], y2 + pad_y),
                    )
                )
        return boxes

    def start_tracking(
        self,
        frame: np.ndarray,
        boxes: list[tuple[int, int, int, int]],
    ) -> None:
        self.tracked_boxes = list(boxes)
        self.previous_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def update_tracking(
        self,
        frame: np.ndarray,
    ) -> list[tuple[int, int, int, int]]:
        if not self.tracked_boxes or self.previous_gray is None:
            return []

        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        updated_boxes = []
        for x1, y1, x2, y2 in self.tracked_boxes:
            mask = np.zeros_like(self.previous_gray)
            mask[y1:y2, x1:x2] = 255
            points = cv2.goodFeaturesToTrack(
                self.previous_gray,
                maxCorners=40,
                qualityLevel=0.01,
                minDistance=4,
                mask=mask,
            )
            moved_box = (x1, y1, x2, y2)
            if points is not None:
                next_points, status, _ = cv2.calcOpticalFlowPyrLK(
                    self.previous_gray,
                    current_gray,
                    points,
                    None,
                    winSize=(21, 21),
                    maxLevel=3,
                )
                if next_points is not None and status is not None:
                    valid = status.reshape(-1) == 1
                    if np.count_nonzero(valid) >= 2:
                        movement = next_points[valid] - points[valid]
                        dx, dy = np.median(movement.reshape(-1, 2), axis=0)
                        dx, dy = int(round(dx)), int(round(dy))
                        moved_box = (
                            max(0, x1 + dx),
                            max(0, y1 + dy),
                            min(frame.shape[1], x2 + dx),
                            min(frame.shape[0], y2 + dy),
                        )
            if moved_box[2] > moved_box[0] and moved_box[3] > moved_box[1]:
                updated_boxes.append(moved_box)

        self.tracked_boxes = updated_boxes
        self.previous_gray = current_gray
        return updated_boxes

    def process(self, frame: np.ndarray) -> tuple[np.ndarray, int]:
        self.frame_count += 1
        should_detect = (
            not self.tracked_boxes
            or self.frame_count % self.detect_interval == 0
        )
        if should_detect:
            detected_boxes = self.detect_faces(frame)
            if detected_boxes:
                boxes = detected_boxes
                self.start_tracking(frame, detected_boxes)
            else:
                boxes = self.update_tracking(frame)
        else:
            boxes = self.update_tracking(frame)

        protected = frame.copy()
        if boxes:
            self.privacy_mode.apply(protected, boxes)
            self.audit.write(
                "frame_anonymized",
                frame_number=self.frame_count,
                face_count=len(boxes),
                mode=self.privacy_mode.mode,
            )
            return protected, len(boxes)

        self.audit.write(
            "no_face_detected",
            frame_number=self.frame_count,
            reason="frame_left_unchanged",
        )
        return protected, 0
