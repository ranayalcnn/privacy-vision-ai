"""Merge the downloaded forklift datasets into one deduplicated YOLO dataset."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed"

TARGET_NAMES = ["forklift", "person", "pallet", "pallet_truck"]
TARGET_ID = {name: index for index, name in enumerate(TARGET_NAMES)}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
NEAR_DUPLICATE_DISTANCE = 2
MAX_NEGATIVE_IMAGES = 500


@dataclass
class Record:
    source: str
    image_path: Path
    width: int
    height: int
    sha256: str
    dhash: int
    labels: list[tuple[int, float, float, float, float]] = field(default_factory=list)


SOURCE_CONFIGS = [
    {
        "name": "roboflow_forklift_v1",
        "type": "yolo",
        "class_map": {0: "forklift", 1: "person"},
    },
    {
        "name": "roboflow_warehouse",
        "type": "yolo",
        "class_map": {0: "forklift", 1: "pallet_truck"},
    },
    {
        "name": "roboflow_1000ware",
        "type": "yolo",
        "class_map": {0: None, 1: "forklift", 2: "person", 3: "pallet"},
    },
    {
        "name": "roboflow_loco",
        "type": "yolo",
        "class_map": {
            0: "forklift",
            1: "pallet",
            2: "pallet_truck",
            3: None,
            4: None,
        },
    },
    {
        "name": "hf_forklift_object_detection",
        "type": "coco",
        "class_map": {0: "forklift", 1: "person"},
    },
]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def difference_hash(image: Image.Image) -> int:
    gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = list(gray.get_flattened_data())
    result = 0
    for row in range(8):
        for col in range(8):
            left = pixels[row * 9 + col]
            right = pixels[row * 9 + col + 1]
            result = (result << 1) | int(left > right)
    return result


def read_image_info(path: Path) -> tuple[int, int, int]:
    with Image.open(path) as image:
        width, height = image.size
        dhash = difference_hash(image)
    return width, height, dhash


def normalize_yolo_box(
    values: list[float],
) -> tuple[float, float, float, float] | None:
    if len(values) < 4:
        return None
    x, y, width, height = values[:4]
    x = min(1.0, max(0.0, x))
    y = min(1.0, max(0.0, y))
    width = min(1.0, max(0.0, width))
    height = min(1.0, max(0.0, height))
    if width <= 0 or height <= 0:
        return None
    return x, y, width, height


def load_yolo_source(config: dict) -> list[Record]:
    source_root = RAW / config["name"]
    records: list[Record] = []
    for split in ("train", "valid", "test"):
        image_dir = source_root / split / "images"
        label_dir = source_root / split / "labels"
        if not image_dir.exists():
            continue
        for image_path in sorted(image_dir.iterdir()):
            if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            width, height, dhash = read_image_info(image_path)
            labels: list[tuple[int, float, float, float, float]] = []
            label_path = label_dir / f"{image_path.stem}.txt"
            if label_path.exists():
                for line in label_path.read_text(encoding="utf-8").splitlines():
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    source_class = int(float(parts[0]))
                    target_name = config["class_map"].get(source_class)
                    if target_name is None:
                        continue
                    box = normalize_yolo_box([float(value) for value in parts[1:5]])
                    if box is not None:
                        labels.append((TARGET_ID[target_name], *box))
            records.append(
                Record(
                    source=config["name"],
                    image_path=image_path,
                    width=width,
                    height=height,
                    sha256=file_sha256(image_path),
                    dhash=dhash,
                    labels=labels,
                )
            )
    return records


def load_coco_source(config: dict) -> list[Record]:
    source_root = RAW / config["name"]
    records: list[Record] = []
    for split in ("train", "valid", "test"):
        split_root = source_root / split
        annotation_path = split_root / "_annotations.coco.json"
        if not annotation_path.exists():
            continue
        coco = json.loads(annotation_path.read_text(encoding="utf-8"))
        annotations_by_image: dict[int, list[dict]] = defaultdict(list)
        for annotation in coco["annotations"]:
            annotations_by_image[annotation["image_id"]].append(annotation)
        for image_info in coco["images"]:
            image_path = split_root / image_info["file_name"]
            if not image_path.exists():
                continue
            width = int(image_info["width"])
            height = int(image_info["height"])
            actual_width, actual_height, dhash = read_image_info(image_path)
            if (width, height) != (actual_width, actual_height):
                width, height = actual_width, actual_height
            labels: list[tuple[int, float, float, float, float]] = []
            for annotation in annotations_by_image.get(image_info["id"], []):
                target_name = config["class_map"].get(annotation["category_id"])
                if target_name is None:
                    continue
                x, y, box_width, box_height = annotation["bbox"]
                box = normalize_yolo_box(
                    [
                        (x + box_width / 2) / width,
                        (y + box_height / 2) / height,
                        box_width / width,
                        box_height / height,
                    ]
                )
                if box is not None:
                    labels.append((TARGET_ID[target_name], *box))
            records.append(
                Record(
                    source=config["name"],
                    image_path=image_path,
                    width=width,
                    height=height,
                    sha256=file_sha256(image_path),
                    dhash=dhash,
                    labels=labels,
                )
            )
    return records


def box_iou(
    first: tuple[int, float, float, float, float],
    second: tuple[int, float, float, float, float],
) -> float:
    if first[0] != second[0]:
        return 0.0
    _, ax, ay, aw, ah = first
    _, bx, by, bw, bh = second
    a_left, a_top, a_right, a_bottom = ax - aw / 2, ay - ah / 2, ax + aw / 2, ay + ah / 2
    b_left, b_top, b_right, b_bottom = bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2
    intersection_width = max(0.0, min(a_right, b_right) - max(a_left, b_left))
    intersection_height = max(0.0, min(a_bottom, b_bottom) - max(a_top, b_top))
    intersection = intersection_width * intersection_height
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0 else 0.0


def merge_labels(
    target: list[tuple[int, float, float, float, float]],
    incoming: list[tuple[int, float, float, float, float]],
) -> None:
    for label in incoming:
        if not any(box_iou(label, existing) >= 0.90 for existing in target):
            target.append(label)


def deduplicate(records: list[Record]) -> tuple[list[Record], dict]:
    exact_by_sha: dict[str, Record] = {}
    exact_duplicates = 0
    for record in records:
        existing = exact_by_sha.get(record.sha256)
        if existing is None:
            exact_by_sha[record.sha256] = record
        else:
            merge_labels(existing.labels, record.labels)
            exact_duplicates += 1

    unique_exact = list(exact_by_sha.values())
    positive_records = [record for record in unique_exact if record.labels]
    negative_records = sorted(
        (record for record in unique_exact if not record.labels),
        key=lambda record: record.sha256,
    )
    retained_negatives = negative_records[:MAX_NEGATIVE_IMAGES]
    filtered_records = positive_records + retained_negatives

    buckets: dict[tuple[int, int], list[int]] = defaultdict(list)
    kept: list[Record] = []
    near_duplicate_candidates = 0
    for record in filtered_records:
        candidates: set[int] = set()
        for segment in range(4):
            value = (record.dhash >> (segment * 16)) & 0xFFFF
            candidates.update(buckets[(segment, value)])
        similar_found = False
        aspect = record.width / record.height
        for index in candidates:
            candidate = kept[index]
            candidate_aspect = candidate.width / candidate.height
            if abs(aspect - candidate_aspect) > 0.01:
                continue
            if (record.dhash ^ candidate.dhash).bit_count() <= NEAR_DUPLICATE_DISTANCE:
                similar_found = True
                break
        if similar_found:
            near_duplicate_candidates += 1
        index = len(kept)
        kept.append(record)
        for segment in range(4):
            value = (record.dhash >> (segment * 16)) & 0xFFFF
            buckets[(segment, value)].append(index)

    return kept, {
        "input_images": len(records),
        "exact_duplicates_removed": exact_duplicates,
        "empty_target_images_removed": max(
            0, len(negative_records) - len(retained_negatives)
        ),
        "negative_images_retained": len(retained_negatives),
        "near_duplicate_candidates_retained_for_manual_review": near_duplicate_candidates,
        "near_duplicates_removed_automatically": 0,
        "unique_images": len(kept),
    }


def choose_split(sha256: str) -> str:
    value = int(sha256[:8], 16) % 100
    if value < 80:
        return "train"
    if value < 90:
        return "val"
    return "test"


def write_dataset(records: list[Record]) -> dict:
    for split in ("train", "val", "test"):
        (OUTPUT / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUTPUT / "labels" / split).mkdir(parents=True, exist_ok=True)

    split_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    empty_images = 0

    for record in records:
        split = choose_split(record.sha256)
        extension = ".jpg" if record.image_path.suffix.lower() in {".jpg", ".jpeg"} else ".png"
        stem = f"{record.source}_{record.sha256[:16]}"
        destination_image = OUTPUT / "images" / split / f"{stem}{extension}"
        destination_label = OUTPUT / "labels" / split / f"{stem}.txt"
        shutil.copy2(record.image_path, destination_image)
        lines = []
        for class_id, x, y, width, height in sorted(record.labels):
            lines.append(
                f"{class_id} {x:.6f} {y:.6f} {width:.6f} {height:.6f}"
            )
            class_counts[TARGET_NAMES[class_id]] += 1
        destination_label.write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )
        if not lines:
            empty_images += 1
        split_counts[split] += 1
        source_counts[record.source] += 1

    dataset_yaml = "\n".join(
        [
            f"path: {OUTPUT.as_posix()}",
            "train: images/train",
            "val: images/val",
            "test: images/test",
            "",
            f"nc: {len(TARGET_NAMES)}",
            f"names: {TARGET_NAMES}",
            "",
        ]
    )
    (OUTPUT / "data.yaml").write_text(dataset_yaml, encoding="utf-8")
    return {
        "split_images": dict(split_counts),
        "class_instances": dict(class_counts),
        "source_images_after_deduplication": dict(source_counts),
        "images_without_target_labels": empty_images,
    }


def main() -> None:
    existing_outputs = [
        path
        for path in OUTPUT.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    ]
    if existing_outputs:
        raise SystemExit(
            "data/processed already contains generated files. "
            "Move or remove them before rerunning."
        )

    all_records: list[Record] = []
    source_input_counts: dict[str, int] = {}
    for config in SOURCE_CONFIGS:
        if config["type"] == "yolo":
            records = load_yolo_source(config)
        else:
            records = load_coco_source(config)
        source_input_counts[config["name"]] = len(records)
        all_records.extend(records)
        print(f"Loaded {len(records):5d} images from {config['name']}")

    unique_records, deduplication = deduplicate(all_records)
    output_stats = write_dataset(unique_records)
    report = {
        "source_input_images": source_input_counts,
        "deduplication": deduplication,
        **output_stats,
        "target_classes": TARGET_NAMES,
        "near_duplicate_hamming_threshold": NEAR_DUPLICATE_DISTANCE,
        "maximum_negative_images": MAX_NEGATIVE_IMAGES,
    }
    report_path = ROOT / "reports" / "dataset_preparation_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
