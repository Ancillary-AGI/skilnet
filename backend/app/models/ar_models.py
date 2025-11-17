from .base_model import BaseModel
from app.core.database import Field
from enum import Enum
import uuid

class VRDeviceType(str, Enum):
    OCULUS_QUEST = "oculus_quest"
    HTC_VIVE = "htc_vive"
    VALVE_INDEX = "valve_index"
    PSVR = "psvr"
    WINDOWS_MR = "windows_mr"
    CARDBOARD = "cardboard"
    UNKNOWN = "unknown"

class VREnvironmentType(str, Enum):
    CLASSROOM = "classroom"
    LABORATORY = "laboratory"
    NATURE = "nature"
    SPACE = "space"
    HISTORICAL = "historical"
    FUTURISTIC = "futuristic"
    CUSTOM = "custom"

class VRSession(BaseModel):
    _table_name = "vr_sessions"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'course_id': Field('TEXT', index=True),
        'lesson_id': Field('TEXT', index=True),
        'device_type': Field('TEXT', default=VRDeviceType.UNKNOWN),
        'environment_type': Field('TEXT', default=VREnvironmentType.CLASSROOM),
        'session_duration_minutes': Field('INTEGER', default=0),
        'motion_sickness_level': Field('INTEGER'),  # 1-10 scale
        'comfort_rating': Field('INTEGER'),  # 1-5 stars
        'interactions_count': Field('INTEGER', default=0),
        'objects_manipulated': Field('INTEGER', default=0),
        'spatial_understanding_score': Field('REAL'),
        'performance_metrics': Field('JSON', default={}),
        'started_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'ended_at': Field('TIMESTAMP'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class ARExperience(BaseModel):
    _table_name = "ar_experiences"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'course_id': Field('TEXT', nullable=False, index=True),
        'lesson_id': Field('TEXT', index=True),
        'name': Field('TEXT', nullable=False),
        'description': Field('TEXT'),
        'marker_type': Field('TEXT'),  # image, object, location
        'marker_data': Field('JSON'),
        'ar_content_url': Field('TEXT'),
        'interactivity_level': Field('TEXT'),  # low, medium, high
        'required_device_capabilities': Field('JSON', default=[]),
        'compatibility_notes': Field('TEXT'),
        'usage_count': Field('INTEGER', default=0),
        'average_rating': Field('REAL', default=0.0),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class SpatialAudioSession(BaseModel):
    _table_name = "spatial_audio_sessions"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'course_id': Field('TEXT', index=True),
        'lesson_id': Field('TEXT', index=True),
        'audio_quality_rating': Field('INTEGER'),  # 1-5 stars
        'spatial_accuracy_rating': Field('INTEGER'),  # 1-5 stars
        'immersion_level': Field('INTEGER'),  # 1-10 scale
        'session_duration_minutes': Field('INTEGER', default=0),
        'audio_events_triggered': Field('INTEGER', default=0),
        'started_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'ended_at': Field('TIMESTAMP'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }