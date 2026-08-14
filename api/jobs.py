from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event, Lock, Thread
from time import time
from uuid import uuid4

from api.services.people import PeopleMode
from api.services.privacy import PrivacyMode
from api.config import settings
from api.services.video import (
    VideoProcessingCancelled,
    anonymize_video,
    detect_video,
    estimate_pose_video,
    process_people_video,
)
from api.video_io import output_video_path, remove_runtime_files


class VideoJobCapacityError(RuntimeError):
    pass


@dataclass
class VideoJob:
    id: str
    operation: str
    input_path: Path
    output_path: Path
    status: str = "queued"
    processed_frames: int = 0
    total_frames: int = 0
    stats: dict[str, int] = field(default_factory=dict)
    error: str | None = None
    created_at: float = field(default_factory=time)
    finished_at: float | None = None
    cancel_event: Event = field(default_factory=Event)
    selected_point: tuple[float, float] | None = None

    @property
    def progress(self) -> int:
        if self.status == "completed":
            return 100
        if self.total_frames <= 0:
            return 0
        return min(99, round(self.processed_frames / self.total_frames * 100))


class VideoJobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, VideoJob] = {}
        self._lock = Lock()
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="video-job",
        )
        self._cleanup_stop = Event()
        self._cleanup_thread = Thread(
            target=self._cleanup_loop,
            name="video-job-cleanup",
            daemon=True,
        )
        self._cleanup_thread.start()

    def create(
        self,
        input_path: Path,
        operation: str,
        mode: str | None,
        confidence: float,
        selected_point: tuple[float, float] | None = None,
    ) -> VideoJob:
        job = VideoJob(
            id=uuid4().hex,
            operation=operation,
            input_path=input_path,
            output_path=output_video_path(),
            selected_point=selected_point,
        )
        with self._lock:
            active_jobs = sum(
                item.status in {"queued", "processing"}
                for item in self._jobs.values()
            )
            if active_jobs >= settings.max_active_video_jobs:
                remove_runtime_files(input_path)
                raise VideoJobCapacityError(
                    "Video işlem sırası dolu. Lütfen kısa süre sonra tekrar deneyin."
                )
            self._jobs[job.id] = job
        self._executor.submit(self._run, job, mode, confidence)
        return job

    def get(self, job_id: str) -> VideoJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> VideoJob | None:
        job = self.get(job_id)
        if job is not None and job.status in {"queued", "processing"}:
            job.cancel_event.set()
        return job

    def cleanup(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.pop(job_id, None)
        if job is not None:
            remove_runtime_files(job.input_path, job.output_path)

    def cleanup_expired(self, now: float | None = None) -> int:
        current_time = time() if now is None else now
        expired_jobs: list[VideoJob] = []
        with self._lock:
            for job_id, job in list(self._jobs.items()):
                if (
                    job.finished_at is not None
                    and current_time - job.finished_at
                    >= settings.video_job_ttl_seconds
                ):
                    expired_jobs.append(self._jobs.pop(job_id))

        for job in expired_jobs:
            remove_runtime_files(job.input_path, job.output_path)
        return len(expired_jobs)

    def _cleanup_loop(self) -> None:
        interval = max(1, settings.video_job_cleanup_interval_seconds)
        while not self._cleanup_stop.wait(interval):
            self.cleanup_expired()

    def shutdown(self) -> None:
        self._cleanup_stop.set()
        self._cleanup_thread.join(timeout=2)
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _progress(self, job: VideoJob, processed: int, total: int) -> None:
        job.processed_frames = processed
        job.total_frames = total

    def _run(self, job: VideoJob, mode: str | None, confidence: float) -> None:
        job.status = "processing"
        callback = lambda processed, total: self._progress(job, processed, total)
        try:
            if job.operation == "privacy":
                stats = anonymize_video(
                    job.input_path,
                    job.output_path,
                    PrivacyMode(mode or PrivacyMode.soft_blur),
                    confidence,
                    callback,
                    job.cancel_event,
                )
            elif job.operation in {"people_blur", "people_remove"}:
                people_mode = (
                    PeopleMode.remove
                    if job.operation == "people_remove"
                    else PeopleMode.blur
                )
                stats = process_people_video(
                    job.input_path,
                    job.output_path,
                    people_mode,
                    confidence,
                    callback,
                    job.cancel_event,
                    job.selected_point,
                )
            elif job.operation == "forklift":
                stats = detect_video(
                    job.input_path,
                    job.output_path,
                    confidence,
                    callback,
                    job.cancel_event,
                )
            elif job.operation == "pose":
                stats = estimate_pose_video(
                    job.input_path,
                    job.output_path,
                    confidence,
                    callback,
                    job.cancel_event,
                )
            else:
                raise ValueError("Desteklenmeyen video işlemi.")

            job.stats = stats
            job.processed_frames = stats.get("frame_count", job.processed_frames)
            job.total_frames = max(job.total_frames, job.processed_frames)
            job.status = "completed"
        except VideoProcessingCancelled as error:
            job.status = "cancelled"
            job.error = str(error)
            remove_runtime_files(job.output_path)
        except Exception as error:
            job.status = "failed"
            job.error = str(error)
            remove_runtime_files(job.output_path)
        finally:
            job.finished_at = time()
            remove_runtime_files(job.input_path)


video_job_manager = VideoJobManager()
