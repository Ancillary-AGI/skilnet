from .base_model import BaseModel
from ..core.database import Field
from enum import Enum
import uuid

class NotificationType(str, Enum):
    COURSE_UPDATE = "course_update"
    ASSIGNMENT_DUE = "assignment_due"
    LIVE_CLASS_STARTING = "live_class_starting"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    NEW_MESSAGE = "new_message"
    FRIEND_REQUEST = "friend_request"
    STUDY_REMINDER = "study_reminder"
    BREAK_REMINDER = "break_reminder"
    WELLNESS_CHECK = "wellness_check"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SECURITY_ALERT = "security_alert"
    CONTENT_RECOMMENDATION = "content_recommendation"
    SOCIAL_ACTIVITY = "social_activity"
    CERTIFICATE_READY = "certificate_ready"
    VR_SESSION_INVITE = "vr_session_invite"
    AI_TUTOR_INSIGHT = "ai_tutor_insight"

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(BaseModel):
    _table_name = "notifications"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'type': Field('TEXT', nullable=False),
        'title': Field('TEXT', nullable=False),
        'message': Field('TEXT', nullable=False),
        'rich_content': Field('JSON', default={}),
        'priority': Field('TEXT', default=NotificationPriority.NORMAL),
        'category': Field('TEXT'),
        'tags': Field('JSON', default=[]),
        'channels': Field('JSON', default=[]),
        'scheduled_for': Field('TIMESTAMP'),
        'expires_at': Field('TIMESTAMP'),
        'is_read': Field('BOOLEAN', default=False),
        'is_delivered': Field('BOOLEAN', default=False),
        'delivery_attempts': Field('INTEGER', default=0),
        'last_delivery_attempt': Field('TIMESTAMP'),
        'clicked': Field('BOOLEAN', default=False),
        'clicked_at': Field('TIMESTAMP'),
        'action_taken': Field('TEXT'),
        'language': Field('TEXT', default="en"),
        'related_entity_type': Field('TEXT'),
        'related_entity_id': Field('TEXT'),
        'push_notification_id': Field('TEXT'),
        'email_message_id': Field('TEXT'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'read_at': Field('TIMESTAMP')
    }

class NotificationPreference(BaseModel):
    _table_name = "notification_preferences"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, unique=True, index=True),
        'notifications_enabled': Field('BOOLEAN', default=True),
        'quiet_hours_enabled': Field('BOOLEAN', default=False),
        'quiet_hours_start': Field('TEXT', default="22:00"),
        'quiet_hours_end': Field('TEXT', default="08:00"),
        'timezone': Field('TEXT', default="UTC"),
        'email_enabled': Field('BOOLEAN', default=True),
        'push_enabled': Field('BOOLEAN', default=True),
        'sms_enabled': Field('BOOLEAN', default=False),
        'in_app_enabled': Field('BOOLEAN', default=True),
        'course_updates': Field('JSON', default={"email": True, "push": True, "in_app": True}),
        'assignments': Field('JSON', default={"email": True, "push": True, "in_app": True}),
        'live_classes': Field('JSON', default={"email": True, "push": True, "in_app": True}),
        'achievements': Field('JSON', default={"email": False, "push": True, "in_app": True}),
        'payments': Field('JSON', default={"email": True, "push": True, "in_app": True}),
        'social': Field('JSON', default={"email": False, "push": True, "in_app": True}),
        'wellness': Field('JSON', default={"email": False, "push": True, "in_app": True}),
        'security': Field('JSON', default={"email": True, "push": True, "in_app": True}),
        'digest_frequency': Field('TEXT', default="daily"),
        'digest_time': Field('TEXT', default="09:00"),
        'device_tokens': Field('JSON', default=[]),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class NotificationTemplate(BaseModel):
    _table_name = "notification_templates"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'type': Field('TEXT', nullable=False),
        'channel': Field('TEXT', nullable=False),
        'language': Field('TEXT', default="en"),
        'version': Field('INTEGER', default=1),
        'subject_template': Field('TEXT'),
        'title_template': Field('TEXT', nullable=False),
        'message_template': Field('TEXT', nullable=False),
        'html_template': Field('TEXT'),
        'required_variables': Field('JSON', default=[]),
        'optional_variables': Field('JSON', default=[]),
        'style_config': Field('JSON', default={}),
        'is_active': Field('BOOLEAN', default=True),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class NotificationCampaign(BaseModel):
    _table_name = "notification_campaigns"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'name': Field('TEXT', nullable=False),
        'description': Field('TEXT'),
        'target_audience': Field('JSON'),  # {criteria: value}
        'notification_template_id': Field('TEXT'),
        'scheduled_time': Field('TIMESTAMP'),
        'timezone': Field('TEXT', default="UTC"),
        'status': Field('TEXT', default="draft"),  # draft, scheduled, running, completed, cancelled
        'total_recipients': Field('INTEGER', default=0),
        'successful_deliveries': Field('INTEGER', default=0),
        'failed_deliveries': Field('INTEGER', default=0),
        'open_rate': Field('REAL', default=0.0),
        'click_rate': Field('REAL', default=0.0),
        'conversion_rate': Field('REAL', default=0.0),
        'created_by': Field('TEXT', nullable=False),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class NotificationQueue(BaseModel):
    _table_name = "notification_queue"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'notification_id': Field('TEXT', index=True),
        'user_id': Field('TEXT', nullable=False, index=True),
        'channel': Field('TEXT', nullable=False),
        'priority': Field('INTEGER', default=5),
        'status': Field('TEXT', default="pending"),  # pending, processing, sent, failed
        'attempts': Field('INTEGER', default=0),
        'max_attempts': Field('INTEGER', default=3),
        'scheduled_for': Field('TIMESTAMP', nullable=False),
        'next_attempt': Field('TIMESTAMP'),
        'last_error': Field('TEXT'),
        'error_count': Field('INTEGER', default=0),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'processed_at': Field('TIMESTAMP')
    }