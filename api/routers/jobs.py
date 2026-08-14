from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from api.jobs import VideoJob, VideoJobCapacityError, video_job_manager
from api.video_io import save_video_upload


router = APIRouter(prefix="/jobs", tags=["Video İşleri"])
OPERATIONS = {"privacy", "people_blur", "people_remove", "forklift", "pose"}


def job_payload(job: VideoJob) -> dict:
    return {
        "id": job.id,
        "operation": job.operation,
        "status": job.status,
        "progress": job.progress,
        "processed_frames": job.processed_frames,
        "total_frames": job.total_frames,
        "stats": job.stats,
        "error": job.error,
    }


@router.post("/video", status_code=202)
async def create_video_job(
    file: UploadFile = File(...),
    operation: str = Query(...),
    mode: str | None = Query(None),
    confidence: float = Query(0.25, ge=0.1, le=1.0),
    selection_x: float | None = Query(None, ge=0.0, le=1.0),
    selection_y: float | None = Query(None, ge=0.0, le=1.0),
) -> dict:
    if operation not in OPERATIONS:
        raise HTTPException(status_code=400, detail="Geçersiz analiz aracı.")
    input_path = await save_video_upload(file)
    try:
        selected_point = (
            (selection_x, selection_y)
            if selection_x is not None and selection_y is not None
            else None
        )
        job = video_job_manager.create(
            input_path,
            operation,
            mode,
            confidence,
            selected_point,
        )
    except VideoJobCapacityError as error:
        raise HTTPException(
            status_code=429,
            detail=str(error),
            headers={"Retry-After": "10"},
        ) from error
    return job_payload(job)


@router.get("/{job_id}")
def get_video_job(job_id: str) -> dict:
    job = video_job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Video işi bulunamadı.")
    return job_payload(job)


@router.delete("/{job_id}")
def cancel_video_job(job_id: str) -> dict:
    job = video_job_manager.cancel(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Video işi bulunamadı.")
    return job_payload(job)


@router.get("/{job_id}/result", response_class=FileResponse)
def get_video_result(
    job_id: str,
    background_tasks: BackgroundTasks,
) -> FileResponse:
    job = video_job_manager.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Video işi bulunamadı.")
    if job.status != "completed" or not job.output_path.is_file():
        raise HTTPException(status_code=409, detail="Video sonucu henüz hazır değil.")

    background_tasks.add_task(video_job_manager.cleanup, job.id)
    return FileResponse(
        job.output_path,
        media_type="video/mp4",
        filename=f"{job.operation}-sonucu.mp4",
        headers={
            "X-Job-Stats": ",".join(
                f"{key}:{value}" for key, value in job.stats.items()
            )
        },
        background=background_tasks,
    )
