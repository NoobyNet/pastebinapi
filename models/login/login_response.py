from pydantic import BaseModel

class LoginResponse(BaseModel):
    api_user_key: str

    def __init__(self, **data):
        super().__init__(**data)