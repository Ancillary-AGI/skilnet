import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field

class VRPlatform(str, Enum):
    OCULUS_QUEST = "oculus_quest"
    OCULUS_RIFT = "oculus_rift"
    HTC_VIVE = "htc_vive"
    VALVE_INDEX = "valve_index"
    WINDOWS_MIXED_REALITY = "windows_mixed_reality"
    APPLE_VISION_PRO = "apple_vision_pro"
    HOLO_LENS = "holo_lens"
    META_QUEST_3 = "meta_quest_3"
    GENERIC_VR = "generic_vr"
    GENERIC_AR = "generic_ar"

class VRContentType(str, Enum):
    ENVIRONMENT = "environment"
    INTERACTIVE_OBJECT = "interactive_object"
    SIMULATION = "simulation"
    LABORATORY = "laboratory"
    CLASSROOM = "classroom"
    HISTORICAL_RECREATION = "historical_recreation"
    SCIENTIFIC_VISUALIZATION = "scientific_visualization"
    LANGUAGE_IMMERSION = "language_immersion"

class HandTrackingMode(str, Enum):
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    PRECISE = "precise"

class VREnvironment(SQLModel, table=True):
    """VR/AR environments for immersive learning"""
    __tablename__ = "vr_environments"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Content Details
    content_type: str = Field(default=VRContentType.ENVIRONMENT.value)
    subject_area: str = Field(nullable=False)
    difficulty_level: str = Field(default="intermediate")

    # Technical Specifications
    platform_support: List[str] = Field(default_factory=list)  # List of VRPlatform values
    min_hardware_requirements: Dict[str, Any] = Field(default_factory=dict)
    recommended_hardware: Dict[str, Any] = Field(default_factory=dict)

    # File Assets
    environment_file_url: str = Field(nullable=False)
    thumbnail_url: Optional[str] = Field(default=None)
    preview_video_url: Optional[str] = Field(default=None)

    # Spatial Configuration
    dimensions: Dict[str, float] = Field(default_factory=dict)  # width, height, depth
    spawn_points: List[Dict[str, Any]] = Field(default_factory=list)
    navigation_zones: List[Dict[str, Any]] = Field(default_factory=list)

    # Features
    hand_tracking_enabled: bool = Field(default=False)
    hand_tracking_mode: str = Field(default=HandTrackingMode.NONE.value)
    haptic_feedback_enabled: bool = Field(default=False)
    spatial_audio_enabled: bool = Field(default=False)

    # Learning Integration
    associated_course_id: Optional[str] = Field(default=None, index=True)
    associated_lesson_id: Optional[str] = Field(default=None, index=True)
    learning_objectives: List[str] = Field(default_factory=list)

    # Analytics
    total_sessions: int = Field(default=0)
    average_session_duration: int = Field(default=0)
    average_completion_rate: float = Field(default=0.0)

    # Metadata
    version: str = Field(default="1.0.0")
    file_size_mb: Optional[float] = Field(default=None)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VRSession(SQLModel, table=True):
    """User VR/AR learning sessions"""
    __tablename__ = "vr_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    environment_id: str = Field(index=True, nullable=False)

    # Session Details
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    duration_minutes: int = Field(default=0)

    # Platform Information
    platform_used: str = Field(nullable=False)
    device_info: Dict[str, Any] = Field(default_factory=dict)
    software_version: Optional[str] = Field(default=None)

    # Learning Context
    course_id: Optional[str] = Field(default=None)
    lesson_id: Optional[str] = Field(default=None)
    session_objectives: List[str] = Field(default_factory=list)

    # Performance Metrics
    completion_percentage: float = Field(default=0.0)
    objectives_achieved: List[str] = Field(default_factory=list)
    score_earned: int = Field(default=0)

    # Interaction Data
    objects_interacted: List[Dict[str, Any]] = Field(default_factory=list)
    hand_tracking_data: List[Dict[str, Any]] = Field(default_factory=list)
    movement_patterns: List[Dict[str, Any]] = Field(default_factory=list)

    # Technical Metrics
    frame_rate_average: Optional[float] = Field(default=None)
    latency_average_ms: Optional[float] = Field(default=None)
    crashes_encountered: int = Field(default=0)

    # User Experience
    comfort_level: Optional[int] = Field(default=None)  # 1-5 scale
    immersion_rating: Optional[int] = Field(default=None)  # 1-5 scale
    feedback_text: Optional[str] = Field(default=None)

    # Health & Safety
    motion_sickness_reported: bool = Field(default=False)
    breaks_taken: int = Field(default=0)
    eye_strain_reported: bool = Field(default=False)

