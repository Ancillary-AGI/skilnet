from typing import Dict, Any
from enum import Enum
from datetime import datetime

from .user import BaseUser

from ..core.database import Field

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MIXED = "mixed"

class VRComfortLevel(str, Enum):
    COMFORTABLE = "comfortable"
    MODERATE = "moderate"
    SENSITIVE = "sensitive"
    VERY_SENSITIVE = "very_sensitive"

class AIInteractionStyle(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    MOTIVATIONAL = "motivational"
    ADAPTIVE = "adaptive"

class SubscriptionTier(str, Enum):
    FREE = "free"
    EXPLORER = "explorer"
    SCHOLAR = "scholar"
    GENIUS = "genius"
    UNLIMITED = "unlimited"

class ProfileVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"
    COURSE_ONLY = "course_only"

class UserProfile(BaseUser):
    """Extended user model with profile and preferences"""
    
    # Extend the base columns with profile fields
    _columns = {
        **BaseUser._columns,  # Inherit all base columns
        'display_name': Field('TEXT'),
        'bio': Field('TEXT'),
        'avatar_url': Field('TEXT'),
        'learning_style': Field('TEXT', default=LearningStyle.MIXED.value),
        'preferred_language': Field('TEXT', default="en"),
        'timezone': Field('TEXT', default="UTC"),
        'experience_points': Field('INTEGER', default=0),
        'level': Field('INTEGER', default=1),
        'badges': Field('JSON', default=[]),
        'streak_days': Field('INTEGER', default=0),
        'vr_comfort_level': Field('TEXT', default=VRComfortLevel.COMFORTABLE.value),
        'preferred_vr_environment': Field('TEXT', default="classroom"),
        'motion_sickness_settings': Field('JSON', default={}),
        'ai_interaction_style': Field('TEXT', default=AIInteractionStyle.FRIENDLY.value),
        'preferred_ai_voice': Field('TEXT', default="neutral"),
        'ai_difficulty_adaptation': Field('BOOLEAN', default=True),
        'two_factor_enabled': Field('BOOLEAN', default=False),
        'two_factor_secret': Field('TEXT'),
        'webauthn_credentials': Field('JSON', default=[]),
        'oauth_providers': Field('JSON', default=[]),
        'subscription_tier': Field('TEXT', default=SubscriptionTier.FREE.value),
        'subscription_expires': Field('TIMESTAMP'),
        'profile_visibility': Field('TEXT', default=ProfileVisibility.PUBLIC.value),
        'data_sharing_consent': Field('BOOLEAN', default=False),
        'marketing_consent': Field('BOOLEAN', default=False),
        'accessibility_settings': Field('JSON', default={}),
        'screen_reader_enabled': Field('BOOLEAN', default=False),
        'high_contrast_mode': Field('BOOLEAN', default=False),
        'last_activity': Field('TIMESTAMP'),
    }

    @property
    def full_name(self) -> str:
        """Get user's full name with display name fallback"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username

    @property
    def is_premium(self) -> bool:
        """Check if user has active premium subscription"""
        premium_tiers = [SubscriptionTier.SCHOLAR.value, SubscriptionTier.GENIUS.value, 
                        SubscriptionTier.UNLIMITED.value, "premium", "enterprise"]
        
        if self.subscription_tier in premium_tiers:
            if self.subscription_expires:
                try:
                    if isinstance(self.subscription_expires, str):
                        expires = datetime.fromisoformat(self.subscription_expires.replace('Z', '+00:00'))
                    else:
                        expires = self.subscription_expires
                    return expires > datetime.utcnow()
                except (ValueError, TypeError):
                    return False
            return True  # No expiration date means perpetual subscription
        return False

    async def add_experience_points(self, points: int):
        """Add experience points and level up if needed"""
        self.experience_points += points
        new_level = int((self.experience_points / 100) ** 0.5) + 1
        if new_level > self.level:
            self.level = new_level
        await self.save()

    async def add_badge(self, badge_name: str):
        """Add a badge to user's collection"""
        if not self.badges:
            self.badges = []
        if badge_name not in self.badges:
            self.badges.append(badge_name)
        await self.save()

    async def update_streak(self, active_today: bool = True):
        """Update login streak"""
        if active_today:
            self.streak_days += 1
        else:
            self.streak_days = 0
        await self.save()

    async def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        await self.save()

    def get_learning_preferences(self) -> Dict[str, Any]:
        """Get learning preferences as a dictionary"""
        return {
            "learning_style": self.learning_style,
            "preferred_language": self.preferred_language,
            "timezone": self.timezone,
            "ai_interaction_style": self.ai_interaction_style,
            "ai_difficulty_adaptation": self.ai_difficulty_adaptation,
            "preferred_ai_voice": self.preferred_ai_voice
        }

    def get_accessibility_settings(self) -> Dict[str, Any]:
        """Get accessibility settings"""
        base_settings = {
            "screen_reader_enabled": self.screen_reader_enabled,
            "high_contrast_mode": self.high_contrast_mode
        }
        # Merge with custom accessibility settings
        if self.accessibility_settings:
            base_settings.update(self.accessibility_settings)
        return base_settings

    def to_dict(self, include_profile: bool = False) -> Dict[str, Any]:
        """Convert to dictionary with optional profile fields"""
        base_data = super().to_dict()
        
        if include_profile:
            profile_data = {
                "display_name": self.display_name,
                "bio": self.bio,
                "avatar_url": self.avatar_url,
                "learning_style": self.learning_style,
                "preferred_language": self.preferred_language,
                "timezone": self.timezone,
                "experience_points": self.experience_points,
                "level": self.level,
                "badges": self.badges or [],
                "streak_days": self.streak_days,
                "vr_comfort_level": self.vr_comfort_level,
                "preferred_vr_environment": self.preferred_vr_environment,
                "ai_interaction_style": self.ai_interaction_style,
                "preferred_ai_voice": self.preferred_ai_voice,
                "subscription_tier": self.subscription_tier,
                "is_premium": self.is_premium,
                "profile_visibility": self.profile_visibility,
                "last_activity": self.last_activity
            }
            base_data.update(profile_data)
        
        return base_data

    def to_public_profile(self) -> Dict[str, Any]:
        """Get public profile information (safe for sharing)"""
        public_data = {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "level": self.level,
            "badges": self.badges or [],
            "learning_style": self.learning_style if self.profile_visibility != ProfileVisibility.PRIVATE else None,
            "created_at": self.created_at
        }
        
        # Only show certain fields based on visibility settings
        if self.profile_visibility == ProfileVisibility.FRIENDS_ONLY:
            # Additional fields for friends
            public_data.update({
                "experience_points": self.experience_points,
                "streak_days": self.streak_days
            })
        
        return public_data