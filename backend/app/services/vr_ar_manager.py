"""
VR/AR Manager for Immersive Learning Experiences
Handles 3D models, spatial audio, haptic feedback, and immersive environments
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
import numpy as np
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class VRSession:
    """Represents a VR learning session"""
    session_id: str
    user_id: str
    environment_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    interactions: List[Dict[str, Any]] = None
    gaze_data: List[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.interactions is None:
            self.interactions = []
        if self.gaze_data is None:
            self.gaze_data = []
        if self.performance_metrics is None:
            self.performance_metrics = {}

@dataclass
class ARSession:
    """Represents an AR learning session"""
    session_id: str
    user_id: str
    experience_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tracked_objects: List[Dict[str, Any]] = None
    spatial_data: List[Dict[str, Any]] = None
    learning_outcomes: Dict[str, Any] = None

    def __post_init__(self):
        if self.tracked_objects is None:
            self.tracked_objects = []
        if self.spatial_data is None:
            self.spatial_data = []
        if self.learning_outcomes is None:
            self.learning_outcomes = {}

@dataclass
class Model3D:
    """3D model for interactive learning"""
    model_id: str
    name: str
    description: str
    file_path: str
    file_format: str  # gltf, obj, fbx, etc.
    scale: List[float]
    position: List[float]
    rotation: List[float]
    animations: List[str]
    interactions: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class VRARManager:
    """Manager for VR/AR learning experiences"""

    def __init__(self):
        self.active_vr_sessions: Dict[str, VRSession] = {}
        self.active_ar_sessions: Dict[str, ARSession] = {}
        self.loaded_models: Dict[str, Model3D] = {}
        self.spatial_audio_sources: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        """Initialize VR/AR manager"""
        logger.info("VR/AR Manager initialized")

    async def start_vr_session(
        self,
        user_id: str,
        environment_id: str,
        initial_position: List[float] = None
    ) -> str:
        """Start a VR learning session"""
        session_id = f"vr_{user_id}_{datetime.utcnow().timestamp()}"

        session = VRSession(
            session_id=session_id,
            user_id=user_id,
            environment_id=environment_id,
            start_time=datetime.utcnow(),
            interactions=[],
            gaze_data=[],
            performance_metrics={}
        )

        self.active_vr_sessions[session_id] = session

        # Load VR environment
        await self._load_vr_environment(environment_id, session_id)

        logger.info(f"Started VR session {session_id} for user {user_id}")
        return session_id

    async def start_ar_session(
        self,
        user_id: str,
        experience_id: str,
        anchor_objects: List[Dict[str, Any]] = None
    ) -> str:
        """Start an AR learning session"""
        session_id = f"ar_{user_id}_{datetime.utcnow().timestamp()}"

        session = ARSession(
            session_id=session_id,
            user_id=user_id,
            experience_id=experience_id,
            start_time=datetime.utcnow(),
            tracked_objects=[],
            spatial_data=[],
            learning_outcomes={}
        )

        self.active_ar_sessions[session_id] = session

        # Initialize AR tracking
        await self._initialize_ar_tracking(session_id, anchor_objects or [])

        logger.info(f"Started AR session {session_id} for user {user_id}")
        return session_id

    async def end_vr_session(self, session_id: str) -> Dict[str, Any]:
        """End VR session and return analytics"""
        if session_id not in self.active_vr_sessions:
            raise ValueError(f"VR session {session_id} not found")

        session = self.active_vr_sessions[session_id]
        session.end_time = datetime.utcnow()

        # Calculate session metrics
        duration = (session.end_time - session.start_time).total_seconds()
        analytics = await self._calculate_vr_analytics(session)

        # Save session data
        await self._save_vr_session_data(session, analytics)

        # Clean up
        del self.active_vr_sessions[session_id]

        logger.info(f"Ended VR session {session_id}")
        return analytics

    async def end_ar_session(self, session_id: str) -> Dict[str, Any]:
        """End AR session and return analytics"""
        if session_id not in self.active_ar_sessions:
            raise ValueError(f"AR session {session_id} not found")

        session = self.active_ar_sessions[session_id]
        session.end_time = datetime.utcnow()

        # Calculate session metrics
        duration = (session.end_time - session.start_time).total_seconds()
        analytics = await self._calculate_ar_analytics(session)

        # Save session data
        await self._save_ar_session_data(session, analytics)

        # Clean up
        del self.active_ar_sessions[session_id]

        logger.info(f"Ended AR session {session_id}")
        return analytics

    async def load_3d_model(self, model_id: str) -> bool:
        """Load 3D model for interaction"""
        try:
            # Load model metadata from database
            model_data = await self._get_model_from_database(model_id)

            if model_data:
                model = Model3D(
                    model_id=model_data['id'],
                    name=model_data['name'],
                    description=model_data['description'],
                    file_path=model_data['file_path'],
                    file_format=model_data['file_format'],
                    scale=model_data.get('scale', [1.0, 1.0, 1.0]),
                    position=model_data.get('position', [0.0, 0.0, 0.0]),
                    rotation=model_data.get('rotation', [0.0, 0.0, 0.0]),
                    animations=model_data.get('animations', []),
                    interactions=model_data.get('interactions', []),
                    metadata=model_data.get('metadata', {})
                )

                self.loaded_models[model_id] = model
                return True

            return False
        except Exception as e:
            logger.error(f"Failed to load 3D model {model_id}: {e}")
            return False

    async def manipulate_3d_model(
        self,
        session_id: str,
        model_id: str,
        transformation: Dict[str, Any]
    ) -> bool:
        """Apply transformation to 3D model"""
        try:
            if session_id not in self.active_vr_sessions:
                return False

            session = self.active_vr_sessions[session_id]

            # Record interaction
            interaction = {
                "type": "model_manipulation",
                "model_id": model_id,
                "transformation": transformation,
                "timestamp": datetime.utcnow().isoformat()
            }

            session.interactions.append(interaction)

            # Apply transformation (this would interface with VR engine)
            success = await self._apply_model_transformation(model_id, transformation)

            return success

        except Exception as e:
            logger.error(f"Failed to manipulate 3D model: {e}")
            return False

    async def play_spatial_audio(
        self,
        session_id: str,
        audio_id: str,
        position: List[float],
        volume: float = 1.0
    ) -> bool:
        """Play spatial audio at specific position"""
        try:
            if session_id not in self.active_vr_sessions:
                return False

            audio_source = {
                "audio_id": audio_id,
                "position": position,
                "volume": volume,
                "start_time": datetime.utcnow().isoformat()
            }

            self.spatial_audio_sources[audio_id] = audio_source

            # Play spatial audio (interface with VR audio engine)
            success = await self._play_spatial_audio(audio_id, position, volume)

            return success

        except Exception as e:
            logger.error(f"Failed to play spatial audio: {e}")
            return False

    async def trigger_haptic_feedback(
        self,
        session_id: str,
        pattern: str,
        intensity: float = 1.0
    ) -> bool:
        """Trigger haptic feedback pattern"""
        try:
            if session_id not in self.active_vr_sessions:
                return False

            # Record haptic interaction
            interaction = {
                "type": "haptic_feedback",
                "pattern": pattern,
                "intensity": intensity,
                "timestamp": datetime.utcnow().isoformat()
            }

            session = self.active_vr_sessions[session_id]
            session.interactions.append(interaction)

            # Trigger haptic feedback (interface with VR hardware)
            success = await self._trigger_haptic_feedback(pattern, intensity)

            return success

        except Exception as e:
            logger.error(f"Failed to trigger haptic feedback: {e}")
            return False

    async def track_gaze_data(
        self,
        session_id: str,
        gaze_point: List[float],
        head_position: List[float],
        focus_duration: float
    ) -> bool:
        """Track user gaze data for attention analysis"""
        try:
            if session_id not in self.active_vr_sessions:
                return False

            gaze_data = {
                "gaze_point": gaze_point,
                "head_position": head_position,
                "focus_duration": focus_duration,
                "timestamp": datetime.utcnow().isoformat()
            }

            session = self.active_vr_sessions[session_id]
            session.gaze_data.append(gaze_data)

            return True

        except Exception as e:
            logger.error(f"Failed to track gaze data: {e}")
            return False

    async def track_ar_object(
        self,
        session_id: str,
        object_id: str,
        position: List[float],
        rotation: List[float],
        confidence: float
    ) -> bool:
        """Track AR object position and state"""
        try:
            if session_id not in self.active_ar_sessions:
                return False

            object_data = {
                "object_id": object_id,
                "position": position,
                "rotation": rotation,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat()
            }

            session = self.active_ar_sessions[session_id]
            session.tracked_objects.append(object_data)

            return True

        except Exception as e:
            logger.error(f"Failed to track AR object: {e}")
            return False

    async def _load_vr_environment(self, environment_id: str, session_id: str) -> bool:
        """Load VR environment and assets"""
        try:
            # Load environment configuration
            environment_data = await self._get_environment_data(environment_id)

            if environment_data:
                # Load associated 3D models
                models = environment_data.get('models', [])
                for model_id in models:
                    await self.load_3d_model(model_id)

                # Load audio sources
                audio_sources = environment_data.get('audio_sources', [])
                for audio_source in audio_sources:
                    await self.play_spatial_audio(
                        session_id,
                        audio_source['audio_id'],
                        audio_source['position']
                    )

                return True

            return False
        except Exception as e:
            logger.error(f"Failed to load VR environment: {e}")
            return False

    async def _initialize_ar_tracking(self, session_id: str, anchor_objects: List[Dict[str, Any]]) -> bool:
        """Initialize AR object tracking"""
        try:
            # Set up anchor objects for AR tracking
            for anchor in anchor_objects:
                await self._setup_ar_anchor(anchor)

            return True
        except Exception as e:
            logger.error(f"Failed to initialize AR tracking: {e}")
            return False

    async def _calculate_vr_analytics(self, session: VRSession) -> Dict[str, Any]:
        """Calculate VR session analytics"""
        duration = (session.end_time - session.start_time).total_seconds()

        # Calculate interaction metrics
        interaction_count = len(session.interactions)
        interactions_per_minute = interaction_count / (duration / 60)

        # Calculate attention metrics from gaze data
        attention_score = await self._calculate_attention_score(session.gaze_data)

        # Calculate engagement metrics
        engagement_score = await self._calculate_engagement_score(session.interactions)

        return {
            "session_id": session.session_id,
            "duration_seconds": duration,
            "total_interactions": interaction_count,
            "interactions_per_minute": interactions_per_minute,
            "attention_score": attention_score,
            "engagement_score": engagement_score,
            "models_interacted": len(set(
                interaction.get('model_id')
                for interaction in session.interactions
                if interaction.get('type') == 'model_manipulation'
            )),
            "haptic_interactions": len([
                interaction for interaction in session.interactions
                if interaction.get('type') == 'haptic_feedback'
            ])
        }

    async def _calculate_ar_analytics(self, session: ARSession) -> Dict[str, Any]:
        """Calculate AR session analytics"""
        duration = (session.end_time - session.start_time).total_seconds()

        # Calculate object tracking accuracy
        tracking_accuracy = await self._calculate_tracking_accuracy(session.tracked_objects)

        # Calculate learning outcomes
        learning_progress = await self._calculate_learning_progress(session.tracked_objects)

        return {
            "session_id": session.session_id,
            "duration_seconds": duration,
            "tracked_objects_count": len(session.tracked_objects),
            "tracking_accuracy": tracking_accuracy,
            "learning_progress": learning_progress,
            "spatial_interactions": len(session.spatial_data)
        }

    async def _calculate_attention_score(self, gaze_data: List[Dict[str, Any]]) -> float:
        """Calculate attention score from gaze data"""
        if not gaze_data:
            return 0.0

        # Analyze gaze patterns for attention
        focused_gazes = [
            gaze for gaze in gaze_data
            if gaze.get('focus_duration', 0) > 2.0  # Focused for more than 2 seconds
        ]

        attention_score = len(focused_gazes) / len(gaze_data)
        return min(attention_score, 1.0)

    async def _calculate_engagement_score(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate engagement score from interactions"""
        if not interactions:
            return 0.0

        # Different interaction types have different weights
        weights = {
            "model_manipulation": 0.3,
            "haptic_feedback": 0.2,
            "gaze_focus": 0.2,
            "audio_interaction": 0.15,
            "navigation": 0.15
        }

        weighted_score = 0.0
        for interaction in interactions:
            interaction_type = interaction.get('type', '')
            weight = weights.get(interaction_type, 0.1)
            weighted_score += weight

        return min(weighted_score, 1.0)

    async def _calculate_tracking_accuracy(self, tracked_objects: List[Dict[str, Any]]) -> float:
        """Calculate AR object tracking accuracy"""
        if not tracked_objects:
            return 0.0

        # Average confidence scores
        total_confidence = sum(obj.get('confidence', 0) for obj in tracked_objects)
        return total_confidence / len(tracked_objects)

    async def _calculate_learning_progress(self, tracked_objects: List[Dict[str, Any]]) -> float:
        """Calculate learning progress from AR interactions"""
        # Analyze object interactions for learning outcomes
        # This would implement specific learning logic based on AR experience
        return 0.75  # Placeholder

    async def _get_model_from_database(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get 3D model data from database"""
        try:
            db: Session = SessionLocal()
            # Query 3D models table
            # Return model data
            db.close()
            return {
                "id": model_id,
                "name": "Sample 3D Model",
                "description": "Interactive 3D model for learning",
                "file_path": f"/models/{model_id}.gltf",
                "file_format": "gltf",
                "scale": [1.0, 1.0, 1.0],
                "position": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "animations": ["idle", "interact"],
                "interactions": ["rotate", "scale", "disassemble"],
                "metadata": {"category": "educational", "difficulty": "intermediate"}
            }
        except Exception as e:
            logger.error(f"Failed to get model from database: {e}")
            return None

    async def _get_environment_data(self, environment_id: str) -> Optional[Dict[str, Any]]:
        """Get VR environment data"""
        try:
            db: Session = SessionLocal()
            # Query VR environments table
            db.close()
            return {
                "id": environment_id,
                "name": "Sample VR Environment",
                "models": ["model_1", "model_2"],
                "audio_sources": [
                    {"audio_id": "ambient_1", "position": [0, 0, 0]},
                    {"audio_id": "instruction_1", "position": [5, 0, 0]}
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get environment data: {e}")
            return None

    async def _apply_model_transformation(self, model_id: str, transformation: Dict[str, Any]) -> bool:
        """Apply transformation to 3D model (interface with VR engine)"""
        try:
            # Get model from loaded models
            model = self.loaded_models.get(model_id)
            if not model:
                return False

            # Apply transformation to model
            if 'scale' in transformation:
                model.scale = transformation['scale']
            if 'position' in transformation:
                model.position = transformation['position']
            if 'rotation' in transformation:
                model.rotation = transformation['rotation']

            # Send transformation to VR engine
            # This would interface with Unity/Unreal Engine via WebSocket or API
            await self._send_to_vr_engine('model_transform', {
                'model_id': model_id,
                'transformation': transformation
            })

            return True
        except Exception as e:
            logger.error(f"Failed to apply model transformation: {e}")
            return False

    async def _play_spatial_audio(self, audio_id: str, position: List[float], volume: float) -> bool:
        """Play spatial audio (interface with VR audio engine)"""
        try:
            # Load audio file
            audio_file = await self._get_audio_file(audio_id)
            if not audio_file:
                return False

            # Send spatial audio command to VR engine
            await self._send_to_vr_engine('play_spatial_audio', {
                'audio_id': audio_id,
                'position': position,
                'volume': volume,
                'file_path': audio_file
            })

            return True
        except Exception as e:
            logger.error(f"Failed to play spatial audio: {e}")
            return False

    async def _trigger_haptic_feedback(self, pattern: str, intensity: float) -> bool:
        """Trigger haptic feedback (interface with VR hardware)"""
        try:
            # Send haptic command to VR controllers
            await self._send_to_vr_engine('haptic_feedback', {
                'pattern': pattern,
                'intensity': intensity,
                'duration': 100  # milliseconds
            })

            return True
        except Exception as e:
            logger.error(f"Failed to trigger haptic feedback: {e}")
            return False

    async def _setup_ar_anchor(self, anchor: Dict[str, Any]) -> bool:
        """Setup AR anchor object"""
        try:
            # Initialize AR tracking for anchor object
            await self._send_to_ar_engine('setup_anchor', anchor)
            return True
        except Exception as e:
            logger.error(f"Failed to setup AR anchor: {e}")
            return False

    async def _send_to_vr_engine(self, command: str, data: Dict[str, Any]):
        """Send command to VR engine"""
        # This would send commands to Unity/Unreal Engine
        # For now, we'll just log the command
        logger.info(f"VR Engine Command: {command} - {data}")

    async def _send_to_ar_engine(self, command: str, data: Dict[str, Any]):
        """Send command to AR engine"""
        # This would send commands to ARKit/ARCore
        logger.info(f"AR Engine Command: {command} - {data}")

    async def _get_audio_file(self, audio_id: str) -> Optional[str]:
        """Get audio file path"""
        # Query audio files from database
        return f"/audio/{audio_id}.mp3"

    async def _save_vr_session_data(self, session: VRSession, analytics: Dict[str, Any]):
        """Save VR session data to database"""
        try:
            db: Session = SessionLocal()
            # Save session data
            # Save analytics
            # Save interactions
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to save VR session data: {e}")

    async def _save_ar_session_data(self, session: ARSession, analytics: Dict[str, Any]):
        """Save AR session data to database"""
        try:
            db: Session = SessionLocal()
            # Save session data
            # Save analytics
            # Save tracked objects
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to save AR session data: {e}")

    def get_active_vr_sessions(self) -> List[str]:
        """Get list of active VR session IDs"""
        return list(self.active_vr_sessions.keys())

    def get_active_ar_sessions(self) -> List[str]:
        """Get list of active AR session IDs"""
        return list(self.active_ar_sessions.keys())

    def get_session_analytics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get real-time analytics for active session"""
        if session_id in self.active_vr_sessions:
            session = self.active_vr_sessions[session_id]
            return {
                "session_id": session_id,
                "duration": (datetime.utcnow() - session.start_time).total_seconds(),
                "interactions": len(session.interactions),
                "gaze_points": len(session.gaze_data),
                "models_loaded": len(self.loaded_models)
            }
        elif session_id in self.active_ar_sessions:
            session = self.active_ar_sessions[session_id]
            return {
                "session_id": session_id,
                "duration": (datetime.utcnow() - session.start_time).total_seconds(),
                "tracked_objects": len(session.tracked_objects),
                "spatial_data_points": len(session.spatial_data)
            }
        return None

# Global VR/AR manager
vr_ar_manager = VRARManager()

# Initialize manager
asyncio.create_task(vr_ar_manager.initialize())
