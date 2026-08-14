from __future__ import annotations

import cv2
import numpy as np

from blur_and_segment.blur import apply_segmentation_blur
from blur_and_segment.person_remover import remove_people
from api.config import settings
from api.schemas import BoundingBox
from api.services.forklift import ForkliftService, ForkliftTracker
from api.services.people import PeopleMode, PeopleService
from api.services.pose import PoseService
from api.services.privacy import PrivacyMode, PrivacyService


class CpuArray:
    def __init__(self, value) -> None:
        self.value = np.asarray(value)

    def cpu(self):
        return self

    def numpy(self):
        return self.value


class FakeBoxes:
    def __init__(self, xyxy, confidence=None, classes=None, track_ids=None) -> None:
        self.xyxy = CpuArray(xyxy)
        self.conf = CpuArray(confidence if confidence is not None else [])
        self.cls = CpuArray(classes if classes is not None else [])
        self.id = CpuArray(track_ids) if track_ids is not None else None


def test_privacy_service_applies_all_provided_modes() -> None:
    image = np.zeros((80, 100, 3), dtype=np.uint8)
    image[20:60, 30:70] = np.arange(40, dtype=np.uint8)[:, None, None]
    result = type("Result", (), {"boxes": FakeBoxes([[30, 20, 70, 60]])})()
    service = PrivacyService()
    service._model.predict = lambda *args, **kwargs: [result]

    outputs = {}
    for mode in PrivacyMode:
        output, count, fail_safe = service.anonymize(image, mode, 0.55)
        outputs[mode] = output
        assert count == 1
        assert fail_safe is False
        assert not np.array_equal(output[12:68, 24:76], image[12:68, 24:76])

    assert not np.array_equal(
        outputs[PrivacyMode.mosaic],
        outputs[PrivacyMode.color_shield],
    )


def test_privacy_service_leaves_frame_unchanged_when_no_face_is_found() -> None:
    image = np.indices((80, 100)).sum(axis=0).astype(np.uint8)
    image = np.repeat(image[..., None], 3, axis=2)
    result = type("Result", (), {"boxes": None})()
    service = PrivacyService()
    service._model.predict = lambda *args, **kwargs: [result]

    output, count, fail_safe = service.anonymize(
        image,
        PrivacyMode.soft_blur,
        0.55,
    )

    assert count == 0
    assert fail_safe is False
    assert np.array_equal(output, image)


def test_privacy_service_uses_detailed_pass_for_distant_faces() -> None:
    image = np.indices((160, 240)).sum(axis=0).astype(np.uint8)
    image = np.repeat(image[..., None], 3, axis=2)
    empty = type("Result", (), {"boxes": None})()
    distant = type("Result", (), {"boxes": FakeBoxes([[110, 35, 120, 45]])})()
    prediction_options = []
    service = PrivacyService()

    def fake_predict(*args, **kwargs):
        prediction_options.append(kwargs)
        return [empty] if len(prediction_options) == 1 else [distant]

    service._model.predict = fake_predict

    output, count, fail_safe = service.anonymize(
        image,
        PrivacyMode.soft_blur,
        0.30,
    )

    assert count == 1
    assert fail_safe is False
    assert prediction_options[1]["imgsz"] == 1280
    assert prediction_options[1]["conf"] == 0.12
    assert not np.array_equal(output[30:50, 105:125], image[30:50, 105:125])
    assert np.array_equal(output[:20, :20], image[:20, :20])


def test_people_service_routes_blur_and_remove_to_provided_functions(
    monkeypatch,
) -> None:
    image = np.zeros((30, 40, 3), dtype=np.uint8)
    model_results = [object()]
    service = PeopleService()
    prediction_options = {}

    def fake_predict(*args, **kwargs):
        prediction_options.update(kwargs)
        return model_results

    service._model.predict = fake_predict
    calls: list[str] = []

    def fake_blur(frame, results, **kwargs):
        assert results is model_results
        assert kwargs == {
            "blur_strength": 71,
            "dilation_size": 3,
            "feather_size": 15,
            "restrict_to_segmentation": True,
        }
        calls.append("blur")
        return frame + 1, 2, 0.25

    def fake_remove(frame, results):
        assert results is model_results
        calls.append("remove")
        return frame + 2, 3

    monkeypatch.setattr("api.services.people.apply_segmentation_blur", fake_blur)
    monkeypatch.setattr("api.services.people.remove_people", fake_remove)

    blurred, blur_count = service.process(image, PeopleMode.blur, 0.25)
    removed, remove_count = service.process(image, PeopleMode.remove, 0.25)

    assert calls == ["blur", "remove"]
    assert prediction_options["classes"] == [0]
    assert blur_count == 2 and np.all(blurred == 1)
    assert remove_count == 3 and np.all(removed == 2)


