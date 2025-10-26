"""
EduVerse API - Main FastAPI Application
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.core.config import settings
from app.core.database import create_tables, get_db
from app.core.logging import setup_logging, get_logger
from app.api.v1.api import api_router

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting EduVerse API...")

    try:
        # Create database tables
        await create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database setup error: {e}")
        raise

    yield

    logger.info("🔄 Shutting down EduVerse API...")

# Create FastAPI app
app = FastAPI(
    title="EduVerse API",
    description="Advanced E-Learning Platform with VR/AR and AI capabilities",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for production
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include API routers
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Beautiful landing page for the API"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduVerse API - The Future of Learning</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            .logo {
                font-size: 3rem;
                font-weight: bold;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 20px;
            }
            .subtitle {
                color: #666;
                font-size: 1.2rem;
                margin-bottom: 30px;
                line-height: 1.6;
            }
            .cta-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 30px;
                flex-wrap: wrap;
            }
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                font-size: 1rem;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.3s ease;
                display: inline-block;
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-secondary {
                background: transparent;
                color: #667eea;
                border: 2px solid #667eea;
            }
            .btn-secondary:hover {
                background: #667eea;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎓 EduVerse</div>
            <p class="subtitle">
                The future of social e-learning with VR/AR capabilities and AI-powered personalization.
                Experience education like never before.
            </p>
            <div class="cta-buttons">
                <a href="/docs" class="btn btn-primary">📖 View API Docs</a>
                <a href="/api/v1/health" class="btn btn-secondary">ℹ️ API Health</a>
            </div>
        </div>
    </body>
    </html>
    """

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "EduVerse API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
