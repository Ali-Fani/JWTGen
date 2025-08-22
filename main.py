from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import jwt
from datetime import datetime, timedelta, timezone
import uvicorn

app = FastAPI(title="JWT Generator API", version="1.0.0")

# Pydantic models for request/response validation
class JWTRequest(BaseModel):
    key: str
    body: Dict[str, Any] = {}
    options: Optional[Dict[str, Any]] = {}

class JWTResponse(BaseModel):
    token: str

@app.post("/generate_jwt", response_model=JWTResponse)
async def generate_jwt(request: JWTRequest):
    try:
        # Extract parameters
        secret_key = request.key
        jwt_payload = request.body.copy()
        options = request.options or {}
        
        # Set default expiration if not provided
        if "exp" not in jwt_payload and options.get("add_exp", True):
            jwt_payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Set default issued at time
        if "iat" not in jwt_payload:
            jwt_payload["iat"] = datetime.now(timezone.utc)
        
        # Generate the JWT
        algorithm = options.get("algorithm", "HS256")
        token = jwt.encode(jwt_payload, secret_key, algorithm=algorithm)
        
        return JWTResponse(token=token)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)