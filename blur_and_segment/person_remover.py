import cv2

from blur_and_segment.blur import create_person_mask


def remove_people(frame, segmentation_results):
    """Remove every detected person, including detections with missing masks."""
    mask, person_count = create_person_mask(
        frame.shape,
        segmentation_results,
        dilation_size=17,
        feather_size=3,
    )

    if person_count == 0:
        return frame.copy(), 0

    output = cv2.inpaint(
        frame,
        mask,
        5,
        cv2.INPAINT_TELEA,
    )

    return output, person_count
