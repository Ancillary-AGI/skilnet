from .base_model import BaseModel
from ..core.database import Field
from enum import Enum
import uuid

class AITutorPersona(str, Enum):
    FRIENDLY_MENTOR = "friendly_mentor"
    TECHNICAL_EXPERT = "technical_expert"
    MOTIVATIONAL_COACH = "motivational_coach"
    SOCRATIC_TEACHER = "socratic_teacher"
    ADAPTIVE_LEARNER = "adaptive_learner"

class AIConversationType(str, Enum):
    EXPLANATION = "explanation"
    QUIZ = "quiz"
    HINT = "hint"
    FEEDBACK = "feedback"
    MOTIVATION = "motivation"
    CLARIFICATION = "clarification"

class AITutorSession(BaseModel):
    _table_name = "ai_tutor_sessions"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'course_id': Field('TEXT', index=True),
        'lesson_id': Field('TEXT', index=True),
        'persona': Field('TEXT', default=AITutorPersona.FRIENDLY_MENTOR),
        'conversation_history': Field('JSON', default=[]),
        'learning_style_adapted': Field('BOOLEAN', default=False),
        'difficulty_level': Field('TEXT', default="medium"),
        'session_duration_minutes': Field('INTEGER', default=0),
        'questions_asked': Field('INTEGER', default=0),
        'hints_provided': Field('INTEGER', default=0),
        'explanations_given': Field('INTEGER', default=0),
        'user_satisfaction_rating': Field('REAL'),
        'effectiveness_score': Field('REAL'),
        'started_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'ended_at': Field('TIMESTAMP'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class AIContentGeneration(BaseModel):
    _table_name = "ai_content_generations"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'instructor_id': Field('TEXT', nullable=False, index=True),
        'course_id': Field('TEXT', index=True),
        'content_type': Field('TEXT', nullable=False),
        'prompt': Field('TEXT', nullable=False),
        'generated_content': Field('JSON'),
        'ai_model': Field('TEXT'),
        'model_version': Field('TEXT'),
        'quality_score': Field('REAL'),
        'relevance_score': Field('REAL'),
        'needs_human_review': Field('BOOLEAN', default=True),
        'approved': Field('BOOLEAN', default=False),
        'reviewer_notes': Field('TEXT'),
        'generation_time_seconds': Field('REAL'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }

class AILearningPath(BaseModel):
    _table_name = "ai_learning_paths"
    _columns = {
        'id': Field('TEXT', primary_key=True, default=lambda: str(uuid.uuid4())),
        'user_id': Field('TEXT', nullable=False, index=True),
        'learning_goals': Field('JSON', default=[]),
        'current_skill_level': Field('TEXT'),
        'target_skill_level': Field('TEXT'),
        'recommended_courses': Field('JSON', default=[]),
        'estimated_completion_time_hours': Field('REAL'),
        'progress_percentage': Field('REAL', default=0.0),
        'adaptation_frequency': Field('TEXT', default="weekly"),
        'last_adapted': Field('TIMESTAMP'),
        'effectiveness_score': Field('REAL'),
        'created_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP'),
        'updated_at': Field('TIMESTAMP', default='CURRENT_TIMESTAMP')
    }