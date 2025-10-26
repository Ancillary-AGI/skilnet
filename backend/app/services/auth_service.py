"""
Authentication service for EduVerse platform
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import uuid

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserRegister, SocialProvider

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserRegister) -> User:
        """Create new user account"""
        # Hash password
        hashed_password = self._hash_password(user_data.password)
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            country_code=user_data.country_code,
            language_preference=user_data.language_preference,
            timezone=user_data.timezone,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        
        if not user or not user.hashed_password:
            return None
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def create_password_reset_token(self, user_id: str) -> str:
        """Create password reset token"""
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type": "password_reset"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def create_email_verification_token(self, user_id: str) -> str:
        """Create email verification token"""
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type": "email_verification"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    async def validate_access_token(self, token: str) -> Optional[User]:
        """Validate access token and return user"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            if payload.get("type") != "access":
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            user = await self.get_user_by_id(user_id)
            return user
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    async def validate_refresh_token(self, token: str) -> Optional[User]:
        """Validate refresh token and return user"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            if payload.get("type") != "refresh":
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            user = await self.get_user_by_id(user_id)
            return user
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def validate_password_reset_token(self, token: str) -> Optional[str]:
        """Validate password reset token and return user ID"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            if payload.get("type") != "password_reset":
                return None
            
            return payload.get("user_id")
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def validate_email_verification_token(self, token: str) -> Optional[str]:
        """Validate email verification token and return user ID"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            if payload.get("type") != "email_verification":
                return None
            
            return payload.get("user_id")
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.hashed_password = self._hash_password(new_password)
        await self.db.commit()
        return True
    
    async def verify_user_email(self, user_id: str) -> bool:
        """Mark user email as verified"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def invalidate_user_tokens(self, user_id: str) -> bool:
        """Invalidate all user tokens (logout from all devices)"""
        # In a production system, you would maintain a token blacklist
        # or use a different approach like storing tokens in Redis
        # For now, we'll just return True as tokens will expire naturally
        return True
    
    async def verify_social_token(self, provider: SocialProvider, token: str) -> Dict[str, Any]:
        """Verify social login token and get user info"""
        if provider == SocialProvider.GOOGLE:
            return await self._verify_google_token(token)
        elif provider == SocialProvider.APPLE:
            return await self._verify_apple_token(token)
        elif provider == SocialProvider.FACEBOOK:
            return await self._verify_facebook_token(token)
        else:
            raise ValueError(f"Unsupported social provider: {provider}")
    
    async def get_or_create_social_user(self, user_info: Dict[str, Any], provider: SocialProvider) -> User:
        """Get existing user or create new user from social login"""
        # Try to find existing user by email
        user = await self.get_user_by_email(user_info["email"])
        
        if user:
            # Update social ID if not set
            if provider == SocialProvider.GOOGLE and not user.google_id:
                user.google_id = user_info["id"]
            elif provider == SocialProvider.APPLE and not user.apple_id:
                user.apple_id = user_info["id"]
            elif provider == SocialProvider.FACEBOOK and not user.facebook_id:
                user.facebook_id = user_info["id"]
            
            await self.db.commit()
            return user
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=user_info["email"],
            full_name=user_info.get("name"),
            avatar_url=user_info.get("picture"),
            is_verified=True,  # Social accounts are pre-verified
            email_verified_at=datetime.utcnow(),
        )
        
        # Set social ID
        if provider == SocialProvider.GOOGLE:
            user.google_id = user_info["id"]
        elif provider == SocialProvider.APPLE:
            user.apple_id = user_info["id"]
        elif provider == SocialProvider.FACEBOOK:
            user.facebook_id = user_info["id"]
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    async def _verify_google_token(self, token: str) -> Dict[str, Any]:
        """Verify Google OAuth token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
            )
            
            if response.status_code != 200:
                raise ValueError("Invalid Google token")
            
            user_info = response.json()
            return {
                "id": user_info["id"],
                "email": user_info["email"],
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
            }
    
    async def _verify_apple_token(self, token: str) -> Dict[str, Any]:
        """Verify Apple Sign In token"""
        # Apple Sign In verification is more complex and requires
        # validating the JWT token with Apple's public keys
        # This is a simplified implementation
        try:
            # In production, you would verify the JWT signature
            # against Apple's public keys
            payload = jwt.decode(token, options={"verify_signature": False})
            
            return {
                "id": payload["sub"],
                "email": payload.get("email"),
                "name": payload.get("name"),
            }
        except jwt.JWTError:
            raise ValueError("Invalid Apple token")
    
    async def _verify_facebook_token(self, token: str) -> Dict[str, Any]:
        """Verify Facebook access token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/me?access_token={token}&fields=id,email,name,picture"
            )
            
            if response.status_code != 200:
                raise ValueError("Invalid Facebook token")
            
            user_info = response.json()
            return {
                "id": user_info["id"],
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture", {}).get("data", {}).get("url"),
            }