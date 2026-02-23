from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    encryption_key: str
    host: str
    database: str
    user_database: str
    password: str

settings = Settings() 

class UserFeedback(BaseModel):
    balance: float
    name: str
    access_token: str
    token_type: str