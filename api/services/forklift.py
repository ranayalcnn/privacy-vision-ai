from __future__ import annotations

from threading import Lock

import cv2
import numpy as np

from api.config import settings
from api.schemas import (
    BoundingBox,
    Detection,
    ForkliftDetectionResponse,
)
from api.services.model_loader import LazyYoloModel
from api.services.vision_preprocess import enhance_for_detection


DETECTION_COLORS = {
    "forklift": (42, 176, 220),
    "person": (91, 196, 126),
    "pallet": (192, 122, 211),
    "pallet_truck": (210, 151, 75),
}
SMOOTHING_ALPHA = 0.55
VELOCITY_ALPHA = 0.65
MAX_GAP_FRAMES = 90


def _intersection_over_union(first: np.ndarray, second: np.ndarray) -> float:
    x1 = max(first[0], second[0])
    y1 = max(first[1], second[1])
    x2 = min(first[2], second[2])
    y2 = min(first[3], second[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    first_area = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
    second_area = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
    union = first_area + second_area - intersection
    return intersection / union if union > 0 else 0.0


def _annotate_detections(
    image: np.ndarray,
    response: ForkliftDetectionResponse,
) -> np.ndarray:
    """Render clean boxes and stable IDs without tracker trajectory lines."""
    output = image.copy()
    for detection in response.detections:
        color = DETECTION_COLORS.get(detection.class_name, (110, 190, 220))
        box = detection.box
        cv2.rectangle(output, (box.x1, box.y1), (box.x2, box.y2), color, 2, cv2.LINE_AA)
        identity = f" #{detection.track_id}" if detection.track_id is not None else ""
        label = f"{detection.class_name}{identity} {detection.confidence:.0%}"
        (text_width, text_height), baseline = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            1,
        )
        label_top = max(0, box.y1 - text_height - baseline - 8)
        cv2.rectangle(
            output,
            (box.x1, label_top),
            (min(output.shape[1], box.x1 + text_width + 8), box.y1),
            color,
            -1,
        )
        cv2.putText(
            output,
            label,
            (box.x1 + 4, max(text_height + 2, box.y1 - baseline - 3)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (12, 24, 20),
            1,
            cv2.LINE_AA,
        )

    return output


class ForkliftService:
    def __init__(self) -> None:
        self._model = LazyYoloModel(settings.forklift_model_path)
        self._live_tracker = ForkliftTracker()

    def detect(
        self,
        image: np.ndarray,
        confidence: float,
        image_size: int = 640,
    ) -> ForkliftDetectionResponse:
        result = self._predict(image, confidence, image_size)
        return self._to_response(image, result)

    def annotate(
        self,
        image: np.ndarray,
        confidence: float,
        image_size: int = 640,
    ) -> tuple[np.ndarray, ForkliftDetectionResponse]:
        result = self._predict(image, confidence, image_size)
        response = self._to_response(image, result)
        return _annotate_detections(image, response), response

    def track(
        self,
        image: np.ndarray,
        confidence: float,
        session_id: str,
        image_size: int = 640,
    ) -> ForkliftDetectionResponse:
        _annotated, response = self._live_tracker.process(
            image,
            confidence,
            session_id,
            image_size,
        )
        return response

    @staticmethod
    def create_tracker() -> "ForkliftTracker":
        return ForkliftTracker()

    def _predict(self, image: np.ndarray, confidence: float, image_size: int):
        automatic_size = 512 if image_size < 640 else max(960, image_size)
        return self._model.predict(
            enhance_for_detection(image),
            conf=min(confidence, 0.05),
            iou=0.75,
            imgsz=automatic_size,
            max_det=200,
            verbose=False,
        )[0]

    @staticmethod
    def _to_response(
        image: np.ndarray,
        result,
    ) -> ForkliftDetectionResponse:
        detections: list[Detection] = []
        height, width = image.shape[:2]
        if result.boxes is not None:
            coordinates = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            track_ids = [None] * len(coordinates)
            if getattr(result.boxes, "id", None) is not None:
                track_ids = (
                    result.boxes.id.cpu().numpy().astype(int).tolist()
                )

            for raw_box, score, class_id, track_id in zip(
                coordinates, scores, class_ids, track_ids, strict=True
            ):
                x1, y1, x2, y2 = map(int, raw_box)
                class_name = str(result.names[int(class_id)])
                if class_name == "forklift":
                    # The detector can fit tightly around the mast/body. Keep
                    # a small safety margin so the full vehicle stays inside.
                    box_width = max(1, x2 - x1)
                    box_height = max(1, y2 - y1)
                    x1 = max(0, x1 - round(box_width * 0.10))
                    y1 = max(0, y1 - round(box_height * 0.08))
                    x2 = min(width, x2 + round(box_width * 0.10))
                    y2 = min(height, y2 + round(box_height * 0.12))
                detections.append(
                    Detection(
                        class_id=int(class_id),
                        class_name=class_name,
                        confidence=round(float(score), 4),
                        box=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                        track_id=track_id,
                    )
                )

        return ForkliftDetectionResponse(
            image_width=width,
            image_height=height,
            detection_count=len(detections),
            detections=detections,
        )


class ForkliftTracker:
    """ByteTrack adapter using the user's original tracker configuration."""

    def __init__(self) -> None:
        self._model = LazyYoloModel(settings.forklift_model_path)
        self._session_id: str | None = None
        self._session_lock = Lock()
        self._smoothed_boxes: dict[int, np.ndarray] = {}
        self._velocities: dict[int, np.ndarray] = {}
        self._track_detections: dict[int, Detection] = {}
        self._last_seen: dict[int, int] = {}
        self._frame_index = 0

    def _reset_state(self) -> None:
        self._smoothed_boxes.clear()
        self._velocities.clear()
        self._track_detections.clear()
        self._last_seen.clear()
        self._frame_index = 0

    @staticmethod
    def _with_box(
        detection: Detection,
        box: np.ndarray,
        width: int,
        height: int,
    ) -> Detection:
        x1, y1, x2, y2 = np.rint(box).astype(int)
        x1 = max(0, min(width - 1, x1))
        y1 = max(0, min(height - 1, y1))
        x2 = max(x1 + 1, min(width, x2))
        y2 = max(y1 + 1, min(height, y2))
        return Detection(
            class_id=detection.class_id,
            class_name=detection.class_name,
            confidence=detection.confidence,
            box=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
            track_id=detection.track_id,
        )

    def _stabilize_tracks(
        self,
        response: ForkliftDetectionResponse,
    ) -> ForkliftDetectionResponse:
        visible: list[Detection] = []
        active_ids: set[int] = set()

        for detection in response.detections:
            if detection.track_id is None:
                visible.append(detection)
                continue
            track_id = detection.track_id
            active_ids.add(track_id)
            raw_box = np.array(
                [detection.box.x1, detection.box.y1, detection.box.x2, detection.box.y2],
                dtype=float,
            )
            previous = self._smoothed_boxes.get(track_id)
            if previous is None:
                smoothed = raw_box
                self._velocities[track_id] = np.zeros(4, dtype=float)
            else:
                smoothed = SMOOTHING_ALPHA * raw_box + (1.0 - SMOOTHING_ALPHA) * previous
                measured_velocity = smoothed - previous
                self._velocities[track_id] = (
                    VELOCITY_ALPHA * measured_velocity
                    + (1.0 - VELOCITY_ALPHA) * self._velocities.get(track_id, np.zeros(4))
                )
            self._smoothed_boxes[track_id] = smoothed
            self._track_detections[track_id] = detection
            self._last_seen[track_id] = self._frame_index
            visible.append(
                self._with_box(
                    detection,
                    smoothed,
                    response.image_width,
                    response.image_height,
                )
            )

        for track_id, box in list(self._smoothed_boxes.items()):
            if track_id in active_ids:
                continue
            gap = self._frame_index - self._last_seen.get(track_id, self._frame_index)
            if gap > 90:
                self._smoothed_boxes.pop(track_id, None)
                self._velocities.pop(track_id, None)
                self._track_detections.pop(track_id, None)
                self._last_seen.pop(track_id, None)
                continue
            if gap > MAX_GAP_FRAMES:
                continue

            detection = self._track_detections[track_id]
            # Follow short motion gaps, then freeze the last reliable box so a
            # long occlusion cannot make the predicted rectangle drift away.
            prediction_gap = min(gap, 12)
            predicted = (
                box
                + self._velocities.get(track_id, np.zeros(4)) * prediction_gap
            )
            overlaps_active = any(
                item.track_id in active_ids
                and item.class_id == detection.class_id
                and _intersection_over_union(
                    predicted,
                    np.array([item.box.x1, item.box.y1, item.box.x2, item.box.y2]),
                ) >= 0.30
                for item in visible
            )
            if not overlaps_active:
                visible.append(
                    self._with_box(
                        detection,
                        predicted,
                        response.image_width,
                        response.image_height,
                    )
                )

        self._frame_index += 1
        return ForkliftDetectionResponse(
            image_width=response.image_width,
            image_height=response.image_height,
            detection_count=len(visible),
            detections=visible,
        )

    def process(
        self,
        image: np.ndarray,
        confidence: float,
        session_id: str,
        image_size: int = 960,
    ) -> tuple[np.ndarray, ForkliftDetectionResponse]:
        with self._session_lock:
            if session_id != self._session_id:
                self._model.reset_tracking()
                self._session_id = session_id
                self._reset_state()
            result = self._model.track(
                enhance_for_detection(image),
                persist=True,
                tracker=str(settings.forklift_tracker_config_path),
                classes=[0, 1, 2, 3],
                conf=min(confidence, 0.03),
                iou=0.60,
                imgsz=image_size,
                max_det=200,
                verbose=False,
            )[0]
            response = ForkliftService._to_response(image, result)
            response = self._stabilize_tracks(response)
            return _annotate_detections(image, response), response


forklift_service = ForkliftService()
