"""
Authentication endpoints for EduVerse platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import jwt
from datetime import datetime, timedelta
import bcrypt
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    UserLogin, UserRegister, TokenResponse, UserResponse,
    PasswordReset, PasswordResetConfirm, SocialLogin
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    auth_service = AuthService(db)
    
    try:
        # Check if user already exists
        existing_user = await auth_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user = await auth_service.create_user(user_data)
        
        # Send welcome email
        email_service = EmailService()
        await email_service.send_welcome_email(user)
        
        return UserResponse.from_orm(user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """User login with email and password"""
    auth_service = AuthService(db)
    
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            user_credentials.email,
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate tokens
        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token(user.id)
        
        # Set refresh token as httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        # Update last login
        await auth_service.update_last_login(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    auth_service = AuthService(db)
    
    # Get refresh token from cookie or header
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ")[1]
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    
    try:
        # Validate refresh token and get user
        user = await auth_service.validate_refresh_token(refresh_token)
        
        # Generate new access token
        access_token = auth_service.create_access_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """User logout"""
    auth_service = AuthService(db)
    
    try:
        # Invalidate refresh token
        await auth_service.invalidate_user_tokens(current_user.id)
        
        # Clear refresh token cookie
        response.delete_cookie("refresh_token")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Logout failed: {str(e)}"
        )

@router.post("/social-login", response_model=TokenResponse)
async def social_login(
    social_data: SocialLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Social login with Google, Apple, Facebook"""
    auth_service = AuthService(db)
    
    try:
        # Verify social token
        user_info = await auth_service.verify_social_token(
            social_data.provider,
            social_data.token
        )
        
        # Get or create user
        user = await auth_service.get_or_create_social_user(
            user_info,
            social_data.provider
        )
        
        # Generate tokens
        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token(user.id)
        
        # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Social login failed: {str(e)}"
        )

@router.post("/forgot-password")
async def forgot_password(
    password_reset: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email"""
    auth_service = AuthService(db)
    email_service = EmailService()
    
    try:
        # Check if user exists
        user = await auth_service.get_user_by_email(password_reset.email)
        if not user:
            # Don't reveal if email exists for security
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token
        reset_token = auth_service.create_password_reset_token(user.id)
        
        # Send reset email
        await email_service.send_password_reset_email(user, reset_token)
        
        return {"message": "Password reset email sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset failed: {str(e)}"
        )

@router.post("/reset-password")
async def reset_password(
    password_reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token"""
    auth_service = AuthService(db)
    
    try:
        # Validate reset token
        user_id = auth_service.validate_password_reset_token(
            password_reset_confirm.token
        )
        
        # Update password
        await auth_service.update_password(
            user_id,
            password_reset_confirm.new_password
        )
        
        # Invalidate all user tokens
        await auth_service.invalidate_user_tokens(user_id)
        
        return {"message": "Password reset successful"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email address"""
    auth_service = AuthService(db)
    
    try:
        # Validate verification token
        user_id = auth_service.validate_email_verification_token(token)
        
        # Mark email as verified
        await auth_service.verify_user_email(user_id)
        
        return {"message": "Email verified successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email verification failed: {str(e)}"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    auth_service = AuthService(db)
    
    try:
        # Validate access token
        user = await auth_service.validate_access_token(credentials.credentials)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive user"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

# Optional dependency for endpoints that work with or without authentication
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Optional dependency to get current authenticated user"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None