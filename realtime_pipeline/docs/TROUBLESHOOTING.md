# Troubleshooting

| Problem | Solution |
|---|---|
| Camera cannot be opened | Change `SOURCE` in `config.py` to `1`, or use a video path. |
| Low FPS | Reduce `IMAGE_SIZE`, increase `DETECT_INTERVAL`, or use a GPU. |
| Blur disappears during motion | Check tracker support and lower `DETECT_INTERVAL`. |
| Entire frame becomes blurred | This is the fail-safe mode; verify lighting and confidence threshold. |
| Model not found | Place `yolov8n-face.pt` beside `main.py`. |
| Audit log cannot be written | Check write permission for the project directory. |
| Window does not appear | Run locally with a graphical desktop rather than a headless server. |
