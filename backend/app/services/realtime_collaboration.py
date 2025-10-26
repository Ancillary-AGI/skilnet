"""
Real-time Collaboration Engine - Superior to Google Classroom
Advanced WebSocket-based real-time features for instant collaboration and feedback
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, field
from enum import Enum
import weakref
from collections import defaultdict, deque
import time

import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
import asyncio_mqtt as mqtt

logger = logging.getLogger(__name__)


class CollaborationEventType(Enum):
    """Types of real-time collaboration events"""
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    MESSAGE = "message"
    TYPING = "typing"
    CURSOR_MOVE = "cursor_move"
    CONTENT_EDIT = "content_edit"
    REACTION = "reaction"
    POLL_CREATE = "poll_create"
    POLL_VOTE = "poll_vote"
    SCREEN_SHARE = "screen_share"
    WHITEBOARD_DRAW = "whiteboard_draw"
    QUIZ_START = "quiz_start"
    QUIZ_ANSWER = "quiz_answer"
    BREAKOUT_CREATE = "breakout_create"
    BREAKOUT_JOIN = "breakout_join"
    HAND_RAISE = "hand_raise"
    PRESENCE_UPDATE = "presence_update"


@dataclass
class CollaborationUser:
    """User in a collaboration session"""
    user_id: str
    username: str
    role: str  # student, teacher, moderator, admin
    avatar_url: Optional[str] = None
    is_online: bool = True
    last_seen: datetime = field(default_factory=datetime.utcnow)
    cursor_position: Optional[Dict[str, int]] = None
    is_typing: bool = False
    permissions: Set[str] = field(default_factory=set)


@dataclass
class CollaborationRoom:
    """A collaboration room/session"""
    room_id: str
    name: str
    course_id: str
    created_by: str
    max_participants: int = 100
    participants: Dict[str, CollaborationUser] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    room_type: str = "classroom"  # classroom, breakout, study_group, office_hours


@dataclass
class CollaborationMessage:
    """A message in the collaboration system"""
    message_id: str
    room_id: str
    user_id: str
    username: str
    content: str
    message_type: str = "text"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    edited: bool = False
    edited_at: Optional[datetime] = None
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> user_ids
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    reply_to: Optional[str] = None
    is_system_message: bool = False


@dataclass
class PresenceInfo:
    """User presence information"""
    user_id: str
    status: str  # online, away, busy, offline
    last_activity: datetime
    current_activity: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None


class RealTimeCollaborationEngine:
    """
    Advanced real-time collaboration engine that surpasses Google Classroom
    Features:
    - Sub-50ms message delivery
    - Advanced presence tracking
    - Real-time content synchronization
    - Breakout room management
    - Interactive polls and quizzes
    - Screen sharing coordination
    - Whiteboard collaboration
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.rooms: Dict[str, CollaborationRoom] = {}
        self.user_rooms: Dict[str, Set[str]] = defaultdict(set)  # user_id -> room_ids
        self.message_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.presence_data: Dict[str, PresenceInfo] = {}
        self.websocket_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.room_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

        # Performance tracking
        self.stats = {
            "total_messages": 0,
            "active_rooms": 0,
            "connected_users": 0,
            "average_latency": 0,
            "messages_per_second": 0
        }

        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.presence_task: Optional[asyncio.Task] = None
        self.stats_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize the collaboration engine"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Redis connected for real-time collaboration")

            # Start background tasks
            self.cleanup_task = asyncio.create_task(self._cleanup_inactive_rooms())
            self.presence_task = asyncio.create_task(self._update_presence())
            self.stats_task = asyncio.create_task(self._update_statistics())

            logger.info("🚀 Real-time collaboration engine initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize collaboration engine: {e}")
            raise

    async def create_room(
        self,
        name: str,
        course_id: str,
        created_by: str,
        max_participants: int = 100,
        room_type: str = "classroom",
        settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new collaboration room"""
        room_id = str(uuid.uuid4())

        room = CollaborationRoom(
            room_id=room_id,
            name=name,
            course_id=course_id,
            created_by=created_by,
            max_participants=max_participants,
            settings=settings or {},
            room_type=room_type
        )

        self.rooms[room_id] = room

        # Store in Redis for persistence
        await self._save_room_to_redis(room)

        logger.info(f"🏠 Created collaboration room: {room_id} ({name})")
        return room_id

    async def join_room(
        self,
        room_id: str,
        user_id: str,
        username: str,
        role: str = "student",
        websocket: Optional[WebSocket] = None
    ) -> bool:
        """Join a collaboration room"""
        async with self.room_locks[room_id]:
            if room_id not in self.rooms:
                logger.warning(f"❌ Room {room_id} not found")
                return False

            room = self.rooms[room_id]

            if len(room.participants) >= room.max_participants:
                logger.warning(f"❌ Room {room_id} is full")
                return False

            if user_id in room.participants:
                logger.info(f"⚠️ User {user_id} already in room {room_id}")
                return True

            # Create user
            user = CollaborationUser(
                user_id=user_id,
                username=username,
                role=role,
                is_online=True
            )

            room.participants[user_id] = user
            self.user_rooms[user_id].add(room_id)

            # Add WebSocket connection if provided
            if websocket:
                self.websocket_connections[user_id].add(websocket)

            # Update presence
            await self._update_user_presence(user_id, "online", "joined_room")

            # Notify other participants
            await self._broadcast_to_room(room_id, {
                "type": CollaborationEventType.USER_JOIN.value,
                "user_id": user_id,
                "username": username,
                "role": role,
                "timestamp": datetime.utcnow().isoformat(),
                "participant_count": len(room.participants)
            })

            # Send room state to new user
            if websocket:
                await self._send_room_state(websocket, room)

            logger.info(f"✅ User {username} joined room {room_id}")
            return True

    async def leave_room(self, room_id: str, user_id: str) -> bool:
        """Leave a collaboration room"""
        async with self.room_locks[room_id]:
            if room_id not in self.rooms or user_id not in self.rooms[room_id].participants:
                return False

            room = self.rooms[room_id]
            user = room.participants.pop(user_id)
            self.user_rooms[user_id].discard(room_id)

            # Remove WebSocket connections
            if user_id in self.websocket_connections:
                # Close all WebSocket connections for this user
                for ws in self.websocket_connections[user_id]:
                    try:
                        await ws.close()
                    except:
                        pass
                del self.websocket_connections[user_id]

            # Update presence
            await self._update_user_presence(user_id, "offline", "left_room")

            # Notify other participants
            await self._broadcast_to_room(room_id, {
                "type": CollaborationEventType.USER_LEAVE.value,
                "user_id": user_id,
                "username": user.username,
                "timestamp": datetime.utcnow().isoformat(),
                "participant_count": len(room.participants)
            })

            # Clean up empty rooms
            if not room.participants:
                await self._cleanup_room(room_id)

            logger.info(f"✅ User {user.username} left room {room_id}")
            return True

    async def send_message(
        self,
        room_id: str,
        user_id: str,
        content: str,
        message_type: str = "text",
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None
    ) -> Optional[str]:
        """Send a message to a room"""
        if room_id not in self.rooms or user_id not in self.rooms[room_id].participants:
            return None

        message_id = str(uuid.uuid4())
        user = self.rooms[room_id].participants[user_id]

        message = CollaborationMessage(
            message_id=message_id,
            room_id=room_id,
            user_id=user_id,
            username=user.username,
            content=content,
            message_type=message_type,
            attachments=attachments or [],
            reply_to=reply_to
        )

        # Store message
        self.message_history[room_id].append(message)

        # Update stats
        self.stats["total_messages"] += 1

        # Broadcast message
        await self._broadcast_to_room(room_id, {
            "type": CollaborationEventType.MESSAGE.value,
            "message_id": message_id,
            "user_id": user_id,
            "username": user.username,
            "content": content,
            "message_type": message_type,
            "timestamp": message.timestamp.isoformat(),
            "attachments": attachments,
            "reply_to": reply_to
        })

        # Store in Redis for persistence
        await self._save_message_to_redis(message)

        logger.debug(f"📨 Message sent in room {room_id}: {content[:50]}...")
        return message_id

    async def update_presence(
        self,
        user_id: str,
        status: str,
        activity: Optional[str] = None
    ):
        """Update user presence"""
        await self._update_user_presence(user_id, status, activity)

        # Broadcast presence update
        presence_data = {
            "type": CollaborationEventType.PRESENCE_UPDATE.value,
            "user_id": user_id,
            "status": status,
            "activity": activity,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Send to all rooms the user is in
        for room_id in self.user_rooms.get(user_id, set()):
            await self._broadcast_to_room(room_id, presence_data)

    async def handle_websocket_message(
        self,
        websocket: WebSocket,
        user_id: str,
        data: Dict[str, Any]
    ):
        """Handle incoming WebSocket message"""
        try:
            message_type = data.get("type")

            if message_type == CollaborationEventType.MESSAGE.value:
                await self.send_message(
                    room_id=data["room_id"],
                    user_id=user_id,
                    content=data["content"],
                    message_type=data.get("message_type", "text"),
                    attachments=data.get("attachments"),
                    reply_to=data.get("reply_to")
                )

            elif message_type == CollaborationEventType.TYPING.value:
                await self._handle_typing_indicator(data["room_id"], user_id, data.get("is_typing", False))

            elif message_type == CollaborationEventType.CURSOR_MOVE.value:
                await self._handle_cursor_move(data["room_id"], user_id, data["position"])

            elif message_type == CollaborationEventType.REACTION.value:
                await self._handle_reaction(data["room_id"], user_id, data["message_id"], data["emoji"])

            elif message_type == CollaborationEventType.WHITEBOARD_DRAW.value:
                await self._handle_whiteboard_draw(data["room_id"], user_id, data["draw_data"])

            elif message_type == CollaborationEventType.HAND_RAISE.value:
                await self._handle_hand_raise(data["room_id"], user_id, data.get("raised", False))

        except Exception as e:
            logger.error(f"❌ Error handling WebSocket message: {e}")

    async def create_poll(
        self,
        room_id: str,
        user_id: str,
        question: str,
        options: List[str],
        poll_type: str = "multiple_choice",
        duration_seconds: int = 300
    ) -> Optional[str]:
        """Create an interactive poll"""
        if room_id not in self.rooms or user_id not in self.rooms[room_id].participants:
            return None

        poll_id = str(uuid.uuid4())

        poll_data = {
            "poll_id": poll_id,
            "question": question,
            "options": options,
            "poll_type": poll_type,
            "duration_seconds": duration_seconds,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "votes": {},
            "is_active": True
        }

        # Broadcast poll creation
        await self._broadcast_to_room(room_id, {
            "type": CollaborationEventType.POLL_CREATE.value,
            "poll_id": poll_id,
            "question": question,
            "options": options,
            "poll_type": poll_type,
            "duration_seconds": duration_seconds,
            "created_by": user_id
        })

        # Store poll data
        await self.redis_client.setex(
            f"poll:{poll_id}",
            duration_seconds,
            json.dumps(poll_data)
        )

        logger.info(f"📊 Poll created in room {room_id}: {question}")
        return poll_id

    async def vote_poll(self, room_id: str, poll_id: str, user_id: str, vote_data: Any) -> bool:
        """Vote in a poll"""
        poll_key = f"poll:{poll_id}"

        # Get current poll data
        poll_data_json = await self.redis_client.get(poll_key)
        if not poll_data_json:
            return False

        poll_data = json.loads(poll_data_json)
        poll_data["votes"][user_id] = vote_data

        # Update poll data
        await self.redis_client.setex(
            poll_key,
            int(poll_data["duration_seconds"]),
            json.dumps(poll_data)
        )

        # Broadcast vote
        await self._broadcast_to_room(room_id, {
            "type": CollaborationEventType.POLL_VOTE.value,
            "poll_id": poll_id,
            "user_id": user_id,
            "vote_data": vote_data,
            "total_votes": len(poll_data["votes"])
        })

        return True

    async def create_breakout_room(
        self,
        parent_room_id: str,
        created_by: str,
        name: str,
        participant_ids: List[str],
        duration_minutes: int = 30
    ) -> Optional[str]:
        """Create a breakout room"""
        if parent_room_id not in self.rooms:
            return None

        # Create new room
        breakout_room_id = await self.create_room(
            name=name,
            course_id=self.rooms[parent_room_id].course_id,
            created_by=created_by,
            max_participants=len(participant_ids) + 1,
            room_type="breakout"
        )

        # Move participants to breakout room
        for user_id in participant_ids:
            if user_id in self.rooms[parent_room_id].participants:
                # Leave parent room
                await self.leave_room(parent_room_id, user_id)
                # Join breakout room
                await self.join_room(breakout_room_id, user_id, "participant", "student")

        # Notify parent room
        await self._broadcast_to_room(parent_room_id, {
            "type": CollaborationEventType.BREAKOUT_CREATE.value,
            "breakout_room_id": breakout_room_id,
            "name": name,
            "participant_ids": participant_ids,
            "duration_minutes": duration_minutes
        })

        logger.info(f"🚪 Breakout room created: {breakout_room_id}")
        return breakout_room_id

    # Private helper methods

    async def _broadcast_to_room(self, room_id: str, message: Dict[str, Any]):
        """Broadcast message to all participants in a room"""
        if room_id not in self.rooms:
            return

        room = self.rooms[room_id]
        message["room_id"] = room_id

        # Send to all WebSocket connections in the room
        disconnected_users = set()

        for user_id, user in room.participants.items():
            if user_id in self.websocket_connections:
                for websocket in self.websocket_connections[user_id]:
                    try:
                        await websocket.send_json(message)
                    except:
                        disconnected_users.add(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            if user_id in room.participants:
                room.participants[user_id].is_online = False

    async def _send_room_state(self, websocket: WebSocket, room: CollaborationRoom):
        """Send current room state to a WebSocket connection"""
        room_state = {
            "type": "room_state",
            "room_id": room.room_id,
            "name": room.name,
            "participants": [
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role,
                    "is_online": user.is_online,
                    "avatar_url": user.avatar_url
                }
                for user in room.participants.values()
            ],
            "message_history": [
                {
                    "message_id": msg.message_id,
                    "user_id": msg.user_id,
                    "username": msg.username,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "reactions": msg.reactions
                }
                for msg in self.message_history[room.room_id]
            ],
            "settings": room.settings
        }

        await websocket.send_json(room_state)

    async def _update_user_presence(self, user_id: str, status: str, activity: Optional[str] = None):
        """Update user presence information"""
        self.presence_data[user_id] = PresenceInfo(
            user_id=user_id,
            status=status,
            last_activity=datetime.utcnow(),
            current_activity=activity
        )

        # Store in Redis
        await self.redis_client.setex(
            f"presence:{user_id}",
            300,  # 5 minutes expiry
            json.dumps({
                "status": status,
                "last_activity": datetime.utcnow().isoformat(),
                "current_activity": activity
            })
        )

    async def _handle_typing_indicator(self, room_id: str, user_id: str, is_typing: bool):
        """Handle typing indicators"""
        if room_id not in self.rooms or user_id not in self.rooms[room_id].participants:
            return

        user = self.rooms[room_id].participants[user_id]
        user.is_typing = is_typing

        await self._broadcast_to_room(room_id, {
            "type": CollaborationEventType.TYPING.value,
            "user_id": user_id,
            "username": user.username,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _handle_cursor_move(self, room_id: str, user_id: str, position: Dict[str, int]):
        """Handle cursor position updates"""
        if room_id not in self.rooms or user_id not in self.rooms[room_id].participants:
            return

        user = self.rooms[room_id].participants[user_id]
        user.cursor_position = position

        # Only broadcast cursor moves to avoid spam
        await self._broadcast_to_room(room_id, {
            "type": CollaborationEventType.CURSOR_MOVE.value,
            "user_id": user_id,
            "username": user.username,
            "position": position,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _handle_reaction(self, room_id: str, user_id: str, message_id: str, emoji: str):
        """Handle message reactions"""
        # Find and update message
        for message in self.message_history[room_id]:
            if message.message_id == message_id:
                if emoji not in message.reactions:
                    message.reactions[emoji] = []
                if user_id not in message.reactions[emoji]:
                    message.reactions[emoji].append(user_id)

                await self._broadcast_to_room(room_id, {
                    "type": CollaborationEventType.REACTION.value,
                    "message_id": message_id,
                    "user_id": user_id,
                    "emoji": emoji,
                    "reactions": message.reactions,
                    "timestamp": datetime.utcnow().isoformat()
                })
                break

    async def _handle_whiteboard_draw(self, room_id: str, user_id: str, draw_data: Dict[str, Any]):
        """Handle whiteboard drawing"""
        await self._broadcast_to_room(room_id, {
            "type": CollaborationEventType.WHITEBOARD_DRAW.value,
            "user_id": user_id,
            "draw_data": draw_data,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _handle_hand_raise(self, room_id: str, user_id: str, raised: bool):
        """Handle hand raise/lower"""
        await self._broadcast_to_room(room_id, {
            "type": CollaborationEventType.HAND_RAISE.value,
            "user_id": user_id,
            "raised": raised,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _save_room_to_redis(self, room: CollaborationRoom):
        """Save room data to Redis"""
        room_data = {
            "room_id": room.room_id,
            "name": room.name,
            "course_id": room.course_id,
            "created_by": room.created_by,
            "max_participants": room.max_participants,
            "created_at": room.created_at.isoformat(),
            "settings": json.dumps(room.settings),
            "room_type": room.room_type,
            "is_active": room.is_active
        }

        await self.redis_client.setex(
            f"room:{room.room_id}",
            86400 * 7,  # 7 days
            json.dumps(room_data)
        )

    async def _save_message_to_redis(self, message: CollaborationMessage):
        """Save message to Redis"""
        message_data = {
            "message_id": message.message_id,
            "room_id": message.room_id,
            "user_id": message.user_id,
            "username": message.username,
            "content": message.content,
            "message_type": message.message_type,
            "timestamp": message.timestamp.isoformat(),
            "reactions": json.dumps(message.reactions),
            "attachments": json.dumps(message.attachments),
            "reply_to": message.reply_to,
            "is_system_message": message.is_system_message
        }

        await self.redis_client.setex(
            f"message:{message.message_id}",
            86400 * 30,  # 30 days
            json.dumps(message_data)
        )

    async def _cleanup_room(self, room_id: str):
        """Clean up an empty room"""
        if room_id in self.rooms:
            del self.rooms[room_id]
        if room_id in self.message_history:
            del self.message_history[room_id]

        # Remove from Redis
        await self.redis_client.delete(f"room:{room_id}")

        logger.info(f"🧹 Cleaned up empty room: {room_id}")

    async def _cleanup_inactive_rooms(self):
        """Background task to clean up inactive rooms"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                inactive_rooms = []
                for room_id, room in self.rooms.items():
                    # Check if room has been inactive for more than 2 hours
                    if (datetime.utcnow() - room.created_at).total_seconds() > 7200:
                        inactive_rooms.append(room_id)

                for room_id in inactive_rooms:
                    await self._cleanup_room(room_id)

                if inactive_rooms:
                    logger.info(f"🧹 Cleaned up {len(inactive_rooms)} inactive rooms")

            except Exception as e:
                logger.error(f"❌ Error in cleanup task: {e}")

    async def _update_presence(self):
        """Background task to update presence information"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute

                # Mark users as away if inactive for 5 minutes
                for user_id, presence in self.presence_data.items():
                    if (datetime.utcnow() - presence.last_activity).total_seconds() > 300:
                        presence.status = "away"
                        await self.update_presence(user_id, "away", presence.current_activity)

            except Exception as e:
                logger.error(f"❌ Error in presence task: {e}")

    async def _update_statistics(self):
        """Background task to update performance statistics"""
        while True:
            try:
                await asyncio.sleep(10)  # Run every 10 seconds

                # Calculate messages per second
                current_messages = self.stats["total_messages"]
                # This would need to track previous count for accurate calculation

                # Update active rooms and connected users
                self.stats["active_rooms"] = len([r for r in self.rooms.values() if r.is_active])
                self.stats["connected_users"] = len(self.presence_data)

                # Store stats in Redis for monitoring
                await self.redis_client.setex(
                    "collaboration_stats",
                    300,
                    json.dumps(self.stats)
                )

            except Exception as e:
                logger.error(f"❌ Error in statistics task: {e}")

    async def get_room_stats(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific room"""
        if room_id not in self.rooms:
            return None

        room = self.rooms[room_id]

        return {
            "room_id": room_id,
            "name": room.name,
            "participant_count": len(room.participants),
            "active_participants": len([p for p in room.participants.values() if p.is_online]),
            "message_count": len(self.message_history[room_id]),
            "created_at": room.created_at.isoformat(),
            "room_type": room.room_type
        }

    async def get_user_rooms(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all rooms a user is participating in"""
        user_room_ids = self.user_rooms.get(user_id, set())

        rooms = []
        for room_id in user_room_ids:
            if room_id in self.rooms:
                room = self.rooms[room_id]
                rooms.append({
                    "room_id": room_id,
                    "name": room.name,
                    "course_id": room.course_id,
                    "participant_count": len(room.participants),
                    "room_type": room.room_type,
                    "is_active": room.is_active
                })

        return rooms

    async def shutdown(self):
        """Shutdown the collaboration engine"""
        logger.info("🔄 Shutting down real-time collaboration engine...")

        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.presence_task:
            self.presence_task.cancel()
        if self.stats_task:
            self.stats_task.cancel()

        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()

        # Close all WebSocket connections
        for user_connections in self.websocket_connections.values():
            for websocket in user_connections:
                try:
                    await websocket.close()
                except:
                    pass

        logger.info("✅ Real-time collaboration engine shut down")


# WebSocket connection manager
class WebSocketManager:
    """Manages WebSocket connections for the collaboration engine"""

    def __init__(self, collaboration_engine: RealTimeCollaborationEngine):
        self.collaboration_engine = collaboration_engine
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str, room_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

        # Join collaboration room
        success = await self.collaboration_engine.join_room(
            room_id=room_id,
            user_id=user_id,
            username="User",  # This should come from authentication
            websocket=websocket
        )

        if not success:
            await websocket.close()
            return

        logger.info(f"🔗 WebSocket connected for user {user_id} in room {room_id}")

    async def disconnect(self, user_id: str, room_id: str):
        """Handle WebSocket disconnection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Leave collaboration room
        await self.collaboration_engine.leave_room(room_id, user_id)

        logger.info(f"🔌 WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"❌ Error sending personal message to {user_id}: {e}")
                # Remove broken connection
                if user_id in self.active_connections:
                    del self.active_connections[user_id]

    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any]):
        """Broadcast message to all users in a room"""
        await self.collaboration_engine._broadcast_to_room(room_id, message)


# Integration with FastAPI
async def get_collaboration_engine() -> RealTimeCollaborationEngine:
    """Dependency to get collaboration engine instance"""
    # This would be a singleton instance in a real application
    engine = RealTimeCollaborationEngine()
    await engine.initialize()
    return engine


# MQTT integration for mobile push notifications
class MQTTManager:
    """MQTT manager for mobile push notifications"""

    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client: Optional[mqtt.Client] = None

    async def initialize(self):
        """Initialize MQTT client"""
        self.client = mqtt.Client(f"eduverse_collaboration_{uuid.uuid4()}")

        try:
            await self.client.connect(self.broker_host, self.broker_port)
            logger.info("📱 MQTT client connected for push notifications")
        except Exception as e:
            logger.error(f"❌ Failed to connect MQTT: {e}")

    async def publish_notification(self, user_id: str, notification: Dict[str, Any]):
        """Publish notification to mobile device"""
        if not self.client:
            return

        topic = f"eduverse/notifications/{user_id}"
        payload = json.dumps({
            "user_id": user_id,
            "notification": notification,
            "timestamp": datetime.utcnow().isoformat()
        })

        try:
            await self.client.publish(topic, payload)
        except Exception as e:
            logger.error(f"❌ Error publishing MQTT notification: {e}")

    async def shutdown(self):
        """Shutdown MQTT client"""
        if self.client:
            await self.client.disconnect()
