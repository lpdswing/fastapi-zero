import sentry_sdk
from fastapi import FastAPI, status, APIRouter, Depends
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from asgi_correlation_id import correlation_id

from src.auth.router import router as auth_router
from src.utils.router import router as util_router
from src.config import app_configs, settings
from src.lib.lifespan import lifespan
from src.lib.logger import log
from src.middlewares import register_middlewares
from src.deps import set_global_user

app = FastAPI(**app_configs,
              lifespan=lifespan,
              dependencies=[Depends(set_global_user)]
              )
register_middlewares(app)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(_, exc) -> ORJSONResponse:
    return ORJSONResponse(
        content={
            "code": str(exc.status_code),
            "message": exc.detail,
        },
        status_code=exc.status_code,
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log.error(exc)
    response = ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "9999",
            "message": "System Error",
        },
    )
    origin = request.headers.get("origin")

    if origin:
        # Have the middleware do the heavy lifting for us to parse
        # all the config, then update our response headers
        cors = CORSMiddleware(
            app=app,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID"],
        )

        # Logic directly from Starlette's CORSMiddleware:
        # https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py#L152

        response.headers.update(cors.simple_headers)
        has_cookie = "cookie" in request.headers

        # If request includes any cookie headers, then we must respond
        # with the specific origin instead of '*'.
        if cors.allow_all_origins and has_cookie:
            response.headers["Access-Control-Allow-Origin"] = origin

        # If we only allow specific origins, then we have to mirror back
        # the Origin header in the response.
        elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.add_vary_header("Origin")
        response.headers.update({"X-Request-ID": correlation_id.get() or ""})
    return response


if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


api_router = APIRouter()
########################## New routers here ############################  # noqa
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(util_router, prefix='/util', tags=["Util"])
########################################################################  # noqa

app.include_router(api_router, prefix=settings.APIPrefix)
