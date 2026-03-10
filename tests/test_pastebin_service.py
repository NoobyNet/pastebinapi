"""Unit tests for PastebinService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientSession
from config import Settings
from services.pastebin_service import PastebinService
from models.login.login_request import LoginRequest
from models.paste.list_paste_request import ListPasteRequest
from models.paste.create_paste_request import CreatePasteRequest
from models.paste.paste_format import PasteFormat
from models.paste.paste_privacy import PastePrivacy
from models.paste.paste_expiration import PasteExpiration
from exceptions import (
    AuthenticationError,
    PasteListError,
    PasteCreationError,
    InvalidRequestError
)


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        PASTEBIN_BASE_URL="https://pastebin.com/api",
        DEV_API_KEY="test_dev_key",
        USER_NAME="test_user",
        USER_PASSWORD="test_pass"
    )


@pytest.fixture
def pastebin_service(settings):
    """Create PastebinService instance."""
    return PastebinService(settings)


class TestAuthenticateUser:
    """Tests for authenticate_user method."""

    @pytest.mark.asyncio
    async def test_successful_authentication(self, pastebin_service):
        """Test successful user authentication."""
        login_req = LoginRequest(
            api_user_name="test_user",
            api_user_password="test_password"
        )
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="user_api_key_12345")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await pastebin_service.authenticate_user(login_req)
            
            assert result == "user_api_key_12345"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_authentication_http_error(self, pastebin_service):
        """Test authentication with HTTP error."""
        login_req = LoginRequest(
            api_user_name="test_user",
            api_user_password="wrong_password"
        )
        
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.text = AsyncMock(return_value="invalid login")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(AuthenticationError) as exc_info:
                await pastebin_service.authenticate_user(login_req)
            
            assert "Login failed" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_authentication_bad_api_request(self, pastebin_service):
        """Test authentication with bad API request response."""
        login_req = LoginRequest(
            api_user_name="test_user",
            api_user_password="test_password"
        )
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="Bad API request, invalid api_dev_key")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(AuthenticationError) as exc_info:
                await pastebin_service.authenticate_user(login_req)
            
            assert "Bad API request" in str(exc_info.value.message)


class TestListPastes:
    """Tests for list_pastes method."""

    @pytest.mark.asyncio
    async def test_successful_list_pastes(self, pastebin_service):
        """Test successful paste listing."""
        list_req = ListPasteRequest(
            api_user_key="user_key_123",
            api_results_limit=10
        )
        
        mock_xml = """
        <paste>
            <paste_key>abc123</paste_key>
            <paste_date>1615000000</paste_date>
            <paste_title>Test Paste</paste_title>
            <paste_size>1024</paste_size>
            <paste_expire_date>0</paste_expire_date>
            <paste_private>0</paste_private>
            <paste_format_long>Python</paste_format_long>
            <paste_format_short>python</paste_format_short>
            <paste_url>https://pastebin.com/abc123</paste_url>
            <paste_hits>42</paste_hits>
        </paste>
        """
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_xml)
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with patch("services.pastebin_service.parse_paste_list_xml") as mock_parse:
                mock_parse.return_value = []
                
                result = await pastebin_service.list_pastes(list_req)
                
                assert isinstance(result, list)
                mock_parse.assert_called_once_with(mock_xml)

    @pytest.mark.asyncio
    async def test_list_pastes_http_error(self, pastebin_service):
        """Test paste listing with HTTP error."""
        list_req = ListPasteRequest(
            api_user_key="invalid_key",
            api_results_limit=10
        )
        
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal server error")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(PasteListError) as exc_info:
                await pastebin_service.list_pastes(list_req)
            
            assert "Failed to list pastes" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_list_pastes_bad_api_request(self, pastebin_service):
        """Test paste listing with bad API request."""
        list_req = ListPasteRequest(
            api_user_key="user_key_123",
            api_results_limit=10
        )
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="Bad API request, invalid api_user_key")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(InvalidRequestError) as exc_info:
                await pastebin_service.list_pastes(list_req)
            
            assert "Bad API request" in str(exc_info.value.message)


class TestCreatePaste:
    """Tests for create_paste method."""

    @pytest.mark.asyncio
    async def test_successful_create_paste(self, pastebin_service):
        """Test successful paste creation."""
        create_req = CreatePasteRequest(
            api_paste_code="print('Hello, World!')",
            api_paste_name="Test Paste",
            api_paste_format=PasteFormat.PYTHON
        )
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="https://pastebin.com/abc123")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await pastebin_service.create_paste(create_req)
            
            assert result == "https://pastebin.com/abc123"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_paste_http_error(self, pastebin_service):
        """Test paste creation with HTTP error."""
        create_req = CreatePasteRequest(
            api_paste_code="test code"
        )
        
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Server error")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(PasteCreationError) as exc_info:
                await pastebin_service.create_paste(create_req)
            
            assert "Failed to create paste" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_create_paste_bad_api_request(self, pastebin_service):
        """Test paste creation with bad API request."""
        create_req = CreatePasteRequest(
            api_paste_code=""
        )
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="Bad API request, invalid api_paste_code")
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(InvalidRequestError) as exc_info:
                await pastebin_service.create_paste(create_req)
            
            assert "Bad API request" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_create_paste_with_all_options(self, pastebin_service):
        """Test paste creation with all optional parameters."""
        create_req = CreatePasteRequest(
            api_paste_code="print('Hello')",
            api_paste_name="Full Options Paste",
            api_paste_format=PasteFormat.PYTHON,
            api_paste_private=PastePrivacy.UNLISTED,
            api_paste_expire_date=PasteExpiration.TEN_MINUTES,
            api_user_key="user_key_123"
        )

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="https://pastebin.com/xyz789")

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await pastebin_service.create_paste(create_req)

            assert result == "https://pastebin.com/xyz789"

            # Verify form data includes all optional fields
            call_args = mock_post.call_args
            form_data = call_args[1]["data"]
            assert form_data["api_paste_name"] == "Full Options Paste"
            assert form_data["api_paste_format"] == "python"
            assert form_data["api_paste_private"] == 1
            assert form_data["api_paste_expire_date"] == "10M"
            assert form_data["api_user_key"] == "user_key_123"
