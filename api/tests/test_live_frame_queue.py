from __future__ import annotations

import asyncio
import threading

import pytest

from api.services.live_frame_queue import FrameSuperseded, LatestFrameQueue


def test_latest_frame_queue_keeps_active_and_newest_frame_only() -> None:
    async def scenario() -> None:
        queue = LatestFrameQueue()
        first_started = threading.Event()
        release_first = threading.Event()
        calls: list[str] = []

        def first() -> str:
            calls.append("first")
            first_started.set()
            assert release_first.wait(timeout=2)
            return "first-result"

        def second() -> str:
            calls.append("second")
            return "second-result"

        def third() -> str:
            calls.append("third")
            return "third-result"

        first_task = asyncio.create_task(queue.submit("camera", first))
        assert await asyncio.to_thread(first_started.wait, 1)

        second_task = asyncio.create_task(queue.submit("camera", second))
        await asyncio.sleep(0)
        third_task = asyncio.create_task(queue.submit("camera", third))
        await asyncio.sleep(0)

        with pytest.raises(FrameSuperseded):
            await second_task

        release_first.set()
        assert await first_task == "first-result"
        assert await third_task == "third-result"
        assert calls == ["first", "third"]
        assert queue._sessions == {}

    asyncio.run(scenario())

