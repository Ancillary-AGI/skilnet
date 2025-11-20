"""
Adaptive Content API endpoints for EduVerse platform

Provides endpoints for AI-powered content adaptation and personalized learning experiences.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.services.adaptive_content_service import AdaptiveContentService
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService

router = APIRouter()
logger = get_logger("adaptive_content_api")


@router.post("/adapt-content/{course_id}")
async def adapt_content(
    course_id: str,
    content_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Adapt content for the current user based on their learning profile and performance.

    This endpoint uses AI to personalize content delivery, adjusting difficulty,
    adding relevant examples, and incorporating the user's preferred learning style.
    """
    try:
        # Get course and enrollment
        course_service = CourseService(db)
        course = await course_service.get_course_by_id(course_id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        enrollment_service = EnrollmentService(db)
        enrollment = await enrollment_service.get_enrollment(current_user.id, course_id)

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )

        # Adapt content
        adaptive_service = AdaptiveContentService()
        adapted_content = await adaptive_service.adapt_content_for_user(
            current_user, course, enrollment, content_data
        )

        logger.info(f"Adapted content for user {current_user.id} in course {course_id}")
        return {
            "success": True,
            "adapted_content": adapted_content,
            "adaptations_applied": [
                "difficulty_adjustment",
                "personalized_examples",
                "learning_style_optimization"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to adapt content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content adaptation failed"
        )


@router.post("/generate-quiz/{course_id}")
async def generate_personalized_quiz(
    course_id: str,
    topic: str,
    difficulty_level: str = "intermediate",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a personalized quiz based on the user's knowledge gaps and learning preferences.

    The quiz will be adapted to focus on areas where the user needs improvement
    and presented in their preferred learning style.
    """
    try:
        # Validate course access
        course_service = CourseService(db)
        course = await course_service.get_course_by_id(course_id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Check enrollment
        enrollment_service = EnrollmentService(db)
        enrollment = await enrollment_service.get_enrollment(current_user.id, course_id)

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be enrolled in course to generate quiz"
            )

        # Generate personalized quiz
        adaptive_service = AdaptiveContentService()
        quiz = await adaptive_service.generate_personalized_quiz(
            current_user, course, topic, difficulty_level
        )

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate quiz"
            )

        logger.info(f"Generated personalized quiz for user {current_user.id} on topic {topic}")
        return {
            "success": True,
            "quiz": quiz,
            "personalization_features": [
                "knowledge_gap_focused",
                "learning_style_adapted",
                "difficulty_optimized"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Quiz generation failed"
        )


@router.post("/learning-path/{course_id}")
async def create_learning_path(
    course_id: str,
    target_completion_days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a personalized learning path for the course based on the user's schedule,
    learning preferences, and available time.

    The learning path includes daily goals, milestone rewards, and gamification elements.
    """
    try:
        # Validate course
        course_service = CourseService(db)
        course = await course_service.get_course_by_id(course_id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Check enrollment
        enrollment_service = EnrollmentService(db)
        enrollment = await enrollment_service.get_enrollment(current_user.id, course_id)

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be enrolled in course to create learning path"
            )

        # Create learning path
        adaptive_service = AdaptiveContentService()
        learning_path = await adaptive_service.create_learning_path(
            current_user, course, target_completion_days
        )

        if not learning_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create learning path"
            )

        logger.info(f"Created learning path for user {current_user.id} in course {course_id}")
        return {
            "success": True,
            "learning_path": learning_path,
            "features": [
                "personalized_schedule",
                "gamification_elements",
                "progress_tracking",
                "adaptive_goals"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create learning path: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Learning path creation failed"
        )


@router.get("/predict-outcomes/{course_id}")
async def predict_learning_outcomes(
    course_id: str,
    study_hours_per_week: int = 5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Predict learning outcomes for the course based on the user's study patterns,
    historical performance, and planned study hours.

    Provides completion probability, predicted grade range, and study recommendations.
    """
    try:
        # Validate course
        course_service = CourseService(db)
        course = await course_service.get_course_by_id(course_id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Check enrollment
        enrollment_service = EnrollmentService(db)
        enrollment = await enrollment_service.get_enrollment(current_user.id, course_id)

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be enrolled in course to get predictions"
            )

        # Predict outcomes
        adaptive_service = AdaptiveContentService()
        predictions = await adaptive_service.predict_learning_outcomes(
            current_user, course, study_hours_per_week
        )

        if not predictions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate predictions"
            )

        logger.info(f"Generated learning predictions for user {current_user.id} in course {course_id}")
        return {
            "success": True,
            "predictions": predictions,
            "insights": [
                "completion_probability",
                "grade_prediction",
                "time_estimation",
                "personalized_recommendations"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to predict outcomes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction generation failed"
        )


@router.get("/learning-analytics/{course_id}")
async def get_learning_analytics(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive learning analytics for personalized insights and recommendations.

    Includes performance trends, learning patterns, strengths, weaknesses, and
    actionable recommendations for improvement.
    """
    try:
        # Validate course access
        course_service = CourseService(db)
        course = await course_service.get_course_by_id(course_id)

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Check enrollment
        enrollment_service = EnrollmentService(db)
        enrollment = await enrollment_service.get_enrollment(current_user.id, course_id)

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be enrolled in course to view analytics"
            )

        # Get analytics
        adaptive_service = AdaptiveContentService()

        # Get performance data
        performance_data = await adaptive_service._analyze_user_performance(
            current_user.id, course_id
        )

        # Get learning profile
        learning_profile = await adaptive_service._get_learning_profile(current_user.id)

        # Generate insights
        insights = {
            "performance_summary": performance_data,
            "learning_profile": learning_profile,
            "strengths": performance_data.get("strong_topics", []),
            "weaknesses": performance_data.get("weak_topics", []),
            "recommendations": await adaptive_service._generate_study_recommendations(
                current_user, course, 0.8, {"most_likely": 85}
            ),
            "next_steps": [
                "Focus on weak topics in upcoming study sessions",
                "Practice with adaptive quizzes",
                "Review learning path recommendations"
            ]
        }

        logger.info(f"Retrieved learning analytics for user {current_user.id} in course {course_id}")
        return {
            "success": True,
            "analytics": insights,
            "data_points": [
                "performance_metrics",
                "learning_patterns",
                "skill_assessment",
                "personalized_insights"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get learning analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics retrieval failed"
        )