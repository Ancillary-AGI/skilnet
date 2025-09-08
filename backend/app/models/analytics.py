import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field

class AnalyticsEventType(str, Enum):
    PAGE_VIEW = "page_view"
    LESSON_START = "lesson_start"
    LESSON_COMPLETE = "lesson_complete"
    QUIZ_ATTEMPT = "quiz_attempt"
    QUIZ_COMPLETE = "quiz_complete"
    VIDEO_PLAY = "video_play"
    VIDEO_PAUSE = "video_pause"
    VIDEO_COMPLETE = "video_complete"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    SEARCH = "search"
    SOCIAL_INTERACTION = "social_interaction"
    VR_AR_SESSION = "vr_ar_session"
    AI_INTERACTION = "ai_interaction"
    GAMIFICATION_EVENT = "gamification_event"

class LearningMetricType(str, Enum):
    TIME_SPENT = "time_spent"
    COMPLETION_RATE = "completion_rate"
    QUIZ_SCORE = "quiz_score"
    ENGAGEMENT_SCORE = "engagement_score"
    RETENTION_RATE = "retention_rate"
    PROGRESS_VELOCITY = "progress_velocity"
    LEARNING_EFFICIENCY = "learning_efficiency"

class AnalyticsEvent(SQLModel, table=True):
    """Raw analytics events for detailed tracking"""
    __tablename__ = "analytics_events"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: Optional[str] = Field(default=None, index=True)
    session_id: str = Field(nullable=False, index=True)

    # Event Details
    event_type: str = Field(nullable=False)
    event_name: str = Field(nullable=False)
    event_data: Dict[str, Any] = Field(default_factory=dict)

    # Context
    page_url: Optional[str] = Field(default=None)
    referrer: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)

    # Device Information
    device_type: Optional[str] = Field(default=None)
    device_os: Optional[str] = Field(default=None)
    browser: Optional[str] = Field(default=None)
    screen_resolution: Optional[str] = Field(default=None)

    # Geographic Information
    ip_address: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    timezone: Optional[str] = Field(default=None)

    # Learning Context
    course_id: Optional[str] = Field(default=None, index=True)
    lesson_id: Optional[str] = Field(default=None, index=True)
    module_id: Optional[str] = Field(default=None)

    # Timing
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_start: datetime = Field(default_factory=datetime.utcnow)
    time_on_page: Optional[int] = Field(default=None)  # seconds

    # Performance Metrics
    load_time: Optional[float] = Field(default=None)  # milliseconds
    interaction_count: int = Field(default=0)
    error_count: int = Field(default=0)

