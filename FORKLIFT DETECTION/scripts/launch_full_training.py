"""Launch the full training as a detached Windows process."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
STDOUT = RUNS / "full_train.stdout.log"
STDERR = RUNS / "full_train.stderr.log"
PID_FILE = RUNS / "full_train.pid"


def main() -> None:
    creation_flags = (
        subprocess.CREATE_NO_WINDOW
        | subprocess.DETACHED_PROCESS
        | subprocess.CREATE_NEW_PROCESS_GROUP
    )
    with STDOUT.open("w", encoding="utf-8") as stdout_handle, STDERR.open(
        "w", encoding="utf-8"
    ) as stderr_handle:
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts" / "train_full.py")],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=creation_flags,
            close_fds=True,
        )
    PID_FILE.write_text(str(process.pid), encoding="utf-8")
    print(process.pid)


if __name__ == "__main__":
    main()
