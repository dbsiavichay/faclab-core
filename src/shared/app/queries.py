import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Query:
    pass


TQuery = TypeVar("TQuery", bound=Query)
TResult = TypeVar("TResult")


class QueryHandler(Generic[TQuery, TResult], ABC):
    def handle(self, query: TQuery) -> TResult:
        query_name = type(query).__name__
        handler_name = type(self).__name__
        logger.info(
            "query_started",
            query=query_name,
            handler=handler_name,
        )
        start = time.perf_counter()
        try:
            result = self._handle(query)
            elapsed = time.perf_counter() - start
            logger.info(
                "query_completed",
                query=query_name,
                handler=handler_name,
                duration_ms=round(elapsed * 1000, 2),
            )
            return result
        except Exception as exc:
            elapsed = time.perf_counter() - start
            logger.error(
                "query_failed",
                query=query_name,
                handler=handler_name,
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(elapsed * 1000, 2),
            )
            raise

    @abstractmethod
    def _handle(self, query: TQuery) -> TResult:
        raise NotImplementedError
