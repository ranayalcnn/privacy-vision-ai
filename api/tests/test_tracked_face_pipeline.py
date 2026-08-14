from __future__ import annotations

import cv2
import numpy as np

from api.services.tracked_face_pipeline import TrackedFacePipeline
from realtime_pipeline.mode import PrivacyMode


class FakeAudit:
    def __init__(self) -> None:
        self.events = []

    def write(self, event, **data):
        self.events.append((event, data))


def face_frame(offset_x: int = 0) -> np.ndarray:
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    for x, y in ((35, 35), (50, 35), (35, 50), (50, 50)):
        cv2.rectangle(
            frame,
            (x + offset_x - 2, y - 2),
            (x + offset_x + 2, y + 2),
            (255, 255, 255),
            -1,
        )
    return frame


def bare_pipeline(frame: np.ndarray) -> TrackedFacePipeline:
    pipeline = TrackedFacePipeline.__new__(TrackedFacePipeline)
    pipeline.confidence = 0.55
    pipeline.image_size = 320
    pipeline.minimum_face_size = 6
    pipeline.detect_interval = 6
    pipeline.privacy_mode = PrivacyMode()
    pipeline.audit = FakeAudit()
    pipeline.tracked_boxes = [(25, 25, 65, 65)]
    pipeline.previous_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pipeline.frame_count = 5
    return pipeline


def test_web_adapter_tracks_face_motion_without_changing_original_files() -> None:
    pipeline = bare_pipeline(face_frame())

    boxes = pipeline.update_tracking(face_frame(offset_x=8))

    assert len(boxes) == 1
    assert 31 <= boxes[0][0] <= 35
    assert 71 <= boxes[0][2] <= 75


def test_web_adapter_keeps_original_blur_during_missed_detection() -> None:
    pipeline = bare_pipeline(face_frame())
    pipeline.detect_faces = lambda frame: []

    protected, face_count = pipeline.process(face_frame(offset_x=4))

    assert face_count == 1
    assert pipeline.audit.events[-1][0] == "frame_anonymized"
    assert not np.array_equal(protected, face_frame(offset_x=4))


def test_web_adapter_does_not_blur_full_frame_without_face_or_track() -> None:
    frame = face_frame()
    pipeline = bare_pipeline(frame)
    pipeline.tracked_boxes = []
    pipeline.previous_gray = None
    pipeline.detect_faces = lambda current_frame: []

    protected, face_count = pipeline.process(frame)

    assert face_count == 0
    assert np.array_equal(protected, frame)
    assert pipeline.audit.events[-1][0] == "no_face_detected"


def test_soft_face_blur_has_feathered_non_rectangular_edges() -> None:
    rng = np.random.default_rng(31)
    frame = rng.integers(0, 255, (100, 100, 3), dtype=np.uint8)
    original = frame.copy()
    mode = PrivacyMode()

    mode.apply(frame, [(20, 20, 80, 80)])

    assert not np.array_equal(frame[45:55, 45:55], original[45:55, 45:55])
    corner_change = np.abs(
        frame[20:25, 20:25].astype(np.int16)
        - original[20:25, 20:25].astype(np.int16)
    ).mean()
    center_change = np.abs(
        frame[45:55, 45:55].astype(np.int16)
        - original[45:55, 45:55].astype(np.int16)
    ).mean()
    assert corner_change < center_change * 0.15
