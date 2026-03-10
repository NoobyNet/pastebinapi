from pydantic import BaseModel


class CreatePasteResponse(BaseModel):
    """Response model for successful paste creation."""

    paste_url: str
