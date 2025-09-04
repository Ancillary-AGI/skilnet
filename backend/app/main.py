"""
EduVerse - Advanced E-Learning Platform
Main FastAPI application with comprehensive features
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
from typing import List

from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import get_current_user
from app.api.v1 import auth, courses, users, ai_teaching, vr_classroom, analytics
from app.services.websocket_manager import WebSocketManager
from app.services.ai_video_generator import AIVideoGenerator
from app.models.user import User

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

# Security middleware
security = HTTPBearer()

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