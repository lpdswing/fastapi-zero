from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, NotAuthenticated, PermissionDenied, NotFound


class AuthRequired(NotAuthenticated):
    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class AuthorizationFailed(PermissionDenied):
    DETAIL = ErrorCode.AUTHORIZATION_FAILED


class InvalidToken(NotAuthenticated):
    DETAIL = ErrorCode.INVALID_TOKEN


class InvalidCredentials(NotAuthenticated):
    DETAIL = ErrorCode.INVALID_CREDENTIALS


class EmailTaken(BadRequest):
    DETAIL = ErrorCode.EMAIL_TAKEN


class RefreshTokenNotValid(NotAuthenticated):
    DETAIL = ErrorCode.REFRESH_TOKEN_NOT_VALID


class InactiveUser(PermissionDenied):
    DETAIL = ErrorCode.INACTIVE_USER


class UserNotFound(NotFound):
    DETAIL = ErrorCode.USER_NOT_FOUND
