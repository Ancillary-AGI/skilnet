"""
Cloud storage service with support for multiple providers
"""

import os
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, BinaryIO, List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
import aiofiles
from pathlib import Path

class StorageProvider(str, Enum):
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    CLOUDFLARE_R2 = "cloudflare_r2"
    DIGITALOCEAN_SPACES = "digitalocean_spaces"

class CloudStorageConfig(BaseSettings):
    """Cloud storage configuration"""
    
    # Storage provider selection
    STORAGE_PROVIDER: StorageProvider = StorageProvider.AWS_S3
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "eduverse-storage"
    AWS_S3_ENDPOINT_URL: Optional[str] = None  # For S3-compatible services
    
    # Google Cloud Storage settings
    GCP_PROJECT_ID: Optional[str] = None
    GCP_CREDENTIALS_PATH: Optional[str] = None
    GCP_BUCKET: str = "eduverse-storage"
    
    # Azure Blob Storage settings
    AZURE_ACCOUNT_NAME: Optional[str] = None
    AZURE_ACCOUNT_KEY: Optional[str] = None
    AZURE_CONTAINER: str = "eduverse-storage"
    
    # Cloudflare R2 settings
    CLOUDFLARE_R2_ACCESS_KEY: Optional[str] = None
    CLOUDFLARE_R2_SECRET_KEY: Optional[str] = None
    CLOUDFLARE_R2_BUCKET: str = "eduverse-storage"
    CLOUDFLARE_R2_ENDPOINT: Optional[str] = None
    
    # DigitalOcean Spaces settings
    DO_SPACES_KEY: Optional[str] = None
    DO_SPACES_SECRET: Optional[str] = None
    DO_SPACES_BUCKET: str = "eduverse-storage"
    DO_SPACES_REGION: str = "nyc3"
    
    # Local storage settings
    LOCAL_STORAGE_PATH: str = "./uploads"
    
    # CDN settings
    CDN_BASE_URL: Optional[str] = None
    CDN_ENABLED: bool = False
    
    # File upload settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",  # Images
        ".mp4", ".webm", ".mov", ".avi", ".mkv",  # Videos
        ".mp3", ".wav", ".ogg", ".m4a",  # Audio
        ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt",  # Documents
        ".zip", ".rar", ".7z",  # Archives
        ".glb", ".gltf", ".fbx", ".obj", ".dae",  # 3D models for VR/AR
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class BaseStorageService(ABC):
    """Abstract base class for storage services"""
    
    @abstractmethod
    async def upload_file(self, file_path: str, content: bytes, content_type: str = None) -> str:
        """Upload file and return public URL"""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """Download file content"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files with optional prefix"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for file access"""
        pass

class LocalStorageService(BaseStorageService):
    """Local file system storage service"""
    
    def __init__(self, config: CloudStorageConfig):
        self.config = config
        self.base_path = Path(config.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(self, file_path: str, content: bytes, content_type: str = None) -> str:
        """Upload file to local storage"""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(content)
        
        return f"/uploads/{file_path}"
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from local storage"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        full_path = self.base_path / file_path
        
        try:
            full_path.unlink()
            return True
        except FileNotFoundError:
            return False
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files in local storage"""
        search_path = self.base_path / prefix if prefix else self.base_path
        files = []
        
        if search_path.is_dir():
            for file_path in search_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.base_path)
                    files.append(str(relative_path))
        
        return files
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get URL for local file"""
        return f"/uploads/{file_path}"

class AWSS3StorageService(BaseStorageService):
    """AWS S3 storage service"""
    
    def __init__(self, config: CloudStorageConfig):
        self.config = config
        self._s3_client = None
    
    async def _get_s3_client(self):
        """Get S3 client (lazy initialization)"""
        if self._s3_client is None:
            try:
                import aioboto3
                
                session = aioboto3.Session()
                self._s3_client = session.client(
                    's3',
                    aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY,
                    region_name=self.config.AWS_REGION,
                    endpoint_url=self.config.AWS_S3_ENDPOINT_URL
                )
            except ImportError:
                raise ImportError("aioboto3 is required for AWS S3 support")
        
        return self._s3_client
    
    async def upload_file(self, file_path: str, content: bytes, content_type: str = None) -> str:
        """Upload file to S3"""
        s3 = await self._get_s3_client()
        
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        async with s3 as client:
            await client.put_object(
                Bucket=self.config.AWS_S3_BUCKET,
                Key=file_path,
                Body=content,
                **extra_args
            )
        
        if self.config.CDN_ENABLED and self.config.CDN_BASE_URL:
            return f"{self.config.CDN_BASE_URL}/{file_path}"
        
        return f"https://{self.config.AWS_S3_BUCKET}.s3.{self.config.AWS_REGION}.amazonaws.com/{file_path}"
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3"""
        s3 = await self._get_s3_client()
        
        async with s3 as client:
            response = await client.get_object(
                Bucket=self.config.AWS_S3_BUCKET,
                Key=file_path
            )
            return await response['Body'].read()
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        s3 = await self._get_s3_client()
        
        try:
            async with s3 as client:
                await client.delete_object(
                    Bucket=self.config.AWS_S3_BUCKET,
                    Key=file_path
                )
            return True
        except Exception:
            return False
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files in S3"""
        s3 = await self._get_s3_client()
        
        async with s3 as client:
            response = await client.list_objects_v2(
                Bucket=self.config.AWS_S3_BUCKET,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append(obj['Key'])
            
            return files
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for S3 file"""
        s3 = await self._get_s3_client()
        
        async with s3 as client:
            url = await client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.config.AWS_S3_BUCKET, 'Key': file_path},
                ExpiresIn=expires_in
            )
            return url

class GoogleCloudStorageService(BaseStorageService):
    """Google Cloud Storage service"""
    
    def __init__(self, config: CloudStorageConfig):
        self.config = config
        self._client = None
    
    async def _get_client(self):
        """Get GCS client (lazy initialization)"""
        if self._client is None:
            try:
                from google.cloud import storage
                
                if self.config.GCP_CREDENTIALS_PATH:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.GCP_CREDENTIALS_PATH
                
                self._client = storage.Client(project=self.config.GCP_PROJECT_ID)
            except ImportError:
                raise ImportError("google-cloud-storage is required for Google Cloud Storage support")
        
        return self._client
    
    async def upload_file(self, file_path: str, content: bytes, content_type: str = None) -> str:
        """Upload file to Google Cloud Storage"""
        client = await self._get_client()
        bucket = client.bucket(self.config.GCP_BUCKET)
        blob = bucket.blob(file_path)
        
        if content_type:
            blob.content_type = content_type
        
        # Run in thread pool since GCS client is sync
        await asyncio.get_event_loop().run_in_executor(
            None, blob.upload_from_string, content
        )
        
        return f"https://storage.googleapis.com/{self.config.GCP_BUCKET}/{file_path}"
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from Google Cloud Storage"""
        client = await self._get_client()
        bucket = client.bucket(self.config.GCP_BUCKET)
        blob = bucket.blob(file_path)
        
        return await asyncio.get_event_loop().run_in_executor(
            None, blob.download_as_bytes
        )
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Google Cloud Storage"""
        client = await self._get_client()
        bucket = client.bucket(self.config.GCP_BUCKET)
        blob = bucket.blob(file_path)
        
        try:
            await asyncio.get_event_loop().run_in_executor(None, blob.delete)
            return True
        except Exception:
            return False
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files in Google Cloud Storage"""
        client = await self._get_client()
        bucket = client.bucket(self.config.GCP_BUCKET)
        
        blobs = await asyncio.get_event_loop().run_in_executor(
            None, lambda: list(bucket.list_blobs(prefix=prefix))
        )
        
        return [blob.name for blob in blobs]
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for GCS file"""
        client = await self._get_client()
        bucket = client.bucket(self.config.GCP_BUCKET)
        blob = bucket.blob(file_path)
        
        from datetime import datetime, timedelta
        
        url = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: blob.generate_signed_url(
                expiration=datetime.utcnow() + timedelta(seconds=expires_in),
                method='GET'
            )
        )
        
        return url

# Storage service factory
class StorageServiceFactory:
    """Factory for creating storage service instances"""
    
    @staticmethod
    def create_storage_service(config: CloudStorageConfig) -> BaseStorageService:
        """Create storage service based on configuration"""
        
        if config.STORAGE_PROVIDER == StorageProvider.LOCAL:
            return LocalStorageService(config)
        elif config.STORAGE_PROVIDER == StorageProvider.AWS_S3:
            return AWSS3StorageService(config)
        elif config.STORAGE_PROVIDER == StorageProvider.GOOGLE_CLOUD:
            return GoogleCloudStorageService(config)
        elif config.STORAGE_PROVIDER == StorageProvider.CLOUDFLARE_R2:
            # Cloudflare R2 is S3-compatible
            config.AWS_S3_ENDPOINT_URL = config.CLOUDFLARE_R2_ENDPOINT
            config.AWS_ACCESS_KEY_ID = config.CLOUDFLARE_R2_ACCESS_KEY
            config.AWS_SECRET_ACCESS_KEY = config.CLOUDFLARE_R2_SECRET_KEY
            config.AWS_S3_BUCKET = config.CLOUDFLARE_R2_BUCKET
            return AWSS3StorageService(config)
        else:
            raise ValueError(f"Unsupported storage provider: {config.STORAGE_PROVIDER}")

# Global storage configuration and service
storage_config = CloudStorageConfig()
storage_service = StorageServiceFactory.create_storage_service(storage_config)

# Utility functions
async def upload_file(file_path: str, content: bytes, content_type: str = None) -> str:
    """Upload file using configured storage service"""
    return await storage_service.upload_file(file_path, content, content_type)

async def download_file(file_path: str) -> bytes:
    """Download file using configured storage service"""
    return await storage_service.download_file(file_path)

async def delete_file(file_path: str) -> bool:
    """Delete file using configured storage service"""
    return await storage_service.delete_file(file_path)

async def get_file_url(file_path: str, expires_in: int = 3600) -> str:
    """Get file URL using configured storage service"""
    return await storage_service.get_file_url(file_path, expires_in)

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    file_ext = Path(filename).suffix.lower()
    return file_ext in storage_config.ALLOWED_EXTENSIONS

def get_file_category(filename: str) -> str:
    """Get file category based on extension"""
    file_ext = Path(filename).suffix.lower()
    
    if file_ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]:
        return "image"
    elif file_ext in [".mp4", ".webm", ".mov", ".avi", ".mkv"]:
        return "video"
    elif file_ext in [".mp3", ".wav", ".ogg", ".m4a"]:
        return "audio"
    elif file_ext in [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt"]:
        return "document"
    elif file_ext in [".glb", ".gltf", ".fbx", ".obj", ".dae"]:
        return "3d_model"
    elif file_ext in [".zip", ".rar", ".7z"]:
        return "archive"
    else:
        return "other"