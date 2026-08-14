from datetime import datetime, timezone
from pathlib import Path
import json
import time

import cv2

from tracker import ObjectTracker
from yolo_detector import YOLODetector
from person_segmenter import PersonSegmenter
from blur import (
    apply_blur,
    apply_full_frame_blur,
    apply_segmentation_blur,
)
from person_remover import remove_people


BASE_DIR = Path(__file__).resolve().parent

INPUT_PATH = BASE_DIR / "input.mp4"
OUTPUT_PATH = BASE_DIR / "output.mp4"
AUDIT_LOG_PATH = BASE_DIR / "audit.log"

# "blur" veya "remove"
ANONYMIZATION_MODE = "blur"

BODY_BLUR_STRENGTH = 71
MASK_DILATION = 21
MASK_FEATHER = 31
FULL_FRAME_BLUR_STRENGTH = 101


def face_is_inside_person(face_box, person_box):
    face_x1, face_y1, face_x2, face_y2 = face_box
    person_x1, person_y1, person_x2, person_y2 = person_box

    face_center_x = (face_x1 + face_x2) // 2
    face_center_y = (face_y1 + face_y2) // 2

    return (
        person_x1 <= face_center_x <= person_x2
        and person_y1 <= face_center_y <= person_y2
    )


def apply_fallback_blur(frame, people, faces):
    """
    Segmentasyon maskesi bulunamadığında tracker ve
    yüz detector sonuçlarını kullanır.
    """
    safe_frame = frame.copy()
    applied_count = 0

    # Önce takip edilen insanların tamamını blurla.
    for person in people:
        safe_frame = apply_blur(
            safe_frame,
            person["box"],
            blur_strength=71,
            padding_ratio=0.08,
        )

        applied_count += 1

    # İnsan kutusuyla eşleşmeyen yüzler varsa onları da blurla.
    for face in faces:
        face_box = face["box"]

        matched_person = any(
            face_is_inside_person(
                face_box,
                person["box"],
            )
            for person in people
        )

        if not matched_person:
            safe_frame = apply_blur(
                safe_frame,
                face_box,
                blur_strength=51,
                padding_ratio=0.25,
            )

            applied_count += 1

    return safe_frame, applied_count


def write_audit_log(
    log_file,
    frame_id,
    timestamp_ms,
    tracked_people,
    detected_faces,
    segmented_people,
    anonymization_mode,
    status,
    processing_time_ms,
    mask_coverage,
    error_code=None,
):
    event = {
        "event_time": datetime.now(
            timezone.utc
        ).isoformat(),

        "frame_id": frame_id,
        "video_timestamp_ms": timestamp_ms,

        "tracked_people": tracked_people,
        "detected_faces": detected_faces,
        "segmented_people": segmented_people,

        "anonymization_mode": anonymization_mode,
        "status": status,

        "processing_time_ms": round(
            processing_time_ms,
            2,
        ),

        "mask_coverage_ratio": round(
            mask_coverage,
            4,
        ),

        "error_code": error_code,
    }

    log_file.write(
        json.dumps(
            event,
            ensure_ascii=False,
        ) + "\n"
    )

    log_file.flush()


def validate_files():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Test videosu bulunamadı: {INPUT_PATH}"
        )

    if ANONYMIZATION_MODE not in {
        "blur",
        "remove",
    }:
        raise ValueError(
            "ANONYMIZATION_MODE yalnızca "
            "'blur' veya 'remove' olabilir."
        )


