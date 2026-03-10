"""Unit tests for FastAPI routers."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from main import app
from config import Settings, get_settings
from services.pastebin_service import PastebinService, get_pastebin_service
from models.paste.paste_item import PasteItem
from models.paste.paste_privacy import PastePrivacy
from datetime import datetime
from exceptions import (
    AuthenticationError,
    PasteListError,
    PasteCreationError,
    InvalidRequestError
)


@pytest.fixture
def client():
    """Create test client."""
    # Override settings dependency with test settings
    def override_get_settings():
        return Settings(
            PASTEBIN_BASE_URL="https://pastebin.com/api",
            DEV_API_KEY="test_dev_key",
            USER_NAME="test_user",
            USER_PASSWORD="test_pass"
        )

    app.dependency_overrides[get_settings] = override_get_settings
    return TestClient(app)


@pytest.fixture
def mock_pastebin_service():
    """Create mock PastebinService."""
    return MagicMock(spec=PastebinService)


@pytest.fixture(autouse=True)
def cleanup_overrides():
    """Clean up dependency overrides after each test."""
    yield
    # Only clear pastebin service override, keep settings override
    app.dependency_overrides.pop(get_pastebin_service, None)


class TestAuthRouter:
    """Tests for authentication router."""

    def test_login_success(self, client, mock_pastebin_service):
        """Test successful login."""
        mock_pastebin_service.authenticate_user = AsyncMock(return_value="user_api_key_12345")
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/auth/login",
            json={
                "api_user_name": "test_user",
                "api_user_password": "test_password"
            }
        )

        if response.status_code != 200:
            print(f"\nActual response: {response.json()}")
        assert response.status_code == 200, f"Got {response.status_code}: {response.json()}"
        assert response.json()["data"]["api_user_key"] == "user_api_key_12345"

    def test_login_authentication_error(self, client, mock_pastebin_service):
        """Test login with authentication error."""
        mock_pastebin_service.authenticate_user = AsyncMock(side_effect=AuthenticationError("Invalid credentials"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/auth/login",
            json={
                "api_user_name": "test_user",
                "api_user_password": "wrong_password"
            }
        )

        assert response.status_code == 401
        assert "Authentication Error" in response.json()["error"]
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_invalid_request(self, client):
        """Test login with missing fields."""
        response = client.post(
            "/auth/login",
            json={
                "api_user_name": "test_user"
                # Missing api_user_password
            }
        )

        assert response.status_code == 422  # Validation error


class TestPasteRouter:
    """Tests for paste router."""

    def test_list_pastes_success(self, client, mock_pastebin_service):
        """Test successful paste listing."""
        mock_pastes = [
            PasteItem(
                key="abc123",
                date=datetime.now(),
                title="Test Paste 1",
                size=1024,
                expire_date=0,
                private=PastePrivacy.PUBLIC,
                format_long="Python",
                format_short="python",
                url="https://pastebin.com/abc123",
                hits=42
            ),
            PasteItem(
                key="def456",
                date=datetime.now(),
                title="Test Paste 2",
                size=2048,
                expire_date=0,
                private=PastePrivacy.PUBLIC,
                format_long="JavaScript",
                format_short="javascript",
                url="https://pastebin.com/def456",
                hits=100
            )
        ]

        mock_pastebin_service.list_pastes = AsyncMock(return_value=mock_pastes)
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/list",
            json={
                "api_user_key": "user_key_123",
                "api_results_limit": 10
            }
        )

        assert response.status_code == 200
        assert len(response.json()["data"]["pastes"]) == 2
        assert response.json()["data"]["pastes"][0]["key"] == "abc123"
        assert response.json()["data"]["pastes"][1]["key"] == "def456"

    def test_list_pastes_error(self, client, mock_pastebin_service):
        """Test paste listing with error."""
        mock_pastebin_service.list_pastes = AsyncMock(side_effect=PasteListError("Failed to retrieve pastes"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/list",
            json={
                "api_user_key": "invalid_key",
                "api_results_limit": 10
            }
        )

        assert response.status_code == 500
        assert "Paste List Error" in response.json()["error"]

    def test_list_pastes_invalid_request(self, client, mock_pastebin_service):
        """Test paste listing with invalid request."""
        mock_pastebin_service.list_pastes = AsyncMock(side_effect=InvalidRequestError("Bad API request, invalid api_user_key"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/list",
            json={
                "api_user_key": "invalid_key",
                "api_results_limit": 10
            }
        )

        assert response.status_code == 400
        assert "Invalid Request" in response.json()["error"]

    def test_create_paste_success(self, client, mock_pastebin_service):
        """Test successful paste creation."""
        mock_pastebin_service.create_paste = AsyncMock(return_value="https://pastebin.com/abc123")
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/create",
            json={
                "api_paste_code": "print('Hello, World!')",
                "api_paste_name": "Test Paste",
                "api_paste_format": "python"
            }
        )

        assert response.status_code == 200
        assert response.json()["data"]["paste_url"] == "https://pastebin.com/abc123"

    def test_create_paste_with_all_options(self, client, mock_pastebin_service):
        """Test paste creation with all optional parameters."""
        mock_pastebin_service.create_paste = AsyncMock(return_value="https://pastebin.com/xyz789")
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/create",
            json={
                "api_paste_code": "console.log('Hello');",
                "api_paste_name": "JS Test",
                "api_paste_format": "javascript",
                "api_paste_private": 1,
                "api_paste_expire_date": "10M",
                "api_user_key": "user_key_123"
            }
        )

        assert response.status_code == 200
        assert response.json()["data"]["paste_url"] == "https://pastebin.com/xyz789"

    def test_create_paste_error(self, client, mock_pastebin_service):
        """Test paste creation with error."""
        mock_pastebin_service.create_paste = AsyncMock(side_effect=PasteCreationError("Failed to create paste"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/create",
            json={
                "api_paste_code": "test code"
            }
        )

        assert response.status_code == 500
        assert "Paste Creation Error" in response.json()["error"]

    def test_create_paste_missing_code(self, client):
        """Test paste creation without required code field."""
        response = client.post(
            "/paste/create",
            json={
                "api_paste_name": "Test Paste"
                # Missing api_paste_code
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestExceptionHandlers:
    """Tests for custom exception handlers."""

    def test_authentication_error_handler(self, client, mock_pastebin_service):
        """Test AuthenticationError exception handler."""
        mock_pastebin_service.authenticate_user = AsyncMock(side_effect=AuthenticationError("Test auth error"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/auth/login",
            json={
                "api_user_name": "test",
                "api_user_password": "test"
            }
        )

        assert response.status_code == 401
        assert response.json()["error"] == "Authentication Error"
        assert response.json()["detail"] == "Test auth error"

    def test_invalid_request_error_handler(self, client, mock_pastebin_service):
        """Test InvalidRequestError exception handler."""
        mock_pastebin_service.list_pastes = AsyncMock(side_effect=InvalidRequestError("Bad API request"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/list",
            json={
                "api_user_key": "test_key"
            }
        )

        assert response.status_code == 400
        assert response.json()["error"] == "Invalid Request"
        assert response.json()["detail"] == "Bad API request"

    def test_paste_list_error_handler(self, client, mock_pastebin_service):
        """Test PasteListError exception handler."""
        mock_pastebin_service.list_pastes = AsyncMock(side_effect=PasteListError("List error"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/list",
            json={
                "api_user_key": "test_key"
            }
        )

        assert response.status_code == 500
        assert response.json()["error"] == "Paste List Error"
        assert response.json()["detail"] == "List error"

    def test_paste_creation_error_handler(self, client, mock_pastebin_service):
        """Test PasteCreationError exception handler."""
        mock_pastebin_service.create_paste = AsyncMock(side_effect=PasteCreationError("Creation error"))
        app.dependency_overrides[get_pastebin_service] = lambda: mock_pastebin_service

        response = client.post(
            "/paste/create",
            json={
                "api_paste_code": "test"
            }
        )

        assert response.status_code == 500
        assert response.json()["error"] == "Paste Creation Error"
        assert response.json()["detail"] == "Creation error"
