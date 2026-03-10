import aiohttp
from config import Settings
from models.paste.list_paste_request import ListPasteRequest
from models.login.login_request import LoginRequest
from models.paste.create_paste_request import CreatePasteRequest
from models.paste.paste_item import PasteItem
from services.xml_service import parse_paste_list_xml
from exceptions import AuthenticationError, PasteListError, PasteCreationError, InvalidRequestError

PASTEBIN_LOGIN_ENDPOINT = "/api_login.php"
PASTEBIN_POST_ENDPOINT = "/api_post.php"


class PastebinService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def authenticate_user(self, req: LoginRequest) -> str:
        """Authenticate the user with Pastebin API and return API User Key."""
        form_data = {
            "api_dev_key": self.settings.DEV_API_KEY,
            "api_user_name": req.api_user_name,
            "api_user_password": req.api_user_password
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.settings.PASTEBIN_BASE_URL}{PASTEBIN_LOGIN_ENDPOINT}",
                data=form_data
            ) as response:
                response_text = (await response.text()).strip()
                if response.status != 200:
                    raise AuthenticationError(f"Login failed: {response_text}")
                if response_text.startswith("Bad API request"):
                    raise AuthenticationError(response_text)
                return response_text

    async def list_pastes(self, req: ListPasteRequest) -> list[PasteItem]:
        """List all pastes for a user."""
        form_data = {
            "api_option": "list",
            "api_dev_key": self.settings.DEV_API_KEY,
            "api_user_key": req.api_user_key
        }
        if req.api_results_limit:
            form_data["api_results_limit"] = req.api_results_limit

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.settings.PASTEBIN_BASE_URL}{PASTEBIN_POST_ENDPOINT}",
                data=form_data
            ) as response:
                response_text = await response.text()
                if response.status != 200:
                    raise PasteListError(f"Failed to list pastes: {response_text}")
                if response_text.startswith("Bad API request"):
                    raise InvalidRequestError(response_text)
                return parse_paste_list_xml(response_text)

    async def create_paste(self, req: CreatePasteRequest) -> str:
        """Create a new paste on Pastebin and return the paste URL."""
        form_data = {
            "api_option": "paste",
            "api_dev_key": self.settings.DEV_API_KEY,
            "api_paste_code": req.api_paste_code,
        }

        # Add optional parameters only if provided
        if req.api_paste_name:
            form_data["api_paste_name"] = req.api_paste_name
        if req.api_paste_format:
            form_data["api_paste_format"] = req.api_paste_format.value
        if req.api_paste_private is not None:
            form_data["api_paste_private"] = req.api_paste_private.value
        if req.api_paste_expire_date:
            form_data["api_paste_expire_date"] = req.api_paste_expire_date.value
        if req.api_user_key:
            form_data["api_user_key"] = req.api_user_key


        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.settings.PASTEBIN_BASE_URL}{PASTEBIN_POST_ENDPOINT}",
                data=form_data
            ) as response:
                paste_url = (await response.text()).strip()
                if response.status != 200:
                    raise PasteCreationError(f"Failed to create paste: {paste_url}")
                if paste_url.startswith("Bad API request"):
                    raise InvalidRequestError(paste_url)
                return paste_url


def get_pastebin_service(settings: Settings) -> PastebinService:
    """FastAPI dependency for PastebinService."""
    return PastebinService(settings)