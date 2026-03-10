from pydantic import BaseModel


class LoginResponse(BaseModel):
    """Response model for successful authentication."""
    api_user_key: str