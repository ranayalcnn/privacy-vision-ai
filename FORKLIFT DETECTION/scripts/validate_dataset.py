"""Validate image/label pairing and YOLO annotation integrity."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "processed"
REPORT = ROOT / "reports" / "dataset_validation_report.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
CLASS_COUNT = 4


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    split_stats: dict[str, dict] = {}
    hashes: dict[str, str] = {}
    class_instances: Counter[int] = Counter()

    for split in ("train", "val", "test"):
        image_dir = DATASET / "images" / split
        label_dir = DATASET / "labels" / split
        images = sorted(
            path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS
        )
        labels = sorted(label_dir.glob("*.txt"))
        image_stems = {path.stem for path in images}
        label_stems = {path.stem for path in labels}
        missing_labels = sorted(image_stems - label_stems)
        missing_images = sorted(label_stems - image_stems)
        if missing_labels:
            errors.append(f"{split}: {len(missing_labels)} missing label files")
        if missing_images:
            errors.append(f"{split}: {len(missing_images)} labels without images")

        empty_labels = 0
        for image_path in images:
            try:
                with Image.open(image_path) as image:
                    image.verify()
            except Exception as exc:
                errors.append(f"Unreadable image {image_path}: {exc}")
            digest = sha256(image_path)
            previous = hashes.get(digest)
            if previous is not None:
                errors.append(
                    f"Exact duplicate across processed dataset: {previous} and {image_path}"
                )
            else:
                hashes[digest] = str(image_path)

            label_path = label_dir / f"{image_path.stem}.txt"
            if not label_path.exists():
                continue
            lines = [
                line.strip()
                for line in label_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            if not lines:
                empty_labels += 1
            for line_number, line in enumerate(lines, start=1):
                parts = line.split()
                if len(parts) != 5:
                    errors.append(f"{label_path}:{line_number}: expected 5 fields")
                    continue
                try:
                    class_id = int(parts[0])
                    coordinates = [float(value) for value in parts[1:]]
                except ValueError:
                    errors.append(f"{label_path}:{line_number}: non-numeric annotation")
                    continue
                if not 0 <= class_id < CLASS_COUNT:
                    errors.append(f"{label_path}:{line_number}: invalid class {class_id}")
                if not all(0.0 <= value <= 1.0 for value in coordinates):
                    errors.append(f"{label_path}:{line_number}: coordinate outside [0,1]")
                if coordinates[2] <= 0 or coordinates[3] <= 0:
                    errors.append(f"{label_path}:{line_number}: non-positive box size")
                class_instances[class_id] += 1

        split_stats[split] = {
            "images": len(images),
            "labels": len(labels),
            "empty_labels": empty_labels,
        }

    if class_instances[3] < 500:
        warnings.append("pallet_truck has fewer than 500 instances")

    report = {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "splits": split_stats,
        "class_instances": {
            "forklift": class_instances[0],
            "person": class_instances[1],
            "pallet": class_instances[2],
            "pallet_truck": class_instances[3],
        },
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
