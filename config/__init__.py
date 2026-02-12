import structlog
from environs import Env

from .base import OpenTelemetryConfig

__all__ = ["OpenTelemetryConfig"]

env = Env()
logger = structlog.get_logger(__name__)

environment = env("ENVIRONMENT", "local")

if environment == "local":
    from .local import Config
elif environment == "staging":
    from .staging import Config
elif environment == "production":
    from .production import Config
else:
    raise ValueError("Invalid environment specified.")

logger.info("environment_loaded", environment=environment)

config = Config()
