from pathlib import Path
import random
import cv2


ROOT = (
    Path(__file__).resolve().parents[1]
    / "datasets"
    / "widerface"
)

SPLITS = ("train", "val", "test")
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
SAMPLE_COUNT = 12


def read_boxes(label_path):
    errors = []

    for line_no, line in enumerate(
        label_path.read_text().splitlines(), 1
    ):
        parts = line.split()

        if len(parts) != 5:
            errors.append((line_no, "wrong column count"))
            continue

        try:
            cls, xc, yc, width, height = map(float, parts)
        except ValueError:
            errors.append((line_no, "non-numeric value"))
            continue

        values = [xc, yc, width, height]

        if cls != 0 or any(value < 0 or value > 1 for value in values):
            errors.append((line_no, "value outside YOLO range"))

        elif width <= 0 or height <= 0:
            errors.append((line_no, "zero-size box"))

    return errors


def get_images(split):
    image_dir = ROOT / "images" / split

    if not image_dir.exists():
        return []

    return [
        image for image in image_dir.iterdir()
        if image.suffix.lower() in IMAGE_EXTS
    ]


def main():
    total_images = 0
    split_counts = {}

    print("DATASET SUMMARY")
    print("-" * 50)

    for split in SPLITS:
        image_dir = ROOT / "images" / split
        label_dir = ROOT / "labels" / split
        images = get_images(split)

        missing = []
        empty = []
        invalid = []

        for image in images:
            label_path = label_dir / f"{image.stem}.txt"

            if not label_path.exists():
                missing.append(image.name)
                continue

            if not label_path.read_text().strip():
                empty.append(image.name)

            errors = read_boxes(label_path)

            for error in errors:
                invalid.append((image.name, *error))

        split_counts[split] = len(images)
        total_images += len(images)

        print(
            f"{split:5}: {len(images):6} images | "
            f"missing: {len(missing):4} | "
            f"empty: {len(empty):4} | "
            f"invalid: {len(invalid):4}"
        )

        if missing:
            print("Missing examples:", missing[:3])

        if invalid:
            print("Invalid examples:", invalid[:3])

    print("-" * 50)
    print(f"Total images: {total_images}")

    print("\nSPLIT RATIOS")

    for split, count in split_counts.items():
        ratio = (
            count / total_images * 100
            if total_images > 0
            else 0
        )

        print(
            f"{split:5}: {count:6} images "
            f"({ratio:.2f}%)"
        )

    output_dir = ROOT / "label_check_samples"
    output_dir.mkdir(exist_ok=True)

    random.seed(42)

    for split in SPLITS:
        image_dir = ROOT / "images" / split
        label_dir = ROOT / "labels" / split
        images = get_images(split)

        samples = random.sample(
            images,
            min(SAMPLE_COUNT, len(images))
        )

        for image_path in samples:
            frame = cv2.imread(str(image_path))
            label_path = label_dir / f"{image_path.stem}.txt"

            if frame is None or not label_path.exists():
                continue

            height, width = frame.shape[:2]

            for line in label_path.read_text().splitlines():
                parts = line.split()

                if len(parts) != 5:
                    continue

                _, xc, yc, box_width, box_height = map(
                    float,
                    parts
                )

                x1 = int((xc - box_width / 2) * width)
                y1 = int((yc - box_height / 2) * height)
                x2 = int((xc + box_width / 2) * width)
                y2 = int((yc + box_height / 2) * height)

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

            output_path = output_dir / f"{split}_{image_path.name}"
            cv2.imwrite(str(output_path), frame)

    print("\nVisual samples saved to:")
    print(output_dir)


if __name__ == "__main__":
    main()