class UserLearningAnalytics(SQLModel, table=True):
    """Aggregated learning analytics per user"""
    __tablename__ = "user_learning_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True, nullable=False)

    # Time Tracking
    total_learning_time: int = Field(default=0)  # minutes
    average_session_duration: int = Field(default=0)  # minutes
    longest_session_duration: int = Field(default=0)  # minutes
    sessions_this_week: int = Field(default=0)
    sessions_this_month: int = Field(default=0)

    # Course Progress
    courses_enrolled: int = Field(default=0)
    courses_completed: int = Field(default=0)
    lessons_completed: int = Field(default=0)
    average_completion_rate: float = Field(default=0.0)

    # Assessment Performance
    quizzes_taken: int = Field(default=0)
    average_quiz_score: float = Field(default=0.0)
    highest_quiz_score: float = Field(default=0.0)
    perfect_scores: int = Field(default=0)

    # Learning Patterns
    preferred_learning_times: List[str] = Field(default_factory=list)  # hour ranges
    preferred_days: List[str] = Field(default_factory=list)  # weekdays
    learning_streak_current: int = Field(default=0)
    learning_streak_longest: int = Field(default=0)

    # Engagement Metrics
    total_page_views: int = Field(default=0)
    total_video_views: int = Field(default=0)
    total_downloads: int = Field(default=0)
    forum_posts: int = Field(default=0)
    forum_replies: int = Field(default=0)

    # VR/AR Usage
    vr_sessions_count: int = Field(default=0)
    ar_sessions_count: int = Field(default=0)
    total_vr_time: int = Field(default=0)  # minutes
    total_ar_time: int = Field(default=0)  # minutes

    # AI Interactions
    ai_questions_asked: int = Field(default=0)
    ai_hints_used: int = Field(default=0)
    ai_recommendations_viewed: int = Field(default=0)
    ai_recommendations_implemented: int = Field(default=0)

    # Social Learning
    study_groups_joined: int = Field(default=0)
    peer_sessions_attended: int = Field(default=0)
    collaborative_projects: int = Field(default=0)

    # Gamification
    points_earned: int = Field(default=0)
    badges_earned: int = Field(default=0)
    achievements_unlocked: int = Field(default=0)
    leaderboard_rankings: Dict[str, int] = Field(default_factory=dict)

    # Learning Goals
    weekly_goal_hours: int = Field(default=0)
    monthly_goal_hours: int = Field(default=0)
    weekly_goal_achieved: bool = Field(default=False)
    monthly_goal_achieved: bool = Field(default=False)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseAnalytics(SQLModel, table=True):
    """Analytics for individual courses"""
    __tablename__ = "course_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    course_id: str = Field(unique=True, index=True, nullable=False)

    # Enrollment Metrics
    total_enrollments: int = Field(default=0)
    active_enrollments: int = Field(default=0)
    completion_rate: float = Field(default=0.0)
    average_completion_time: int = Field(default=0)  # days

    # Engagement Metrics
    total_views: int = Field(default=0)
    unique_viewers: int = Field(default=0)
    average_session_duration: int = Field(default=0)  # minutes
    bounce_rate: float = Field(default=0.0)

    # Content Performance
    lesson_completion_rates: Dict[str, float] = Field(default_factory=dict)
    quiz_average_scores: Dict[str, float] = Field(default_factory=dict)
    most_viewed_lessons: List[Dict[str, Any]] = Field(default_factory=list)
    least_viewed_lessons: List[Dict[str, Any]] = Field(default_factory=list)

    # Assessment Analytics
    total_quiz_attempts: int = Field(default=0)
    average_quiz_score: float = Field(default=0.0)
    quiz_pass_rate: float = Field(default=0.0)
    quiz_retake_rate: float = Field(default=0.0)

    # Time-based Analytics
    enrollments_by_month: Dict[str, int] = Field(default_factory=dict)
    completions_by_month: Dict[str, int] = Field(default_factory=dict)
    peak_usage_hours: List[int] = Field(default_factory=list)

    # Demographic Data
    learner_demographics: Dict[str, Any] = Field(default_factory=dict)
    geographic_distribution: Dict[str, int] = Field(default_factory=dict)

    # Rating and Feedback
    average_rating: float = Field(default=0.0)
    total_reviews: int = Field(default=0)
    rating_distribution: Dict[str, int] = Field(default_factory=dict)

    # Retention Metrics
    day_1_retention: float = Field(default=0.0)
    day_7_retention: float = Field(default=0.0)
    day_30_retention: float = Field(default=0.0)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SystemAnalytics(SQLModel, table=True):
    """System-wide analytics and performance metrics"""
    __tablename__ = "system_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    date: datetime = Field(nullable=False, index=True)
    period: str = Field(default="daily")  # daily, weekly, monthly

    # User Metrics
    total_users: int = Field(default=0)
    active_users: int = Field(default=0)
    new_registrations: int = Field(default=0)
    returning_users: int = Field(default=0)

    # Learning Activity
    total_sessions: int = Field(default=0)
    total_learning_time: int = Field(default=0)  # minutes
    courses_completed: int = Field(default=0)
    lessons_completed: int = Field(default=0)
    quizzes_taken: int = Field(default=0)

    # Content Metrics
    total_courses: int = Field(default=0)
    total_lessons: int = Field(default=0)
    total_enrollments: int = Field(default=0)
    average_course_rating: float = Field(default=0.0)

    # Platform Usage
    page_views: int = Field(default=0)
    unique_visitors: int = Field(default=0)
    api_requests: int = Field(default=0)
    average_response_time: float = Field(default=0.0)  # milliseconds

    # Device and Platform
    desktop_users: int = Field(default=0)
    mobile_users: int = Field(default=0)
    tablet_users: int = Field(default=0)
    vr_users: int = Field(default=0)

    # Geographic Distribution
    top_countries: List[Dict[str, Any]] = Field(default_factory=list)
    user_locations: Dict[str, int] = Field(default_factory=dict)

    # Error Tracking
    total_errors: int = Field(default=0)
    error_rate: float = Field(default=0.0)
    top_errors: List[Dict[str, Any]] = Field(default_factory=list)

    # Performance Metrics
    server_response_time: float = Field(default=0.0)
    database_query_time: float = Field(default=0.0)
    cache_hit_rate: float = Field(default=0.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)

