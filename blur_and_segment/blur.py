import cv2
import numpy as np


def odd_number(value):
    value = max(3, int(value))

    if value % 2 == 0:
        value += 1

    return value


def expand_box(box, frame_shape, padding_ratio=0.08):
    x1, y1, x2, y2 = box
    height, width = frame_shape[:2]

    box_width = max(0, x2 - x1)
    box_height = max(0, y2 - y1)

    padding_x = int(box_width * padding_ratio)
    padding_y = int(box_height * padding_ratio)

    return (
        max(0, x1 - padding_x),
        max(0, y1 - padding_y),
        min(width, x2 + padding_x),
        min(height, y2 + padding_y),
    )


def apply_blur(
    frame,
    box,
    blur_strength=61,
    padding_ratio=0.08,
):
    """
    Bounding box bölgesine yumuşak kenarlı blur uygular.

    Segmentasyon bulunamadığında yedek yöntem olarak kullanılır.
    """
    x1, y1, x2, y2 = expand_box(
        box,
        frame.shape,
        padding_ratio,
    )

    if x2 <= x1 or y2 <= y1:
        return frame

    region = frame[y1:y2, x1:x2]

    if region.size == 0:
        return frame

    region_height, region_width = region.shape[:2]

    maximum_kernel = min(
        region_width,
        region_height,
        blur_strength,
    )

    kernel = odd_number(maximum_kernel)

    if kernel > region_width:
        kernel = odd_number(max(3, region_width - 1))

    if kernel > region_height:
        kernel = odd_number(max(3, region_height - 1))

    blurred_region = cv2.GaussianBlur(
        region,
        (kernel, kernel),
        0,
    )

    # Dikdörtgen kenarlarını daha doğal yapmak için
    # yumuşak alpha maskesi oluştur.
    mask = np.full(
        (region_height, region_width),
        255,
        dtype=np.uint8,
    )

    feather_size = odd_number(
        min(31, region_width, region_height)
    )

    mask = cv2.GaussianBlur(
        mask,
        (feather_size, feather_size),
        0,
    )

    alpha = mask.astype(np.float32) / 255.0
    alpha = alpha[..., np.newaxis]

    blended_region = (
        blurred_region.astype(np.float32) * alpha
        + region.astype(np.float32) * (1.0 - alpha)
    )

    frame[y1:y2, x1:x2] = np.clip(
        blended_region,
        0,
        255,
    ).astype(np.uint8)

    return frame


def apply_full_frame_blur(frame, blur_strength=101):
    kernel = odd_number(blur_strength)

    return cv2.GaussianBlur(
        frame,
        (kernel, kernel),
        0,
    )


def _to_numpy(value):
    if value is None:
        return np.empty((0, 4), dtype=np.float32)
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def _fill_polygon(mask, polygon):
    """Fill one person mask, including multipart Ultralytics polygons."""
    if polygon is None:
        return False

    try:
        points = np.asarray(polygon)
    except (TypeError, ValueError):
        points = np.asarray([], dtype=np.float32)

    if points.ndim == 2 and points.shape[0] >= 3 and points.shape[1] >= 2:
        cv2.fillPoly(mask, [points[:, :2].astype(np.int32)], 255)
        return True

    painted = False
    if isinstance(polygon, (list, tuple)) or points.ndim > 2:
        for part in polygon:
            painted = _fill_polygon(mask, part) or painted
    return painted


def _fill_box_fallback(mask, box, frame_shape):
    """Protect a detected person when its segmentation polygon is missing."""
    if box is None or len(box) < 4:
        return False
    x1, y1, x2, y2 = expand_box(
        tuple(map(int, box[:4])),
        frame_shape,
        padding_ratio=0.05,
    )
    if x2 <= x1 or y2 <= y1:
        return False
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    return True


def create_person_mask(
    frame_shape,
    segmentation_results,
    dilation_size=21,
    feather_size=31,
    restrict_to_segmentation=False,
):
    height, width = frame_shape[:2]

    mask = np.zeros(
        (height, width),
        dtype=np.uint8,
    )

    person_count = 0

    for result in segmentation_results:
        result_masks = getattr(result, "masks", None)
        polygons = list(getattr(result_masks, "xy", None) or [])
        result_boxes = getattr(result, "boxes", None)
        boxes = _to_numpy(getattr(result_boxes, "xyxy", None))
        if boxes.ndim == 1 and boxes.size >= 4:
            boxes = boxes.reshape(1, -1)
        if boxes.ndim != 2:
            boxes = np.empty((0, 4), dtype=np.float32)

        # A difficult frame may contain a valid person box but no usable mask.
        # Match by detection index and fall back to that box instead of silently
        # leaving the person visible.
        for index in range(max(len(polygons), len(boxes))):
            painted = index < len(polygons) and _fill_polygon(mask, polygons[index])
            if not painted and index < len(boxes) and not restrict_to_segmentation:
                painted = _fill_box_fallback(mask, boxes[index], frame_shape)
            if painted:
                person_count += 1

    if person_count == 0:
        return mask, 0

    person_outline = mask.copy()

    # Saç, el, ayak ve kıyafet kenarlarının açıkta
    # kalma ihtimalini azaltmak için maskeyi genişlet.
    dilation_size = odd_number(dilation_size)

    dilation_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (dilation_size, dilation_size),
    )

    mask = cv2.dilate(
        mask,
        dilation_kernel,
        iterations=1,
    )

    # Maskenin kenarlarını yumuşat.
    feather_size = odd_number(feather_size)

    mask = cv2.GaussianBlur(
        mask,
        (feather_size, feather_size),
        0,
    )

    if restrict_to_segmentation:
        # Keep every background pixel byte-for-byte unchanged. Feathering is
        # allowed only on the inside of the detected person silhouette.
        mask[person_outline == 0] = 0

    return mask, person_count


def apply_segmentation_blur(
    frame,
    segmentation_results,
    blur_strength=71,
    dilation_size=21,
    feather_size=31,
    restrict_to_segmentation=False,
):
    """
    YOLO segmentasyon maskesine göre tüm insan vücudunu blur uygular.
    """
    mask, mask_count = create_person_mask(
        frame.shape,
        segmentation_results,
        dilation_size=dilation_size,
        feather_size=feather_size,
        restrict_to_segmentation=restrict_to_segmentation,
    )

    if mask_count == 0:
        return frame.copy(), 0, 0.0

    blur_strength = odd_number(blur_strength)

    # Blur only the union mask's bounding region. This produces the same
    # protected output without applying a large Gaussian kernel to background
    # pixels that will never be used.
    active_pixels = cv2.findNonZero(mask)
    if active_pixels is None:
        return frame.copy(), 0, 0.0
    x, y, width, height = cv2.boundingRect(active_pixels)
    source_region = frame[y:y + height, x:x + width]
    mask_region = mask[y:y + height, x:x + width]
    blurred_region = cv2.GaussianBlur(
        source_region,
        (blur_strength, blur_strength),
        0,
    )
    alpha = (mask_region.astype(np.float32) / 255.0)[..., np.newaxis]
    blended_region = (
        blurred_region.astype(np.float32) * alpha
        + source_region.astype(np.float32) * (1.0 - alpha)
    )
    output = frame.copy()
    output[y:y + height, x:x + width] = np.clip(
        blended_region,
        0,
        255,
    ).astype(np.uint8)

    mask_coverage = (
        float(np.count_nonzero(mask))
        / float(mask.size)
    )

    return output, mask_count, mask_coverage
