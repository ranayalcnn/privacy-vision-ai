# User Guide

The application captures a frame, detects faces, applies the selected privacy
transformation, and displays the protected frame. The dashboard reports FPS,
latency, queue size, dropped frames, and detected-face count.

If no reliable face is detected, the fail-safe policy protects the complete
frame with a strong blur. This prevents an unprotected frame from being sent
to the display or a downstream analytics component.

## Privacy modes

`SOFT BLUR`, `MOSAIC`, and `COLOR SHIELD` are provided by `PrivacyMode`.
The selected mode is recorded in the audit log without recording image data.
