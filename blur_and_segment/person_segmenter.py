from ultralytics import YOLO
import torch


class PersonSegmenter:
    def __init__(self):
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model = YOLO("yolo11s-seg.pt")
        self.model.to(self.device)

    def segment(self, frame):
        return self.model(
            frame,
            classes=[0],
            conf=0.25,
            iou=0.5,
            imgsz=640,
            device=self.device,
            retina_masks=True,
            verbose=False,
        )