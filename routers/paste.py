from fastapi import APIRouter, Depends

from models.paste.create_paste_request import CreatePasteRequest
from models.paste.create_paste_response import CreatePasteResponse
from models.paste.list_paste_request import ListPasteRequest
from models.api_response import ApiResponse
from models.paste.list_paste_response import ListPasteResponse
from services.pastebin_service import PastebinService, get_pastebin_service
from config import Settings, get_settings

router = APIRouter(prefix="/paste", tags=["paste"])

@router.post("/list", response_model=ApiResponse[ListPasteResponse])
async def list_user_pastes(
    req: ListPasteRequest,
    pastebin_service: PastebinService = Depends(get_pastebin_service),
    settings: Settings = Depends(get_settings)
):
    """List all pastes for a user."""
    items = await pastebin_service.list_pastes(req)
    return ApiResponse[ListPasteResponse](data=ListPasteResponse(pastes=items))

@router.post("/create", response_model=ApiResponse[CreatePasteResponse])
async def create_new_paste(
    req: CreatePasteRequest,
    pastebin_service: PastebinService = Depends(get_pastebin_service),
    settings: Settings = Depends(get_settings)
):
    """Create a new paste on Pastebin with syntax highlighting support."""
    paste_url = await pastebin_service.create_paste(req)
    return ApiResponse[CreatePasteResponse](data=CreatePasteResponse(paste_url=paste_url))