import http
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.schemas.error import ErrorResponse

logger = get_logger(__name__)


def _status_to_code(status_code: int) -> str:
    try:
        return http.HTTPStatus(status_code).name
    except ValueError:
        return f"HTTP_{status_code}"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            "request_validation_error",
            path=str(request.url),
            errors=exc.errors(),
        )

        error_msgs = []
        clean_errors = []
        for err in exc.errors():
            loc = err.get("loc", ())
            loc_str = " -> ".join(str(item) for item in loc if item != "body")
            msg = err.get("msg", "Invalid value")
            if loc_str:
                error_msgs.append(f"{loc_str}: {msg}")
            else:
                error_msgs.append(msg)
            clean_errors.append(
                {
                    "loc": list(loc),
                    "msg": msg,
                    "type": str(err.get("type", "value_error")),
                }
            )

        detail_text = (
            "Validation error: " + "; ".join(error_msgs) if error_msgs else "Validation error in request payload"
        )

        response_body = ErrorResponse(
            detail=detail_text,
            error_code="VALIDATION_ERROR",
            errors=clean_errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_body.model_dump(),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        logger.warning(
            "pydantic_validation_error",
            path=str(request.url),
            errors=exc.errors(),
        )
        response_body = ErrorResponse(
            detail="Validation error",
            error_code="VALIDATION_ERROR",
            errors=[
                {
                    "loc": list(err.get("loc", ())),
                    "msg": str(err.get("msg", "")),
                    "type": str(err.get("type", "")),
                }
                for err in exc.errors()
            ],
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_body.model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        detail_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        code = _status_to_code(exc.status_code)

        if exc.status_code >= 500:
            logger.error("http_server_error", path=str(request.url), status_code=exc.status_code, detail=detail_msg)
        else:
            logger.info("http_client_error", path=str(request.url), status_code=exc.status_code, detail=detail_msg)

        response_body = ErrorResponse(
            detail=detail_msg,
            error_code=code,
            errors=None,
        )
        return JSONResponse(
            status_code=exc.status_code,
            headers=getattr(exc, "headers", None),
            content=response_body.model_dump(),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning("value_error", path=str(request.url), error=str(exc))
        response_body = ErrorResponse(
            detail=str(exc),
            error_code="BAD_REQUEST",
            errors=None,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response_body.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "unhandled_exception",
            path=str(request.url),
            error=str(exc),
        )
        response_body = ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_SERVER_ERROR",
            errors=None,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_body.model_dump(),
        )
