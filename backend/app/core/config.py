"""
Configuration settings for EduVerse platform - FastAPI Best Practices
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings"""

    # Application
    app_name: str = "EduVerse"
    debug: bool = True
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"

    # Database - SQLite for development (FastAPI best practice)
    database_url: str = "sqlite+aiosqlite:///./eduverse.db"

    # Security
    secret_key: str = "change-this-in-production-make-it-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB

    # Email (optional)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None

    # AI Services (optional)
    openai_api_key: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
