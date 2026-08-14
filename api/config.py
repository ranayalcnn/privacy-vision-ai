from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings:
    """Runtime settings, overridable with environment variables."""

    title = "KVKK Safe Human Analysis API"
    version = "1.0.0"
    max_upload_bytes = int(os.getenv("API_MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
    max_video_upload_bytes = int(
        os.getenv("API_MAX_VIDEO_UPLOAD_BYTES", 250 * 1024 * 1024)
    )
    max_image_pixels = int(os.getenv("API_MAX_IMAGE_PIXELS", 25_000_000))
    max_video_pixels = int(os.getenv("API_MAX_VIDEO_PIXELS", 3840 * 2160))
    max_video_duration_seconds = int(
        os.getenv("API_MAX_VIDEO_DURATION_SECONDS", 600)
    )
    api_key = os.getenv("API_KEY") or None
    rate_limit_requests = int(os.getenv("API_RATE_LIMIT_REQUESTS", 240))
    rate_limit_window_seconds = int(os.getenv("API_RATE_LIMIT_WINDOW_SECONDS", 60))
    video_job_ttl_seconds = int(os.getenv("API_VIDEO_JOB_TTL_SECONDS", 3600))
    video_job_cleanup_interval_seconds = int(
        os.getenv("API_VIDEO_JOB_CLEANUP_INTERVAL_SECONDS", 60)
    )
    max_active_video_jobs = int(os.getenv("API_MAX_ACTIVE_VIDEO_JOBS", 3))
    runtime_dir = Path(os.getenv("API_RUNTIME_DIR", PROJECT_ROOT / ".runtime"))

    face_model_path = Path(
        os.getenv(
            "FACE_MODEL_PATH",
            PROJECT_ROOT / "blur_and_segment" / "yolov8n-face.pt",
        )
    )
    forklift_model_path = Path(
        os.getenv(
            "FORKLIFT_MODEL_PATH",
            PROJECT_ROOT
            / "FORKLIFT DETECTION"
            / "models"
            / "forklift_yolo11s_multivideo_best.pt",
        )
    )
    forklift_tracker_config_path = (
        PROJECT_ROOT / "FORKLIFT DETECTION" / "configs" / "bytetrack_forklift.yaml"
    )
    segmentation_model_path = Path(
        os.getenv(
            "SEGMENTATION_MODEL_PATH",
            PROJECT_ROOT / "blur_and_segment" / "yolo11s-seg.pt",
        )
    )
    pose_model_path = Path(
        os.getenv(
            "POSE_MODEL_PATH",
            PROJECT_ROOT / "blur_and_segment" / "yolo11n-pose.pt",
        )
    )


settings = Settings()
