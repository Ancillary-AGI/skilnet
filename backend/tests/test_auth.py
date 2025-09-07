"""
Comprehensive authentication tests
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
import json

from app.main import app
from app.core.database import get_db
from backend.app.models.profile import User
from app.core.security import SecurityManager
from tests.conftest import TestDatabase


class TestAuthentication:
    """Test authentication endpoints and security"""

    @pytest.mark.asyncio
    async def test_user_registration_success(self, client: AsyncClient, db: AsyncSession):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "first_name": "Test",
            "last_name": "User",
            "learning_style": "visual"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "password" not in data  # Password should not be returned
        assert data["is_verified"] == False  # Should require email verification

    @pytest.mark.asyncio
    async def test_user_registration_duplicate_email(self, client: AsyncClient, db: AsyncSession):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }
        
        # First registration
        await client.post("/api/v1/auth/register", json=user_data)
        
        # Second registration with same email
        user_data["username"] = "user2"
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_user_login_success(self, client: AsyncClient, test_user: User):
        """Test successful user login"""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_user_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(self, client: AsyncClient, auth_headers: dict):
        """Test accessing protected endpoint with valid token"""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "username" in data

    @pytest.mark.asyncio
    async def test_token_refresh(self, client: AsyncClient, test_user: User):
        """Test token refresh functionality"""
        # Login to get tokens
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        tokens = login_response.json()
        
        # Use refresh token to get new access token
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]  # Should be different

    @pytest.mark.asyncio
    async def test_password_reset_flow(self, client: AsyncClient, test_user: User):
        """Test password reset flow"""
        # Request password reset
        reset_request = {"email": test_user.email}
        response = await client.post("/api/v1/auth/forgot-password", json=reset_request)
        
        assert response.status_code == status.HTTP_200_OK
        assert "reset link has been sent" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_two_factor_setup(self, client: AsyncClient, auth_headers: dict):
        """Test two-factor authentication setup"""
        setup_data = {"password": "testpassword123"}
        response = await client.post("/api/v1/auth/2fa/setup", json=setup_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "qr_code" in data
        assert "backup_codes" in data
        assert len(data["backup_codes"]) == 10

    @pytest.mark.asyncio
    async def test_oauth_login_google(self, client: AsyncClient):
        """Test OAuth login with Google"""
        oauth_data = {
            "code": "mock_google_auth_code",
            "redirect_uri": "http://localhost:3000/auth/callback"
        }
        
        response = await client.post("/api/v1/auth/oauth/google", json=oauth_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["user"]["oauth_providers"] == ["google"]

    @pytest.mark.asyncio
    async def test_webauthn_registration_flow(self, client: AsyncClient, auth_headers: dict):
        """Test WebAuthn (passkey) registration"""
        # Start registration
        response = await client.post("/api/v1/auth/webauthn/register/start", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "options" in data
        assert "challenge" in data

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client: AsyncClient):
        """Test rate limiting on login endpoint"""
        login_data = {
            "username": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Make multiple failed login attempts
        for _ in range(10):
            response = await client.post("/api/v1/auth/login", data=login_data)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        
        # Should eventually hit rate limit
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_session_timeout(self, client: AsyncClient, auth_headers: dict):
        """Test session timeout handling"""
        # Mock expired token
        expired_headers = {
            "Authorization": "Bearer expired_token_here"
        }
        
        response = await client.get("/api/v1/auth/me", headers=expired_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSecurity:
    """Test security features and vulnerabilities"""

    def test_password_hashing(self):
        """Test password hashing security"""
        password = "testpassword123"
        hashed = SecurityManager.get_password_hash(password)
        
        # Should not store plain text
        assert password != hashed
        assert len(hashed) > 50  # Bcrypt hashes are long
        
        # Should verify correctly
        assert SecurityManager.verify_password(password, hashed)
        assert not SecurityManager.verify_password("wrongpassword", hashed)

    def test_jwt_token_creation_and_verification(self):
        """Test JWT token security"""
        user_data = {"sub": "user123", "email": "test@example.com"}
        token = SecurityManager.create_access_token(user_data)
        
        # Should create valid token
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long
        
        # Should verify correctly
        payload = SecurityManager.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"

    def test_invalid_jwt_token(self):
        """Test invalid JWT token handling"""
        invalid_token = "invalid.jwt.token"
        payload = SecurityManager.verify_token(invalid_token)
        
        assert payload is None

    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, client: AsyncClient):
        """Test SQL injection protection"""
        malicious_input = "'; DROP TABLE users; --"
        
        user_data = {
            "email": f"test{malicious_input}@example.com",
            "username": f"user{malicious_input}",
            "password": "password123"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # Should handle malicious input safely
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    @pytest.mark.asyncio
    async def test_xss_protection(self, client: AsyncClient, auth_headers: dict):
        """Test XSS protection"""
        malicious_script = "<script>alert('xss')</script>"
        
        # Try to inject script in profile update
        profile_data = {
            "bio": malicious_script,
            "display_name": f"User{malicious_script}"
        }
        
        response = await client.put("/api/v1/users/profile", json=profile_data, headers=auth_headers)
        
        # Should sanitize or reject malicious input
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "<script>" not in data.get("bio", "")
            assert "<script>" not in data.get("display_name", "")


class TestPerformance:
    """Test performance and scalability"""

    @pytest.mark.asyncio
    async def test_concurrent_logins(self, client: AsyncClient):
        """Test handling concurrent login requests"""
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        
        # Create multiple concurrent login requests
        tasks = []
        for _ in range(50):
            task = client.post("/api/v1/auth/login", data=login_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle concurrent requests without errors
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) > 0

    @pytest.mark.asyncio
    async def test_database_connection_pooling(self, client: AsyncClient):
        """Test database connection pooling under load"""
        # Make multiple concurrent database requests
        tasks = []
        for _ in range(100):
            task = client.get("/api/v1/courses/")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle all requests without connection errors
        successful_responses = [
            r for r in responses 
            if not isinstance(r, Exception) and r.status_code == status.HTTP_200_OK
        ]
        assert len(successful_responses) == 100

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, client: AsyncClient):
        """Test memory usage under heavy load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate load
        tasks = []
        for i in range(200):
            task = client.get(f"/api/v1/courses/?skip={i}&limit=20")
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024