class LearningPathAnalytics(SQLModel, table=True):
    """Analytics for personalized learning paths"""
    __tablename__ = "learning_path_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    learning_path_id: str = Field(index=True, nullable=False)

    # Path Progress
    current_position: int = Field(default=0)
    total_steps: int = Field(nullable=False)
    completion_percentage: float = Field(default=0.0)
    estimated_completion_date: Optional[datetime] = Field(default=None)

    # Performance Metrics
    average_score: float = Field(default=0.0)
    time_spent: int = Field(default=0)  # minutes
    skills_improved: List[str] = Field(default_factory=list)

    # Adaptation Data
    difficulty_adjustments: int = Field(default=0)
    content_switches: int = Field(default=0)
    pace_changes: int = Field(default=0)

    # Engagement
    sessions_completed: int = Field(default=0)
    average_session_length: int = Field(default=0)
    consistency_score: float = Field(default=0.0)

    # Outcomes
    skills_achieved: List[str] = Field(default_factory=list)
    certificates_earned: List[str] = Field(default_factory=list)
    goals_met: List[str] = Field(default_factory=list)

    # AI Insights
    recommended_adjustments: List[Dict[str, Any]] = Field(default_factory=list)
    predicted_completion_date: Optional[datetime] = Field(default=None)
    risk_factors: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContentEngagementAnalytics(SQLModel, table=True):
    """Detailed analytics for content engagement"""
    __tablename__ = "content_engagement_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    content_type: str = Field(nullable=False)  # course, lesson, quiz, video
    content_id: str = Field(nullable=False, index=True)

    # Engagement Metrics
    total_views: int = Field(default=0)
    unique_viewers: int = Field(default=0)
    average_view_duration: int = Field(default=0)  # seconds
    completion_rate: float = Field(default=0.0)

    # Interaction Data
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)
    shares: int = Field(default=0)
    bookmarks: int = Field(default=0)
    downloads: int = Field(default=0)

    # Time-based Analytics
    views_by_hour: Dict[str, int] = Field(default_factory=dict)
    views_by_day: Dict[str, int] = Field(default_factory=dict)
    peak_engagement_times: List[str] = Field(default_factory=list)

    # User Segmentation
    new_user_views: int = Field(default=0)
    returning_user_views: int = Field(default=0)
    paid_user_views: int = Field(default=0)
    free_user_views: int = Field(default=0)

    # Device Analytics
    desktop_views: int = Field(default=0)
    mobile_views: int = Field(default=0)
    tablet_views: int = Field(default=0)
    vr_views: int = Field(default=0)

    # Geographic Analytics
    top_viewing_countries: List[Dict[str, Any]] = Field(default_factory=list)
    regional_engagement: Dict[str, float] = Field(default_factory=dict)

    # Quality Metrics
    average_rating: float = Field(default=0.0)
    helpfulness_score: float = Field(default=0.0)
    reported_issues: int = Field(default=0)

    # Performance Insights
    drop_off_points: List[Dict[str, Any]] = Field(default_factory=list)
    engagement_peaks: List[Dict[str, Any]] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PredictiveAnalytics(SQLModel, table=True):
    """AI-powered predictive analytics for user behavior"""
    __tablename__ = "predictive_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)

    # Churn Prediction
    churn_probability: float = Field(default=0.0)
    churn_risk_level: str = Field(default="low")  # low, medium, high
    predicted_churn_date: Optional[datetime] = Field(default=None)
    churn_factors: List[str] = Field(default_factory=list)

    # Engagement Prediction
    engagement_score: float = Field(default=0.0)
    predicted_active_days: int = Field(default=0)
    engagement_trend: str = Field(default="stable")  # increasing, decreasing, stable

    # Learning Prediction
    predicted_completion_rate: float = Field(default=0.0)
    estimated_completion_date: Optional[datetime] = Field(default=None)
    learning_velocity: float = Field(default=0.0)
    at_risk_subjects: List[str] = Field(default_factory=list)

    # Recommendation Engine
    recommended_courses: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_actions: List[Dict[str, Any]] = Field(default_factory=list)
    personalized_study_plan: Dict[str, Any] = Field(default_factory=dict)

    # Performance Insights
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)

    # Intervention Suggestions
    suggested_interventions: List[Dict[str, Any]] = Field(default_factory=list)
    optimal_study_times: List[str] = Field(default_factory=list)
    recommended_difficulty: str = Field(default="medium")

    # Model Metadata
    prediction_model_version: str = Field(default="1.0")
    confidence_score: float = Field(default=0.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    created_at: datetime = Field(default_factory=datetime.utcnow)
