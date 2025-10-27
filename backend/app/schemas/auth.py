"""
Authentication schemas for EduVerse platform
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SocialProvider(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"
    MICROSOFT = "microsoft"


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    username: Optional[str] = Field(None, min_length=3, max_length=30, description="Username (optional)")
    country_code: Optional[str] = Field(None, min_length=2, max_length=2, description="ISO country code")
    language_preference: str = Field("en", description="Preferred language")
    timezone: Optional[str] = Field(None, description="User timezone")
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    marketing_consent: bool = Field(False, description="Marketing emails consent")
    terms_accepted: bool = Field(..., description="Terms and conditions acceptance")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v
    
    @validator('terms_accepted')
    def validate_terms(cls, v):
        """Ensure terms are accepted"""
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(False, description="Remember login session")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")


class SocialLogin(BaseModel):
    """Social login schema"""
    provider: SocialProvider = Field(..., description="Social login provider")
    token: str = Field(..., description="Social provider access token")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: 'UserResponse' = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str = Field(..., description="Email verification token")


class TwoFactorSetup(BaseModel):
    """Two-factor authentication setup schema"""
    secret: str = Field(..., description="2FA secret key")
    qr_code: str = Field(..., description="QR code for 2FA setup")


class TwoFactorVerify(BaseModel):
    """Two-factor authentication verification schema"""
    code: str = Field(..., min_length=6, max_length=6, description="2FA verification code")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate 2FA code format"""
        if not v.isdigit():
            raise ValueError('2FA code must be numeric')
        return v


class BiometricSetup(BaseModel):
    """Biometric authentication setup schema"""
    public_key: str = Field(..., description="Biometric public key")
    device_id: str = Field(..., description="Device identifier")
    biometric_type: str = Field(..., description="Type of biometric (fingerprint, face, etc.)")


class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: Optional[str] = Field(None, description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    bio: Optional[str] = Field(None, description="User bio")
    country_code: Optional[str] = Field(None, description="Country code")
    language_preference: str = Field("en", description="Language preference")
    timezone: Optional[str] = Field(None, description="User timezone")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verification status")
    is_premium: bool = Field(..., description="Premium subscription status")
    is_instructor: bool = Field(..., description="Instructor status")
    total_xp: int = Field(0, description="Total experience points")
    current_level: int = Field(1, description="Current level")
    current_streak: int = Field(0, description="Current learning streak")
    longest_streak: int = Field(0, description="Longest learning streak")
    created_at: datetime = Field(..., description="Account creation date")
    last_login_at: Optional[datetime] = Field(None, description="Last login date")
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update schema"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    bio: Optional[str] = Field(None, max_length=500)
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    language_preference: Optional[str] = Field(None)
    timezone: Optional[str] = Field(None)
    date_of_birth: Optional[datetime] = Field(None)
    learning_style: Optional[str] = Field(None)
    difficulty_preference: Optional[str] = Field(None)
    daily_goal_minutes: Optional[int] = Field(None, ge=5, le=480)
    accessibility_settings: Optional[Dict[str, Any]] = Field(None)
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class DeviceInfo(BaseModel):
    """Device information schema"""
    device_id: str = Field(..., description="Unique device identifier")
    device_type: str = Field(..., description="Device type (mobile, tablet, desktop, vr, etc.)")
    platform: str = Field(..., description="Platform (ios, android, web, windows, etc.)")
    app_version: str = Field(..., description="App version")
    os_version: str = Field(..., description="Operating system version")
    screen_resolution: Optional[str] = Field(None, description="Screen resolution")
    user_agent: Optional[str] = Field(None, description="User agent string")


class SessionInfo(BaseModel):
    """Session information schema"""
    session_id: str = Field(..., description="Session identifier")
    device_info: DeviceInfo = Field(..., description="Device information")
    ip_address: str = Field(..., description="IP address")
    location: Optional[Dict[str, Any]] = Field(None, description="Approximate location")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    is_active: bool = Field(..., description="Session active status")


class SecurityEvent(BaseModel):
    """Security event schema"""
    event_type: str = Field(..., description="Type of security event")
    description: str = Field(..., description="Event description")
    ip_address: str = Field(..., description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    timestamp: datetime = Field(..., description="Event timestamp")
    severity: str = Field(..., description="Event severity (low, medium, high, critical)")


# Update forward references
TokenResponse.model_rebuild()