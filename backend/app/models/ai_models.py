import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"

class AIModelType(str, Enum):
    TEXT_GENERATION = "text_generation"
    TEXT_EMBEDDING = "text_embedding"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    SPEECH_RECOGNITION = "speech_recognition"
    SPEECH_SYNTHESIS = "speech_synthesis"
    CODE_GENERATION = "code_generation"
    QUESTION_ANSWERING = "question_answering"

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

class AIModel(SQLModel, table=True):
    """AI models available in the system"""
    __tablename__ = "ai_models"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    provider: str = Field(default=AIProvider.OPENAI.value)
    model_type: str = Field(default=AIModelType.TEXT_GENERATION.value)
    model_version: str = Field(nullable=False)

    # Configuration
    api_endpoint: Optional[str] = Field(default=None)
    api_key_required: bool = Field(default=True)
    max_tokens: Optional[int] = Field(default=None)
    temperature: float = Field(default=0.7)
    parameters: Dict[str, Any] = Field(default_factory=dict)

    # Capabilities
    supported_languages: List[str] = Field(default_factory=lambda: ["en"])
    max_input_length: Optional[int] = Field(default=None)
    supports_streaming: bool = Field(default=False)

    # Usage Limits
    rate_limit_per_minute: int = Field(default=60)
    max_requests_per_day: Optional[int] = Field(default=None)
    cost_per_token: Optional[float] = Field(default=None)

    # Status
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AITutor(SQLModel, table=True):
    """AI tutor configurations for courses and lessons"""
    __tablename__ = "ai_tutors"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Associated Content
    course_id: Optional[str] = Field(default=None, index=True)
    lesson_id: Optional[str] = Field(default=None, index=True)

    # AI Configuration
    model_id: str = Field(nullable=False)
    system_prompt: str = Field(nullable=False)
    personality_traits: Dict[str, Any] = Field(default_factory=dict)

    # Capabilities
    can_answer_questions: bool = Field(default=True)
    can_provide_hints: bool = Field(default=True)
    can_generate_examples: bool = Field(default=True)
    can_assess_understanding: bool = Field(default=True)
    can_adapt_difficulty: bool = Field(default=True)

    # Learning Style Support
    supported_learning_styles: List[str] = Field(default_factory=list)
    preferred_style: Optional[str] = Field(default=None)

    # Interaction Limits
    max_questions_per_session: int = Field(default=50)
    max_hints_per_lesson: int = Field(default=10)
    response_delay_seconds: float = Field(default=1.0)

    # Analytics
    total_interactions: int = Field(default=0)
    average_rating: float = Field(default=0.0)
    helpfulness_score: float = Field(default=0.0)

    # Status
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AIInteraction(SQLModel, table=True):
    """User interactions with AI tutors"""
    __tablename__ = "ai_interactions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    ai_tutor_id: str = Field(index=True, nullable=False)

    # Interaction Details
    user_message: str = Field(nullable=False)
    ai_response: str = Field(nullable=False)
    interaction_type: str = Field(default="question")  # question, hint_request, feedback, etc.

    # Context
    lesson_id: Optional[str] = Field(default=None)
    course_id: Optional[str] = Field(default=None)
    session_id: str = Field(nullable=False)  # Group interactions in sessions

    # AI Processing
    tokens_used: int = Field(default=0)
    processing_time_seconds: float = Field(default=0.0)
    confidence_score: Optional[float] = Field(default=None)

    # User Feedback
    user_rating: Optional[int] = Field(default=None)  # 1-5 scale
    was_helpful: Optional[bool] = Field(default=None)
    feedback_text: Optional[str] = Field(default=None)

    # Learning Analytics
    learning_style_detected: Optional[str] = Field(default=None)
    difficulty_level: Optional[str] = Field(default=None)
    knowledge_gap_identified: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

