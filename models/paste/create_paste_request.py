from pydantic import BaseModel, Field
from models.paste.paste_format import PasteFormat


class CreatePasteRequest(BaseModel):
    """Request model for creating a new paste on Pastebin."""

    api_paste_code: str = Field(..., description="The text/code content of your paste")
    api_paste_name: str | None = Field(default=None, description="Title of your paste")
    api_paste_format: PasteFormat | None = Field(default=PasteFormat.NONE, description="Syntax highlighting format")
    api_paste_private: int | None = Field(default=0, description="0=public, 1=unlisted, 2=private")
    api_paste_expire_date: str | None = Field(default="N", description="N=never, 10M, 1H, 1D, 1W, 2W, 1M, 6M, 1Y")
    api_user_key: str | None = Field(default=None, description="User session key from login (required for private pastes)")
