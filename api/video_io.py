from __future__ import annotations

import uuid
from pathlib import Path

import cv2
from fastapi import HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from api.config import settings


ALLOWED_VIDEO_TYPES = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/x-msvideo": ".avi",
    "video/webm": ".webm",
}


def _matches_video_signature(content_type: str, header: bytes) -> bool:
    if content_type in {"video/mp4", "video/quicktime"}:
        return len(header) >= 12 and header[4:8] == b"ftyp"
    if content_type == "video/x-msvideo":
        return len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"AVI "
    if content_type == "video/webm":
        return header.startswith(b"\x1a\x45\xdf\xa3")
    return False


def _validate_video_metadata(path: Path) -> None:
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError("open")
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if width <= 0 or height <= 0 or fps <= 0 or frames <= 0:
            raise ValueError("metadata")
        if width * height > settings.max_video_pixels:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Video çözünürlüğü en fazla 4K olabilir.",
            )
        if frames / fps > settings.max_video_duration_seconds:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Video süresi en fazla 10 dakika olabilir.",
            )
    except HTTPException:
        raise
    except (ValueError, OSError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosyanın içeriği geçerli veya okunabilir bir video değil.",
        ) from error
    finally:
        capture.release()


async def save_video_upload(upload: UploadFile) -> Path:
    """Validate and stream an uploaded video into the private runtime folder."""
    content_type = upload.content_type or ""
    suffix = ALLOWED_VIDEO_TYPES.get(content_type)
    if suffix is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Yalnızca MP4, MOV, AVI veya WebM videosu yüklenebilir.",
        )

    upload_dir = settings.runtime_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{uuid.uuid4().hex}{suffix}"
    total_bytes = 0
    header = bytearray()

    try:
        with destination.open("wb") as stream:
            while chunk := await upload.read(1024 * 1024):
                if len(header) < 16:
                    header.extend(chunk[: 16 - len(header)])
                total_bytes += len(chunk)
                if total_bytes > settings.max_video_upload_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="Video 250 MB sınırını aşıyor.",
                    )
                stream.write(chunk)
        if not _matches_video_signature(content_type, bytes(header)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dosya uzantısı ile gerçek video biçimi eşleşmiyor.",
            )
        await run_in_threadpool(_validate_video_metadata, destination)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return destination


def output_video_path() -> Path:
    output_dir = settings.runtime_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{uuid.uuid4().hex}.mp4"


def remove_runtime_files(*paths: Path) -> None:
    for path in paths:
        path.unlink(missing_ok=True)
