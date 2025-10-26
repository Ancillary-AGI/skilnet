"""
Authentication schemas for EduVerse platform
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SocialProvider(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"
    MICROSOFT = "microsoft"

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    country_code: Optional[str] = Field(None, max_length=2)
    language_preference: str = Field("en", max_length=5)
    timezone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
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
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class SocialLogin(BaseModel):
    provider: SocialProvider
    token: str
    device_info: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    country_code: Optional[str]
    language_preference: str
    is_active: bool
    is_verified: bool
    is_premium: bool
    is_instructor: bool
    total_xp: int
    current_level: int
    current_streak: int
    created_at: Optional[datetime]
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
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
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class EmailVerification(BaseModel):
    token: str

class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str

class TwoFactorVerify(BaseModel):
    code: str

class BiometricSetup(BaseModel):
    device_id: str
    public_key: str
    device_name: Optional[str] = None

class BiometricAuth(BaseModel):
    device_id: str
    signature: str
    challenge: str

class DeviceInfo(BaseModel):
    device_id: str
    device_name: str
    device_type: str  # mobile, desktop, tablet, watch
    os: str
    browser: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class SessionInfo(BaseModel):
    id: str
    device_info: DeviceInfo
    created_at: datetime
    last_active: datetime
    is_current: bool

class UserPreferences(BaseModel):
    language_preference: str = "en"
    timezone: Optional[str] = None
    learning_style: Optional[str] = None  # visual, auditory, kinesthetic
    difficulty_preference: str = "intermediate"
    daily_goal_minutes: int = 30
    notifications_enabled: bool = True
    email_notifications: bool = True
    push_notifications: bool = True
    accessibility_settings: Optional[Dict[str, Any]] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    country_code: Optional[str] = Field(None, max_length=2)
    preferences: Optional[UserPreferences] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v