def test_person_blur_does_not_change_background_outside_person_mask() -> None:
    rng = np.random.default_rng(7)
    image = rng.integers(0, 255, (100, 120, 3), dtype=np.uint8)
    polygon = np.array([[45, 30], [75, 30], [75, 80], [45, 80]])
    masks = type("Masks", (), {"xy": [polygon]})()
    result = type("Result", (), {"masks": masks})()

    output, count, coverage = apply_segmentation_blur(
        image,
        [result],
        blur_strength=71,
        dilation_size=3,
        feather_size=15,
        restrict_to_segmentation=True,
    )

    assert count == 1
    assert coverage > 0
    person_pixels = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(person_pixels, [polygon.astype(np.int32)], 1)
    assert np.array_equal(output[person_pixels == 0], image[person_pixels == 0])
    assert not np.array_equal(output[40:70, 50:70], image[40:70, 50:70])


def test_people_operations_protect_every_box_when_one_mask_is_missing() -> None:
    rng = np.random.default_rng(19)
    image = rng.integers(0, 255, (120, 180, 3), dtype=np.uint8)
    first_person = np.array([[20, 20], [60, 20], [60, 100], [20, 100]])
    masks = type("Masks", (), {"xy": [first_person]})()
    boxes = FakeBoxes([[20, 20, 60, 100], [110, 20, 150, 100]])
    result = type("Result", (), {"masks": masks, "boxes": boxes})()

    blurred, blur_count, _ = apply_segmentation_blur(
        image,
        [result],
        blur_strength=31,
        dilation_size=5,
        feather_size=5,
    )
    removed, remove_count = remove_people(image, [result])

    assert blur_count == 2
    assert remove_count == 2
    assert not np.array_equal(blurred[35:85, 30:50], image[35:85, 30:50])
    assert not np.array_equal(blurred[35:85, 120:140], image[35:85, 120:140])
    assert not np.array_equal(removed[35:85, 30:50], image[35:85, 30:50])
    assert not np.array_equal(removed[35:85, 120:140], image[35:85, 120:140])
    assert np.array_equal(blurred[:5, :5], image[:5, :5])


def test_pose_service_returns_plotted_keypoints() -> None:
    plotted = np.full((20, 30, 3), 120, dtype=np.uint8)
    result = type(
        "Result",
        (),
        {
            "keypoints": [object(), object()],
            "plot": lambda self: plotted,
        },
    )()
    service = PoseService()
    service._model.predict = lambda *args, **kwargs: [result]

    output, count = service.estimate(
        np.zeros((20, 30, 3), dtype=np.uint8),
        0.25,
    )

    assert count == 2
    assert np.array_equal(output, plotted)


def test_forklift_service_builds_detections_and_expands_vehicle_box() -> None:
    result = type(
        "Result",
        (),
        {
            "boxes": FakeBoxes(
                [[10, 10, 50, 60], [45, 10, 75, 65]],
                [0.9, 0.8],
                [0, 1],
                [4, 9],
            ),
            "names": {0: "forklift", 1: "person"},
        },
    )()
    service = ForkliftService()
    service._model.predict = lambda *args, **kwargs: [result]

    response = service.detect(
        np.zeros((100, 120, 3), dtype=np.uint8),
        0.25,
    )

    assert response.detection_count == 2
    assert [item.class_name for item in response.detections] == [
        "forklift",
        "person",
    ]
    assert "proximity_alerts" not in response.model_dump()
    assert response.detections[0].box == BoundingBox(x1=6, y1=6, x2=54, y2=66)
    assert [item.track_id for item in response.detections] == [4, 9]


def test_forklift_tracker_uses_original_bytetrack_configuration() -> None:
    boxes = FakeBoxes([[10, 10, 40, 50]], [0.9], [0], [12])
    plotted = np.zeros((60, 80, 3), dtype=np.uint8)
    result = type(
        "Result",
        (),
        {
            "boxes": boxes,
            "names": {0: "forklift"},
            "plot": lambda self: plotted,
        },
    )()

    class FakeTrackingModel:
        def __init__(self) -> None:
            self.reset_count = 0
            self.options = {}

        def reset_tracking(self):
            self.reset_count += 1

        def track(self, image, **kwargs):
            self.options = kwargs
            return [result]

    tracker = ForkliftTracker()
    tracker._model = FakeTrackingModel()
    _annotated, response = tracker.process(
        np.zeros((60, 80, 3), dtype=np.uint8),
        0.25,
        "warehouse-camera",
    )

    assert response.detections[0].track_id == 12
    assert tracker._model.reset_count == 1
    assert tracker._model.options["persist"] is True
    assert tracker._model.options["tracker"] == str(
        settings.forklift_tracker_config_path
    )
