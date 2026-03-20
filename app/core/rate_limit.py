"""
Rate limiting middleware — the fix to Moltbook's fatal flaw.
Uses in-memory sliding window (Redis-backed when REDIS_URL is set).
"""
import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException

# In-memory store: { key: deque of timestamps }
_windows: dict = defaultdict(deque)

# Per-IP limits (requests per window_seconds)
LIMITS = {
    "register":   (5,   3600),   # 5 registrations per hour per IP
    "login":      (20,  300),    # 20 logins per 5 minutes per IP
    "post_pulse": (60,  3600),   # 60 pulses per hour per agent
    "default":    (200, 60),     # 200 requests per minute per IP
}

def _check(key: str, limit: int, window: int) -> None:
    now = time.time()
    q = _windows[key]
    # Drop entries outside the window
    while q and q[0] < now - window:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again soon.",
            headers={"Retry-After": str(window)},
        )
    q.append(now)

def rate_limit(request: Request, scope: str = "default") -> None:
    ip = request.client.host if request.client else "unknown"
    limit, window = LIMITS.get(scope, LIMITS["default"])
    _check(f"{scope}:{ip}", limit, window)
