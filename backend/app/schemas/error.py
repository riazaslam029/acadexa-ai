from typing import Any
from pydantic import BaseModel, Field


class ValidationErrorItem(BaseModel):
    loc: list[str | int] = Field(default_factory=list, description="Location of the validation error")
    msg: str = Field(..., description="Error message description")
    type: str = Field(..., description="Error type identifier")


class ErrorResponse(BaseModel):
    """
    Standardized API error response format across the Acadexa AI platform.
    Ensures backward compatibility with clients expecting `detail` while
    providing structured `error_code` and optional validation `errors`.
    """
    detail: str = Field(..., description="Human-readable summary of the error")
    error_code: str = Field(..., description="Machine-readable error identifier")
    errors: list[dict[str, Any]] | None = Field(
        default=None,
        description="Detailed list of validation or field errors if applicable",
    )
