"""
Tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin


class TestAuthService:
    """Test authentication service methods"""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test user creation"""
        # Ensure database is set up
        from app.core.database import init_database, create_tables
        await init_database()
        await create_tables()

        auth_service = AuthService(db_session)

        user_data = UserRegister(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="TestPassword123"
        )

        user = await auth_service.create_user(user_data)

        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active == True
        assert user.is_verified == False

    @pytest.mark.asyncio
    async def test_authenticate_user(self, db_session: AsyncSession):
        """Test user authentication"""
        # Ensure database is set up
        from app.core.database import init_database, create_tables
        await init_database()
        await create_tables()

        auth_service = AuthService(db_session)

        # Create user first
        user_data = UserRegister(
            email="auth_test@example.com",
            username="authtestuser",
            full_name="Auth Test User",
            password="TestPassword123"
        )
        await auth_service.create_user(user_data)

        # Test authentication
        user = await auth_service.authenticate_user("auth_test@example.com", "TestPassword123")
        assert user is not None
        assert user.email == "auth_test@example.com"

        # Test invalid password
        user = await auth_service.authenticate_user("auth_test@example.com", "wrongpassword")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session: AsyncSession):
        """Test getting user by email"""
        auth_service = AuthService(db_session)

        # Create user first
        user_data = UserRegister(
            email="get_test@example.com",
            username="gettestuser",
            full_name="Get Test User",
            password="TestPassword123"
        )
        created_user = await auth_service.create_user(user_data)

        # Get user by email
        user = await auth_service.get_user_by_email("get_test@example.com")
        assert user is not None
        assert user.id == created_user.id

        # Test non-existent user
        user = await auth_service.get_user_by_email("nonexistent@example.com")
        assert user is None


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    @pytest.mark.asyncio
    async def test_register_endpoint(self, async_client: AsyncClient):
        """Test user registration endpoint"""
        # Ensure database is set up for endpoint tests
        from app.core.database import init_database, create_tables
        await init_database()
        await create_tables()

        user_data = {
            "email": "endpoint_test@example.com",
            "username": "endpointtestuser",
            "full_name": "Endpoint Test User",
            "password": "TestPassword123"
        }

        response = await async_client.post("/api/v1/auth/register", json=user_data)
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == "endpoint_test@example.com"
        assert data["full_name"] == "Endpoint Test User"

    @pytest.mark.asyncio
    async def test_login_endpoint(self, async_client: AsyncClient):
        """Test user login endpoint"""
        # Register user first
        user_data = {
            "email": "login_test@example.com",
            "username": "logintestuser",
            "full_name": "Login Test User",
            "password": "TestPassword123"
        }
        await async_client.post("/api/v1/auth/register", json=user_data)

        # Test login
        login_data = {
            "email": "login_test@example.com",
            "password": "TestPassword123"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient):
        """Test registering with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "duplicatetestuser",
            "full_name": "Duplicate Test User",
            "password": "TestPassword123"
        }

        # Register first time
        response1 = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 200

        # Try to register again with same email
        response2 = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint"""
        response = await async_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "EduVerse API"

    @pytest.mark.asyncio
    async def test_api_info(self, async_client: AsyncClient):
        """Test API info endpoint"""
        response = await async_client.get("/api/info")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "EduVerse API"
        assert data["version"] == "2.0.0"
        assert "features" in data
        # Check that authentication features exist
        assert "Multi-provider Authentication" in data["features"]


# Integration tests
class TestAuthIntegration:
    """Integration tests for authentication flow"""

    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, async_client: AsyncClient):
        """Test complete authentication flow"""
        # 1. Register user
        user_data = {
            "email": "flow_test@example.com",
            "username": "flowtestuser",
            "full_name": "Flow Test User",
            "password": "TestPassword123"
        }

        register_response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200

        # 2. Login
        login_data = {
            "email": "flow_test@example.com",
            "password": "TestPassword123"
        }

        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        tokens = login_response.json()
        access_token = tokens["access_token"]

        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_data = me_response.json()
        assert user_data["email"] == "flow_test@example.com"

    @pytest.mark.asyncio
    async def test_password_validation(self, async_client: AsyncClient):
        """Test password validation"""
        # Test weak password
        user_data = {
            "email": "weak_password@example.com",
            "username": "weakpassworduser",
            "full_name": "Weak Password User",
            "password": "123"  # Too short, no uppercase, no lowercase
        }

        response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_email_validation(self, async_client: AsyncClient):
        """Test email validation"""
        user_data = {
            "email": "invalid-email",  # Invalid email format
            "username": "invalidemailuser",
            "full_name": "Invalid Email User",
            "password": "TestPassword123"
        }

        response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error
