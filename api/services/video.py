from __future__ import annotations

from collections import Counter
from pathlib import Path
import subprocess
from threading import Event
from typing import Callable

import cv2
import imageio_ffmpeg

from api.config import settings
from api.services.forklift import forklift_service
from api.services.people import PeopleMode, people_service
from api.services.pose import pose_service
from api.services.privacy import PrivacyMode
from api.services.tracked_face_pipeline import TrackedFacePipeline


class VideoProcessingError(RuntimeError):
    pass


class VideoProcessingCancelled(VideoProcessingError):
    pass


ProgressCallback = Callable[[int, int], None]


def report_progress(
    capture: cv2.VideoCapture,
    processed_frames: int,
    callback: ProgressCallback | None,
    cancel_event: Event | None,
) -> None:
    if cancel_event is not None and cancel_event.is_set():
        raise VideoProcessingCancelled("Video işlemi kullanıcı tarafından iptal edildi.")
    if callback is not None:
        total_frames = max(
            processed_frames,
            int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        )
        callback(processed_frames, total_frames)


def video_properties(capture: cv2.VideoCapture) -> tuple[float, int, int]:
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0:
        fps = 25.0
    if width <= 0 or height <= 0:
        raise VideoProcessingError("Video boyutları okunamadı.")
    return fps, width, height


def open_video_writer(
    output_path: Path,
    fps: float,
    width: int,
    height: int,
) -> cv2.VideoWriter:
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        raise VideoProcessingError("İşlenmiş video oluşturulamadı.")
    return writer


def make_browser_compatible(path: Path) -> None:
    """Transcode OpenCV's output to browser-friendly H.264."""
    converted = path.with_name(f"{path.stem}.browser.mp4")
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y",
        "-i",
        str(path),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(converted),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0 or not converted.is_file():
        converted.unlink(missing_ok=True)
        raise VideoProcessingError("Video tarayıcı biçimine dönüştürülemedi.")
    converted.replace(path)


def anonymize_video(
    input_path: Path,
    output_path: Path,
    mode: PrivacyMode,
    confidence: float,
    progress_callback: ProgressCallback | None = None,
    cancel_event: Event | None = None,
) -> dict[str, int]:
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise VideoProcessingError("Yüklenen video açılamadı.")

    writer = None
    frame_count = 0
    protected_face_count = 0
    fail_safe_frame_count = 0
    audit_path = settings.runtime_dir / f"{output_path.stem}_privacy_audit.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    tracker = TrackedFacePipeline(
        model_path=settings.face_model_path,
        audit_path=audit_path,
        confidence=confidence,
        image_size=960,
        minimum_face_size=6,
    )
    tracker.privacy_mode.set_mode(
        {
            PrivacyMode.soft_blur: 1,
            PrivacyMode.mosaic: 2,
            PrivacyMode.color_shield: 3,
        }[mode]
    )
    try:
        fps, width, height = video_properties(capture)
        writer = open_video_writer(output_path, fps, width, height)

        while True:
            report_progress(capture, frame_count, progress_callback, cancel_event)
            success, frame = capture.read()
            if not success:
                break
            protected, face_count = tracker.process(frame)
            fail_safe = face_count == 0
            writer.write(protected)
            frame_count += 1
            protected_face_count += face_count
            fail_safe_frame_count += int(fail_safe)
    finally:
        capture.release()
        if writer is not None:
            writer.release()

    if frame_count == 0:
        output_path.unlink(missing_ok=True)
        raise VideoProcessingError("Videoda işlenebilir kare bulunamadı.")

    report_progress(capture, frame_count, progress_callback, cancel_event)
    make_browser_compatible(output_path)
    return {
        "frame_count": frame_count,
        "face_count": protected_face_count,
        "fail_safe_frame_count": fail_safe_frame_count,
    }


def detect_video(
    input_path: Path,
    output_path: Path,
    confidence: float,
    progress_callback: ProgressCallback | None = None,
    cancel_event: Event | None = None,
) -> dict[str, int]:
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise VideoProcessingError("Yüklenen video açılamadı.")

    writer = None
    frame_count = 0
    counts: Counter[str] = Counter()
    tracker = forklift_service.create_tracker()
    tracking_session_id = f"video-{input_path.stem}"
    try:
        fps, width, height = video_properties(capture)
        writer = open_video_writer(output_path, fps, width, height)

        while True:
            report_progress(capture, frame_count, progress_callback, cancel_event)
            success, frame = capture.read()
            if not success:
                break
            annotated, response = tracker.process(
                frame,
                confidence,
                tracking_session_id,
            )
            writer.write(annotated)
            frame_count += 1
            counts.update(item.class_name for item in response.detections)
    finally:
        capture.release()
        if writer is not None:
            writer.release()

    if frame_count == 0:
        output_path.unlink(missing_ok=True)
        raise VideoProcessingError("Videoda işlenebilir kare bulunamadı.")

    report_progress(capture, frame_count, progress_callback, cancel_event)
    make_browser_compatible(output_path)
    return {
        "frame_count": frame_count,
        "forklift_count": counts["forklift"],
        "person_count": counts["person"],
        "pallet_count": counts["pallet"],
        "pallet_truck_count": counts["pallet_truck"],
    }


def process_people_video(
    input_path: Path,
    output_path: Path,
    mode: PeopleMode,
    confidence: float,
    progress_callback: ProgressCallback | None = None,
    cancel_event: Event | None = None,
    selected_point: tuple[float, float] | None = None,
) -> dict[str, int]:
    tracker = people_service.create_tracker()
    tracking_session_id = f"people-video-{input_path.stem}"
    return _transform_video(
        input_path,
        output_path,
        lambda frame: tracker.process(
            frame,
            mode,
            confidence,
            tracking_session_id,
            selected_point,
        ),
        "person_count",
        progress_callback,
        cancel_event,
    )


def estimate_pose_video(
    input_path: Path,
    output_path: Path,
    confidence: float,
    progress_callback: ProgressCallback | None = None,
    cancel_event: Event | None = None,
) -> dict[str, int]:
    tracker = pose_service.create_tracker()
    tracking_session_id = f"pose-video-{input_path.stem}"
    return _transform_video(
        input_path,
        output_path,
        lambda frame: tracker.process(frame, confidence, tracking_session_id),
        "pose_count",
        progress_callback,
        cancel_event,
    )


def _transform_video(
    input_path: Path,
    output_path: Path,
    transform,
    count_key: str,
    progress_callback: ProgressCallback | None = None,
    cancel_event: Event | None = None,
) -> dict[str, int]:
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise VideoProcessingError("Yüklenen video açılamadı.")

    writer = None
    frame_count = 0
    item_count = 0
    try:
        fps, width, height = video_properties(capture)
        writer = open_video_writer(output_path, fps, width, height)
        while True:
            report_progress(capture, frame_count, progress_callback, cancel_event)
            success, frame = capture.read()
            if not success:
                break
            processed, count = transform(frame)
            writer.write(processed)
            frame_count += 1
            item_count += count
    finally:
        capture.release()
        if writer is not None:
            writer.release()

    if frame_count == 0:
        output_path.unlink(missing_ok=True)
        raise VideoProcessingError("Videoda işlenebilir kare bulunamadı.")

    report_progress(capture, frame_count, progress_callback, cancel_event)
    make_browser_compatible(output_path)
    return {"frame_count": frame_count, count_key: item_count}
