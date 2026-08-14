from ultralytics import YOLO
import torch


class ObjectTracker:
    def __init__(self):
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model = YOLO("yolo11s.pt")
        self.model.to(self.device)

    def track_people(self, frame):
        results = self.model.track(
            frame,
            persist=True,
            classes=[0],
            conf=0.25,
            iou=0.5,
            tracker="bytetrack.yaml",
            device=self.device,
            verbose=False,
        )

        people = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist(),
                )

                track_id = None

                if box.id is not None:
                    track_id = int(box.id[0])

                confidence = float(box.conf[0])

                people.append({
                    "id": track_id,
                    "box": (x1, y1, x2, y2),
                    "confidence": confidence,
                })

        return people