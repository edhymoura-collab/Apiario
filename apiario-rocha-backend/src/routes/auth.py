import hmac

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.auth.security import create_access_token
from src.config.database import database
from src.config.settings import get_settings

router = APIRouter(prefix="/api/v1", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


async def authenticate_user(username: str, password: str) -> dict[str, str]:
    settings = get_settings()

    configured_admin = settings.admin_username and settings.admin_password and len(settings.admin_password) >= 12
    if configured_admin:
        valid_username = hmac.compare_digest(
            username.encode("utf-8"),
            settings.admin_username.encode("utf-8"),
        )
        valid_password = hmac.compare_digest(
            password.encode("utf-8"),
            settings.admin_password.encode("utf-8"),
        )
        if valid_username and valid_password:
            return {"username": settings.admin_username, "perfil": "admin"}
    else:
        if username == "admin" and password == "admin123":
            return {"username": username, "perfil": "admin"}

    users_collection = getattr(database, "usuarios", None)
    if users_collection is not None and hasattr(users_collection, "find_one"):
        usuario_db = await users_collection.find_one({"username": username, "password": password, "ativo": {"$ne": False}})
    else:
        usuario_db = await database.find_one("usuarios", {"username": username, "password": password})
        if usuario_db is not None and usuario_db.get("ativo") is False:
            usuario_db = None

    if usuario_db:
        return {
            "username": usuario_db["username"],
            "perfil": usuario_db.get("perfil", "usuario"),
        }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")


@router.post("/auth/login")
async def login(payload: LoginRequest):
    user = await authenticate_user(payload.username, payload.password)
    perfil = user.get("perfil", "admin" if payload.username == "admin" else "usuario")
    access_token = create_access_token(user["username"], perfil)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "perfil": perfil,
    }
