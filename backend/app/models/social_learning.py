from .base_model import BaseModel
from ..core.database import Field
from enum import Enum
import uuid

class StudyGroupStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CollaborationType(str, Enum):
    STUDY_GROUP = "study_group"
    PROJECT_TEAM = "project_team"
    PEER_REVIEW = "peer_review"
    MENTORSHIP = "mentorship"
    DISCUSSION = "discussion"

class StudyGroup(BaseModel):
    _table_name = "study_groups"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'name': Field('TEXT', nullable=False),
        'description': Field('TEXT'),
        'course_id': Field('TEXT', index=True),
        'created_by': Field('TEXT', nullable=False, index=True),
        'max_members': Field('INTEGER', default=10),
        'current_members': Field('INTEGER', default=1),
        'status': Field('TEXT', default=StudyGroupStatus.ACTIVE),
        'meeting_schedule': Field('JSON'),  # {days: [], time: "", timezone: ""}
        'preferred_platform': Field('TEXT'),  # vr, video, chat
        'tags': Field('JSON', default=[]),
        'is_public': Field('BOOLEAN', default=True),
        'join_code': Field('TEXT'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class StudyGroupMember(BaseModel):
    _table_name = "study_group_members"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'study_group_id': Field('TEXT', nullable=False, index=True),
        'user_id': Field('TEXT', nullable=False, index=True),
        'role': Field('TEXT', default="member"),  # owner, moderator, member
        'joined_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'last_active': Field('TIMESTAMP'),
        'contribution_score': Field('REAL', default=0.0),
        'is_active': Field('BOOLEAN', default=True),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class PeerReview(BaseModel):
    _table_name = "peer_reviews"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'reviewer_id': Field('TEXT', nullable=False, index=True),
        'reviewee_id': Field('TEXT', nullable=False, index=True),
        'submission_id': Field('TEXT', index=True),
        'course_id': Field('TEXT', index=True),
        'rating': Field('REAL'),  # 1-5 scale
        'feedback': Field('TEXT'),
        'rubric_scores': Field('JSON'),  # {criteria: score}
        'is_anonymous': Field('BOOLEAN', default=False),
        'helpfulness_score': Field('REAL'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class LearningCommunity(BaseModel):
    _table_name = "learning_communities"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'name': Field('TEXT', nullable=False),
        'description': Field('TEXT'),
        'topic': Field('TEXT'),
        'created_by': Field('TEXT', nullable=False, index=True),
        'member_count': Field('INTEGER', default=1),
        'is_public': Field('BOOLEAN', default=True),
        'moderation_level': Field('TEXT', default="relaxed"),
        'weekly_digest_enabled': Field('BOOLEAN', default=True),
        'tags': Field('JSON', default=[]),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }