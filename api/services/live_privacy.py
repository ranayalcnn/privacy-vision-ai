from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

import numpy as np

from api.config import settings
from api.services.hand_gesture import HandGestureController
from api.services.privacy import PrivacyMode
from api.services.tracked_face_pipeline import TrackedFacePipeline


@dataclass(frozen=True)
class LivePrivacyResult:
    image: np.ndarray
    face_count: int
    gesture_available: bool
    privacy_enabled: bool
    mode: PrivacyMode
    gesture: str | None = None


class LivePrivacyService:
    """Use the provided tracker pipeline for low-latency camera frames."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._processor: TrackedFacePipeline | None = None
        self._session_id: str | None = None
        self._gesture_controller = HandGestureController()
        self._gesture_control_active = False

    def process(
        self,
        image: np.ndarray,
        mode: PrivacyMode,
        confidence: float,
        session_id: str,
        gesture_control: bool = False,
    ) -> LivePrivacyResult:
        with self._lock:
            if self._processor is None:
                audit_path = settings.runtime_dir / "live_privacy_audit.jsonl"
                audit_path.parent.mkdir(parents=True, exist_ok=True)
                self._processor = TrackedFacePipeline(
                    model_path=settings.face_model_path,
                    audit_path=audit_path,
                    confidence=confidence,
                    image_size=416,
                    minimum_face_size=6,
                )

            if self._session_id != session_id:
                self._processor.reset()
                self._gesture_controller.reset(mode)
                self._session_id = session_id

            if self._gesture_control_active and not gesture_control:
                self._gesture_controller.reset(mode)
                self._processor.reset()
            self._gesture_control_active = gesture_control

            gesture_available = True
            privacy_enabled = True
            gesture = None
            effective_mode = mode
            if gesture_control:
                gesture_state = self._gesture_controller.process(image, mode)
                gesture_available = gesture_state.available
                privacy_enabled = gesture_state.privacy_enabled
                effective_mode = gesture_state.mode
                gesture = gesture_state.gesture

            self._processor.confidence = confidence
            self._processor.privacy_mode.set_mode(
                {
                    PrivacyMode.soft_blur: 1,
                    PrivacyMode.mosaic: 2,
                    PrivacyMode.color_shield: 3,
                }[effective_mode]
            )
            if not privacy_enabled:
                self._processor.reset()
                return LivePrivacyResult(
                    image.copy(),
                    0,
                    gesture_available,
                    False,
                    effective_mode,
                    gesture,
                )

            protected, face_count = self._processor.process(image)
            return LivePrivacyResult(
                protected,
                face_count,
                gesture_available,
                True,
                effective_mode,
                gesture,
            )


live_privacy_service = LivePrivacyService()
