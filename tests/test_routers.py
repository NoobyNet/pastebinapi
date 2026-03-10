"""Unit tests for FastAPI routers."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from config import Settings
from services.pastebin_service import PastebinService
from models.paste.paste_item import PasteItem
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
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    return Settings(
        PASTEBIN_BASE_URL="https://pastebin.com/api",
        DEV_API_KEY="test_dev_key",
        USER_NAME="test_user",
        USER_PASSWORD="test_pass"
    )


class TestAuthRouter:
    """Tests for authentication router."""

    def test_login_success(self, client):
        """Test successful login."""
        with patch("routers.auth.PastebinService.authenticate_user") as mock_auth:
            mock_auth.return_value = "user_api_key_12345"
            
            response = client.post(
                "/auth/login",
                json={
                    "api_user_name": "test_user",
                    "api_user_password": "test_password"
                }
            )
            
            assert response.status_code == 200
            assert response.json()["data"]["api_user_key"] == "user_api_key_12345"

    def test_login_authentication_error(self, client):
        """Test login with authentication error."""
        with patch("routers.auth.PastebinService.authenticate_user") as mock_auth:
            mock_auth.side_effect = AuthenticationError("Invalid credentials")
            
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

    def test_list_pastes_success(self, client):
        """Test successful paste listing."""
        mock_pastes = [
            PasteItem(
                key="abc123",
                date=datetime.now(),
                title="Test Paste 1",
                size=1024,
                expire_date=0,
                private=0,
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
                private=0,
                format_long="JavaScript",
                format_short="javascript",
                url="https://pastebin.com/def456",
                hits=100
            )
        ]
        
        with patch("routers.paste.PastebinService.list_pastes") as mock_list:
            mock_list.return_value = mock_pastes
            
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

    def test_list_pastes_error(self, client):
        """Test paste listing with error."""
        with patch("routers.paste.PastebinService.list_pastes") as mock_list:
            mock_list.side_effect = PasteListError("Failed to retrieve pastes")
            
            response = client.post(
                "/paste/list",
                json={
                    "api_user_key": "invalid_key",
                    "api_results_limit": 10
                }
            )
            
            assert response.status_code == 500
            assert "Paste List Error" in response.json()["error"]

    def test_list_pastes_invalid_request(self, client):
        """Test paste listing with invalid request."""
        with patch("routers.paste.PastebinService.list_pastes") as mock_list:
            mock_list.side_effect = InvalidRequestError("Bad API request, invalid api_user_key")
            
            response = client.post(
                "/paste/list",
                json={
                    "api_user_key": "invalid_key",
                    "api_results_limit": 10
                }
            )
            
            assert response.status_code == 400
            assert "Invalid Request" in response.json()["error"]

    def test_create_paste_success(self, client):
        """Test successful paste creation."""
        with patch("routers.paste.PastebinService.create_paste") as mock_create:
            mock_create.return_value = "https://pastebin.com/abc123"
            
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

    def test_create_paste_with_all_options(self, client):
        """Test paste creation with all optional parameters."""
        with patch("routers.paste.PastebinService.create_paste") as mock_create:
            mock_create.return_value = "https://pastebin.com/xyz789"
            
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

    def test_create_paste_error(self, client):
        """Test paste creation with error."""
        with patch("routers.paste.PastebinService.create_paste") as mock_create:
            mock_create.side_effect = PasteCreationError("Failed to create paste")
            
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

    def test_authentication_error_handler(self, client):
        """Test AuthenticationError exception handler."""
        with patch("routers.auth.PastebinService.authenticate_user") as mock_auth:
            mock_auth.side_effect = AuthenticationError("Test auth error")
            
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

    def test_invalid_request_error_handler(self, client):
        """Test InvalidRequestError exception handler."""
        with patch("routers.paste.PastebinService.list_pastes") as mock_list:
            mock_list.side_effect = InvalidRequestError("Bad API request")
            
            response = client.post(
                "/paste/list",
                json={
                    "api_user_key": "test_key"
                }
            )
            
            assert response.status_code == 400
            assert response.json()["error"] == "Invalid Request"
            assert response.json()["detail"] == "Bad API request"

    def test_paste_list_error_handler(self, client):
        """Test PasteListError exception handler."""
        with patch("routers.paste.PastebinService.list_pastes") as mock_list:
            mock_list.side_effect = PasteListError("List error")
            
            response = client.post(
                "/paste/list",
                json={
                    "api_user_key": "test_key"
                }
            )
            
            assert response.status_code == 500
            assert response.json()["error"] == "Paste List Error"
            assert response.json()["detail"] == "List error"

    def test_paste_creation_error_handler(self, client):
        """Test PasteCreationError exception handler."""
        with patch("routers.paste.PastebinService.create_paste") as mock_create:
            mock_create.side_effect = PasteCreationError("Creation error")
            
            response = client.post(
                "/paste/create",
                json={
                    "api_paste_code": "test"
                }
            )
            
            assert response.status_code == 500
            assert response.json()["error"] == "Paste Creation Error"
            assert response.json()["detail"] == "Creation error"
