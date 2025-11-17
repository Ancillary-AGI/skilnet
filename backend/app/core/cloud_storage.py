"""
Cloud storage service for EduVerse platform
Supports multiple storage providers: Local, AWS S3, Google Cloud, Azure
"""

import os
import aiofiles
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from importlib import import_module
from importlib.util import find_spec
import mimetypes
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
import uuid

from app.core.logging import get_logger

logger = get_logger("cloud_storage")


class StorageProvider(str, Enum):
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    MINIO = "minio"


class StorageConfig:
    """Storage configuration"""
    
    def __init__(self):
        self.STORAGE_PROVIDER = StorageProvider(os.getenv("STORAGE_PROVIDER", "local"))
        
        # Local storage
        self.LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./uploads")
        
        # AWS S3
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
        self.AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
        
        # Google Cloud Storage
        self.GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
        self.GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
        self.GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")
        
        # Azure Blob Storage
        self.AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME")
        self.AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
        self.AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
        
        # MinIO (S3-compatible)
        self.MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
        self.MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
        self.MINIO_BUCKET = os.getenv("MINIO_BUCKET", "eduverse")
        
        # CDN settings
        self.CDN_ENABLED = os.getenv("CDN_ENABLED", "false").lower() == "true"
        self.CDN_BASE_URL = os.getenv("CDN_BASE_URL")
        
        # File settings
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 100 * 1024 * 1024))  # 100MB
        self.ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.gif,.pdf,.mp4,.webm").split(",")


