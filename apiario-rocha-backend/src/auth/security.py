from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.config.settings import get_settings

security = HTTPBearer(auto_error=False)


def create_access_token(subject: str, perfil: str = "usuario") -> str:
    settings = get_settings()
    if not settings.secret_key or len(settings.secret_key) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chave JWT não configurada. Defina SECRET_KEY no arquivo .env.",
        )
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "perfil": perfil, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def _decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("sub") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from exc


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> str:
    settings = get_settings()
    if not settings.secret_key or len(settings.secret_key) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chave JWT não configurada. Defina SECRET_KEY no arquivo .env.",
        )
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _decode_token(credentials.credentials).get("sub")


def get_current_user_profile(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _decode_token(credentials.credentials).get("perfil", "usuario")
