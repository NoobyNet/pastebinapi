from datetime import datetime
from pydantic import BaseModel, Field

class PasteItem(BaseModel):
    """Model representing a Pastebin paste."""
    key: str = Field(..., description="Paste unique identifier")
    date: datetime = Field(..., description="Paste creation date")
    title: str | None = Field(default=None, description="Paste title")
    size: int = Field(..., description="Paste size in bytes")
    expire_date: int = Field(..., description="Paste expiration date")
    private: int = Field(..., description="Paste privacy status (0=public, 1=unlisted, 2=private)")
    format_long: str = Field(..., description="Paste syntax highlighting format")
    format_short: str = Field(..., description="Paste syntax highlighting format (short)")
    url: str = Field(..., description="Paste URL")
    hits: int = Field(..., description="Paste hit count")