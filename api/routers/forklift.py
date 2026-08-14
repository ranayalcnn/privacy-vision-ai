from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.background import BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, Response

from api.image_io import read_image
from api.schemas import ForkliftDetectionResponse
from api.services.forklift import forklift_service
from api.services.live_frame_queue import FrameSuperseded, latest_frame_queue
from api.services.video import VideoProcessingError, detect_video
from api.video_io import output_video_path, remove_runtime_files, save_video_upload


router = APIRouter(prefix="/forklift", tags=["Depo Analizi"])


@router.post(
    "/detect",
    response_model=ForkliftDetectionResponse,
    summary="Forklift, insan, palet ve palet taşıma aracı tespit et",
)
async def detect_forklift_objects(
    response: Response,
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
    fast: bool = Query(False),
    session_id: str | None = Query(None, min_length=8, max_length=80),
) -> ForkliftDetectionResponse:
    started_at = perf_counter()
    image = await read_image(file)
    if session_id:
        try:
            result = await latest_frame_queue.submit(
                f"forklift:{session_id}",
                lambda: forklift_service.track(
                    image,
                    confidence,
                    session_id,
                    384 if fast else 640,
                ),
            )
        except FrameSuperseded:
            return Response(status_code=204, headers={"X-Frame-Dropped": "true"})
        response.headers["X-Tracking-Enabled"] = "bytetrack"
    else:
        result = await run_in_threadpool(
            forklift_service.detect,
            image,
            confidence,
            384 if fast else 640,
        )
    processing_ms = (perf_counter() - started_at) * 1000
    response.headers["X-Processing-Time-Ms"] = f"{processing_ms:.1f}"
    response.headers["Server-Timing"] = f"analysis;dur={processing_ms:.1f}"
    return result


@router.post(
    "/detect-video",
    response_class=FileResponse,
    summary="Videoda depo nesnelerini tespit et",
)
async def detect_forklift_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
) -> FileResponse:
    input_path = await save_video_upload(file)
    output_path = output_video_path()
    try:
        stats = await run_in_threadpool(
            detect_video, input_path, output_path, confidence
        )
    except VideoProcessingError as error:
        remove_runtime_files(input_path, output_path)
        raise HTTPException(status_code=400, detail=str(error)) from error

    background_tasks.add_task(remove_runtime_files, input_path, output_path)
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="depo-analizi.mp4",
        headers={
            "X-Frame-Count": str(stats["frame_count"]),
            "X-Forklift-Count": str(stats["forklift_count"]),
            "X-Person-Count": str(stats["person_count"]),
            "X-Pallet-Count": str(stats["pallet_count"]),
        },
        background=background_tasks,
    )
