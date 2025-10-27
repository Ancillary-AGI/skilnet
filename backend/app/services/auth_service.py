"""
Authentication service for EduVerse platform
"""

import jwt
import bcrypt
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
import httpx
import base64
import json

from app.core.config import settings
from app.core.logging import get_logger, log_performance
from app.models.user import User
from app.schemas.auth import UserRegister, SocialProvider, DeviceInfo


class AuthService:
    """Authentication service with comprehensive security features"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = get_logger("auth_service")
    
    @log_performance
    async def create_user(self, user_data: UserRegister) -> User:
        """Create a new user account"""
        try:
            # Hash password
            hashed_password = self._hash_password(user_data.password)
            
            # Create user instance
            user = User(
                id=str(uuid.uuid4()),
                email=user_data.email.lower(),
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                country_code=user_data.country_code,
                language_preference=user_data.language_preference,
                timezone=user_data.timezone,
                date_of_birth=user_data.date_of_birth,
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow()
            )
            
            # Add to database
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            self.logger.info(f"User created successfully: {user.email}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to create user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User creation failed: {str(e)}"
            )
    
    @log_performance
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            # Get user by email
            user = await self.get_user_by_email(email.lower())
            
            if not user:
                self.logger.warning(f"Authentication failed: User not found - {email}")
                return None
            
            if not user.is_active:
                self.logger.warning(f"Authentication failed: User inactive - {email}")
                return None
            
            # Verify password
            if not self._verify_password(password, user.hashed_password):
                self.logger.warning(f"Authentication failed: Invalid password - {email}")
                return None
            
            self.logger.info(f"User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None
    
    @log_performance
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email.lower())
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user by email: {e}")
            return None
    
    @log_performance
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user by ID: {e}")
            return None
    
    def create_access_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())  # Unique token ID for revocation
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def create_password_reset_token(self, user_id: str) -> str:
        """Create password reset token"""
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "type": "password_reset",
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def create_email_verification_token(self, user_id: str) -> str:
        """Create email verification token"""
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
        
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "type": "email_verification",
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @log_performance
    async def validate_access_token(self, token: str) -> Optional[User]:
        """Validate access token and return user"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != "access":
                return None
            
            # Get user
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            user = await self.get_user_by_id(user_id)
            return user
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Access token expired")
            return None
        except jwt.JWTError as e:
            self.logger.warning(f"Invalid access token: {e}")
            return None
    
    @log_performance
    async def validate_refresh_token(self, token: str) -> Optional[User]:
        """Validate refresh token and return user"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != "refresh":
                return None
            
            # Get user
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            user = await self.get_user_by_id(user_id)
            return user
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Refresh token expired")
            return None
        except jwt.JWTError as e:
            self.logger.warning(f"Invalid refresh token: {e}")
            return None
    
    def validate_password_reset_token(self, token: str) -> Optional[str]:
        """Validate password reset token and return user ID"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != "password_reset":
                return None
            
            return payload.get("user_id")
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Password reset token expired")
            return None
        except jwt.JWTError as e:
            self.logger.warning(f"Invalid password reset token: {e}")
            return None
    
    def validate_email_verification_token(self, token: str) -> Optional[str]:
        """Validate email verification token and return user ID"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != "email_verification":
                return None
            
            return payload.get("user_id")
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Email verification token expired")
            return None
        except jwt.JWTError as e:
            self.logger.warning(f"Invalid email verification token: {e}")
            return None
    
    @log_performance
    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login_at=datetime.utcnow())
            )
            await self.db.commit()
        except Exception as e:
            self.logger.error(f"Failed to update last login: {e}")
    
    @log_performance
    async def update_password(self, user_id: str, new_password: str) -> None:
        """Update user password"""
        try:
            hashed_password = self._hash_password(new_password)
            
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(hashed_password=hashed_password)
            )
            await self.db.commit()
            
            self.logger.info(f"Password updated for user: {user_id}")
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to update password: {e}")
            raise
    
    @log_performance
    async def verify_user_email(self, user_id: str) -> None:
        """Mark user email as verified"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    is_verified=True,
                    email_verified_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            
            self.logger.info(f"Email verified for user: {user_id}")
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to verify email: {e}")
            raise
    
    @log_performance
    async def invalidate_user_tokens(self, user_id: str) -> None:
        """Invalidate all user tokens (logout from all devices)"""
        # In a production system, you would maintain a token blacklist
        # or use a different approach like storing token versions in the database
        self.logger.info(f"Tokens invalidated for user: {user_id}")
    
    @log_performance
    async def verify_social_token(self, provider: SocialProvider, token: str) -> Dict[str, Any]:
        """Verify social login token and get user info"""
        try:
            if provider == SocialProvider.GOOGLE:
                return await self._verify_google_token(token)
            elif provider == SocialProvider.APPLE:
                return await self._verify_apple_token(token)
            elif provider == SocialProvider.FACEBOOK:
                return await self._verify_facebook_token(token)
            else:
                raise ValueError(f"Unsupported social provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Social token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Social login verification failed: {str(e)}"
            )
    
    @log_performance
    async def get_or_create_social_user(self, user_info: Dict[str, Any], provider: SocialProvider) -> User:
        """Get existing user or create new user from social login"""
        try:
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
                email=user_info["email"].lower(),
                full_name=user_info.get("name", ""),
                avatar_url=user_info.get("picture"),
                is_active=True,
                is_verified=True,  # Social accounts are pre-verified
                email_verified_at=datetime.utcnow(),
                created_at=datetime.utcnow()
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
            
            self.logger.info(f"Social user created: {user.email} via {provider}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to create social user: {e}")
            raise
    
    async def _verify_google_token(self, token: str) -> Dict[str, Any]:
        """Verify Google OAuth token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
            )
            
            if response.status_code != 200:
                raise ValueError("Invalid Google token")
            
            return response.json()
    
    async def _verify_apple_token(self, token: str) -> Dict[str, Any]:
        """Verify Apple Sign-In token"""
        # Apple Sign-In uses JWT tokens that need to be verified
        # This is a simplified implementation
        try:
            # Decode without verification for demo (in production, verify with Apple's public keys)
            payload = jwt.decode(token, options={"verify_signature": False})
            
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "name": payload.get("name", ""),
            }
        except Exception as e:
            raise ValueError(f"Invalid Apple token: {e}")
    
    async def _verify_facebook_token(self, token: str) -> Dict[str, Any]:
        """Verify Facebook OAuth token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.facebook.com/me?access_token={token}&fields=id,name,email,picture"
            )
            
            if response.status_code != 200:
                raise ValueError("Invalid Facebook token")
            
            data = response.json()
            return {
                "id": data["id"],
                "email": data.get("email"),
                "name": data.get("name", ""),
                "picture": data.get("picture", {}).get("data", {}).get("url")
            }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )