from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        logger.warning(
            "validation_error",
            path=str(request.url),
            errors=exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "unhandled_exception",
            path=str(request.url),
            error=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
            },
        )
