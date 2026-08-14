from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import cv2
import numpy as np

from api.services.privacy import PrivacyMode


@dataclass(frozen=True)
class GestureState:
    available: bool
    privacy_enabled: bool
    mode: PrivacyMode
    gesture: str | None = None


class HandGestureController:
    """Web adapter for the gestures in realtime_pipeline/hand_control.py."""

    def __init__(self) -> None:
        self._hands = None
        self._available: bool | None = None
        self.privacy_enabled = True
        self.mode = PrivacyMode.soft_blur
        self.last_gesture = ""
        self.last_gesture_time = 0.0
        self.gesture_cooldown = 1.2

    def reset(self, mode: PrivacyMode) -> None:
        self.privacy_enabled = True
        self.mode = mode
        self.last_gesture = ""
        self.last_gesture_time = 0.0

    def _ensure_hands(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import mediapipe as mp

            self._hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                model_complexity=0,
                min_detection_confidence=0.65,
                min_tracking_confidence=0.65,
            )
            self._available = True
        except (ImportError, AttributeError, RuntimeError):
            self._hands = None
            self._available = False
        return self._available

    @staticmethod
    def _is_pinch(hand) -> bool:
        thumb = hand.landmark[4]
        index = hand.landmark[8]
        distance = ((thumb.x - index.x) ** 2 + (thumb.y - index.y) ** 2) ** 0.5
        return distance < 0.055

    @staticmethod
    def _count_fingers(hand) -> int:
        return sum(
            hand.landmark[tip].y < hand.landmark[pip].y
            for tip, pip in ((8, 6), (12, 10), (16, 14))
        )

    def process(self, frame: np.ndarray, requested_mode: PrivacyMode) -> GestureState:
        if not self._ensure_hands() or self._hands is None:
            return GestureState(False, True, requested_mode)

        self.mode = requested_mode
        result = self._hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        gesture = None
        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            if self._is_pinch(hand):
                gesture = "PINCH"
            else:
                fingers = self._count_fingers(hand)
                gesture = {
                    0: "FIST",
                    1: "BLUR",
                    2: "PIXEL",
                    3: "COLOR",
                }.get(fingers)

        now = perf_counter()
        accepted = None
        if (
            gesture
            and gesture != self.last_gesture
            and now - self.last_gesture_time > self.gesture_cooldown
        ):
            accepted = gesture
            if gesture == "PINCH":
                self.privacy_enabled = not self.privacy_enabled
            elif gesture == "FIST":
                self.privacy_enabled = False
            else:
                self.privacy_enabled = True
                self.mode = {
                    "BLUR": PrivacyMode.soft_blur,
                    "PIXEL": PrivacyMode.mosaic,
                    "COLOR": PrivacyMode.color_shield,
                }[gesture]
            self.last_gesture = gesture
            self.last_gesture_time = now
        elif gesture is None:
            self.last_gesture = ""

        return GestureState(True, self.privacy_enabled, self.mode, accepted)
