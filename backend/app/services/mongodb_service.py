"""
MongoDB service for NoSQL operations alongside SQL database
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo import ASCENDING, DESCENDING
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MongoCollection(str, Enum):
    """MongoDB collections"""
    USER_ANALYTICS = "user_analytics"
    COURSE_ANALYTICS = "course_analytics"
    LEARNING_PATHS = "learning_paths"
    USER_PREFERENCES = "user_preferences"
    CONTENT_METADATA = "content_metadata"
    SOCIAL_INTERACTIONS = "social_interactions"
    RECOMMENDATIONS = "recommendations"
    CACHE_DOCUMENTS = "cache_documents"
    LOGS = "logs"
    METRICS = "metrics"


@dataclass
class MongoConfig:
    """MongoDB configuration"""
    host: str = "localhost"
    port: int = 27017
    database: str = "eduverse_nosql"
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"
    max_pool_size: int = 10
    min_pool_size: int = 5
    max_idle_time_ms: int = 30000
    connect_timeout_ms: int = 5000
    server_selection_timeout_ms: int = 5000


class MongoDBService:
    """MongoDB service for flexible NoSQL operations"""

    def __init__(self, config: Optional[MongoConfig] = None):
        self.config = config or MongoConfig()
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            # Build connection string
            if self.config.username and self.config.password:
                connection_string = (
                    f"mongodb://{self.config.username}:{self.config.password}@"
                    f"{self.config.host}:{self.config.port}/{self.config.database}?"
                    f"authSource={self.config.auth_source}&"
                    f"maxPoolSize={self.config.max_pool_size}&"
                    f"minPoolSize={self.config.min_pool_size}&"
                    f"maxIdleTimeMS={self.config.max_idle_time_ms}&"
                    f"connectTimeoutMS={self.config.connect_timeout_ms}&"
                    f"serverSelectionTimeoutMS={self.config.server_selection_timeout_ms}"
                )
            else:
                connection_string = (
                    f"mongodb://{self.config.host}:{self.config.port}/{self.config.database}?"
                    f"maxPoolSize={self.config.max_pool_size}&"
                    f"minPoolSize={self.config.min_pool_size}&"
                    f"maxIdleTimeMS={self.config.max_idle_time_ms}&"
                    f"connectTimeoutMS={self.config.connect_timeout_ms}&"
                    f"serverSelectionTimeoutMS={self.config.server_selection_timeout_ms}"
                )

            self.client = AsyncIOMotorClient(connection_string)
            self.database = self.client[self.config.database]

            # Test connection
            await self.client.admin.command('ping')
            self._connected = True

            logger.info(f"Connected to MongoDB: {self.config.database}")
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from MongoDB"""
        try:
            if self.client:
                self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")

        except Exception as e:
            logger.error(f"MongoDB disconnect error: {e}")

    def get_collection(self, collection_name: Union[str, MongoCollection]) -> AsyncIOMotorCollection:
        """Get a collection instance"""
        if not self.database:
            raise ConnectionError("Not connected to MongoDB")
        return self.database[str(collection_name)]

    # User Analytics Operations
    async def save_user_analytics(self, user_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Save user analytics data"""
        try:
            collection = self.get_collection(MongoCollection.USER_ANALYTICS)

            document = {
                "user_id": user_id,
                "data": analytics_data,
                "timestamp": datetime.utcnow(),
                "version": "1.0"
            }

            result = await collection.insert_one(document)
            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to save user analytics: {e}")
            return False

    async def get_user_analytics(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user analytics data"""
        try:
            collection = self.get_collection(MongoCollection.USER_ANALYTICS)

            cursor = collection.find(
                {"user_id": user_id}
            ).sort("timestamp", DESCENDING).limit(limit)

            return await cursor.to_list(length=limit)

        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return []

    # Learning Paths Operations
    async def save_learning_path(self, user_id: str, learning_path: Dict[str, Any]) -> bool:
        """Save user learning path"""
        try:
            collection = self.get_collection(MongoCollection.LEARNING_PATHS)

            document = {
                "user_id": user_id,
                "path_data": learning_path,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": "1.0"
            }

            result = await collection.insert_one(document)
            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to save learning path: {e}")
            return False

    async def get_learning_path(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user learning path"""
        try:
            collection = self.get_collection(MongoCollection.LEARNING_PATHS)

            document = await collection.find_one(
                {"user_id": user_id},
                sort=[("updated_at", DESCENDING)]
            )

            return document

        except Exception as e:
            logger.error(f"Failed to get learning path: {e}")
            return None

    # User Preferences Operations
    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences"""
        try:
            collection = self.get_collection(MongoCollection.USER_PREFERENCES)

            document = {
                "user_id": user_id,
                "preferences": preferences,
                "updated_at": datetime.utcnow(),
                "version": "1.0"
            }

            # Upsert operation
            result = await collection.replace_one(
                {"user_id": user_id},
                document,
                upsert=True
            )

            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
            return False

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        try:
            collection = self.get_collection(MongoCollection.USER_PREFERENCES)

            document = await collection.find_one({"user_id": user_id})
            return document

        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return None

    # Content Metadata Operations
    async def save_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Save content metadata"""
        try:
            collection = self.get_collection(MongoCollection.CONTENT_METADATA)

            document = {
                "content_id": content_id,
                "metadata": metadata,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": "1.0"
            }

            result = await collection.replace_one(
                {"content_id": content_id},
                document,
                upsert=True
            )

            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to save content metadata: {e}")
            return False

    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content metadata"""
        try:
            collection = self.get_collection(MongoCollection.CONTENT_METADATA)

            document = await collection.find_one({"content_id": content_id})
            return document

        except Exception as e:
            logger.error(f"Failed to get content metadata: {e}")
            return None

    # Social Interactions Operations
    async def save_social_interaction(self, interaction: Dict[str, Any]) -> bool:
        """Save social interaction"""
        try:
            collection = self.get_collection(MongoCollection.SOCIAL_INTERACTIONS)

            document = {
                **interaction,
                "timestamp": datetime.utcnow(),
                "version": "1.0"
            }

            result = await collection.insert_one(document)
            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to save social interaction: {e}")
            return False

    async def get_social_interactions(
        self,
        user_id: str,
        interaction_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get social interactions for user"""
        try:
            collection = self.get_collection(MongoCollection.SOCIAL_INTERACTIONS)

            query = {"$or": [{"user_id": user_id}, {"target_user_id": user_id}]}
            if interaction_type:
                query["interaction_type"] = interaction_type

            cursor = collection.find(query).sort("timestamp", DESCENDING).limit(limit)
            return await cursor.to_list(length=limit)

        except Exception as e:
            logger.error(f"Failed to get social interactions: {e}")
            return []

    # Recommendations Operations
    async def save_recommendation(self, user_id: str, recommendation: Dict[str, Any]) -> bool:
        """Save recommendation for user"""
        try:
            collection = self.get_collection(MongoCollection.RECOMMENDATIONS)

            document = {
                "user_id": user_id,
                "recommendation": recommendation,
                "created_at": datetime.utcnow(),
                "version": "1.0"
            }

            result = await collection.insert_one(document)
            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to save recommendation: {e}")
            return False

    async def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations for user"""
        try:
            collection = self.get_collection(MongoCollection.RECOMMENDATIONS)

            cursor = collection.find({"user_id": user_id}).sort("created_at", DESCENDING).limit(limit)
            return await cursor.to_list(length=limit)

        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []

    # Generic CRUD Operations
    async def insert_document(
        self,
        collection_name: Union[str, MongoCollection],
        document: Dict[str, Any]
    ) -> Optional[str]:
        """Insert a document into collection"""
        try:
            collection = self.get_collection(collection_name)

            # Add metadata
            document["created_at"] = datetime.utcnow()
            document["updated_at"] = datetime.utcnow()
            document["version"] = "1.0"

            result = await collection.insert_one(document)
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Failed to insert document: {e}")
            return None

    async def find_documents(
        self,
        collection_name: Union[str, MongoCollection],
        query: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find documents in collection"""
        try:
            collection = self.get_collection(collection_name)

            cursor = collection.find(query)

            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)

            return await cursor.to_list(length=limit or 100)

        except Exception as e:
            logger.error(f"Failed to find documents: {e}")
            return []

    async def find_one_document(
        self,
        collection_name: Union[str, MongoCollection],
        query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find one document in collection"""
        try:
            collection = self.get_collection(collection_name)
            return await collection.find_one(query)

        except Exception as e:
            logger.error(f"Failed to find document: {e}")
            return None

    async def update_document(
        self,
        collection_name: Union[str, MongoCollection],
        query: Dict[str, Any],
        update_data: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """Update a document in collection"""
        try:
            collection = self.get_collection(collection_name)

            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow()

            result = await collection.update_one(
                query,
                {"$set": update_data},
                upsert=upsert
            )

            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False

    async def delete_document(
        self,
        collection_name: Union[str, MongoCollection],
        query: Dict[str, Any]
    ) -> bool:
        """Delete a document from collection"""
        try:
            collection = self.get_collection(collection_name)

            result = await collection.delete_one(query)
            return result.acknowledged

        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    # Aggregation Operations
    async def aggregate(
        self,
        collection_name: Union[str, MongoCollection],
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Run aggregation pipeline"""
        try:
            collection = self.get_collection(collection_name)

            cursor = collection.aggregate(pipeline)
            return await cursor.to_list(length=None)

        except Exception as e:
            logger.error(f"Failed to run aggregation: {e}")
            return []

    # Index Management
    async def create_index(
        self,
        collection_name: Union[str, MongoCollection],
        keys: List[tuple],
        unique: bool = False
    ) -> bool:
        """Create index on collection"""
        try:
            collection = self.get_collection(collection_name)

            result = await collection.create_index(keys, unique=unique)
            logger.info(f"Created index: {result}")
            return True

        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    # Database Operations
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            if not self.database:
                return {}

            stats = await self.database.command("dbStats")
            return stats

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    async def list_collections(self) -> List[str]:
        """List all collections in database"""
        try:
            if not self.database:
                return []

            collections = await self.database.list_collection_names()
            return collections

        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB connection health"""
        try:
            if not self.client:
                return {"status": "disconnected"}

            # Ping the database
            await self.client.admin.command('ping')

            # Get basic stats
            stats = await self.get_database_stats()

            return {
                "status": "connected",
                "database": self.config.database,
                "collections_count": len(await self.list_collections()),
                "stats": stats
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global MongoDB service instance
mongodb_service = None

async def get_mongodb_service() -> MongoDBService:
    """Get MongoDB service instance"""
    global mongodb_service
    if mongodb_service is None:
        mongodb_service = MongoDBService()
        await mongodb_service.connect()
    return mongodb_service

async def close_mongodb_service():
    """Close MongoDB service"""
    global mongodb_service
    if mongodb_service:
        await mongodb_service.disconnect()
        mongodb_service = None
