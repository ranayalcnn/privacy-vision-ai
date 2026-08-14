# Installation Guide

## Requirements

- Python 3.10 or newer
- A webcam or a video source
- Optional NVIDIA GPU for faster inference

## Setup

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

Place `yolov8n-face.pt` in the project directory and run:

```bash
python main.py
```

Press `q` to stop the pipeline. The system writes only metadata to
`privacy_audit.jsonl`; original frames are not written to disk.
