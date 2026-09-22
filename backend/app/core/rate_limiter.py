import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Lightweight rate limiter middleware tracking requests per IP.
    Returns HTTP 429 Too Many Requests if client exceeds limit.
    """
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.client_history: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        # Rate limit only sensitive public paths
        path = request.url.path
        if path.startswith("/api/v1/public/chat") or path.startswith("/api/v1/auth"):
            client_ip = request.client.host if request.client else "127.0.0.1"
            now = time.time()
            
            # Clean old timestamps
            timestamps = [t for t in self.client_history.get(client_ip, []) if now - t < self.window_seconds]
            
            if len(timestamps) >= self.max_requests:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too Many Requests: Rate limit exceeded. Please try again later."}
                )

            timestamps.append(now)
            self.client_history[client_ip] = timestamps

        response = await call_next(request)
        return response
