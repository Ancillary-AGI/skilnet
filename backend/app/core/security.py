"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core.database import get_db

# Password hashing
from passlib.context import CryptContext
import hashlib
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        # Try bcrypt if available
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except:
            pass

    # Fallback to SHA256
    salt = hashed_password.split(":")[0] if ":" in hashed_password else ""
    if salt:
        expected = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return hashed_password == f"{salt}:{expected}"

    return False

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    # Use SHA256 with salt for now
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            return None

        return payload
    except PyJWTError:
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify refresh token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            return None

        return payload
    except PyJWTError:
        return None

def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Get user from JWT token"""
    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user

def create_user_tokens(user: User) -> Dict[str, str]:
    """Create access and refresh tokens for user"""
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def refresh_access_token(refresh_token: str, db: Session) -> Optional[Dict[str, str]]:
    """Generate new access token from refresh token"""
    payload = verify_refresh_token(refresh_token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Create new tokens
    return create_user_tokens(user)

def require_auth(credentials: str) -> Dict[str, Any]:
    """Extract and verify authentication from request"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not credentials.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials[7:]  # Remove "Bearer " prefix
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

def require_admin(payload: Dict[str, Any]):
    """Check if user has admin privileges"""
    user_role = payload.get("role", "user")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

def require_premium(payload: Dict[str, Any]):
    """Check if user has premium subscription"""
    subscription_tier = payload.get("subscription_tier", "free")
    if subscription_tier == "free":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Premium subscription required"
        )

def check_permission(payload: Dict[str, Any], permission: str) -> bool:
    """Check if user has specific permission"""
    user_permissions = payload.get("permissions", [])
    return permission in user_permissions

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(payload: Dict[str, Any]):
        if not check_permission(payload, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return payload
    return decorator

# Rate limiting utilities
class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if request is within rate limit"""
        now = datetime.utcnow()

        if key not in self.requests:
            self.requests[key] = []

        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).total_seconds() < window_seconds
        ]

        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True

        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_rate_limit(key: str, limit: int = 100, window_seconds: int = 3600) -> bool:
    """Check rate limit for key"""
    return rate_limiter.is_allowed(key, limit, window_seconds)

# Security headers middleware
def get_security_headers():
    """Get security headers for responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }

# Input validation utilities
def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    return True, "Password is strong"

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    import html
    return html.escape(text)

# Session management
def create_session(user_id: str, db: Session) -> str:
    """Create user session"""
    session_id = f"session_{user_id}_{datetime.utcnow().timestamp()}"

    # Store session in database
    # This would create a session record

    return session_id

def validate_session(session_id: str, db: Session) -> Optional[str]:
    """Validate session and return user_id"""
    try:
        # Query session from database
        # Return user_id if valid
        return "user_123"  # Placeholder
    except Exception:
        return None

def invalidate_session(session_id: str, db: Session):
    """Invalidate user session"""
    # Remove session from database
    pass

# Two-factor authentication utilities
def generate_2fa_secret() -> str:
    """Generate 2FA secret"""
    import secrets
    return secrets.token_hex(32)

def verify_2fa_token(secret: str, token: str) -> bool:
    """Verify 2FA token"""
    import pyotp

    totp = pyotp.TOTP(secret)
    return totp.verify(token)

# Biometric authentication utilities
def register_biometric_data(user_id: str, biometric_data: str, db: Session):
    """Register biometric data for user"""
    # Store encrypted biometric data
    pass

def verify_biometric_data(user_id: str, biometric_data: str, db: Session) -> bool:
    """Verify biometric data"""
    # Compare biometric data
    return True  # Placeholder

# Audit logging
def log_security_event(event_type: str, user_id: str, details: Dict[str, Any]):
    """Log security-related events"""
    import logging

    logger = logging.getLogger("security")
    logger.info(f"Security Event: {event_type} | User: {user_id} | Details: {details}")

# Encryption utilities
def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    from cryptography.fernet import Fernet
    import base64

    # Generate key from settings
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'\0'))
    f = Fernet(key)

    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    from cryptography.fernet import Fernet
    import base64

    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'\0'))
    f = Fernet(key)

    return f.decrypt(encrypted_data.encode()).decode()

# API key management
def generate_api_key(user_id: str) -> str:
    """Generate API key for user"""
    import secrets
    api_key = f"eduv_{secrets.token_hex(32)}"

    # Store API key hash in database
    # This would create an api_key record

    return api_key

def verify_api_key(api_key: str, db: Session) -> Optional[str]:
    """Verify API key and return user_id"""
    # Query API key from database
    return "user_123"  # Placeholder

# OAuth utilities
def generate_oauth_state() -> str:
    """Generate OAuth state parameter"""
    import secrets
    return secrets.token_urlsafe(32)

def verify_oauth_state(state: str, stored_state: str) -> bool:
    """Verify OAuth state parameter"""
    return state == stored_state

def exchange_oauth_code(code: str, provider: str) -> Dict[str, Any]:
    """Exchange OAuth code for access token"""
    # Implement OAuth code exchange for different providers
    return {
        "access_token": "oauth_access_token",
        "user_info": {
            "id": "oauth_user_id",
            "email": "user@example.com",
            "name": "OAuth User"
        }
    }

# Security monitoring
def detect_suspicious_activity(user_id: str, activity: Dict[str, Any]) -> bool:
    """Detect suspicious user activity"""
    # Implement suspicious activity detection
    # Multiple failed login attempts
    # Unusual login locations
    # Rapid API calls
    # etc.

    return False  # Placeholder

def block_suspicious_user(user_id: str, reason: str, db: Session):
    """Block user due to suspicious activity"""
    # Update user status to blocked
    # Log security event
    pass

# Data validation
def validate_user_data(data: Dict[str, Any]) -> bool:
    """Validate user input data"""
    required_fields = ["email", "name"]

    for field in required_fields:
        if field not in data or not data[field]:
            return False

    if not validate_email(data["email"]):
        return False

    return True

def sanitize_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize user input data"""
    sanitized = {}

    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value.strip())
        else:
            sanitized[key] = value

    return sanitized

# FastAPI dependency functions
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Export security utilities
__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "verify_refresh_token",
    "authenticate_user",
    "create_user_tokens",
    "refresh_access_token",
    "require_auth",
    "require_admin",
    "require_premium",
    "check_permission",
    "require_permission",
    "get_security_headers",
    "validate_email",
    "validate_password_strength",
    "sanitize_input",
    "log_security_event",
    "encrypt_sensitive_data",
    "decrypt_sensitive_data",
    "generate_api_key",
    "verify_api_key",
    "detect_suspicious_activity",
    "validate_user_data",
    "sanitize_user_data",
    "get_current_user",
    "get_current_active_user"
]
