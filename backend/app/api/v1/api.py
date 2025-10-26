"""
EduVerse API Router - Main API router that includes all endpoint modules
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
import time

# Import endpoint modules
from .endpoints import (
    auth, courses, analytics, collaboration,
    certificates, adaptive_learning, payments,
    categories, translations, websocket, app_updates
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}}
)

api_router.include_router(
    courses.router,
    prefix="/courses",
    tags=["Courses"],
    responses={404: {"description": "Course not found"}}
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
    responses={403: {"description": "Forbidden"}}
)

api_router.include_router(
    collaboration.router,
    prefix="/collaboration",
    tags=["Collaboration"],
    responses={404: {"description": "Room not found"}}
)

api_router.include_router(
    certificates.router,
    prefix="/certificates",
    tags=["Certificates"],
    responses={404: {"description": "Certificate not found"}}
)

api_router.include_router(
    adaptive_learning.router,
    prefix="/adaptive-learning",
    tags=["Adaptive Learning"],
    responses={403: {"description": "Forbidden"}}
)

api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["Payments"],
    responses={402: {"description": "Payment required"}}
)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"],
    responses={404: {"description": "Category not found"}}
)

api_router.include_router(
    translations.router,
    prefix="/translations",
    tags=["Translations"],
    responses={404: {"description": "Translation not found"}}
)

api_router.include_router(
    app_updates.router,
    prefix="/app",
    tags=["App Updates"],
    responses={404: {"description": "Update not found"}}
)

# Security scheme
security = HTTPBearer()

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user
    Validates JWT tokens and retrieves user from database
    """
    token = credentials.credentials

    try:
        # Import JWT utilities
        import jwt
        from datetime import datetime, timedelta
        from app.core.config import settings

        # Decode and validate JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check if token is expired
        exp = payload.get('exp')
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == payload['user_id']).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is deactivated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return user
        finally:
            db.close()

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Global exception handlers
# Note: These are handled by the main FastAPI app

# Health check endpoints
@api_router.get("/health")
async def api_health_check():
    """API health check"""
    return {
        "status": "healthy",
        "service": "EduVerse API v1",
        "endpoints": {
            "auth": "/auth",
            "courses": "/courses",
            "analytics": "/analytics",
            "collaboration": "/collaboration",
            "certificates": "/certificates",
            "adaptive_learning": "/adaptive-learning",
            "payments": "/payments"
        }
    }

# API information endpoint
@api_router.get("/info")
async def api_information():
    """Get comprehensive API information"""
    return {
        "name": "EduVerse API",
        "version": "2.0.0",
        "description": "Advanced E-Learning Platform with VR/AR and AI capabilities",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "features": {
            "authentication": {
                "social_login": ["google", "apple", "facebook"],
                "two_factor": "ready",
                "biometric": "ready",
                "jwt_tokens": "enabled"
            },
            "real_time": {
                "websockets": "enabled",
                "collaboration": "enabled",
                "live_classes": "ready"
            },
            "ai_powered": {
                "recommendations": "enabled",
                "tutoring": "enabled",
                "analytics": "enabled"
            },
            "content": {
                "vr_ar": "ready",
                "interactive": "enabled",
                "multilingual": "ready"
            }
        },
        "limits": {
            "free_tier": {
                "requests_per_hour": 100,
                "storage_gb": 1,
                "features": ["basic_courses", "community_access"]
            },
            "premium_tier": {
                "requests_per_hour": 1000,
                "storage_gb": 10,
                "features": ["all_courses", "vr_ar_content", "priority_support"]
            },
            "enterprise_tier": {
                "requests_per_hour": "unlimited",
                "storage_gb": "unlimited",
                "features": ["custom_branding", "advanced_analytics", "api_access"]
            }
        }
    }

# Metrics endpoint (for monitoring)
@api_router.get("/metrics")
async def get_metrics():
    """Get API metrics and statistics"""
    return {
        "total_requests": 0,  # Implement actual metrics
        "active_users": 0,    # Implement actual metrics
        "total_courses": 0,   # Implement actual metrics
        "uptime": "99.9%",    # Implement actual metrics
        "response_time_avg": "150ms"  # Implement actual metrics
    }

# Export the router
__all__ = ["api_router"]
