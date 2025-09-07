"""
EduVerse - Advanced E-Learning Platform
Main FastAPI application with comprehensive features
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
from typing import List, Optional
from datetime import datetime, timedelta
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import get_current_user
from app.api.v1 import auth, courses, users, ai_teaching, vr_classroom, analytics
from app.services.websocket_manager import WebSocketManager
from app.services.ai_video_generator import AIVideoGenerator
from backend.app.models.profile import User
import jwt

from backend.app.core.database import DatabaseConfig, DatabaseConnection, BaseModel
from backend.app.models.profile import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket manager for real-time features
websocket_manager = WebSocketManager()

# AI Video Generator
ai_video_generator = AIVideoGenerator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting EduVerse platform...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize AI models
    await ai_video_generator.initialize_models()
    
    yield
    
    # Shutdown
    logger.info("Shutting down EduVerse platform...")
    await ai_video_generator.cleanup()


# Create FastAPI app
app = FastAPI(
    title="EduVerse API",
    description="Advanced E-Learning Platform with VR/AR and AI capabilities",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Security configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security middleware
security = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["Courses"])
app.include_router(ai_teaching.router, prefix="/api/v1/ai", tags=["AI Teaching"])
app.include_router(vr_classroom.router, prefix="/api/v1/vr", tags=["VR Classroom"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        users = await BaseUser.filter(username=username)
        if not users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return users[0]
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

# Database initialization
@app.on_event("startup")
async def startup():
    # Use SQLite for testing, PostgreSQL for production
    database_url = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    config = DatabaseConfig(database_url)
    
    # Set config for all models
    BaseModel.set_db_config(config)
    
    # Initialize database connection
    db = DatabaseConnection.get_instance(config)
    await db.connect()
    
    # Create tables
    ...

@app.on_event("shutdown")
async def shutdown():
    db = DatabaseConnection.get_instance()
    await db.disconnect()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Welcome to EduVerse - The Future of Learning",
        "version": "1.0.0",
        "status": "operational"
    }


@app.websocket("/ws/classroom/{room_id}")
async def websocket_classroom(
    websocket: WebSocket,
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """WebSocket endpoint for real-time classroom interactions"""
    await websocket_manager.connect(websocket, room_id, current_user.id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.broadcast_to_room(room_id, data, current_user.id)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, room_id, current_user.id)


@app.websocket("/ws/ai-class/{class_id}")
async def websocket_ai_class(
    websocket: WebSocket,
    class_id: str,
    current_user: User = Depends(get_current_user)
):
    """WebSocket endpoint for AI-powered live classes"""
    await websocket_manager.connect(websocket, f"ai_class_{class_id}", current_user.id)
    try:
        # Start AI video generation for live class
        await ai_video_generator.start_live_session(class_id, websocket)
        
        while True:
            data = await websocket.receive_text()
            # Process student input and generate AI response
            await ai_video_generator.process_student_input(class_id, data, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, f"ai_class_{class_id}", current_user.id)
        await ai_video_generator.end_live_session(class_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )