# Schemas package

from .auth import (
    UserCreate, UserUpdate, UserResponse, UserProfileResponse,
    LoginRequest, TokenResponse, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
    EmailVerificationRequest, EmailVerificationConfirm,
    SocialLoginRequest, TwoFactorSetupResponse, TwoFactorVerifyRequest,
    TwoFactorDisableRequest, AccountDeletionRequest,
    UserStats, InstructorStats,
    # Backward compatibility aliases
    UserLogin, UserRegister, PasswordReset, SocialLogin
)

from .course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseFilter,
    CourseStatistics, CourseRatingCreate, CourseRatingUpdate,
    CourseRatingResponse, InstructorCourseSummary
)

from .enrollment import (
    EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse,
    EnrollmentDetailResponse, EnrollmentStatistics,
    CertificateRequest, UserEnrollmentsResponse, CourseEnrollmentsResponse
)

from .content import (
    ContentUploadResponse, ContentMetadata, ContentInfo,
    ContentListResponse, ContentValidationResult,
    ContentProcessingRequest, ContentProcessingStatus,
    BulkUploadRequest, BulkUploadResult,
    ContentStreamingInfo, ContentAccessLog,
    ContentAnalytics, ContentQuotaInfo,
    ContentBackupInfo, ContentSecurityScan
)

__all__ = [
    # Auth schemas
    "UserCreate", "UserUpdate", "UserResponse", "UserProfileResponse",
    "LoginRequest", "TokenResponse", "RefreshTokenRequest",
    "PasswordResetRequest", "PasswordResetConfirm", "ChangePasswordRequest",
    "EmailVerificationRequest", "EmailVerificationConfirm",
    "SocialLoginRequest", "TwoFactorSetupResponse", "TwoFactorVerifyRequest",
    "TwoFactorDisableRequest", "AccountDeletionRequest",
    "UserStats", "InstructorStats",
    # Backward compatibility aliases
    "UserLogin", "UserRegister", "PasswordReset", "SocialLogin",

    # Course schemas
    "CourseCreate", "CourseUpdate", "CourseResponse", "CourseFilter",
    "CourseStatistics", "CourseRatingCreate", "CourseRatingUpdate",
    "CourseRatingResponse", "InstructorCourseSummary",

    # Enrollment schemas
    "EnrollmentCreate", "EnrollmentUpdate", "EnrollmentResponse",
    "EnrollmentDetailResponse", "EnrollmentStatistics",
    "CertificateRequest", "UserEnrollmentsResponse", "CourseEnrollmentsResponse",

    # Content schemas
    "ContentUploadResponse", "ContentMetadata", "ContentInfo",
    "ContentListResponse", "ContentValidationResult",
    "ContentProcessingRequest", "ContentProcessingStatus",
    "BulkUploadRequest", "BulkUploadResult",
    "ContentStreamingInfo", "ContentAccessLog",
    "ContentAnalytics", "ContentQuotaInfo",
    "ContentBackupInfo", "ContentSecurityScan"
]
