import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Command:
    pass


TCommand = TypeVar("TCommand", bound=Command)
TResult = TypeVar("TResult")


class CommandHandler(Generic[TCommand, TResult], ABC):
    def handle(self, command: TCommand) -> TResult:
        command_name = type(command).__name__
        handler_name = type(self).__name__
        logger.info(
            "command_started",
            command=command_name,
            handler=handler_name,
        )
        start = time.perf_counter()
        try:
            result = self._handle(command)
            elapsed = time.perf_counter() - start
            logger.info(
                "command_completed",
                command=command_name,
                handler=handler_name,
                duration_ms=round(elapsed * 1000, 2),
            )
            return result
        except Exception as exc:
            elapsed = time.perf_counter() - start
            logger.error(
                "command_failed",
                command=command_name,
                handler=handler_name,
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(elapsed * 1000, 2),
            )
            raise

    @abstractmethod
    def _handle(self, command: TCommand) -> TResult:
        raise NotImplementedError
