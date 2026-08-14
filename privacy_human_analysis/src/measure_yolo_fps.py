import time
from pathlib import Path
import cv2
from ultralytics import YOLO

ROOT = Path(__file__).parent.parent

model = YOLO(
    ROOT / "runs/detect/models/widerface_gpu_10_fresh/weights/best.pt"
)

cap = cv2.VideoCapture(str(ROOT / "video.mp4"))

if not cap.isOpened():
    raise FileNotFoundError("video.mp4 açılamadı.")

count = 0
start = time.perf_counter()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    model.predict(
        frame,
        conf=0.25,
        device=0,
        verbose=False
    )

    count += 1

elapsed = time.perf_counter() - start
fps = count / elapsed

cap.release()

print(f"Processed frames: {count}")
print(f"Elapsed time: {elapsed:.2f} seconds")
print(f"YOLO FPS: {fps:.2f}")
