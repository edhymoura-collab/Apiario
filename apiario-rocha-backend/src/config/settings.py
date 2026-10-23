from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sistema de Gestão"
    company_name: str = "Empresa"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:8081",
            "http://localhost:8081",
            "http://127.0.0.1:8083",
            "http://localhost:8083",
            "http://127.0.0.1:8085",
            "http://localhost:8085",
            "http://127.0.0.1:8087",
            "http://localhost:8087",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ]
    )
    sqlite_path: Path = Path("../data/apiario.db")
    secret_key: str | None = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_username: str | None = None
    admin_password: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
