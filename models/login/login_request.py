from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request model for authenticating with Pastebin."""

    api_user_name: str = Field(..., description="Pastebin username")
    api_user_password: str = Field(..., description="Pastebin password")
