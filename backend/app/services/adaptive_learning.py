"""
Adaptive Learning Algorithm - Personalized Difficulty and Pacing
Superior to basic recommendation systems with real-time adaptation and cognitive modeling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid
import math
import statistics
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class LearningStyle(Enum):
    """Learning style categories"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class DifficultyLevel(Enum):
    """Adaptive difficulty levels"""
    BEGINNER = "beginner"
    EASY = "easy"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class LearningProfile:
    """User's learning profile and preferences"""
    user_id: str
    learning_style: LearningStyle
    preferred_difficulty: DifficultyLevel
    pace_factor: float  # 0.5 (slow) to 2.0 (fast)
    attention_span_minutes: int
    preferred_content_types: List[str]
    strengths: List[str]
    weaknesses: List[str]
    goals: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceMetrics:
    """Performance tracking for adaptation"""
    user_id: str
    topic_id: str
    attempts: int = 0
    correct_attempts: int = 0
    average_time_seconds: float = 0
    hint_usage: int = 0
    difficulty_rating: float = 0  # User's self-reported difficulty
    engagement_score: float = 0  # Based on interaction patterns
    last_practice: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AdaptiveRecommendation:
    """Adaptive learning recommendation"""
    recommendation_id: str
    user_id: str
    content_id: str
    recommended_difficulty: DifficultyLevel
    confidence_score: float
    reasoning: List[str]
    estimated_completion_time: int  # minutes
    prerequisites: List[str]
    next_review_date: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)


