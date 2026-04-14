from src.shared.domain.exceptions import ApplicationError, DomainError


class InvalidCredentialsError(ApplicationError):
    error_code = "INVALID_CREDENTIALS"


class TokenExpiredError(ApplicationError):
    error_code = "TOKEN_EXPIRED"


class InvalidTokenError(ApplicationError):
    error_code = "INVALID_TOKEN"


class PermissionDeniedError(ApplicationError):
    error_code = "PERMISSION_DENIED"


class UsernameAlreadyExistsError(DomainError):
    error_code = "USERNAME_ALREADY_EXISTS"


class EmailAlreadyExistsError(DomainError):
    error_code = "EMAIL_ALREADY_EXISTS"
