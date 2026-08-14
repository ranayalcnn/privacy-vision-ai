from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.background import BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, Response

from api.image_io import encode_jpeg, encode_live_overlay, read_image
from api.services.people import PeopleMode, people_service
from api.services.live_frame_queue import FrameSuperseded, latest_frame_queue
from api.services.video import VideoProcessingError, process_people_video
from api.video_io import output_video_path, remove_runtime_files, save_video_upload


router = APIRouter(prefix="/people", tags=["Kişi İşleme"])


@router.post("/live", response_class=Response)
async def process_live_people_frame(
    file: UploadFile = File(...),
    mode: PeopleMode = Query(PeopleMode.blur),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
    session_id: str = Query(..., min_length=8, max_length=80),
) -> Response:
    started_at = perf_counter()
    image = await read_image(file)
    try:
        processed, count = await latest_frame_queue.submit(
            f"people:{session_id}",
            lambda: people_service.track(
                image,
                mode,
                confidence,
                session_id,
                320,
            ),
        )
    except FrameSuperseded:
        return Response(status_code=204, headers={"X-Frame-Dropped": "true"})
    content = await run_in_threadpool(encode_live_overlay, image, processed)
    processing_ms = (perf_counter() - started_at) * 1000
    return Response(
        content=content,
        media_type="image/png",
        headers={
            "X-Person-Count": str(count),
            "X-Tracking-Enabled": "bytetrack",
            "X-Live-Overlay": "true",
            "X-Processing-Time-Ms": f"{processing_ms:.1f}",
            "Server-Timing": f"analysis;dur={processing_ms:.1f}",
        },
    )


@router.post("/process", response_class=Response)
async def process_people_image(
    file: UploadFile = File(...),
    mode: PeopleMode = Query(PeopleMode.blur),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
    fast: bool = Query(False),
    selection_x: float | None = Query(None, ge=0.0, le=1.0),
    selection_y: float | None = Query(None, ge=0.0, le=1.0),
) -> Response:
    started_at = perf_counter()
    image = await read_image(file)
    processed, count = await run_in_threadpool(
        people_service.process,
        image,
        mode,
        confidence,
        384 if fast else 640,
        (selection_x, selection_y)
        if selection_x is not None and selection_y is not None
        else None,
    )
    content = await run_in_threadpool(encode_jpeg, processed)
    processing_ms = (perf_counter() - started_at) * 1000
    return Response(
        content=content,
        media_type="image/jpeg",
        headers={
            "X-Person-Count": str(count),
            "X-Processing-Time-Ms": f"{processing_ms:.1f}",
            "Server-Timing": f"analysis;dur={processing_ms:.1f}",
        },
    )


@router.post("/process-video", response_class=FileResponse)
async def process_people_video_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: PeopleMode = Query(PeopleMode.blur),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
    selection_x: float | None = Query(None, ge=0.0, le=1.0),
    selection_y: float | None = Query(None, ge=0.0, le=1.0),
) -> FileResponse:
    input_path = await save_video_upload(file)
    output_path = output_video_path()
    try:
        stats = await run_in_threadpool(
            process_people_video,
            input_path,
            output_path,
            mode,
            confidence,
            None,
            None,
            (selection_x, selection_y)
            if selection_x is not None and selection_y is not None
            else None,
        )
    except VideoProcessingError as error:
        remove_runtime_files(input_path, output_path)
        raise HTTPException(status_code=400, detail=str(error)) from error

    background_tasks.add_task(remove_runtime_files, input_path, output_path)
    filename = (
        "insanlar-kaldirildi.mp4"
        if mode == PeopleMode.remove
        else "insanlar-bulaniklastirildi.mp4"
    )
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=filename,
        headers={
            "X-Frame-Count": str(stats["frame_count"]),
            "X-Person-Count": str(stats["person_count"]),
        },
        background=background_tasks,
    )
