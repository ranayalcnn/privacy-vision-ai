from __future__ import annotations

import cv2
import numpy as np

from api.image_io import encode_live_overlay


def test_live_overlay_keeps_unchanged_pixels_transparent() -> None:
    original = np.full((30, 40, 3), 120, dtype=np.uint8)
    processed = original.copy()
    processed[10:20, 12:28] = (20, 180, 70)

    encoded = encode_live_overlay(original, processed)
    overlay = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

    assert overlay.shape == (30, 40, 4)
    assert overlay[0, 0, 3] == 0
    assert overlay[15, 20, 3] == 255


def test_live_overlay_rejects_mismatched_frames() -> None:
    original = np.zeros((10, 10, 3), dtype=np.uint8)
    processed = np.zeros((9, 10, 3), dtype=np.uint8)

    try:
        encode_live_overlay(original, processed)
    except ValueError as error:
        assert "eşleşmiyor" in str(error)
    else:
        raise AssertionError("Boyutu eşleşmeyen kare reddedilmeliydi.")
