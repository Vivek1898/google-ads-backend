import os
from typing import Optional
from fastapi import HTTPException, Request
import jwt
from jwt.exceptions import PyJWTError
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET")  # Replace with your actual secret key
ALGORITHM = "HS256"

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        return None


async def auth_middleware(request: Request, call_next):
    token = request.headers.get("Authorization")
    print(request)
    if token:
        token = token.split("Bearer ")[1] if token.startswith("Bearer ") else token
        payload = decode_token(token)
        if payload:
            request.state.user = payload
            response = await call_next(request)
            return response
    raise HTTPException(status_code=401, detail="Invalid or missing token")
