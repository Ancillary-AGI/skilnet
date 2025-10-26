"""
App update endpoints for EduVerse platform
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime
from packaging import version

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

# App version configurations
APP_VERSIONS = {
    "android": {
        "current_version": "2.0.0",
        "build_number": "200",
        "min_supported_version": "1.8.0",
        "download_url": f"{settings.APP_URL}/api/v1/app/download/android",
        "store_url": "https://play.google.com/store/apps/details?id=com.eduverse.app",
        "file_size_bytes": 45 * 1024 * 1024,  # 45MB
        "release_notes": """
🎉 What's New in EduVerse 2.0:

✨ New Features:
• Enhanced VR/AR learning experiences
• AI-powered personalized study plans
• Real-time collaboration tools
• Offline course downloads
• Advanced progress analytics

🔧 Improvements:
• 50% faster app performance
• Improved video streaming quality
• Better accessibility support
• Enhanced dark mode

🛡️ Security & Bug Fixes:
• Important security updates
• Fixed crash issues
• Improved data synchronization
• Better error handling

🌍 Accessibility:
• Screen reader improvements
• High contrast mode
• Larger text options
• Voice navigation support
        """,
        "is_mandatory": False,
        "is_security_update": True,
        "has_new_features": True,
        "release_date": "2024-01-15T10:00:00Z"
    },
    "ios": {
        "current_version": "2.0.0",
        "build_number": "200",
        "min_supported_version": "1.8.0",
        "download_url": None,  # iOS uses App Store
        "store_url": "https://apps.apple.com/app/eduverse/id123456789",
        "file_size_bytes": 52 * 1024 * 1024,  # 52MB
        "release_notes": """
🎉 What's New in EduVerse 2.0:

✨ New Features:
• Enhanced VR/AR learning with ARKit
• AI-powered personalized study plans
• Real-time collaboration tools
• Offline course downloads
• Advanced progress analytics
• Apple Watch companion app

🔧 Improvements:
• Native iOS 17 support
• Improved performance on all devices
• Better integration with Shortcuts app
• Enhanced Siri support

🛡️ Security & Bug Fixes:
• Important security updates
• Fixed memory leaks
• Improved data synchronization
• Better error handling

🌍 Accessibility:
• VoiceOver improvements
• Dynamic Type support
• Reduced motion options
• Voice Control compatibility
        """,
        "is_mandatory": False,
        "is_security_update": True,
        "has_new_features": True,
        "release_date": "2024-01-15T10:00:00Z"
    },
    "web": {
        "current_version": "2.0.0",
        "build_number": "200",
        "min_supported_version": "1.9.0",
        "download_url": None,  # Web updates automatically
        "store_url": None,
        "file_size_bytes": 0,  # Web updates are automatic
        "release_notes": """
🎉 What's New in EduVerse Web 2.0:

✨ New Features:
• Progressive Web App (PWA) support
• Offline functionality
• Push notifications
• WebRTC for real-time collaboration
• WebGL-based 3D learning environments

🔧 Improvements:
• 40% faster loading times
• Better mobile responsiveness
• Improved keyboard navigation
• Enhanced browser compatibility

🛡️ Security & Bug Fixes:
• Updated security headers
• Fixed CORS issues
• Improved error handling
• Better data validation

🌍 Accessibility:
• WCAG 2.1 AA compliance
• Screen reader improvements
• Keyboard navigation
• High contrast themes
        """,
        "is_mandatory": False,
        "is_security_update": True,
        "has_new_features": True,
        "release_date": "2024-01-15T10:00:00Z"
    }
}

@router.get("/updates")
async def check_for_updates(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Check for app updates"""
    
    # Get client information from headers
    platform = request.headers.get("X-Platform", "unknown").lower()
    current_version = request.headers.get("X-Current-Version", "0.0.0")
    current_build = request.headers.get("X-Build-Number", "0")
    
    if platform not in APP_VERSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform: {platform}"
        )
    
    app_config = APP_VERSIONS[platform]
    latest_version = app_config["current_version"]
    latest_build = int(app_config["build_number"])
    
    # Check if update is available
    has_update = False
    is_mandatory = False
    
    try:
        # Compare versions
        if version.parse(current_version) < version.parse(latest_version):
            has_update = True
        elif version.parse(current_version) == version.parse(latest_version):
            # Same version, check build number
            if int(current_build) < latest_build:
                has_update = True
        
        # Check if current version is below minimum supported
        min_version = app_config["min_supported_version"]
        if version.parse(current_version) < version.parse(min_version):
            is_mandatory = True
            has_update = True
            
    except Exception as e:
        # If version parsing fails, assume update is needed
        has_update = True
    
    response_data = {
        "hasUpdate": has_update,
        "platform": platform,
        "currentVersion": current_version,
        "currentBuild": current_build,
    }
    
    if has_update:
        response_data["updateInfo"] = {
            "version": latest_version,
            "buildNumber": app_config["build_number"],
            "releaseNotes": app_config["release_notes"],
            "downloadUrl": app_config["download_url"] or "",
            "storeUrl": app_config["store_url"],
            "isMandatory": is_mandatory or app_config.get("is_mandatory", False),
            "isSecurityUpdate": app_config["is_security_update"],
            "hasNewFeatures": app_config["has_new_features"],
            "fileSizeBytes": app_config["file_size_bytes"],
            "releaseDate": app_config["release_date"],
            "supportedPlatforms": list(APP_VERSIONS.keys()),
            "minSupportedVersion": min_version,
        }
    
    return response_data

