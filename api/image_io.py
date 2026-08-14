from __future__ import annotations

from io import BytesIO

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from api.config import settings


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def read_image(upload: UploadFile) -> np.ndarray:
    """Validate an upload and decode it into an OpenCV BGR image."""
    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Yalnızca JPEG, PNG veya WebP görüntüsü yüklenebilir.",
        )

    content = await upload.read(settings.max_upload_bytes + 1)
    await upload.close()

    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Yüklenen görüntü izin verilen boyutu aşıyor.",
        )

    try:
        with Image.open(BytesIO(content)) as probe:
            width, height = probe.size
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosyanın içeriği geçerli bir görüntü biçimi değil.",
        ) from error

    if width <= 0 or height <= 0 or width * height > settings.max_image_pixels:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Görüntü çözünürlüğü güvenli işleme sınırını aşıyor.",
        )

    image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosya geçerli bir görüntü olarak çözümlenemedi.",
        )

    return image


def encode_jpeg(image: np.ndarray, quality: int = 92) -> bytes:
    quality = max(40, min(100, int(quality)))
    success, encoded = cv2.imencode(
        ".jpg",
        image,
        [cv2.IMWRITE_JPEG_QUALITY, quality],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="İşlenmiş görüntü kodlanamadı.",
        )
    return encoded.tobytes()


def encode_live_overlay(original: np.ndarray, processed: np.ndarray) -> bytes:
    """Encode only changed pixels so the live camera can keep moving below it."""
    if original.shape != processed.shape:
        raise ValueError("Canlı analiz katmanı görüntü boyutuyla eşleşmiyor.")

    difference = cv2.absdiff(original, processed)
    changed = np.max(difference, axis=2).astype(np.uint8)
    _, alpha = cv2.threshold(changed, 2, 255, cv2.THRESH_BINARY)
    alpha = cv2.dilate(alpha, np.ones((5, 5), dtype=np.uint8), iterations=1)
    overlay = cv2.cvtColor(processed, cv2.COLOR_BGR2BGRA)
    overlay[:, :, 3] = alpha
    success, encoded = cv2.imencode(
        ".png",
        overlay,
        [cv2.IMWRITE_PNG_COMPRESSION, 1],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Canlı analiz katmanı kodlanamadı.",
        )
    return encoded.tobytes()