class TestAccessibility:
    """Test accessibility features"""

    @pytest.mark.asyncio
    async def test_screen_reader_compatibility(self, client: AsyncClient):
        """Test API responses for screen reader compatibility"""
        response = await client.get("/api/v1/courses/")
        
        assert response.status_code == status.HTTP_200_OK
        courses = response.json()
        
        # Should have descriptive fields for screen readers
        for course in courses:
            assert "title" in course
            assert "description" in course
            assert "instructor" in course

    @pytest.mark.asyncio
    async def test_high_contrast_support(self, client: AsyncClient, auth_headers: dict):
        """Test high contrast mode support"""
        # Update user preferences for high contrast
        preferences = {
            "accessibility_settings": {
                "high_contrast_mode": True,
                "large_text": True,
                "reduced_motion": True
            }
        }
        
        response = await client.put(
            "/api/v1/users/preferences", 
            json=preferences, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_keyboard_navigation_support(self, client: AsyncClient):
        """Test keyboard navigation support in API responses"""
        response = await client.get("/api/v1/courses/")
        
        assert response.status_code == status.HTTP_200_OK
        courses = response.json()
        
        # Should provide navigation hints
        for course in courses:
            assert "id" in course  # For keyboard navigation
            assert "title" in course  # For screen readers


class TestVRClassroom:
    """Test VR classroom functionality"""

    @pytest.mark.asyncio
    async def test_vr_session_creation(self, client: AsyncClient, auth_headers: dict):
        """Test VR classroom session creation"""
        session_data = {
            "room_name": "Test VR Classroom",
            "max_participants": 30,
            "environment": "modern_classroom",
            "features": ["whiteboard", "3d_models", "spatial_audio"]
        }
        
        response = await client.post(
            "/api/v1/vr/sessions", 
            json=session_data, 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["room_name"] == session_data["room_name"]
        assert data["max_participants"] == session_data["max_participants"]

    @pytest.mark.asyncio
    async def test_vr_spatial_tracking(self, client: AsyncClient, auth_headers: dict):
        """Test VR spatial position tracking"""
        spatial_data = {
            "position": [1.5, 0.0, -2.0],
            "rotation": [0.0, 0.707, 0.0, 0.707],
            "head_position": [1.5, 1.7, -2.0],
            "hand_positions": {
                "left": [1.2, 1.2, -1.8],
                "right": [1.8, 1.2, -1.8]
            }
        }
        
        response = await client.post(
            "/api/v1/vr/sessions/test-room/spatial-update",
            json=spatial_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_vr_object_interaction(self, client: AsyncClient, auth_headers: dict):
        """Test VR object interaction"""
        interaction_data = {
            "object_id": "whiteboard_1",
            "action": "draw",
            "interaction_data": {
                "stroke_data": [[100, 150], [120, 160], [140, 170]],
                "color": "#FF0000",
                "thickness": 3
            }
        }
        
        response = await client.post(
            "/api/v1/vr/sessions/test-room/object-interaction",
            json=interaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK


class TestAIFeatures:
    """Test AI-powered features"""

    @pytest.mark.asyncio
    async def test_ai_content_generation(self, client: AsyncClient, auth_headers: dict):
        """Test AI content generation"""
        content_request = {
            "type": "video",
            "topic": "Introduction to Machine Learning",
            "duration": 300,
            "style": "professional",
            "target_audience": "beginners"
        }
        
        response = await client.post(
            "/api/v1/courses/test-course-id/generate-ai-content",
            json=content_request,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["type"] == "video"
        assert "content_url" in data

    @pytest.mark.asyncio
    async def test_ai_tutor_interaction(self, client: AsyncClient, auth_headers: dict):
        """Test AI tutor chat functionality"""
        chat_data = {
            "message": "Can you explain quantum computing?",
            "context": {
                "current_course": "physics_101",
                "current_lesson": "quantum_basics",
                "user_level": "beginner"
            }
        }
        
        response = await client.post(
            "/api/v1/ai/chat",
            json=chat_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "confidence" in data
        assert data["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_video_model_training(self, client: AsyncClient, auth_headers: dict):
        """Test video model training"""
        training_config = {
            "epochs": 10,
            "batch_size": 4,
            "learning_rate": 1e-4,
            "resolution": "512x512",
            "style": "educational"
        }
        
        response = await client.post(
            "/api/v1/courses/test-course-id/train-video-model",
            json=training_config,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "model_path" in data
        assert "training_config" in data


class TestCourseManagement:
    """Test course management functionality"""

    @pytest.mark.asyncio
    async def test_course_creation(self, client: AsyncClient, auth_headers: dict):
        """Test course creation"""
        course_data = {
            "title": "Advanced Machine Learning",
            "description": "Comprehensive ML course with VR labs",
            "short_description": "Learn ML with immersive VR experiences",
            "category": "technology",
            "difficulty_level": "advanced",
            "estimated_duration_hours": 40.0,
            "price": 199.99,
            "learning_objectives": [
                "Understand neural networks",
                "Implement ML algorithms",
                "Use VR for data visualization"
            ],
            "vr_environment_id": "ml_lab_environment",
            "ai_tutor_enabled": True
        }
        
        response = await client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == course_data["title"]
        assert data["ai_tutor_enabled"] == True

    @pytest.mark.asyncio
    async def test_course_enrollment(self, client: AsyncClient, auth_headers: dict, test_course):
        """Test course enrollment"""
        response = await client.post(
            f"/api/v1/courses/{test_course.id}/enroll",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["course_id"] == str(test_course.id)
        assert data["progress_percentage"] == 0.0

    @pytest.mark.asyncio
    async def test_lesson_progress_tracking(self, client: AsyncClient, auth_headers: dict):
        """Test lesson progress tracking"""
        progress_data = {
            "completion_percentage": 85.0,
            "time_spent_minutes": 25,
            "is_completed": False,
            "quiz_score": 88.5,
            "vr_interactions_count": 15,
            "ai_questions_asked": 3
        }
        
        response = await client.post(
            "/api/v1/courses/test-course/modules/test-module/lessons/test-lesson/progress",
            json=progress_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "xp_earned" in data

    @pytest.mark.asyncio
    async def test_course_search_and_filtering(self, client: AsyncClient):
        """Test course search and filtering"""
        # Test search
        response = await client.get("/api/v1/courses/?search=machine learning")
        assert response.status_code == status.HTTP_200_OK
        
        # Test category filter
        response = await client.get("/api/v1/courses/?category=technology")
        assert response.status_code == status.HTTP_200_OK
        
        # Test VR filter
        response = await client.get("/api/v1/courses/?has_vr=true")
        assert response.status_code == status.HTTP_200_OK
        
        # Test difficulty filter
        response = await client.get("/api/v1/courses/?difficulty=beginner")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_course_analytics(self, client: AsyncClient, auth_headers: dict, test_course):
        """Test course analytics for instructors"""
        response = await client.get(
            f"/api/v1/courses/{test_course.id}/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_enrollments" in data
        assert "completion_rate" in data
        assert "vr_usage_stats" in data
        assert "ai_interaction_stats" in data


class TestWebSocketConnections:
    """Test real-time WebSocket functionality"""

    @pytest.mark.asyncio
    async def test_websocket_classroom_connection(self, client: AsyncClient):
        """Test WebSocket connection for classroom"""
        async with client.websocket_connect("/ws/classroom/test-room") as websocket:
            # Should connect successfully
            data = await websocket.receive_json()
            assert data["type"] == "connection_established"

    @pytest.mark.asyncio
    async def test_websocket_ai_class_connection(self, client: AsyncClient):
        """Test WebSocket connection for AI classes"""
        async with client.websocket_connect("/ws/ai-class/test-class") as websocket:
            # Should connect and start AI session
            data = await websocket.receive_json()
            assert data["type"] == "ai_teacher_message"

    @pytest.mark.asyncio
    async def test_websocket_message_broadcasting(self, client: AsyncClient):
        """Test message broadcasting in classrooms"""
        # Connect two clients to same room
        async with client.websocket_connect("/ws/classroom/test-room") as ws1:
            async with client.websocket_connect("/ws/classroom/test-room") as ws2:
                # Send message from first client
                await ws1.send_json({
                    "type": "chat_message",
                    "content": "Hello everyone!"
                })
                
                # Second client should receive the message
                data = await ws2.receive_json()
                assert data["type"] == "chat_message"
                assert data["content"] == "Hello everyone!"


# Fixtures and test data
@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=SecurityManager.get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User):
    """Get authentication headers for test user"""
    login_data = {
        "username": test_user.email,
        "password": "testpassword123"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
async def test_course(db: AsyncSession, test_user: User):
    """Create a test course"""
    course = Course(
        title="Test Course",
        slug="test-course",
        description="A test course for unit testing",
        instructor_id=test_user.id,
        category="technology",
        difficulty_level="beginner",
        price=0.0,
        is_published=True
    )
    
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course