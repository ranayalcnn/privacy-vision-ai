# Technical API

## `Capture`

`Capture(source, input_queue)` opens a camera or video source and pushes
`(frame_id, capture_time, frame)` tuples into a bounded queue. Old frames are
dropped when the queue is full to minimize latency.

## `Processor`

`Processor(audit_path)` loads the face detector and processes one frame.

`process(frame) -> (protected_frame, face_count)` detects, tracks, anonymizes,
and audits a frame. Detection failure invokes the fail-safe transformation.

## `PrivacyAudit`

`write(event, **data)` appends JSON Lines metadata. Pixel arrays, original
frames, and face crops must never be passed to this method.
