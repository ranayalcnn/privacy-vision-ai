from __future__ import annotations

from collections import defaultdict, deque
import hmac
from threading import Lock
from time import monotonic

from fastapi import Header, HTTPException, Request, status

from api.config import settings


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self._last_cleanup = monotonic()

    def check(self, key: str, now: float | None = None) -> None:
        limit = settings.rate_limit_requests
        window = settings.rate_limit_window_seconds
        if limit <= 0 or window <= 0:
            return

        current_time = monotonic() if now is None else now
        window_start = current_time - window
        with self._lock:
            if current_time - self._last_cleanup >= window:
                stale_keys = [
                    request_key
                    for request_key, timestamps in self._requests.items()
                    if not timestamps or timestamps[-1] <= window_start
                ]
                for request_key in stale_keys:
                    self._requests.pop(request_key, None)
                self._last_cleanup = current_time

            requests = self._requests[key]
            while requests and requests[0] <= window_start:
                requests.popleft()
            if len(requests) >= limit:
                retry_after = max(1, round(requests[0] + window - current_time))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Çok fazla istek gönderildi. Lütfen kısa süre sonra tekrar deneyin.",
                    headers={"Retry-After": str(retry_after)},
                )
            requests.append(current_time)

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()
            self._last_cleanup = monotonic()


rate_limiter = SlidingWindowRateLimiter()


async def enforce_api_access(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> None:
    if settings.api_key and (
        x_api_key is None or not hmac.compare_digest(x_api_key, settings.api_key)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçerli bir API anahtarı gerekli.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        client_host = request.client.host if request.client else "unknown"
        rate_limiter.check(client_host)