class AdaptiveLearningProfile(SQLModel, table=True):
    """User learning profiles for AI adaptation"""
    __tablename__ = "adaptive_learning_profiles"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True, nullable=False)

    # Learning Style Analysis
    primary_learning_style: str = Field(default=LearningStyle.VISUAL.value)
    secondary_learning_style: Optional[str] = Field(default=None)
    learning_style_confidence: float = Field(default=0.0)

    # Performance Metrics
    average_quiz_score: float = Field(default=0.0)
    preferred_difficulty: str = Field(default="medium")
    optimal_pace: str = Field(default="moderate")  # slow, moderate, fast

    # Engagement Patterns
    preferred_content_types: List[str] = Field(default_factory=list)
    attention_span_minutes: Optional[int] = Field(default=None)
    best_learning_time: Optional[str] = Field(default=None)  # morning, afternoon, evening

    # Strengths and Weaknesses
    strong_subjects: List[str] = Field(default_factory=list)
    weak_subjects: List[str] = Field(default_factory=list)
    recommended_focus_areas: List[str] = Field(default_factory=list)

    # Adaptation Settings
    adaptive_difficulty_enabled: bool = Field(default=True)
    personalized_content_enabled: bool = Field(default=True)
    spaced_repetition_enabled: bool = Field(default=True)

    # Analytics
    total_lessons_completed: int = Field(default=0)
    total_quizzes_taken: int = Field(default=0)
    average_session_duration: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AIRecommendation(SQLModel, table=True):
    """AI-generated learning recommendations"""
    __tablename__ = "ai_recommendations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)

    # Recommendation Details
    recommendation_type: str = Field(nullable=False)  # course, lesson, skill, break, etc.
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)

    # Target Content
    recommended_course_id: Optional[str] = Field(default=None)
    recommended_lesson_id: Optional[str] = Field(default=None)
    recommended_skill: Optional[str] = Field(default=None)

    # Reasoning
    reasoning: str = Field(nullable=False)
    confidence_score: float = Field(default=0.0)
    supporting_data: Dict[str, Any] = Field(default_factory=dict)

    # User Interaction
    is_viewed: bool = Field(default=False)
    is_implemented: bool = Field(default=False)
    user_feedback: Optional[str] = Field(default=None)

    # Validity
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIContentGeneration(SQLModel, table=True):
    """AI-generated content for courses and lessons"""
    __tablename__ = "ai_content_generation"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Source Information
    course_id: Optional[str] = Field(default=None, index=True)
    lesson_id: Optional[str] = Field(default=None, index=True)
    instructor_id: str = Field(index=True, nullable=False)

    # Generation Request
    content_type: str = Field(nullable=False)  # quiz, explanation, example, exercise
    prompt: str = Field(nullable=False)
    context_data: Dict[str, Any] = Field(default_factory=dict)

    # Generated Content
    generated_content: str = Field(nullable=False)
    content_metadata: Dict[str, Any] = Field(default_factory=dict)

    # AI Processing
    model_used: str = Field(nullable=False)
    tokens_used: int = Field(default=0)
    processing_time_seconds: float = Field(default=0.0)

    # Quality Assessment
    quality_score: Optional[float] = Field(default=None)
    instructor_rating: Optional[int] = Field(default=None)
    needs_revision: bool = Field(default=False)
    revision_notes: Optional[str] = Field(default=None)

    # Usage
    is_approved: bool = Field(default=False)
    is_published: bool = Field(default=False)
    usage_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LearningPath(SQLModel, table=True):
    """AI-generated personalized learning paths"""
    __tablename__ = "learning_paths"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)

    # Path Configuration
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    target_skill: str = Field(nullable=False)
    estimated_duration_weeks: int = Field(default=4)

    # Learning Objectives
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisite_skills: List[str] = Field(default_factory=list)

    # Course Sequence
    recommended_courses: List[Dict[str, Any]] = Field(default_factory=list)
    course_sequence: List[str] = Field(default_factory=list)  # Course IDs in order

    # Progress Tracking
    current_course_index: int = Field(default=0)
    overall_progress: float = Field(default=0.0)
    estimated_completion_date: Optional[datetime] = Field(default=None)

    # Adaptation
    difficulty_level: str = Field(default="intermediate")
    learning_style: str = Field(default=LearningStyle.VISUAL.value)
    pace_preference: str = Field(default="moderate")

    # AI Generation
    generated_by_ai: bool = Field(default=True)
    ai_model_version: Optional[str] = Field(default=None)
    last_adapted: datetime = Field(default_factory=datetime.utcnow)

    # Status
    is_active: bool = Field(default=True)
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
