from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jose import jwt
from pydantic import BaseModel, EmailStr

from src.config import settings
from src.lib.logger import log

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=False,
    TEMPLATE_FOLDER=settings.EMAIL_TEMPLATES_DIR,
    VALIDATE_CERTS=True,
)


class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, Any]


async def send_email_async(
    email: EmailSchema,
    subject_template: str = "",
    template_name: str = "",
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = MessageSchema(
        subject=subject_template,
        recipients=email.model_dump().get("email"),
        template_body=email.model_dump().get("body"),
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    result = await fm.send_message(message, template_name=template_name)
    log.info(f"Send email to {email.model_dump()['email']}, the result is {result}")


async def send_reset_password_email(email_to: EmailStr, username: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {username}"
    template_name = "reset_password.html"
    server_host = settings.SERVER_HOST
    link = f"{server_host}/#/pswd_transit?token={token}"
    email = EmailSchema(
        email=[email_to],
        body={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    await send_email_async(
        email=email, subject_template=subject, template_name=template_name
    )


async def send_new_account_email(email_to: EmailStr, username: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for {username}"
    template_name = "new_account.html"
    link = settings.SERVER_HOST
    token = generate_password_reset_token(email=email_to)
    activate_url = f"{link}/#/activate_transit?token={token}"
    email = EmailSchema(
        email=[email_to],
        body={
            "project_name": settings.PROJECT_NAME,
            "activate_url": activate_url,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
        },
    )
    await send_email_async(
        email=email,
        subject_template=subject,
        template_name=template_name,
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None
