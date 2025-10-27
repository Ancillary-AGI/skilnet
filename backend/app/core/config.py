"""
Configuration settings for EduVerse platform
"""

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "EduVerse"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/eduverse")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60 * 24 * 7  # 7 days
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # AI Models
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    STABILITY_AI_API_KEY: Optional[str] = None
    
    # Video Generation
    VIDEO_MODEL_PATH: str = "./models/video_generation"
    MAX_VIDEO_LENGTH: int = 300  # seconds
    VIDEO_RESOLUTION: str = "1920x1080"
    
    # VR/AR Settings
    VR_STREAMING_QUALITY: str = "high"
    AR_TRACKING_PRECISION: str = "high"
    XR_FRAME_RATE: int = 90
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".mp4", ".webm", ".pdf", ".docx", ".pptx", 
        ".jpg", ".jpeg", ".png", ".gif", ".svg",
        ".glb", ".gltf", ".fbx", ".obj"  # 3D models for VR/AR
    ]
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    APP_URL: str = os.getenv("APP_URL", "http://localhost:8000")
    
    # OAuth Providers
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    APPLE_CLIENT_ID: Optional[str] = None
    APPLE_CLIENT_SECRET: Optional[str] = None
    
    # WebRTC for VR streaming
    WEBRTC_STUN_SERVERS: List[str] = [
        "stun:stun.l.google.com:19302",
        "stun:stun1.l.google.com:19302"
    ]
    
    # Analytics
    ANALYTICS_ENABLED: bool = True
    MIXPANEL_TOKEN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100

    # Internationalization
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = [
        "en", "es", "fr", "de", "zh", "ja", "ko", "ar", "hi", "pt", "ru",
        "sw", "am", "yo", "ig", "ha"
    ]
    TRANSLATIONS_DIR: str = "./app/translations"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
