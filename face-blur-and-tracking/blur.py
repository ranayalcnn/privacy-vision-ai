import cv2


def apply_blur(frame, box):
    """Apply the original Gaussian face blur inside a safe image boundary."""
    x1, y1, x2, y2 = box
    height, width = frame.shape[:2]
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)

    if x2 <= x1 or y2 <= y1:
        return frame

    face = frame[y1:y2, x1:x2]
    if face.size == 0:
        return frame

    frame[y1:y2, x1:x2] = cv2.GaussianBlur(face, (51, 51), 20)
    return frame
