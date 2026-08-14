from pathlib import Path

from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FACE_MODEL = PROJECT_ROOT / "blur_and_segment" / "yolov8n-face.pt"


class YOLODetector:
    """Original YOLO face detector, using the project's shared face model."""

    def __init__(self, model_path: str | Path = DEFAULT_FACE_MODEL):
        self.face_model = YOLO(str(model_path))

    def detect_faces(self, frame):
        results = self.face_model(
            frame,
            conf=0.10,
            iou=0.5,
            imgsz=1280,
            verbose=False,
        )

        faces = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                faces.append((x1, y1, x2, y2))
        return faces
