"""
Analytics endpoints for EduVerse platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("analytics")

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user dashboard analytics"""
    try:
        # Mock analytics data - replace with real database queries
        analytics_data = {
            "user_stats": {
                "total_xp": current_user.total_xp,
                "current_level": current_user.current_level,
                "current_streak": current_user.current_streak,
                "longest_streak": current_user.longest_streak,
                "courses_completed": 0,  # Query from enrollments
                "certificates_earned": 0,  # Query from certificates
                "study_time_minutes": 0,  # Query from learning sessions
                "achievements_unlocked": 0  # Query from achievements
            },
            "learning_progress": {
                "weekly_minutes": [45, 60, 30, 90, 75, 120, 85],  # Last 7 days
                "monthly_xp": [500, 750, 600, 900, 1200, 800, 950],  # Last 7 months
                "skill_levels": {
                    "programming": 75,
                    "mathematics": 60,
                    "science": 80,
                    "languages": 45
                }
            },
            "recent_activity": [
                {
                    "type": "course_completed",
                    "title": "Introduction to Python",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "xp_earned": 100
                },
                {
                    "type": "streak_milestone",
                    "title": "7-day learning streak!",
                    "timestamp": "2024-01-14T09:15:00Z",
                    "xp_earned": 50
                }
            ],
            "recommendations": [
                {
                    "type": "course",
                    "title": "Advanced Python Programming",
                    "reason": "Based on your completed courses",
                    "confidence": 0.85
                },
                {
                    "type": "skill",
                    "title": "Data Structures",
                    "reason": "Complement your programming skills",
                    "confidence": 0.78
                }
            ]
        }
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Failed to get dashboard analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics data"
        )

