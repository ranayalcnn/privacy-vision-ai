import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))

from privacy_compliance import PrivacyAudit, fail_safe, validate_privacy_config


def test_original_storage_is_rejected():
    try:
        validate_privacy_config(save_original=True)
    except ValueError:
        return
    raise AssertionError("Original-frame storage must be rejected")


def test_fail_safe_changes_frame():
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    frame[20:100, 40:120] = 255
    protected = fail_safe(frame)
    assert protected.shape == frame.shape
    assert not np.array_equal(protected, frame)


def test_audit_contains_metadata_only(tmp_path):
    path = tmp_path / "audit.jsonl"
    PrivacyAudit(path).write("test", frame_number=1, face_count=2)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["event"] == "test"
    assert "image" not in data
    assert "frame" not in data or data["frame"] != "pixels"
