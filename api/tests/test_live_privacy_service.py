from __future__ import annotations

import numpy as np

from api.services.live_privacy import LivePrivacyService
from api.services.privacy import PrivacyMode


class FakeMode:
    def __init__(self) -> None:
        self.selected = None

    def set_mode(self, mode_id):
        self.selected = mode_id


class FakeProcessor:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.tracked_boxes = [(1, 1, 3, 3)]
        self.previous_gray = np.ones((2, 2), dtype=np.uint8)
        self.frame_count = 12
        self.confidence = None
        self.privacy_mode = FakeMode()

    def process(self, image):
        return image.copy(), 1

    def reset(self):
        self.tracked_boxes = []
        self.previous_gray = None
        self.frame_count = 0


def test_live_service_reuses_processor_and_resets_new_session(monkeypatch) -> None:
    created: list[FakeProcessor] = []

    def fake_constructor(**kwargs):
        processor = FakeProcessor(**kwargs)
        created.append(processor)
        return processor

    monkeypatch.setattr(
        "api.services.live_privacy.TrackedFacePipeline",
        fake_constructor,
    )
    service = LivePrivacyService()
    image = np.zeros((20, 30, 3), dtype=np.uint8)

    first_result = service.process(
        image,
        PrivacyMode.mosaic,
        0.6,
        "camera-session-one",
    )
    processor = created[0]
    assert processor.kwargs["image_size"] == 416
    assert processor.kwargs["minimum_face_size"] == 6
    processor.tracked_boxes = [(2, 2, 4, 4)]
    processor.frame_count = 4

    second_result = service.process(
        image,
        PrivacyMode.color_shield,
        0.7,
        "camera-session-one",
    )
    assert processor.tracked_boxes == [(2, 2, 4, 4)]
    assert processor.frame_count == 4

    service.process(
        image,
        PrivacyMode.soft_blur,
        0.55,
        "camera-session-two",
    )

    assert len(created) == 1
    assert first_result.face_count == second_result.face_count == 1
    assert processor.tracked_boxes == []
    assert processor.previous_gray is None
    assert processor.frame_count == 0
    assert processor.confidence == 0.55
    assert processor.privacy_mode.selected == 1
