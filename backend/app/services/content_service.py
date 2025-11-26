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

            # Store video information in course
            await self._store_video_in_course(course_id, {
                "file_path": file_path,
                "file_url": upload_result,
                "streaming_urls": streaming_urls,
                "filename": filename,
                "uploaded_at": datetime.utcnow().isoformat()
            })

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

    @log_performance
    async def process_content_item(
        self,
        course_id: str,
        content_path: str,
        content_type: str,
        instructor_id: str
    ) -> Dict[str, Any]:
        """Process a single content item"""
        try:
            # Validate course ownership
            course = await self._validate_course_ownership(course_id, instructor_id)
            if not course:
                raise ValueError("Course not found or access denied")

            # Download content for processing
            content_data = await storage_service.download_file(content_path)
            if not content_data:
                raise ValueError(f"Could not download content: {content_path}")

            processing_result = {
                "content_path": content_path,
                "content_type": content_type,
                "processed_at": datetime.utcnow().isoformat(),
                "operations": []
            }

            # Process based on content type
            if content_type == "videos":
                result = await self._process_video_content(content_path, content_data)
                processing_result["operations"].extend(result["operations"])
                processing_result.update(result)

            elif content_type == "images" or content_type == "thumbnails":
                result = await self._process_image_content(content_path, content_data)
                processing_result["operations"].extend(result["operations"])
                processing_result.update(result)

            elif content_type == "documents":
                result = await self._process_document_content(content_path, content_data)
                processing_result["operations"].extend(result["operations"])
                processing_result.update(result)

            # Update metadata
            metadata = await self.generate_content_metadata(content_path, content_data)
            processing_result["metadata"] = metadata

            self.logger.info(f"Processed content: {content_path}")
            return processing_result

        except Exception as e:
            self.logger.error(f"Content processing failed for {content_path}: {e}")
            return {
                "content_path": content_path,
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat(),
                "status": "failed"
            }

    @log_performance
    async def update_course_video_urls(self, course_id: str, processing_results: List[Dict[str, Any]]) -> None:
        """Update course with processed video URLs"""
        try:
            # Collect all video URLs from processing results
            video_urls = []
            for result in processing_results:
                if result.get("streaming_urls"):
                    video_urls.append({
                        "original_path": result["content_path"],
                        "streaming_urls": result["streaming_urls"],
                        "duration": result.get("metadata", {}).get("duration", 0),
                        "processed_at": result["processed_at"]
                    })

            if video_urls:
                # Update course with video information
                from app.core.database import get_db
                from sqlalchemy import update

                async with get_db() as db:
                    # For now, store as JSON in a new field or update existing video field
                    # This would need a course model update to properly store multiple videos
                    await db.execute(
                        update(Course)
                        .where(Course.id == course_id)
                        .values(video_content=video_urls)
                    )
                    await db.commit()

                self.logger.info(f"Updated course {course_id} with {len(video_urls)} processed videos")

        except Exception as e:
            self.logger.error(f"Failed to update course video URLs: {e}")

    async def _process_video_content(self, content_path: str, content_data: bytes) -> Dict[str, Any]:
        """Process video content - transcode, generate thumbnails, etc."""
        operations = []

        try:
            # Generate streaming URLs (HLS/DASH)
            streaming_urls = await self._generate_streaming_urls(content_path)
            operations.append("streaming_urls_generated")

            # Generate thumbnail from video
            thumbnail_path = content_path.replace('/videos/', '/thumbnails/').replace('.mp4', '_thumb.jpg')
            thumbnail_result = await self._generate_video_thumbnail(content_path, thumbnail_path)
            if thumbnail_result["success"]:
                operations.append("thumbnail_generated")

            # Extract metadata
            metadata = await self._get_video_metadata(content_data)
            operations.append("metadata_extracted")

            return {
                "streaming_urls": streaming_urls,
                "thumbnail_url": thumbnail_result.get("url"),
                "metadata": metadata,
                "operations": operations,
                "status": "success"
            }

        except Exception as e:
            return {
                "error": str(e),
                "operations": operations,
                "status": "partial_success" if operations else "failed"
            }

    async def _process_image_content(self, content_path: str, content_data: bytes) -> Dict[str, Any]:
        """Process image content - generate different sizes"""
        operations = []

        try:
            # Generate different thumbnail sizes
            sizes = await self._generate_thumbnail_sizes(content_path)
            operations.append("sizes_generated")

            return {
                "thumbnail_sizes": sizes,
                "operations": operations,
                "status": "success"
            }

        except Exception as e:
            return {
                "error": str(e),
                "operations": operations,
                "status": "failed"
            }

    async def _process_document_content(self, content_path: str, content_data: bytes) -> Dict[str, Any]:
        """Process document content - extract text, generate preview"""
        operations = []

        try:
            # Extract document metadata
            metadata = await self._get_document_metadata(content_data)
            operations.append("metadata_extracted")

            # Generate preview/thumbnail if possible
            preview_result = await self._generate_document_preview(content_path, content_data)
            if preview_result["success"]:
                operations.append("preview_generated")

            return {
                "metadata": metadata,
                "preview_url": preview_result.get("url"),
                "operations": operations,
                "status": "success"
            }

        except Exception as e:
            return {
                "error": str(e),
                "operations": operations,
                "status": "failed"
            }

    async def _generate_video_thumbnail(self, video_path: str, thumbnail_path: str) -> Dict[str, Any]:
        """Generate thumbnail from video"""
        try:
            # This would use ffmpeg or similar to extract a frame
            # For now, create a placeholder
            thumbnail_data = b"placeholder_thumbnail_data"
            upload_result = await storage_service.upload_file(
                file_path=thumbnail_path,
                file_data=thumbnail_data,
                content_type="image/jpeg"
            )

            return {
                "success": True,
                "url": upload_result,
                "path": thumbnail_path
            }

        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_document_preview(self, document_path: str, document_data: bytes) -> Dict[str, Any]:
        """Generate preview for document"""
        try:
            # This would convert first page to image
            # For now, create a placeholder
            preview_path = document_path.replace('/documents/', '/previews/').replace('.pdf', '_preview.jpg')
            preview_data = b"placeholder_preview_data"
            upload_result = await storage_service.upload_file(
                file_path=preview_path,
                file_data=preview_data,
                content_type="image/jpeg"
            )

            return {
                "success": True,
                "url": upload_result,
                "path": preview_path
            }

        except Exception as e:
            self.logger.error(f"Document preview generation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _store_video_in_course(self, course_id: str, video_info: Dict[str, Any]) -> None:
        """Store video information in course model"""
        try:
            from app.core.database import get_db
            from sqlalchemy import select, update

            async with get_db() as db:
                # Get current video content
                result = await db.execute(
                    select(Course.video_content).where(Course.id == course_id)
                )
                current_videos = result.scalar_one_or_none() or []

                # Add new video to the list
                current_videos.append(video_info)

                # Update course
                await db.execute(
                    update(Course)
                    .where(Course.id == course_id)
                    .values(video_content=current_videos)
                )
                await db.commit()

        except Exception as e:
            self.logger.error(f"Failed to store video in course: {e}")

    async def _validate_course_ownership(self, course_id: str, instructor_id: str) -> Optional[Course]:
        """Validate that user owns the course"""
        try:
            # Query the database to check course ownership
            from app.core.database import get_db
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy import select

            async with get_db() as db:
                # Query to check if the user is the instructor of the course
                result = await db.execute(
                    select(Course).where(
                        Course.id == course_id,
                        Course.instructor_id == instructor_id
                    )
                )
                course = result.scalar_one_or_none()

                if course:
                    return course
                else:
                    self.logger.warning(f"Course {course_id} not found or user {instructor_id} is not the instructor")
                    return None

        except Exception as e:
            self.logger.error(f"Error validating course ownership: {e}")
            return None


# Global content service instance
content_service = ContentService()
