from pydantic import BaseModel, Field


class ListPasteRequest(BaseModel):
    """Request model for listing user pastes."""

    api_user_key: str = Field(..., description="User session key from login")
    api_results_limit: int | None = Field(default=50, ge=1, le=1000, description="Number of pastes to return (max 1000)")
