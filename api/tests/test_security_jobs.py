from __future__ import annotations

from time import time

from fastapi.testclient import TestClient

from api.config import settings
from api.jobs import VideoJob, VideoJobManager
from api.main import app
from api.security import rate_limiter
from api.tests.test_api import jpeg_bytes


client = TestClient(app)


def test_security_headers_and_private_api_cache_policy() -> None:
    page = client.get("/")
    api_response = client.post(
        "/api/v1/forklift/detect",
        files={"file": ("notes.txt", b"invalid", "text/plain")},
    )

    assert page.headers["x-content-type-options"] == "nosniff"
    assert page.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in page.headers["content-security-policy"]
    assert "camera=(self)" in page.headers["permissions-policy"]
    assert api_response.headers["cache-control"] == "no-store, max-age=0"


def test_spoofed_video_content_is_rejected_before_job_creation() -> None:
    response = client.post(
        "/api/v1/jobs/video?operation=privacy",
        files={"file": ("fake.mp4", b"not-a-real-video", "video/mp4")},
    )

    assert response.status_code == 400
    assert "eşleşmiyor" in response.json()["detail"]


def test_excessive_image_resolution_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(settings, "max_image_pixels", 1)
    response = client.post(
        "/api/v1/privacy/anonymize",
        files={"file": ("large.jpg", jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 413
    assert "çözünürlüğü" in response.json()["detail"]


def test_api_key_is_optional_and_enforced_when_configured(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", "test-secret")
    rate_limiter.clear()

    missing_key = client.post(
        "/api/v1/forklift/detect",
        files={"file": ("notes.txt", b"invalid", "text/plain")},
    )
    valid_key = client.post(
        "/api/v1/forklift/detect",
        headers={"X-API-Key": "test-secret"},
        files={"file": ("notes.txt", b"invalid", "text/plain")},
    )

    assert missing_key.status_code == 401
    assert valid_key.status_code == 415


def test_mutating_api_requests_are_rate_limited(monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", None)
    monkeypatch.setattr(settings, "rate_limit_requests", 2)
    monkeypatch.setattr(settings, "rate_limit_window_seconds", 60)
    rate_limiter.clear()

    responses = [
        client.post(
            "/api/v1/forklift/detect",
            files={"file": ("notes.txt", b"invalid", "text/plain")},
        )
        for _ in range(3)
    ]

    assert [response.status_code for response in responses] == [415, 415, 429]
    assert responses[-1].headers["retry-after"]


def test_expired_video_jobs_and_files_are_cleaned(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(settings, "video_job_ttl_seconds", 10)
    manager = VideoJobManager()
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    input_path.write_bytes(b"input")
    output_path.write_bytes(b"output")
    job = VideoJob(
        id="expired-job",
        operation="privacy",
        input_path=input_path,
        output_path=output_path,
        status="completed",
        finished_at=time() - 11,
    )
    with manager._lock:
        manager._jobs[job.id] = job

    try:
        assert manager.cleanup_expired() == 1
        assert manager.get(job.id) is None
        assert not input_path.exists()
        assert not output_path.exists()
    finally:
        manager.shutdown()
