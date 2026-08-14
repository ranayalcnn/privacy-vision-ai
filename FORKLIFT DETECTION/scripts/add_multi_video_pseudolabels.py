from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "data/hard_examples_multi/selected_frames"
LABELS = ROOT / "data/hard_examples_multi/prelabels"
TRAIN_IMAGES = ROOT / "data/processed/images/train"
TRAIN_LABELS = ROOT / "data/processed/labels/train"
MAX_NEGATIVES = 100


def main() -> None:
    positives = []
    negatives = []
    for image in sorted(IMAGES.rglob("*.jpg")):
        relative = image.relative_to(IMAGES)
        label = LABELS / relative.parent / f"{image.stem}.txt"
        (positives if label.read_text(encoding="utf-8").strip() else negatives).append(
            (image, label)
        )

    if len(negatives) > MAX_NEGATIVES:
        step = len(negatives) / MAX_NEGATIVES
        negatives = [negatives[int(index * step)] for index in range(MAX_NEGATIVES)]

    for image, label in positives + negatives:
        video_name = image.parent.name
        stem = f"multivideo_{video_name}_{image.stem}"
        shutil.copy2(image, TRAIN_IMAGES / f"{stem}.jpg")
        shutil.copy2(label, TRAIN_LABELS / f"{stem}.txt")
    print(
        f"Added positives={len(positives)} negatives={len(negatives)} "
        f"total={len(positives) + len(negatives)}"
    )


if __name__ == "__main__":
    main()
