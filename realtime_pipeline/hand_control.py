import time

import cv2
import mediapipe as mp
from ultralytics import YOLO

from hand_config import (
    SOURCE,
    WINDOW_NAME,
    FACE_MODEL,
    FACE_CONFIDENCE,
    FACE_INTERVAL,
    BLUR_ENABLED,
)

from mode import PrivacyMode
from dashboard import draw_dashboard


class HandPrivacyApp:
    def __init__(self):
        self.face_model = YOLO(FACE_MODEL)
        self.mode_manager = PrivacyMode()

        self.privacy_enabled = BLUR_ENABLED
        self.face_boxes = []
        self.frame_count = 0

        self.last_gesture = ""
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.2

        self.notification_text = ""
        self.notification_until = 0

        self.hand_points = []
        self.swipe_start_x = None
        self.swipe_start_time = 0
        self.swipe_cooldown_until = 0

        self.hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.65,
        )

        self.drawer = mp.solutions.drawing_utils
        self.hand_style = mp.solutions.drawing_styles

    def select_mode(self, mode_id):
        self.mode_manager.set_mode(mode_id)
        self.privacy_enabled = True
        self.notification_text = self.mode_manager.mode
        self.notification_until = time.perf_counter() + 1.5

    def detect_faces(self, frame):
        results = self.face_model.predict(
            frame,
            conf=FACE_CONFIDENCE,
            imgsz=320,
            max_det=10,
            verbose=False,
        )

        boxes = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = map(int, box)

                width = x2 - x1
                height = y2 - y1

                if width < 25 or height < 25:
                    continue

                pad_x = int(width * 0.15)
                pad_y = int(height * 0.20)

                boxes.append(
                    (
                        max(0, x1 - pad_x),
                        max(0, y1 - pad_y),
                        min(frame.shape[1], x2 + pad_x),
                        min(frame.shape[0], y2 + pad_y),
                    )
                )

        return boxes

    def is_pinch(self, hand):
        thumb = hand.landmark[4]
        index = hand.landmark[8]

        distance = (
            (thumb.x - index.x) ** 2
            + (thumb.y - index.y) ** 2
        ) ** 0.5

        return distance < 0.055

    def count_fingers(self, hand):
        count = 0

        for tip, pip in [
            (8, 6),
            (12, 10),
            (16, 14),
        ]:
            if hand.landmark[tip].y < hand.landmark[pip].y:
                count += 1

        return count

    def detect_swipe(self, hand, now):
        wrist_x = hand.landmark[0].x

        if self.swipe_start_x is None:
            self.swipe_start_x = wrist_x
            self.swipe_start_time = now
            return None

        elapsed = now - self.swipe_start_time
        movement = wrist_x - self.swipe_start_x

        if elapsed > 0.45:
            self.swipe_start_x = wrist_x
            self.swipe_start_time = now
            return None

        if (
            abs(movement) > 0.20
            and now >= self.swipe_cooldown_until
        ):
            self.swipe_start_x = None
            self.swipe_cooldown_until = now + 0.8
            return "SWIPE RIGHT" if movement > 0 else "SWIPE LEFT"

        return None

    def cycle_mode(self, direction):
        mode_id = self.mode_manager.mode_id + direction
        if mode_id < 1:
            mode_id = len(self.mode_manager.MODES)
        elif mode_id > len(self.mode_manager.MODES):
            mode_id = 1
        self.select_mode(mode_id)

    def handle_hands(self, frame):
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        result = self.hands.process(rgb)
        gesture = None
        self.hand_points = []

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            h, w = frame.shape[:2]
            now = time.perf_counter()

            self.hand_points = [
                (
                    int(point.x * w),
                    int(point.y * h),
                )
                for point in hand.landmark
            ]

            self.drawer.draw_landmarks(
                frame,
                hand,
                mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(
                    color=(196, 164, 54),
                    thickness=2,
                    circle_radius=3,
                ),
                mp.solutions.drawing_utils.DrawingSpec(
                    color=(225, 204, 112),
                    thickness=3,
                    circle_radius=2,
                ),
            )

            swipe = self.detect_swipe(hand, now)

            if swipe:
                gesture = swipe
            elif self.is_pinch(hand):
                gesture = "PINCH"
            else:
                fingers = self.count_fingers(hand)

                if fingers == 1:
                    gesture = "BLUR"
                elif fingers == 2:
                    gesture = "PIXEL"
                elif fingers == 3:
                    gesture = "COLOR"
                elif fingers == 0:
                    gesture = "FIST"
        else:
            self.swipe_start_x = None

        now = time.perf_counter()

        if (
            gesture
            and gesture != self.last_gesture
            and now - self.last_gesture_time
            > self.gesture_cooldown
        ):
            if gesture == "PINCH":
                self.privacy_enabled = not self.privacy_enabled

                self.notification_text = (
                    "PRIVACY ON"
                    if self.privacy_enabled
                    else "PRIVACY OFF"
                )

            elif gesture == "SWIPE LEFT":
                self.cycle_mode(-1)
                self.notification_text = "<  " + self.mode_manager.mode

            elif gesture == "SWIPE RIGHT":
                self.cycle_mode(1)
                self.notification_text = self.mode_manager.mode + "  >"

            elif gesture == "FIST":
                self.privacy_enabled = False
                self.notification_text = "PRIVACY OFF"

            elif gesture == "BLUR":
                self.select_mode(1)

            elif gesture == "PIXEL":
                self.select_mode(2)

            elif gesture == "COLOR":
                self.select_mode(3)

            self.notification_until = now + 1.5
            self.last_gesture = gesture
            self.last_gesture_time = now

        if gesture is None:
            self.last_gesture = ""

    def process(self, frame):
        self.frame_count += 1

        self.handle_hands(frame)

        if self.frame_count % FACE_INTERVAL == 0:
            self.face_boxes = self.detect_faces(frame)

        if self.privacy_enabled:
            self.mode_manager.apply(
                frame,
                self.face_boxes,
            )

        return frame


def open_camera(source):
    for backend in (
        cv2.CAP_DSHOW,
        cv2.CAP_MSMF,
        cv2.CAP_ANY,
    ):
        camera = cv2.VideoCapture(
            source,
            backend,
        )

        if camera.isOpened():
            camera.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                640,
            )

            camera.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                480,
            )

            return camera

        camera.release()

    return None


def main():
    camera = open_camera(SOURCE)

    if camera is None:
        raise RuntimeError(
            "Kamera açılamadı. hand_config.py içinde SOURCE = 1 dene."
        )

    app = HandPrivacyApp()

    previous_time = time.perf_counter()
    fps = 0

    try:
        while True:
            success, frame = camera.read()

            if not success:
                continue

            frame = cv2.flip(frame, 1)
            frame = app.process(frame)

            now = time.perf_counter()

            instant_fps = 1 / max(
                now - previous_time,
                0.001,
            )

            fps = (
                instant_fps
                if fps == 0
                else fps * 0.9 + instant_fps * 0.1
            )

            previous_time = now

            frame = draw_dashboard(
                frame,
                app,
                fps,
            )

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("b"):
                app.privacy_enabled = not app.privacy_enabled

                app.notification_text = (
                    "PRIVACY ON"
                    if app.privacy_enabled
                    else "PRIVACY OFF"
                )

                app.notification_until = (
                    time.perf_counter() + 1.5
                )

            elif key in (ord("1"), ord("2"), ord("3")):
                app.select_mode(int(chr(key)))

            elif key == ord("q"):
                break

    finally:
        camera.release()
        app.hands.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
