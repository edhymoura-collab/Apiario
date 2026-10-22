from functools import lru_cache

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
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "apiario_backend_db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
