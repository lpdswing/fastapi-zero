from fastapi.requests import Request
from fastapi import Depends
from src.auth.service import current_option_user
from src.middlewares import global_userid


async def set_global_user(request: Request, user=Depends(current_option_user)):
    # request.state is really useful to put shared state in the request object
    # Ref: https://www.starlette.io/requests/#other-state
    if user is not None:
        request.state.global_user_id = user.id
        global_userid.set(user.id)
