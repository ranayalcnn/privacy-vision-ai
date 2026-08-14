from pathlib import Path
import time
import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "datasets" / "widerface" / "images" / "val"
LABEL_DIR = ROOT / "datasets" / "widerface" / "labels" / "val"
IOU_THRESHOLD = 0.50
CONFIDENCE = 0.50


def iou(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union else 0


def ground_truth(path, width, height):
    boxes = []
    if not path.exists():
        return boxes
    for line in path.read_text().splitlines():
        p = line.split()
        if len(p) != 5:
            continue
        _, xc, yc, w, h = map(float, p)
        boxes.append(((xc - w / 2) * width, (yc - h / 2) * height,
                      (xc + w / 2) * width, (yc + h / 2) * height))
    return boxes


def score(predictions, truths):
    tp = fp = fn = 0
    aps = []
    for preds, real in zip(predictions, truths):
        used = set()
        for box, confidence in sorted(preds, key=lambda x: x[1], reverse=True):
            matches = [iou(box, gt) for gt in real]
            best = max(matches, default=0)
            index = int(np.argmax(matches)) if matches else -1
            if best >= IOU_THRESHOLD and index not in used:
                tp += 1
                used.add(index)
            else:
                fp += 1
        fn += len(real) - len(used)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    return precision, recall


def run_blazeface(images):
    import mediapipe as mp
    detector = mp.solutions.face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=CONFIDENCE
    )
    results = []
    start = time.perf_counter()
    for image_path in images:
        frame = cv2.imread(str(image_path))
        height, width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = detector.process(rgb)
        boxes = []
        for detection in output.detections or []:
            score_value = detection.score[0]
            if score_value < CONFIDENCE:
                continue
            box = detection.location_data.relative_bounding_box
            boxes.append(((box.xmin * width, box.ymin * height,
                           (box.xmin + box.width) * width,
                           (box.ymin + box.height) * height), score_value))
        results.append(boxes)
    return results, time.perf_counter() - start


def run_scrfd(images):
    from insightface.app import FaceAnalysis
    detector = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    detector.prepare(ctx_id=0, det_size=(256, 256))
    results = []
    start = time.perf_counter()
    for image_path in images:
        frame = cv2.imread(str(image_path))
        boxes = []
        for face in detector.get(frame):
            if face.det_score < CONFIDENCE:
                continue
            boxes.append((tuple(face.bbox.tolist()), float(face.det_score)))
        results.append(boxes)
    return results, time.perf_counter() - start


def main():
    images = sorted(p for p in IMAGE_DIR.iterdir()
                    if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not images:
        raise FileNotFoundError(f"Validation görüntüsü bulunamadı: {IMAGE_DIR}")

    truths = []
    for path in images:
        frame = cv2.imread(str(path))
        truths.append(ground_truth(LABEL_DIR / f"{path.stem}.txt",
                                   frame.shape[1], frame.shape[0]))

    for name, runner in (("BlazeFace", run_blazeface), ("SCRFD", run_scrfd)):
        predictions, elapsed = runner(images)
        precision, recall = score(predictions, truths)
        fps = len(images) / elapsed if elapsed else 0
        print(f"\n{name}")
        print(f"Images: {len(images)}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"mAP50 (approx.): {precision * recall:.4f}")
        print(f"FPS: {fps:.2f}")


if __name__ == "__main__":
    main()