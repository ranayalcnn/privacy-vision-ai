from __future__ import annotations

from threading import Lock

import cv2
import numpy as np

from api.config import settings
from api.services.model_loader import LazyYoloModel
from api.services.vision_preprocess import enhance_for_detection


BODY_SKELETON = (
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
    (5, 11), (6, 12), (11, 12),
    (11, 13), (13, 15), (12, 14), (14, 16),
)
FACE_KEYPOINTS = (0, 1, 2, 3, 4)
SHOULDER_KEYPOINTS = (5, 6)
POSE_COLORS = (
    (67, 217, 173),
    (255, 173, 74),
    (114, 159, 255),
    (225, 112, 182),
    (104, 207, 255),
)


def _lighter_color(color: tuple[int, int, int], amount: float = 0.28) -> tuple[int, int, int]:
    return tuple(int(channel + (255 - channel) * amount) for channel in color)


def _to_numpy(value):
    if value is None:
        return None
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def _pose_result_count(result) -> int:
    keypoints = getattr(result, "keypoints", None)
    coordinates = _to_numpy(getattr(keypoints, "xy", None))
    if coordinates is not None:
        return len(coordinates)
    return 0 if keypoints is None else len(keypoints)


def _motion_label(
    points: np.ndarray,
    scores: np.ndarray,
    previous: np.ndarray | None,
) -> str:
    if previous is None or previous.shape != points.shape:
        return "TRACKING"

    reliable = (
        (scores >= 0.30)
        & np.all(points > 0, axis=1)
        & np.all(previous > 0, axis=1)
    )
    if np.count_nonzero(reliable) < 4:
        return "TRACKING"

    body_height = max(1.0, float(np.ptp(points[reliable, 1])))
    torso_indices = np.array([5, 6, 11, 12])
    torso_valid = reliable[torso_indices]
    center_motion = 0.0
    if np.count_nonzero(torso_valid) >= 2:
        indices = torso_indices[torso_valid]
        current_center = np.mean(points[indices], axis=0)
        previous_center = np.mean(previous[indices], axis=0)
        center_motion = float(np.linalg.norm(current_center - previous_center)) / body_height

    leg_indices = np.array([13, 14, 15, 16])
    leg_valid = reliable[leg_indices]
    leg_motion = 0.0
    if np.count_nonzero(leg_valid) >= 2:
        indices = leg_indices[leg_valid]
        leg_motion = float(
            np.mean(np.linalg.norm(points[indices] - previous[indices], axis=1))
        ) / body_height

    if leg_motion >= 0.020 and (center_motion >= 0.006 or leg_motion >= 0.035):
        return "WALKING"
    if center_motion >= 0.012 or leg_motion >= 0.012:
        return "MOVING"
    return "STILL"


