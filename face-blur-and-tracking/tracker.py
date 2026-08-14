from pathlib import Path

from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PERSON_MODEL = PROJECT_ROOT / "realtime_pipeline" / "yolo11n.pt"


class ObjectTracker:
    """Original persistent ByteTrack person tracker."""

    def __init__(self, model_path: str | Path = DEFAULT_PERSON_MODEL):
        self.model = YOLO(str(model_path))

    def track_people(self, frame):
        results = self.model.track(
            frame,
            persist=True,
            classes=[0],
            conf=0.35,
            iou=0.5,
            tracker="bytetrack.yaml",
            verbose=False,
        )

        people = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                if box.id is None:
                    continue
                people.append(
                    {
                        "id": int(box.id[0]),
                        "box": tuple(map(int, box.xyxy[0])),
                    }
                )
        return people