class ARMarker(SQLModel, table=True):
    """AR markers and tracking data"""
    __tablename__ = "ar_markers"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Marker Configuration
    marker_type: str = Field(default="image")  # image, qr_code, nfc, gps
    marker_data: str = Field(nullable=False)  # Image URL, QR code data, etc.
    marker_size_cm: float = Field(default=10.0)

    # Associated Content
    course_id: Optional[str] = Field(default=None, index=True)
    lesson_id: Optional[str] = Field(default=None, index=True)
    content_id: Optional[str] = Field(default=None)

    # AR Content
    ar_content_url: Optional[str] = Field(default=None)
    ar_content_type: str = Field(default="3d_model")  # 3d_model, video, animation, text
    trigger_distance_meters: float = Field(default=1.0)

    # Interaction
    is_interactive: bool = Field(default=False)
    interaction_type: Optional[str] = Field(default=None)  # tap, gaze, voice, gesture
    interaction_data: Dict[str, Any] = Field(default_factory=dict)

    # Location (for GPS-based AR)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    altitude: Optional[float] = Field(default=None)
    location_accuracy_meters: Optional[float] = Field(default=None)

    # Analytics
    total_scans: int = Field(default=0)
    successful_interactions: int = Field(default=0)
    average_session_duration: int = Field(default=0)

    # Status
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ARInteraction(SQLModel, table=True):
    """User interactions with AR content"""
    __tablename__ = "ar_interactions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    marker_id: str = Field(index=True, nullable=False)

    # Session Information
    session_id: str = Field(nullable=False)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    duration_seconds: int = Field(default=0)

    # Interaction Details
    interaction_type: str = Field(nullable=False)
    interaction_data: Dict[str, Any] = Field(default_factory=dict)
    objects_manipulated: List[Dict[str, Any]] = Field(default_factory=list)

    # Learning Context
    course_id: Optional[str] = Field(default=None)
    lesson_id: Optional[str] = Field(default=None)
    learning_objective: Optional[str] = Field(default=None)

    # Performance
    completion_score: float = Field(default=0.0)
    accuracy_percentage: Optional[float] = Field(default=None)
    hints_used: int = Field(default=0)

    # Technical
    device_type: str = Field(nullable=False)  # phone, tablet, glasses, etc.
    ar_framework: str = Field(default="arkit")  # arkit, arcore, etc.
    tracking_quality: Optional[float] = Field(default=None)

    # User Feedback
    difficulty_rating: Optional[int] = Field(default=None)  # 1-5 scale
    enjoyment_rating: Optional[int] = Field(default=None)  # 1-5 scale
    feedback_text: Optional[str] = Field(default=None)

class SpatialAudioProfile(SQLModel, table=True):
    """Spatial audio configurations for VR/AR environments"""
    __tablename__ = "spatial_audio_profiles"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    environment_id: str = Field(index=True, nullable=False)

    # Audio Configuration
    audio_engine: str = Field(default="steam_audio")  # steam_audio, google_resonance, etc.
    sample_rate: int = Field(default=48000)
    channels: int = Field(default=2)

    # Spatial Settings
    speed_of_sound: float = Field(default=343.0)  # meters per second
    reverb_enabled: bool = Field(default=True)
    occlusion_enabled: bool = Field(default=True)
    reflection_enabled: bool = Field(default=True)

    # Audio Sources
    audio_sources: List[Dict[str, Any]] = Field(default_factory=list)
    ambient_audio: Optional[str] = Field(default=None)  # Audio file URL

    # Learning Integration
    narration_enabled: bool = Field(default=True)
    voice_guidance: bool = Field(default=True)
    sound_effects: Dict[str, str] = Field(default_factory=dict)  # event -> audio_url

    # Accessibility
    volume_normalization: bool = Field(default=True)
    hearing_assistance: bool = Field(default=False)
    audio_descriptions: bool = Field(default=False)

    # Status
    is_active: bool = Field(default=True)
    version: str = Field(default="1.0.0")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VRDeviceProfile(SQLModel, table=True):
    """User VR/AR device profiles and preferences"""
    __tablename__ = "vr_device_profiles"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True, nullable=False)

    # Device Information
    primary_device: str = Field(nullable=False)
    device_model: Optional[str] = Field(default=None)
    firmware_version: Optional[str] = Field(default=None)

    # Hardware Capabilities
    has_hand_tracking: bool = Field(default=False)
    has_eye_tracking: bool = Field(default=False)
    has_haptic_feedback: bool = Field(default=False)
    supported_controllers: List[str] = Field(default_factory=list)

    # User Preferences
    comfort_settings: Dict[str, Any] = Field(default_factory=dict)
    accessibility_settings: Dict[str, Any] = Field(default_factory=dict)
    audio_preferences: Dict[str, Any] = Field(default_factory=dict)

    # Performance Settings
    preferred_resolution: str = Field(default="auto")
    preferred_frame_rate: int = Field(default=90)
    quality_settings: Dict[str, Any] = Field(default_factory=dict)

    # Health & Safety
    motion_sickness_sensitivity: str = Field(default="medium")  # low, medium, high
    eye_strain_prevention: bool = Field(default=True)
    break_reminders: bool = Field(default=True)

    # Usage Statistics
    total_vr_time_minutes: int = Field(default=0)
    sessions_completed: int = Field(default=0)
    average_session_duration: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HapticFeedbackPattern(SQLModel, table=True):
    """Haptic feedback patterns for VR interactions"""
    __tablename__ = "haptic_feedback_patterns"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    # Pattern Configuration
    pattern_type: str = Field(default="vibration")  # vibration, pulse, continuous
    intensity: float = Field(default=0.5)  # 0.0 to 1.0
    duration_ms: int = Field(default=100)
    frequency_hz: Optional[float] = Field(default=None)

    # Advanced Settings
    waveform: Optional[str] = Field(default=None)  # sine, square, triangle, etc.
    amplitude_curve: List[float] = Field(default_factory=list)
    controller_mapping: Dict[str, Any] = Field(default_factory=dict)

    # Usage Context
    trigger_event: str = Field(nullable=False)  # object_interaction, achievement, error, etc.
    environment_id: Optional[str] = Field(default=None, index=True)

    # Learning Integration
    feedback_type: str = Field(default="general")  # positive, negative, neutral, instructional
    associated_learning_objective: Optional[str] = Field(default=None)

    # Status
    is_active: bool = Field(default=True)
    usage_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
