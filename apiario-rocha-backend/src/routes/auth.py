from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.auth.security import create_access_token

router = APIRouter(prefix="/api/v1", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


async def authenticate_user(username: str, password: str) -> dict[str, str]:
    if username == "admin" and password == "admin123":
        return {"username": username}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")


@router.post("/auth/login")
async def login(payload: LoginRequest):
    user = await authenticate_user(payload.username, payload.password)
    access_token = create_access_token(user["username"])
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
