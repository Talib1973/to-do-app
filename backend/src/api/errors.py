"""Standardized error response format."""
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """
    Standardized error detail structure.

    Attributes:
        code: Error code (e.g., VALIDATION_ERROR, AUTHENTICATION_ERROR)
        message: Human-readable error message
        details: Additional context (optional)
    """
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """
    Standardized error response wrapper.

    Attributes:
        error: Error details
    """
    error: ErrorDetail


# Error code constants
ERROR_CODES = {
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "AUTHENTICATION_ERROR": "AUTHENTICATION_ERROR",
    "AUTHORIZATION_ERROR": "AUTHORIZATION_ERROR",
    "RESOURCE_NOT_FOUND": "RESOURCE_NOT_FOUND",
    "INTERNAL_SERVER_ERROR": "INTERNAL_SERVER_ERROR",
}


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        code: Error code (use ERROR_CODES constants)
        message: Human-readable error message
        details: Additional context (optional)

    Returns:
        Dictionary with standardized error structure

    Example:
        >>> create_error_response(
        ...     code="VALIDATION_ERROR",
        ...     message="Task title cannot be empty",
        ...     details={"field": "title", "constraint": "non_empty"}
        ... )
        {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Task title cannot be empty",
                "details": {"field": "title", "constraint": "non_empty"}
            }
        }
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }
