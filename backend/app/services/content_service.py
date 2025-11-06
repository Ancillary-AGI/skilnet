"""
Content management service for EduVerse platform
Handles video, audio, documents, and other course materials
"""

import os
import uuid
import mimetypes
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import aiofiles
import hashlib

from app.core.logging import get_logger, log_performance
from app.core.config import settings
from app.core.cloud_storage import storage_service
from app.models.course import Course
from app.models.user import User


class ContentService:
    """Service for managing course content and media files"""

    def __init__(self):
        self.logger = get_logger("content_service")
        self.allowed_video_types = ['.mp4', '.webm', '.avi', '.mov', '.mkv']
        self.allowed_audio_types = ['.mp3', '.wav', '.aac', '.ogg', '.m4a']
        self.allowed_document_types = ['.pdf', '.docx', '.pptx', '.txt', '.md']
        self.allowed_image_types = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']

    @log_performance
    async def upload_course_video(
        self,
        course_id: str,
        instructor_id: str,
        file_data: bytes,
        filename: str,
        content_type: str = None
    ) -> Dict[str, Any]:
        """Upload video content for a course"""
        try:
            # Validate course ownership
            course = await self._validate_course_ownership(course_id, instructor_id)
            if not course:
                raise ValueError("Course not found or access denied")

            # Validate file
            validation = self._validate_video_file(filename, len(file_data))
            if not validation["valid"]:
                raise ValueError(f"Invalid video file: {', '.join(validation['errors'])}")

            # Generate unique filename
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = f"courses/{course_id}/videos/{unique_filename}"

            # Upload to storage
            upload_result = await storage_service.upload_file(
                file_path=file_path,
                file_data=file_data,
                content_type=content_type or mimetypes.guess_type(filename)[0]
            )

            # Generate streaming URLs (HLS/DASH)
            streaming_urls = await self._generate_streaming_urls(file_path)

            # Update course with video URL
            # TODO: Update course model to store video URLs

            self.logger.info(f"Video uploaded for course {course_id}: {filename}")

            return {
                "success": True,
                "file_path": file_path,
                "file_url": upload_result,
                "streaming_urls": streaming_urls,
                "file_size": len(file_data),
                "content_type": content_type,
                "filename": filename
            }

        except Exception as e:
            self.logger.error(f"Video upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @log_performance
    async def upload_course_document(
        self,
        course_id: str,
        instructor_id: str,
        file_data: bytes,
        filename: str,
        content_type: str = None
    ) -> Dict[str, Any]:
        """Upload document/material for a course"""
        try:
            # Validate course ownership
            course = await self._validate_course_ownership(course_id, instructor_id)
            if not course:
                raise ValueError("Course not found or access denied")

            # Validate file
            validation = self._validate_document_file(filename, len(file_data))
            if not validation["valid"]:
                raise ValueError(f"Invalid document file: {', '.join(validation['errors'])}")

            # Generate unique filename
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = f"courses/{course_id}/documents/{unique_filename}"

            # Upload to storage
            upload_result = await storage_service.upload_file(
                file_path=file_path,
                file_data=file_data,
                content_type=content_type or mimetypes.guess_type(filename)[0]
            )

            self.logger.info(f"Document uploaded for course {course_id}: {filename}")

            return {
                "success": True,
                "file_path": file_path,
                "file_url": upload_result,
                "file_size": len(file_data),
                "content_type": content_type,
                "filename": filename
            }

        except Exception as e:
            self.logger.error(f"Document upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @log_performance
    async def upload_course_thumbnail(
        self,
        course_id: str,
        instructor_id: str,
        file_data: bytes,
        filename: str,
        content_type: str = None
    ) -> Dict[str, Any]:
        """Upload thumbnail image for a course"""
        try:
            # Validate course ownership
            course = await self._validate_course_ownership(course_id, instructor_id)
            if not course:
                raise ValueError("Course not found or access denied")

            # Validate file
            validation = self._validate_image_file(filename, len(file_data))
            if not validation["valid"]:
                raise ValueError(f"Invalid image file: {', '.join(validation['errors'])}")

            # Generate unique filename
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = f"courses/{course_id}/thumbnails/{unique_filename}"

            # Upload to storage
            upload_result = await storage_service.upload_file(
                file_path=file_path,
                file_data=file_data,
                content_type=content_type or mimetypes.guess_type(filename)[0]
            )

            # Generate different sizes
            thumbnail_urls = await self._generate_thumbnail_sizes(file_path)

            self.logger.info(f"Thumbnail uploaded for course {course_id}: {filename}")

            return {
                "success": True,
                "file_path": file_path,
                "file_url": upload_result,
                "thumbnail_urls": thumbnail_urls,
                "file_size": len(file_data),
                "content_type": content_type,
                "filename": filename
            }

        except Exception as e:
            self.logger.error(f"Thumbnail upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @log_performance
    async def get_course_content(self, course_id: str, content_type: str = None) -> List[Dict[str, Any]]:
        """Get all content for a course"""
        try:
            prefix = f"courses/{course_id}/"
            if content_type:
                prefix += f"{content_type}/"

            files = await storage_service.list_files(prefix)

            # Enrich with metadata
            content_list = []
            for file_info in files:
                content_list.append({
                    "path": file_info["path"],
                    "size": file_info["size"],
                    "modified": file_info["modified"],
                    "content_type": self._guess_content_type(file_info["path"]),
                    "url": await storage_service.get_file_url(file_info["path"])
                })

            return content_list

        except Exception as e:
            self.logger.error(f"Failed to get course content: {e}")
            return []

    @log_performance
    async def delete_course_content(
        self,
        course_id: str,
        instructor_id: str,
        file_path: str
    ) -> bool:
        """Delete course content"""
        try:
            # Validate course ownership
            course = await self._validate_course_ownership(course_id, instructor_id)
            if not course:
                raise ValueError("Course not found or access denied")

            # Ensure file belongs to this course
            if not file_path.startswith(f"courses/{course_id}/"):
                raise ValueError("File does not belong to this course")

            # Delete from storage
            success = await storage_service.delete_file(file_path)

            if success:
                self.logger.info(f"Content deleted for course {course_id}: {file_path}")

            return success

        except Exception as e:
            self.logger.error(f"Content deletion failed: {e}")
            return False

    @log_performance
    async def generate_content_metadata(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Generate metadata for uploaded content"""
        try:
            # Calculate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()

            # Get file info
            file_size = len(file_data)
            content_type = mimetypes.guess_type(file_path)[0]

            metadata = {
                "file_hash": file_hash,
                "file_size": file_size,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
            }

            # Add content-specific metadata
            if self._is_video_file(file_path):
                metadata.update(await self._get_video_metadata(file_data))
            elif self._is_audio_file(file_path):
                metadata.update(await self._get_audio_metadata(file_data))
            elif self._is_document_file(file_path):
                metadata.update(await self._get_document_metadata(file_data))

            return metadata

        except Exception as e:
            self.logger.error(f"Metadata generation failed: {e}")
            return {}

    def _validate_video_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate video file"""
        errors = []

        file_extension = Path(filename).suffix.lower()
        if file_extension not in self.allowed_video_types:
            errors.append(f"Unsupported video format. Allowed: {', '.join(self.allowed_video_types)}")

        if file_size > settings.MAX_FILE_SIZE:
            errors.append(f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _validate_document_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate document file"""
        errors = []

        file_extension = Path(filename).suffix.lower()
        if file_extension not in self.allowed_document_types:
            errors.append(f"Unsupported document format. Allowed: {', '.join(self.allowed_document_types)}")

        if file_size > settings.MAX_FILE_SIZE:
            errors.append(f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _validate_image_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate image file"""
        errors = []

        file_extension = Path(filename).suffix.lower()
        if file_extension not in self.allowed_image_types:
            errors.append(f"Unsupported image format. Allowed: {', '.join(self.allowed_image_types)}")

        # Thumbnails should be smaller
        if file_size > 5 * 1024 * 1024:  # 5MB limit for thumbnails
            errors.append("Thumbnail too large. Maximum size: 5MB")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def _generate_streaming_urls(self, file_path: str) -> Dict[str, str]:
        """Generate streaming URLs for video content"""
        # This would integrate with a video streaming service like Cloudflare Stream
        # For now, return basic URLs
        base_url = await storage_service.get_file_url(file_path)

        return {
            "direct": base_url,
            "hls": base_url.replace('.mp4', '.m3u8'),  # Placeholder for HLS
            "dash": base_url.replace('.mp4', '.mpd'),   # Placeholder for DASH
        }

    async def _generate_thumbnail_sizes(self, file_path: str) -> Dict[str, str]:
        """Generate different thumbnail sizes"""
        # This would use image processing to create different sizes
        # For now, return the original
        base_url = await storage_service.get_file_url(file_path)

        return {
            "original": base_url,
            "large": base_url,    # Placeholder
            "medium": base_url,   # Placeholder
            "small": base_url,    # Placeholder
        }

    async def _get_video_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract video metadata"""
        # This would use a library like moviepy or ffmpeg-python
        # For now, return basic info
        return {
            "duration": 0,  # Would extract actual duration
            "width": 1920,  # Would extract actual dimensions
            "height": 1080,
            "bitrate": 0,
            "codec": "unknown"
        }

    async def _get_audio_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract audio metadata"""
        # This would use a library like mutagen
        return {
            "duration": 0,
            "bitrate": 0,
            "sample_rate": 0,
            "channels": 0,
            "codec": "unknown"
        }

    async def _get_document_metadata(self, file_data: bytes) -> Dict[str, Any]:
        """Extract document metadata"""
        return {
            "pages": 0,  # Would extract page count for PDFs
            "word_count": 0,
            "language": "unknown"
        }

    def _guess_content_type(self, file_path: str) -> str:
        """Guess content type from file path"""
        if '/videos/' in file_path:
            return 'video'
        elif '/documents/' in file_path:
            return 'document'
        elif '/thumbnails/' in file_path:
            return 'image'
        elif '/audio/' in file_path:
            return 'audio'
        else:
            return 'unknown'

    def _is_video_file(self, file_path: str) -> bool:
        """Check if file is a video"""
        return Path(file_path).suffix.lower() in self.allowed_video_types

    def _is_audio_file(self, file_path: str) -> bool:
        """Check if file is audio"""
        return Path(file_path).suffix.lower() in self.allowed_audio_types

    def _is_document_file(self, file_path: str) -> bool:
        """Check if file is a document"""
        return Path(file_path).suffix.lower() in self.allowed_document_types

    async def _validate_course_ownership(self, course_id: str, instructor_id: str) -> Optional[Course]:
        """Validate that user owns the course"""
        # This would query the database to check course ownership
        # For now, return a mock course object
        from app.services.course_service import CourseService
        from app.core.database import get_db
        from sqlalchemy.ext.asyncio import AsyncSession

        # This is a simplified version - in real implementation,
        # we'd inject the db session properly
        return None  # Placeholder


# Global content service instance
content_service = ContentService()