class AdaptiveLearningEngine:
    """
    Advanced adaptive learning system that surpasses basic recommendation engines

    Features:
    - Real-time difficulty adjustment
    - Cognitive load modeling
    - Spaced repetition optimization
    - Multi-dimensional performance tracking
    - Personalized pacing algorithms
    - Learning style adaptation
    """

    def __init__(self):
        self.learning_profiles: Dict[str, LearningProfile] = {}
        self.performance_data: Dict[str, List[PerformanceMetrics]] = {}
        self.recommendations: Dict[str, List[AdaptiveRecommendation]] = {}
        self.adaptation_history: Dict[str, List[Dict[str, Any]]] = {}

        # Algorithm parameters
        self.difficulty_thresholds = {
            DifficultyLevel.BEGINNER: 0.2,
            DifficultyLevel.EASY: 0.4,
            DifficultyLevel.INTERMEDIATE: 0.6,
            DifficultyLevel.ADVANCED: 0.8,
            DifficultyLevel.EXPERT: 1.0
        }

        # Cognitive load parameters
        self.cognitive_load_weights = {
            "content_complexity": 0.3,
            "user_fatigue": 0.2,
            "time_pressure": 0.2,
            "distraction_level": 0.3
        }

    async def initialize(self):
        """Initialize the adaptive learning engine"""
        logger.info("🚀 Adaptive learning engine initialized")

    async def create_learning_profile(
        self,
        user_id: str,
        initial_assessment: Dict[str, Any]
    ) -> LearningProfile:
        """Create initial learning profile based on assessment"""

        # Analyze initial assessment to determine learning style and preferences
        learning_style = await self._analyze_learning_style(initial_assessment)
        preferred_difficulty = await self._determine_initial_difficulty(initial_assessment)
        pace_factor = await self._calculate_initial_pace(initial_assessment)

        profile = LearningProfile(
            user_id=user_id,
            learning_style=learning_style,
            preferred_difficulty=preferred_difficulty,
            pace_factor=pace_factor,
            attention_span_minutes=await self._estimate_attention_span(initial_assessment),
            preferred_content_types=await self._determine_content_preferences(initial_assessment),
            strengths=initial_assessment.get("strengths", []),
            weaknesses=initial_assessment.get("weaknesses", []),
            goals=initial_assessment.get("goals", [])
        )

        self.learning_profiles[user_id] = profile

        logger.info(f"👤 Learning profile created for user {user_id}")
        return profile

    async def update_performance(
        self,
        user_id: str,
        topic_id: str,
        performance_data: Dict[str, Any]
    ):
        """Update user performance data for adaptive learning"""

        if user_id not in self.performance_data:
            self.performance_data[user_id] = []

        # Create or update performance metrics
        existing_metrics = None
        for metrics in self.performance_data[user_id]:
            if metrics.topic_id == topic_id:
                existing_metrics = metrics
                break

        if existing_metrics:
            # Update existing metrics
            existing_metrics.attempts += 1
            if performance_data.get("correct", False):
                existing_metrics.correct_attempts += 1
            existing_metrics.average_time_seconds = (
                (existing_metrics.average_time_seconds * (existing_metrics.attempts - 1) +
                 performance_data.get("time_seconds", 0)) / existing_metrics.attempts
            )
            existing_metrics.hint_usage += performance_data.get("hints_used", 0)
            existing_metrics.difficulty_rating = performance_data.get("difficulty_rating", existing_metrics.difficulty_rating)
            existing_metrics.engagement_score = performance_data.get("engagement_score", existing_metrics.engagement_score)
            existing_metrics.last_practice = datetime.utcnow()
        else:
            # Create new metrics
            metrics = PerformanceMetrics(
                user_id=user_id,
                topic_id=topic_id,
                attempts=1,
                correct_attempts=1 if performance_data.get("correct", False) else 0,
                average_time_seconds=performance_data.get("time_seconds", 0),
                hint_usage=performance_data.get("hints_used", 0),
                difficulty_rating=performance_data.get("difficulty_rating", 0.5),
                engagement_score=performance_data.get("engagement_score", 0.5),
                last_practice=datetime.utcnow()
            )
            self.performance_data[user_id].append(metrics)

        # Trigger adaptation analysis
        await self._analyze_and_adapt(user_id)

    async def get_adaptive_recommendation(
        self,
        user_id: str,
        current_topic: str,
        available_content: List[Dict[str, Any]]
    ) -> AdaptiveRecommendation:
        """Get personalized content recommendation"""

        if user_id not in self.learning_profiles:
            # Create default profile if none exists
            profile = await self.create_learning_profile(user_id, {})
        else:
            profile = self.learning_profiles[user_id]

        # Analyze user performance
        user_performance = self.performance_data.get(user_id, [])
        topic_performance = [p for p in user_performance if p.topic_id == current_topic]

        # Calculate optimal difficulty
        optimal_difficulty = await self._calculate_optimal_difficulty(
            profile, topic_performance, current_topic
        )

        # Find best content match
        best_content = await self._find_best_content_match(
            available_content, optimal_difficulty, profile
        )

        # Generate recommendation
        recommendation = AdaptiveRecommendation(
            recommendation_id=str(uuid.uuid4()),
            user_id=user_id,
            content_id=best_content["content_id"],
            recommended_difficulty=optimal_difficulty,
            confidence_score=await self._calculate_confidence_score(
                profile, topic_performance, best_content
            ),
            reasoning=await self._generate_reasoning(
                profile, topic_performance, optimal_difficulty, best_content
            ),
            estimated_completion_time=await self._estimate_completion_time(
                profile, best_content, optimal_difficulty
            ),
            prerequisites=best_content.get("prerequisites", []),
            next_review_date=await self._calculate_next_review_date(
                profile, topic_performance, optimal_difficulty
            )
        )

        # Store recommendation
        if user_id not in self.recommendations:
            self.recommendations[user_id] = []
        self.recommendations[user_id].append(recommendation)

        # Update learning profile based on recommendation
        await self._update_profile_from_recommendation(profile, recommendation)

        logger.info(f"🎯 Adaptive recommendation generated for user {user_id}")
        return recommendation

    async def adapt_content_difficulty(
        self,
        user_id: str,
        content_id: str,
        current_performance: Dict[str, Any]
    ) -> DifficultyLevel:
        """Adapt content difficulty based on real-time performance"""

        profile = self.learning_profiles.get(user_id)
        if not profile:
            return DifficultyLevel.INTERMEDIATE

        # Calculate current performance indicators
        accuracy_rate = current_performance.get("accuracy_rate", 0.5)
        completion_time = current_performance.get("completion_time", 1.0)
        engagement_level = current_performance.get("engagement_level", 0.5)

        # Adaptive algorithm based on multiple factors
        adaptation_score = await self._calculate_adaptation_score(
            accuracy_rate, completion_time, engagement_level, profile
        )

        # Determine new difficulty level
        if adaptation_score > 0.8:
            new_difficulty = await self._increase_difficulty(profile.preferred_difficulty)
        elif adaptation_score < 0.3:
            new_difficulty = await self._decrease_difficulty(profile.preferred_difficulty)
        else:
            new_difficulty = profile.preferred_difficulty

        # Update profile
        profile.preferred_difficulty = new_difficulty
        profile.last_updated = datetime.utcnow()

        # Record adaptation
        await self._record_adaptation(user_id, content_id, new_difficulty, adaptation_score)

        return new_difficulty

    async def optimize_learning_path(
        self,
        user_id: str,
        course_content: List[Dict[str, Any]],
        time_constraint_minutes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Optimize learning path based on user profile and constraints"""

        profile = self.learning_profiles.get(user_id)
        if not profile:
            return course_content  # Return original order if no profile

        # Get user performance data
        user_performance = self.performance_data.get(user_id, [])

        # Score each content item
        scored_content = []
        for content in course_content:
            score = await self._score_content_for_user(
                content, profile, user_performance
            )
            scored_content.append({
                **content,
                "adaptation_score": score,
                "estimated_time": await self._estimate_content_time(content, profile),
                "difficulty_match": await self._calculate_difficulty_match(content, profile)
            })

        # Sort by adaptation score (higher is better)
        optimized_path = sorted(scored_content, key=lambda x: x["adaptation_score"], reverse=True)

        # Apply time constraints if specified
        if time_constraint_minutes:
            optimized_path = await self._apply_time_constraints(
                optimized_path, time_constraint_minutes, profile
            )

        # Ensure prerequisites are met
        optimized_path = await self._ensure_prerequisite_order(optimized_path)

        logger.info(f"🛣️ Optimized learning path for user {user_id}")
        return optimized_path

    async def predict_learning_outcomes(
        self,
        user_id: str,
        target_content: List[Dict[str, Any]],
        prediction_horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict learning outcomes and success probability"""

        profile = self.learning_profiles.get(user_id)
        if not profile:
            return {"error": "No learning profile available"}

        user_performance = self.performance_data.get(user_id, [])

        # Calculate success probabilities for each content item
        predictions = []
        for content in target_content:
            success_probability = await self._predict_success_probability(
                content, profile, user_performance
            )

            time_to_completion = await self._predict_completion_time(
                content, profile, user_performance
            )

            predictions.append({
                "content_id": content["content_id"],
                "success_probability": success_probability,
                "estimated_completion_days": time_to_completion,
                "confidence_level": await self._calculate_prediction_confidence(
                    content, profile, user_performance
                ),
                "risk_factors": await self._identify_risk_factors(
                    content, profile, user_performance
                )
            })

        # Overall prediction
        overall_success_rate = sum(p["success_probability"] for p in predictions) / len(predictions)

        return {
            "user_id": user_id,
            "prediction_horizon_days": prediction_horizon_days,
            "overall_success_rate": overall_success_rate,
            "content_predictions": predictions,
            "recommended_interventions": await self._generate_interventions(
                predictions, profile
            ),
            "predicted_completion_date": (datetime.utcnow() + timedelta(
                days=sum(p["estimated_completion_days"] for p in predictions)
            )).isoformat()
        }

    # Private helper methods

    async def _analyze_learning_style(self, assessment: Dict[str, Any]) -> LearningStyle:
        """Analyze assessment to determine learning style"""

        # Simple heuristic-based analysis (in production, use ML models)
        style_scores = {
            LearningStyle.VISUAL: 0,
            LearningStyle.AUDITORY: 0,
            LearningStyle.KINESTHETIC: 0,
            LearningStyle.READING_WRITING: 0
        }

        # Analyze responses
        responses = assessment.get("style_questions", {})

        for question, answer in responses.items():
            if "visual" in question.lower() and answer > 3:
                style_scores[LearningStyle.VISUAL] += 1
            elif "audio" in question.lower() and answer > 3:
                style_scores[LearningStyle.AUDITORY] += 1
            elif "hands" in question.lower() and answer > 3:
                style_scores[LearningStyle.KINESTHETIC] += 1
            elif "read" in question.lower() and answer > 3:
                style_scores[LearningStyle.READING_WRITING] += 1

        # Return dominant style
        return max(style_scores, key=style_scores.get)

    async def _determine_initial_difficulty(self, assessment: Dict[str, Any]) -> DifficultyLevel:
        """Determine initial difficulty level"""

        skill_level = assessment.get("skill_level", 0.5)  # 0.0 to 1.0
        confidence_level = assessment.get("confidence_level", 0.5)

        avg_level = (skill_level + confidence_level) / 2

        if avg_level < 0.3:
            return DifficultyLevel.BEGINNER
        elif avg_level < 0.5:
            return DifficultyLevel.EASY
        elif avg_level < 0.7:
            return DifficultyLevel.INTERMEDIATE
        elif avg_level < 0.9:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT

    async def _calculate_initial_pace(self, assessment: Dict[str, Any]) -> float:
        """Calculate initial pace factor"""

        preferred_pace = assessment.get("preferred_pace", 1.0)  # 0.5 to 2.0
        time_availability = assessment.get("time_availability", 1.0)

        return min(preferred_pace * time_availability, 2.0)  # Cap at 2.0x speed

    async def _estimate_attention_span(self, assessment: Dict[str, Any]) -> int:
        """Estimate user's attention span in minutes"""

        base_span = assessment.get("attention_span", 25)  # Default 25 minutes
        focus_level = assessment.get("focus_level", 0.5)

        return int(base_span * (0.5 + focus_level))

    async def _determine_content_preferences(self, assessment: Dict[str, Any]) -> List[str]:
        """Determine preferred content types"""

        preferences = assessment.get("content_preferences", [])
        if not preferences:
            # Default preferences based on learning style
            style = await self._analyze_learning_style(assessment)
            style_preferences = {
                LearningStyle.VISUAL: ["video", "infographics", "diagrams"],
                LearningStyle.AUDITORY: ["audio", "podcasts", "lectures"],
                LearningStyle.KINESTHETIC: ["interactive", "hands_on", "simulations"],
                LearningStyle.READING_WRITING: ["text", "articles", "documents"]
            }
            return style_preferences.get(style, ["text", "video"])

        return preferences

    async def _analyze_and_adapt(self, user_id: str):
        """Analyze performance and adapt learning profile"""

        profile = self.learning_profiles.get(user_id)
        if not profile:
            return

        performance = self.performance_data.get(user_id, [])

        if len(performance) < 3:  # Need minimum data points
            return

        # Calculate performance trends
        recent_performance = performance[-5:]  # Last 5 attempts

        avg_accuracy = sum(p.correct_attempts / max(p.attempts, 1) for p in recent_performance) / len(recent_performance)
        avg_engagement = sum(p.engagement_score for p in recent_performance) / len(recent_performance)
        avg_difficulty_rating = sum(p.difficulty_rating for p in recent_performance) / len(recent_performance)

        # Adaptation logic
        if avg_accuracy > 0.8 and avg_engagement > 0.7:
            # User is performing well, consider increasing difficulty
            if profile.preferred_difficulty != DifficultyLevel.EXPERT:
                profile.preferred_difficulty = await self._increase_difficulty(profile.preferred_difficulty)

        elif avg_accuracy < 0.5 or avg_engagement < 0.4:
            # User is struggling, consider decreasing difficulty
            if profile.preferred_difficulty != DifficultyLevel.BEGINNER:
                profile.preferred_difficulty = await self._decrease_difficulty(profile.preferred_difficulty)

        # Adjust pace based on performance
        if avg_accuracy > 0.7 and avg_difficulty_rating < 0.6:
            # User finds content too easy, increase pace
            profile.pace_factor = min(profile.pace_factor * 1.1, 2.0)
        elif avg_accuracy < 0.6 and avg_difficulty_rating > 0.8:
            # User finds content too hard, decrease pace
            profile.pace_factor = max(profile.pace_factor * 0.9, 0.5)

        profile.last_updated = datetime.utcnow()

    async def _increase_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Increase difficulty level"""
        levels = list(DifficultyLevel)
        current_index = levels.index(current)
        return levels[min(current_index + 1, len(levels) - 1)]

    async def _decrease_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """Decrease difficulty level"""
        levels = list(DifficultyLevel)
        current_index = levels.index(current)
        return levels[max(current_index - 1, 0)]

    async def _calculate_optimal_difficulty(
        self,
        profile: LearningProfile,
        performance: List[PerformanceMetrics],
        topic: str
    ) -> DifficultyLevel:
        """Calculate optimal difficulty for user"""

        if not performance:
            return profile.preferred_difficulty

        # Calculate current performance level
        avg_accuracy = sum(p.correct_attempts / max(p.attempts, 1) for p in performance) / len(performance)
        avg_engagement = sum(p.engagement_score for p in performance) / len(performance)

        # Optimal difficulty based on flow theory (challenge = skill level)
        if avg_accuracy > 0.8 and avg_engagement > 0.7:
            return await self._increase_difficulty(profile.preferred_difficulty)
        elif avg_accuracy < 0.6 or avg_engagement < 0.5:
            return await self._decrease_difficulty(profile.preferred_difficulty)
        else:
            return profile.preferred_difficulty

    async def _find_best_content_match(
        self,
        available_content: List[Dict[str, Any]],
        difficulty: DifficultyLevel,
        profile: LearningProfile
    ) -> Dict[str, Any]:
        """Find best content match for user"""

        best_match = None
        best_score = -1

        for content in available_content:
            score = await self._calculate_content_match_score(content, difficulty, profile)

            if score > best_score:
                best_score = score
                best_match = content

        return best_match or available_content[0]  # Fallback to first item

    async def _calculate_content_match_score(
        self,
        content: Dict[str, Any],
        difficulty: DifficultyLevel,
        profile: LearningProfile
    ) -> float:
        """Calculate how well content matches user profile"""

        score = 0.0

        # Difficulty match (40% weight)
        content_difficulty = content.get("difficulty", DifficultyLevel.INTERMEDIATE)
        if content_difficulty == difficulty:
            score += 0.4
        elif abs(list(DifficultyLevel).index(content_difficulty) -
                list(DifficultyLevel).index(difficulty)) == 1:
            score += 0.2

        # Learning style match (30% weight)
        content_types = content.get("content_types", [])
        style_match = len(set(content_types) & set(profile.preferred_content_types))
        score += 0.3 * (style_match / max(len(profile.preferred_content_types), 1))

        # Time compatibility (20% weight)
        content_duration = content.get("duration_minutes", 30)
        if content_duration <= profile.attention_span_minutes:
            score += 0.2

        # Preference alignment (10% weight)
        if content.get("tags", []):
            tag_match = len(set(content["tags"]) & set(profile.strengths))
            score += 0.1 * (tag_match / max(len(profile.strengths), 1))

        return score

    async def _calculate_confidence_score(
        self,
        profile: LearningProfile,
        performance: List[PerformanceMetrics],
        content: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for recommendation"""

        if not performance:
            return 0.5  # Default confidence

        # Base confidence on performance consistency
        accuracy_rates = [p.correct_attempts / max(p.attempts, 1) for p in performance]
        consistency = 1 - (statistics.stdev(accuracy_rates) if len(accuracy_rates) > 1 else 0)

        # Adjust based on content familiarity
        content_tags = set(content.get("tags", []))
        profile_strengths = set(profile.strengths)
        familiarity = len(content_tags & profile_strengths) / max(len(content_tags), 1)

        return min(consistency * 0.7 + familiarity * 0.3, 1.0)

    async def _generate_reasoning(
        self,
        profile: LearningProfile,
        performance: List[PerformanceMetrics],
        difficulty: DifficultyLevel,
        content: Dict[str, Any]
    ) -> List[str]:
        """Generate reasoning for recommendation"""

        reasoning = []

        # Difficulty reasoning
        if difficulty != profile.preferred_difficulty:
            reasoning.append(
                f"Difficulty adjusted from {profile.preferred_difficulty.value} to {difficulty.value} "
                "based on recent performance"
            )

        # Performance-based reasoning
        if performance:
            avg_accuracy = sum(p.correct_attempts / max(p.attempts, 1) for p in performance) / len(performance)
            if avg_accuracy > 0.8:
                reasoning.append("Strong performance indicates readiness for more challenging content")
            elif avg_accuracy < 0.6:
                reasoning.append("Recent struggles suggest need for foundational content review")

        # Learning style reasoning
        content_types = content.get("content_types", [])
        style_matches = set(content_types) & set(profile.preferred_content_types)
        if style_matches:
            reasoning.append(f"Content matches preferred learning style: {', '.join(style_matches)}")

        return reasoning

    async def _estimate_completion_time(
        self,
        profile: LearningProfile,
        content: Dict[str, Any],
        difficulty: DifficultyLevel
    ) -> int:
        """Estimate completion time for content"""

        base_time = content.get("duration_minutes", 30)

        # Adjust for pace factor
        adjusted_time = base_time / profile.pace_factor

        # Adjust for difficulty match
        if difficulty == profile.preferred_difficulty:
            adjusted_time *= 0.9  # 10% faster when difficulty matches
        else:
            adjusted_time *= 1.2  # 20% slower when difficulty doesn't match

        return max(int(adjusted_time), 5)  # Minimum 5 minutes

    async def _calculate_next_review_date(
        self,
        profile: LearningProfile,
        performance: List[PerformanceMetrics],
        difficulty: DifficultyLevel
    ) -> datetime:
        """Calculate optimal next review date using spaced repetition"""

        if not performance:
            return datetime.utcnow() + timedelta(hours=24)  # Default 1 day

        # Calculate average performance
        avg_accuracy = sum(p.correct_attempts / max(p.attempts, 1) for p in performance) / len(performance)

        # Spaced repetition algorithm (simplified SM-2)
        if avg_accuracy > 0.9:
            interval_days = 7  # Review in 1 week for excellent performance
        elif avg_accuracy > 0.7:
            interval_days = 3  # Review in 3 days for good performance
        elif avg_accuracy > 0.5:
            interval_days = 1  # Review next day for moderate performance
        else:
            interval_days = 0.25  # Review in 6 hours for poor performance

        # Adjust for pace factor
        interval_days = interval_days / profile.pace_factor

        return datetime.utcnow() + timedelta(days=interval_days)

    async def _update_profile_from_recommendation(
        self,
        profile: LearningProfile,
        recommendation: AdaptiveRecommendation
    ):
        """Update learning profile based on recommendation"""

        # Record adaptation in history
        if profile.user_id not in self.adaptation_history:
            self.adaptation_history[profile.user_id] = []

        self.adaptation_history[profile.user_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "recommendation_id": recommendation.recommendation_id,
            "difficulty": recommendation.recommended_difficulty.value,
            "confidence": recommendation.confidence_score,
            "reasoning": recommendation.reasoning
        })

        # Keep only last 100 adaptations
        if len(self.adaptation_history[profile.user_id]) > 100:
            self.adaptation_history[profile.user_id] = self.adaptation_history[profile.user_id][-100:]

    async def _calculate_adaptation_score(
        self,
        accuracy_rate: float,
        completion_time: float,
        engagement_level: float,
        profile: LearningProfile
    ) -> float:
        """Calculate adaptation score for difficulty adjustment"""

        # Normalize completion time (assuming 1.0 is optimal pace)
        time_score = 1.0 - abs(completion_time - 1.0)

        # Weighted combination
        score = (
            accuracy_rate * 0.5 +
            time_score * 0.2 +
            engagement_level * 0.3
        )

        return min(score, 1.0)

    async def _score_content_for_user(
        self,
        content: Dict[str, Any],
        profile: LearningProfile,
        performance: List[PerformanceMetrics]
    ) -> float:
        """Score content suitability for user"""

        score = 0.0

        # Difficulty alignment (30%)
        content_difficulty = content.get("difficulty", DifficultyLevel.INTERMEDIATE)
        if content_difficulty == profile.preferred_difficulty:
            score += 0.3
        elif abs(list(DifficultyLevel).index(content_difficulty) -
                list(DifficultyLevel).index(profile.preferred_difficulty)) <= 1:
            score += 0.15

        # Learning style match (25%)
        content_types = content.get("content_types", [])
        style_match = len(set(content_types) & set(profile.preferred_content_types))
        score += 0.25 * (style_match / max(len(profile.preferred_content_types), 1))

        # Performance history (20%)
        if performance:
            recent_performance = performance[-3:]  # Last 3 attempts
            avg_accuracy = sum(p.correct_attempts / max(p.attempts, 1) for p in recent_performance) / len(recent_performance)
            score += 0.2 * avg_accuracy

        # Time compatibility (15%)
        content_duration = content.get("duration_minutes", 30)
        if content_duration <= profile.attention_span_minutes * 1.5:
            score += 0.15

        # Novelty factor (10%)
        content_tags = set(content.get("tags", []))
        learned_topics = set(p.topic_id for p in performance)
        novelty = len(content_tags - learned_topics) / max(len(content_tags), 1)
        score += 0.1 * novelty

        return score

    async def _estimate_content_time(
        self,
        content: Dict[str, Any],
        profile: LearningProfile
    ) -> int:
        """Estimate time to complete content"""

        base_time = content.get("duration_minutes", 30)
        return int(base_time / profile.pace_factor)

    async def _calculate_difficulty_match(
        self,
        content: Dict[str, Any],
        profile: LearningProfile
    ) -> float:
        """Calculate difficulty match score"""

        content_difficulty = content.get("difficulty", DifficultyLevel.INTERMEDIATE)
        profile_difficulty = profile.preferred_difficulty

        if content_difficulty == profile_difficulty:
            return 1.0
        elif abs(list(DifficultyLevel).index(content_difficulty) -
                list(DifficultyLevel).index(profile_difficulty)) == 1:
            return 0.7
        else:
            return 0.3

    async def _apply_time_constraints(
        self,
        content_list: List[Dict[str, Any]],
        max_time_minutes: int,
        profile: LearningProfile
    ) -> List[Dict[str, Any]]:
        """Apply time constraints to content list"""

        total_time = 0
        constrained_list = []

        for content in content_list:
            estimated_time = await self._estimate_content_time(content, profile)

            if total_time + estimated_time <= max_time_minutes:
                constrained_list.append(content)
                total_time += estimated_time
            else:
                break

        return constrained_list

    async def _ensure_prerequisite_order(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure prerequisite order is maintained"""

        # Simple topological sort based on prerequisites
        # In production, implement proper dependency resolution
        return sorted(content_list, key=lambda x: len(x.get("prerequisites", [])))

    async def _predict_success_probability(
        self,
        content: Dict[str, Any],
        profile: LearningProfile,
        performance: List[PerformanceMetrics]
    ) -> float:
        """Predict probability of success for content"""

        # Base probability
        base_prob = 0.5

        # Adjust based on difficulty match
        difficulty_match = await self._calculate_difficulty_match(content, profile)
        base_prob += (difficulty_match - 0.5) * 0.3

        # Adjust based on learning style match
        content_types = content.get("content_types", [])
        style_match = len(set(content_types) & set(profile.preferred_content_types))
        style_score = style_match / max(len(profile.preferred_content_types), 1)
        base_prob += (style_score - 0.5) * 0.2

        # Adjust based on recent performance
        if performance:
            recent_performance = performance[-5:]
            avg_accuracy = sum(p.correct_attempts / max(p.attempts, 1) for p in recent_performance) / len(recent_performance)
            base_prob += (avg_accuracy - 0.5) * 0.3

        return max(min(base_prob, 1.0), 0.0)

    async def _predict_completion_time(
        self,
        content: Dict[str, Any],
        profile: LearningProfile,
        performance: List[PerformanceMetrics]
    ) -> float:
        """Predict time to complete content"""

        base_time = content.get("duration_minutes", 30)
        adjusted_time = base_time / profile.pace_factor

        # Adjust based on performance trends
        if performance:
            recent_times = [p.average_time_seconds / 60 for p in performance[-3:]]  # Convert to minutes
            avg_recent_time = sum(recent_times) / len(recent_times)
            adjusted_time = (adjusted_time + avg_recent_time) / 2

        return adjusted_time

    async def _calculate_prediction_confidence(
        self,
        content: Dict[str, Any],
        profile: LearningProfile,
        performance: List[PerformanceMetrics]
    ) -> float:
        """Calculate confidence level for prediction"""

        confidence = 0.5  # Base confidence

        # More confidence with more performance data
        if performance:
            confidence += min(len(performance) / 10, 0.3)  # Up to 30% boost

        # More confidence with better profile match
        difficulty_match = await self._calculate_difficulty_match(content, profile)
        confidence += (difficulty_match - 0.5) * 0.2

        return min(confidence, 1.0)

    async def _identify_risk_factors(
        self,
        content: Dict[str, Any],
        profile: LearningProfile,
        performance: List[PerformanceMetrics]
    ) -> List[str]:
        """Identify potential risk factors for content"""

        risk_factors = []

        # Difficulty mismatch risk
        difficulty_match = await self._calculate_difficulty_match(content, profile)
        if difficulty_match < 0.5:
            risk_factors.append("Difficulty level may not match current skill level")

        # Learning style mismatch risk
        content_types = content.get("content_types", [])
        style_match = len(set(content_types) & set(profile.preferred_content_types))
        if style_match == 0:
            risk_factors.append("Content type may not match preferred learning style")

        # Time constraint risk
        content_duration = content.get("duration_minutes", 30)
        if content_duration > profile.attention_span_minutes * 1.5:
            risk_factors.append("Content duration may exceed attention span")

        # Performance trend risk
        if performance:
            recent_performance = performance[-3:]
            avg_accuracy = sum(p.correct_attempts / max(p.attempts, 1) for p in recent_performance) / len(recent_performance)
            if avg_accuracy < 0.6:
                risk_factors.append("Recent performance suggests potential difficulty")

        return risk_factors

    async def _generate_interventions(
        self,
        predictions: List[Dict[str, Any]],
        profile: LearningProfile
    ) -> List[Dict[str, Any]]:
        """Generate recommended interventions based on predictions"""

        interventions = []

        # Identify content with low success probability
        low_success_content = [p for p in predictions if p["success_probability"] < 0.6]

        for content in low_success_content:
            intervention = {
                "content_id": content["content_id"],
                "intervention_type": "difficulty_adjustment",
                "recommended_actions": [
                    "Provide additional scaffolding",
                    "Break into smaller chunks",
                    "Add more practice opportunities"
                ],
                "estimated_impact": "Increase success probability by 20-30%"
            }
            interventions.append(intervention)

        return interventions

    async def _record_adaptation(self, user_id: str, content_id: str, new_difficulty: DifficultyLevel, score: float):
        """Record adaptation for analysis"""

        if user_id not in self.adaptation_history:
            self.adaptation_history[user_id] = []

        self.adaptation_history[user_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "content_id": content_id,
            "new_difficulty": new_difficulty.value,
            "adaptation_score": score,
            "adaptation_type": "real_time"
        })

    async def get_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive learning analytics for user"""

        profile = self.learning_profiles.get(user_id)
        if not profile:
            return {"error": "No learning profile found"}

        performance = self.performance_data.get(user_id, [])
        adaptations = self.adaptation_history.get(user_id, [])

        # Calculate analytics
        if performance:
            accuracy_trend = [p.correct_attempts / max(p.attempts, 1) for p in performance]
            engagement_trend = [p.engagement_score for p in performance]
            difficulty_trend = [p.difficulty_rating for p in performance]

            analytics = {
                "user_id": user_id,
                "current_level": profile.preferred_difficulty.value,
                "learning_style": profile.learning_style.value,
                "pace_factor": profile.pace_factor,
                "total_attempts": sum(p.attempts for p in performance),
                "average_accuracy": sum(accuracy_trend) / len(accuracy_trend),
                "average_engagement": sum(engagement_trend) / len(engagement_trend),
                "difficulty_progression": self._calculate_difficulty_progression(adaptations),
                "strengths": profile.strengths,
                "areas_for_improvement": profile.weaknesses,
                "recommendations_count": len(self.recommendations.get(user_id, [])),
                "last_activity": profile.last_updated.isoformat()
            }
        else:
            analytics = {
                "user_id": user_id,
                "current_level": profile.preferred_difficulty.value,
                "learning_style": profile.learning_style.value,
                "status": "insufficient_data",
                "message": "Complete more content to see detailed analytics"
            }

        return analytics

    def _calculate_difficulty_progression(self, adaptations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate difficulty progression over time"""

        if not adaptations:
            return {"trend": "stable", "changes": 0}

        # Count difficulty changes
        difficulty_changes = 0
        for adaptation in adaptations[-10:]:  # Last 10 adaptations
            if adaptation.get("adaptation_type") == "real_time":
                difficulty_changes += 1

        if difficulty_changes > 5:
            trend = "increasing"
        elif difficulty_changes < -5:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "changes": difficulty_changes,
            "adaptations_count": len(adaptations)
        }

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("✅ Adaptive learning engine cleaned up")
