from __future__ import annotations

from enum import Enum

import numpy as np

from api.config import settings
from api.services.model_loader import LazyYoloModel
from realtime_pipeline.mode import PrivacyMode as SourcePrivacyMode


class PrivacyMode(str, Enum):
    soft_blur = "soft_blur"
    mosaic = "mosaic"
    color_shield = "color_shield"


class PrivacyService:
    def __init__(self) -> None:
        self._model = LazyYoloModel(settings.face_model_path)

    def anonymize(
        self,
        image: np.ndarray,
        mode: PrivacyMode,
        confidence: float,
        image_size: int = 640,
    ) -> tuple[np.ndarray, int, bool]:
        primary_results = self._model.predict(
            image,
            conf=confidence,
            imgsz=image_size,
            iou=0.45,
            max_det=100,
            verbose=False,
        )

        boxes = self._extract_boxes(primary_results, image.shape)
        if image_size >= 640:
            detail_results = self._model.predict(
                image,
                conf=min(confidence, 0.12),
                imgsz=max(1280, image_size),
                iou=0.40,
                max_det=200,
                verbose=False,
            )
            boxes = self._merge_boxes(
                boxes,
                self._extract_boxes(detail_results, image.shape),
            )

        protected = image.copy()
        if not boxes:
            return protected, 0, False

        source_mode = SourcePrivacyMode()
        source_mode.set_mode(
            {
                PrivacyMode.soft_blur: 1,
                PrivacyMode.mosaic: 2,
                PrivacyMode.color_shield: 3,
            }[mode]
        )
        source_mode.apply(protected, boxes)
        return protected, len(boxes), False

    @staticmethod
    def _extract_boxes(results, image_shape) -> list[tuple[int, int, int, int]]:
        boxes: list[tuple[int, int, int, int]] = []
        for result in results:
            if result.boxes is None:
                continue
            for raw_box in result.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, raw_box)
                width, height = x2 - x1, y2 - y1
                pad_x, pad_y = int(width * 0.15), int(height * 0.20)
                boxes.append(
                    (
                        max(0, x1 - pad_x),
                        max(0, y1 - pad_y),
                        min(image_shape[1], x2 + pad_x),
                        min(image_shape[0], y2 + pad_y),
                    )
                )
        return boxes

    @classmethod
    def _merge_boxes(cls, boxes, candidates):
        merged = list(boxes)
        for candidate in candidates:
            if all(cls._intersection_over_union(candidate, box) < 0.55 for box in merged):
                merged.append(candidate)
        return merged

    @staticmethod
    def _intersection_over_union(first, second) -> float:
        x1 = max(first[0], second[0])
        y1 = max(first[1], second[1])
        x2 = min(first[2], second[2])
        y2 = min(first[3], second[3])
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        if intersection == 0:
            return 0.0
        first_area = max(1, (first[2] - first[0]) * (first[3] - first[1]))
        second_area = max(1, (second[2] - second[0]) * (second[3] - second[1]))
        return intersection / float(first_area + second_area - intersection)


privacy_service = PrivacyService()
