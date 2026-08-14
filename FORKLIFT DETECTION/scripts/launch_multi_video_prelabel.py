import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    with (ROOT / "runs/multi_prelabel.stdout.log").open("w", encoding="utf-8") as out, (
        ROOT / "runs/multi_prelabel.stderr.log"
    ).open("w", encoding="utf-8") as err:
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts/prelabel_multi_video_frames.py")],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            creationflags=flags,
            close_fds=True,
        )
    (ROOT / "runs/multi_prelabel.pid").write_text(str(process.pid), encoding="utf-8")
    print(process.pid)
