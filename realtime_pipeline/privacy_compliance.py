import json
import time
from pathlib import Path


class PrivacyAudit:
    """Writes processing metadata only; image pixels are never logged."""

    def __init__(self, path="privacy_audit.jsonl"):
        self.path = Path(path)

    def write(self, event, **data):
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event,
            **data,
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate_privacy_config(save_original=False):
    if save_original:
        raise ValueError(
            "Privacy policy violation: original frame storage is disabled."
        )


def fail_safe(frame, reason="detection_failure"):
    """Protects the full frame when face detection cannot be trusted."""
    import cv2

    return cv2.GaussianBlur(frame, (99, 99), 0)
