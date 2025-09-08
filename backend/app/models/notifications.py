import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field

class NotificationType(str, Enum):
    COURSE_UPDATE = "course_update"
    LESSON_AVAILABLE = "lesson_available"
    ASSIGNMENT_DUE = "assignment_due"
    GRADE_POSTED = "grade_posted"
    FORUM_REPLY = "forum_reply"
    STUDY_GROUP_INVITE = "study_group_invite"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    BADGE_EARNED = "badge_earned"
    AI_RECOMMENDATION = "ai_recommendation"
    PEER_LEARNING_SESSION = "peer_learning_session"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SECURITY_ALERT = "security_alert"
    SOCIAL_INTERACTION = "social_interaction"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class Notification(SQLModel, table=True):
    """User notifications"""
    __tablename__ = "notifications"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)

    # Notification Content
    title: str = Field(nullable=False)
    message: str = Field(nullable=False)
    notification_type: str = Field(default=NotificationType.COURSE_UPDATE.value)
    priority: str = Field(default=NotificationPriority.MEDIUM.value)

    # Associated Data
    related_entity_type: Optional[str] = Field(default=None)  # course, lesson, user, etc.
    related_entity_id: Optional[str] = Field(default=None)
    action_url: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Delivery Channels
    channels: List[str] = Field(default_factory=lambda: [NotificationChannel.IN_APP.value])

    # Status Tracking
    is_read: bool = Field(default=False)
    read_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)

    # Email/SMS specific
    email_sent: bool = Field(default=False)
    sms_sent: bool = Field(default=False)
    push_sent: bool = Field(default=False)

    # Scheduling
    scheduled_for: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    # Analytics
    clicked: bool = Field(default=False)
    action_taken: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationPreference(SQLModel, table=True):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True, nullable=False)

    # Channel Preferences
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=True)
    in_app_enabled: bool = Field(default=True)

    # Notification Type Preferences
    course_updates: bool = Field(default=True)
    lesson_notifications: bool = Field(default=True)
    assignment_reminders: bool = Field(default=True)
    grade_notifications: bool = Field(default=True)
    forum_activity: bool = Field(default=True)
    social_interactions: bool = Field(default=True)
    achievement_notifications: bool = Field(default=True)
    ai_recommendations: bool = Field(default=True)
    system_updates: bool = Field(default=True)
    marketing_emails: bool = Field(default=False)

    # Timing Preferences
    quiet_hours_start: Optional[str] = Field(default=None)  # "22:00"
    quiet_hours_end: Optional[str] = Field(default=None)    # "08:00"
    timezone: str = Field(default="UTC")

    # Frequency Settings
    digest_frequency: str = Field(default="immediate")  # immediate, daily, weekly
    batch_similar: bool = Field(default=True)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationTemplate(SQLModel, table=True):
    """Reusable notification templates"""
    __tablename__ = "notification_templates"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    notification_type: str = Field(nullable=False)

    # Template Content
    subject_template: str = Field(nullable=False)
    message_template: str = Field(nullable=False)
    action_button_text: Optional[str] = Field(default=None)

    # Variables (JSON schema for validation)
    variables_schema: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    language: str = Field(default="en")
    category: str = Field(default="general")
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationQueue(SQLModel, table=True):
    """Queued notifications for batch processing"""
    __tablename__ = "notification_queue"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Notification Data
    user_id: str = Field(index=True, nullable=False)
    notification_data: Dict[str, Any] = Field(nullable=False)

    # Processing
    channel: str = Field(nullable=False)
    priority: str = Field(default=NotificationPriority.MEDIUM.value)
    scheduled_for: datetime = Field(default_factory=datetime.utcnow)

    # Status
    status: str = Field(default="pending")  # pending, processing, sent, failed
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    last_attempt: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)

    # Batch Processing
    batch_id: Optional[str] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PushSubscription(SQLModel, table=True):
    """Web push notification subscriptions"""
    __tablename__ = "push_subscriptions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)

    # Push Subscription Data
    endpoint: str = Field(nullable=False)
    p256dh: str = Field(nullable=False)
    auth: str = Field(nullable=False)

    # Device Information
    user_agent: Optional[str] = Field(default=None)
    device_type: Optional[str] = Field(default=None)  # desktop, mobile, tablet
    browser: Optional[str] = Field(default=None)

    # Status
    is_active: bool = Field(default=True)
    last_used: Optional[datetime] = Field(default=None)
    failure_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationAnalytics(SQLModel, table=True):
    """Analytics for notification performance"""
    __tablename__ = "notification_analytics"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Time Period
    date: datetime = Field(nullable=False, index=True)
    period: str = Field(default="daily")  # daily, weekly, monthly

    # Metrics
    total_sent: int = Field(default=0)
    total_delivered: int = Field(default=0)
    total_read: int = Field(default=0)
    total_clicked: int = Field(default=0)
    total_actions: int = Field(default=0)

    # Channel Breakdown
    email_sent: int = Field(default=0)
    email_delivered: int = Field(default=0)
    email_opened: int = Field(default=0)
    email_clicked: int = Field(default=0)

    push_sent: int = Field(default=0)
    push_delivered: int = Field(default=0)
    push_clicked: int = Field(default=0)

    sms_sent: int = Field(default=0)
    sms_delivered: int = Field(default=0)

    in_app_sent: int = Field(default=0)
    in_app_read: int = Field(default=0)
    in_app_clicked: int = Field(default=0)

    # Performance Rates
    delivery_rate: float = Field(default=0.0)
    open_rate: float = Field(default=0.0)
    click_rate: float = Field(default=0.0)
    action_rate: float = Field(default=0.0)

    # Type Breakdown
    by_type: Dict[str, int] = Field(default_factory=dict)
    by_priority: Dict[str, int] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserNotificationStats(SQLModel, table=True):
    """Per-user notification statistics"""
    __tablename__ = "user_notification_stats"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True, nullable=False)

    # Overall Stats
    total_received: int = Field(default=0)
    total_read: int = Field(default=0)
    total_clicked: int = Field(default=0)
    total_actions: int = Field(default=0)

    # Engagement Rates
    read_rate: float = Field(default=0.0)
    click_rate: float = Field(default=0.0)
    action_rate: float = Field(default=0.0)

    # Channel Preferences
    preferred_channel: Optional[str] = Field(default=None)
    channel_effectiveness: Dict[str, float] = Field(default_factory=dict)

    # Timing Preferences
    best_send_hour: Optional[int] = Field(default=None)
    best_send_day: Optional[int] = Field(default=None)

    # Type Preferences
    most_engaged_types: List[str] = Field(default_factory=list)
    least_engaged_types: List[str] = Field(default_factory=list)

    # Recent Activity
    last_notification_date: Optional[datetime] = Field(default=None)
    notifications_this_week: int = Field(default=0)
    notifications_this_month: int = Field(default=0)

    updated_at: datetime = Field(default_factory=datetime.utcnow)
