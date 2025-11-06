"""
Content management endpoints for EduVerse platform
Handles file uploads, video streaming, and content delivery
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.content_service import content_service
from app.schemas.content import ContentUploadResponse, ContentListResponse

router = APIRouter()

@router.post("/courses/{course_id}/videos", response_model=ContentUploadResponse)
async def upload_course_video(
    course_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload video content for a course (instructor only)"""
    try:
        # Read file data
        file_data = await file.read()

        # Upload video
        result = await content_service.upload_course_video(
            course_id=course_id,
            instructor_id=current_user.id,
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return ContentUploadResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video upload failed: {str(e)}"
        )

@router.post("/courses/{course_id}/documents", response_model=ContentUploadResponse)
async def upload_course_document(
    course_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload document/material for a course (instructor only)"""
    try:
        # Read file data
        file_data = await file.read()

        # Upload document
        result = await content_service.upload_course_document(
            course_id=course_id,
            instructor_id=current_user.id,
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return ContentUploadResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )

@router.post("/courses/{course_id}/thumbnail", response_model=ContentUploadResponse)
async def upload_course_thumbnail(
    course_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload thumbnail image for a course (instructor only)"""
    try:
        # Read file data
        file_data = await file.read()

        # Upload thumbnail
        result = await content_service.upload_course_thumbnail(
            course_id=course_id,
            instructor_id=current_user.id,
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return ContentUploadResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Thumbnail upload failed: {str(e)}"
        )

@router.get("/courses/{course_id}/content")
async def get_course_content(
    course_id: str,
    content_type: Optional[str] = Query(None, description="Filter by content type (video, document, image, audio)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all content for a course"""
    try:
        # TODO: Add proper access control - enrolled students should see course content
        content_list = await content_service.get_course_content(course_id, content_type)

        return {
            "course_id": course_id,
            "content": content_list,
            "total": len(content_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course content: {str(e)}"
        )

@router.delete("/courses/{course_id}/content")
async def delete_course_content(
    course_id: str,
    file_path: str = Query(..., description="Path of the file to delete"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete course content (instructor only)"""
    try:
        success = await content_service.delete_course_content(
            course_id=course_id,
            instructor_id=current_user.id,
            file_path=file_path
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete content"
            )

        return {"message": "Content deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content deletion failed: {str(e)}"
        )

@router.get("/stream/{course_id}/{content_type}/{filename}")
async def stream_course_content(
    course_id: str,
    content_type: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream course content (enrolled students only)"""
    try:
        # TODO: Add enrollment check
        file_path = f"courses/{course_id}/{content_type}/{filename}"

        # Check if file exists
        exists = await content_service._storage_service.file_exists(file_path)
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        # Get streaming URL
        stream_url = await content_service._storage_service.get_file_url(file_path)

        return {
            "stream_url": stream_url,
            "content_type": content_type,
            "filename": filename
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content streaming failed: {str(e)}"
        )

@router.post("/courses/{course_id}/bulk-upload")
async def bulk_upload_course_content(
    course_id: str,
    files: List[UploadFile] = File(...),
    content_type: str = Form(..., description="Type of content (videos, documents, images)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk upload multiple files for a course (instructor only)"""
    try:
        results = []

        for file in files:
            file_data = await file.read()

            # Determine upload method based on content type
            if content_type == "videos":
                result = await content_service.upload_course_video(
                    course_id=course_id,
                    instructor_id=current_user.id,
                    file_data=file_data,
                    filename=file.filename,
                    content_type=file.content_type
                )
            elif content_type == "documents":
                result = await content_service.upload_course_document(
                    course_id=course_id,
                    instructor_id=current_user.id,
                    file_data=file_data,
                    filename=file.filename,
                    content_type=file.content_type
                )
            elif content_type == "images" or content_type == "thumbnails":
                result = await content_service.upload_course_thumbnail(
                    course_id=course_id,
                    instructor_id=current_user.id,
                    file_data=file_data,
                    filename=file.filename,
                    content_type=file.content_type
                )
            else:
                result = {"success": False, "error": f"Unsupported content type: {content_type}"}

            results.append({
                "filename": file.filename,
                **result
            })

        successful_uploads = sum(1 for r in results if r.get("success", False))

        return {
            "message": f"Processed {len(files)} files, {successful_uploads} successful",
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk upload failed: {str(e)}"
        )

@router.get("/content/metadata")
async def get_content_metadata(
    file_path: str = Query(..., description="Path of the content file"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get metadata for content file"""
    try:
        # TODO: Add access control
        # For now, just return basic info
        exists = await content_service._storage_service.file_exists(file_path)

        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )

        # Get file info from storage
        files = await content_service._storage_service.list_files(file_path)
        if files:
            file_info = files[0]
            return {
                "path": file_info["path"],
                "size": file_info["size"],
                "modified": file_info["modified"],
                "url": await content_service._storage_service.get_file_url(file_path)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content metadata not available"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata retrieval failed: {str(e)}"
        )

@router.post("/content/process/{course_id}")
async def process_course_content(
    course_id: str,
    content_type: str = Query(..., description="Type of content to process"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process uploaded content (generate thumbnails, transcode videos, etc.)"""
    try:
        # TODO: Implement content processing pipeline
        # This would trigger background jobs for:
        # - Video transcoding to multiple formats
        # - Thumbnail generation
        # - Content analysis and tagging
        # - Metadata extraction

        return {
            "message": f"Content processing started for course {course_id}",
            "content_type": content_type,
            "status": "processing"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content processing failed: {str(e)}"
        )
