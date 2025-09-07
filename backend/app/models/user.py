import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import hashlib

from .base_model import BaseModel

from ..core.database import Field

class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    CONTENT_CREATOR = "content_creator"
    AI_TRAINER = "ai_trainer"
    MODERATOR = "moderator"

class BaseUser(BaseModel):
    """Base user model with core authentication fields"""
    _table_name = "users"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'email': Field('TEXT', unique=True, nullable=False, index=True),
        'username': Field('TEXT', unique=True, nullable=False, index=True),
        'password_hash': Field('TEXT', nullable=False),
        'first_name': Field('TEXT'),
        'last_name': Field('TEXT'),
        'is_active': Field('BOOLEAN', default=True),
        'is_verified': Field('BOOLEAN', default=False),
        'is_superuser': Field('BOOLEAN', default=False),
        'role': Field('TEXT', default=UserRole.STUDENT.value),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'last_login': Field('TIMESTAMP'),
        'login_count': Field('INTEGER', default=0)
    }

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    async def authenticate(cls, username: str, password: str) -> Optional['BaseUser']:
        """Authenticate user with username and password"""
        users = await cls.filter(username=username)
        if users and users[0].password_hash == cls.hash_password(password):
            return users[0]
        return None

    @classmethod
    async def create_user(cls, email: str, username: str, password: str, 
                         role: UserRole = UserRole.STUDENT, **kwargs) -> 'BaseUser':
        """Create a new user with hashed password"""
        password_hash = cls.hash_password(password)
        return await cls.create(
            email=email, 
            username=username, 
            password_hash=password_hash, 
            role=role.value,
            **kwargs
        )
    
    async def update_login_info(self):
        """Update login information"""
        self.last_login = datetime.now()
        self.login_count = (self.login_count or 0) + 1
        await self.save()

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def verify_password(self, password: str) -> bool:
        """Verify if password matches hash"""
        return self.password_hash == self.hash_password(password)

    async def change_password(self, new_password: str):
        """Change user password"""
        self.password_hash = self.hash_password(new_password)
        await self.save()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with core fields"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login
        }