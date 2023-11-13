import uuid
from collections.abc import Callable
from typing import Optional

from fastapi import BackgroundTasks, Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from src.auth.config import auth_config
from src.auth.deps import get_user_db
from src.auth.utils import send_new_account_email, send_reset_password_email
from src.config import settings
from src.db.models import User
from src.lib.logger import log


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = auth_config.SECRET_KEY
    verification_token_secret = auth_config.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        log.info(f"User {user.id} has forgot their password. Reset token: {token}")
        background = BackgroundTasks()
        background.add_task(
            send_reset_password_email,
            email_to=user.email,
            username=user.username,
            token=token,
        )
        request.state.background = background

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        log.info(f"Verification requested for user {user.id}. Verification token: {token}")
        background = BackgroundTasks()
        background.add_task(send_new_account_email, email_to=user.email, username=user.username)
        request.state.background = background


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl=f"{settings.APIPrefix}/auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=auth_config.SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_user = fastapi_users.current_user()
current_option_user = fastapi_users.current_user(optional=True)
current_active_user = fastapi_users.current_user(active=True)
