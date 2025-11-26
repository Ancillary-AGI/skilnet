"""
Advanced Analytics Dashboard - Comprehensive Learning Insights
Superior to basic analytics with predictive modeling and actionable recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid
import statistics
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of learning metrics"""
    COMPLETION_RATE = "completion_rate"
    ENGAGEMENT_SCORE = "engagement_score"
    TIME_TO_COMPLETION = "time_to_completion"
    ACCURACY_RATE = "accuracy_rate"
    RETENTION_RATE = "retention_rate"
    SATISFACTION_SCORE = "satisfaction_score"
    PROGRESS_VELOCITY = "progress_velocity"
    KNOWLEDGE_GAIN = "knowledge_gain"


@dataclass
class LearningMetrics:
    """Comprehensive learning metrics"""
    user_id: str
    course_id: str
    topic_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 1.0


@dataclass
class AnalyticsInsight:
    """Generated analytics insight"""
    insight_id: str
    user_id: str
    insight_type: str  # trend, prediction, recommendation, alert
    title: str
    description: str
    confidence: float
    actionable: bool
    priority: str  # low, medium, high, critical
    related_metrics: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PredictiveModel:
    """Predictive model for learning outcomes"""
    model_id: str
    model_type: str  # regression, classification, time_series
    target_metric: MetricType
    features: List[str]
    accuracy: float
    last_trained: datetime
    parameters: Dict[str, Any]


