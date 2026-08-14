from __future__ import annotations

import numpy as np

from api.services.vision_preprocess import enhance_for_detection


def test_dark_frame_is_enhanced_for_model_inference() -> None:
    gradient = np.linspace(8, 65, 160, dtype=np.uint8)
    gray = np.tile(gradient, (100, 1))
    image = np.repeat(gray[..., None], 3, axis=2)

    enhanced = enhance_for_detection(image)

    assert enhanced.shape == image.shape
    assert enhanced.dtype == image.dtype
    assert float(np.mean(enhanced)) > float(np.mean(image))
    assert not np.shares_memory(enhanced, image)


def test_well_lit_high_contrast_frame_is_not_modified() -> None:
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    image[:, :60] = 70
    image[:, 60:] = 220

    enhanced = enhance_for_detection(image)

    assert enhanced is image
