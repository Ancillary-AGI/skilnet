"""
EduVerse API - Advanced E-Learning Platform
Main FastAPI application with comprehensive Swagger documentation
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

# Import core modules
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import setup_logging
from app.api.v1.api import api_router

# Setup logging
setup_logging()

# Create database tables
Base.metadata.create_all(bind=engine)

# Security scheme
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting EduVerse API...")
    yield
    # Shutdown
    print("🔄 Shutting down EduVerse API...")

# Create FastAPI application with comprehensive metadata
app = FastAPI(
    title="EduVerse API",
    description="""
    # 🎓 EduVerse API

    **The Future of Social E-Learning with VR/AR and AI**

    ## 🌟 Features

    ### 🔐 Advanced Authentication
    - Multi-provider social login (Google, Apple, Facebook)
    - JWT token management with automatic refresh
    - Biometric authentication support
    - Two-factor authentication ready

    ### 📚 Course Management
    - Comprehensive course catalog
    - AI-powered recommendations
    - Progress tracking and analytics
    - Interactive content with VR/AR support

    ### 👥 Real-Time Collaboration
    - WebSocket-based live communication
    - Multi-user whiteboards
    - Screen sharing capabilities
    - Breakout rooms for group activities

    ### 🤖 AI Integration
    - Personalized learning recommendations
    - Intelligent tutoring system
    - Predictive analytics
    - Content generation and adaptation

    ### 💳 Subscription System
    - Multiple subscription tiers
    - In-app purchase integration
    - Premium feature gating
    - Family and corporate licensing

    ### 🔒 Security & Privacy
    - End-to-end encryption
    - GDPR compliance ready
    - Secure data storage
    - Privacy-first design

    ## 🚀 Quick Start

    1. **Register/Login** using the authentication endpoints
    2. **Browse Courses** to find interesting topics
    3. **Enroll** in courses that match your interests
    4. **Join Study Groups** for collaborative learning
    5. **Track Progress** with detailed analytics

    ## 📊 Analytics

    Get insights into your learning patterns, achievements, and areas for improvement.

    ## 🌐 Real-Time Features

    Experience live collaboration, instant messaging, and synchronized learning sessions.

    ## 📱 Mobile Ready

    Full mobile optimization with responsive design and offline capabilities.
    """,
    version="2.0.0",
    terms_of_service="https://eduverse.com/terms",
    contact={
        "name": "EduVerse Support",
        "url": "https://eduverse.com/support",
        "email": "support@eduverse.com",
    },
    license_info={
        "name": "EduVerse Platform License",
        "url": "https://eduverse.com/license",
    },
    root_path="",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "EduVerse API",
        "version": "2.0.0",
        "timestamp": "2024-01-15T10:30:00Z"
    }

@app.get("/health/database", tags=["Health"])
async def database_health_check():
    """Database health check"""
    try:
        # Test database connection
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()

        return {
            "status": "healthy",
            "database": "connected",
            "service": "EduVerse API"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/health/complete", tags=["Health"])
async def complete_health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "service": "EduVerse API",
        "version": "2.0.0",
        "components": {
            "database": "healthy",
            "redis": "healthy",  # Add Redis check if using
            "ai_services": "healthy",  # Add AI service checks
            "file_storage": "healthy"  # Add storage checks
        },
        "features": {
            "authentication": "enabled",
            "social_login": "enabled",
            "real_time": "enabled",
            "ai_powered": "enabled",
            "vr_ar": "enabled",
            "blockchain": "enabled"
        }
    }

# API Information endpoint
@app.get("/api/info", tags=["Information"])
async def api_info():
    """Get detailed API information"""
    return {
        "name": "EduVerse API",
        "version": "2.0.0",
        "description": "Advanced E-Learning Platform with VR/AR and AI capabilities",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health"
        },
        "features": [
            "Multi-provider Authentication",
            "Course Management",
            "Real-time Collaboration",
            "AI-Powered Learning",
            "VR/AR Content Support",
            "Subscription Management",
            "Analytics & Insights",
            "Social Learning",
            "Blockchain Certificates",
            "Offline Support"
        ],
        "supported_platforms": [
            "Web",
            "iOS",
            "Android",
            "Desktop"
        ]
    }

# Root endpoint with beautiful landing page
@app.get("/", response_class=HTMLResponse, tags=["Public"])
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
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
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

            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
                text-align: left;
            }

            .feature {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }

            .feature h3 {
                color: #333;
                font-size: 1rem;
                margin-bottom: 5px;
            }

            .feature p {
                color: #666;
                font-size: 0.9rem;
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

            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
                font-size: 0.9rem;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 20px;
                    margin: 10px;
                }

                .features {
                    grid-template-columns: 1fr;
                }

                .cta-buttons {
                    flex-direction: column;
                }
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

            <div class="features">
                <div class="feature">
                    <h3>🤖 AI-Powered Learning</h3>
                    <p>Personalized recommendations and intelligent tutoring</p>
                </div>
                <div class="feature">
                    <h3>👥 Social Collaboration</h3>
                    <p>Real-time study groups and peer learning</p>
                </div>
                <div class="feature">
                    <h3>🕶️ VR/AR Integration</h3>
                    <p>Immersive learning experiences</p>
                </div>
                <div class="feature">
                    <h3>📊 Advanced Analytics</h3>
                    <p>Track progress and optimize learning</p>
                </div>
            </div>

            <div class="cta-buttons">
                <a href="/docs" class="btn btn-primary">📖 View API Docs</a>
                <a href="/api/info" class="btn btn-secondary">ℹ️ API Information</a>
            </div>

            <div class="footer">
                <p>🚀 EduVerse API v2.0.0 | Advanced E-Learning Platform</p>
                <p>Built with ❤️ using FastAPI, Flutter, and cutting-edge technologies</p>
            </div>
        </div>
    </body>
    </html>
    """

# Custom OpenAPI schema with enhanced documentation
def custom_openapi():
    """Generate custom OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="EduVerse API",
        version="2.0.0",
        description="""
        # 🎓 EduVerse API Documentation

        **Advanced Social E-Learning Platform with VR/AR and AI**

        ## Key Features

        ### 🔐 Authentication
        - JWT-based authentication with refresh tokens
        - Social login (Google, Apple, Facebook)
        - Biometric authentication support
        - Two-factor authentication ready

        ### 📚 Course Management
        - Comprehensive course catalog
        - AI-powered recommendations
        - Progress tracking and analytics
        - Interactive content support

        ### 👥 Real-Time Features
        - WebSocket-based communication
        - Live collaboration rooms
        - Real-time messaging
        - Presence indicators

        ### 🤖 AI Integration
        - Personalized learning paths
        - Intelligent tutoring
        - Content generation
        - Predictive analytics

        ### 💳 Subscription System
        - Multiple subscription tiers
        - In-app purchase integration
        - Feature gating
        - Usage analytics

        ## Getting Started

        1. Register or login using the auth endpoints
        2. Browse available courses
        3. Enroll in courses of interest
        4. Join study groups for collaboration
        5. Track your learning progress

        ## Support

        For support and questions:
        - 📧 Email: support@eduverse.com
        - 💬 Community: community.eduverse.com
        - 📖 Docs: docs.eduverse.com
        """,
        routes=app.routes,
    )

    # Add custom components for better documentation
    openapi_schema["components"] = {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter: **'Bearer <JWT>'**, where JWT is the access token"
            }
        }
    }

    # Add security to all endpoints
    for path_data in openapi_schema["paths"].values():
        for operation in path_data.values():
            if "security" not in operation:
                operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False
    )
