import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

class StudyGroupType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    COURSE_SPECIFIC = "course_specific"
    SKILL_BASED = "skill_based"
    COMPETITION = "competition"

class GroupRole(str, Enum):
    OWNER = "owner"
    MODERATOR = "moderator"
    MEMBER = "member"
    PENDING = "pending"

class PostType(str, Enum):
    DISCUSSION = "discussion"
    QUESTION = "question"
    ANNOUNCEMENT = "announcement"
    RESOURCE = "resource"
    POLL = "poll"

class StudyGroup(SQLModel, table=True):
    """Study groups for collaborative learning"""
    __tablename__ = "study_groups"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Group Configuration
    group_type: str = Field(default=StudyGroupType.PUBLIC.value)
    course_id: Optional[str] = Field(default=None, index=True)
    subject_area: Optional[str] = Field(default=None)
    skill_level: str = Field(default="intermediate")

    # Membership
    max_members: Optional[int] = Field(default=None)
    current_members: int = Field(default=0)
    is_joinable: bool = Field(default=True)
    requires_approval: bool = Field(default=False)

    # Learning Focus
    learning_objectives: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    meeting_schedule: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    study_materials: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    # Gamification
    group_points: int = Field(default=0)
    achievements_unlocked: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Communication
    discussion_forum_enabled: bool = Field(default=True)
    video_calls_enabled: bool = Field(default=True)
    file_sharing_enabled: bool = Field(default=True)

    # Metadata
    created_by: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GroupMembership(SQLModel, table=True):
    """User membership in study groups"""
    __tablename__ = "group_memberships"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    group_id: str = Field(index=True, nullable=False)

    # Membership Details
    role: str = Field(default=GroupRole.MEMBER.value)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = Field(default=None)

    # Activity Tracking
    posts_count: int = Field(default=0)
    last_activity: Optional[datetime] = Field(default=None)
    contribution_score: int = Field(default=0)

    # Status
    is_active: bool = Field(default=True)
    muted_until: Optional[datetime] = Field(default=None)

