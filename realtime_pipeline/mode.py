import cv2
import numpy as np


class PrivacyMode:
    MODES = {
        1: ("SOFT BLUR", (214, 156, 62)),
        2: ("MOSAIC", (190, 112, 172)),
        3: ("COLOR SHIELD", (180, 190, 52)),
    }

    def __init__(self):
        self.mode_id = 1
        self.mode = self.MODES[1][0]

    def set_mode(self, mode_id):
        if mode_id in self.MODES:
            self.mode_id = mode_id
            self.mode = self.MODES[mode_id][0]

    def get_color(self):
        return self.MODES[self.mode_id][1]

    def apply(self, frame, boxes):
        for x1, y1, x2, y2 in boxes:
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)

            if x2 <= x1 or y2 <= y1:
                continue

            face = frame[y1:y2, x1:x2].copy()
            width = x2 - x1
            height = y2 - y1

            if self.mode_id == 1:
                # Oval and feathered blending follows the face shape more
                # naturally than a visible rectangular blur boundary.
                kernel = max(3, min(61, width, height))
                if kernel % 2 == 0:
                    kernel -= 1
                blurred = cv2.GaussianBlur(face, (kernel, kernel), 0)

                mask = np.zeros((height, width), dtype=np.uint8)
                cv2.ellipse(
                    mask,
                    (width // 2, height // 2),
                    (max(1, int(width * 0.48)), max(1, int(height * 0.48))),
                    0,
                    0,
                    360,
                    255,
                    -1,
                )
                feather = max(3, min(31, width, height))
                if feather % 2 == 0:
                    feather -= 1
                mask = cv2.GaussianBlur(mask, (feather, feather), 0)
                alpha = (mask.astype(np.float32) / 255.0)[..., None]
                blended = (
                    blurred.astype(np.float32) * alpha
                    + face.astype(np.float32) * (1.0 - alpha)
                )
                frame[y1:y2, x1:x2] = blended.astype(np.uint8)

            elif self.mode_id == 2:
                block_size = max(8, min(width, height) // 10)
                small = cv2.resize(
                    face,
                    (
                        max(1, width // block_size),
                        max(1, height // block_size),
                    ),
                    interpolation=cv2.INTER_AREA,
                )

                pixel = cv2.resize(
                    small,
                    (width, height),
                    interpolation=cv2.INTER_NEAREST,
                )

                frame[y1:y2, x1:x2] = pixel

            elif self.mode_id == 3:
                color = self.get_color()
                color_layer = face.copy()
                color_layer[:] = color

                frame[y1:y2, x1:x2] = cv2.addWeighted(
                    face,
                    0.15,
                    color_layer,
                    0.85,
                    0,
                )
