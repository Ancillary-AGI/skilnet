"""
Adaptive Learning endpoints for EduVerse platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("adaptive_learning")

@router.get("/learning-path")
async def get_personalized_learning_path(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated personalized learning path"""
    try:
        # Mock adaptive learning path - in production, use ML algorithms
        learning_path = {
            "user_id": current_user.id,
            "path_id": "path_001",
            "generated_at": datetime.utcnow().isoformat(),
            "learning_style": current_user.learning_style or "visual",
            "difficulty_level": current_user.difficulty_preference or "intermediate",
            "estimated_completion": "6 weeks",
            "confidence_score": 0.87,
            
            "current_phase": {
                "phase_number": 1,
                "phase_name": "Foundation Building",
                "description": "Establishing core programming concepts",
                "progress": 0.65,
                "estimated_time_remaining": "1 week"
            },
            
            "recommended_courses": [
                {
                    "course_id": "course_001",
                    "title": "Python Data Structures",
                    "priority": "high",
                    "reason": "Essential for your programming journey",
                    "estimated_duration": "2 weeks",
                    "difficulty": "intermediate",
                    "prerequisites_met": True,
                    "learning_objectives": [
                        "Master lists, dictionaries, and sets",
                        "Understand algorithmic complexity",
                        "Implement custom data structures"
                    ]
                },
                {
                    "course_id": "course_002",
                    "title": "Web Development with Flask",
                    "priority": "medium",
                    "reason": "Natural progression from Python basics",
                    "estimated_duration": "3 weeks",
                    "difficulty": "intermediate",
                    "prerequisites_met": True,
                    "learning_objectives": [
                        "Build web applications",
                        "Handle HTTP requests",
                        "Work with databases"
                    ]
                }
            ],
            
            "skill_gaps": [
                {
                    "skill": "Algorithm Design",
                    "current_level": 3,
                    "target_level": 6,
                    "importance": "high",
                    "recommended_resources": [
                        "Algorithm Visualization Course",
                        "Coding Interview Prep"
                    ]
                },
                {
                    "skill": "Database Management",
                    "current_level": 2,
                    "target_level": 5,
                    "importance": "medium",
                    "recommended_resources": [
                        "SQL Fundamentals",
                        "Database Design Principles"
                    ]
                }
            ],
            
            "learning_milestones": [
                {
                    "milestone": "Complete Python Fundamentals",
                    "status": "completed",
                    "completed_at": "2024-01-15T10:30:00Z",
                    "xp_earned": 500
                },
                {
                    "milestone": "Build First Web Application",
                    "status": "in_progress",
                    "progress": 0.3,
                    "estimated_completion": "2024-01-25T00:00:00Z"
                },
                {
                    "milestone": "Master Data Structures",
                    "status": "upcoming",
                    "estimated_start": "2024-01-20T00:00:00Z",
                    "estimated_completion": "2024-02-05T00:00:00Z"
                }
            ],
            
            "adaptive_recommendations": {
                "study_schedule": {
                    "optimal_session_length": 45,  # minutes
                    "recommended_frequency": "daily",
                    "best_time_slots": ["19:00-20:00", "20:00-21:00"],
                    "break_intervals": 5  # minutes
                },
                "content_preferences": {
                    "video_to_text_ratio": 0.7,
                    "interactive_exercises": True,
                    "peer_collaboration": True,
                    "gamification_level": "high"
                },
                "difficulty_adjustments": {
                    "current_success_rate": 0.85,
                    "target_success_rate": 0.80,
                    "adjustment": "maintain_current_level"
                }
            }
        }
        
        return learning_path
        
    except Exception as e:
        logger.error(f"Failed to get learning path: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate learning path"
        )

