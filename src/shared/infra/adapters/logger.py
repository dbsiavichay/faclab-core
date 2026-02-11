from typing import Optional

import structlog
from structlog.processors import TimeStamper, add_log_level
from structlog.stdlib import LoggerFactory, filter_by_level, render_to_log_kwargs

from src.shared.domain.ports import Logger


class StructLogger(Logger):
    _level: str = "NOSET"
    _instance: Optional["StructLogger"] = None
    _logger = None

    def __new__(cls, level: str = "INFO") -> "StructLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._level = level
            cls._instance.__initialize__()

        return cls._instance

    def __initialize__(self) -> None:
        self._logger = structlog.get_logger()

        structlog.configure(
            processors=[
                filter_by_level,
                add_log_level,
                TimeStamper(fmt="iso"),
                render_to_log_kwargs,
            ],
            wrapper_class=structlog.make_filtering_bound_logger(self._level),
            context_class=dict,
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def debug(self, message: str, **kwargs) -> None:
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self._logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        self._logger.exception(message, **kwargs)
