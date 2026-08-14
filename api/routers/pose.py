from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.background import BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, Response

from api.image_io import encode_jpeg, encode_live_overlay, read_image
from api.services.pose import pose_service
from api.services.live_frame_queue import FrameSuperseded, latest_frame_queue
from api.services.video import VideoProcessingError, estimate_pose_video
from api.video_io import output_video_path, remove_runtime_files, save_video_upload


router = APIRouter(prefix="/pose", tags=["Duruş Analizi"])


@router.post("/live", response_class=Response)
async def estimate_live_pose_frame(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
    session_id: str = Query(..., min_length=8, max_length=80),
) -> Response:
    started_at = perf_counter()
    image = await read_image(file)
    try:
        processed, count = await latest_frame_queue.submit(
            f"pose:{session_id}",
            lambda: pose_service.track(image, confidence, session_id, 320),
        )
    except FrameSuperseded:
        return Response(status_code=204, headers={"X-Frame-Dropped": "true"})
    content = await run_in_threadpool(encode_live_overlay, image, processed)
    processing_ms = (perf_counter() - started_at) * 1000
    return Response(
        content=content,
        media_type="image/png",
        headers={
            "X-Pose-Count": str(count),
            "X-Tracking-Enabled": "bytetrack",
            "X-Live-Overlay": "true",
            "X-Processing-Time-Ms": f"{processing_ms:.1f}",
            "Server-Timing": f"analysis;dur={processing_ms:.1f}",
        },
    )


@router.post("/estimate", response_class=Response)
async def estimate_pose_image(
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
    fast: bool = Query(False),
) -> Response:
    started_at = perf_counter()
    image = await read_image(file)
    processed, count = await run_in_threadpool(
        pose_service.estimate,
        image,
        confidence,
        384 if fast else 640,
    )
    content = await run_in_threadpool(encode_jpeg, processed)
    processing_ms = (perf_counter() - started_at) * 1000
    return Response(
        content=content,
        media_type="image/jpeg",
        headers={
            "X-Pose-Count": str(count),
            "X-Processing-Time-Ms": f"{processing_ms:.1f}",
            "Server-Timing": f"analysis;dur={processing_ms:.1f}",
        },
    )


@router.post("/estimate-video", response_class=FileResponse)
async def estimate_pose_video_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
) -> FileResponse:
    input_path = await save_video_upload(file)
    output_path = output_video_path()
    try:
        stats = await run_in_threadpool(
            estimate_pose_video, input_path, output_path, confidence
        )
    except VideoProcessingError as error:
        remove_runtime_files(input_path, output_path)
        raise HTTPException(status_code=400, detail=str(error)) from error

    background_tasks.add_task(remove_runtime_files, input_path, output_path)
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="vucut-durusu-analizi.mp4",
        headers={
            "X-Frame-Count": str(stats["frame_count"]),
            "X-Pose-Count": str(stats["pose_count"]),
        },
        background=background_tasks,
    )
