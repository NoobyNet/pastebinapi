from pydantic import BaseModel, Field
from models.paste.paste_format import PasteFormat
from models.paste.paste_privacy import PastePrivacy
from models.paste.paste_expiration import PasteExpiration


class CreatePasteRequest(BaseModel):
    """Request model for creating a new paste on Pastebin."""

    api_paste_code: str = Field(..., description="The text/code content of your paste")
    api_paste_name: str | None = Field(default=None, description="Title of your paste")
    api_paste_format: PasteFormat | None = Field(default=PasteFormat.NONE, description="Syntax highlighting format")
    api_paste_private: PastePrivacy | None = Field(default=PastePrivacy.PUBLIC, description="Privacy level for the paste")
    api_paste_expire_date: PasteExpiration | None = Field(default=PasteExpiration.NEVER, description="Expiration time for the paste")
    api_user_key: str | None = Field(default=None, description="User session key from login (required for private pastes)")