class BaseStorageService(ABC):
    """Abstract base class for storage services"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.logger = logger
    
    @abstractmethod
    async def upload_file(self, file_path: str, file_data: bytes, content_type: str = None) -> str:
        """Upload file and return URL"""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """Download file and return bytes"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files with metadata"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get file URL (signed if needed)"""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass
    
    async def health_check(self) -> bool:
        """Health check for storage service"""
        try:
            # Try to upload and delete a test file
            test_path = f"health_check_{uuid.uuid4().hex}.txt"
            test_data = b"health check"
            
            await self.upload_file(test_path, test_data)
            exists = await self.file_exists(test_path)
            await self.delete_file(test_path)
            
            return exists
        except Exception as e:
            self.logger.error(f"Storage health check failed: {e}")
            return False


class LocalStorageService(BaseStorageService):
    """Local file system storage service"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.base_path = Path(config.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(self, file_path: str, file_data: bytes, content_type: str = None) -> str:
        """Upload file to local storage"""
        try:
            full_path = self.base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(full_path, 'wb') as f:
                await f.write(file_data)
            
            # Return local URL
            return f"/uploads/{file_path}"
            
        except Exception as e:
            self.logger.error(f"Local upload failed: {e}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from local storage"""
        try:
            full_path = self.base_path / file_path
            
            async with aiofiles.open(full_path, 'rb') as f:
                return await f.read()
                
        except Exception as e:
            self.logger.error(f"Local download failed: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            full_path = self.base_path / file_path
            
            if full_path.exists():
                full_path.unlink()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Local delete failed: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in local storage"""
        try:
            files = []
            search_path = self.base_path / prefix if prefix else self.base_path
            
            if search_path.is_dir():
                for file_path in search_path.rglob("*"):
                    if file_path.is_file():
                        stat = file_path.stat()
                        relative_path = file_path.relative_to(self.base_path)
                        
                        files.append({
                            "path": str(relative_path),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "content_type": mimetypes.guess_type(str(file_path))[0]
                        })
            
            return files
            
        except Exception as e:
            self.logger.error(f"Local list failed: {e}")
            return []
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get file URL for local storage"""
        return f"/uploads/{file_path}"
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local storage"""
        full_path = self.base_path / file_path
        return full_path.exists()


_aioboto3_spec = find_spec("aioboto3")
_aioboto3_module = import_module("aioboto3") if _aioboto3_spec else None


class AWSS3StorageService(BaseStorageService):
    """AWS S3 storage service"""
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.bucket_name = config.AWS_S3_BUCKET
        self._s3_client = None
    
    async def _get_s3_client(self):
        """Get S3 client (lazy initialization)"""
        if self._s3_client is None:
            if _aioboto3_module is None:
                raise ImportError("aioboto3 is required for AWS S3 storage")
            
            session = _aioboto3_module.Session()
            self._s3_client = session.client(
                's3',
                aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY,
                region_name=self.config.AWS_REGION
            )
        
        return self._s3_client
    
    async def upload_file(self, file_path: str, file_data: bytes, content_type: str = None) -> str:
        """Upload file to S3"""
        try:
            s3_client = await self._get_s3_client()
            
            if not content_type:
                content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            async with s3_client as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=file_path,
                    Body=file_data,
                    ContentType=content_type
                )
            
            # Return S3 URL
            if self.config.CDN_ENABLED and self.config.CDN_BASE_URL:
                return f"{self.config.CDN_BASE_URL}/{file_path}"
            else:
                return f"https://{self.bucket_name}.s3.{self.config.AWS_REGION}.amazonaws.com/{file_path}"
                
        except Exception as e:
            self.logger.error(f"S3 upload failed: {e}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3"""
        try:
            s3_client = await self._get_s3_client()
            
            async with s3_client as s3:
                response = await s3.get_object(Bucket=self.bucket_name, Key=file_path)
                return await response['Body'].read()
                
        except Exception as e:
            self.logger.error(f"S3 download failed: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            s3_client = await self._get_s3_client()
            
            async with s3_client as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=file_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"S3 delete failed: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in S3"""
        try:
            s3_client = await self._get_s3_client()
            files = []
            
            async with s3_client as s3:
                paginator = s3.get_paginator('list_objects_v2')
                
                async for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            files.append({
                                "path": obj['Key'],
                                "size": obj['Size'],
                                "modified": obj['LastModified'].isoformat(),
                                "etag": obj['ETag'].strip('"')
                            })
            
            return files
            
        except Exception as e:
            self.logger.error(f"S3 list failed: {e}")
            return []
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for S3 file"""
        try:
            s3_client = await self._get_s3_client()
            
            async with s3_client as s3:
                url = await s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_path},
                    ExpiresIn=expires_in
                )
            
            return url
            
        except Exception as e:
            self.logger.error(f"S3 URL generation failed: {e}")
            raise
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            s3_client = await self._get_s3_client()
            
            async with s3_client as s3:
                await s3.head_object(Bucket=self.bucket_name, Key=file_path)
            
            return True
            
        except Exception:
            return False


class CloudStorageService:
    """Main cloud storage service that delegates to specific providers"""
    
    def __init__(self):
        self.config = StorageConfig()
        self._service = None
    
    async def initialize(self):
        """Initialize the appropriate storage service"""
        if self.config.STORAGE_PROVIDER == StorageProvider.LOCAL:
            self._service = LocalStorageService(self.config)
        elif self.config.STORAGE_PROVIDER == StorageProvider.AWS_S3:
            self._service = AWSS3StorageService(self.config)
        # Add other providers as needed
        else:
            # Fallback to local storage
            logger.warning(f"Unsupported storage provider: {self.config.STORAGE_PROVIDER}, falling back to local")
            self.config.STORAGE_PROVIDER = StorageProvider.LOCAL
            self._service = LocalStorageService(self.config)
        
        logger.info(f"Storage service initialized: {self.config.STORAGE_PROVIDER}")
    
    async def upload_file(self, file_path: str, file_data: bytes, content_type: str = None) -> str:
        """Upload file"""
        if not self._service:
            await self.initialize()
        return await self._service.upload_file(file_path, file_data, content_type)
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file"""
        if not self._service:
            await self.initialize()
        return await self._service.download_file(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        if not self._service:
            await self.initialize()
        return await self._service.delete_file(file_path)
    
    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files"""
        if not self._service:
            await self.initialize()
        return await self._service.list_files(prefix)
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get file URL"""
        if not self._service:
            await self.initialize()
        return await self._service.get_file_url(file_path, expires_in)
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        if not self._service:
            await self.initialize()
        return await self._service.file_exists(file_path)
    
    async def health_check(self) -> bool:
        """Health check"""
        if not self._service:
            await self.initialize()
        return await self._service.health_check()
    
    def validate_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate file before upload"""
        errors = []
        
        # Check file size
        if file_size > self.config.MAX_FILE_SIZE:
            errors.append(f"File size ({file_size} bytes) exceeds maximum allowed size ({self.config.MAX_FILE_SIZE} bytes)")
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.config.ALLOWED_EXTENSIONS:
            errors.append(f"File extension '{file_ext}' is not allowed. Allowed extensions: {', '.join(self.config.ALLOWED_EXTENSIONS)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def generate_file_path(self, filename: str, user_id: str = None, category: str = "general") -> str:
        """Generate organized file path"""
        file_ext = Path(filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # Organize by date and category
        date_path = datetime.now().strftime("%Y/%m/%d")
        
        if user_id:
            return f"{category}/{user_id}/{date_path}/{unique_filename}"
        else:
            return f"{category}/{date_path}/{unique_filename}"


# Global instances
storage_config = StorageConfig()
storage_service = CloudStorageService()


# Utility functions
async def upload_user_file(file_data: bytes, filename: str, user_id: str, category: str = "general") -> Dict[str, Any]:
    """Upload user file with validation"""
    try:
        # Validate file
        validation = storage_service.validate_file(filename, len(file_data))
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"]
            }
        
        # Generate file path
        file_path = storage_service.generate_file_path(filename, user_id, category)
        
        # Upload file
        file_url = await storage_service.upload_file(file_path, file_data)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_url": file_url,
            "file_size": len(file_data)
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return {
            "success": False,
            "errors": [str(e)]
        }


async def get_user_files(user_id: str, category: str = None) -> List[Dict[str, Any]]:
    """Get all files for a user"""
    try:
        prefix = f"{category}/{user_id}/" if category else f"general/{user_id}/"
        return await storage_service.list_files(prefix)
    except Exception as e:
        logger.error(f"Failed to get user files: {e}")
        return []