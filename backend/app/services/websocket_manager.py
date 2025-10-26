"""
WebSocket Manager for Real-Time Communication
Handles real-time events, collaboration, and live features
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
import redis
import aioredis
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self.user_rooms: Dict[str, Set[str]] = {}
        self.heartbeat_intervals: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()

        # Store connection
        self.active_connections[user_id] = websocket

        # Start heartbeat monitoring
        self._start_heartbeat(user_id, websocket)

        logger.info(f"User {user_id} connected via WebSocket")

        # Send welcome message
        await self.send_personal_message(user_id, {
            "type": "connection_established",
            "message": "Connected to EduVerse real-time services",
            "timestamp": datetime.utcnow().isoformat()
        })

    def _start_heartbeat(self, user_id: str, websocket: WebSocket):
        """Start heartbeat monitoring for connection"""
        async def heartbeat():
            try:
                while True:
                    await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                    if user_id in self.active_connections:
                        await self.send_personal_message(user_id, {
                            "type": "heartbeat",
                            "timestamp": datetime.utcnow().isoformat()
                        })
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Heartbeat error for user {user_id}: {e}")

        task = asyncio.create_task(heartbeat())
        self.heartbeat_intervals[user_id] = task

    async def disconnect(self, user_id: str):
        """Handle WebSocket disconnection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        if user_id in self.heartbeat_intervals:
            self.heartbeat_intervals[user_id].cancel()
            del self.heartbeat_intervals[user_id]

        # Remove user from all rooms
        if user_id in self.user_rooms:
            for room_id in self.user_rooms[user_id]:
                await self.leave_room(room_id, user_id)
            del self.user_rooms[user_id]

        logger.info(f"User {user_id} disconnected from WebSocket")

    async def join_room(self, room_id: str, user_id: str):
        """Add user to a room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()

        self.rooms[room_id].add(user_id)

        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()

        self.user_rooms[user_id].add(room_id)

        # Notify other room members
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)

        logger.info(f"User {user_id} joined room {room_id}")

    async def leave_room(self, room_id: str, user_id: str):
        """Remove user from a room"""
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            self.rooms[room_id].remove(user_id)

            if not self.rooms[room_id]:
                del self.rooms[room_id]

        if user_id in self.user_rooms and room_id in self.user_rooms[user_id]:
            self.user_rooms[user_id].remove(room_id)

            if not self.user_rooms[user_id]:
                del self.user_rooms[user_id]

        # Notify other room members
        await self.broadcast_to_room(room_id, {
            "type": "user_left",
            "user_id": user_id,
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)

        logger.info(f"User {user_id} left room {room_id}")

    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                await self.disconnect(user_id)

    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_user: str = None):
        """Broadcast message to all users in a room"""
        if room_id not in self.rooms:
            return

        disconnected_users = []
        for user_id in self.rooms[room_id]:
            if exclude_user and user_id == exclude_user:
                continue

            if user_id in self.active_connections:
                try:
                    websocket = self.active_connections[user_id]
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    disconnected_users.append(user_id)
            else:
                disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            if user_id in self.rooms[room_id]:
                self.rooms[room_id].remove(user_id)
            await self.disconnect(user_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected users"""
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.disconnect(user_id)

    def get_room_users(self, room_id: str) -> List[str]:
        """Get list of users in a room"""
        return list(self.rooms.get(room_id, set()))

    def get_user_rooms(self, user_id: str) -> List[str]:
        """Get list of rooms user is in"""
        return list(self.user_rooms.get(user_id, set()))

# Global connection manager
manager = ConnectionManager()

