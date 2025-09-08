"""
EduVerse - Advanced E-Learning Platform
Main FastAPI application with comprehensive features
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status, OAuth2PasswordBearer, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
from typing import List, Optional
from app.core.config import settings
from datetime import datetime, timedelta
import os
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import create_tables, get_db
from app.core.security import get_current_user
from app.core.logging import get_logger, log_request_middleware
from app.middleware.i18n_middleware import I18nMiddleware
from app.models.user import User
from app.api.v1.endpoints import auth, translations

# Configure advanced logging
logger = get_logger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting EduVerse platform...")

    # Create database tables
    await create_tables()

    logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Shutting down EduVerse platform...")

# Create FastAPI app
app = FastAPI(
    title="EduVerse API",
    description="Advanced E-Learning Platform with VR/AR and AI capabilities",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
    openapi_url="/api/v1/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (configure for production)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# I18n middleware for multilanguage support
app.add_middleware(I18nMiddleware, default_language=settings.DEFAULT_LANGUAGE)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(translations.router, prefix="/api/v1/translations", tags=["Translations"])
# TODO: Add other routers as they are refactored
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(courses.router, prefix="/api/v1/courses", tags=["Courses"])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Query user from database
    from sqlmodel import select
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Welcome to EduVerse - The Future of Learning",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "EduVerse API"
    }

# WebSocket endpoints (commented out until services are refactored)
# @app.websocket("/ws/classroom/{room_id}")
# async def websocket_classroom(
#     websocket: WebSocket,
#     room_id: str,
#     current_user: User = Depends(get_current_user_from_token)
# ):
#     """WebSocket endpoint for real-time classroom interactions"""
#     # TODO: Implement WebSocket manager with SQLModel
#     pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
