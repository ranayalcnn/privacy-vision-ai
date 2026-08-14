from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.background import BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, Response

from api.image_io import encode_jpeg, read_image
from api.services.live_privacy import live_privacy_service
from api.services.live_frame_queue import FrameSuperseded, latest_frame_queue
from api.services.privacy import PrivacyMode, privacy_service
from api.services.video import VideoProcessingError, anonymize_video
from api.video_io import output_video_path, remove_runtime_files, save_video_upload


router = APIRouter(prefix="/privacy", tags=["Anonimleştirme"])


@router.post(
    "/live",
    response_class=Response,
    summary="Canlı kamera karesini takip ederek anonimleştir",
)
async def anonymize_live_frame(
    file: UploadFile = File(...),
    mode: PrivacyMode = Query(PrivacyMode.soft_blur),
    confidence: float = Query(0.30, ge=0.1, le=1.0),
    session_id: str = Query(..., min_length=8, max_length=80),
    gesture_control: bool = Query(False),
) -> Response:
    started_at = perf_counter()
    image = await read_image(file)
    try:
        result = await latest_frame_queue.submit(
            f"privacy:{session_id}",
            lambda: live_privacy_service.process(
                image,
                mode,
                confidence,
                session_id,
                gesture_control,
            ),
        )
    except FrameSuperseded:
        return Response(status_code=204, headers={"X-Frame-Dropped": "true"})
    content = await run_in_threadpool(encode_jpeg, result.image, 80)
    processing_ms = (perf_counter() - started_at) * 1000
    return Response(
        content=content,
        media_type="image/jpeg",
        headers={
            "X-Face-Count": str(result.face_count),
            "X-Tracking-Enabled": "true",
            "X-Gesture-Control-Available": str(result.gesture_available).lower(),
            "X-Privacy-Enabled": str(result.privacy_enabled).lower(),
            "X-Privacy-Mode": result.mode.value,
            "X-Gesture": result.gesture or "none",
            "X-Processing-Time-Ms": f"{processing_ms:.1f}",
            "Server-Timing": f"analysis;dur={processing_ms:.1f}",
        },
    )


@router.post(
    "/anonymize",
    response_class=Response,
    summary="Görüntüdeki yüzleri anonimleştir",
)
async def anonymize_image(
    file: UploadFile = File(...),
    mode: PrivacyMode = Query(PrivacyMode.soft_blur),
    confidence: float = Query(0.30, ge=0.1, le=1.0),
    fast: bool = Query(False),
) -> Response:
    started_at = perf_counter()
    image = await read_image(file)
    protected, face_count, fail_safe = await run_in_threadpool(
        privacy_service.anonymize,
        image,
        mode,
        confidence,
        384 if fast else 640,
    )
    content = await run_in_threadpool(encode_jpeg, protected)
    processing_ms = (perf_counter() - started_at) * 1000
    return Response(
        content=content,
        media_type="image/jpeg",
        headers={
            "X-Face-Count": str(face_count),
            "X-Fail-Safe-Applied": str(fail_safe).lower(),
            "X-Processing-Time-Ms": f"{processing_ms:.1f}",
            "Server-Timing": f"analysis;dur={processing_ms:.1f}",
        },
    )


@router.post(
    "/anonymize-video",
    response_class=FileResponse,
    summary="Videodaki yüzleri anonimleştir",
)
async def anonymize_video_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: PrivacyMode = Query(PrivacyMode.soft_blur),
    confidence: float = Query(0.30, ge=0.1, le=1.0),
) -> FileResponse:
    input_path = await save_video_upload(file)
    output_path = output_video_path()
    try:
        stats = await run_in_threadpool(
            anonymize_video, input_path, output_path, mode, confidence
        )
    except VideoProcessingError as error:
        remove_runtime_files(input_path, output_path)
        raise HTTPException(status_code=400, detail=str(error)) from error

    background_tasks.add_task(remove_runtime_files, input_path, output_path)
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="anonimlestirilmis-video.mp4",
        headers={
            "X-Frame-Count": str(stats["frame_count"]),
            "X-Face-Count": str(stats["face_count"]),
        },
        background=background_tasks,
    )