class DiscussionForum(SQLModel, table=True):
    """Discussion forums for courses and groups"""
    __tablename__ = "discussion_forums"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Association
    course_id: Optional[str] = Field(default=None, index=True)
    group_id: Optional[str] = Field(default=None, index=True)
    lesson_id: Optional[str] = Field(default=None, index=True)

    # Configuration
    is_moderated: bool = Field(default=False)
    allows_anonymous_posts: bool = Field(default=False)
    requires_course_enrollment: bool = Field(default=False)

    # Categories
    categories: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Statistics
    total_posts: int = Field(default=0)
    total_threads: int = Field(default=0)
    active_users_count: int = Field(default=0)

    # Status
    is_active: bool = Field(default=True)
    created_by: str = Field(nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ForumPost(SQLModel, table=True):
    """Posts in discussion forums"""
    __tablename__ = "forum_posts"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    forum_id: str = Field(index=True, nullable=False)
    author_id: str = Field(index=True, nullable=False)

    # Content
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    post_type: str = Field(default=PostType.DISCUSSION.value)

    # Thread Structure
    parent_post_id: Optional[str] = Field(default=None, index=True)  # For replies
    thread_id: str = Field(nullable=False, index=True)  # Root post ID

    # Metadata
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    attachments: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    # Engagement
    upvotes: int = Field(default=0)
    downvotes: int = Field(default=0)
    reply_count: int = Field(default=0)
    view_count: int = Field(default=0)

    # Moderation
    is_pinned: bool = Field(default=False)
    is_locked: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    moderated_by: Optional[str] = Field(default=None)
    moderation_reason: Optional[str] = Field(default=None)

    # Learning Context
    related_lesson_id: Optional[str] = Field(default=None)
    learning_objective: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PeerLearningSession(SQLModel, table=True):
    """Peer-to-peer learning sessions"""
    __tablename__ = "peer_learning_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Participants
    host_id: str = Field(nullable=False)
    participants: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # User IDs
    max_participants: int = Field(default=10)

    # Session Details
    session_type: str = Field(default="study_session")  # study_session, tutoring, group_project
    subject_area: str = Field(nullable=False)
    skill_level: str = Field(default="intermediate")

    # Scheduling
    scheduled_start: datetime = Field(nullable=False)
    scheduled_end: datetime = Field(nullable=False)
    actual_start: Optional[datetime] = Field(default=None)
    actual_end: Optional[datetime] = Field(default=None)

    # Learning Focus
    learning_objectives: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    materials_to_cover: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    # Communication
    video_enabled: bool = Field(default=True)
    screen_sharing_enabled: bool = Field(default=True)
    recording_enabled: bool = Field(default=False)

    # Status
    status: str = Field(default="scheduled")  # scheduled, in_progress, completed, cancelled
    is_public: bool = Field(default=False)

    # Analytics
    attendance_count: int = Field(default=0)
    average_rating: float = Field(default=0.0)
    feedback_collected: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudyBuddyMatch(SQLModel, table=True):
    """AI-powered study buddy matching"""
    __tablename__ = "study_buddy_matches"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    buddy_id: str = Field(index=True, nullable=False)

    # Matching Criteria
    matching_score: float = Field(default=0.0)
    matching_factors: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))  # learning_style, goals, schedule, etc.

    # Relationship Status
    status: str = Field(default="pending")  # pending, accepted, active, ended
    initiated_by: str = Field(nullable=False)  # user_id or system

    # Study Preferences
    study_frequency: str = Field(default="weekly")  # daily, weekly, biweekly
    preferred_times: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # time slots
    study_goals: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Communication Preferences
    preferred_platforms: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # discord, zoom, etc.
    communication_style: str = Field(default="balanced")  # quiet, balanced, social

    # Activity Tracking
    sessions_completed: int = Field(default=0)
    total_study_time: int = Field(default=0)
    goals_achieved: int = Field(default=0)

    # Relationship Health
    satisfaction_rating: Optional[float] = Field(default=None)
    last_interaction: Optional[datetime] = Field(default=None)
    compatibility_score: float = Field(default=0.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CollaborativeProject(SQLModel, table=True):
    """Group projects and assignments"""
    __tablename__ = "collaborative_projects"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)

    # Project Details
    course_id: Optional[str] = Field(default=None, index=True)
    lesson_id: Optional[str] = Field(default=None, index=True)
    project_type: str = Field(default="assignment")  # assignment, research, creative, practical

    # Team Configuration
    team_members: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # User IDs
    max_team_size: int = Field(default=4)
    min_team_size: int = Field(default=2)

    # Timeline
    start_date: datetime = Field(default_factory=datetime.utcnow)
    deadline: datetime = Field(nullable=False)
    submission_date: Optional[datetime] = Field(default=None)

    # Requirements
    deliverables: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    evaluation_criteria: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    resources_provided: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    # Progress Tracking
    completion_percentage: float = Field(default=0.0)
    milestones: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    current_milestone: Optional[str] = Field(default=None)

    # Communication
    project_channel_id: Optional[str] = Field(default=None)  # Chat/forum channel
    file_repository_url: Optional[str] = Field(default=None)

    # Evaluation
    peer_reviews_required: bool = Field(default=True)
    instructor_evaluation: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    final_grade: Optional[str] = Field(default=None)

    # Status
    status: str = Field(default="planning")  # planning, in_progress, review, completed
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserContribution(SQLModel, table=True):
    """Tracking user contributions to social learning"""
    __tablename__ = "user_contributions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)

    # Contribution Types
    contribution_type: str = Field(nullable=False)  # post, answer, project, mentoring, etc.
    target_type: str = Field(nullable=False)  # forum, project, user, etc.
    target_id: str = Field(nullable=False)

    # Impact Metrics
    upvotes_received: int = Field(default=0)
    helpful_votes: int = Field(default=0)
    views_generated: int = Field(default=0)
    responses_generated: int = Field(default=0)

    # Quality Metrics
    quality_score: float = Field(default=0.0)
    peer_rating: Optional[float] = Field(default=None)
    instructor_rating: Optional[float] = Field(default=None)

    # Learning Impact
    students_helped: int = Field(default=0)
    knowledge_shared: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    skills_demonstrated: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Rewards
    points_earned: int = Field(default=0)
    badges_unlocked: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)

class LearningCommunity(SQLModel, table=True):
    """Learning communities and interest groups"""
    __tablename__ = "learning_communities"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)

    # Community Focus
    primary_subject: str = Field(nullable=False)
    secondary_subjects: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    skill_levels: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Membership
    member_count: int = Field(default=0)
    is_public: bool = Field(default=True)
    membership_rules: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    # Activities
    regular_events: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    discussion_topics: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    shared_resources: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    # Governance
    moderators: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    community_guidelines: str = Field(default="")
    code_of_conduct: str = Field(default="")

    # Engagement Metrics
    activity_score: float = Field(default=0.0)
    average_member_engagement: float = Field(default=0.0)
    top_contributors: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    # Status
    is_active: bool = Field(default=True)
    founded_date: datetime = Field(default_factory=datetime.utcnow)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
