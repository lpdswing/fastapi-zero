import os
import secrets
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import (
    AmqpDsn,
    AnyHttpUrl,
    EmailStr,
    FieldValidationInfo,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    field_validator,
    validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment

load_dotenv()

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config(BaseSettings):
    APP_VERSION: str = "1"
    APIPrefix: str = f"/api/v{APP_VERSION}"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SERVER_NAME: str = "fastapi-zero"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    @field_validator("SENTRY_DSN", mode="before")
    @classmethod
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            path=f"{info.data.get('POSTGRES_DB') or ''}",
        )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME")
    @classmethod
    def get_project_name(cls, v: Optional[str], info: FieldValidationInfo) -> str:
        if not v:
            return info.data["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = os.path.join(basedir, "email-templates/build")
    EMAILS_ENABLED: bool = True

    @field_validator("EMAILS_ENABLED", mode="before")
    @classmethod
    def get_emails_enabled(cls, v: bool, info: FieldValidationInfo) -> bool:
        return bool(info.data.get("SMTP_HOST") and info.data.get("SMTP_PORT") and info.data.get("EMAILS_FROM_EMAIL"))

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin@123"
    USERS_OPEN_REGISTRATION: bool = False

    # logs
    LOG_DIR: str = os.path.join(basedir, "logs")
    ROTATION: str = "00:00"
    RETENTION: str = "7 days"

    # redis
    REDIS_URL: RedisDsn

    # kafka
    kafka_bootstrap_servers: str = "localhost:9092"

    # rabbitmq
    RABBIT_URL: AmqpDsn
    RABBIT_POOL_SIZE: int = 2
    RABBIT_CHANNEL_POOL_SIZE: int = 10

    ENVIRONMENT: Environment = Environment.PRODUCTION
    model_config = SettingsConfigDict(case_sensitive=True)


settings = Config()

app_configs: dict[str, Any] = {"title": f"{settings.PROJECT_NAME} API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["openapi_url"] = f"{settings.APIPrefix}/openapi.json"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs

if __name__ == "__main__":
    print(basedir)
    print(os.path.join(basedir, "email-templates/build"))
    print(os.path.join(basedir, "logs"))