@router.post("/update-preferences")
async def update_learning_preferences(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user learning preferences for adaptive algorithm"""
    try:
        # Validate preferences
        valid_preferences = {
            "learning_style", "difficulty_preference", "daily_goal_minutes",
            "preferred_content_types", "study_schedule", "accessibility_needs"
        }
        
        # Update user preferences
        if "learning_style" in preferences:
            current_user.learning_style = preferences["learning_style"]
        
        if "difficulty_preference" in preferences:
            current_user.difficulty_preference = preferences["difficulty_preference"]
        
        if "daily_goal_minutes" in preferences:
            current_user.daily_goal_minutes = preferences["daily_goal_minutes"]
        
        # Store additional preferences in accessibility_settings JSON field
        accessibility_settings = current_user.accessibility_settings or {}
        for key, value in preferences.items():
            if key in valid_preferences:
                accessibility_settings[key] = value
        
        current_user.accessibility_settings = accessibility_settings
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Learning preferences updated successfully",
            "updated_preferences": preferences
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update learning preferences"
        )

@router.get("/content-recommendations")
async def get_content_recommendations(
    content_type: Optional[str] = Query(None, regex="^(video|article|exercise|quiz|project)$"),
    difficulty: Optional[str] = Query(None, regex="^(beginner|intermediate|advanced)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered content recommendations"""
    try:
        # Mock content recommendations - in production, use ML recommendation engine
        recommendations = {
            "user_id": current_user.id,
            "generated_at": datetime.utcnow().isoformat(),
            "recommendation_type": "personalized",
            "filters_applied": {
                "content_type": content_type,
                "difficulty": difficulty,
                "learning_style": current_user.learning_style
            },
            
            "recommended_content": [
                {
                    "content_id": "content_001",
                    "title": "Advanced Python Decorators",
                    "type": "video",
                    "difficulty": "intermediate",
                    "duration_minutes": 25,
                    "match_score": 0.92,
                    "reasons": [
                        "Matches your Python skill level",
                        "Builds on recently completed topics",
                        "High engagement from similar learners"
                    ],
                    "learning_objectives": [
                        "Understand decorator syntax",
                        "Create custom decorators",
                        "Apply decorators in real projects"
                    ],
                    "estimated_completion_time": "30 minutes",
                    "prerequisite_knowledge": ["Python functions", "Closures"]
                },
                {
                    "content_id": "content_002",
                    "title": "Interactive Python Coding Challenge",
                    "type": "exercise",
                    "difficulty": "intermediate",
                    "duration_minutes": 15,
                    "match_score": 0.88,
                    "reasons": [
                        "Reinforces recent learning",
                        "Matches your preferred learning style",
                        "Optimal difficulty for skill growth"
                    ],
                    "skills_practiced": [
                        "Problem solving",
                        "Algorithm implementation",
                        "Code optimization"
                    ]
                }
            ],
            
            "alternative_suggestions": [
                {
                    "content_id": "content_003",
                    "title": "Python Testing with pytest",
                    "type": "article",
                    "difficulty": "intermediate",
                    "match_score": 0.75,
                    "reason": "Expands your Python toolkit"
                }
            ],
            
            "learning_insights": {
                "strength_areas": ["Python syntax", "Problem solving"],
                "improvement_areas": ["Testing", "Code organization"],
                "next_skill_targets": ["Web frameworks", "Database integration"],
                "learning_velocity": "above_average"
            }
        }
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get content recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate content recommendations"
        )

