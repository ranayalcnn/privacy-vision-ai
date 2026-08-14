from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str


class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float = Field(ge=0, le=1)
    box: BoundingBox
    track_id: int | None = None


class ForkliftDetectionResponse(BaseModel):
    image_width: int
    image_height: int
    detection_count: int
    detections: list[Detection]
