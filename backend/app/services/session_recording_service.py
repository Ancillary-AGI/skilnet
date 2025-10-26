"""
Session Recording Service with AI-Powered Summaries
Records learning sessions and generates intelligent summaries
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.services.websocket_manager import manager
import openai
import anthropic
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SessionEvent:
    """Represents a single event in a learning session"""
    event_id: str
    session_id: str
    user_id: str
    event_type: str  # lesson_view, quiz_attempt, discussion_post, etc.
    content: Dict[str, Any]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SessionSummary:
    """AI-generated summary of a learning session"""
    summary_id: str
    session_id: str
    summary_type: str  # periodic, final, highlights
    content: str
    key_points: List[str]
    action_items: List[str]
    generated_at: datetime
    confidence_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SessionRecordingService:
    """Service for recording and summarizing learning sessions"""

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_events: Dict[str, List[SessionEvent]] = {}
        self.ai_client = None
        self.summary_tasks: Dict[str, asyncio.Task] = {}

    async def initialize(self):
        """Initialize the recording service"""
        # Initialize AI client
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.ai_client = "openai"
        elif settings.ANTHROPIC_API_KEY:
            self.ai_client = anthropic.Client(settings.ANTHROPIC_API_KEY)
        else:
            logger.warning("No AI API key configured for session summaries")

    async def start_session_recording(
        self,
        session_id: str,
        user_id: str,
        session_type: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Start recording a learning session"""
        try:
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "user_id": user_id,
                "session_type": session_type,
                "start_time": datetime.utcnow(),
                "metadata": metadata or {},
                "event_count": 0
            }

            self.session_events[session_id] = []

            # Schedule periodic summaries
            self._schedule_periodic_summary(session_id)

            logger.info(f"Started recording session {session_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start session recording: {e}")
            return False

    async def stop_session_recording(self, session_id: str) -> Optional[SessionSummary]:
        """Stop recording and generate final summary"""
        try:
            if session_id not in self.active_sessions:
                return None

            session_data = self.active_sessions[session_id]
            events = self.session_events.get(session_id, [])

            # Cancel periodic summary task
            if session_id in self.summary_tasks:
                self.summary_tasks[session_id].cancel()
                del self.summary_tasks[session_id]

            # Generate final summary
            final_summary = await self._generate_session_summary(
                session_id,
                events,
                session_data,
                summary_type="final"
            )

            # Clean up
            del self.active_sessions[session_id]
            del self.session_events[session_id]

            # Save to database
            await self._save_session_data(session_id, events, final_summary)

            logger.info(f"Stopped recording session {session_id}")
            return final_summary

        except Exception as e:
            logger.error(f"Failed to stop session recording: {e}")
            return None

    async def record_event(self, event: SessionEvent) -> bool:
        """Record a single event in the session"""
        try:
            session_id = event.session_id

            if session_id not in self.active_sessions:
                logger.warning(f"Event recorded for non-active session: {session_id}")
                return False

            # Add event to session
            if session_id not in self.session_events:
                self.session_events[session_id] = []

            self.session_events[session_id].append(event)
            self.active_sessions[session_id]["event_count"] += 1

            # Broadcast event to session participants
            await manager.broadcast_to_room(session_id, {
                "type": "session_event",
                "event": event.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })

            return True

        except Exception as e:
            logger.error(f"Failed to record event: {e}")
            return False

    def _schedule_periodic_summary(self, session_id: str):
        """Schedule periodic summary generation"""
        async def generate_periodic_summary():
            while session_id in self.active_sessions:
                try:
                    await asyncio.sleep(300)  # Every 5 minutes

                    if session_id in self.session_events:
                        events = self.session_events[session_id]
                        if events:
                            await self._generate_session_summary(
                                session_id,
                                events[-50:],  # Last 50 events
                                self.active_sessions[session_id],
                                summary_type="periodic"
                            )

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in periodic summary: {e}")

        task = asyncio.create_task(generate_periodic_summary())
        self.summary_tasks[session_id] = task

    async def _generate_session_summary(
        self,
        session_id: str,
        events: List[SessionEvent],
        session_data: Dict[str, Any],
        summary_type: str
    ) -> SessionSummary:
        """Generate AI-powered summary of session events"""

        if not events:
            return SessionSummary(
                summary_id=f"{session_id}_{summary_type}_{datetime.utcnow().timestamp()}",
                session_id=session_id,
                summary_type=summary_type,
                content="No events recorded in this session.",
                key_points=[],
                action_items=[],
                generated_at=datetime.utcnow(),
                confidence_score=0.0
            )

        try:
            # Prepare events for AI processing
            events_text = self._format_events_for_ai(events)

            # Generate summary using AI
            if self.ai_client == "openai":
                summary_content = await self._generate_openai_summary(events_text, session_data)
            elif self.ai_client:
                summary_content = await self._generate_anthropic_summary(events_text, session_data)
            else:
                summary_content = self._generate_basic_summary(events)

            # Extract key points and action items
            key_points = self._extract_key_points(events)
            action_items = self._extract_action_items(events)

            summary = SessionSummary(
                summary_id=f"{session_id}_{summary_type}_{datetime.utcnow().timestamp()}",
                session_id=session_id,
                summary_type=summary_type,
                content=summary_content,
                key_points=key_points,
                action_items=action_items,
                generated_at=datetime.utcnow(),
                confidence_score=0.85  # Placeholder confidence score
            )

            # Broadcast summary to session participants
            await manager.broadcast_to_room(session_id, {
                "type": f"{summary_type}_summary",
                "summary": summary.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            })

            return summary

        except Exception as e:
            logger.error(f"Failed to generate {summary_type} summary: {e}")

            # Return basic summary as fallback
            return SessionSummary(
                summary_id=f"{session_id}_{summary_type}_fallback_{datetime.utcnow().timestamp()}",
                session_id=session_id,
                summary_type=summary_type,
                content=f"Session recorded {len(events)} events. Summary generation failed: {str(e)}",
                key_points=[f"Total events: {len(events)}"],
                action_items=["Review session manually"],
                generated_at=datetime.utcnow(),
                confidence_score=0.0
            )

    def _format_events_for_ai(self, events: List[SessionEvent]) -> str:
        """Format events for AI processing"""
        formatted_events = []

        for event in events:
            formatted_events.append(
                f"[{event.timestamp.isoformat()}] {event.event_type}: "
                f"{event.content.get('description', 'No description')}"
            )

        return "\n".join(formatted_events)

    async def _generate_openai_summary(self, events_text: str, session_data: Dict[str, Any]) -> str:
        """Generate summary using OpenAI"""
        try:
            prompt = self._build_summary_prompt(events_text, session_data)

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational analyst. Provide a comprehensive summary of this learning session."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI summary generation failed: {e}")
            raise

    async def _generate_anthropic_summary(self, events_text: str, session_data: Dict[str, Any]) -> str:
        """Generate summary using Anthropic"""
        try:
            prompt = self._build_summary_prompt(events_text, session_data)

            response = await self.ai_client.completions.create(
                model="claude-2",
                prompt=prompt,
                max_tokens_to_sample=500,
                temperature=0.7
            )

            return response.completion.strip()

        except Exception as e:
            logger.error(f"Anthropic summary generation failed: {e}")
            raise

    def _generate_basic_summary(self, events: List[SessionEvent]) -> str:
        """Generate basic summary without AI"""
        event_types = {}
        total_duration = timedelta()

        for event in events:
            event_type = event.event_type
            event_types[event_type] = event_types.get(event_type, 0) + 1

        # Calculate approximate duration
        if len(events) > 1:
            total_duration = events[-1].timestamp - events[0].timestamp

        return (
            f"Session Summary: {len(events)} events recorded over {total_duration}. "
            f"Event breakdown: {', '.join([f'{k}: {v}' for k, v in event_types.items()])}"
        )

    def _build_summary_prompt(self, events_text: str, session_data: Dict[str, Any]) -> str:
        """Build prompt for AI summary generation"""
        return f"""
        Please analyze this learning session and provide a comprehensive summary.

        Session Details:
        - Type: {session_data.get('session_type', 'Unknown')}
        - Duration: {session_data.get('event_count', 0)} events
        - Start Time: {session_data.get('start_time', 'Unknown')}

        Events:
        {events_text}

        Please provide:
        1. A concise summary of what happened in this session
        2. Key learning outcomes or topics covered
        3. Any challenges or difficulties encountered
        4. Suggestions for improvement or next steps
        5. Overall assessment of the session effectiveness

        Format your response as a well-structured summary.
        """

    def _extract_key_points(self, events: List[SessionEvent]) -> List[str]:
        """Extract key points from events"""
        key_points = []

        for event in events:
            if event.event_type in ['lesson_completed', 'quiz_passed', 'achievement_unlocked']:
                description = event.content.get('description', '')
                if description:
                    key_points.append(description)

        return key_points[:10]  # Limit to 10 key points

    def _extract_action_items(self, events: List[SessionEvent]) -> List[str]:
        """Extract action items from events"""
        action_items = []

        for event in events:
            if event.event_type == 'homework_assigned':
                homework = event.content.get('homework', '')
                if homework:
                    action_items.append(f"Complete: {homework}")

        return action_items

    async def _save_session_data(
        self,
        session_id: str,
        events: List[SessionEvent],
        summary: SessionSummary
    ):
        """Save session data to database"""
        try:
            db: Session = SessionLocal()

            # Save events
            for event in events:
                # Save to session_events table
                pass

            # Save summary
            # Save to session_summaries table
            pass

            db.commit()
            db.close()

        except Exception as e:
            logger.error(f"Failed to save session data: {e}")

    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a recorded session"""
        if session_id not in self.session_events:
            return {}

        events = self.session_events[session_id]
        session_data = self.active_sessions.get(session_id, {})

        # Calculate analytics
        event_types = {}
        user_participation = {}
        time_distribution = {}

        for event in events:
            # Count event types
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

            # Count user participation
            user_participation[event.user_id] = user_participation.get(event.user_id, 0) + 1

            # Time distribution (by hour)
            hour = event.timestamp.hour
            time_distribution[hour] = time_distribution.get(hour, 0) + 1

        return {
            "session_id": session_id,
            "total_events": len(events),
            "unique_users": len(user_participation),
            "event_types": event_types,
            "user_participation": user_participation,
            "time_distribution": time_distribution,
            "session_duration": session_data.get("event_count", 0),
            "most_active_user": max(user_participation.items(), key=lambda x: x[1])[0] if user_participation else None
        }

# Global session recording service
session_recording_service = SessionRecordingService()

# Initialize service
asyncio.create_task(session_recording_service.initialize())
