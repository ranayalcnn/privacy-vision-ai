from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi.concurrency import run_in_threadpool


class FrameSuperseded(Exception):
    """Raised when a newer camera frame replaces a frame waiting in line."""


@dataclass
class _FrameWork:
    callback: Callable[[], Any]
    future: asyncio.Future[Any]


@dataclass
class _SessionQueue:
    active: bool = False
    pending: _FrameWork | None = None


class LatestFrameQueue:
    """Run one model call per session and retain at most one pending frame."""

    def __init__(self) -> None:
        self._sessions: dict[str, _SessionQueue] = {}
        self._lock = asyncio.Lock()

    async def submit(self, session_key: str, callback: Callable[[], Any]) -> Any:
        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        work = _FrameWork(callback=callback, future=future)

        async with self._lock:
            queue = self._sessions.setdefault(session_key, _SessionQueue())
            if queue.pending is not None and not queue.pending.future.done():
                queue.pending.future.set_exception(FrameSuperseded())
            queue.pending = work
            if not queue.active:
                queue.active = True
                asyncio.create_task(self._drain(session_key, queue))

        return await future

    async def _drain(self, session_key: str, queue: _SessionQueue) -> None:
        while True:
            async with self._lock:
                work = queue.pending
                queue.pending = None
                if work is None:
                    queue.active = False
                    if self._sessions.get(session_key) is queue:
                        self._sessions.pop(session_key, None)
                    return

            try:
                result = await run_in_threadpool(work.callback)
            except Exception as error:
                if not work.future.done():
                    work.future.set_exception(error)
            else:
                if not work.future.done():
                    work.future.set_result(result)


latest_frame_queue = LatestFrameQueue()
