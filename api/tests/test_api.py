from __future__ import annotations

import cv2
import numpy as np
from fastapi.testclient import TestClient

from api.main import app
from api.schemas import ForkliftDetectionResponse
from api.services.live_privacy import LivePrivacyResult
from api.services.privacy import PrivacyMode


client = TestClient(app)


def jpeg_bytes() -> bytes:
    image = np.full((40, 60, 3), 180, dtype=np.uint8)
    success, encoded = cv2.imencode(".jpg", image)
    assert success
    return encoded.tobytes()


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}


def test_model_health_exposes_warmup_progress() -> None:
    response = client.get("/health/models")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"pending", "warming", "ready", "error"}
    assert body["total"] == 4
    assert set(body["models"]) == {"privacy", "people", "pose", "forklift"}


def test_favicon_request_does_not_return_error() -> None:
    response = client.get("/favicon.ico")

    assert response.status_code == 204


def test_theme_brand_assets_are_available_and_lightweight() -> None:
    for asset in ("brand-owl-light.webp", "brand-owl-dark.webp"):
        response = client.get(f"/static/assets/{asset}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/webp"
        assert len(response.content) < 100_000


def test_local_font_assets_are_available_and_lightweight() -> None:
    for asset in ("outfit-latin.woff2", "outfit-latin-ext.woff2"):
        response = client.get(f"/static/assets/fonts/{asset}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "font/woff2"
        assert len(response.content) < 50_000


def test_home_page_is_user_interface() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Görüntünüzü güvenle analiz edin." in response.text
    assert "Kişileri kaldır" in response.text
    assert "Vücut duruşunu analiz et" in response.text
    assert "Kameradan çek" in response.text
    assert "Koyu tema" in response.text
    assert 'id="workflow-title"' in response.text
    assert 'id="faq-title"' in response.text
    assert 'role="radio"' in response.text
    assert "github.com/vispection/KVKK_Safe_Human_Analysis" in response.text
    assert "linkedin.com/company/vispection" in response.text
    assert 'id="advanced-panel"' in response.text
    assert 'id="upload-queue"' in response.text
    assert 'id="batch-results"' in response.text
    assert 'id="live-status"' in response.text
    assert 'id="camera-quality-alert"' in response.text
    assert 'class="quick-guide"' in response.text
    assert 'id="language-select"' in response.text
    assert 'id="model-status-title"' in response.text
    assert 'class="learn-section"' in response.text
    assert 'id="info-detail-dialog"' in response.text
    assert 'class="about-section"' in response.text
    assert "Rana Yalçın" in response.text
    assert "Vispection AI" in response.text
    assert "/static/assets/brand-owl-light.webp" in response.text
    assert "/static/assets/brand-owl-dark.webp" in response.text
    assert 'class="panel-label-actions"' in response.text
    assert 'role="progressbar"' in response.text
    assert 'type="file"' in response.text and "multiple" in response.text
    assert "text/html" in response.headers["content-type"]


def test_api_docs_follow_saved_theme() -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "vispection_theme" in response.text
    assert 'html[data-theme="dark"]' in response.text
    assert "docs-home" in response.text


def test_invalid_content_type_is_rejected() -> None:
    response = client.post(
        "/api/v1/forklift/detect",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 415


def test_invalid_video_type_is_rejected() -> None:
    response = client.post(
        "/api/v1/privacy/anonymize-video",
        files={"file": ("notes.txt", b"not a video", "text/plain")},
    )

    assert response.status_code == 415


def test_invalid_video_job_operation_is_rejected() -> None:
    response = client.post(
        "/api/v1/jobs/video?operation=unknown",
        files={"file": ("test.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 400


def test_privacy_endpoint_returns_image(monkeypatch) -> None:
    def fake_anonymize(image, mode, confidence, image_size):
        assert mode == PrivacyMode.mosaic
        assert image_size == 640
        return image, 2, False

    monkeypatch.setattr(
        "api.routers.privacy.privacy_service.anonymize",
        fake_anonymize,
    )
    response = client.post(
        "/api/v1/privacy/anonymize?mode=mosaic",
        files={"file": ("test.jpg", jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.headers["x-face-count"] == "2"
    assert response.headers["x-fail-safe-applied"] == "false"


def test_live_privacy_endpoint_uses_tracking_pipeline(monkeypatch) -> None:
    def fake_process(image, mode, confidence, session_id, gesture_control):
        assert mode == PrivacyMode.soft_blur
        assert confidence == 0.55
        assert session_id == "camera-session-1"
        assert gesture_control is True
        return LivePrivacyResult(
            image=image,
            face_count=1,
            gesture_available=True,
            privacy_enabled=False,
            mode=PrivacyMode.soft_blur,
            gesture="PINCH",
        )

    monkeypatch.setattr(
        "api.routers.privacy.live_privacy_service.process",
        fake_process,
    )
    response = client.post(
        "/api/v1/privacy/live?mode=soft_blur&confidence=0.55&session_id=camera-session-1&gesture_control=true",
        files={"file": ("frame.jpg", jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["x-face-count"] == "1"
    assert response.headers["x-tracking-enabled"] == "true"
    assert response.headers["x-gesture"] == "PINCH"
    assert response.headers["x-privacy-enabled"] == "false"
    assert float(response.headers["x-processing-time-ms"]) >= 0
    assert response.headers["server-timing"].startswith("analysis;dur=")


def test_live_people_endpoint_uses_bytetrack(monkeypatch) -> None:
    def fake_track(image, mode, confidence, session_id, image_size):
        assert mode.value == "blur"
        assert confidence == 0.3
        assert session_id == "people-camera"
        assert image_size == 320
        return image, 2

    monkeypatch.setattr("api.routers.people.people_service.track", fake_track)
    response = client.post(
        "/api/v1/people/live?mode=blur&confidence=0.3&session_id=people-camera",
        files={"file": ("frame.jpg", jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-person-count"] == "2"
    assert response.headers["x-tracking-enabled"] == "bytetrack"
    assert response.headers["x-live-overlay"] == "true"


def test_live_pose_endpoint_uses_bytetrack(monkeypatch) -> None:
    def fake_track(image, confidence, session_id, image_size):
        assert confidence == 0.35
        assert session_id == "pose-camera"
        assert image_size == 320
        return image, 3

    monkeypatch.setattr("api.routers.pose.pose_service.track", fake_track)
    response = client.post(
        "/api/v1/pose/live?confidence=0.35&session_id=pose-camera",
        files={"file": ("frame.jpg", jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-pose-count"] == "3"
    assert response.headers["x-tracking-enabled"] == "bytetrack"
    assert response.headers["x-live-overlay"] == "true"


def test_forklift_endpoint_returns_json(monkeypatch) -> None:
    def fake_detect(image, confidence, image_size):
        assert image_size == 640
        height, width = image.shape[:2]
        return ForkliftDetectionResponse(
            image_width=width,
            image_height=height,
            detection_count=0,
            detections=[],
        )

    monkeypatch.setattr(
        "api.routers.forklift.forklift_service.detect",
        fake_detect,
    )
    response = client.post(
        "/api/v1/forklift/detect",
        files={"file": ("test.jpg", jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["image_width"] == 60
    assert response.json()["detection_count"] == 0
    assert float(response.headers["x-processing-time-ms"]) >= 0
    assert response.headers["server-timing"].startswith("analysis;dur=")


def test_live_forklift_endpoint_enables_bytetrack(monkeypatch) -> None:
    def fake_track(image, confidence, session_id, image_size):
        assert session_id == "warehouse-camera"
        assert image_size == 384
        height, width = image.shape[:2]
        return ForkliftDetectionResponse(
            image_width=width,
            image_height=height,
            detection_count=0,
            detections=[],
        )

    monkeypatch.setattr(
        "api.routers.forklift.forklift_service.track",
        fake_track,
    )
    response = client.post(
        "/api/v1/forklift/detect?fast=true&session_id=warehouse-camera",
        files={"file": ("frame.jpg", jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.headers["x-tracking-enabled"] == "bytetrack"
