import uuid
from datetime import datetime

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry import trace
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.domain.exceptions import ApplicationError, BaseError, DomainError

logger = structlog.get_logger(__name__)

ERROR_CODE_TO_STATUS = {
    "NOT_FOUND": 404,
    "VALIDATION_ERROR": 422,
    "REQUEST_VALIDATION_ERROR": 422,
}

LAYER_TO_STATUS = {
    DomainError: 400,
    ApplicationError: 400,
}


def _resolve_status(exc: BaseError) -> int:
    status = ERROR_CODE_TO_STATUS.get(exc.error_code)
    if status:
        return status
    for layer, code in LAYER_TO_STATUS.items():
        if isinstance(exc, layer):
            return code
    return 500


def _build_error_response(
    error_code: str,
    message: str,
    request_id: str,
    detail: str | None = None,
) -> dict:
    body = {
        "error_code": error_code,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
    }
    if detail is not None:
        body["detail"] = detail
    return body


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        bind_vars = {"request_id": request_id}

        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            bind_vars["trace_id"] = format(ctx.trace_id, "032x")
            bind_vars["span_id"] = format(ctx.span_id, "016x")

        structlog.contextvars.bind_contextvars(**bind_vars)

        try:
            response = await call_next(request)
            return response
        except RequestValidationError as exc:
            logger.warning("request_validation_error", detail=str(exc))
            body = _build_error_response(
                error_code="REQUEST_VALIDATION_ERROR",
                message="Request validation failed",
                request_id=request_id,
                detail=str(exc),
            )
            return JSONResponse(status_code=422, content=body)
        except StarletteHTTPException as exc:
            logger.exception(
                "http_error",
                error_class=exc.__class__.__name__,
                detail=exc.detail,
            )
            body = _build_error_response(
                error_code="HTTP_ERROR",
                message=str(exc.detail),
                request_id=request_id,
            )
            return JSONResponse(status_code=exc.status_code, content=body)
        except BaseError as exc:
            status = _resolve_status(exc)
            logger.warning(
                "domain_error",
                error_code=exc.error_code,
                message=exc.message,
            )
            body = _build_error_response(
                error_code=exc.error_code,
                message=exc.message,
                request_id=request_id,
                detail=exc.detail,
            )
            return JSONResponse(status_code=status, content=body)
        except IntegrityError as exc:
            logger.warning("integrity_error", message=str(exc.orig))
            body = _build_error_response(
                error_code="INTEGRITY_ERROR",
                message="Cannot complete operation because this record is referenced by other records",
                request_id=request_id,
            )
            return JSONResponse(status_code=409, content=body)
        except ValueError as exc:
            logger.warning("value_error", message=str(exc))
            body = _build_error_response(
                error_code="VALIDATION_ERROR",
                message=str(exc),
                request_id=request_id,
            )
            return JSONResponse(status_code=422, content=body)
        except Exception as exc:
            logger.exception("unhandled_exception", error=str(exc))
            body = _build_error_response(
                error_code="INTERNAL_ERROR",
                message="Internal Server Error",
                request_id=request_id,
            )
            return JSONResponse(status_code=500, content=body)
        finally:
            structlog.contextvars.unbind_contextvars(
                "request_id", "trace_id", "span_id"
            )
