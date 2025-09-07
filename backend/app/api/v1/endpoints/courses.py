"""
Course management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from backend.app.models.profile import User
from app.models.course import Course, CourseModule, Lesson, Enrollment, LessonProgress, CourseReview
from app.repositories.course_repository import CourseRepository
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseDetailResponse,
    ModuleCreate, ModuleResponse, LessonCreate, LessonResponse,
    EnrollmentResponse, ProgressUpdate, ReviewCreate, ReviewResponse
)
from app.services.ai_video_generator import AIVideoGenerator, VideoModelTrainer
from app.services.content_processor import ContentProcessor
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    has_vr: Optional[bool] = Query(None),
    has_ar: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|rating|popularity|price)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get courses with filtering and pagination"""
    course_repo = CourseRepository(db)
    
    filters = {}
    if category:
        filters['category'] = category
    if difficulty:
        filters['difficulty_level'] = difficulty
    if has_vr is not None:
        filters['vr_environment_id__isnull'] = not has_vr
    if has_ar is not None:
        filters['ar_markers__len__gt'] = 0 if has_ar else -1
    
    courses = await course_repo.get_courses_with_filters(
        skip=skip,
        limit=limit,
        filters=filters,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return [CourseResponse.from_orm(course) for course in courses]


@router.get("/featured", response_model=List[CourseResponse])
async def get_featured_courses(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get featured courses"""
    course_repo = CourseRepository(db)
    courses = await course_repo.get_featured_courses(limit=limit)
    return [CourseResponse.from_orm(course) for course in courses]


@router.get("/recommendations", response_model=List[CourseResponse])
async def get_course_recommendations(
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized course recommendations"""
    recommendation_engine = RecommendationEngine(db)
    recommended_courses = await recommendation_engine.get_personalized_recommendations(
        user_id=current_user.id,
        limit=limit
    )
    
    return [CourseResponse.from_orm(course) for course in recommended_courses]


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course_detail(
    course_id: str,
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed course information"""
    course_repo = CourseRepository(db)
    course = await course_repo.get_course_with_details(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if user is enrolled
    enrollment = None
    if current_user:
        enrollment = await course_repo.get_user_enrollment(current_user.id, course_id)
    
    return CourseDetailResponse.from_orm(course, enrollment)


@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new course (instructors only)"""
    # Check if user can create courses
    if not current_user.is_superuser and current_user.subscription_tier not in ['premium', 'enterprise']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create courses"
        )
    
    course_repo = CourseRepository(db)
    
    # Create course
    course = Course(
        title=course_data.title,
        slug=course_data.slug or course_data.title.lower().replace(' ', '-'),
        description=course_data.description,
        short_description=course_data.short_description,
        instructor_id=current_user.id,
        category=course_data.category,
        subcategory=course_data.subcategory,
        tags=course_data.tags,
        difficulty_level=course_data.difficulty_level,
        estimated_duration_hours=course_data.estimated_duration_hours,
        price=course_data.price,
        learning_objectives=course_data.learning_objectives,
        prerequisites=course_data.prerequisites,
        skills_gained=course_data.skills_gained,
        vr_environment_id=course_data.vr_environment_id,
        ar_markers=course_data.ar_markers,
        ai_tutor_enabled=course_data.ai_tutor_enabled,
    )
    
    created_course = await course_repo.create(course)
    return CourseResponse.from_orm(created_course)


@router.post("/{course_id}/enroll", response_model=EnrollmentResponse)
async def enroll_in_course(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Enroll user in a course"""
    course_repo = CourseRepository(db)
    
    # Check if course exists
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing_enrollment = await course_repo.get_user_enrollment(current_user.id, course_id)
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Check if course is free or user has premium access
    if course.price > 0 and not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment required for this course"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course.id,
        payment_amount=course.price,
        payment_currency=course.currency,
        payment_method="premium_subscription" if current_user.is_premium else "free"
    )
    
    created_enrollment = await course_repo.create_enrollment(enrollment)
    
    # Update course enrollment count
    course.enrollment_count += 1
    await course_repo.update(course)
    
    # Award enrollment XP
    current_user.add_experience_points(50)
    await course_repo.update_user(current_user)
    
    return EnrollmentResponse.from_orm(created_enrollment)


@router.get("/{course_id}/modules", response_model=List[ModuleResponse])
async def get_course_modules(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get course modules with user progress"""
    course_repo = CourseRepository(db)
    
    # Verify enrollment
    enrollment = await course_repo.get_user_enrollment(current_user.id, course_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    modules = await course_repo.get_course_modules_with_progress(course_id, current_user.id)
    return [ModuleResponse.from_orm(module) for module in modules]


@router.post("/{course_id}/modules/{module_id}/lessons/{lesson_id}/progress")
async def update_lesson_progress(
    course_id: str,
    module_id: str,
    lesson_id: str,
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update lesson progress"""
    course_repo = CourseRepository(db)
    
    # Verify enrollment
    enrollment = await course_repo.get_user_enrollment(current_user.id, course_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    # Update or create lesson progress
    progress = await course_repo.update_lesson_progress(
        enrollment_id=enrollment.id,
        lesson_id=lesson_id,
        progress_data=progress_data
    )
    
    # Award XP for progress
    if progress_data.is_completed:
        xp_earned = 100
        if progress_data.quiz_score and progress_data.quiz_score >= 90:
            xp_earned += 50  # Bonus for excellent performance
        
        current_user.add_experience_points(xp_earned)
        
        # Check for badges
        if progress_data.vr_interactions_count and progress_data.vr_interactions_count > 10:
            current_user.add_badge("VR_Explorer")
        
        await course_repo.update_user(current_user)
    
    
    
    # Update enrollment progress
    await course_repo.update_enrollment_progress(enrollment.id)
    
    return {"message": "Progress updated successfully", "xp_earned": xp_earned if progress_data.is_completed else 0}


@router.post("/{course_id}/generate-ai-content")
async def generate_ai_course_content(
    course_id: str,
    content_request: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI content for course"""
    course_repo = CourseRepository(db)
    
    # Verify course ownership or admin access
    course = await course_repo.get_by_id(course_id)
    if not course or (course.instructor_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    ai_generator = AIVideoGenerator()
    
    content_type = content_request.get("type", "video")
    topic = content_request.get("topic", "")
    duration = content_request.get("duration", 300)
    style = content_request.get("style", "professional")
    
    if content_type == "video":
        # Generate AI video content
        script = f"Educational content about {topic} for {course.title}"
        video_path = await ai_generator.generate_course_video(
            script=script,
            visual_style=style,
            duration_seconds=duration
        )
        
        return {
            "type": "video",
            "content_url": video_path,
            "duration": duration,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    elif content_type == "interactive":
        # Generate interactive content
        return {
            "type": "interactive",
            "content": {
                "quiz_questions": await _generate_ai_quiz(topic),
                "interactive_elements": await _generate_interactive_elements(topic),
                "vr_objects": await _generate_vr_objects(topic)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type"
        )


@router.post("/{course_id}/train-video-model")
async def train_course_video_model(
    course_id: str,
    training_config: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Train custom video model for course"""
    course_repo = CourseRepository(db)
    
    # Verify permissions
    course = await course_repo.get_by_id(course_id)
    if not course or (course.instructor_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get course videos for training data
    course_videos = await course_repo.get_course_video_urls(course_id)
    
    if len(course_videos) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 5 videos to train a custom model"
        )
    
    # Initialize trainer
    trainer = VideoModelTrainer()
    
    # Prepare training data
    dataset_path = await trainer.prepare_training_data(course_videos)
    
    # Train model
    model_path = await trainer.train_video_model(dataset_path, training_config)
    
    return {
        "message": "Video model training started",
        "model_path": model_path,
        "dataset_path": dataset_path,
        "estimated_completion": "2-4 hours",
        "training_config": training_config
    }


@router.post("/{course_id}/reviews", response_model=ReviewResponse)
async def create_course_review(
    course_id: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a course review"""
    course_repo = CourseRepository(db)
    
    # Verify enrollment
    enrollment = await course_repo.get_user_enrollment(current_user.id, course_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be enrolled to review course"
        )
    
    # Check if already reviewed
    existing_review = await course_repo.get_user_review(current_user.id, course_id)
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already reviewed this course"
        )
    
    # Create review
    review = CourseReview(
        user_id=current_user.id,
        course_id=course_id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        content_quality_rating=review_data.content_quality_rating,
        instructor_rating=review_data.instructor_rating,
        value_for_money_rating=review_data.value_for_money_rating,
        vr_experience_rating=review_data.vr_experience_rating,
        ai_tutor_rating=review_data.ai_tutor_rating,
        is_verified_purchase=enrollment.payment_amount > 0
    )
    
    created_review = await course_repo.create_review(review)
    
    # Update course rating
    await course_repo.update_course_rating(course_id)
    
    return ReviewResponse.from_orm(created_review)


@router.get("/{course_id}/analytics")
async def get_course_analytics(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get course analytics (instructors only)"""
    course_repo = CourseRepository(db)
    
    # Verify course ownership
    course = await course_repo.get_by_id(course_id)
    if not course or (course.instructor_id != current_user.id and not current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    analytics = await course_repo.get_course_analytics(course_id)
    
    return {
        "course_id": course_id,
        "total_enrollments": analytics["total_enrollments"],
        "active_learners": analytics["active_learners"],
        "completion_rate": analytics["completion_rate"],
        "average_progress": analytics["average_progress"],
        "total_watch_time": analytics["total_watch_time"],
        "vr_usage_stats": analytics["vr_usage_stats"],
        "ar_usage_stats": analytics["ar_usage_stats"],
        "ai_interaction_stats": analytics["ai_interaction_stats"],
        "popular_lessons": analytics["popular_lessons"],
        "drop_off_points": analytics["drop_off_points"],
        "student_feedback": analytics["student_feedback"],
        "revenue": analytics["revenue"],
        "geographic_distribution": analytics["geographic_distribution"],
    }


@router.post("/{course_id}/modules", response_model=ModuleResponse)
async def create_course_module(
    course_id: str,
    module_data: ModuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new course module"""
    course_repo = CourseRepository(db)
    
    # Verify course ownership
    course = await course_repo.get_by_id(course_id)
    if not course or course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get next order index
    next_order = await course_repo.get_next_module_order(course_id)
    
    module = CourseModule(
        course_id=course_id,
        title=module_data.title,
        description=module_data.description,
        order_index=next_order,
        vr_scene_id=module_data.vr_scene_id,
        ar_content_id=module_data.ar_content_id
    )
    
    created_module = await course_repo.create_module(module)
    return ModuleResponse.from_orm(created_module)


@router.post("/{course_id}/modules/{module_id}/lessons", response_model=LessonResponse)
async def create_lesson(
    course_id: str,
    module_id: str,
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new lesson"""
    course_repo = CourseRepository(db)
    
    # Verify course ownership
    course = await course_repo.get_by_id(course_id)
    if not course or course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get next order index
    next_order = await course_repo.get_next_lesson_order(module_id)
    
    lesson = Lesson(
        module_id=module_id,
        title=lesson_data.title,
        description=lesson_data.description,
        content_type=lesson_data.content_type,
        order_index=next_order,
        video_url=lesson_data.video_url,
        text_content=lesson_data.text_content,
        interactive_content=lesson_data.interactive_content,
        vr_scene_url=lesson_data.vr_scene_url,
        ar_model_url=lesson_data.ar_model_url,
        duration_minutes=lesson_data.duration_minutes,
        is_free=lesson_data.is_free,
        requires_vr=lesson_data.requires_vr,
        requires_ar=lesson_data.requires_ar,
        has_quiz=lesson_data.has_quiz,
        quiz_questions=lesson_data.quiz_questions,
        passing_score=lesson_data.passing_score
    )
    
    created_lesson = await course_repo.create_lesson(lesson)
    return LessonResponse.from_orm(created_lesson)


@router.post("/upload-content")
async def upload_course_content(
    file: UploadFile = File(...),
    course_id: str = Query(...),
    content_type: str = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload course content (video, 3D models, etc.)"""
    course_repo = CourseRepository(db)
    
    # Verify course ownership
    course = await course_repo.get_by_id(course_id)
    if not course or course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Process uploaded content
    content_processor = ContentProcessor()
    
    try:
        processed_content = await content_processor.process_upload(
            file=file,
            content_type=content_type,
            course_id=course_id
        )
        
        return {
            "message": "Content uploaded successfully",
            "content_url": processed_content["url"],
            "content_type": content_type,
            "file_size": processed_content["size"],
            "processing_status": processed_content["status"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process content: {str(e)}"
        )


# Helper functions for AI content generation
async def _generate_ai_quiz(topic: str) -> List[Dict[str, Any]]:
    """Generate AI quiz questions for topic"""
    # Mock implementation - would use AI to generate questions
    return [
        {
            "question": f"What is the main concept of {topic}?",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": f"The main concept of {topic} is..."
        },
        {
            "question": f"How does {topic} apply in real-world scenarios?",
            "type": "short_answer",
            "sample_answer": f"{topic} can be applied in various ways..."
        }
    ]


async def _generate_interactive_elements(topic: str) -> List[Dict[str, Any]]:
    """Generate interactive elements for topic"""
    return [
        {
            "type": "simulation",
            "title": f"{topic} Simulator",
            "description": f"Interactive simulation for {topic}",
            "parameters": {"complexity": "medium", "duration": 300}
        },
        {
            "type": "drag_drop",
            "title": f"{topic} Matching",
            "description": f"Match concepts related to {topic}",
            "items": [f"{topic} concept {i}" for i in range(1, 6)]
        }
    ]


async def _generate_vr_objects(topic: str) -> List[Dict[str, Any]]:
    """Generate VR objects for topic"""
    return [
        {
            "object_id": f"{topic}_model_1",
            "type": "3d_model",
            "url": f"/models/{topic}_model.glb",
            "position": [0, 0, -2],
            "scale": [1, 1, 1],
            "interactive": True,
            "physics_enabled": True
        },
        {
            "object_id": f"{topic}_diagram",
            "type": "interactive_diagram",
            "url": f"/diagrams/{topic}_diagram.svg",
            "position": [-2, 1, -1],
            "scale": [1.5, 1.5, 1],
            "interactive": True
        }
    ]