from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import uvicorn
import json
import hashlib
from functools import lru_cache
import os

# Import PyJWT explicitly
try:
    import jwt
    # Test if it has encode method
    if not hasattr(jwt, 'encode'):
        raise ImportError("Wrong jwt package installed")
except ImportError:
    raise ImportError("Please install PyJWT: pip uninstall jwt && pip install PyJWT")

# Try to import Redis for optional caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

app = FastAPI(title="JWT Generator API", version="1.0.0")

# Initialize cache
cache = {}
redis_client = None

# Setup Redis if available and configured
if REDIS_AVAILABLE and os.getenv("REDIS_URL"):
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
        redis_client.ping()  # Test connection
        print("✅ Redis cache enabled")
    except:
        print("❌ Redis connection failed, using in-memory cache")
        redis_client = None
else:
    print("📝 Using in-memory cache")

def generate_cache_key(secret_key: str, payload: Dict[str, Any], algorithm: str) -> str:
    """Generate a cache key from request parameters (excluding timestamp fields)"""
    # Remove timestamp fields and create a clean payload for caching
    cache_payload = {k: v for k, v in payload.items() if k not in ['iat', 'exp']}
    cache_data = {
        'key_hash': hashlib.sha256(secret_key.encode()).hexdigest()[:16],  # Hash secret for security
        'payload': cache_payload,
        'algorithm': algorithm
    }
    cache_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_string.encode()).hexdigest()

def should_cache_request(payload: Dict[str, Any], add_exp: bool) -> bool:
    """Determine if a request should be cached based on whether it has dynamic timestamps"""
    # Don't cache if we're adding timestamps (iat/exp) as they make each request unique
    return not add_exp and 'iat' not in payload and 'exp' not in payload

def get_from_cache(cache_key: str) -> Optional[str]:
    """Get token from cache"""
    if redis_client:
        try:
            return redis_client.get(f"jwt:{cache_key}")
        except:
            pass
    return cache.get(cache_key)

def set_cache(cache_key: str, token: str, ttl: int = 3600):
    """Set token in cache with TTL"""
    if redis_client:
        try:
            redis_client.setex(f"jwt:{cache_key}", ttl, token)
            return
        except:
            pass
    # In-memory cache with simple cleanup
    cache[cache_key] = token
    # Keep cache size reasonable
    if len(cache) > 1000:
        # Remove oldest 100 items
        for _ in range(100):
            cache.pop(next(iter(cache)), None)

# Pydantic models for request/response validation
class JWTRequest(BaseModel):
    key: str
    body: Dict[str, Any] = {}
    options: Optional[Dict[str, Any]] = {}

class JWTResponse(BaseModel):
    token: str
    cached: Optional[bool] = False

@app.post("/generate_jwt", response_model=JWTResponse)
async def generate_jwt_post(request: JWTRequest):
    """Generate JWT using JSON body (original method)"""
    options = request.options or {}
    return await _generate_jwt_logic(request.key, request.body, options)

@app.get("/generate_jwt", response_model=JWTResponse)
async def generate_jwt_get(
    key: str = Query(..., description="Secret key for JWT signing"),
    body: Optional[str] = Query("{}", description="JWT payload as JSON string"),
    algorithm: Optional[str] = Query("HS256", description="JWT algorithm"),
    add_exp: Optional[bool] = Query(True, description="Add expiration time (1 hour)")
):
    """Generate JWT using URL query parameters"""
    try:
        # Parse the body JSON string
        jwt_payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON in 'body' parameter"
        )
    
    options = {
        "algorithm": algorithm,
        "add_exp": add_exp
    }
    
    return await _generate_jwt_logic(key, jwt_payload, options)

async def _generate_jwt_logic(secret_key: str, jwt_payload: Dict[str, Any], options: Dict[str, Any]) -> JWTResponse:
    """Common logic for JWT generation with intelligent caching"""
    try:
        algorithm = options.get("algorithm", "HS256")
        add_exp = options.get("add_exp", False)
        
        # Make a copy to avoid modifying the original
        payload = jwt_payload.copy() if jwt_payload else {}
        
        # Check if this request can be cached (no dynamic timestamps)
        can_cache = should_cache_request(payload, add_exp)
        
        # Check cache first if request is cacheable
        if can_cache:
            cache_key = generate_cache_key(secret_key, payload, algorithm)
            cached_token = get_from_cache(cache_key)
            if cached_token:
                return JWTResponse(token=cached_token, cached=True)
        
        # Add timestamps if needed (these make tokens unique)
        if add_exp and "exp" not in payload:
            payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)
        
        if "iat" not in payload:
            payload["iat"] = datetime.now(timezone.utc)
        
        # Generate the JWT
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        
        # Cache the token only if it doesn't have dynamic content
        if can_cache:
            cache_key = generate_cache_key(secret_key, jwt_payload, algorithm)  # Use original payload for key
            set_cache(cache_key, token, ttl=3600)  # Cache for 1 hour
        
        return JWTResponse(token=token, cached=False)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)