@router.post("/feedback")
async def submit_content_feedback(
    feedback_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback on content to improve recommendations"""
    try:
        # Validate feedback data
        required_fields = ["content_id", "rating", "feedback_type"]
        for field in required_fields:
            if field not in feedback_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Process feedback for adaptive learning algorithm
        feedback_entry = {
            "user_id": current_user.id,
            "content_id": feedback_data["content_id"],
            "rating": feedback_data["rating"],
            "feedback_type": feedback_data["feedback_type"],
            "difficulty_rating": feedback_data.get("difficulty_rating"),
            "engagement_rating": feedback_data.get("engagement_rating"),
            "usefulness_rating": feedback_data.get("usefulness_rating"),
            "comments": feedback_data.get("comments"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store feedback (in production, use proper database)
        logger.info(f"Content feedback received: {json.dumps(feedback_entry)}")
        
        # Update user's learning profile based on feedback
        await update_learning_profile_from_feedback(current_user, feedback_entry, db)
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "impact": "Your recommendations will be improved based on this feedback"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )

@router.get("/difficulty-assessment")
async def get_difficulty_assessment(
    skill_area: str = Query(..., description="Skill area to assess"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get adaptive difficulty assessment for a skill area"""
    try:
        # Mock difficulty assessment - in production, use adaptive testing algorithms
        assessment = {
            "skill_area": skill_area,
            "user_id": current_user.id,
            "assessment_id": f"assess_{skill_area}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "estimated_duration": "15 minutes",
            
            "current_level_estimate": {
                "level": "intermediate",
                "confidence": 0.78,
                "score_range": "65-75%"
            },
            
            "adaptive_questions": [
                {
                    "question_id": "q001",
                    "difficulty": "intermediate",
                    "type": "multiple_choice",
                    "question": "What is the time complexity of searching in a balanced binary search tree?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                    "explanation_available": True
                },
                {
                    "question_id": "q002",
                    "difficulty": "intermediate",
                    "type": "code_completion",
                    "question": "Complete the function to implement binary search:",
                    "code_template": "def binary_search(arr, target):\n    # Your code here",
                    "test_cases": [
                        {"input": "[1,2,3,4,5], 3", "expected": "2"},
                        {"input": "[1,3,5,7,9], 6", "expected": "-1"}
                    ]
                }
            ],
            
            "learning_objectives": [
                "Assess current understanding of algorithms",
                "Identify knowledge gaps",
                "Calibrate difficulty for future content"
            ],
            
            "next_steps": {
                "if_beginner": "Start with Algorithm Basics course",
                "if_intermediate": "Continue with Advanced Data Structures",
                "if_advanced": "Move to System Design concepts"
            }
        }
        
        return assessment
        
    except Exception as e:
        logger.error(f"Failed to get difficulty assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate difficulty assessment"
        )

@router.post("/assessment-results")
async def submit_assessment_results(
    results_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit assessment results to update user's skill profile"""
    try:
        # Process assessment results
        assessment_results = {
            "user_id": current_user.id,
            "assessment_id": results_data["assessment_id"],
            "skill_area": results_data["skill_area"],
            "score": results_data["score"],
            "total_questions": results_data["total_questions"],
            "correct_answers": results_data["correct_answers"],
            "time_taken_minutes": results_data["time_taken_minutes"],
            "difficulty_level": results_data["difficulty_level"],
            "submitted_at": datetime.utcnow().isoformat()
        }
        
        # Update user's skill level based on assessment
        skill_level = calculate_skill_level(results_data["score"])
        
        # Store results and update user profile
        logger.info(f"Assessment results: {json.dumps(assessment_results)}")
        
        # Update learning path based on new skill assessment
        updated_path = await regenerate_learning_path(current_user, skill_level, db)
        
        return {
            "success": True,
            "results": assessment_results,
            "skill_level": skill_level,
            "recommendations": {
                "next_courses": updated_path["recommended_courses"][:3],
                "difficulty_adjustment": "optimal" if 70 <= results_data["score"] <= 85 else "needs_adjustment"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to submit assessment results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process assessment results"
        )

async def update_learning_profile_from_feedback(user: User, feedback: Dict[str, Any], db: AsyncSession):
    """Update user's learning profile based on content feedback"""
    # In production, this would update ML model features
    logger.info(f"Updating learning profile for user {user.id} based on feedback")

async def regenerate_learning_path(user: User, skill_level: str, db: AsyncSession) -> Dict[str, Any]:
    """Regenerate learning path based on new skill assessment"""
    # Mock regenerated path - in production, use ML algorithms
    return {
        "recommended_courses": [
            {"course_id": "advanced_001", "title": "Advanced Algorithms"},
            {"course_id": "system_001", "title": "System Design Fundamentals"}
        ]
    }

def calculate_skill_level(score: float) -> str:
    """Calculate skill level based on assessment score"""
    if score >= 85:
        return "advanced"
    elif score >= 65:
        return "intermediate"
    else:
        return "beginner"