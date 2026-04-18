from .base import BaseConfig, env

_DEV_JWT_SECRET = "dev-only-change-me"
_MIN_JWT_SECRET_LENGTH = 32


class Config(BaseConfig):
    JWT_SECRET = env.str("JWT_SECRET")

    def __init__(self):
        if (
            self.JWT_SECRET == _DEV_JWT_SECRET
            or len(self.JWT_SECRET) < _MIN_JWT_SECRET_LENGTH
        ):
            raise RuntimeError(
                "JWT_SECRET must be unique and at least "
                f"{_MIN_JWT_SECRET_LENGTH} characters in staging"
            )
