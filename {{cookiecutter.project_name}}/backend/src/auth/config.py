from datetime import timedelta
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class AuthConfig(BaseSettings):
    SECRET_KEY: str


auth_config = AuthConfig()
