# System Architecture

```mermaid
flowchart LR
    A[Camera or video source] --> B[Capture thread]
    B --> C[Bounded frame queue]
    C --> D[YOLO face detection and tracking]
    D --> E[Privacy mode or fail-safe blur]
    E --> F[Protected display/output]
    D --> G[Metadata-only audit log]
```

The queue is bounded so that delayed processing does not create an unlimited
backlog. The original frame exists only in memory during processing. The
audit branch receives metadata and never receives pixel arrays.
