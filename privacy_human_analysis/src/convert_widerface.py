from pathlib import Path
import shutil

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "datasets" / "widerface"


def find_image_root(split):
    root = BASE / "raw_images" / f"WIDER_{split}"

    matches = list(root.rglob("images"))

    if not matches:
        raise FileNotFoundError(
            f"{split} görüntü klasörü bulunamadı: {root}"
        )

    return matches[0]


def read_annotations(path):
    lines = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).splitlines()

    annotations = {}
    i = 0

    while i < len(lines):
        image_name = lines[i].strip()

        if not image_name or not image_name.lower().endswith(".jpg"):
            i += 1
            continue

        if i + 1 >= len(lines):
            break

        count_text = lines[i + 1].strip()

        if not count_text.isdigit():
            i += 1
            continue

        count = int(count_text)
        boxes = []

        for j in range(count):
            index = i + 2 + j

            if index < len(lines):
                boxes.append(lines[index].strip())

        annotations[image_name] = boxes
        i += 2 + count

    return annotations


def convert(split):
    image_root = find_image_root(split)

    annotation_file = (
        BASE
        / "annotations"
        / "wider_face_split"
        / f"wider_face_{split}_bbx_gt.txt"
    )

    output_images = BASE / "images" / split
    output_labels = BASE / "labels" / split

    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    annotations = read_annotations(annotation_file)

    converted = 0
    skipped = 0

    for image_name, boxes in annotations.items():
        source = image_root / image_name

        if not source.exists():
            skipped += 1
            continue

        relative_path = Path(image_name)

        image_id = str(
            relative_path.with_suffix("")
        ).replace("\\", "_").replace("/", "_")

        target_image = output_images / f"{image_id}.jpg"
        target_label = output_labels / f"{image_id}.txt"

        shutil.copy2(source, target_image)

        with Image.open(source) as image:
            width, height = image.size

        labels = []

        for box in boxes:
            values = box.split()

            if len(values) < 4:
                continue

            try:
                x, y, box_width, box_height = map(
                    int,
                    values[:4],
                )
            except ValueError:
                continue

            if box_width <= 0 or box_height <= 0:
                continue

            x_center = (x + box_width / 2) / width
            y_center = (y + box_height / 2) / height
            normalized_width = box_width / width
            normalized_height = box_height / height

            x_center = max(0, min(1, x_center))
            y_center = max(0, min(1, y_center))
            normalized_width = max(
                0,
                min(1, normalized_width),
            )
            normalized_height = max(
                0,
                min(1, normalized_height),
            )

            labels.append(
                f"0 {x_center:.6f} "
                f"{y_center:.6f} "
                f"{normalized_width:.6f} "
                f"{normalized_height:.6f}"
            )

        target_label.write_text(
            "\n".join(labels),
            encoding="utf-8",
        )

        converted += 1

        if converted % 1000 == 0:
            print(f"{split}: {converted} görüntü işlendi...")

    print(
        f"{split}: {converted} görüntü dönüştürüldü, "
        f"{skipped} görüntü bulunamadı."
    )


convert("train")
convert("val")

print("WIDER FACE dönüştürme tamamlandı.")