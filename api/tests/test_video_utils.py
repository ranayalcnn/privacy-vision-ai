from __future__ import annotations

from threading import Event

import cv2
import pytest

from api.services.video import (
    VideoProcessingCancelled,
    VideoProcessingError,
    report_progress,
    video_properties,
)


class FakeCapture:
    def __init__(self, values) -> None:
        self.values = values

    def get(self, property_id):
        return self.values.get(property_id, 0)


def test_video_properties_preserve_fps_and_dimensions() -> None:
    capture = FakeCapture(
        {
            cv2.CAP_PROP_FPS: 30,
            cv2.CAP_PROP_FRAME_WIDTH: 1280,
            cv2.CAP_PROP_FRAME_HEIGHT: 720,
        }
    )

    assert video_properties(capture) == (30, 1280, 720)


def test_video_properties_use_safe_fps_fallback() -> None:
    capture = FakeCapture(
        {
            cv2.CAP_PROP_FPS: 0,
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
        }
    )

    assert video_properties(capture) == (25.0, 640, 480)


def test_video_properties_reject_missing_dimensions() -> None:
    with pytest.raises(VideoProcessingError):
        video_properties(FakeCapture({cv2.CAP_PROP_FPS: 30}))


def test_video_progress_reports_percentage_inputs_and_honors_cancel() -> None:
    capture = FakeCapture({cv2.CAP_PROP_FRAME_COUNT: 100})
    progress: list[tuple[int, int]] = []

    report_progress(
        capture,
        processed_frames=35,
        callback=lambda current, total: progress.append((current, total)),
        cancel_event=None,
    )
    assert progress == [(35, 100)]

    cancel_event = Event()
    cancel_event.set()
    with pytest.raises(VideoProcessingCancelled):
        report_progress(capture, 36, None, cancel_event)
