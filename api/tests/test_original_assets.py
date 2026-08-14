from __future__ import annotations

from api.config import PROJECT_ROOT, settings
from blur_and_segment.blur import apply_segmentation_blur
from blur_and_segment.person_remover import remove_people
from realtime_pipeline.mode import PrivacyMode
from realtime_pipeline.privacy_compliance import fail_safe


def test_api_uses_original_analysis_functions() -> None:
    assert apply_segmentation_blur.__module__ == "blur_and_segment.blur"
    assert remove_people.__module__ == "blur_and_segment.person_remover"
    assert PrivacyMode.__module__ == "realtime_pipeline.mode"
    assert fail_safe.__module__ == "realtime_pipeline.privacy_compliance"


def test_api_uses_models_from_original_project_folders() -> None:
    expected_models = {
        settings.face_model_path: PROJECT_ROOT / "blur_and_segment" / "yolov8n-face.pt",
        settings.segmentation_model_path: PROJECT_ROOT / "blur_and_segment" / "yolo11s-seg.pt",
        settings.pose_model_path: PROJECT_ROOT / "blur_and_segment" / "yolo11n-pose.pt",
        settings.forklift_model_path: (
            PROJECT_ROOT
            / "FORKLIFT DETECTION"
            / "models"
            / "forklift_yolo11s_multivideo_best.pt"
        ),
    }
    for configured_path, expected_path in expected_models.items():
        assert configured_path == expected_path
        assert configured_path.is_file()