def _render_pose_result(
    image: np.ndarray,
    result,
    history: dict[int, np.ndarray] | None = None,
    motion_history: dict[int, np.ndarray] | None = None,
) -> tuple[np.ndarray, int, set[int]]:
    keypoints = getattr(result, "keypoints", None)
    coordinates = _to_numpy(getattr(keypoints, "xy", None))
    if coordinates is None:
        # Keep compatibility with older/fake Ultralytics results.
        pose_count = 0 if keypoints is None else len(keypoints)
        return result.plot(), pose_count, set()

    confidence = _to_numpy(getattr(keypoints, "conf", None))
    if confidence is None:
        confidence = np.ones(coordinates.shape[:2], dtype=np.float32)

    track_ids = None
    boxes = getattr(result, "boxes", None)
    if boxes is not None:
        track_ids = _to_numpy(getattr(boxes, "id", None))
    if track_ids is None or len(track_ids) != len(coordinates):
        track_ids = np.arange(len(coordinates), dtype=np.int32)

    output = image.copy()
    glow_layer = np.zeros_like(image)
    shortest_side = min(image.shape[:2])
    render_scale = float(np.clip(shortest_side / 360.0, 0.85, 1.55))
    line_width = max(2, int(round(2.4 * render_scale)))
    line_outline = line_width + max(2, int(round(2.0 * render_scale)))
    joint_radius = max(4, int(round(4.0 * render_scale)))
    joint_outline = joint_radius + max(2, int(round(1.8 * render_scale)))
    glow_radius = joint_outline + max(2, int(round(2.5 * render_scale)))
    visible_ids: set[int] = set()
    for person_index, raw_points in enumerate(coordinates):
        track_id = int(track_ids[person_index])
        visible_ids.add(track_id)
        points = raw_points.astype(np.float32).copy()
        scores = confidence[person_index]
        motion_label = _motion_label(
            points,
            scores,
            None if motion_history is None else motion_history.get(track_id),
        )
        if motion_history is not None:
            motion_history[track_id] = points.copy()

        if history is not None and track_id in history:
            previous = history[track_id]
            if previous.shape == points.shape:
                valid = (scores >= 0.30) & np.all(points > 0, axis=1)
                points[valid] = points[valid] * 0.68 + previous[valid] * 0.32
        if history is not None:
            history[track_id] = points.copy()

        color = POSE_COLORS[track_id % len(POSE_COLORS)]
        highlight = _lighter_color(color)
        for first, second in BODY_SKELETON:
            if scores[first] < 0.30 or scores[second] < 0.30:
                continue
            p1 = tuple(np.rint(points[first]).astype(int))
            p2 = tuple(np.rint(points[second]).astype(int))
            if min(*p1, *p2) <= 0:
                continue
            cv2.line(glow_layer, p1, p2, color, line_outline + 4, cv2.LINE_AA)
            cv2.line(output, p1, p2, (11, 18, 28), line_outline, cv2.LINE_AA)
            cv2.line(output, p1, p2, color, line_width, cv2.LINE_AA)

        face_valid = np.array(
            [scores[index] >= 0.30 and np.all(points[index] > 0) for index in FACE_KEYPOINTS]
        )
        head_center: tuple[int, int] | None = None
        if np.count_nonzero(face_valid):
            face_points = points[np.array(FACE_KEYPOINTS)[face_valid]]
            head_center = tuple(np.rint(np.mean(face_points, axis=0)).astype(int))
            face_span = float(np.ptp(face_points[:, 0])) if len(face_points) > 1 else 0.0
            shoulder_width = 0.0
            if all(scores[index] >= 0.30 and np.all(points[index] > 0) for index in SHOULDER_KEYPOINTS):
                shoulder_width = float(np.linalg.norm(points[5] - points[6]))
            head_radius = int(
                round(
                    np.clip(
                        max(face_span * 0.62, shoulder_width * 0.18),
                        7 * render_scale,
                        13 * render_scale,
                    )
                )
            )

            for shoulder_index in SHOULDER_KEYPOINTS:
                if scores[shoulder_index] < 0.30 or np.any(points[shoulder_index] <= 0):
                    continue
                shoulder = tuple(np.rint(points[shoulder_index]).astype(int))
                cv2.line(glow_layer, head_center, shoulder, color, line_outline + 4, cv2.LINE_AA)
                cv2.line(output, head_center, shoulder, (11, 18, 28), line_outline, cv2.LINE_AA)
                cv2.line(output, head_center, shoulder, color, line_width, cv2.LINE_AA)

            cv2.circle(glow_layer, head_center, head_radius + 4, color, -1, cv2.LINE_AA)
            cv2.circle(output, head_center, head_radius + 2, (11, 18, 28), -1, cv2.LINE_AA)
            cv2.circle(output, head_center, head_radius, color, -1, cv2.LINE_AA)
            cv2.circle(output, head_center, max(2, head_radius - 3), highlight, 2, cv2.LINE_AA)

        for point_index, (point, score) in enumerate(zip(points, scores, strict=True)):
            if point_index in FACE_KEYPOINTS:
                continue
            if score < 0.30 or np.any(point <= 0):
                continue
            center = tuple(np.rint(point).astype(int))
            cv2.circle(glow_layer, center, glow_radius, color, -1, cv2.LINE_AA)
            cv2.circle(output, center, joint_outline, (11, 18, 28), -1, cv2.LINE_AA)
            cv2.circle(output, center, joint_radius, color, -1, cv2.LINE_AA)
            cv2.circle(output, center, max(1, joint_radius // 2), highlight, -1, cv2.LINE_AA)

    cv2.addWeighted(output, 1.0, glow_layer, 0.14, 0, output)

    return output, len(coordinates), visible_ids


class PoseService:
    def __init__(self) -> None:
        self._model = LazyYoloModel(settings.pose_model_path)
        self._live_tracker = PoseTracker()

    def estimate(
        self,
        image: np.ndarray,
        confidence: float,
        image_size: int = 640,
    ) -> tuple[np.ndarray, int]:
        inference_image = enhance_for_detection(image)
        result = self._model.predict(
            inference_image,
            conf=confidence,
            iou=0.75,
            imgsz=image_size,
            max_det=100,
            verbose=False,
        )[0]
        first_count = _pose_result_count(result)
        if first_count <= 1 and image_size >= 640:
            recovery = self._model.predict(
                inference_image,
                conf=min(confidence, 0.15),
                iou=0.80,
                imgsz=max(768, image_size),
                max_det=100,
                verbose=False,
            )[0]
            if _pose_result_count(recovery) > first_count:
                result = recovery
        output, pose_count, _ = _render_pose_result(image, result)
        return output, pose_count

    @staticmethod
    def create_tracker() -> "PoseTracker":
        return PoseTracker()

    def track(
        self,
        image: np.ndarray,
        confidence: float,
        session_id: str,
        image_size: int = 320,
    ) -> tuple[np.ndarray, int]:
        return self._live_tracker.process(
            image,
            confidence,
            session_id,
            image_size,
        )


class PoseTracker:
    """ByteTrack IDs plus light keypoint smoothing for crowded pose videos."""

    def __init__(self) -> None:
        self._model = LazyYoloModel(settings.pose_model_path)
        self._session_id: str | None = None
        self._lock = Lock()
        self._history: dict[int, np.ndarray] = {}
        self._motion_history: dict[int, np.ndarray] = {}
        self._missing_frames: dict[int, int] = {}

    def process(
        self,
        image: np.ndarray,
        confidence: float,
        session_id: str,
        image_size: int = 640,
    ) -> tuple[np.ndarray, int]:
        with self._lock:
            if session_id != self._session_id:
                self._model.reset_tracking()
                self._session_id = session_id
                self._history.clear()
                self._motion_history.clear()
                self._missing_frames.clear()

            result = self._model.track(
                enhance_for_detection(image),
                persist=True,
                tracker=str(settings.forklift_tracker_config_path),
                conf=min(confidence, 0.20),
                iou=0.75,
                imgsz=image_size,
                max_det=100,
                verbose=False,
            )[0]
            output, pose_count, visible_ids = _render_pose_result(
                image,
                result,
                self._history,
                self._motion_history,
            )

            for track_id in list(self._history):
                self._missing_frames[track_id] = (
                    0 if track_id in visible_ids
                    else self._missing_frames.get(track_id, 0) + 1
                )
                if self._missing_frames[track_id] > 30:
                    self._history.pop(track_id, None)
                    self._motion_history.pop(track_id, None)
                    self._missing_frames.pop(track_id, None)

            return output, pose_count


pose_service = PoseService()
