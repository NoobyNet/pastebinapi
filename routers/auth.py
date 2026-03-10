from fastapi import APIRouter, Depends
from models.login.login_request import LoginRequest
from models.api_response import ApiResponse
from models.login.login_response import LoginResponse
from services.pastebin_service import PastebinService, get_pastebin_service
from config import Settings, get_settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(
    req: LoginRequest,
    pastebin_service: PastebinService = Depends(get_pastebin_service),
    settings: Settings = Depends(get_settings)
):
    """Authenticate with Pastebin and return a user API key."""
    api_user_key = await pastebin_service.authenticate_user(req)
    return ApiResponse[LoginResponse](data=LoginResponse(api_user_key=api_user_key))
