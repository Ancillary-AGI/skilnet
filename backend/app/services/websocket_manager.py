"""
WebSocket connection manager for real-time features
"""

from typing import Dict, List, Set
from fastapi import WebSocket
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections for real-time features"""
    
    def __init__(self):
        # Active connections by room
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # User mapping for rooms
        self.room_users: Dict[str, Set[str]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        """Connect user to a room"""
        await websocket.accept()
        
        # Add to room connections
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        
        # Add user to room
        if room_id not in self.room_users:
            self.room_users[room_id] = set()
        self.room_users[room_id].add(user_id)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "room_id": room_id,
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "message_count": 0
        }
        
        # Notify room about new user
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "room_user_count": len(self.room_users[room_id])
        }, exclude_user=user_id)
        
        logger.info(f"User {user_id} connected to room {room_id}")
    
    def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        """Disconnect user from room"""
        # Remove from connections
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        # Remove user from room
        if room_id in self.room_users:
            self.room_users[room_id].discard(user_id)
            if not self.room_users[room_id]:
                del self.room_users[room_id]
        
        # Remove connection metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        # Notify room about user leaving
        asyncio.create_task(self.broadcast_to_room(room_id, {
            "type": "user_left",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "room_user_count": len(self.room_users.get(room_id, set()))
        }, exclude_user=user_id))
        
        logger.info(f"User {user_id} disconnected from room {room_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(message)
            
            # Update message count
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["message_count"] += 1
                
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_room(
        self, 
        room_id: str, 
        message: any, 
        exclude_user: str = None
    ):
        """Broadcast message to all users in a room"""
        if room_id not in self.active_connections:
            return
        
        # Convert message to JSON if it's a dict
        if isinstance(message, dict):
            message_text = json.dumps(message)
        else:
            message_text = str(message)
        
        # Send to all connections in room
        disconnected_connections = []
        
        for connection in self.active_connections[room_id]:
            try:
                # Skip excluded user
                if exclude_user and connection in self.connection_metadata:
                    if self.connection_metadata[connection]["user_id"] == exclude_user:
                        continue
                
                await connection.send_text(message_text)
                
                # Update message count
                if connection in self.connection_metadata:
                    self.connection_metadata[connection]["message_count"] += 1
                    
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected_connections.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected_connections:
            if connection in self.active_connections[room_id]:
                self.active_connections[room_id].remove(connection)
            if connection in self.connection_metadata:
                del self.connection_metadata[connection]
    
    async def broadcast_to_all_rooms(self, message: any):
        """Broadcast message to all active rooms"""
        for room_id in self.active_connections:
            await self.broadcast_to_room(room_id, message)
    
    def get_room_users(self, room_id: str) -> List[str]:
        """Get list of users in a room"""
        return list(self.room_users.get(room_id, set()))
    
    def get_active_rooms(self) -> List[str]:
        """Get list of active rooms"""
        return list(self.active_connections.keys())
    
    def get_connection_stats(self) -> Dict[str, any]:
        """Get connection statistics"""
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        
        return {
            "total_connections": total_connections,
            "active_rooms": len(self.active_connections),
            "total_users": sum(len(users) for users in self.room_users.values()),
            "rooms": {
                room_id: {
                    "connections": len(connections),
                    "users": len(self.room_users.get(room_id, set()))
                }
                for room_id, connections in self.active_connections.items()
            }
        }


class VRClassroomManager:
    """Specialized manager for VR classroom sessions"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.vr_sessions: Dict[str, Dict] = {}
        self.spatial_data: Dict[str, Dict] = {}
    
    async def create_vr_session(
        self, 
        room_id: str, 
        instructor_id: str, 
        max_participants: int = 30
    ) -> Dict[str, Any]:
        """Create a new VR classroom session"""
        session_config = {
            "room_id": room_id,
            "instructor_id": instructor_id,
            "max_participants": max_participants,
            "created_at": datetime.utcnow(),
            "participants": set(),
            "spatial_objects": {},
            "shared_whiteboard": {"content": [], "version": 0},
            "voice_channels": {},
            "recording_enabled": True
        }
        
        self.vr_sessions[room_id] = session_config
        
        logger.info(f"Created VR session for room {room_id}")
        return session_config
    
    async def handle_spatial_update(
        self, 
        room_id: str, 
        user_id: str, 
        spatial_data: Dict[str, Any]
    ):
        """Handle user spatial position updates in VR"""
        if room_id not in self.spatial_data:
            self.spatial_data[room_id] = {}
        
        self.spatial_data[room_id][user_id] = {
            "position": spatial_data.get("position", [0, 0, 0]),
            "rotation": spatial_data.get("rotation", [0, 0, 0, 1]),
            "head_position": spatial_data.get("head_position", [0, 1.7, 0]),
            "hand_positions": spatial_data.get("hand_positions", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast spatial update to other users in room
        await self.websocket_manager.broadcast_to_room(room_id, {
            "type": "spatial_update",
            "user_id": user_id,
            "spatial_data": self.spatial_data[room_id][user_id]
        }, exclude_user=user_id)
    
    async def handle_object_interaction(
        self, 
        room_id: str, 
        user_id: str, 
        interaction_data: Dict[str, Any]
    ):
        """Handle VR object interactions"""
        object_id = interaction_data.get("object_id")
        action = interaction_data.get("action")
        
        # Update object state
        if room_id in self.vr_sessions:
            session = self.vr_sessions[room_id]
            if object_id not in session["spatial_objects"]:
                session["spatial_objects"][object_id] = {}
            
            session["spatial_objects"][object_id].update({
                "last_interaction": {
                    "user_id": user_id,
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": interaction_data
                }
            })
        
        # Broadcast interaction to all users
        await self.websocket_manager.broadcast_to_room(room_id, {
            "type": "object_interaction",
            "object_id": object_id,
            "user_id": user_id,
            "action": action,
            "interaction_data": interaction_data
        })
    
    async def update_shared_whiteboard(
        self, 
        room_id: str, 
        user_id: str, 
        whiteboard_data: Dict[str, Any]
    ):
        """Update shared VR whiteboard"""
        if room_id in self.vr_sessions:
            session = self.vr_sessions[room_id]
            session["shared_whiteboard"]["content"].append({
                "user_id": user_id,
                "data": whiteboard_data,
                "timestamp": datetime.utcnow().isoformat()
            })
            session["shared_whiteboard"]["version"] += 1
            
            # Broadcast whiteboard update
            await self.websocket_manager.broadcast_to_room(room_id, {
                "type": "whiteboard_update",
                "content": session["shared_whiteboard"],
                "updated_by": user_id
            })