from pydantic import BaseModel, Field

# models/base.py
class AuthenticatedRequest(BaseModel):
    """Base for requests requiring authentication."""
    api_user_key: str = Field(..., description="User session key")


class PaginatedRequest(AuthenticatedRequest):
    """Base for pagfrom pydantic import BaseModel, Fieldinated requests."""
    limit: int | None = Field(default=50, ge=1, le=1000)