@router.get("/download/{platform}")
async def download_app_update(
    platform: str,
    db: AsyncSession = Depends(get_db)
):
    """Download app update file"""
    
    if platform not in APP_VERSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform: {platform}"
        )
    
    # For Android, serve APK file
    if platform == "android":
        apk_path = os.path.join(settings.UPLOAD_DIR, "app_updates", "eduverse-latest.apk")
        
        if not os.path.exists(apk_path):
            # Create a mock APK file for development
            os.makedirs(os.path.dirname(apk_path), exist_ok=True)
            with open(apk_path, "wb") as f:
                f.write(b"Mock APK file content for development")
        
        if os.path.exists(apk_path):
            return FileResponse(
                apk_path,
                media_type="application/vnd.android.package-archive",
                filename=f"eduverse-{APP_VERSIONS[platform]['current_version']}.apk",
                headers={
                    "Content-Disposition": f"attachment; filename=eduverse-{APP_VERSIONS[platform]['current_version']}.apk"
                }
            )
    
    # For other platforms, redirect to store
    app_config = APP_VERSIONS[platform]
    if app_config["store_url"]:
        return {"redirect_url": app_config["store_url"]}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Download not available for this platform"
    )

@router.get("/version-info")
async def get_version_info(
    platform: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get version information for all platforms or specific platform"""
    
    if platform:
        if platform not in APP_VERSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        return {platform: APP_VERSIONS[platform]}
    
    return APP_VERSIONS

@router.post("/update-feedback")
async def submit_update_feedback(
    feedback_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback about app update"""
    
    # Log update feedback for analytics
    feedback = {
        "platform": feedback_data.get("platform"),
        "version": feedback_data.get("version"),
        "rating": feedback_data.get("rating"),
        "comment": feedback_data.get("comment"),
        "update_success": feedback_data.get("update_success", True),
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # In production, save to database
    print(f"Update feedback received: {feedback}")
    
    return {"message": "Feedback received successfully"}

@router.get("/changelog")
async def get_changelog(
    platform: Optional[str] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get app changelog"""
    
    # Mock changelog data - in production, this would come from database
    changelog = [
        {
            "version": "2.0.0",
            "build_number": "200",
            "release_date": "2024-01-15T10:00:00Z",
            "platform": "all",
            "type": "major",
            "changes": [
                "Enhanced VR/AR learning experiences",
                "AI-powered personalized study plans",
                "Real-time collaboration tools",
                "Offline course downloads",
                "Advanced progress analytics",
                "Important security updates"
            ]
        },
        {
            "version": "1.9.5",
            "build_number": "195",
            "release_date": "2024-01-01T10:00:00Z",
            "platform": "all",
            "type": "patch",
            "changes": [
                "Fixed video playback issues",
                "Improved app stability",
                "Bug fixes and performance improvements"
            ]
        },
        {
            "version": "1.9.0",
            "build_number": "190",
            "release_date": "2023-12-15T10:00:00Z",
            "platform": "all",
            "type": "minor",
            "changes": [
                "New course categories",
                "Improved search functionality",
                "Enhanced user profiles",
                "Better notification system"
            ]
        }
    ]
    
    if platform:
        changelog = [entry for entry in changelog if entry["platform"] in ["all", platform]]
    
    return {
        "changelog": changelog[:limit],
        "total": len(changelog)
    }

@router.get("/rollout-status")
async def get_rollout_status(
    platform: str,
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """Get rollout status for a specific version"""
    
    # Mock rollout data - in production, this would track actual rollout metrics
    rollout_status = {
        "version": version,
        "platform": platform,
        "rollout_percentage": 100,  # 100% rollout
        "total_users": 50000,
        "updated_users": 45000,
        "success_rate": 98.5,
        "rollout_start_date": "2024-01-15T10:00:00Z",
        "rollout_completion_date": "2024-01-20T10:00:00Z",
        "status": "completed",  # staged, rolling_out, completed, paused, rolled_back
        "issues": []
    }
    
    return rollout_status

@router.post("/force-update")
async def force_update_version(
    platform: str,
    version: str,
    is_mandatory: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Force update for specific platform and version (Admin only)"""
    
    # This would typically require admin authentication
    # For now, just update the configuration
    
    if platform in APP_VERSIONS:
        APP_VERSIONS[platform]["is_mandatory"] = is_mandatory
        
        return {
            "message": f"Force update {'enabled' if is_mandatory else 'disabled'} for {platform} version {version}",
            "platform": platform,
            "version": version,
            "is_mandatory": is_mandatory
        }
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported platform: {platform}"
    )