class AdvancedAnalyticsService:
    """Service wrapper for Advanced Analytics Engine"""

    def __init__(self):
        self.engine = AdvancedAnalyticsEngine()

    async def initialize(self):
        """Initialize the analytics service"""
        await self.engine.initialize()

    async def record_metrics(self, user_id: str, course_id: str, topic_id: str, metrics: Dict[str, float], metadata: Optional[Dict[str, Any]] = None):
        """Record learning metrics"""
        await self.engine.record_metrics(user_id, course_id, topic_id, metrics, metadata)

    async def generate_insights(self, user_id: str, course_id: str, analysis_depth: str = "medium") -> List[AnalyticsInsight]:
        """Generate insights"""
        return await self.engine.generate_insights(user_id, course_id, analysis_depth)

    async def predict_learning_outcomes(self, user_id: str, course_id: str, prediction_horizon_days: int = 30) -> Dict[str, Any]:
        """Predict learning outcomes"""
        return await self.engine.predict_learning_outcomes(user_id, course_id, prediction_horizon_days)

    async def generate_comparative_analysis(self, user_id: str, course_id: str, comparison_group: str = "course_average") -> Dict[str, Any]:
        """Generate comparative analysis"""
        return await self.engine.generate_comparative_analysis(user_id, course_id, comparison_group)

    async def detect_learning_patterns(self, user_id: str, course_id: str, pattern_types: List[str] = None) -> Dict[str, Any]:
        """Detect learning patterns"""
        return await self.engine.detect_learning_patterns(user_id, course_id, pattern_types)

    async def generate_early_warning_alerts(self, user_id: str, course_id: str) -> List[Dict[str, Any]]:
        """Generate early warning alerts"""
        return await self.engine.generate_early_warning_alerts(user_id, course_id)

    async def generate_learning_dashboard(self, user_id: str, course_id: str, dashboard_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate learning dashboard"""
        return await self.engine.generate_learning_dashboard(user_id, course_id, dashboard_type)

    async def get_analytics_report(self, user_id: str, course_id: str, report_type: str = "comprehensive", date_range_days: int = 30) -> Dict[str, Any]:
        """Generate analytics report"""
        return await self.engine.get_analytics_report(user_id, course_id, report_type, date_range_days)

    async def get_user_performance_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user performance history"""
        # Mock implementation - in production would query database
        return [
            {"course_id": "sample_course", "score": 85, "completed": True, "date": "2024-01-01"},
            {"course_id": "sample_course2", "score": 90, "completed": True, "date": "2024-02-01"}
        ]

    async def get_course_completion_analytics(self, course_id: str) -> Dict[str, Any]:
        """Get course completion analytics"""
        # Mock implementation
        return {
            "completion_rate": 0.75,
            "average_score": 82.5,
            "total_enrollments": 1000,
            "total_completions": 750
        }

    async def cleanup(self):
        """Cleanup resources"""
        await self.engine.cleanup()


class AdvancedAnalyticsEngine:
    """
    Advanced analytics system that surpasses basic learning dashboards

    Features:
    - Predictive modeling for learning outcomes
    - Real-time trend analysis
    - Automated insight generation
    - Comparative benchmarking
    - Risk identification and early warning
    - Personalized recommendations
    - Multi-dimensional performance tracking
    """

    def __init__(self):
        self.metrics_data: Dict[str, List[LearningMetrics]] = defaultdict(list)
        self.insights: Dict[str, List[AnalyticsInsight]] = defaultdict(list)
        self.predictive_models: Dict[str, PredictiveModel] = {}
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.trend_analysis: Dict[str, Dict[str, Any]] = {}

        # Analytics configuration
        self.analysis_windows = {
            "short_term": timedelta(days=7),
            "medium_term": timedelta(days=30),
            "long_term": timedelta(days=90)
        }

        # Alert thresholds
        self.alert_thresholds = {
            "engagement_drop": 0.3,
            "completion_delay": 2.0,
            "accuracy_decline": 0.25,
            "retention_loss": 0.4
        }

    async def initialize(self):
        """Initialize the analytics engine"""
        await self._initialize_predictive_models()
        await self._load_baselines()
        logger.info("🚀 Advanced analytics engine initialized")

    async def record_metrics(
        self,
        user_id: str,
        course_id: str,
        topic_id: str,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record learning metrics for analysis"""

        timestamp = datetime.utcnow()

        for metric_type_str, value in metrics.items():
            try:
                metric_type = MetricType(metric_type_str)

                learning_metric = LearningMetrics(
                    user_id=user_id,
                    course_id=course_id,
                    topic_id=topic_id,
                    metric_type=metric_type,
                    value=value,
                    timestamp=timestamp,
                    metadata=metadata or {},
                    confidence_score=self._calculate_metric_confidence(metric_type, value)
                )

                # Store metrics with user as key
                key = f"{user_id}:{course_id}:{topic_id}"
                self.metrics_data[key].append(learning_metric)

                # Keep only last 1000 metrics per user/course/topic
                if len(self.metrics_data[key]) > 1000:
                    self.metrics_data[key] = self.metrics_data[key][-1000:]

            except ValueError:
                logger.warning(f"Unknown metric type: {metric_type_str}")

        # Trigger analysis
        await self._analyze_user_progress(user_id, course_id)

    async def generate_insights(
        self,
        user_id: str,
        course_id: str,
        analysis_depth: str = "medium"
    ) -> List[AnalyticsInsight]:
        """Generate actionable insights for user"""

        insights = []

        # Trend analysis insights
        trend_insights = await self._generate_trend_insights(user_id, course_id)
        insights.extend(trend_insights)

        # Predictive insights
        predictive_insights = await self._generate_predictive_insights(user_id, course_id)
        insights.extend(predictive_insights)

        # Comparative insights
        comparative_insights = await self._generate_comparative_insights(user_id, course_id)
        insights.extend(comparative_insights)

        # Risk assessment insights
        risk_insights = await self._generate_risk_insights(user_id, course_id)
        insights.extend(risk_insights)

        # Store insights
        self.insights[user_id].extend(insights)

        # Keep only last 100 insights per user
        if len(self.insights[user_id]) > 100:
            self.insights[user_id] = self.insights[user_id][-100:]

        logger.info(f"💡 Generated {len(insights)} insights for user {user_id}")
        return insights

    async def predict_learning_outcomes(
        self,
        user_id: str,
        course_id: str,
        prediction_horizon_days: int = 30
    ) -> Dict[str, Any]:
        """Predict future learning outcomes"""

        # Get user's historical data
        user_metrics = []
        for key, metrics in self.metrics_data.items():
            if key.startswith(f"{user_id}:{course_id}:"):
                user_metrics.extend(metrics)

        if not user_metrics:
            return {"error": "Insufficient data for prediction"}

        # Prepare features for prediction
        features = await self._extract_prediction_features(user_metrics)

        # Generate predictions for each metric type
        predictions = {}
        for metric_type in MetricType:
            prediction = await self._predict_metric_trend(
                metric_type, features, prediction_horizon_days
            )
            predictions[metric_type.value] = prediction

        # Overall success prediction
        overall_success_probability = await self._calculate_overall_success_probability(predictions)

        # Risk assessment
        risk_factors = await self._assess_completion_risks(user_id, course_id, predictions)

        return {
            "user_id": user_id,
            "course_id": course_id,
            "prediction_horizon_days": prediction_horizon_days,
            "predictions": predictions,
            "overall_success_probability": overall_success_probability,
            "risk_factors": risk_factors,
            "confidence_score": await self._calculate_prediction_confidence(features),
            "predicted_completion_date": await self._predict_completion_date(
                user_id, course_id, overall_success_probability
            ),
            "recommended_actions": await self._generate_recommended_actions(
                predictions, risk_factors
            )
        }

    async def generate_comparative_analysis(
        self,
        user_id: str,
        course_id: str,
        comparison_group: str = "course_average"
    ) -> Dict[str, Any]:
        """Generate comparative analysis against peers"""

        user_metrics = await self._get_user_course_metrics(user_id, course_id)

        if comparison_group == "course_average":
            comparison_metrics = await self._get_course_average_metrics(course_id)
        elif comparison_group == "similar_learners":
            comparison_metrics = await self._get_similar_learners_metrics(user_id, course_id)
        else:
            comparison_metrics = await self._get_course_average_metrics(course_id)

        # Calculate comparative scores
        comparative_scores = {}
        for metric_type in MetricType:
            user_value = await self._get_latest_metric_value(user_metrics, metric_type)
            comparison_value = await self._get_latest_metric_value(comparison_metrics, metric_type)

            if user_value is not None and comparison_value is not None:
                percentile_rank = await self._calculate_percentile_rank(
                    user_value, metric_type, course_id
                )

                comparative_scores[metric_type.value] = {
                    "user_value": user_value,
                    "comparison_value": comparison_value,
                    "difference": user_value - comparison_value,
                    "percentile_rank": percentile_rank,
                    "performance_level": await self._categorize_performance_level(percentile_rank)
                }

        # Generate comparative insights
        strengths = [k for k, v in comparative_scores.items() if v["percentile_rank"] > 0.7]
        areas_for_improvement = [k for k, v in comparative_scores.items() if v["percentile_rank"] < 0.3]

        return {
            "user_id": user_id,
            "course_id": course_id,
            "comparison_group": comparison_group,
            "comparative_scores": comparative_scores,
            "overall_percentile_rank": sum(v["percentile_rank"] for v in comparative_scores.values()) / len(comparative_scores),
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "benchmark_insights": await self._generate_benchmark_insights(comparative_scores)
        }

    async def detect_learning_patterns(
        self,
        user_id: str,
        course_id: str,
        pattern_types: List[str] = None
    ) -> Dict[str, Any]:
        """Detect learning patterns and behaviors"""

        if pattern_types is None:
            pattern_types = ["time_patterns", "engagement_patterns", "difficulty_patterns", "retention_patterns"]

        user_metrics = await self._get_user_course_metrics(user_id, course_id)

        patterns = {}

        if "time_patterns" in pattern_types:
            patterns["time_patterns"] = await self._analyze_time_patterns(user_metrics)

        if "engagement_patterns" in pattern_types:
            patterns["engagement_patterns"] = await self._analyze_engagement_patterns(user_metrics)

        if "difficulty_patterns" in pattern_types:
            patterns["difficulty_patterns"] = await self._analyze_difficulty_patterns(user_metrics)

        if "retention_patterns" in pattern_types:
            patterns["retention_patterns"] = await self._analyze_retention_patterns(user_metrics)

        # Generate pattern-based recommendations
        recommendations = await self._generate_pattern_recommendations(patterns)

        return {
            "user_id": user_id,
            "course_id": course_id,
            "detected_patterns": patterns,
            "pattern_strength": await self._calculate_pattern_strength(patterns),
            "recommendations": recommendations,
            "confidence_score": await self._calculate_pattern_confidence(user_metrics)
        }

    async def generate_early_warning_alerts(
        self,
        user_id: str,
        course_id: str
    ) -> List[Dict[str, Any]]:
        """Generate early warning alerts for at-risk students"""

        alerts = []
        user_metrics = await self._get_user_course_metrics(user_id, course_id)

        # Engagement drop alert
        engagement_trend = await self._calculate_metric_trend(user_metrics, MetricType.ENGAGEMENT_SCORE)
        if engagement_trend["direction"] == "declining" and abs(engagement_trend["slope"]) > self.alert_thresholds["engagement_drop"]:
            alerts.append({
                "alert_type": "engagement_drop",
                "severity": "high",
                "title": "Decreasing Engagement Detected",
                "description": f"Engagement has dropped by {abs(engagement_trend['slope']):.2f} over the last 7 days",
                "recommended_actions": [
                    "Schedule one-on-one check-in",
                    "Review content relevance",
                    "Adjust difficulty level"
                ],
                "metric_data": engagement_trend
            })

        # Completion delay alert
        completion_trend = await self._calculate_metric_trend(user_metrics, MetricType.TIME_TO_COMPLETION)
        if completion_trend["direction"] == "increasing":
            delay_factor = completion_trend["slope"]
            if delay_factor > self.alert_thresholds["completion_delay"]:
                alerts.append({
                    "alert_type": "completion_delay",
                    "severity": "medium",
                    "title": "Slower Progress Detected",
                "description": f"Content completion is taking {delay_factor:.1f}x longer than expected",
                    "recommended_actions": [
                        "Provide additional time management support",
                        "Break content into smaller chunks",
                        "Review prerequisite knowledge"
                    ],
                    "metric_data": completion_trend
                })

        # Accuracy decline alert
        accuracy_trend = await self._calculate_metric_trend(user_metrics, MetricType.ACCURACY_RATE)
        if accuracy_trend["direction"] == "declining" and abs(accuracy_trend["slope"]) > self.alert_thresholds["accuracy_decline"]:
            alerts.append({
                "alert_type": "accuracy_decline",
                "severity": "high",
                "title": "Learning Effectiveness Declining",
                "description": f"Accuracy has decreased by {abs(accuracy_trend['slope']):.2f} recently",
                "recommended_actions": [
                    "Provide remedial content",
                    "Schedule tutoring session",
                    "Adjust difficulty level downward"
                ],
                "metric_data": accuracy_trend
            })

        # Retention risk alert
        retention_metrics = await self._calculate_retention_metrics(user_metrics)
        if retention_metrics["risk_score"] > self.alert_thresholds["retention_loss"]:
            alerts.append({
                "alert_type": "retention_risk",
                "severity": "critical",
                "title": "High Risk of Non-Completion",
                "description": f"Retention risk score: {retention_metrics['risk_score']:.2f}",
                "recommended_actions": [
                    "Immediate intervention required",
                    "Personalized support plan",
                    "Alternative learning path"
                ],
                "metric_data": retention_metrics
            })

        logger.info(f"🚨 Generated {len(alerts)} early warning alerts for user {user_id}")
        return alerts

    async def generate_learning_dashboard(
        self,
        user_id: str,
        course_id: str,
        dashboard_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate comprehensive learning dashboard"""

        # Get all relevant data
        user_metrics = await self._get_user_course_metrics(user_id, course_id)
        insights = await self.generate_insights(user_id, course_id)
        predictions = await self.predict_learning_outcomes(user_id, course_id)
        comparative_analysis = await self.generate_comparative_analysis(user_id, course_id)
        patterns = await self.detect_learning_patterns(user_id, course_id)
        alerts = await self.generate_early_warning_alerts(user_id, course_id)

        # Generate dashboard sections
        dashboard = {
            "user_id": user_id,
            "course_id": course_id,
            "generated_at": datetime.utcnow().isoformat(),
            "dashboard_type": dashboard_type,
            "summary": await self._generate_dashboard_summary(user_metrics, predictions),
            "key_metrics": await self._get_key_metrics_summary(user_metrics),
            "progress_tracking": await self._generate_progress_tracking(user_metrics),
            "insights": [self._insight_to_dict(insight) for insight in insights[-5:]],  # Last 5 insights
            "predictions": predictions,
            "comparative_analysis": comparative_analysis,
            "learning_patterns": patterns,
            "alerts": alerts,
            "recommendations": await self._generate_dashboard_recommendations(
                insights, predictions, alerts
            )
        }

        return dashboard

    # Private helper methods

    async def _initialize_predictive_models(self):
        """Initialize predictive models"""

        # Linear regression model for completion time prediction
        self.predictive_models["completion_time_regression"] = PredictiveModel(
            model_id="completion_time_lr",
            model_type="linear_regression",
            target_metric=MetricType.TIME_TO_COMPLETION,
            features=["engagement_score", "difficulty_rating", "pace_factor"],
            accuracy=0.85,
            last_trained=datetime.utcnow(),
            parameters={"learning_rate": 0.01, "epochs": 1000}
        )

        # Classification model for success prediction
        self.predictive_models["success_classification"] = PredictiveModel(
            model_id="success_classifier",
            model_type="random_forest",
            target_metric=MetricType.COMPLETION_RATE,
            features=["accuracy_rate", "engagement_score", "time_to_completion"],
            accuracy=0.78,
            last_trained=datetime.utcnow(),
            parameters={"n_estimators": 100, "max_depth": 10}
        )

        logger.info("🤖 Predictive models initialized")

    async def _load_baselines(self):
        """Load baseline metrics for comparison"""

        # In production, these would be loaded from a database or configuration
        self.baselines = {
            "global_averages": {
                MetricType.COMPLETION_RATE.value: 0.75,
                MetricType.ENGAGEMENT_SCORE.value: 0.65,
                MetricType.ACCURACY_RATE.value: 0.70,
                MetricType.TIME_TO_COMPLETION.value: 1.0,
                MetricType.SATISFACTION_SCORE.value: 0.80
            },
            "course_specific_baselines": {},
            "skill_level_baselines": {}
        }

    async def _analyze_user_progress(self, user_id: str, course_id: str):
        """Analyze user progress and trigger insights"""

        user_metrics = await self._get_user_course_metrics(user_id, course_id)

        if len(user_metrics) < 5:  # Need minimum data points
            return

        # Calculate progress indicators
        completion_rate = await self._calculate_completion_rate(user_metrics)
        engagement_trend = await self._calculate_engagement_trend(user_metrics)
        performance_velocity = await self._calculate_performance_velocity(user_metrics)

        # Generate insights based on analysis
        if completion_rate < 0.5:
            insight = AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                insight_type="alert",
                title="Low Completion Rate Detected",
                description=f"Current completion rate is {completion_rate:.1%}, below the recommended 70%",
                confidence=0.8,
                actionable=True,
                priority="medium",
                related_metrics=["completion_rate", "engagement_score"]
            )
            self.insights[user_id].append(insight)

        if engagement_trend["slope"] < -0.1:
            insight = AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                insight_type="trend",
                title="Declining Engagement Trend",
                description="Engagement has been decreasing over the past week",
                confidence=0.9,
                actionable=True,
                priority="high",
                related_metrics=["engagement_score", "time_to_completion"]
            )
            self.insights[user_id].append(insight)

    async def _generate_trend_insights(self, user_id: str, course_id: str) -> List[AnalyticsInsight]:
        """Generate trend-based insights"""

        insights = []
        user_metrics = await self._get_user_course_metrics(user_id, course_id)

        for metric_type in MetricType:
            trend = await self._calculate_metric_trend(user_metrics, metric_type)

            if trend["significant"]:
                insight_type = "positive_trend" if trend["direction"] == "improving" else "negative_trend"

                insights.append(AnalyticsInsight(
                    insight_id=str(uuid.uuid4()),
                    user_id=user_id,
                    insight_type=insight_type,
                    title=f"{metric_type.value.replace('_', ' ').title()} Trend Detected",
                    description=trend["description"],
                    confidence=trend["confidence"],
                    actionable=trend["actionable"],
                    priority=trend["priority"],
                    related_metrics=[metric_type.value]
                ))

        return insights

    async def _generate_predictive_insights(self, user_id: str, course_id: str) -> List[AnalyticsInsight]:
        """Generate predictive insights"""

        insights = []
        predictions = await self.predict_learning_outcomes(user_id, course_id)

        if predictions.get("overall_success_probability", 0) < 0.6:
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                insight_type="prediction",
                title="Success Probability Below Threshold",
                description=f"Predicted success rate is {predictions['overall_success_probability']:.1%}",
                confidence=predictions.get("confidence_score", 0.5),
                actionable=True,
                priority="high",
                related_metrics=list(predictions.get("predictions", {}).keys())
            ))

        return insights

    async def _generate_comparative_insights(self, user_id: str, course_id: str) -> List[AnalyticsInsight]:
        """Generate comparative insights"""

        insights = []
        comparative = await self.generate_comparative_analysis(user_id, course_id)

        overall_rank = comparative.get("overall_percentile_rank", 0.5)

        if overall_rank > 0.8:
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                insight_type="achievement",
                title="Outstanding Performance",
                description=f"Performing in the top {int(overall_rank * 100)}% of learners",
                confidence=0.9,
                actionable=False,
                priority="low",
                related_metrics=list(comparative.get("comparative_scores", {}).keys())
            ))

        return insights

    async def _generate_risk_insights(self, user_id: str, course_id: str) -> List[AnalyticsInsight]:
        """Generate risk-based insights"""

        insights = []
        alerts = await self.generate_early_warning_alerts(user_id, course_id)

        for alert in alerts:
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                user_id=user_id,
                insight_type="risk_alert",
                title=alert["title"],
                description=alert["description"],
                confidence=0.8,
                actionable=True,
                priority=alert["severity"],
                related_metrics=list(alert.get("metric_data", {}).keys())
            ))

        return insights

    async def _calculate_metric_trend(
        self,
        metrics: List[LearningMetrics],
        metric_type: MetricType
    ) -> Dict[str, Any]:
        """Calculate trend for specific metric"""

        # Get metrics of specific type
        type_metrics = [m for m in metrics if m.metric_type == metric_type]

        if len(type_metrics) < 3:
            return {
                "direction": "insufficient_data",
                "slope": 0,
                "significant": False,
                "confidence": 0,
                "description": "Insufficient data for trend analysis"
            }

        # Sort by timestamp
        sorted_metrics = sorted(type_metrics, key=lambda x: x.timestamp)

        # Calculate linear trend
        timestamps = [(m.timestamp - sorted_metrics[0].timestamp).total_seconds() / 86400 for m in sorted_metrics]  # Days
        values = [m.value for m in sorted_metrics]

        if len(timestamps) > 1:
            # Simple linear regression
            n = len(timestamps)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0

            # Determine direction and significance
            if slope > 0.01:
                direction = "improving"
            elif slope < -0.01:
                direction = "declining"
            else:
                direction = "stable"

            significant = abs(slope) > 0.05  # Arbitrary threshold

            description = f"{metric_type.value} is {direction} with slope {slope:.3f}"
        else:
            direction = "stable"
            slope = 0
            significant = False
            description = "Insufficient data for trend calculation"

        return {
            "direction": direction,
            "slope": slope,
            "significant": significant,
            "confidence": min(len(type_metrics) / 10, 1.0),
            "description": description,
            "actionable": significant and direction in ["declining"],
            "priority": "high" if significant and direction == "declining" else "low"
        }

    async def _calculate_completion_rate(self, metrics: List[LearningMetrics]) -> float:
        """Calculate overall completion rate"""

        completion_metrics = [m for m in metrics if m.metric_type == MetricType.COMPLETION_RATE]

        if not completion_metrics:
            return 0.0

        return sum(m.value for m in completion_metrics) / len(completion_metrics)

    async def _calculate_engagement_trend(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Calculate engagement trend"""

        return await self._calculate_metric_trend(metrics, MetricType.ENGAGEMENT_SCORE)

    async def _calculate_performance_velocity(self, metrics: List[LearningMetrics]) -> float:
        """Calculate learning velocity"""

        # Simple velocity calculation based on progress over time
        progress_metrics = [m for m in metrics if m.metric_type == MetricType.PROGRESS_VELOCITY]

        if not progress_metrics:
            return 0.0

        return sum(m.value for m in progress_metrics) / len(progress_metrics)

    async def _extract_prediction_features(self, metrics: List[LearningMetrics]) -> Dict[str, float]:
        """Extract features for predictive modeling"""

        features = {}

        for metric_type in MetricType:
            type_metrics = [m for m in metrics if m.metric_type == metric_type]

            if type_metrics:
                values = [m.value for m in type_metrics]
                features[f"{metric_type.value}_mean"] = sum(values) / len(values)
                features[f"{metric_type.value}_std"] = statistics.stdev(values) if len(values) > 1 else 0
                features[f"{metric_type.value}_trend"] = await self._calculate_metric_trend(metrics, metric_type)

        return features

    async def _predict_metric_trend(
        self,
        metric_type: MetricType,
        features: Dict[str, float],
        horizon_days: int
    ) -> Dict[str, Any]:
        """Predict future trend for specific metric"""

        # Simple linear extrapolation (in production, use ML models)
        current_value = features.get(f"{metric_type.value}_mean", 0.5)
        trend_slope = features.get(f"{metric_type.value}_trend", 0)

        predicted_change = trend_slope * horizon_days
        predicted_value = max(min(current_value + predicted_change, 1.0), 0.0)

        return {
            "current_value": current_value,
            "predicted_value": predicted_value,
            "predicted_change": predicted_change,
            "confidence": features.get("confidence_score", 0.5),
            "horizon_days": horizon_days
        }

    async def _calculate_overall_success_probability(self, predictions: Dict[str, Any]) -> float:
        """Calculate overall success probability"""

        # Weighted combination of different metric predictions
        weights = {
            MetricType.COMPLETION_RATE.value: 0.4,
            MetricType.ENGAGEMENT_SCORE.value: 0.3,
            MetricType.ACCURACY_RATE.value: 0.3
        }

        total_weight = 0
        weighted_sum = 0

        for metric_name, prediction in predictions.items():
            if metric_name in weights:
                weight = weights[metric_name]
                value = prediction.get("predicted_value", 0.5)
                weighted_sum += value * weight
                total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    async def _assess_completion_risks(self, user_id: str, course_id: str, predictions: Dict[str, Any]) -> List[str]:
        """Assess risks to course completion"""

        risks = []

        # Low completion rate risk
        completion_pred = predictions.get(MetricType.COMPLETION_RATE.value, {})
        if completion_pred.get("predicted_value", 1.0) < 0.6:
            risks.append("Low predicted completion rate")

        # Engagement risk
        engagement_pred = predictions.get(MetricType.ENGAGEMENT_SCORE.value, {})
        if engagement_pred.get("predicted_value", 1.0) < 0.5:
            risks.append("Declining engagement predicted")

        # Time management risk
        time_pred = predictions.get(MetricType.TIME_TO_COMPLETION.value, {})
        if time_pred.get("predicted_value", 1.0) > 1.5:
            risks.append("Slower than expected progress")

        return risks

    async def _calculate_prediction_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in predictions"""

        # Base confidence on data availability
        data_points = sum(1 for k, v in features.items() if "_mean" in k and v is not None)

        return min(data_points / 10, 1.0)  # Up to 10 data points for full confidence

    async def _predict_completion_date(
        self,
        user_id: str,
        course_id: str,
        success_probability: float
    ) -> str:
        """Predict course completion date"""

        # Simple estimation based on success probability
        base_days = 30  # Assume 30 days for average course

        if success_probability > 0.8:
            estimated_days = base_days * 0.8  # Faster completion
        elif success_probability > 0.6:
            estimated_days = base_days
        else:
            estimated_days = base_days * 1.5  # Slower completion

        completion_date = datetime.utcnow() + timedelta(days=estimated_days)
        return completion_date.isoformat()

    async def _generate_recommended_actions(
        self,
        predictions: Dict[str, Any],
        risk_factors: List[str]
    ) -> List[str]:
        """Generate recommended actions based on predictions"""

        actions = []

        if "Low predicted completion rate" in risk_factors:
            actions.extend([
                "Schedule progress review meeting",
                "Provide additional learning resources",
                "Adjust course pacing"
            ])

        if "Declining engagement predicted" in risk_factors:
            actions.extend([
                "Introduce interactive elements",
                "Personalize content recommendations",
                "Schedule engagement check-in"
            ])

        if "Slower than expected progress" in risk_factors:
            actions.extend([
                "Provide time management strategies",
                "Break content into smaller modules",
                "Offer peer study groups"
            ])

        return actions

    async def _get_user_course_metrics(self, user_id: str, course_id: str) -> List[LearningMetrics]:
        """Get all metrics for user in specific course"""

        user_course_metrics = []
        for key, metrics in self.metrics_data.items():
            if key.startswith(f"{user_id}:{course_id}:"):
                user_course_metrics.extend(metrics)

        return user_course_metrics

    async def _get_course_average_metrics(self, course_id: str) -> List[LearningMetrics]:
        """Get average metrics for course"""

        # In production, this would aggregate metrics from all users in the course
        # For now, return baseline metrics
        course_metrics = []
        for metric_type in MetricType:
            course_metrics.append(LearningMetrics(
                user_id="course_average",
                course_id=course_id,
                topic_id="all",
                metric_type=metric_type,
                value=self.baselines["global_averages"].get(metric_type.value, 0.5),
                timestamp=datetime.utcnow()
            ))

        return course_metrics

    async def _get_similar_learners_metrics(self, user_id: str, course_id: str) -> List[LearningMetrics]:
        """Get metrics from similar learners"""

        # In production, this would find users with similar profiles
        # For now, return slightly modified course averages
        return await self._get_course_average_metrics(course_id)

    async def _get_latest_metric_value(self, metrics: List[LearningMetrics], metric_type: MetricType) -> Optional[float]:
        """Get latest value for specific metric type"""

        type_metrics = [m for m in metrics if m.metric_type == metric_type]

        if not type_metrics:
            return None

        # Return most recent value
        latest_metric = max(type_metrics, key=lambda x: x.timestamp)
        return latest_metric.value

    async def _calculate_percentile_rank(self, user_value: float, metric_type: MetricType, course_id: str) -> float:
        """Calculate percentile rank for user metric"""

        # In production, this would compare against actual course distribution
        # For now, use normal distribution assumption
        course_avg = self.baselines["global_averages"].get(metric_type.value, 0.5)
        course_std = 0.15  # Assumed standard deviation

        # Simple percentile calculation
        if user_value >= course_avg:
            return 0.5 + min((user_value - course_avg) / (2 * course_std), 0.5)
        else:
            return max((user_value - course_avg) / (2 * course_std) + 0.5, 0.0)

    async def _categorize_performance_level(self, percentile_rank: float) -> str:
        """Categorize performance level"""

        if percentile_rank >= 0.9:
            return "exceptional"
        elif percentile_rank >= 0.75:
            return "above_average"
        elif percentile_rank >= 0.25:
            return "average"
        elif percentile_rank >= 0.1:
            return "below_average"
        else:
            return "needs_improvement"

    async def _generate_benchmark_insights(self, comparative_scores: Dict[str, Any]) -> List[str]:
        """Generate insights from benchmark comparison"""

        insights = []

        for metric_name, scores in comparative_scores.items():
            if scores["percentile_rank"] > 0.8:
                insights.append(f"Excelling in {metric_name} compared to peers")
            elif scores["percentile_rank"] < 0.3:
                insights.append(f"May need support with {metric_name}")

        return insights

    async def _analyze_time_patterns(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Analyze learning time patterns"""

        # Extract time-based patterns
        time_patterns = {
            "most_productive_hours": [],
            "study_consistency": 0.0,
            "session_length_preference": 0,
            "break_frequency": 0
        }

        # Simple analysis (in production, use time series analysis)
        if len(metrics) > 10:
            # Mock analysis results
            time_patterns["most_productive_hours"] = [9, 10, 14, 15]  # 9-11 AM, 2-4 PM
            time_patterns["study_consistency"] = 0.7
            time_patterns["session_length_preference"] = 45  # minutes
            time_patterns["break_frequency"] = 60  # minutes

        return time_patterns

    async def _analyze_engagement_patterns(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Analyze engagement patterns"""

        engagement_metrics = [m for m in metrics if m.metric_type == MetricType.ENGAGEMENT_SCORE]

        if not engagement_metrics:
            return {"pattern": "insufficient_data"}

        values = [m.value for m in engagement_metrics]
        avg_engagement = sum(values) / len(values)

        return {
            "average_engagement": avg_engagement,
            "engagement_volatility": statistics.stdev(values) if len(values) > 1 else 0,
            "engagement_trend": "increasing" if values[-1] > avg_engagement else "decreasing",
            "peak_engagement_periods": await self._identify_peak_periods(engagement_metrics)
        }

    async def _analyze_difficulty_patterns(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Analyze difficulty progression patterns"""

        # This would analyze how difficulty preferences change over time
        return {
            "difficulty_progression_rate": 0.1,
            "optimal_challenge_level": 0.7,
            "frustration_threshold": 0.3
        }

    async def _analyze_retention_patterns(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Analyze knowledge retention patterns"""

        retention_metrics = [m for m in metrics if m.metric_type == MetricType.RETENTION_RATE]

        if not retention_metrics:
            return {"pattern": "insufficient_data"}

        return {
            "retention_rate": sum(m.value for m in retention_metrics) / len(retention_metrics),
            "forgetting_curve_fit": "standard",  # Ebbinghaus curve
            "review_effectiveness": 0.8
        }

    async def _generate_pattern_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on detected patterns"""

        recommendations = []

        if "time_patterns" in patterns:
            time_pattern = patterns["time_patterns"]
            if time_pattern["study_consistency"] < 0.6:
                recommendations.append("Establish regular study schedule during identified productive hours")

        if "engagement_patterns" in patterns:
            engagement_pattern = patterns["engagement_patterns"]
            if engagement_pattern["engagement_trend"] == "decreasing":
                recommendations.append("Introduce more interactive and varied content types")

        return recommendations

    async def _calculate_pattern_strength(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall strength of detected patterns"""

        # Simple calculation based on pattern completeness
        pattern_count = len([p for p in patterns.values() if p.get("pattern") != "insufficient_data"])
        return pattern_count / len(patterns)

    async def _calculate_pattern_confidence(self, metrics: List[LearningMetrics]) -> float:
        """Calculate confidence in pattern analysis"""

        return min(len(metrics) / 50, 1.0)  # More data = higher confidence

    async def _identify_peak_periods(self, metrics: List[LearningMetrics]) -> List[int]:
        """Identify peak engagement periods"""

        # Simple peak detection (in production, use proper time series analysis)
        if len(metrics) < 7:
            return []

        # Mock peak hours identification
        return [10, 15, 20]  # 10 AM, 3 PM, 8 PM

    async def _calculate_retention_metrics(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Calculate retention-related metrics"""

        retention_metrics = [m for m in metrics if m.metric_type == MetricType.RETENTION_RATE]

        if not retention_metrics:
            return {"risk_score": 0.5, "retention_rate": 0.5}

        avg_retention = sum(m.value for m in retention_metrics) / len(retention_metrics)

        # Calculate risk score (inverse of retention)
        risk_score = 1 - avg_retention

        return {
            "risk_score": risk_score,
            "retention_rate": avg_retention,
            "retention_trend": await self._calculate_metric_trend(metrics, MetricType.RETENTION_RATE)
        }

    async def _generate_dashboard_summary(
        self,
        metrics: List[LearningMetrics],
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate dashboard summary"""

        summary = {
            "total_metrics_recorded": len(metrics),
            "overall_success_probability": predictions.get("overall_success_probability", 0.5),
            "risk_level": "high" if predictions.get("overall_success_probability", 0.5) < 0.6 else "low",
            "last_updated": datetime.utcnow().isoformat()
        }

        return summary

    async def _get_key_metrics_summary(self, metrics: List[LearningMetrics]) -> Dict[str, float]:
        """Get summary of key metrics"""

        summary = {}

        for metric_type in MetricType:
            value = await self._get_latest_metric_value(metrics, metric_type)
            if value is not None:
                summary[metric_type.value] = value

        return summary

    async def _generate_progress_tracking(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Generate progress tracking data"""

        return {
            "milestones_achieved": len([m for m in metrics if m.metric_type == MetricType.COMPLETION_RATE and m.value > 0.8]),
            "current_streak_days": await self._calculate_current_streak(metrics),
            "average_session_length": await self._calculate_average_session_length(metrics),
            "learning_velocity": await self._calculate_performance_velocity(metrics)
        }

    async def _calculate_current_streak(self, metrics: List[LearningMetrics]) -> int:
        """Calculate current learning streak in days"""

        # Simple streak calculation (in production, use proper streak detection)
        return min(len(metrics) // 3, 30)  # Mock calculation

    async def _calculate_average_session_length(self, metrics: List[LearningMetrics]) -> int:
        """Calculate average session length in minutes"""

        time_metrics = [m for m in metrics if m.metric_type == MetricType.TIME_TO_COMPLETION]

        if not time_metrics:
            return 30  # Default

        return int(sum(m.value * 60 for m in time_metrics) / len(time_metrics))  # Convert to minutes

    async def _generate_dashboard_recommendations(
        self,
        insights: List[AnalyticsInsight],
        predictions: Dict[str, Any],
        alerts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate dashboard-level recommendations"""

        recommendations = []

        # High-priority insights
        high_priority_insights = [i for i in insights if i.priority in ["high", "critical"]]
        if high_priority_insights:
            recommendations.append(f"Address {len(high_priority_insights)} high-priority insights")

        # Risk factors
        if predictions.get("risk_factors"):
            recommendations.append(f"Mitigate {len(predictions['risk_factors'])} identified risk factors")

        # Active alerts
        if alerts:
            recommendations.append(f"Review {len(alerts)} active alerts")

        return recommendations

    def _calculate_metric_confidence(self, metric_type: MetricType, value: float) -> float:
        """Calculate confidence score for metric"""

        # Simple confidence calculation based on metric type and value consistency
        base_confidence = 0.8

        # Adjust based on value range (extreme values have lower confidence)
        if value < 0.1 or value > 0.9:
            base_confidence *= 0.8

        return base_confidence

    def _insight_to_dict(self, insight: AnalyticsInsight) -> Dict[str, Any]:
        """Convert insight to dictionary"""

        return {
            "insight_id": insight.insight_id,
            "insight_type": insight.insight_type,
            "title": insight.title,
            "description": insight.description,
            "confidence": insight.confidence,
            "actionable": insight.actionable,
            "priority": insight.priority,
            "related_metrics": insight.related_metrics,
            "generated_at": insight.generated_at.isoformat()
        }

    async def get_analytics_report(
        self,
        user_id: str,
        course_id: str,
        report_type: str = "comprehensive",
        date_range_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""

        # Get data within date range
        cutoff_date = datetime.utcnow() - timedelta(days=date_range_days)
        user_metrics = [
            m for m in await self._get_user_course_metrics(user_id, course_id)
            if m.timestamp >= cutoff_date
        ]

        report = {
            "report_type": report_type,
            "user_id": user_id,
            "course_id": course_id,
            "date_range_days": date_range_days,
            "generated_at": datetime.utcnow().isoformat(),
            "summary_statistics": await self._calculate_summary_statistics(user_metrics),
            "trend_analysis": await self._generate_trend_analysis(user_metrics),
            "predictive_insights": await self.predict_learning_outcomes(user_id, course_id, date_range_days),
            "comparative_analysis": await self.generate_comparative_analysis(user_id, course_id),
            "risk_assessment": await self._generate_risk_assessment(user_metrics),
            "recommendations": await self._generate_report_recommendations(user_metrics)
        }

        return report

    async def _calculate_summary_statistics(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Calculate summary statistics for metrics"""

        if not metrics:
            return {}

        stats = {}

        for metric_type in MetricType:
            type_metrics = [m for m in metrics if m.metric_type == metric_type]

            if type_metrics:
                values = [m.value for m in type_metrics]
                stats[metric_type.value] = {
                    "count": len(values),
                    "mean": sum(values) / len(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1]
                }

        return stats

    async def _generate_trend_analysis(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Generate comprehensive trend analysis"""

        trends = {}

        for metric_type in MetricType:
            trends[metric_type.value] = await self._calculate_metric_trend(metrics, metric_type)

        return trends

    async def _generate_risk_assessment(self, metrics: List[LearningMetrics]) -> Dict[str, Any]:
        """Generate risk assessment"""

        risk_scores = {}

        for metric_type in MetricType:
            trend = await self._calculate_metric_trend(metrics, metric_type)

            if trend["direction"] == "declining":
                risk_scores[metric_type.value] = abs(trend["slope"])
            else:
                risk_scores[metric_type.value] = 0

        overall_risk = sum(risk_scores.values()) / len(risk_scores) if risk_scores else 0

        return {
            "overall_risk_score": overall_risk,
            "risk_by_metric": risk_scores,
            "risk_level": "high" if overall_risk > 0.5 else "medium" if overall_risk > 0.2 else "low"
        }

    async def _generate_report_recommendations(self, metrics: List[LearningMetrics]) -> List[str]:
        """Generate recommendations for report"""

        recommendations = []

        # Analyze metric trends and generate recommendations
        for metric_type in MetricType:
            trend = await self._calculate_metric_trend(metrics, metric_type)

            if trend["direction"] == "declining" and trend["significant"]:
                recommendations.append(f"Focus on improving {metric_type.value.replace('_', ' ')}")

        if not recommendations:
            recommendations.append("Continue current learning approach - performing well")

        return recommendations

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("✅ Advanced analytics engine cleaned up")
