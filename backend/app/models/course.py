from .base_model import BaseModel, Relationship, RelationshipType
from ..core.database import Field
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    INTERACTIVE = "interactive"
    VR_EXPERIENCE = "vr_experience"
    AR_EXPERIENCE = "ar_experience"
    AI_SIMULATION = "ai_simulation"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    LIVE_CLASS = "live_class"
    PODCAST = "podcast"
    CODE_EXERCISE = "code_exercise"
    WHITEBOARD = "whiteboard"

class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"

class Course(BaseModel):
    _table_name = "courses"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'title': Field('TEXT', nullable=False),
        'slug': Field('TEXT', unique=True, nullable=False, index=True),
        'description': Field('TEXT'),
        'short_description': Field('TEXT'),
        'instructor_id': Field('TEXT', nullable=False, index=True),
        'category': Field('TEXT', index=True),
        'subcategory': Field('TEXT', index=True),
        'tags': Field('JSON', default=[]),
        'language': Field('TEXT', default="en"),
        'difficulty_level': Field('TEXT', default=DifficultyLevel.BEGINNER),
        'estimated_duration_hours': Field('REAL', default=0.0),
        'price': Field('REAL', default=0.0),
        'currency': Field('TEXT', default='USD'),
        'thumbnail_url': Field('TEXT'),
        'trailer_video_url': Field('TEXT'),
        'course_materials': Field('JSON', default=[]),
        'vr_environment_id': Field('TEXT'),
        'ar_markers': Field('JSON', default=[]),
        'spatial_audio_enabled': Field('BOOLEAN', default=False),
        'haptic_feedback_enabled': Field('BOOLEAN', default=False),
        'ai_tutor_enabled': Field('BOOLEAN', default=False),
        'ai_difficulty_adaptation': Field('BOOLEAN', default=False),
        'ai_content_generation': Field('BOOLEAN', default=False),
        'status': Field('TEXT', default=CourseStatus.DRAFT),
        'is_featured': Field('BOOLEAN', default=False),
        'enrollment_count': Field('INTEGER', default=0),
        'average_rating': Field('REAL', default=0.0),
        'total_reviews': Field('INTEGER', default=0),
        'completion_rate': Field('REAL', default=0.0),
        'learning_objectives': Field('JSON', default=[]),
        'prerequisites': Field('JSON', default=[]),
        'skills_gained': Field('JSON', default=[]),
        'certificate_enabled': Field('BOOLEAN', default=False),
        'certificate_template_id': Field('TEXT'),
        'ar_content_id': Field('TEXT'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'published_at': Field('TIMESTAMP')
    }
    
    # Relationships
    _relationships = {
        'category': Relationship(
            model_class='Category',
            relationship_type=RelationshipType.MANY_TO_ONE,
            foreign_key='category_id',
            local_key='id'
        ),
    }

class Lesson(BaseModel):
    _table_name = "lessons"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'module_id': Field('TEXT', nullable=False, index=True),
        'title': Field('TEXT', nullable=False),
        'description': Field('TEXT'),
        'content_type': Field('TEXT', nullable=False),
        'order_index': Field('INTEGER', nullable=False),
        'video_url': Field('TEXT'),
        'text_content': Field('TEXT'),
        'interactive_content': Field('JSON'),
        'vr_scene_url': Field('TEXT'),
        'ar_model_url': Field('TEXT'),
        'spatial_audio_url': Field('TEXT'),
        'haptic_patterns': Field('JSON'),
        'ai_generated': Field('BOOLEAN', default=False),
        'ai_model_version': Field('TEXT'),
        'ai_generation_prompt': Field('TEXT'),
        'duration_minutes': Field('INTEGER'),
        'is_free': Field('BOOLEAN', default=False),
        'requires_vr': Field('BOOLEAN', default=False),
        'requires_ar': Field('BOOLEAN', default=False),
        'has_quiz': Field('BOOLEAN', default=False),
        'quiz_questions': Field('JSON', default=[]),
        'passing_score': Field('REAL', default=70.0),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class Enrollment(BaseModel):
    _table_name = "enrollments"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'course_id': Field('TEXT', nullable=False, index=True),
        'enrolled_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'completed_at': Field('TIMESTAMP'),
        'progress_percentage': Field('REAL', default=0.0),
        'payment_amount': Field('REAL', default=0.0),
        'payment_currency': Field('TEXT'),
        'payment_method': Field('TEXT'),
        'total_time_spent_minutes': Field('INTEGER', default=0),
        'last_accessed': Field('TIMESTAMP'),
        'completion_certificate_url': Field('TEXT'),
        'vr_sessions_count': Field('INTEGER', default=0),
        'ar_sessions_count': Field('INTEGER', default=0),
        'total_vr_time_minutes': Field('INTEGER', default=0),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class LessonProgress(BaseModel):
    _table_name = "lesson_progress"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'enrollment_id': Field('TEXT', nullable=False, index=True),
        'lesson_id': Field('TEXT', nullable=False, index=True),
        'is_completed': Field('BOOLEAN', default=False),
        'completion_percentage': Field('REAL', default=0.0),
        'time_spent_minutes': Field('INTEGER', default=0),
        'quiz_score': Field('REAL'),
        'quiz_attempts': Field('INTEGER', default=0),
        'best_quiz_score': Field('REAL'),
        'vr_interactions_count': Field('INTEGER', default=0),
        'ar_objects_manipulated': Field('INTEGER', default=0),
        'spatial_understanding_score': Field('REAL'),
        'ai_questions_asked': Field('INTEGER', default=0),
        'ai_hints_used': Field('INTEGER', default=0),
        'ai_feedback_rating': Field('REAL'),
        'started_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'completed_at': Field('TIMESTAMP'),
        'last_accessed': Field('TIMESTAMP'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class CourseReview(BaseModel):
    _table_name = "course_reviews"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'course_id': Field('TEXT', nullable=False, index=True),
        'rating': Field('REAL', default=0.0),
        'title': Field('TEXT'),
        'content': Field('TEXT'),
        'content_quality_rating': Field('REAL'),
        'instructor_rating': Field('REAL'),
        'value_for_money_rating': Field('REAL'),
        'vr_experience_rating': Field('REAL'),
        'ai_tutor_rating': Field('REAL'),
        'is_verified_purchase': Field('BOOLEAN', default=False),
        'helpful_votes': Field('INTEGER', default=0),
        'total_votes': Field('INTEGER', default=0),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }