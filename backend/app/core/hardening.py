import asyncio
import time
import uuid
from collections import defaultdict, deque

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SlidingWindowRateLimiter:
    """Process-local limiter suited to the single-backend modular monolith."""

    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - window_seconds
        async with self._lock:
            if key not in self._requests and len(self._requests) >= 10_000:
                self._requests = defaultdict(
                    deque,
                    {
                        item: values
                        for item, values in self._requests.items()
                        if values and values[-1] > cutoff
                    },
                )
                if len(self._requests) >= 10_000:
                    return False, window_seconds
            timestamps = self._requests[key]
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= limit:
                retry_after = max(1, int(window_seconds - (now - timestamps[0])) + 1)
                return False, retry_after
            timestamps.append(now)
            return True, 0


rate_limiter = SlidingWindowRateLimiter()


class BodySizeLimitMiddleware:
    """Reject oversized streamed bodies before parsing or unbounded buffering."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_bytes:
                request_id = scope.get("state", {}).get("request_id", str(uuid.uuid4()))
                response = JSONResponse(
                    {
                        "error": {
                            "code": "request_too_large",
                            "message": "Request body is too large",
                            "request_id": request_id,
                        }
                    },
                    status_code=413,
                    headers={"X-Request-ID": request_id, "X-Content-Type-Options": "nosniff"},
                )
                await response(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)
