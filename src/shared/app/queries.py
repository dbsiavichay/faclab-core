import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

import structlog
from opentelemetry import trace

from src.shared.infra.telemetry_instruments import (
    handler_duration,
    handler_errors,
    handler_invocations,
)

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)


@dataclass
class Query:
    pass


TQuery = TypeVar("TQuery", bound=Query)
TResult = TypeVar("TResult")


class QueryHandler(Generic[TQuery, TResult], ABC):
    def handle(self, query: TQuery) -> TResult:
        query_name = type(query).__name__
        handler_name = type(self).__name__
        attributes = {
            "handler.type": "query",
            "handler.name": handler_name,
            "query.name": query_name,
        }

        with tracer.start_as_current_span(
            f"query.{query_name}", attributes=attributes
        ) as span:
            logger.info(
                "query_started",
                query=query_name,
                handler=handler_name,
            )
            handler_invocations.add(1, attributes)
            start = time.perf_counter()
            try:
                result = self._handle(query)
                elapsed = time.perf_counter() - start
                elapsed_ms = round(elapsed * 1000, 2)
                logger.info(
                    "query_completed",
                    query=query_name,
                    handler=handler_name,
                    duration_ms=elapsed_ms,
                )
                handler_duration.record(elapsed_ms, attributes)
                span.set_status(trace.StatusCode.OK)
                return result
            except Exception as exc:
                elapsed = time.perf_counter() - start
                elapsed_ms = round(elapsed * 1000, 2)
                logger.error(
                    "query_failed",
                    query=query_name,
                    handler=handler_name,
                    error=str(exc),
                    error_type=type(exc).__name__,
                    duration_ms=elapsed_ms,
                )
                handler_errors.add(1, attributes)
                handler_duration.record(elapsed_ms, attributes)
                span.set_status(trace.StatusCode.ERROR, str(exc))
                span.record_exception(exc)
                raise

    @abstractmethod
    def _handle(self, query: TQuery) -> TResult:
        raise NotImplementedError
