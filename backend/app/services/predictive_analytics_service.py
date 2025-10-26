"""
Predictive Analytics Service for Student Success Prediction
Uses machine learning to predict student outcomes and provide interventions
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import pickle
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class StudentProfile:
    """Student profile data for prediction"""
    student_id: str
    age: int
    education_level: str
    previous_gpa: float
    learning_style: str
    time_spent_studying: float
    engagement_score: float
    quiz_scores: List[float]
    assignment_completion_rate: float
    forum_participation: int
    course_progress: float
    socioeconomic_factors: Dict[str, Any]
    device_usage_patterns: Dict[str, Any]

@dataclass
class PredictionResult:
    """Prediction result with confidence and recommendations"""
    student_id: str
    predicted_outcome: str  # success, at_risk, dropout_risk
    confidence_score: float
    risk_factors: List[str]
    recommended_interventions: List[str]
    predicted_completion_time: Optional[datetime]
    success_probability: float
    generated_at: datetime

class PredictiveAnalyticsService:
    """Advanced predictive analytics for student success"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
        self.prediction_cache = {}

    async def initialize(self):
        """Initialize ML models and load training data"""
        try:
            logger.info("Initializing predictive analytics models...")

            # Load or train models
            await self._load_or_train_models()

            # Load feature importance data
            await self._load_feature_importance()

            logger.info("Predictive analytics models initialized")

        except Exception as e:
            logger.error(f"Failed to initialize predictive analytics: {e}")

    async def predict_student_success(self, student_id: str) -> Optional[PredictionResult]:
        """Predict student success outcome"""
        try:
            # Get student data
            student_profile = await self._get_student_profile(student_id)
            if not student_profile:
                return None

            # Check cache first
            cache_key = f"prediction_{student_id}_{datetime.utcnow().date()}"
            if cache_key in self.prediction_cache:
                return self.prediction_cache[cache_key]

            # Extract features
            features = self._extract_features(student_profile)

            # Make prediction
            prediction = await self._make_prediction(features, student_profile)

            # Generate interventions
            interventions = await self._generate_interventions(student_profile, prediction)

            # Create result
            result = PredictionResult(
                student_id=student_id,
                predicted_outcome=prediction['outcome'],
                confidence_score=prediction['confidence'],
                risk_factors=prediction['risk_factors'],
                recommended_interventions=interventions,
                predicted_completion_time=prediction.get('completion_time'),
                success_probability=prediction['success_probability'],
                generated_at=datetime.utcnow()
            )

            # Cache result
            self.prediction_cache[cache_key] = result

            # Save to database
            await self._save_prediction_result(result)

            return result

        except Exception as e:
            logger.error(f"Failed to predict student success: {e}")
            return None

    async def generate_personalized_recommendations(self, student_id: str) -> List[str]:
        """Generate personalized learning recommendations"""
        try:
            student_profile = await self._get_student_profile(student_id)
            if not student_profile:
                return []

            # Analyze learning patterns
            learning_patterns = await self._analyze_learning_patterns(student_profile)

            # Generate recommendations based on patterns
            recommendations = await self._generate_recommendations_from_patterns(learning_patterns)

            # Save recommendations
            await self._save_recommendations(student_id, recommendations)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []

    async def optimize_learning_pathway(self, student_id: str, target_skill: str) -> Dict[str, Any]:
        """Optimize learning pathway for student"""
        try:
            student_profile = await self._get_student_profile(student_id)
            if not student_profile:
                return {}

            # Analyze current progress
            current_progress = await self._analyze_current_progress(student_id)

            # Predict optimal pathway
            optimal_pathway = await self._predict_optimal_pathway(
                student_profile,
                target_skill,
                current_progress
            )

            # Save optimized pathway
            await self._save_optimized_pathway(student_id, target_skill, optimal_pathway)

            return optimal_pathway

        except Exception as e:
            logger.error(f"Failed to optimize learning pathway: {e}")
            return {}

    async def _load_or_train_models(self):
        """Load existing models or train new ones"""
        try:
            # Try to load existing models
            if await self._load_existing_models():
                logger.info("Loaded existing ML models")
                return

            # Train new models if none exist
            await self._train_models()
            logger.info("Trained new ML models")

        except Exception as e:
            logger.error(f"Failed to load/train models: {e}")

    async def _load_existing_models(self) -> bool:
        """Load existing trained models"""
        try:
            # Load models from storage
            model_files = [
                "student_success_model.pkl",
                "engagement_model.pkl",
                "dropout_prediction_model.pkl"
            ]

            for model_file in model_files:
                if await self._file_exists(model_file):
                    model = joblib.load(model_file)
                    self.models[model_file] = model

            return len(self.models) > 0

        except Exception as e:
            logger.error(f"Failed to load existing models: {e}")
            return False

    async def _train_models(self):
        """Train new ML models with historical data"""
        try:
            # Get historical training data
            training_data = await self._get_training_data()

            if not training_data:
                logger.warning("No training data available")
                return

            # Prepare features and labels
            X, y = self._prepare_training_data(training_data)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train models
            await self._train_success_prediction_model(X_train, X_test, y_train, y_test)
            await self._train_engagement_model(X_train, X_test, y_train, y_test)
            await self._train_dropout_prediction_model(X_train, X_test, y_train, y_test)

            # Save models
            await self._save_models()

        except Exception as e:
            logger.error(f"Failed to train models: {e}")

    async def _train_success_prediction_model(self, X_train, X_test, y_train, y_test):
        """Train student success prediction model"""
        try:
            # Initialize model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

            # Train model
            model.fit(X_train, y_train)

            # Evaluate model
            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)

            # Save model
            self.models['success_prediction'] = model
            self.model_performance['success_prediction'] = {
                'accuracy': accuracy,
                'feature_importance': model.feature_importances_.tolist()
            }

            logger.info(f"Success prediction model trained with accuracy: {accuracy:.3f}")

        except Exception as e:
            logger.error(f"Failed to train success prediction model: {e}")

    async def _train_engagement_model(self, X_train, X_test, y_train, y_test):
        """Train student engagement prediction model"""
        try:
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                random_state=42
            )

            model.fit(X_train, y_train)

            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)

            self.models['engagement_prediction'] = model
            self.model_performance['engagement_prediction'] = {
                'accuracy': accuracy
            }

            logger.info(f"Engagement prediction model trained with accuracy: {accuracy:.3f}")

        except Exception as e:
            logger.error(f"Failed to train engagement model: {e}")

    async def _train_dropout_prediction_model(self, X_train, X_test, y_train, y_test):
        """Train dropout prediction model"""
        try:
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                random_state=42
            )

            model.fit(X_train, y_train)

            predictions = model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)

            self.models['dropout_prediction'] = model
            self.model_performance['dropout_prediction'] = {
                'accuracy': accuracy
            }

            logger.info(f"Dropout prediction model trained with accuracy: {accuracy:.3f}")

        except Exception as e:
            logger.error(f"Failed to train dropout prediction model: {e}")

    def _extract_features(self, student_profile: StudentProfile) -> np.ndarray:
        """Extract features for ML model"""
        features = [
            student_profile.age,
            self._encode_education_level(student_profile.education_level),
            student_profile.previous_gpa,
            self._encode_learning_style(student_profile.learning_style),
            student_profile.time_spent_studying,
            student_profile.engagement_score,
            np.mean(student_profile.quiz_scores) if student_profile.quiz_scores else 0,
            student_profile.assignment_completion_rate,
            student_profile.forum_participation,
            student_profile.course_progress,
            self._extract_socioeconomic_features(student_profile.socioeconomic_factors),
            self._extract_device_features(student_profile.device_usage_patterns)
        ]

        return np.array(features).reshape(1, -1)

    def _encode_education_level(self, level: str) -> float:
        """Encode education level to numeric value"""
        encoding = {
            'high_school': 0.0,
            'bachelors': 1.0,
            'masters': 2.0,
            'phd': 3.0
        }
        return encoding.get(level.lower(), 0.5)

    def _encode_learning_style(self, style: str) -> float:
        """Encode learning style to numeric value"""
        encoding = {
            'visual': 0.0,
            'auditory': 1.0,
            'kinesthetic': 2.0,
            'reading': 3.0
        }
        return encoding.get(style.lower(), 0.0)

    def _extract_socioeconomic_features(self, factors: Dict[str, Any]) -> float:
        """Extract socioeconomic features"""
        # Implement socioeconomic feature extraction
        return 0.5  # Placeholder

    def _extract_device_features(self, patterns: Dict[str, Any]) -> float:
        """Extract device usage features"""
        # Implement device usage feature extraction
        return 0.5  # Placeholder

    async def _make_prediction(self, features: np.ndarray, student_profile: StudentProfile) -> Dict[str, Any]:
        """Make prediction using trained models"""
        try:
            # Normalize features
            normalized_features = self.scalers['main'].transform(features)

            # Get predictions from different models
            success_prediction = self.models['success_prediction'].predict_proba(normalized_features)[0]
            engagement_prediction = self.models['engagement_prediction'].predict_proba(normalized_features)[0]
            dropout_prediction = self.models['dropout_prediction'].predict_proba(normalized_features)[0]

            # Combine predictions
            combined_prediction = self._combine_predictions(
                success_prediction,
                engagement_prediction,
                dropout_prediction
            )

            # Identify risk factors
            risk_factors = self._identify_risk_factors(
                student_profile,
                combined_prediction,
                normalized_features
            )

            return {
                'outcome': combined_prediction['outcome'],
                'confidence': combined_prediction['confidence'],
                'risk_factors': risk_factors,
                'success_probability': combined_prediction['success_probability'],
                'completion_time': combined_prediction.get('completion_time')
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'outcome': 'unknown',
                'confidence': 0.0,
                'risk_factors': [],
                'success_probability': 0.5
            }

    def _combine_predictions(self, success_pred, engagement_pred, dropout_pred) -> Dict[str, Any]:
        """Combine predictions from multiple models"""
        # Implement prediction combination logic
        success_prob = success_pred[1]  # Probability of success
        engagement_prob = engagement_pred[1]  # Probability of high engagement
        dropout_prob = dropout_pred[1]  # Probability of dropout

        # Weighted combination
        combined_success = (success_prob * 0.5) + (engagement_prob * 0.3) + ((1 - dropout_prob) * 0.2)

        if combined_success > 0.7:
            outcome = 'success'
        elif combined_success > 0.4:
            outcome = 'at_risk'
        else:
            outcome = 'dropout_risk'

        return {
            'outcome': outcome,
            'confidence': min(combined_success, 1.0),
            'success_probability': combined_success
        }

    def _identify_risk_factors(self, student_profile: StudentProfile, prediction: Dict[str, Any], features: np.ndarray) -> List[str]:
        """Identify risk factors for student"""
        risk_factors = []

        # Analyze different aspects
        if student_profile.engagement_score < 0.5:
            risk_factors.append('low_engagement')

        if student_profile.course_progress < 0.3:
            risk_factors.append('slow_progress')

        if student_profile.assignment_completion_rate < 0.6:
            risk_factors.append('incomplete_assignments')

        if student_profile.time_spent_studying < 5:  # Less than 5 hours per week
            risk_factors.append('insufficient_study_time')

        if np.mean(student_profile.quiz_scores) < 0.7:
            risk_factors.append('poor_quiz_performance')

        return risk_factors

    async def _generate_interventions(self, student_profile: StudentProfile, prediction: Dict[str, Any]) -> List[str]:
        """Generate personalized interventions"""
        interventions = []

        risk_factors = prediction['risk_factors']

        if 'low_engagement' in risk_factors:
            interventions.append('Schedule one-on-one tutoring sessions')
            interventions.append('Introduce gamification elements')
            interventions.append('Connect with study buddy')

        if 'slow_progress' in risk_factors:
            interventions.append('Provide additional learning resources')
            interventions.append('Extend assignment deadlines')
            interventions.append('Break down complex topics')

        if 'incomplete_assignments' in risk_factors:
            interventions.append('Send assignment reminders')
            interventions.append('Provide assignment templates')
            interventions.append('Offer assignment help sessions')

        if 'insufficient_study_time' in risk_factors:
            interventions.append('Recommend study schedule optimization')
            interventions.append('Provide time management resources')
            interventions.append('Set achievable study goals')

        if 'poor_quiz_performance' in risk_factors:
            interventions.append('Provide additional practice quizzes')
            interventions.append('Schedule review sessions')
            interventions.append('Recommend concept reinforcement')

        return interventions

    async def _get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Get comprehensive student profile"""
        try:
            db: Session = SessionLocal()

            # Query student data from database
            # This would join multiple tables to get complete profile

            # Mock data for development
            profile = StudentProfile(
                student_id=student_id,
                age=25,
                education_level='bachelors',
                previous_gpa=3.2,
                learning_style='visual',
                time_spent_studying=8.5,
                engagement_score=0.7,
                quiz_scores=[0.8, 0.9, 0.75, 0.85],
                assignment_completion_rate=0.9,
                forum_participation=15,
                course_progress=0.6,
                socioeconomic_factors={},
                device_usage_patterns={}
            )

            db.close()
            return profile

        except Exception as e:
            logger.error(f"Failed to get student profile: {e}")
            return None

    async def _get_training_data(self) -> Optional[pd.DataFrame]:
        """Get historical training data"""
        try:
            # Query historical student data
            # This would get data from student_performance, engagement_metrics, etc.

            # Mock training data for development
            data = {
                'age': [22, 25, 30, 28, 24],
                'education_level': [1.0, 2.0, 1.0, 2.0, 1.0],
                'previous_gpa': [3.5, 3.2, 2.8, 3.7, 3.1],
                'learning_style': [0.0, 1.0, 2.0, 0.0, 1.0],
                'study_time': [10, 8, 5, 12, 7],
                'engagement_score': [0.8, 0.7, 0.4, 0.9, 0.6],
                'quiz_avg': [0.85, 0.75, 0.55, 0.90, 0.70],
                'completion_rate': [0.95, 0.85, 0.60, 0.98, 0.80],
                'forum_posts': [20, 15, 5, 25, 12],
                'progress_rate': [0.8, 0.6, 0.3, 0.9, 0.5],
                'outcome': [1, 1, 0, 1, 0]  # 1 = success, 0 = at_risk
            }

            return pd.DataFrame(data)

        except Exception as e:
            logger.error(f"Failed to get training data: {e}")
            return None

    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for ML models"""
        # Separate features and labels
        feature_columns = [
            'age', 'education_level', 'previous_gpa', 'learning_style',
            'study_time', 'engagement_score', 'quiz_avg', 'completion_rate',
            'forum_posts', 'progress_rate'
        ]

        X = data[feature_columns].values
        y = data['outcome'].values

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        self.scalers['main'] = scaler

        return X_scaled, y

    async def _analyze_learning_patterns(self, student_profile: StudentProfile) -> Dict[str, Any]:
        """Analyze student learning patterns"""
        patterns = {
            'study_consistency': self._analyze_study_consistency(student_profile),
            'engagement_trends': self._analyze_engagement_trends(student_profile),
            'performance_patterns': self._analyze_performance_patterns(student_profile),
            'time_preferences': self._analyze_time_preferences(student_profile),
            'content_preferences': self._analyze_content_preferences(student_profile)
        }

        return patterns

    def _analyze_study_consistency(self, profile: StudentProfile) -> Dict[str, Any]:
        """Analyze study time consistency"""
        return {
            'consistency_score': 0.8,
            'optimal_study_times': ['morning', 'evening'],
            'recommended_breaks': 15
        }

    def _analyze_engagement_trends(self, profile: StudentProfile) -> Dict[str, Any]:
        """Analyze engagement trends"""
        return {
            'engagement_level': 'high' if profile.engagement_score > 0.7 else 'medium',
            'peak_engagement_times': ['10:00', '14:00'],
            'engagement_triggers': ['interactive_content', 'peer_discussion']
        }

    def _analyze_performance_patterns(self, profile: StudentProfile) -> Dict[str, Any]:
        """Analyze performance patterns"""
        avg_quiz_score = np.mean(profile.quiz_scores) if profile.quiz_scores else 0

        return {
            'quiz_performance': 'strong' if avg_quiz_score > 0.8 else 'needs_improvement',
            'assignment_completion': 'excellent' if profile.assignment_completion_rate > 0.9 else 'good',
            'overall_grade_trend': 'improving'
        }

    def _analyze_time_preferences(self, profile: StudentProfile) -> Dict[str, Any]:
        """Analyze preferred study times"""
        return {
            'preferred_times': ['morning', 'afternoon'],
            'session_duration_preference': 45,
            'break_frequency': 15
        }

    def _analyze_content_preferences(self, profile: StudentProfile) -> Dict[str, Any]:
        """Analyze content type preferences"""
        return {
            'preferred_content_types': ['video', 'interactive', 'visual'],
            'difficulty_preference': 'intermediate',
            'pace_preference': 'moderate'
        }

    async def _generate_recommendations_from_patterns(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on learning patterns"""
        recommendations = []

        # Study consistency recommendations
        if patterns['study_consistency']['consistency_score'] < 0.7:
            recommendations.append('Establish a consistent daily study routine')
            recommendations.append('Use study schedule reminders')

        # Engagement recommendations
        if patterns['engagement_trends']['engagement_level'] == 'medium':
            recommendations.append('Increase interactive content consumption')
            recommendations.append('Join study groups for peer motivation')

        # Performance recommendations
        if patterns['performance_patterns']['quiz_performance'] == 'needs_improvement':
            recommendations.append('Schedule additional quiz practice sessions')
            recommendations.append('Review fundamental concepts')

        # Time preference recommendations
        preferred_times = patterns['time_preferences']['preferred_times']
        if 'morning' in preferred_times:
            recommendations.append('Schedule important study sessions in the morning')

        return recommendations

    async def _analyze_current_progress(self, student_id: str) -> Dict[str, Any]:
        """Analyze current student progress"""
        # Query current progress from database
        return {
            'completed_lessons': 15,
            'total_lessons': 30,
            'current_grade': 0.75,
            'time_to_completion': 45,  # days
            'pace_status': 'on_track'
        }

    async def _predict_optimal_pathway(
        self,
        student_profile: StudentProfile,
        target_skill: str,
        current_progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict optimal learning pathway"""
        # Use ML model to predict optimal pathway
        return {
            'recommended_path': 'accelerated' if student_profile.engagement_score > 0.8 else 'standard',
            'estimated_completion': 60,  # days
            'milestones': [
                {'week': 2, 'topic': 'fundamentals', 'checkpoint': True},
                {'week': 4, 'topic': 'intermediate', 'checkpoint': True},
                {'week': 8, 'topic': 'advanced', 'checkpoint': False}
            ],
            'adaptive_adjustments': [
                'Increase pace if performance is strong',
                'Add review sessions if struggling',
                'Include peer collaboration opportunities'
            ]
        }

    async def _save_prediction_result(self, result: PredictionResult):
        """Save prediction result to database"""
        try:
            db: Session = SessionLocal()
            # Save prediction to database
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to save prediction result: {e}")

    async def _save_recommendations(self, student_id: str, recommendations: List[str]):
        """Save recommendations to database"""
        try:
            db: Session = SessionLocal()
            # Save recommendations
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to save recommendations: {e}")

    async def _save_optimized_pathway(self, student_id: str, target_skill: str, pathway: Dict[str, Any]):
        """Save optimized pathway to database"""
        try:
            db: Session = SessionLocal()
            # Save pathway
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to save optimized pathway: {e}")

    async def _save_models(self):
        """Save trained models to disk"""
        try:
            for model_name, model in self.models.items():
                filename = f"{model_name}.pkl"
                joblib.dump(model, filename)

            # Save scalers
            for scaler_name, scaler in self.scalers.items():
                filename = f"{scaler_name}_scaler.pkl"
                joblib.dump(scaler, filename)

        except Exception as e:
            logger.error(f"Failed to save models: {e}")

    async def _file_exists(self, filename: str) -> bool:
        """Check if file exists"""
        import os
        return os.path.exists(filename)

    async def _load_feature_importance(self):
        """Load feature importance data"""
        try:
            # Load from database or file
            self.feature_importance = {
                'engagement_score': 0.25,
                'quiz_scores': 0.20,
                'study_time': 0.15,
                'forum_participation': 0.12,
                'assignment_completion': 0.10,
                'course_progress': 0.18
            }
        except Exception as e:
            logger.error(f"Failed to load feature importance: {e}")

    async def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        return self.model_performance

    async def retrain_models(self):
        """Retrain models with new data"""
        await self._train_models()
        logger.info("Models retrained with latest data")

# Global predictive analytics service
predictive_analytics_service = PredictiveAnalyticsService()

# Initialize service
asyncio.create_task(predictive_analytics_service.initialize())
