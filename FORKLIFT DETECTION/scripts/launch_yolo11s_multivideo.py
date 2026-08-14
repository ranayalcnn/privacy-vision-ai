import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    with (ROOT / "runs/yolo11s_multivideo.stdout.log").open("w", encoding="utf-8") as out, (
        ROOT / "runs/yolo11s_multivideo.stderr.log"
    ).open("w", encoding="utf-8") as err:
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts/train_yolo11s_multivideo.py")],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            creationflags=flags,
            close_fds=True,
        )
    (ROOT / "runs/yolo11s_multivideo.pid").write_text(str(process.pid), encoding="utf-8")
    print(process.pid)
