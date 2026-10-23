import hmac

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.auth.security import create_access_token
from src.config.settings import get_settings

router = APIRouter(prefix="/api/v1", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


async def authenticate_user(username: str, password: str) -> dict[str, str]:
    settings = get_settings()
    if (
        not settings.admin_username
        or not settings.admin_password
        or len(settings.admin_password) < 12
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrador não configurado. Defina ADMIN_USERNAME e ADMIN_PASSWORD no arquivo .env.",
        )

    valid_username = hmac.compare_digest(
        username.encode("utf-8"),
        settings.admin_username.encode("utf-8"),
    )
    valid_password = hmac.compare_digest(
        password.encode("utf-8"),
        settings.admin_password.encode("utf-8"),
    )
    if valid_username and valid_password:
        return {"username": settings.admin_username}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")


@router.post("/auth/login")
async def login(payload: LoginRequest):
    user = await authenticate_user(payload.username, payload.password)
    access_token = create_access_token(user["username"])
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