def main():
    validate_files()

    capture = cv2.VideoCapture(
        str(INPUT_PATH)
    )

    if not capture.isOpened():
        raise RuntimeError(
            f"Video açılamadı: {INPUT_PATH}"
        )

    fps = capture.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:
        fps = 25.0

    width = int(
        capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    writer = cv2.VideoWriter(
        str(OUTPUT_PATH),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        capture.release()

        raise RuntimeError(
            f"Çıktı videosu oluşturulamadı: "
            f"{OUTPUT_PATH}"
        )

    tracker = ObjectTracker()
    face_detector = YOLODetector()
    segmenter = PersonSegmenter()

    frame_id = 0
    previous_timestamp_ms = -1

    print(f"Input: {INPUT_PATH}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Mode: {ANONYMIZATION_MODE}")
    print(f"FPS: {fps:.2f}")
    print(f"Frame count: {total_frames}")
    print("Processing started...")

    try:
        with AUDIT_LOG_PATH.open(
            "w",
            encoding="utf-8",
        ) as audit_file:

            while True:
                success, raw_frame = (
                    capture.read()
                )

                if not success:
                    break

                started_at = (
                    time.perf_counter()
                )

                timestamp_ms = int(
                    capture.get(
                        cv2.CAP_PROP_POS_MSEC
                    )
                )

                if (
                    timestamp_ms
                    <= previous_timestamp_ms
                ):
                    timestamp_ms = (
                        previous_timestamp_ms + 1
                    )

                previous_timestamp_ms = (
                    timestamp_ms
                )

                people = []
                faces = []
                segmentation_results = []

                segmented_count = 0
                mask_coverage = 0.0
                error_code = None
                status = "success"

                try:
                    # 1. Tracking
                    people = tracker.track_people(
                        raw_frame
                    )

                    # 2. Yüz tespiti
                    faces = (
                        face_detector.detect_faces(
                            raw_frame
                        )
                    )

                    # 3. Tüm vücut segmentasyonu
                    segmentation_results = (
                        segmenter.segment(
                            raw_frame
                        )
                    )

                    # 4. Birincil anonimleştirme
                    if ANONYMIZATION_MODE == "blur":
                        (
                            anonymized_frame,
                            segmented_count,
                            mask_coverage,
                        ) = apply_segmentation_blur(
                            raw_frame,
                            segmentation_results,
                            blur_strength=(
                                BODY_BLUR_STRENGTH
                            ),
                            dilation_size=(
                                MASK_DILATION
                            ),
                            feather_size=(
                                MASK_FEATHER
                            ),
                        )

                    else:
                        (
                            anonymized_frame,
                            segmented_count,
                        ) = remove_people(
                            raw_frame,
                            segmentation_results,
                        )

                    # 5. Segmentasyon bulunamadıysa
                    # tracker ve yüz detector yedeği.
                    if segmented_count == 0:
                        (
                            anonymized_frame,
                            fallback_count,
                        ) = apply_fallback_blur(
                            raw_frame,
                            people,
                            faces,
                        )

                        if fallback_count > 0:
                            status = "fallback"
                            error_code = (
                                "SEGMENTATION_MISSING"
                            )

                            anonymization_result = (
                                "tracking_box_blur"
                            )

                        else:
                            # Hiçbir model insan bulamadı.
                            anonymized_frame = (
                                apply_full_frame_blur(
                                    raw_frame,
                                    blur_strength=(
                                        FULL_FRAME_BLUR_STRENGTH
                                    ),
                                )
                            )

                            status = "fail_safe"
                            error_code = (
                                "NO_DETECTION"
                            )

                            anonymization_result = (
                                "full_frame_blur"
                            )

                    elif (
                        ANONYMIZATION_MODE
                        == "remove"
                    ):
                        anonymization_result = (
                            "segmentation_remove"
                        )

                    else:
                        anonymization_result = (
                            "segmentation_body_blur"
                        )

                except Exception as error:
                    # Herhangi bir model hata verirse
                    # ham frame çıktı olarak yazılmaz.
                    anonymized_frame = (
                        apply_full_frame_blur(
                            raw_frame,
                            blur_strength=(
                                FULL_FRAME_BLUR_STRENGTH
                            ),
                        )
                    )

                    status = "fail_safe"
                    error_code = type(
                        error
                    ).__name__

                    anonymization_result = (
                        "full_frame_blur"
                    )

                processing_time_ms = (
                    time.perf_counter()
                    - started_at
                ) * 1000

                write_audit_log(
                    log_file=audit_file,
                    frame_id=frame_id,
                    timestamp_ms=timestamp_ms,
                    tracked_people=len(people),
                    detected_faces=len(faces),
                    segmented_people=(
                        segmented_count
                    ),
                    anonymization_mode=(
                        anonymization_result
                    ),
                    status=status,
                    processing_time_ms=(
                        processing_time_ms
                    ),
                    mask_coverage=mask_coverage,
                    error_code=error_code,
                )

                # Yalnızca anonimleştirilmiş
                # görüntü diske yazılır.
                writer.write(
                    anonymized_frame
                )

                del raw_frame

                frame_id += 1

                if frame_id % 30 == 0:
                    print(
                        f"Processed: "
                        f"{frame_id}/"
                        f"{total_frames}"
                    )

    finally:
        capture.release()
        writer.release()
        cv2.destroyAllWindows()

    print("Processing completed.")
    print(f"Output video: {OUTPUT_PATH}")
    print(f"Audit log: {AUDIT_LOG_PATH}")


if __name__ == "__main__":
    main()