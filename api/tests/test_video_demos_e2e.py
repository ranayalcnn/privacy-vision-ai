from __future__ import annotations

import os
from pathlib import Path
from threading import Event

import pytest

from api.config import PROJECT_ROOT
from api.services.people import PeopleMode
from api.services.privacy import PrivacyMode
from api.services.video import (
    anonymize_video,
    detect_video,
    estimate_pose_video,
    process_people_video,
)


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_MODEL_E2E") != "1",
    reason="Gerçek model testleri RUN_MODEL_E2E=1 ile çalıştırılır.",
)

SAMPLE_DIR = PROJECT_ROOT / "api" / "static" / "samples"
DEMO_VIDEOS = {
    "privacy": SAMPLE_DIR / "face-privacy-demo.mp4",
    "people_blur": SAMPLE_DIR / "people-blur-demo.mp4",
    "people_remove": SAMPLE_DIR / "people-remove-demo.mp4",
    "pose": SAMPLE_DIR / "multi-person-pose-demo.mp4",
    "forklift": SAMPLE_DIR / "warehouse-demo.mp4",
}


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("operation", "sample_path", "expected_stat"),
    [
        ("privacy", DEMO_VIDEOS["privacy"], "face_count"),
        ("people_blur", DEMO_VIDEOS["people_blur"], "person_count"),
        ("people_remove", DEMO_VIDEOS["people_remove"], "person_count"),
        ("pose", DEMO_VIDEOS["pose"], "pose_count"),
        ("forklift", DEMO_VIDEOS["forklift"], "forklift_count"),
    ],
)
def test_demo_video_with_real_model(
    operation: str,
    sample_path: Path,
    expected_stat: str,
    tmp_path: Path,
) -> None:
    assert sample_path.is_file()
    output_path = tmp_path / f"{operation}.mp4"
    cancel_event = Event()

    if operation == "privacy":
        stats = anonymize_video(
            sample_path,
            output_path,
            PrivacyMode.soft_blur,
            0.55,
            cancel_event=cancel_event,
        )
    elif operation == "people_blur":
        stats = process_people_video(
            sample_path,
            output_path,
            PeopleMode.blur,
            0.25,
            cancel_event=cancel_event,
        )
    elif operation == "people_remove":
        stats = process_people_video(
            sample_path,
            output_path,
            PeopleMode.remove,
            0.25,
            cancel_event=cancel_event,
        )
    elif operation == "pose":
        stats = estimate_pose_video(
            sample_path,
            output_path,
            0.25,
            cancel_event=cancel_event,
        )
    else:
        stats = detect_video(
            sample_path,
            output_path,
            0.25,
            cancel_event=cancel_event,
        )

    assert output_path.is_file()
    assert output_path.stat().st_size > 0
    assert stats["frame_count"] > 0
    assert expected_stat in stats
    assert stats[expected_stat] > 0
    if operation == "privacy":
        # The privacy demo contains two visible faces throughout the clip.
        assert stats[expected_stat] >= stats["frame_count"] * 2
    if operation in {"people_blur", "people_remove"}:
        # Both tailored demos contain two people in every frame. This catches
        # regressions where only the first segmentation mask is processed.
        assert stats[expected_stat] >= stats["frame_count"] * 2
    if operation == "pose":
        # The pose demo deliberately keeps three complete walkers in frame.
        assert stats[expected_stat] >= stats["frame_count"] * 3
    if operation == "forklift":
        # The warehouse demo keeps the forklift in frame throughout. ByteTrack
        # and short-gap prediction must keep it visible in every single frame.
        assert stats[expected_stat] >= stats["frame_count"]


@pytest.mark.e2e
def test_selected_person_is_tracked_and_removed_across_video(tmp_path: Path) -> None:
    output_path = tmp_path / "selected-person-remove.mp4"
    stats = process_people_video(
        DEMO_VIDEOS["people_remove"],
        output_path,
        PeopleMode.remove,
        0.20,
        selected_point=(0.25, 0.60),
    )

    assert output_path.is_file()
    assert stats["frame_count"] == 50
    assert stats["person_count"] == stats["frame_count"]
