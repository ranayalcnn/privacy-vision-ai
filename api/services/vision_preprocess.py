from __future__ import annotations

import cv2
import numpy as np


def enhance_for_detection(image: np.ndarray) -> np.ndarray:
    """Improve dark/flat frames for inference without changing final output."""
    if image.size == 0:
        return image

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    if brightness >= 105.0 and contrast >= 38.0:
        return image

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, channel_a, channel_b = cv2.split(lab)
    clip_limit = 2.6 if brightness < 70.0 else 2.0
    corrected_lightness = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(8, 8),
    ).apply(lightness)
    corrected = cv2.cvtColor(
        cv2.merge((corrected_lightness, channel_a, channel_b)),
        cv2.COLOR_LAB2BGR,
    )

    strength = float(np.clip((120.0 - brightness) / 100.0, 0.25, 0.82))
    return cv2.addWeighted(image, 1.0 - strength, corrected, strength, 0)
