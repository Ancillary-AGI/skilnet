"""
Content management schemas for EduVerse platform
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContentUploadResponse(BaseModel):
    """Response schema for content upload"""
    success: bool = Field(..., description="Upload success status")
    file_path: Optional[str] = Field(None, description="Path where file was stored")
    file_url: Optional[str] = Field(None, description="Public URL to access the file")
    streaming_urls: Optional[Dict[str, str]] = Field(None, description="Streaming URLs for video content")
    thumbnail_urls: Optional[Dict[str, str]] = Field(None, description="Thumbnail URLs for images")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="MIME content type")
    filename: Optional[str] = Field(None, description="Original filename")
    error: Optional[str] = Field(None, description="Error message if upload failed")


class ContentMetadata(BaseModel):
    """Content metadata schema"""
    file_hash: str = Field(..., description="SHA256 hash of file content")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME content type")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    duration: Optional[int] = Field(None, description="Duration for audio/video (seconds)")
    width: Optional[int] = Field(None, description="Width for images/videos")
    height: Optional[int] = Field(None, description="Height for images/videos")
    bitrate: Optional[int] = Field(None, description="Bitrate for audio/video")
    codec: Optional[str] = Field(None, description="Codec information")
    pages: Optional[int] = Field(None, description="Page count for documents")
    word_count: Optional[int] = Field(None, description="Word count for documents")
    language: Optional[str] = Field(None, description="Detected language")


class ContentInfo(BaseModel):
    """Basic content information schema"""
    path: str = Field(..., description="File path")
    size: int = Field(..., description="File size in bytes")
    modified: str = Field(..., description="Last modified timestamp")
    content_type: str = Field(..., description="Content type category")
    url: str = Field(..., description="Access URL")
    metadata: Optional[ContentMetadata] = Field(None, description="Extended metadata")


class ContentListResponse(BaseModel):
    """Response schema for content listing"""
    course_id: str = Field(..., description="Course ID")
    content: List[ContentInfo] = Field([], description="List of content items")
    total: int = Field(0, description="Total number of items")


class ContentValidationResult(BaseModel):
    """Content validation result schema"""
    valid: bool = Field(..., description="Validation success")
    errors: List[str] = Field([], description="Validation error messages")
    warnings: List[str] = Field([], description="Validation warnings")


class ContentProcessingRequest(BaseModel):
    """Content processing request schema"""
    course_id: str = Field(..., description="Course ID")
    content_type: str = Field(..., description="Type of content to process")
    options: Optional[Dict[str, Any]] = Field(None, description="Processing options")


class ContentProcessingStatus(BaseModel):
    """Content processing status schema"""
    status: str = Field(..., description="Processing status")
    progress: Optional[float] = Field(None, description="Processing progress (0-100)")
    message: Optional[str] = Field(None, description="Status message")
    estimated_time: Optional[int] = Field(None, description="Estimated time remaining (seconds)")
    results: Optional[Dict[str, Any]] = Field(None, description="Processing results")


class BulkUploadRequest(BaseModel):
    """Bulk upload request schema"""
    course_id: str = Field(..., description="Course ID")
    content_type: str = Field(..., description="Type of content being uploaded")
    files: List[str] = Field(..., description="List of file identifiers")


class BulkUploadResult(BaseModel):
    """Bulk upload result schema"""
    total_files: int = Field(..., description="Total number of files processed")
    successful_uploads: int = Field(..., description="Number of successful uploads")
    failed_uploads: int = Field(..., description="Number of failed uploads")
    results: List[Dict[str, Any]] = Field([], description="Detailed results for each file")


class ContentStreamingInfo(BaseModel):
    """Content streaming information schema"""
    stream_url: str = Field(..., description="Streaming URL")
    content_type: str = Field(..., description="Content type")
    filename: str = Field(..., description="Original filename")
    duration: Optional[int] = Field(None, description="Content duration")
    quality_options: Optional[List[str]] = Field(None, description="Available quality options")
    subtitles: Optional[List[str]] = Field(None, description="Available subtitle languages")


class ContentAccessLog(BaseModel):
    """Content access logging schema"""
    user_id: str = Field(..., description="User ID accessing content")
    course_id: str = Field(..., description="Course ID")
    content_path: str = Field(..., description="Content file path")
    access_type: str = Field(..., description="Type of access (view, download, stream)")
    timestamp: datetime = Field(..., description="Access timestamp")
    ip_address: Optional[str] = Field(None, description="User IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    session_duration: Optional[int] = Field(None, description="Session duration in seconds")


class ContentAnalytics(BaseModel):
    """Content analytics schema"""
    content_path: str = Field(..., description="Content file path")
    total_views: int = Field(0, description="Total view count")
    unique_viewers: int = Field(0, description="Unique viewer count")
    average_view_duration: float = Field(0.0, description="Average view duration")
    completion_rate: float = Field(0.0, description="Content completion rate")
    drop_off_points: Optional[List[Dict[str, Any]]] = Field(None, description="Points where users drop off")
    popular_times: Optional[List[Dict[str, Any]]] = Field(None, description="Popular viewing times")


class ContentQuotaInfo(BaseModel):
    """Content storage quota information"""
    used_storage: int = Field(..., description="Used storage in bytes")
    total_quota: int = Field(..., description="Total quota in bytes")
    available_storage: int = Field(..., description="Available storage in bytes")
    files_count: int = Field(..., description="Total number of files")
    quota_percentage: float = Field(..., description="Quota usage percentage")


class ContentBackupInfo(BaseModel):
    """Content backup information"""
    last_backup: Optional[datetime] = Field(None, description="Last backup timestamp")
    backup_status: str = Field(..., description="Backup status")
    backup_size: Optional[int] = Field(None, description="Backup size in bytes")
    next_backup: Optional[datetime] = Field(None, description="Next scheduled backup")


class ContentSecurityScan(BaseModel):
    """Content security scan results"""
    file_path: str = Field(..., description="Scanned file path")
    scan_status: str = Field(..., description="Scan status (clean, infected, error)")
    scan_timestamp: datetime = Field(..., description="Scan timestamp")
    threats_found: Optional[List[str]] = Field(None, description="Detected threats")
    scan_engine: str = Field(..., description="Scanning engine used")
    scan_duration: float = Field(..., description="Scan duration in seconds")
