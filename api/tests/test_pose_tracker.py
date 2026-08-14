from __future__ import annotations

import numpy as np

from api.config import settings
from api.services.pose import PoseTracker


class CpuArray:
    def __init__(self, value) -> None:
        self.value = np.asarray(value)

    def cpu(self):
        return self

    def numpy(self):
        return self.value


class FakePoseModel:
    def __init__(self, result) -> None:
        self.result = result
        self.options = {}
        self.reset_count = 0

    def reset_tracking(self) -> None:
        self.reset_count += 1

    def track(self, image, **kwargs):
        self.options = kwargs
        return [self.result]


def test_pose_tracker_keeps_two_people_and_uses_bytetrack() -> None:
    points = np.zeros((2, 17, 2), dtype=np.float32)
    for person_index, offset in enumerate((20, 90)):
        for keypoint_index in range(17):
            points[person_index, keypoint_index] = (
                offset + keypoint_index,
                20 + keypoint_index * 2,
            )
    keypoints = type(
        "Keypoints",
        (),
        {
            "xy": CpuArray(points),
            "conf": CpuArray(np.full((2, 17), 0.9, dtype=np.float32)),
        },
    )()
    boxes = type("Boxes", (), {"id": CpuArray([7, 12])})()
    result = type("Result", (), {"keypoints": keypoints, "boxes": boxes})()

    tracker = PoseTracker()
    tracker._model = FakePoseModel(result)
    frame = np.zeros((120, 180, 3), dtype=np.uint8)

    output, pose_count = tracker.process(frame, 0.25, "crowded-demo")

    assert pose_count == 2
    assert tracker._model.reset_count == 1
    assert tracker._model.options["persist"] is True
    assert tracker._model.options["tracker"] == str(
        settings.forklift_tracker_config_path
    )
    assert set(tracker._history) == {7, 12}
    assert not np.array_equal(output, frame)
