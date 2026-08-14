import cv2
from ultralytics import YOLO

model = YOLO(
    "runs/detect/models/widerface_gpu_10_fresh/weights/best.pt"
)

cap = cv2.VideoCapture("video.mp4")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

writer = cv2.VideoWriter(
    "face_result.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height),
)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model.predict(
        frame,
        conf=0.25,
        device=0,
        verbose=False,
    )

    output = results[0].plot()
    writer.write(output)

cap.release()
writer.release()

print("Tamamlandı: face_result.mp4")