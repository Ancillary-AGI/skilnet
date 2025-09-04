"""
Authentication schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    learning_style: Optional[str] = "visual"
    preferred_language: Optional[str] = "en"
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    remember_me: bool = False


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    user: Dict[str, Any]


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    level: int = 1
    experience_points: int = 0
    badges: List[str] = []
    subscription_tier: str = "free"
    is_verified: bool = False
    learning_style: Optional[str]
    preferred_language: str = "en"
    message: Optional[str] = None


class WebAuthnRegistrationStart(BaseModel):
    """WebAuthn registration start schema"""
    user_id: str
    username: str


class WebAuthnRegistrationComplete(BaseModel):
    """WebAuthn registration completion schema"""
    credential: Dict[str, Any]
    challenge: str


class WebAuthnAuthenticationStart(BaseModel):
    """WebAuthn authentication start schema"""
    user_id: Optional[str] = None


class WebAuthnAuthenticationComplete(BaseModel):
    """WebAuthn authentication completion schema"""
    credential: Dict[str, Any]
    challenge: str


class TwoFactorSetup(BaseModel):
    """Two-factor authentication setup schema"""
    password: str  # Confirm password before setup


class TwoFactorVerify(BaseModel):
    """Two-factor authentication verification schema"""
    code: str


class OAuthCallback(BaseModel):
    """OAuth callback schema"""
    code: str
    state: Optional[str] = None
    redirect_uri: str


class PasswordReset(BaseModel):
    """Password reset schema"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str