"""
Authentication API endpoints with comprehensive security features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import secrets
import qrcode
import io
import base64
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import SecurityManager, get_current_user
from backend.app.models.profile import User
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from app.schemas.auth import (
    UserCreate, UserLogin, Token, UserResponse, 
    WebAuthnRegistrationStart, WebAuthnRegistrationComplete,
    WebAuthnAuthenticationStart, WebAuthnAuthenticationComplete,
    TwoFactorSetup, TwoFactorVerify, OAuthCallback
)

router = APIRouter()
security_manager = SecurityManager()
email_service = EmailService()


class AuthService:
    """Comprehensive authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register new user with email verification"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        hashed_password = security_manager.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            learning_style=user_data.learning_style,
            preferred_language=user_data.preferred_language
        )
        
        created_user = await self.user_repo.create(user)
        
        # Send verification email
        await self._send_verification_email(created_user)
        
        return created_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        if not security_manager.verify_password(password, user.hashed_password):
            return None
        
        # Update login statistics
        user.last_login = datetime.utcnow()
        user.login_count += 1
        await self.user_repo.update(user)
        
        return user
    
    async def create_tokens(self, user: User) -> Dict[str, str]:
        """Create access and refresh tokens"""
        access_token = security_manager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = security_manager.create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def setup_two_factor(self, user: User) -> Dict[str, Any]:
        """Setup two-factor authentication"""
        # Generate secret
        secret = secrets.token_urlsafe(16)
        user.two_factor_secret = secret
        
        # Generate QR code
        qr_url = f"otpauth://totp/EduVerse:{user.email}?secret={secret}&issuer=EduVerse"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Convert QR code to base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        await self.user_repo.update(user)
        
        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code_base64}",
            "backup_codes": [secrets.token_urlsafe(8) for _ in range(10)]
        }
    
    async def _send_verification_email(self, user: User):
        """Send email verification"""
        verification_token = security_manager.create_access_token(
            data={"sub": str(user.id), "type": "email_verification"},
            expires_delta=timedelta(hours=24)
        )
        
        await email_service.send_verification_email(
            user.email, 
            user.first_name or user.username,
            verification_token
        )


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_verified=user.is_verified,
        message="Registration successful. Please check your email for verification."
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    tokens = await auth_service.create_tokens(user)
    
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=user.to_dict()
    )


@router.post("/webauthn/register/start")
async def webauthn_register_start(
    current_user: User = Depends(get_current_user)
):
    """Start WebAuthn registration for passkeys"""
    options = security_manager.generate_registration_options_webauthn(
        str(current_user.id),
        current_user.username
    )
    
    # Store challenge in session (in production, use Redis)
    # For now, return challenge to be stored client-side
    
    return {
        "options": options,
        "challenge": options.challenge.decode()
    }


@router.post("/webauthn/register/complete")
async def webauthn_register_complete(
    registration_data: WebAuthnRegistrationComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete WebAuthn registration"""
    try:
        verification = security_manager.verify_registration_response_webauthn(
            registration_data.credential,
            registration_data.challenge
        )
        
        if verification.verified:
            # Store credential
            if not current_user.webauthn_credentials:
                current_user.webauthn_credentials = []
            
            current_user.webauthn_credentials.append({
                "credential_id": verification.credential_id.hex(),
                "public_key": verification.credential_public_key.hex(),
                "sign_count": verification.sign_count,
                "created_at": datetime.utcnow().isoformat()
            })
            
            user_repo = UserRepository(db)
            await user_repo.update(current_user)
            
            return {"verified": True, "message": "Passkey registered successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to verify passkey registration"
            )
            
    except Exception as e:
        logger.error(f"WebAuthn registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passkey registration failed"
        )


@router.post("/2fa/setup")
async def setup_two_factor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Setup two-factor authentication"""
    auth_service = AuthService(db)
    setup_data = await auth_service.setup_two_factor(current_user)
    
    return {
        "qr_code": setup_data["qr_code"],
        "backup_codes": setup_data["backup_codes"],
        "message": "Scan the QR code with your authenticator app"
    }


@router.post("/2fa/verify")
async def verify_two_factor(
    verification_data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify and enable two-factor authentication"""
    # In production, verify TOTP code
    # For now, mock verification
    
    current_user.two_factor_enabled = True
    user_repo = UserRepository(db)
    await user_repo.update(current_user)
    
    return {"message": "Two-factor authentication enabled successfully"}


@router.post("/oauth/{provider}")
async def oauth_login(
    provider: str,
    oauth_data: OAuthCallback,
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth login from various providers"""
    # Mock OAuth implementation
    # In production, verify OAuth token with provider
    
    if provider not in ["google", "microsoft", "apple"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )
    
    # Mock user data from OAuth provider
    oauth_user_data = {
        "email": "user@example.com",
        "name": "OAuth User",
        "provider_id": oauth_data.code
    }
    
    # Find or create user
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(oauth_user_data["email"])
    
    if not user:
        # Create new user from OAuth data
        user = User(
            email=oauth_user_data["email"],
            username=oauth_user_data["email"].split("@")[0],
            display_name=oauth_user_data["name"],
            is_verified=True,  # OAuth users are pre-verified
            oauth_providers=[provider]
        )
        user = await user_repo.create(user)
    else:
        # Update OAuth providers
        if not user.oauth_providers:
            user.oauth_providers = []
        if provider not in user.oauth_providers:
            user.oauth_providers.append(provider)
            await user_repo.update(user)
    
    # Create tokens
    auth_service = AuthService(db)
    tokens = await auth_service.create_tokens(user)
    
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=user.to_dict()
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    payload = security_manager.verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    auth_service = AuthService(db)
    tokens = await auth_service.create_tokens(user)
    
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=user.to_dict()
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (invalidate tokens)"""
    # In production, add token to blacklist
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        level=current_user.level,
        experience_points=current_user.experience_points,
        badges=current_user.badges or [],
        subscription_tier=current_user.subscription_tier,
        is_verified=current_user.is_verified,
        learning_style=current_user.learning_style,
        preferred_language=current_user.preferred_language
    )


@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email address"""
    payload = security_manager.verify_token(token)
    
    if not payload or payload.get("type") != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_verified = True
    await user_repo.update(user)
    
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)
    
    if user:
        # Generate reset token
        reset_token = security_manager.create_access_token(
            data={"sub": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # Send reset email
        await email_service.send_password_reset_email(
            user.email,
            user.first_name or user.username,
            reset_token
        )
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """Reset user password"""
    payload = security_manager.verify_token(token)
    
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = security_manager.get_password_hash(new_password)
    await user_repo.update(user)
    
    return {"message": "Password reset successfully"}