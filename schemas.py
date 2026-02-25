from pydantic import BaseModel
from pydantic_settings import BaseSettings


class UserFeedback(BaseModel):
    balance: float
    name: str
    access_token: str
    token_type: str