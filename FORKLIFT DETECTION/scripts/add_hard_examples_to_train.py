from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/hard_examples/forklift_warehouse_8s_15s"
TRAIN_IMAGES = ROOT / "data/processed/images/train"
TRAIN_LABELS = ROOT / "data/processed/labels/train"
REPEATS = 5


def main() -> None:
    count = 0
    for image in sorted((BASE / "images").glob("*.jpg")):
        label = BASE / "labels_final" / f"{image.stem}.txt"
        if not label.exists():
            raise FileNotFoundError(label)
        for repeat in range(REPEATS):
            stem = f"hardclip_r{repeat}_{image.stem}"
            shutil.copy2(image, TRAIN_IMAGES / f"{stem}.jpg")
            shutil.copy2(label, TRAIN_LABELS / f"{stem}.txt")
            count += 1
    print(f"Added/updated {count} corrective training samples.")


if __name__ == "__main__":
    main()
