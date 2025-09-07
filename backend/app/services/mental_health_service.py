"""
Mental Health and Wellness Service for learner wellbeing
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class MoodState(str, Enum):
    VERY_HAPPY = "very_happy"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    VERY_SAD = "very_sad"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    EXCITED = "excited"
    CALM = "calm"
    FRUSTRATED = "frustrated"


class StressLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class WellnessMetric(str, Enum):
    MOOD = "mood"
    STRESS = "stress"
    FOCUS = "focus"
    ENERGY = "energy"
    MOTIVATION = "motivation"
    SLEEP_QUALITY = "sleep_quality"
    SOCIAL_CONNECTION = "social_connection"


@dataclass
class MoodEntry:
    user_id: str
    mood: MoodState
    stress_level: StressLevel
    energy_level: int  # 1-10
    focus_level: int   # 1-10
    notes: Optional[str]
    timestamp: datetime
    context: Dict[str, Any]  # Learning context when mood was recorded


@dataclass
class WellnessInsight:
    metric: WellnessMetric
    current_value: float
    trend: str  # improving, declining, stable
    recommendation: str
    confidence: float
    supporting_data: Dict[str, Any]


@dataclass
class WellnessAlert:
    user_id: str
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    recommendations: List[str]
    timestamp: datetime
    requires_intervention: bool


class MentalHealthService:
    """Comprehensive mental health and wellness service"""
    
    def __init__(self):
        self.mood_entries: Dict[str, List[MoodEntry]] = {}
        self.wellness_profiles: Dict[str, Dict[str, Any]] = {}
        self.stress_detectors: Dict[str, Any] = {}
        self.intervention_strategies: Dict[str, List[str]] = {}
        
    async def initialize(self):
        """Initialize mental health service"""
        try:
            logger.info("Initializing Mental Health Service...")
            
            # Initialize stress detection models
            await self._initialize_stress_detection()
            
            # Load intervention strategies
            await self._load_intervention_strategies()
            
            # Initialize wellness tracking
            await self._initialize_wellness_tracking()
            
            logger.info("Mental Health Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Mental Health Service: {e}")
    
    async def record_mood_entry(
        self, 
        user_id: str, 
        mood_data: Dict[str, Any]
    ) -> MoodEntry:
        """Record user mood entry"""
        
        mood_entry = MoodEntry(
            user_id=user_id,
            mood=MoodState(mood_data["mood"]),
            stress_level=StressLevel(mood_data["stress_level"]),
            energy_level=mood_data.get("energy_level", 5),
            focus_level=mood_data.get("focus_level", 5),
            notes=mood_data.get("notes"),
            timestamp=datetime.utcnow(),
            context=mood_data.get("context", {})
        )
        
        # Store mood entry
        if user_id not in self.mood_entries:
            self.mood_entries[user_id] = []
        
        self.mood_entries[user_id].append(mood_entry)
        
        # Analyze mood patterns
        await self._analyze_mood_patterns(user_id)
        
        # Check for wellness alerts
        await self._check_wellness_alerts(user_id, mood_entry)
        
        # Update wellness profile
        await self._update_wellness_profile(user_id, mood_entry)
        
        return mood_entry
    
    async def detect_stress_from_behavior(
        self, 
        user_id: str, 
        behavior_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect stress from learning behavior patterns"""
        
        # Extract behavioral indicators
        indicators = await self._extract_stress_indicators(behavior_data)
        
        # Use ML model to predict stress level
        stress_prediction = await self._predict_stress_level(indicators)
        
        # Generate recommendations if stress detected
        recommendations = []
        if stress_prediction["stress_level"] > 0.7:
            recommendations = await self._generate_stress_reduction_recommendations(
                user_id, 
                stress_prediction
            )
        
        return {
            "user_id": user_id,
            "stress_level": stress_prediction["stress_level"],
            "confidence": stress_prediction["confidence"],
            "indicators": indicators,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def provide_wellness_insights(
        self, 
        user_id: str
    ) -> List[WellnessInsight]:
        """Provide personalized wellness insights"""
        
        if user_id not in self.mood_entries:
            return []
        
        insights = []
        recent_entries = self._get_recent_mood_entries(user_id, days=30)
        
        if not recent_entries:
            return insights
        
        # Analyze mood trends
        mood_insight = await self._analyze_mood_trends(recent_entries)
        if mood_insight:
            insights.append(mood_insight)
        
        # Analyze stress patterns
        stress_insight = await self._analyze_stress_patterns(recent_entries)
        if stress_insight:
            insights.append(stress_insight)
        
        # Analyze energy levels
        energy_insight = await self._analyze_energy_patterns(recent_entries)
        if energy_insight:
            insights.append(energy_insight)
        
        # Analyze focus patterns
        focus_insight = await self._analyze_focus_patterns(recent_entries)
        if focus_insight:
            insights.append(focus_insight)
        
        # Learning-specific insights
        learning_insights = await self._analyze_learning_wellness_correlation(user_id)
        insights.extend(learning_insights)
        
        return insights
    
    async def generate_personalized_interventions(
        self, 
        user_id: str, 
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized wellness interventions"""
        
        interventions = []
        
        # Get user wellness profile
        profile = self.wellness_profiles.get(user_id, {})
        
        # Determine intervention needs
        needs = await self._assess_intervention_needs(user_id, current_state)
        
        for need in needs:
            intervention_type = need["type"]
            severity = need["severity"]
            
            if intervention_type == "stress_reduction":
                interventions.extend(
                    await self._generate_stress_interventions(user_id, severity)
                )
            elif intervention_type == "mood_improvement":
                interventions.extend(
                    await self._generate_mood_interventions(user_id, severity)
                )
            elif intervention_type == "focus_enhancement":
                interventions.extend(
                    await self._generate_focus_interventions(user_id, severity)
                )
            elif intervention_type == "energy_boost":
                interventions.extend(
                    await self._generate_energy_interventions(user_id, severity)
                )
        
        # Personalize interventions based on user preferences
        personalized_interventions = await self._personalize_interventions(
            user_id, 
            interventions
        )
        
        return personalized_interventions
    
    async def create_wellness_learning_plan(
        self, 
        user_id: str
    ) -> Dict[str, Any]:
        """Create learning plan optimized for user's wellness"""
        
        # Get current wellness state
        wellness_state = await self._get_current_wellness_state(user_id)
        
        # Get learning preferences and patterns
        learning_patterns = await self._analyze_learning_patterns(user_id)
        
        # Generate wellness-optimized schedule
        schedule = await self._generate_wellness_schedule(
            wellness_state, 
            learning_patterns
        )
        
        # Add wellness breaks and activities
        enhanced_schedule = await self._add_wellness_activities(schedule)
        
        return {
            "user_id": user_id,
            "wellness_state": wellness_state,
            "optimized_schedule": enhanced_schedule,
            "wellness_goals": await self._generate_wellness_goals(user_id),
            "monitoring_plan": await self._create_monitoring_plan(user_id),
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def monitor_learning_session_wellness(
        self, 
        user_id: str, 
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor wellness during learning session"""
        
        # Extract wellness indicators from session
        indicators = {
            "session_duration": session_data.get("duration_minutes", 0),
            "interaction_frequency": session_data.get("interactions_per_minute", 0),
            "error_rate": session_data.get("error_rate", 0),
            "pause_frequency": session_data.get("pauses_per_hour", 0),
            "completion_rate": session_data.get("completion_rate", 0),
            "difficulty_level": session_data.get("difficulty_level", "medium")
        }
        
        # Detect potential wellness issues
        wellness_flags = await self._detect_session_wellness_flags(indicators)
        
        # Generate real-time recommendations
        recommendations = []
        if wellness_flags:
            recommendations = await self._generate_session_recommendations(
                user_id, 
                wellness_flags
            )
        
        # Update wellness tracking
        await self._update_session_wellness_tracking(user_id, indicators)
        
        return {
            "wellness_score": await self._calculate_session_wellness_score(indicators),
            "flags": wellness_flags,
            "recommendations": recommendations,
            "should_suggest_break": await self._should_suggest_break(user_id, indicators),
            "optimal_next_activity": await self._suggest_next_activity(user_id, indicators)
        }
    
    async def provide_crisis_support(
        self, 
        user_id: str, 
        crisis_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide crisis support and resources"""
        
        # Assess crisis severity
        severity = await self._assess_crisis_severity(crisis_indicators)
        
        # Generate immediate support resources
        support_resources = await self._generate_crisis_resources(severity)
        
        # Create safety plan
        safety_plan = await self._create_safety_plan(user_id, severity)
        
        # Alert support team if necessary
        if severity == "high" or severity == "critical":
            await self._alert_support_team(user_id, crisis_indicators, severity)
        
        # Log crisis intervention
        await self._log_crisis_intervention(user_id, crisis_indicators, severity)
        
        return {
            "severity": severity,
            "immediate_resources": support_resources,
            "safety_plan": safety_plan,
            "emergency_contacts": await self._get_emergency_contacts(),
            "follow_up_scheduled": True,
            "support_team_alerted": severity in ["high", "critical"]
        }
    
    # Helper methods
    async def _initialize_stress_detection(self):
        """Initialize stress detection models"""
        
        # Initialize isolation forest for anomaly detection
        self.stress_detectors["anomaly_detector"] = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # Initialize feature scaler
        self.stress_detectors["scaler"] = StandardScaler()
        
        # Load pre-trained models (in production)
        # self.stress_detectors["neural_network"] = load_model("stress_detection_model.h5")
    
    async def _load_intervention_strategies(self):
        """Load intervention strategies"""
        
        self.intervention_strategies = {
            "stress_reduction": [
                {
                    "name": "Deep Breathing Exercise",
                    "duration": 5,
                    "type": "breathing",
                    "instructions": "Take slow, deep breaths for 5 minutes",
                    "effectiveness": 0.8
                },
                {
                    "name": "Progressive Muscle Relaxation",
                    "duration": 10,
                    "type": "relaxation",
                    "instructions": "Tense and relax muscle groups systematically",
                    "effectiveness": 0.85
                },
                {
                    "name": "Mindfulness Meditation",
                    "duration": 15,
                    "type": "meditation",
                    "instructions": "Focus on present moment awareness",
                    "effectiveness": 0.9
                }
            ],
            "mood_improvement": [
                {
                    "name": "Gratitude Practice",
                    "duration": 5,
                    "type": "cognitive",
                    "instructions": "List three things you're grateful for",
                    "effectiveness": 0.75
                },
                {
                    "name": "Physical Movement",
                    "duration": 10,
                    "type": "physical",
                    "instructions": "Do light stretching or walking",
                    "effectiveness": 0.8
                },
                {
                    "name": "Social Connection",
                    "duration": 15,
                    "type": "social",
                    "instructions": "Reach out to a friend or family member",
                    "effectiveness": 0.85
                }
            ],
            "focus_enhancement": [
                {
                    "name": "Pomodoro Technique",
                    "duration": 25,
                    "type": "time_management",
                    "instructions": "Work for 25 minutes, then take a 5-minute break",
                    "effectiveness": 0.9
                },
                {
                    "name": "Environment Optimization",
                    "duration": 5,
                    "type": "environmental",
                    "instructions": "Adjust lighting, reduce distractions",
                    "effectiveness": 0.7
                },
                {
                    "name": "Attention Training",
                    "duration": 10,
                    "type": "cognitive",
                    "instructions": "Practice focused attention exercises",
                    "effectiveness": 0.8
                }
            ]
        }
    
    async def _analyze_mood_patterns(self, user_id: str):
        """Analyze user mood patterns"""
        
        entries = self.mood_entries.get(user_id, [])
        if len(entries) < 7:  # Need at least a week of data
            return
        
        # Analyze trends
        recent_moods = [entry.mood for entry in entries[-7:]]
        mood_trend = await self._calculate_mood_trend(recent_moods)
        
        # Store analysis results
        if user_id not in self.wellness_profiles:
            self.wellness_profiles[user_id] = {}
        
        self.wellness_profiles[user_id]["mood_trend"] = mood_trend
        self.wellness_profiles[user_id]["last_analysis"] = datetime.utcnow()
    
    async def _check_wellness_alerts(self, user_id: str, mood_entry: MoodEntry):
        """Check for wellness alerts"""
        
        alerts = []
        
        # Check for concerning mood patterns
        if mood_entry.mood in [MoodState.VERY_SAD, MoodState.ANXIOUS]:
            recent_entries = self._get_recent_mood_entries(user_id, days=3)
            concerning_moods = [
                entry for entry in recent_entries 
                if entry.mood in [MoodState.VERY_SAD, MoodState.ANXIOUS, MoodState.STRESSED]
            ]
            
            if len(concerning_moods) >= 2:
                alert = WellnessAlert(
                    user_id=user_id,
                    alert_type="mood_concern",
                    severity="medium",
                    message="Concerning mood pattern detected",
                    recommendations=await self._generate_mood_recommendations(user_id),
                    timestamp=datetime.utcnow(),
                    requires_intervention=True
                )
                alerts.append(alert)
        
        # Check for high stress levels
        if mood_entry.stress_level in [StressLevel.HIGH, StressLevel.VERY_HIGH]:
            alert = WellnessAlert(
                user_id=user_id,
                alert_type="high_stress",
                severity="high" if mood_entry.stress_level == StressLevel.VERY_HIGH else "medium",
                message="High stress level detected",
                recommendations=await self._generate_stress_recommendations(user_id),
                timestamp=datetime.utcnow(),
                requires_intervention=True
            )
            alerts.append(alert)
        
        # Process alerts
        for alert in alerts:
            await self._process_wellness_alert(alert)
    
    def _get_recent_mood_entries(self, user_id: str, days: int) -> List[MoodEntry]:
        """Get recent mood entries for user"""
        
        if user_id not in self.mood_entries:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [
            entry for entry in self.mood_entries[user_id]
            if entry.timestamp >= cutoff_date
        ]
    
    async def _extract_stress_indicators(self, behavior_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract stress indicators from behavior data"""
        
        indicators = {}
        
        # Learning performance indicators
        indicators["completion_rate"] = behavior_data.get("completion_rate", 0.5)
        indicators["error_rate"] = behavior_data.get("error_rate", 0.1)
        indicators["time_per_task"] = behavior_data.get("avg_time_per_task", 300)
        
        # Interaction patterns
        indicators["click_frequency"] = behavior_data.get("clicks_per_minute", 10)
        indicators["pause_frequency"] = behavior_data.get("pauses_per_hour", 5)
        indicators["session_duration"] = behavior_data.get("session_duration", 1800)
        
        # Navigation patterns
        indicators["back_navigation"] = behavior_data.get("back_navigations", 0)
        indicators["help_requests"] = behavior_data.get("help_requests", 0)
        indicators["retry_attempts"] = behavior_data.get("retry_attempts", 0)
        
        return indicators
    
    async def _predict_stress_level(self, indicators: Dict[str, float]) -> Dict[str, Any]:
        """Predict stress level using ML model"""
        
        # Prepare features
        features = np.array(list(indicators.values())).reshape(1, -1)
        
        # Scale features
        if hasattr(self.stress_detectors["scaler"], "transform"):
            features = self.stress_detectors["scaler"].transform(features)
        
        # Predict anomaly (high stress)
        anomaly_score = self.stress_detectors["anomaly_detector"].decision_function(features)[0]
        is_anomaly = self.stress_detectors["anomaly_detector"].predict(features)[0]
        
        # Convert to stress level (0-1)
        stress_level = max(0, min(1, (1 - anomaly_score) / 2))
        
        return {
            "stress_level": stress_level,
            "confidence": abs(anomaly_score),
            "is_anomaly": is_anomaly == -1,
            "contributing_factors": await self._identify_stress_factors(indicators)
        }
    
    async def _generate_stress_reduction_recommendations(
        self, 
        user_id: str, 
        stress_prediction: Dict[str, Any]
    ) -> List[str]:
        """Generate stress reduction recommendations"""
        
        recommendations = []
        stress_level = stress_prediction["stress_level"]
        
        if stress_level > 0.8:
            recommendations.extend([
                "Take a 10-minute break from learning",
                "Try a breathing exercise",
                "Consider ending the session and resuming later",
                "Reach out to a friend or counselor"
            ])
        elif stress_level > 0.6:
            recommendations.extend([
                "Take a 5-minute break",
                "Try a quick relaxation exercise",
                "Switch to easier content temporarily",
                "Ensure you're in a comfortable environment"
            ])
        else:
            recommendations.extend([
                "Continue with current pace",
                "Stay hydrated",
                "Take regular breaks"
            ])
        
        return recommendations
    
    async def _analyze_mood_trends(self, entries: List[MoodEntry]) -> Optional[WellnessInsight]:
        """Analyze mood trends from entries"""
        
        if len(entries) < 5:
            return None
        
        # Convert moods to numeric values for trend analysis
        mood_values = [self._mood_to_numeric(entry.mood) for entry in entries]
        
        # Calculate trend
        trend = await self._calculate_trend(mood_values)
        current_avg = np.mean(mood_values[-3:])  # Last 3 entries
        
        # Generate recommendation
        if trend < -0.1:
            recommendation = "Your mood has been declining. Consider stress reduction activities."
        elif trend > 0.1:
            recommendation = "Your mood is improving! Keep up the positive activities."
        else:
            recommendation = "Your mood is stable. Continue current wellness practices."
        
        return WellnessInsight(
            metric=WellnessMetric.MOOD,
            current_value=current_avg,
            trend="declining" if trend < -0.1 else "improving" if trend > 0.1 else "stable",
            recommendation=recommendation,
            confidence=0.8,
            supporting_data={"trend_value": trend, "sample_size": len(entries)}
        )
    
    def _mood_to_numeric(self, mood: MoodState) -> float:
        """Convert mood to numeric value for analysis"""
        
        mood_mapping = {
            MoodState.VERY_SAD: 1.0,
            MoodState.SAD: 2.0,
            MoodState.FRUSTRATED: 2.5,
            MoodState.ANXIOUS: 2.5,
            MoodState.STRESSED: 3.0,
            MoodState.NEUTRAL: 3.5,
            MoodState.CALM: 4.0,
            MoodState.HAPPY: 4.5,
            MoodState.EXCITED: 4.5,
            MoodState.VERY_HAPPY: 5.0
        }
        
        return mood_mapping.get(mood, 3.5)
    
    async def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend from values using linear regression"""
        
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Simple linear regression
        slope = np.corrcoef(x, y)[0, 1] * (np.std(y) / np.std(x))
        
        return slope
    
    async def _should_suggest_break(
        self, 
        user_id: str, 
        session_indicators: Dict[str, float]
    ) -> bool:
        """Determine if break should be suggested"""
        
        # Check session duration
        if session_indicators.get("session_duration", 0) > 90:  # 90 minutes
            return True
        
        # Check error rate
        if session_indicators.get("error_rate", 0) > 0.3:  # 30% error rate
            return True
        
        # Check pause frequency
        if session_indicators.get("pause_frequency", 0) > 10:  # 10 pauses per hour
            return True
        
        # Check recent mood entries
        recent_entries = self._get_recent_mood_entries(user_id, days=1)
        if recent_entries:
            latest_entry = recent_entries[-1]
            if latest_entry.stress_level in [StressLevel.HIGH, StressLevel.VERY_HIGH]:
                return True
        
        return False
    
    async def _process_wellness_alert(self, alert: WellnessAlert):
        """Process wellness alert"""
        
        # Log alert
        logger.info(f"Wellness alert for user {alert.user_id}: {alert.message}")
        
        # Send notification to user
        # Implementation for sending wellness notifications
        
        # Alert support team if necessary
        if alert.requires_intervention:
            await self._alert_wellness_team(alert)
    
    async def _alert_wellness_team(self, alert: WellnessAlert):
        """Alert wellness support team"""
        
        # Implementation for alerting support team
        logger.info(f"Alerting wellness team for user {alert.user_id}")
    
    async def cleanup(self):
        """Cleanup mental health service resources"""
        logger.info("Mental Health Service cleaned up")