@router.get("/learning-progress")
async def get_learning_progress(
    period: str = Query("week", regex="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed learning progress analytics"""
    try:
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # year
            start_date = now - timedelta(days=365)
        
        # Mock progress data - replace with real queries
        progress_data = {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "total_study_time": 450,  # minutes
            "sessions_completed": 12,
            "xp_earned": 850,
            "courses_progress": [
                {
                    "course_id": "course_1",
                    "title": "Python Fundamentals",
                    "progress_percentage": 75,
                    "time_spent": 180,
                    "last_accessed": "2024-01-15T14:30:00Z"
                },
                {
                    "course_id": "course_2", 
                    "title": "Web Development Basics",
                    "progress_percentage": 45,
                    "time_spent": 120,
                    "last_accessed": "2024-01-14T16:45:00Z"
                }
            ],
            "skill_improvements": {
                "programming": 15,  # percentage improvement
                "problem_solving": 12,
                "critical_thinking": 8
            },
            "daily_breakdown": [
                {"date": "2024-01-15", "minutes": 90, "xp": 150},
                {"date": "2024-01-14", "minutes": 75, "xp": 125},
                {"date": "2024-01-13", "minutes": 60, "xp": 100},
                {"date": "2024-01-12", "minutes": 45, "xp": 75},
                {"date": "2024-01-11", "minutes": 80, "xp": 140},
                {"date": "2024-01-10", "minutes": 100, "xp": 180},
                {"date": "2024-01-09", "minutes": 0, "xp": 0}
            ]
        }
        
        return progress_data
        
    except Exception as e:
        logger.error(f"Failed to get learning progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress data"
        )

@router.get("/performance-metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed performance metrics"""
    try:
        metrics = {
            "learning_efficiency": {
                "avg_session_duration": 45,  # minutes
                "completion_rate": 0.85,
                "retention_rate": 0.78,
                "engagement_score": 0.92
            },
            "knowledge_retention": {
                "short_term": 0.88,  # 1 week
                "medium_term": 0.75,  # 1 month
                "long_term": 0.65    # 3 months
            },
            "learning_patterns": {
                "preferred_time": "evening",
                "optimal_session_length": 45,
                "best_learning_days": ["Tuesday", "Thursday", "Saturday"],
                "peak_performance_hour": 19
            },
            "comparative_performance": {
                "percentile_rank": 78,  # compared to similar learners
                "above_average_skills": ["programming", "mathematics"],
                "improvement_areas": ["languages", "creative_writing"]
            },
            "predictions": {
                "next_level_eta": "3 days",
                "course_completion_probability": 0.89,
                "recommended_study_time": 60  # minutes per day
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics"
        )

@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user achievements and badges"""
    try:
        achievements = {
            "earned_badges": [
                {
                    "id": "first_course",
                    "name": "First Steps",
                    "description": "Complete your first course",
                    "icon": "🎯",
                    "earned_at": "2024-01-10T12:00:00Z",
                    "rarity": "common"
                },
                {
                    "id": "week_streak",
                    "name": "Consistent Learner",
                    "description": "Maintain a 7-day learning streak",
                    "icon": "🔥",
                    "earned_at": "2024-01-14T09:15:00Z",
                    "rarity": "uncommon"
                }
            ],
            "available_badges": [
                {
                    "id": "month_streak",
                    "name": "Dedicated Scholar",
                    "description": "Maintain a 30-day learning streak",
                    "icon": "📚",
                    "progress": 0.23,  # 7/30 days
                    "rarity": "rare"
                },
                {
                    "id": "skill_master",
                    "name": "Skill Master",
                    "description": "Reach level 10 in any skill",
                    "icon": "⭐",
                    "progress": 0.75,  # level 7.5/10
                    "rarity": "epic"
                }
            ],
            "leaderboards": {
                "global_rank": 1247,
                "country_rank": 89,
                "friends_rank": 3,
                "category_ranks": {
                    "programming": 156,
                    "mathematics": 234,
                    "science": 89
                }
            },
            "milestone_progress": {
                "total_xp": {
                    "current": current_user.total_xp,
                    "next_milestone": 5000,
                    "progress": current_user.total_xp / 5000
                },
                "courses_completed": {
                    "current": 3,
                    "next_milestone": 10,
                    "progress": 0.3
                }
            }
        }
        
        return achievements
        
    except Exception as e:
        logger.error(f"Failed to get achievements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve achievements"
        )

@router.post("/track-event")
async def track_learning_event(
    event_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Track a learning event for analytics"""
    try:
        # Validate event data
        required_fields = ["event_type", "timestamp"]
        for field in required_fields:
            if field not in event_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Add user context
        event_data["user_id"] = current_user.id
        event_data["session_id"] = event_data.get("session_id", "unknown")
        
        # Store event (in production, use a proper analytics database)
        logger.info(f"Learning event tracked: {json.dumps(event_data)}")
        
        # Update user XP if applicable
        xp_events = ["lesson_completed", "quiz_passed", "course_finished"]
        if event_data["event_type"] in xp_events:
            xp_earned = event_data.get("xp_earned", 10)
            current_user.total_xp += xp_earned
            
            # Check for level up
            new_level = current_user.calculate_level()
            level_up = new_level > current_user.current_level
            current_user.current_level = new_level
            
            await db.commit()
            
            return {
                "success": True,
                "xp_earned": xp_earned,
                "total_xp": current_user.total_xp,
                "level_up": level_up,
                "current_level": current_user.current_level
            }
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to track event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track learning event"
        )

@router.get("/insights")
async def get_learning_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered learning insights and recommendations"""
    try:
        insights = {
            "personalized_insights": [
                {
                    "type": "learning_pattern",
                    "title": "You learn best in the evening",
                    "description": "Your performance is 23% higher during evening sessions (6-9 PM)",
                    "confidence": 0.87,
                    "action": "Schedule more study sessions in the evening"
                },
                {
                    "type": "skill_gap",
                    "title": "Consider strengthening your math foundation",
                    "description": "Your programming progress could accelerate with stronger math skills",
                    "confidence": 0.74,
                    "action": "Take the 'Mathematics for Programmers' course"
                }
            ],
            "learning_recommendations": [
                {
                    "type": "course",
                    "title": "Advanced Python: Data Structures",
                    "reason": "Natural progression from your completed courses",
                    "match_score": 0.92,
                    "estimated_completion": "2 weeks"
                },
                {
                    "type": "practice",
                    "title": "Daily Coding Challenges",
                    "reason": "Reinforce your programming skills",
                    "match_score": 0.85,
                    "estimated_time": "15 min/day"
                }
            ],
            "optimization_tips": [
                {
                    "category": "study_schedule",
                    "tip": "Try 25-minute focused sessions with 5-minute breaks",
                    "impact": "Could improve retention by 15%"
                },
                {
                    "category": "learning_method",
                    "tip": "Use more interactive exercises and less passive video watching",
                    "impact": "Better engagement and knowledge retention"
                }
            ],
            "progress_forecast": {
                "next_level_prediction": {
                    "estimated_date": "2024-01-22",
                    "confidence": 0.78,
                    "required_xp": current_user.xp_to_next_level()
                },
                "skill_mastery_timeline": {
                    "programming": "3 months",
                    "web_development": "2 months",
                    "data_science": "6 months"
                }
            }
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get learning insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve learning insights"
        )