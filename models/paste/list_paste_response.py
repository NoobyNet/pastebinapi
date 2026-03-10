from pydantic import BaseModel

from models.paste.paste_item import PasteItem


class ListPasteResponse(BaseModel):
    """Response model for successful paste creation."""

    pastes: list[PasteItem]
