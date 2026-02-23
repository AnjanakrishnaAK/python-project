from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound
)

def centralized_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:

        message = "Request failed"

        if isinstance(exc, ValidationError):
            message = "Validation error"
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            message = "Authentication failed"
        elif isinstance(exc, PermissionDenied):
            message = "Permission denied"
        elif isinstance(exc, NotFound):
            message = "Resource not found"

        return Response({
            "success": False,
            "message": message,
            "data": None,
            "errors": response.data
        }, status=response.status_code)
    return Response({
        "success": False,
        "message": "Internal server error",
        "data": None,
        "errors": str(exc)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)