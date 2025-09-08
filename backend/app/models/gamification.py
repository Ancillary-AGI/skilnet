import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field

class BadgeType(str, Enum):
    ACHIEVEMENT = "achievement"
    SKILL = "skill"
    PARTICIPATION = "participation"
    COMPLETION = "completion"
    SOCIAL = "social"
    SPECIAL = "special"

class BadgeRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class AchievementType(str, Enum):
    COURSE_COMPLETION = "course_completion"
    LESSON_STREAK = "lesson_streak"
    QUIZ_PERFECT = "quiz_perfect"
    TIME_SPENT = "time_spent"
    SOCIAL_INTERACTION = "social_interaction"
    VR_AR_MASTERY = "vr_ar_mastery"
    AI_INTERACTION = "ai_interaction"
    PEER_TEACHING = "peer_teaching"

class Badge(SQLModel, table=True):
    """Achievement badges that users can earn"""
    __tablename__ = "badges"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    icon_url: Optional[str] = Field(default=None)
    badge_type: str = Field(default=BadgeType.ACHIEVEMENT.value)
    rarity: str = Field(default=BadgeRarity.COMMON.value)

    # Requirements
    points_required: int = Field(default=0)
    criteria: Dict[str, Any] = Field(default_factory=dict)

    # Rewards
    points_reward: int = Field(default=10)
    xp_reward: int = Field(default=50)
    unlocks_features: List[str] = Field(default_factory=list)

    # Metadata
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserBadge(SQLModel, table=True):
    """User earned badges"""
    __tablename__ = "user_badges"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    badge_id: str = Field(index=True, nullable=False)

    # Achievement Details
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    progress_percentage: float = Field(default=100.0)
    criteria_met: Dict[str, Any] = Field(default_factory=dict)

    # Display
    is_displayed: bool = Field(default=True)
    display_order: int = Field(default=0)

class Achievement(SQLModel, table=True):
    """Achievement definitions"""
    __tablename__ = "achievements"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    achievement_type: str = Field(default=AchievementType.COURSE_COMPLETION.value)

    # Requirements
    target_value: int = Field(default=1)
    time_limit_days: Optional[int] = Field(default=None)
    criteria: Dict[str, Any] = Field(default_factory=dict)

    # Rewards
    badge_id: Optional[str] = Field(default=None)
    points_reward: int = Field(default=25)
    xp_reward: int = Field(default=100)
    title_unlocked: Optional[str] = Field(default=None)

    # Metadata
    is_active: bool = Field(default=True)
    difficulty_level: str = Field(default="easy")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserAchievement(SQLModel, table=True):
    """User progress towards achievements"""
    __tablename__ = "user_achievements"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    achievement_id: str = Field(index=True, nullable=False)

    # Progress Tracking
    current_value: int = Field(default=0)
    target_value: int = Field(nullable=False)
    progress_percentage: float = Field(default=0.0)

    # Status
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class UserPoints(SQLModel, table=True):
    """User points and XP tracking"""
    __tablename__ = "user_points"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True, nullable=False)

    # Points System
    total_points: int = Field(default=0)
    available_points: int = Field(default=0)
    spent_points: int = Field(default=0)

    # XP System
    total_xp: int = Field(default=0)
    current_level: int = Field(default=1)
    xp_to_next_level: int = Field(default=1000)

    # Level Benefits
    level_title: str = Field(default="Novice Learner")
    unlocked_features: List[str] = Field(default_factory=list)

    # Streaks
    current_streak_days: int = Field(default=0)
    longest_streak_days: int = Field(default=0)
    last_activity_date: Optional[datetime] = Field(default=None)

    # Weekly/Monthly Stats
    points_this_week: int = Field(default=0)
    points_this_month: int = Field(default=0)
    week_start_date: datetime = Field(default_factory=datetime.utcnow)
    month_start_date: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Leaderboard(SQLModel, table=True):
    """Dynamic leaderboards for competitions"""
    __tablename__ = "leaderboards"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Configuration
    leaderboard_type: str = Field(default="points")  # points, xp, courses_completed, etc.
    time_period: str = Field(default="all_time")  # daily, weekly, monthly, all_time
    max_entries: int = Field(default=100)

    # Competition Settings
    is_active: bool = Field(default=True)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(default=None)

    # Rewards
    top_rewards: Dict[str, Any] = Field(default_factory=dict)  # {"1st": {"badge_id": "...", "points": 100}}

    created_at: datetime = Field(default_factory=datetime.utcnow)

class LeaderboardEntry(SQLModel, table=True):
    """User entries in leaderboards"""
    __tablename__ = "leaderboard_entries"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    leaderboard_id: str = Field(index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)

    # Score Data
    score_value: float = Field(default=0.0)
    rank_position: int = Field(default=0)
    previous_rank: int = Field(default=0)

    # Metadata
    entry_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Challenge(SQLModel, table=True):
    """Time-limited challenges and competitions"""
    __tablename__ = "challenges"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)

    # Challenge Configuration
    challenge_type: str = Field(default="learning_streak")
    target_metric: str = Field(default="lessons_completed")
    target_value: int = Field(default=10)

    # Time Frame
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime = Field(nullable=False)
    duration_days: int = Field(default=7)

    # Participation
    max_participants: Optional[int] = Field(default=None)
    current_participants: int = Field(default=0)
    is_active: bool = Field(default=True)

    # Rewards
    rewards: Dict[str, Any] = Field(default_factory=dict)
    bonus_multiplier: float = Field(default=1.0)

    # Categories
    category: str = Field(default="general")
    difficulty: str = Field(default="medium")

    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserChallenge(SQLModel, table=True):
    """User participation in challenges"""
    __tablename__ = "user_challenges"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    challenge_id: str = Field(index=True, nullable=False)

    # Progress
    current_value: int = Field(default=0)
    target_value: int = Field(nullable=False)
    progress_percentage: float = Field(default=0.0)

    # Status
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # Rewards
    rewards_claimed: bool = Field(default=False)
    bonus_earned: int = Field(default=0)

class PointsTransaction(SQLModel, table=True):
    """Audit trail for points transactions"""
    __tablename__ = "points_transactions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)

    # Transaction Details
    transaction_type: str = Field(nullable=False)  # earned, spent, bonus, penalty
    amount: int = Field(nullable=False)
    balance_after: int = Field(nullable=False)

    # Source Information
    source_type: str = Field(nullable=False)  # lesson_completion, quiz_passed, badge_earned, etc.
    source_id: Optional[str] = Field(default=None)  # ID of the source object
    description: str = Field(nullable=False)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reference_id: Optional[str] = Field(default=None)  # For grouping related transactions
