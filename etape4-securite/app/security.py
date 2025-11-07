"""
Security Middleware and Rate Limiting
"""
import time
import redis
import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from secure import Secure

from .config import REDIS_URL, RATE_LIMIT_PER_MINUTE, RATE_LIMIT_BURST

logger = logging.getLogger(__name__)

# Redis connection for rate limiting
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
    logger.info("✅ Redis connecté pour rate limiting")
except Exception as e:
    logger.warning(f"⚠️ Redis non disponible, utilisation mémoire: {e}")
    redis_client = None
    REDIS_AVAILABLE = False

# In-memory rate limiting fallback
memory_rate_limit = {}

def get_identifier(request: Request) -> str:
    """Get unique identifier for rate limiting"""
    # Try to get user from auth, otherwise use IP
    try:
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.username}"
    except:
        pass
    
    # Fallback to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

# Rate limiter configuration
limiter = Limiter(
    key_func=get_identifier,
    storage_uri=REDIS_URL if REDIS_AVAILABLE else "memory://",
    default_limits=[f"{RATE_LIMIT_PER_MINUTE}/minute"]
)

def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    logger.warning(f"Rate limit exceeded for {get_identifier(request)}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Limite de requêtes dépassée",
            "detail": f"Limite: {exc.detail}",
            "retry_after": getattr(exc, 'retry_after', 60),
            "timestamp": datetime.now().isoformat()
        },
        headers={"Retry-After": str(getattr(exc, 'retry_after', 60))}
    )

class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, app):
        self.app = app
        self.secure = Secure(
            # Content Security Policy
            csp="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;",
            # HTTP Strict Transport Security
            hsts="max-age=31536000; includeSubDomains",
            # X-Frame-Options
            frame="DENY",
            # X-Content-Type-Options
            content="nosniff",
            # Referrer Policy
            referrer="strict-origin-when-cross-origin",
            # Permissions Policy
            permissions="geolocation=(), microphone=(), camera=()"
        )
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    
                    # Add security headers
                    security_headers = self.secure.headers()
                    for name, value in security_headers.items():
                        headers[name.encode()] = value.encode()
                    
                    # Add custom headers
                    headers[b"X-API-Version"] = b"1.0.0"
                    headers[b"X-Powered-By"] = b"Digital-Social-Score"
                    
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

class RequestLoggingMiddleware:
    """Log requests for monitoring and RGPD compliance"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            request = Request(scope, receive)
            
            # Log request start
            identifier = get_identifier(request)
            logger.info(
                f"📝 Request: {request.method} {request.url.path} "
                f"from {identifier[:16]}*** "  # Partial IP for RGPD
                f"UA: {request.headers.get('user-agent', 'Unknown')[:50]}"
            )
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    status_code = message["status"]
                    
                    # Log response
                    logger.info(
                        f"📤 Response: {status_code} "
                        f"Time: {process_time:.3f}s "
                        f"Path: {request.url.path}"
                    )
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

class HTTPSRedirectMiddleware:
    """Force HTTPS redirect if enabled"""
    
    def __init__(self, app, force_https: bool = False):
        self.app = app
        self.force_https = force_https
    
    async def __call__(self, scope, receive, send):
        if self.force_https and scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            scheme = headers.get(b"x-forwarded-proto", b"http").decode()
            
            if scheme != "https":
                url = f"https://{headers.get(b'host', b'localhost').decode()}{scope['path']}"
                if scope.get("query_string"):
                    url += f"?{scope['query_string'].decode()}"
                
                response = JSONResponse(
                    status_code=301,
                    content={"message": "Redirecting to HTTPS"},
                    headers={"Location": url}
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)

def is_rate_limited(identifier: str, limit_per_minute: int = RATE_LIMIT_PER_MINUTE) -> bool:
    """Check if identifier is rate limited (fallback implementation)"""
    if REDIS_AVAILABLE:
        return False  # SlowAPI handles this
    
    now = time.time()
    minute_window = int(now // 60)
    
    if identifier not in memory_rate_limit:
        memory_rate_limit[identifier] = {}
    
    user_limits = memory_rate_limit[identifier]
    
    # Clean old windows
    old_windows = [w for w in user_limits.keys() if w < minute_window - 5]
    for w in old_windows:
        del user_limits[w]
    
    # Check current window
    current_count = user_limits.get(minute_window, 0)
    if current_count >= limit_per_minute:
        return True
    
    # Update count
    user_limits[minute_window] = current_count + 1
    return False

async def check_request_security(request: Request):
    """Additional security checks"""
    # Check for common attack patterns
    user_agent = request.headers.get("user-agent", "").lower()
    suspicious_patterns = ["sqlmap", "nmap", "burp", "nikto", "curl"]
    
    if any(pattern in user_agent for pattern in suspicious_patterns):
        logger.warning(f"🚨 Suspicious User-Agent: {user_agent}")
        # Could block or flag for monitoring
    
    # Check for oversized requests
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
        raise HTTPException(
            status_code=413,
            detail="Request trop volumineux"
        )
    
    return True
