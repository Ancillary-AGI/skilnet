# Core Models
from .user import User, UserRole

# Course Models
from .course import (
    Course, Module, Lesson, Enrollment, LessonProgress, CourseReview,
    DifficultyLevel, ContentType, CourseStatus
)

# Gamification Models
from .gamification import (
    Badge, UserBadge, Achievement, UserAchievement, UserPoints,
    Leaderboard, LeaderboardEntry, Challenge, UserChallenge, PointsTransaction,
    BadgeType, BadgeRarity, AchievementType
)

# AI Models
from .ai_models import (
    AIModel, AITutor, AIInteraction, AdaptiveLearningProfile,
    AIRecommendation, AIContentGeneration, LearningPath,
    AIProvider, AIModelType, LearningStyle
)

# VR/AR Models
from .vr_ar_models import (
    VREnvironment, VRSession, ARMarker, ARInteraction,
    SpatialAudioProfile, VRDeviceProfile, HapticFeedbackPattern,
    VRPlatform, VRContentType, HandTrackingMode
)

# Social Learning Models
from .social_learning import (
    StudyGroup, GroupMembership, DiscussionForum, ForumPost,
    PeerLearningSession, StudyBuddyMatch, CollaborativeProject,
    UserContribution, LearningCommunity,
    StudyGroupType, GroupRole, PostType
)

# Notification Models
from .notifications import (
    Notification, NotificationPreference, NotificationTemplate,
    NotificationQueue, PushSubscription, NotificationAnalytics,
    UserNotificationStats,
    NotificationType, NotificationPriority, NotificationChannel
)

# Analytics Models
from .analytics import (
    AnalyticsEvent, UserLearningAnalytics, CourseAnalytics,
    SystemAnalytics, LearningPathAnalytics, ContentEngagementAnalytics,
    PredictiveAnalytics,
    AnalyticsEventType, LearningMetricType
)

__all__ = [
    # Core
    "User", "UserRole",

    # Course
    "Course", "Module", "Lesson", "Enrollment", "LessonProgress", "CourseReview",
    "DifficultyLevel", "ContentType", "CourseStatus",

    # Gamification
    "Badge", "UserBadge", "Achievement", "UserAchievement", "UserPoints",
    "Leaderboard", "LeaderboardEntry", "Challenge", "UserChallenge", "PointsTransaction",
    "BadgeType", "BadgeRarity", "AchievementType",

    # AI
    "AIModel", "AITutor", "AIInteraction", "AdaptiveLearningProfile",
    "AIRecommendation", "AIContentGeneration", "LearningPath",
    "AIProvider", "AIModelType", "LearningStyle",

    # VR/AR
    "VREnvironment", "VRSession", "ARMarker", "ARInteraction",
    "SpatialAudioProfile", "VRDeviceProfile", "HapticFeedbackPattern",
    "VRPlatform", "VRContentType", "HandTrackingMode",

    # Social Learning
    "StudyGroup", "GroupMembership", "DiscussionForum", "ForumPost",
    "PeerLearningSession", "StudyBuddyMatch", "CollaborativeProject",
    "UserContribution", "LearningCommunity",
    "StudyGroupType", "GroupRole", "PostType",

    # Notifications
    "Notification", "NotificationPreference", "NotificationTemplate",
    "NotificationQueue", "PushSubscription", "NotificationAnalytics",
    "UserNotificationStats",
    "NotificationType", "NotificationPriority", "NotificationChannel",

    # Analytics
    "AnalyticsEvent", "UserLearningAnalytics", "CourseAnalytics",
    "SystemAnalytics", "LearningPathAnalytics", "ContentEngagementAnalytics",
    "PredictiveAnalytics",
    "AnalyticsEventType", "LearningMetricType"
]