class WebSocketManager:
    """Main WebSocket manager for handling connections and events"""

    def __init__(self):
        self.redis_client = None
        self.pubsub = None

    async def initialize_redis(self):
        """Initialize Redis for distributed WebSocket management"""
        try:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe("websocket_events")
            logger.info("Redis initialized for WebSocket management")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")

    async def handle_message(self, user_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = message.get("type")

        try:
            if message_type == "join_room":
                room_id = message.get("room_id")
                if room_id:
                    await manager.join_room(room_id, user_id)

            elif message_type == "leave_room":
                room_id = message.get("room_id")
                if room_id:
                    await manager.leave_room(room_id, user_id)

            elif message_type == "send_message":
                room_id = message.get("room_id")
                content = message.get("content")
                if room_id and content:
                    await manager.broadcast_to_room(room_id, {
                        "type": "new_message",
                        "user_id": user_id,
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            elif message_type == "typing_start":
                room_id = message.get("room_id")
                if room_id:
                    await manager.broadcast_to_room(room_id, {
                        "type": "typing_start",
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }, exclude_user=user_id)

            elif message_type == "typing_stop":
                room_id = message.get("room_id")
                if room_id:
                    await manager.broadcast_to_room(room_id, {
                        "type": "typing_stop",
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }, exclude_user=user_id)

            elif message_type == "presence_update":
                status = message.get("status", "online")
                # Update user presence in database
                await self._update_user_presence(user_id, status)

            elif message_type == "heartbeat_response":
                # Update last seen timestamp
                await self._update_user_activity(user_id)

            # Handle collaboration-specific events
            elif message_type == "whiteboard_stroke":
                room_id = message.get("room_id")
                stroke_data = message.get("stroke_data")
                if room_id and stroke_data:
                    await manager.broadcast_to_room(room_id, {
                        "type": "whiteboard_stroke",
                        "user_id": user_id,
                        "stroke_data": stroke_data,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            elif message_type == "screen_share_started":
                room_id = message.get("room_id")
                if room_id:
                    await manager.broadcast_to_room(room_id, {
                        "type": "screen_share_started",
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            elif message_type == "screen_share_stopped":
                room_id = message.get("room_id")
                if room_id:
                    await manager.broadcast_to_room(room_id, {
                        "type": "screen_share_stopped",
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            # Handle learning events
            elif message_type == "lesson_completed":
                course_id = message.get("course_id")
                lesson_id = message.get("lesson_id")
                if course_id and lesson_id:
                    await self._handle_lesson_completion(user_id, course_id, lesson_id)

            elif message_type == "quiz_submitted":
                quiz_id = message.get("quiz_id")
                score = message.get("score")
                if quiz_id and score is not None:
                    await self._handle_quiz_submission(user_id, quiz_id, score)

            # Handle social events
            elif message_type == "discussion_post":
                content = message.get("content")
                category = message.get("category")
                if content and category:
                    await self._handle_discussion_post(user_id, content, category)

            elif message_type == "achievement_unlocked":
                achievement_id = message.get("achievement_id")
                if achievement_id:
                    await self._handle_achievement_unlock(user_id, achievement_id)

        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}")

    async def _update_user_presence(self, user_id: str, status: str):
        """Update user presence status"""
        try:
            db: Session = SessionLocal()
            # Update user presence in database
            # This would update a user_presence table
            db.close()
        except Exception as e:
            logger.error(f"Error updating user presence: {e}")

    async def _update_user_activity(self, user_id: str):
        """Update user last activity timestamp"""
        try:
            db: Session = SessionLocal()
            # Update user last_seen timestamp
            # This would update the user table
            db.close()
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")

    async def _handle_lesson_completion(self, user_id: str, course_id: str, lesson_id: str):
        """Handle lesson completion event"""
        try:
            # Update progress in database
            db: Session = SessionLocal()
            # Update user progress
            # Check for achievements
            # Update analytics
            db.close()

            # Broadcast to course followers
            await manager.broadcast_to_room(f"course_{course_id}", {
                "type": "lesson_completed",
                "user_id": user_id,
                "course_id": course_id,
                "lesson_id": lesson_id,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"Error handling lesson completion: {e}")

    async def _handle_quiz_submission(self, user_id: str, quiz_id: str, score: float):
        """Handle quiz submission event"""
        try:
            # Update quiz results in database
            db: Session = SessionLocal()
            # Update user analytics
            # Check for achievements
            db.close()

            # Broadcast quiz completion
            await manager.broadcast_to_room(f"quiz_{quiz_id}", {
                "type": "quiz_completed",
                "user_id": user_id,
                "quiz_id": quiz_id,
                "score": score,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"Error handling quiz submission: {e}")

    async def _handle_discussion_post(self, user_id: str, content: str, category: str):
        """Handle discussion post event"""
        try:
            # Save discussion post to database
            db: Session = SessionLocal()
            # Create discussion post record
            # Update user activity
            db.close()

            # Broadcast to discussion followers
            await manager.broadcast_to_room(f"discussion_{category}", {
                "type": "new_discussion_post",
                "user_id": user_id,
                "content": content,
                "category": category,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"Error handling discussion post: {e}")

    async def _handle_achievement_unlock(self, user_id: str, achievement_id: str):
        """Handle achievement unlock event"""
        try:
            # Update user achievements in database
            db: Session = SessionLocal()
            # Create achievement record
            # Update gamification stats
            db.close()

            # Broadcast achievement to user's friends/followers
            user_rooms = manager.get_user_rooms(user_id)
            for room_id in user_rooms:
                await manager.broadcast_to_room(room_id, {
                    "type": "achievement_unlocked",
                    "user_id": user_id,
                    "achievement_id": achievement_id,
                    "timestamp": datetime.utcnow().isoformat()
                })

        except Exception as e:
            logger.error(f"Error handling achievement unlock: {e}")

    async def send_system_announcement(self, message: str, target_audience: str = "all"):
        """Send system-wide announcement"""
        announcement = {
            "type": "system_announcement",
            "message": message,
            "audience": target_audience,
            "timestamp": datetime.utcnow().isoformat()
        }

        if target_audience == "all":
            await manager.broadcast_to_all(announcement)
        else:
            # Send to specific audience (e.g., course students, premium users)
            await self._broadcast_to_audience(announcement, target_audience)

    async def _broadcast_to_audience(self, message: Dict[str, Any], audience: str):
        """Broadcast message to specific audience"""
        # This would query database for users matching the audience criteria
        # and send messages to their active connections
        pass

    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get real-time statistics for user"""
        return {
            "active_connections": len(manager.active_connections),
            "user_rooms": len(manager.get_user_rooms(user_id)),
            "room_users": {room_id: len(users) for room_id, users in manager.rooms.items()},
            "last_activity": datetime.utcnow().isoformat()
        }

# Global WebSocket manager
websocket_manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Main WebSocket endpoint"""
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await websocket_manager.handle_message(user_id, message)
            except json.JSONDecodeError:
                # Send error message for invalid JSON
                await manager.send_personal_message(user_id, {
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        await manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        await manager.disconnect(user_id)

# Background task to clean up inactive connections
async def cleanup_inactive_connections():
    """Clean up connections that haven't sent heartbeat"""
    while True:
        try:
            current_time = datetime.utcnow()
            inactive_users = []

            # Check for inactive connections (no heartbeat for 5 minutes)
            for user_id, connection in manager.active_connections.items():
                # In a real implementation, you'd track last heartbeat time
                # For now, we'll just clean up obviously dead connections
                try:
                    await connection.ping()
                except:
                    inactive_users.append(user_id)

            # Disconnect inactive users
            for user_id in inactive_users:
                await manager.disconnect(user_id)

        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")

        await asyncio.sleep(60)  # Run cleanup every minute

# Start cleanup task when module is imported
asyncio.create_task(cleanup_inactive_connections())
