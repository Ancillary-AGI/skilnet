"""
Authentication schemas for EduVerse platform
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SocialProvider(str, Enum):
    """Social login providers"""
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    is_instructor: bool = Field(False, description="Whether user is an instructor")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Last name")
    is_instructor: Optional[bool] = Field(None, description="Whether user is an instructor")
    is_active: Optional[bool] = Field(None, description="Whether user account is active")


class UserResponse(UserBase):
    """User response schema"""
    id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    is_active: bool = Field(True, description="Whether user account is active")

    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    """Extended user profile response"""
    bio: Optional[str] = Field(None, description="User biography")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    website: Optional[str] = Field(None, description="Personal website")
    location: Optional[str] = Field(None, description="User location")
    social_links: Optional[dict] = Field(None, description="Social media links")
    preferences: Optional[dict] = Field(None, description="User preferences")


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")




class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    email: EmailStr = Field(..., description="Email to verify")


class EmailVerificationConfirm(BaseModel):
    """Email verification confirmation schema"""
    token: str = Field(..., description="Verification token")


class SocialLoginRequest(BaseModel):
    """Social login request schema"""
    provider: str = Field(..., description="Social provider (google, apple, facebook)")
    access_token: str = Field(..., description="OAuth access token")
    id_token: Optional[str] = Field(None, description="OAuth ID token")


class TwoFactorSetupResponse(BaseModel):
    """2FA setup response schema"""
    secret: str = Field(..., description="TOTP secret")
    qr_code_url: str = Field(..., description="QR code URL for authenticator apps")
    backup_codes: list[str] = Field(..., description="Backup recovery codes")


class TwoFactorVerifyRequest(BaseModel):
    """2FA verification request schema"""
    code: str = Field(..., min_length=6, max_length=6, description="TOTP code")


class TwoFactorDisableRequest(BaseModel):
    """2FA disable request schema"""
    password: str = Field(..., description="User password for confirmation")


class AccountDeletionRequest(BaseModel):
    """Account deletion request schema"""
    password: str = Field(..., description="User password for confirmation")
    reason: Optional[str] = Field(None, description="Reason for account deletion")


class PasskeyRegistrationRequest(BaseModel):
    """Passkey registration request schema"""
    challenge: str = Field(..., description="Base64 encoded challenge")
    user_id: str = Field(..., description="User ID for registration")


class PasskeyRegistrationResponse(BaseModel):
    """Passkey registration response schema"""
    challenge: str = Field(..., description="Base64 encoded challenge")
    rp: Dict[str, Any] = Field(..., description="Relying party information")
    user: Dict[str, Any] = Field(..., description="User information")
    pub_key_cred_params: List[Dict[str, Any]] = Field(..., description="Public key credential parameters")
    authenticator_selection: Dict[str, Any] = Field(..., description="Authenticator selection criteria")
    timeout: int = Field(60000, description="Timeout in milliseconds")
    attestation: str = Field("direct", description="Attestation preference")


class PasskeyCredential(BaseModel):
    """Passkey credential schema"""
    id: str = Field(..., description="Credential ID")
    raw_id: str = Field(..., description="Raw credential ID")
    type: str = Field("public-key", description="Credential type")
    response: Dict[str, Any] = Field(..., description="Authenticator response")


class PasskeyRegistrationConfirm(BaseModel):
    """Passkey registration confirmation schema"""
    credential: PasskeyCredential = Field(..., description="Passkey credential")
    challenge: str = Field(..., description="Original challenge")


class PasskeyAuthenticationRequest(BaseModel):
    """Passkey authentication request schema"""
    email: EmailStr = Field(..., description="User email")


class PasskeyAuthenticationChallenge(BaseModel):
    """Passkey authentication challenge schema"""
    challenge: str = Field(..., description="Base64 encoded challenge")
    allow_credentials: List[Dict[str, Any]] = Field(..., description="Allowed credentials")
    timeout: int = Field(60000, description="Timeout in milliseconds")
    user_verification: str = Field("preferred", description="User verification requirement")


class PasskeyAuthenticationConfirm(BaseModel):
    """Passkey authentication confirmation schema"""
    email: str = Field(..., description="User email")
    credential: PasskeyCredential = Field(..., description="Passkey credential")
    challenge: str = Field(..., description="Original challenge")


class UserStats(BaseModel):
    """User statistics schema"""
    total_courses_enrolled: int = Field(0, description="Total courses enrolled")
    completed_courses: int = Field(0, description="Completed courses")
    total_study_time: int = Field(0, description="Total study time in minutes")
    average_score: float = Field(0.0, description="Average quiz/test score")
    certificates_earned: int = Field(0, description="Number of certificates earned")
    achievements_unlocked: int = Field(0, description="Number of achievements unlocked")


class InstructorStats(BaseModel):
    """Instructor statistics schema"""
    total_courses: int = Field(0, description="Total courses created")
    total_students: int = Field(0, description="Total enrolled students")
    average_rating: float = Field(0.0, description="Average course rating")
    total_revenue: float = Field(0.0, description="Total revenue earned")
    published_courses: int = Field(0, description="Number of published courses")
    draft_courses: int = Field(0, description="Number of draft courses")


# Aliases for backward compatibility
UserLogin = LoginRequest
UserRegister = UserCreate
PasswordReset = PasswordResetRequest
SocialLogin = SocialLoginRequest
