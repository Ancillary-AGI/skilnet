from .base_model import BaseModel
from ..core.database import Field
from enum import Enum
import uuid

class BadgeTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class AchievementType(str, Enum):
    COURSE_COMPLETION = "course_completion"
    STREAK = "streak"
    SOCIAL = "social"
    SKILL_MASTERY = "skill_mastery"
    CREATION = "creation"
    EXPLORATION = "exploration"
    COLLECTION = "collection"

class Badge(BaseModel):
    _table_name = "badges"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'name': Field('TEXT', nullable=False, unique=True),
        'description': Field('TEXT'),
        'tier': Field('TEXT', default=BadgeTier.BRONZE),
        'icon_url': Field('TEXT'),
        'xp_reward': Field('INTEGER', default=0),
        'achievement_type': Field('TEXT', default=AchievementType.COURSE_COMPLETION),
        'requirements': Field('JSON', default={}),
        'is_hidden': Field('BOOLEAN', default=False),
        'rarity_percentage': Field('REAL'),  # % of users who have this
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class UserBadge(BaseModel):
    _table_name = "user_badges"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'badge_id': Field('TEXT', nullable=False, index=True),
        'earned_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'context_data': Field('JSON'),  # How they earned it
        'is_featured': Field('BOOLEAN', default=False),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class Leaderboard(BaseModel):
    _table_name = "leaderboards"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'name': Field('TEXT', nullable=False),
        'description': Field('TEXT'),
        'scope': Field('TEXT'),  # global, course, weekly, monthly
        'metric': Field('TEXT'),  # xp, badges, courses_completed
        'start_date': Field('TIMESTAMP'),
        'end_date': Field('TIMESTAMP'),
        'is_active': Field('BOOLEAN', default=True),
        'participant_count': Field('INTEGER', default=0),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class LeaderboardEntry(BaseModel):
    _table_name = "leaderboard_entries"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'leaderboard_id': Field('TEXT', nullable=False, index=True),
        'user_id': Field('TEXT', nullable=False, index=True),
        'score': Field('REAL', default=0.0),
        'rank': Field('INTEGER'),
        'previous_rank': Field('INTEGER'),
        'progress_since_last': Field('REAL', default=0.0),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }