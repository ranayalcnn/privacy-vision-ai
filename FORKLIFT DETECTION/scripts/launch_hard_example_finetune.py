import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def main() -> None:
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    with (RUNS / "hardclip_finetune.stdout.log").open("w", encoding="utf-8") as out, (
        RUNS / "hardclip_finetune.stderr.log"
    ).open("w", encoding="utf-8") as err:
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts/resume_hard_example_finetune.py")],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            creationflags=flags,
            close_fds=True,
        )
    (RUNS / "hardclip_finetune.pid").write_text(str(process.pid), encoding="utf-8")
    print(process.pid)


if __name__ == "__main__":
    main()
