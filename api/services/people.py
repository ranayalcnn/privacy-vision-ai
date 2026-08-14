from __future__ import annotations

from enum import Enum
from threading import Lock

import numpy as np

from api.config import settings
from api.services.model_loader import LazyYoloModel
from api.services.vision_preprocess import enhance_for_detection
from blur_and_segment.blur import apply_segmentation_blur
from blur_and_segment.person_remover import remove_people


class PeopleMode(str, Enum):
    blur = "blur"
    remove = "remove"


class PeopleService:
    def __init__(self) -> None:
        self._model = LazyYoloModel(settings.segmentation_model_path)
        self._live_tracker = PeopleTracker()

    def process(
        self,
        image: np.ndarray,
        mode: PeopleMode,
        confidence: float,
        image_size: int = 640,
        selected_point: tuple[float, float] | None = None,
    ) -> tuple[np.ndarray, int]:
        inference_image = enhance_for_detection(image)
        results = self._predict(
            inference_image,
            confidence,
            image_size,
        )

        # A second, more detailed pass recovers small, dark or overlapping
        # people when the normal pass sees at most one person. Skip it for the
        # low-resolution live profile so camera latency remains bounded.
        if self._detection_count(results) <= 1 and image_size >= 640:
            recovery_results = self._predict(
                inference_image,
                min(confidence, 0.08),
                max(960, image_size),
            )
            if self._detection_count(recovery_results) > self._detection_count(results):
                results = recovery_results

        if selected_point is not None:
            results = _select_person(results, selected_point, image.shape)

        if mode == PeopleMode.remove:
            output, count = remove_people(image, results)
            return output, count

        output, count, _mask_coverage = apply_segmentation_blur(
            image,
            results,
            blur_strength=71,
            dilation_size=3,
            feather_size=15,
            restrict_to_segmentation=True,
        )
        return output, count

    def _predict(
        self,
        image: np.ndarray,
        confidence: float,
        image_size: int,
    ):
        return self._model.predict(
            image,
            classes=[0],
            conf=confidence,
            iou=0.85,
            imgsz=image_size,
            max_det=200,
            retina_masks=True,
            verbose=False,
        )

    @staticmethod
    def _detection_count(results) -> int:
        count = 0
        for result in results:
            boxes = getattr(result, "boxes", None)
            coordinates = getattr(boxes, "xyxy", None)
            if coordinates is not None:
                count += len(coordinates)
        return count

    def create_tracker(self) -> "PeopleTracker":
        return PeopleTracker()

    def track(
        self,
        image: np.ndarray,
        mode: PeopleMode,
        confidence: float,
        session_id: str,
        image_size: int = 320,
    ) -> tuple[np.ndarray, int]:
        return self._live_tracker.process(
            image,
            mode,
            confidence,
            session_id,
            image_size=image_size,
        )


def _to_numpy(value):
    if value is None:
        return None
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def _selected_index(
    boxes: np.ndarray,
    selected_point: tuple[float, float],
    image_shape,
) -> int | None:
    if boxes.ndim != 2 or not len(boxes):
        return None
    height, width = image_shape[:2]
    target = np.array(
        [selected_point[0] * width, selected_point[1] * height],
        dtype=float,
    )
    inside: list[tuple[float, int]] = []
    for index, (x1, y1, x2, y2) in enumerate(boxes[:, :4]):
        if x1 <= target[0] <= x2 and y1 <= target[1] <= y2:
            inside.append((max(1.0, (x2 - x1) * (y2 - y1)), index))
    if inside:
        return min(inside)[1]
    centers = (boxes[:, :2] + boxes[:, 2:4]) / 2.0
    return int(np.argmin(np.linalg.norm(centers - target, axis=1)))


def _select_person(results, selected_point, image_shape, track_id=None):
    for result in results:
        boxes_object = getattr(result, "boxes", None)
        boxes = _to_numpy(getattr(boxes_object, "xyxy", None))
        if boxes is None:
            continue
        index = None
        if track_id is not None:
            ids = _to_numpy(getattr(boxes_object, "id", None))
            if ids is not None:
                matches = np.flatnonzero(ids.astype(int) == track_id)
                if len(matches):
                    index = int(matches[0])
        else:
            index = _selected_index(boxes, selected_point, image_shape)
        if index is not None:
            return [result[[index]]]
    return []


class PeopleTracker:
    """ByteTrack-backed person segmentation for stable multi-person video."""

    def __init__(self) -> None:
        self._model = LazyYoloModel(settings.segmentation_model_path)
        self._recovery_model = LazyYoloModel(settings.segmentation_model_path)
        self._session_id: str | None = None
        self._selected_track_id: int | None = None
        self._lock = Lock()

    def process(
        self,
        image: np.ndarray,
        mode: PeopleMode,
        confidence: float,
        session_id: str,
        selected_point: tuple[float, float] | None = None,
        image_size: int = 832,
    ) -> tuple[np.ndarray, int]:
        with self._lock:
            if session_id != self._session_id:
                self._model.reset_tracking()
                self._session_id = session_id
                self._selected_track_id = None

            results = self._model.track(
                enhance_for_detection(image),
                persist=True,
                tracker=str(settings.forklift_tracker_config_path),
                classes=[0],
                conf=min(confidence, 0.05),
                iou=0.85,
                imgsz=image_size,
                max_det=200,
                retina_masks=True,
                verbose=False,
            )

            if (
                selected_point is None
                and image_size >= 640
                and PeopleService._detection_count(results) <= 1
            ):
                # Crowded/overlapping people can collapse into one tracked mask.
                # A separate high-resolution pass recovers the missing masks
                # without resetting the stateful ByteTrack predictor.
                recovery_results = self._recovery_model.predict(
                    enhance_for_detection(image),
                    classes=[0],
                    conf=0.04,
                    iou=0.90,
                    imgsz=1280,
                    max_det=200,
                    retina_masks=True,
                    verbose=False,
                )
                if PeopleService._detection_count(recovery_results) > PeopleService._detection_count(results):
                    results = recovery_results

            if selected_point is not None:
                if self._selected_track_id is None:
                    for result in results:
                        boxes_object = getattr(result, "boxes", None)
                        boxes = _to_numpy(getattr(boxes_object, "xyxy", None))
                        ids = _to_numpy(getattr(boxes_object, "id", None))
                        if boxes is None or ids is None:
                            continue
                        index = _selected_index(boxes, selected_point, image.shape)
                        if index is not None:
                            self._selected_track_id = int(ids[index])
                            break
                results = _select_person(
                    results,
                    selected_point,
                    image.shape,
                    self._selected_track_id,
                )

            if mode == PeopleMode.remove:
                return remove_people(image, results)
            output, count, _coverage = apply_segmentation_blur(
                image,
                results,
                blur_strength=71,
                dilation_size=3,
                feather_size=15,
                restrict_to_segmentation=True,
            )
            return output, count


people_service = PeopleService()
