# api/middleware/rate_limiter.py
import time
from collections import deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

class PolygonRateLimiter(BaseHTTPMiddleware):
    """
    Middleware to enforce Polygon API rate limits (5 requests per minute).
    
    This middleware tracks requests to Polygon endpoints and enforces the rate limit
    by delaying or rejecting requests that would exceed the limit.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Use a deque to track timestamps of recent requests
        self.request_times = deque(maxlen=100)
        self.max_requests = 5  # 5 requests
        self.time_window = 60  # per 60 seconds (1 minute)
    
    async def dispatch(self, request: Request, call_next):
        # Only apply rate limiting to Polygon-related API endpoints
        if "/api/v1/stocks/" in request.url.path or "/api/v1/indices/" in request.url.path or "/api/v1/options/" in request.url.path:
            current_time = time.time()
            
            # Remove requests older than the time window
            while self.request_times and current_time - self.request_times[0] > self.time_window:
                self.request_times.popleft()
            
            # If we've hit the rate limit, either wait or reject
            if len(self.request_times) >= self.max_requests:
                oldest_request = self.request_times[0]
                time_to_wait = oldest_request + self.time_window - current_time
                
                # If we need to wait more than 5 seconds, reject the request
                if time_to_wait > 5:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {int(time_to_wait)} seconds."
                    )
                # Otherwise, wait until we can process the request
                else:
                    time.sleep(time_to_wait)
            
            # Add the current request time
            self.request_times.append(current_time)
        
        # Process the request
        response = await call_next(request)
        return response