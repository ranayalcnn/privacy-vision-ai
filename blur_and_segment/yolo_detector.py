from pathlib import Path

from ultralytics import YOLO
import torch


class YOLODetector:
    def __init__(self):
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        model_path = Path(__file__).resolve().parent / "yolov8n-face.pt"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Yüz modeli bulunamadı: {model_path}"
            )

        self.face_model = YOLO(str(model_path))
        self.face_model.to(self.device)

    def detect_faces(self, frame):
        results = self.face_model(
            frame,
            conf=0.08,
            iou=0.5,
            imgsz=960,
            device=self.device,
            verbose=False,
        )

        faces = []

        if not results or results[0].boxes is None:
            return faces

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist(),
            )

            confidence = float(box.conf[0])

            faces.append({
                "box": (x1, y1, x2, y2),
                "confidence": confidence,
            })

        return faces